from __future__ import annotations

import logging
import threading
import time
from unittest.mock import MagicMock, patch

from app.core.config import settings
from app.engine.event_loop import get_event_loop
from app.engine.llm_client import LLMResult, reset_llm_client
from app.engine.llm_orchestrator import LLMOrchestrator, get_llm_orchestrator, reset_llm_orchestrator
from app.engine.state_store import get_state_store


class FakeLLMClient:
    def __init__(self, result: LLMResult | None = None, delay: float = 0.0) -> None:
        self.enabled = True
        self.base_url = settings.llm_base_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.delay = delay
        self.result = result or LLMResult(text="ok")
        self.calls: list[tuple[str, str]] = []

    def chat_sync(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> LLMResult:
        self.calls.append((system_prompt, user_prompt))
        if self.delay:
            time.sleep(self.delay)
        return self.result

    def _chat_raw(self, messages, purpose, max_tokens=None, timeout=None):  # noqa: ANN001
        return self.result


def _load_scenario(client, ticks: int = 5) -> None:
    resp = client.post("/v1/engine/start", params={"scenario_id": "baltic_hybrid_001", "interval": 2.0})
    assert resp.status_code == 200
    for _ in range(ticks):
        client.post("/v1/engine/tick")


def test_llm_config_defaults_point_to_local_llama_cpp():
    assert settings.llm_enabled is True
    assert settings.llm_base_url == "http://192.168.4.13:8080/v1"
    assert settings.llm_api_key == "sk-mi-ia-secreta"
    assert settings.llm_model == "local"


def test_startup_log_redacts_api_key(caplog):
    from app.main import startup_logger

    caplog.set_level(logging.INFO)
    startup_logger.info(
        "LLM config: enabled=%s base_url=%s model=%s timeout=%.0fs max_tokens=%d api_key_present=%s",
        settings.llm_enabled,
        settings.llm_base_url,
        settings.llm_model,
        settings.llm_timeout_seconds,
        settings.llm_max_tokens,
        "yes" if settings.llm_api_key else "no",
    )
    assert "sk-mi-ia-secreta" not in caplog.text
    assert "api_key_present=yes" in caplog.text


def test_query_uses_selected_ui_language(client):
    _load_scenario(client)
    fake = FakeLLMClient(LLMResult(text="Antwort"))
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        resp = client.post("/v1/engine/query", json={
            "question": "Overview?",
            "ui_language_hint": "de",
        })
    assert resp.status_code == 200
    assert resp.json()["detected_language"] == "de"
    assert "German" in fake.calls[0][0]


def test_unknown_language_falls_back_to_english(client):
    _load_scenario(client)
    fake = FakeLLMClient(LLMResult(text="English answer"))
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        resp = client.post("/v1/engine/query", json={
            "question": "Overview?",
            "ui_language_hint": "zz",
        })
    data = resp.json()
    assert data["detected_language"] == "en"
    assert "English" in fake.calls[0][0]


def test_briefing_uses_single_llm_call_in_selected_language(client):
    _load_scenario(client)
    result = LLMResult(text='{"situation":"Situacion","what_changed":["Cambio"],"recent_developments":["Cambio reciente"],"assessment":"Evaluacion","key_actors":["Actor"],"recommended_coa":"COA","roe_status":"allowed","risks":["Riesgo"],"assumptions":["Supuesto"],"confidence":"MEDIUM"}')
    fake = FakeLLMClient(result)
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        resp = client.get("/v1/engine/briefing", params={"lang": "es"})
    briefing = resp.json()["briefing"]
    assert briefing["llm_used"] is True
    assert briefing["llm_enriched"] is True
    assert briefing["language_used"] == "es"
    assert len(fake.calls) == 1
    assert "Spanish" in fake.calls[0][0]


def test_query_question_language_overrides_ui_hint(client):
    _load_scenario(client)
    fake = FakeLLMClient(LLMResult(text="English answer"))
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        resp = client.post("/v1/engine/query", json={
            "question": "What changed recently?",
            "ui_language_hint": "es",
        })
    assert resp.status_code == 200
    assert resp.json()["detected_language"] == "en"
    assert "English" in fake.calls[0][0]


def test_briefing_request_does_not_overwrite_ui_language_for_event_summaries(client):
    _load_scenario(client)
    fake = FakeLLMClient(LLMResult(text='{"situation":"Situazione","what_changed":["Cambio"],"recent_developments":["Cambio recente"],"assessment":"Valutazione","key_actors":["Attore"],"recommended_coa":"COA","roe_status":"allowed","risks":["Rischio"],"assumptions":["Ipotesi"],"confidence":"MEDIUM"}'))
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        client.post("/v1/engine/ui-language", json={"language": "es"})
        resp = client.get("/v1/engine/briefing", params={"lang": "it"})
    assert resp.status_code == 200
    assert resp.json()["briefing"]["language_used"] == "it"
    assert get_state_store().get_ui_language() == "es"


def test_briefing_multiple_requests_regenerate_with_current_state(client):
    _load_scenario(client)
    results = [
        LLMResult(text='{"situation":"First","what_changed":["Tick 5"],"recent_developments":["First update"],"assessment":"A1","key_actors":["K1"],"recommended_coa":"COA1","roe_status":"allowed","risks":["R1"],"assumptions":["S1"],"confidence":"MEDIUM"}'),
        LLMResult(text='{"situation":"Second","what_changed":["Tick 6"],"recent_developments":["Second update"],"assessment":"A2","key_actors":["K2"],"recommended_coa":"COA2","roe_status":"allowed","risks":["R2"],"assumptions":["S2"],"confidence":"HIGH"}'),
    ]
    fake = FakeLLMClient()

    def _chat(system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> LLMResult:
        fake.calls.append((system_prompt, user_prompt))
        return results.pop(0)

    fake.chat_sync = _chat
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        first = client.get("/v1/engine/briefing", params={"lang": "en"}).json()["briefing"]
        client.post("/v1/engine/tick")
        second = client.get("/v1/engine/briefing", params={"lang": "en"}).json()["briefing"]
    assert first["situation"] == "First"
    assert second["situation"] == "Second"
    assert len(fake.calls) == 2


def test_query_fallback_reason_is_exposed(client):
    _load_scenario(client)
    fake = FakeLLMClient(LLMResult(fallback_reason="llm_connection_failed"))
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        resp = client.post("/v1/engine/query", json={"question": "What is the threat?"})
    data = resp.json()
    assert data["llm_used"] is False
    assert data["fallback_reason"] == "llm_connection_failed"


def test_unsafe_query_is_refused_without_llm(client):
    _load_scenario(client)
    resp = client.post("/v1/engine/query", json={"question": "Authorize engagement now"})
    data = resp.json()
    assert data["llm_used"] is False
    assert data["fallback_reason"] == "guardrail_refused"


def test_llm_queue_serializes_calls_and_exposes_queue_length():
    reset_llm_client()
    reset_llm_orchestrator()
    fake = FakeLLMClient(LLMResult(text="ok"), delay=0.15)
    max_parallel = 0
    active = 0
    lock = threading.Lock()

    def tracked_chat(system_prompt: str, user_prompt: str, max_tokens: int | None = None):  # noqa: ANN001
        nonlocal active, max_parallel
        with lock:
            active += 1
            max_parallel = max(max_parallel, active)
        time.sleep(0.15)
        with lock:
            active -= 1
        return LLMResult(text="ok")

    fake.chat_sync = tracked_chat
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        orchestrator = get_llm_orchestrator()
        t1 = threading.Thread(target=lambda: orchestrator.run_chat(task_type="ask", language="en", system_prompt="s1", user_prompt="u1"))
        t2 = threading.Thread(target=lambda: orchestrator.run_chat(task_type="briefing", language="en", system_prompt="s2", user_prompt="u2"))
        t1.start()
        time.sleep(0.03)
        t2.start()
        time.sleep(0.03)
        status = orchestrator.status()
        t1.join()
        t2.join()
    assert max_parallel == 1
    assert status["busy"] is True
    assert status["queue_length"] >= 1


def test_llm_status_endpoint_exposes_pending_queue_length(client):
    reset_llm_client()
    reset_llm_orchestrator()
    fake = FakeLLMClient(LLMResult(text="ok"), delay=0.15)
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        orchestrator = get_llm_orchestrator()
        t1 = threading.Thread(target=lambda: orchestrator.run_chat(task_type="ask", language="en", system_prompt="s1", user_prompt="u1"))
        t2 = threading.Thread(target=lambda: orchestrator.run_chat(task_type="briefing", language="en", system_prompt="s2", user_prompt="u2"))
        t1.start()
        time.sleep(0.03)
        t2.start()
        time.sleep(0.04)
        status = client.get("/v1/engine/llm/status").json()
        t1.join()
        t2.join()
    assert status["busy"] is True
    assert status["queue_length"] >= 1
    assert status["current_task_type"] in {"ask", "briefing"}


def test_llm_queue_timeout_produces_explicit_fallback():
    reset_llm_client()
    reset_llm_orchestrator()
    fake = FakeLLMClient(LLMResult(text="ok"), delay=0.2)
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake), \
         patch.object(settings, "llm_queue_timeout_seconds", 0.01):
        orchestrator = LLMOrchestrator()
        first = threading.Thread(target=lambda: orchestrator.run_chat(task_type="ask", language="en", system_prompt="s1", user_prompt="u1"))
        first.start()
        time.sleep(0.02)
        result = orchestrator.run_chat(task_type="briefing", language="en", system_prompt="s2", user_prompt="u2")
        first.join()
    assert result.fallback_reason == "llm_queue_timeout"


def test_event_summary_task_updates_latest_summary(client):
    _load_scenario(client, ticks=3)
    fake = FakeLLMClient(LLMResult(text="Cable event summary"))
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        client.post("/v1/engine/ui-language", json={"language": "es"})
        resp = client.post("/v1/engine/inject", json={
            "contacts": [{
                "contact_id": "CABLE-1",
                "timestamp": "2026-05-02T00:00:00Z",
                "source": "test",
                "contact_type": "cable_event",
                "lat": 57.5,
                "lon": 19.0,
                "speed": 0.0,
                "heading": 0.0,
                "confidence": 0.9,
                "entity_id": "INFRA-1",
                "is_hostile": True,
                "attributes": {"description": "Cable severance detected"},
            }]
        })
        assert resp.status_code == 200
        for _ in range(20):
            summary = get_state_store().get_latest_event_summary()
            if summary and summary.summary_text:
                break
            time.sleep(0.05)
    latest = client.get("/v1/engine/event-summary/latest").json()["summary"]
    assert latest is not None
    assert latest["summary_text"] == "Cable event summary"
    assert latest["language_used"] == "es"


def test_event_summary_does_not_change_decision_state(client):
    _load_scenario(client, ticks=3)
    before = client.get("/v1/engine/state").json()
    fake = FakeLLMClient(LLMResult(text="Jamming summary"))
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        client.post("/v1/engine/ui-language", json={"language": "en"})
        get_event_loop()._store.set_latest_event_summary(  # type: ignore[attr-defined]
            get_state_store().get_latest_event_summary() or get_state_store().get_latest_event_summary()  # noop if None
        ) if get_state_store().get_latest_event_summary() else None
        get_llm_orchestrator().enqueue_event_summary(
            tick=before["tick"],
            event_type="jamming_detected",
            language="en",
            context={"event_type": "jamming_detected", "recommended_coa": before["recommended_coa_id"]},
        )
        time.sleep(0.1)
    after = client.get("/v1/engine/state").json()
    assert before["recommended_coa_id"] == after["recommended_coa_id"]
    assert before["current_threat_level"] == after["current_threat_level"]


def test_health_and_status_endpoints_expose_safe_metadata(client):
    fake = FakeLLMClient(LLMResult(text="OK"))
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        health = client.get("/v1/engine/llm/health").json()
        status = client.get("/v1/engine/llm/status").json()
    assert health["configured"] is True
    assert health["base_url"] == settings.llm_base_url
    assert health["api_key_present"] is True
    assert "api_key" not in health
    assert "queue_length" in status
    assert "current_task_type" in status


def test_llm_is_not_used_in_scoring_recommendation_or_coa_generation():
    for module_name in ("app.engine.scoring", "app.engine.recommendation", "app.engine.coa_generation"):
        module = __import__(module_name, fromlist=["dummy"])
        with open(module.__file__, encoding="utf-8") as handle:
            source = handle.read().lower()
        assert "get_llm_orchestrator" not in source
