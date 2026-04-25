from __future__ import annotations

import logging
import re

import httpx

from ..core.config import settings

logger = logging.getLogger("coa_engine.engine.llm_client")

UNSAFE_WORDS = [
    "target", "weapon", "strike", "engage", "kill", "lethal",
    "execute order", "fire", "destroy", "neutralize",
]


class LLMClient:
    """OpenAI-compatible client for local Gemma 4 via llama.cpp."""

    def __init__(self) -> None:
        self.base_url = settings.llm_base_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.timeout = settings.llm_timeout_seconds
        self.enabled = settings.llm_enabled

    async def chat(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> str | None:
        if not self.enabled:
            logger.debug("LLM disabled, returning None")
            return None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "max_tokens": max_tokens or settings.llm_max_tokens,
                        "temperature": 0.3,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                filtered = self._safety_filter(content)
                logger.info("LLM response: %d chars", len(filtered))
                return filtered
        except Exception as e:
            logger.warning("LLM call failed: %s", e)
            return None

    def chat_sync(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> str | None:
        """Synchronous version for non-async callers."""
        if not self.enabled:
            return None
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "max_tokens": max_tokens or settings.llm_max_tokens,
                        "temperature": 0.3,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return self._safety_filter(content)
        except Exception as e:
            logger.warning("LLM sync call failed: %s", e)
            return None

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
