from __future__ import annotations

import logging
import re
import threading
import time

import httpx

from ..core.config import settings

logger = logging.getLogger("coa_engine.engine.llm_client")

UNSAFE_WORDS = [
    "target", "weapon", "strike", "engage", "kill", "lethal",
    "execute order", "fire", "destroy", "neutralize",
]


class LLMResult:
    """Structured result from an LLM call."""

    __slots__ = ("text", "fallback_reason")

    def __init__(self, text: str | None = None, fallback_reason: str | None = None) -> None:
        self.text = text
        self.fallback_reason = fallback_reason

    @property
    def ok(self) -> bool:
        return self.text is not None and self.fallback_reason is None


class LLMClient:
    """OpenAI-compatible client for llama.cpp server."""

    def __init__(self) -> None:
        self.base_url = settings.llm_base_url
        self.api_key = settings.llm_api_key_effective
        self.model = settings.llm_model
        self.timeout = settings.llm_timeout_seconds
        self.enabled = settings.llm_enabled
        self._lock = threading.Lock()
        self._last_success_at: float | None = None
        self._last_error: str | None = None
        self._last_duration_ms: float | None = None
        self._resolved_model: str | None = None
        self._log_config()

    def _headers(self) -> dict[str, str]:
        """Build request headers. Authorization is omitted when no API key is set."""
        h: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _log_config(self) -> None:
        if self.enabled:
            logger.info(
                "LLM enabled: url=%s model=%s timeout=%.0fs max_tokens=%d api_key=%s",
                self.base_url, self.model, self.timeout,
                settings.llm_max_tokens,
                "yes" if settings.llm_api_key_present else "no",
            )
        else:
            logger.info("LLM disabled — using deterministic fallbacks")

    def _client(self, timeout: float | None = None) -> httpx.Client:
        return httpx.Client(timeout=timeout or self.timeout)

    def _fetch_models(self, client: httpx.Client | None = None, *, timeout: float | None = None) -> tuple[list[dict], float]:
        close_client = False
        started_at = time.monotonic()
        if client is None:
            client = self._client(timeout=timeout)
            close_client = True
        try:
            resp = client.get(f"{self.base_url}/models", headers=self._headers())
            resp.raise_for_status()
            payload = resp.json()
            models = payload.get("data", [])
            return models if isinstance(models, list) else [], (time.monotonic() - started_at) * 1000
        finally:
            if close_client:
                client.close()

    def _effective_model(self, client: httpx.Client) -> str:
        if self.model != "local":
            return self.model
        if self._resolved_model:
            return self._resolved_model
        try:
            models, _ = self._fetch_models(client)
            if models and isinstance(models[0], dict) and models[0].get("id"):
                self._resolved_model = str(models[0]["id"])
                logger.info("Resolved local LLM model id to %s", self._resolved_model)
                return self._resolved_model
        except Exception:
            pass
        self._resolved_model = self.model
        return self._resolved_model

    @property
    def busy(self) -> bool:
        return self._lock.locked()

    def diagnostics(self) -> dict:
        """Return health diagnostics. Never exposes the API key."""
        return {
            "last_success_at": self._last_success_at,
            "last_error": self._last_error,
            "last_duration_ms": self._last_duration_ms,
            "busy": self.busy,
        }

    # ------------------------------------------------------------------
    # Core call helpers
    # ------------------------------------------------------------------

    def _classify_error(self, exc: Exception) -> str:
        """Map an exception to a specific fallback_reason string."""
        if isinstance(exc, httpx.TimeoutException):
            return "llm_timeout"
        if isinstance(exc, httpx.ConnectError):
            return "llm_connection_failed"
        if isinstance(exc, httpx.HTTPStatusError):
            code = exc.response.status_code
            if code == 404:
                return "llm_model_error"
            if code >= 500:
                return "llm_connection_failed"
            return "llm_model_error"
        return "llm_call_failed"

    def _chat_raw(
        self,
        messages: list[dict],
        purpose: str,
        max_tokens: int | None = None,
        *,
        client: httpx.Client | None = None,
        timeout: float | None = None,
    ) -> LLMResult:
        """Synchronous LLM call with structured logging, concurrency guard, and error classification."""
        if not self.enabled:
            return LLMResult(fallback_reason="llm_disabled")

        prompt_chars = sum(len(m.get("content", "")) for m in messages)
        started_at = time.monotonic()

        if not self._lock.acquire(blocking=False):
            logger.warning("LLM busy, skipping purpose=%s", purpose)
            return LLMResult(fallback_reason="llm_busy")

        try:
            logger.info(
                "llm_call: purpose=%s base_url=%s model=%s timeout=%.0fs prompt_chars=%d",
                purpose, self.base_url, self.model, timeout or self.timeout, prompt_chars,
            )

            effective_timeout = timeout or self.timeout
            close_client = False
            if client is None:
                client = httpx.Client(timeout=effective_timeout)
                close_client = True

            try:
                resp = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json={
                        "model": self._effective_model(client),
                        "messages": messages,
                        "max_tokens": max_tokens or settings.llm_max_tokens,
                        "temperature": 0.3,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
            finally:
                if close_client:
                    client.close()

            content = data["choices"][0]["message"]["content"]
            duration_ms = (time.monotonic() - started_at) * 1000
            self._last_success_at = time.time()
            self._last_duration_ms = duration_ms
            self._last_error = None

            if not content or not content.strip():
                logger.warning(
                    "llm_result: purpose=%s success=false fallback=llm_empty_response duration_ms=%.0f",
                    purpose, duration_ms,
                )
                self._last_error = "empty response"
                return LLMResult(fallback_reason="llm_empty_response")

            filtered = self._safety_filter(content)
            logger.info(
                "llm_result: purpose=%s success=true response_chars=%d duration_ms=%.0f",
                purpose, len(filtered), duration_ms,
            )
            return LLMResult(text=filtered)

        except Exception as e:
            duration_ms = (time.monotonic() - started_at) * 1000
            self._last_duration_ms = duration_ms
            self._last_error = str(e)
            reason = self._classify_error(e)
            logger.warning(
                "llm_result: purpose=%s success=false fallback=%s error_type=%s error=%s duration_ms=%.0f",
                purpose, reason, type(e).__name__, e, duration_ms,
            )
            return LLMResult(fallback_reason=reason)
        finally:
            self._lock.release()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> LLMResult:
        """Async-compatible interface (returns LLMResult). Use chat_sync in sync callers."""
        return self.chat_sync(system_prompt, user_prompt, max_tokens=max_tokens)

    def chat_sync(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> LLMResult:
        """Synchronous LLM call. Returns LLMResult with text or fallback_reason."""
        return self._chat_raw(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            purpose="query",
            max_tokens=max_tokens,
        )

    def call_briefing(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> LLMResult:
        """Briefing-purpose LLM call."""
        return self._chat_raw(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            purpose="briefing",
            max_tokens=max_tokens,
        )

    def call_translation(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> LLMResult:
        """Translation-purpose LLM call."""
        return self._chat_raw(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            purpose="translation",
            max_tokens=max_tokens,
        )

    def probe_sync(self) -> dict:
        """Lightweight reachability probe using /models. Never calls the model."""
        result: dict = {
            "configured": self.enabled,
            "base_url": self.base_url,
            "model": self._resolved_model or self.model,
            "reachable": False,
            "api_key_present": settings.llm_api_key_present,
        }
        if not self.enabled:
            result["error"] = "LLM disabled"
            result.update(self.diagnostics())
            return result

        try:
            with self._client(timeout=min(self.timeout, settings.llm_health_timeout_seconds)) as client:
                models, duration_ms = self._fetch_models(client)
            if models and isinstance(models[0], dict) and models[0].get("id"):
                self._resolved_model = str(models[0]["id"])
            self._last_duration_ms = duration_ms
            self._last_success_at = time.time()
            self._last_error = None
            result["reachable"] = True
            result["model"] = self._resolved_model or self.model
        except Exception as exc:
            self._last_duration_ms = None
            self._last_error = self._classify_error(exc)
            result["error"] = self._last_error
        result.update(self.diagnostics())
        return result

    def _safety_filter(self, text: str) -> str:
        for word in UNSAFE_WORDS:
            if word.lower() in text.lower():
                logger.warning("UNSAFE_WORD detected: '%s' — redacting", word)
                text = re.sub(re.escape(word), "[REDACTED]", text, flags=re.IGNORECASE)
        return text


_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def reset_llm_client() -> None:
    """Reset the singleton so the next get_llm_client() picks up current settings."""
    global _llm_client
    _llm_client = None
