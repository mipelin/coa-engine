from __future__ import annotations

import json
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from ..core.config import settings
from ..core.schemas import EventSummary
from ..i18n.languages import final_language_instruction, resolve_language
from .llm_guardrails import LLM_DATA_GUARDRAILS, explanation_references_match, sanitize_llm_text
from .llm_client import LLMResult, get_llm_client
from .state_store import get_state_store

logger = logging.getLogger("coa_engine.engine.llm_orchestrator")


@dataclass
class LLMTask:
    task_type: str
    language: str
    prompt_chars: int
    runner: Callable[[], LLMResult]
    created_at: float = field(default_factory=time.time)
    created_monotonic: float = field(default_factory=time.monotonic)
    started: threading.Event = field(default_factory=threading.Event)
    done: threading.Event = field(default_factory=threading.Event)
    cancelled: bool = False
    result: LLMResult | None = None


class LLMOrchestrator:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tasks: deque[LLMTask] = deque()
        self._current_task_type: str | None = None
        self._last_error: str | None = None
        self._last_success_at: float | None = None
        self._last_duration_ms: float | None = None
        self._worker = threading.Thread(target=self._run, name="coa-llm-worker", daemon=True)
        self._wake = threading.Event()
        self._worker.start()

    def _run(self) -> None:
        while True:
            self._wake.wait()
            while True:
                with self._lock:
                    while self._tasks and self._tasks[0].cancelled:
                        self._tasks.popleft()
                    if not self._tasks:
                        self._wake.clear()
                        break
                    task = self._tasks.popleft()
                    queue_before = len(self._tasks) + 1
                    self._current_task_type = task.task_type
                task.started.set()
                started_at = time.time()
                started_monotonic = time.monotonic()
                result = LLMResult(fallback_reason="llm_model_error")
                try:
                    logger.info(
                        "llm_call: task_type=%s language=%s prompt_chars=%d started_at=%.3f queue_before=%d",
                        task.task_type,
                        task.language,
                        task.prompt_chars,
                        started_at,
                        queue_before,
                    )
                    result = task.runner()
                except Exception as exc:
                    logger.warning("llm_call runner failed for %s: %s", task.task_type, exc)
                    result = LLMResult(fallback_reason="llm_model_error")
                duration_ms = (time.monotonic() - started_monotonic) * 1000
                with self._lock:
                    task.result = result
                    task.done.set()
                    self._current_task_type = None
                    self._last_duration_ms = duration_ms
                    self._last_error = None if result.ok else result.fallback_reason
                    if result.ok:
                        self._last_success_at = time.time()
                    queue_after = len(self._tasks)
                logger.info(
                    "llm_result: task_type=%s language=%s success=%s fallback_reason=%s duration_ms=%.0f queue_after=%d",
                    task.task_type,
                    task.language,
                    result.ok,
                    result.fallback_reason,
                    duration_ms,
                    queue_after,
                )

    def status(self) -> dict:
        with self._lock:
            return {
                "busy": self._current_task_type is not None,
                "queue_length": len(self._tasks),
                "current_task_type": self._current_task_type,
                "last_error": self._last_error,
                "last_success_at": self._last_success_at,
                "last_duration_ms": self._last_duration_ms,
            }

    def _submit(self, task: LLMTask, wait: bool = True) -> LLMResult:
        llm = get_llm_client()
        if not llm.enabled:
            return LLMResult(fallback_reason="llm_disabled")
        with self._lock:
            self._tasks.append(task)
            self._wake.set()
        if not wait:
            return LLMResult(text="queued")
        if not task.started.wait(timeout=settings.llm_queue_timeout_seconds):
            task.cancelled = True
            return LLMResult(fallback_reason="llm_queue_timeout")
        if not task.done.wait(timeout=settings.llm_timeout_seconds + 5.0):
            return LLMResult(fallback_reason="llm_timeout")
        return task.result or LLMResult(fallback_reason="llm_model_error")

    def run_chat(
        self,
        *,
        task_type: str,
        language: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> LLMResult:
        language_code, _ = resolve_language(language)
        prompt_chars = len(system_prompt) + len(user_prompt)
        task = LLMTask(
            task_type=task_type,
            language=language_code,
            prompt_chars=prompt_chars,
            runner=lambda: get_llm_client().chat_sync(system_prompt, user_prompt, max_tokens=max_tokens),
        )
        return self._submit(task, wait=True)

    def run_health_check(self) -> dict:
        llm = get_llm_client()
        status = self.status()
        result = llm.probe_sync()
        result.update({
            "busy": status["busy"],
            "queue_length": status["queue_length"],
            "last_success_at": result.get("last_success_at") or status["last_success_at"],
            "last_error": result.get("last_error") or status["last_error"],
            "last_duration_ms": result.get("last_duration_ms") or status["last_duration_ms"],
        })
        return result

    def enqueue_event_summary(
        self,
        *,
        tick: int,
        event_type: str,
        language: str,
        context: dict,
    ) -> None:
        language_code, language_name = resolve_language(language)
        language_instruction = final_language_instruction(language_code)
        logger.info(
            "event_summary_language: task_type=event_summary requested_language=%s resolved_language=%s prompt_language_instruction=%s",
            language,
            language_code,
            language_instruction,
        )
        system_prompt = (
            "You are an advisory NATO DIANA operations analyst. "
            "Write a short operational situation update based only on the supplied system state. "
            "Do not invent facts. Do not authorize action. Do not change recommendations. "
            "Explain: what happened, why it matters, what could happen next, and what the system currently recommends. "
            f"{LLM_DATA_GUARDRAILS} "
            f"{language_instruction} "
            "If the input mixes languages, keep the response entirely in the requested language."
        )
        user_prompt = (
            "Structured operational context:\n"
            f"{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
            "Return one concise paragraph."
        )
        prompt_chars = len(system_prompt) + len(user_prompt)

        def _runner() -> LLMResult:
            result = get_llm_client().chat_sync(system_prompt, user_prompt, max_tokens=320)
            summary_text = ""
            fallback_reason = result.fallback_reason
            if result.ok:
                candidate = sanitize_llm_text(result.text)
                valid_targets = {
                    item.get("entity_id")
                    for item in [context.get("top_threat") or {}, context.get("latest_event") or {}]
                    if item.get("entity_id")
                }
                valid_coa_titles = {
                    item.get("title")
                    for item in context.get("top_coas", [])
                    if item.get("title")
                }
                recommendation_title = context.get("recommended_coa")
                if recommendation_title and recommendation_title != "None":
                    valid_coa_titles.add(recommendation_title)
                if explanation_references_match(
                    candidate,
                    threat_level=str(context.get("threat_level") or "LOW"),
                    valid_target_ids=valid_targets,
                    valid_coa_titles=valid_coa_titles,
                ):
                    summary_text = candidate
                    fallback_reason = None
                else:
                    # Keep the LLM text but flag the mismatch — don't discard it
                    summary_text = candidate
                    fallback_reason = "llm_state_mismatch"
                    logger.warning("event_summary: state mismatch, keeping text with warning")
            summary = EventSummary(
                tick=tick,
                event_type=event_type,
                summary_text=summary_text,
                timestamp=datetime.now(timezone.utc),
                llm_used=bool(summary_text),
                language_used=language_code,
                fallback_reason=fallback_reason,
            )
            get_state_store().set_latest_event_summary(summary)
            if summary_text:
                return LLMResult(text=summary_text)
            return LLMResult(fallback_reason=fallback_reason or "llm_model_error")

        task = LLMTask(
            task_type="event_summary",
            language=language_code,
            prompt_chars=prompt_chars,
            runner=_runner,
        )
        with self._lock:
            self._tasks.append(task)
            self._wake.set()


_llm_orchestrator: LLMOrchestrator | None = None


def get_llm_orchestrator() -> LLMOrchestrator:
    global _llm_orchestrator
    if _llm_orchestrator is None:
        _llm_orchestrator = LLMOrchestrator()
    return _llm_orchestrator


def reset_llm_orchestrator() -> None:
    global _llm_orchestrator
    _llm_orchestrator = None
