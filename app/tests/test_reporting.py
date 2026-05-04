from __future__ import annotations

from unittest.mock import patch

from app.engine.llm_client import LLMResult
from app.engine.llm_orchestrator import reset_llm_orchestrator
from app.engine.reporting_context import build_reporting_context


class FakeLLMClient:
    enabled = True

    def __init__(self, text: str = "Based on the current system state, report generated.") -> None:
        self.text = text
        self.calls: list[tuple[str, str, int | None]] = []

    def chat_sync(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> LLMResult:
        self.calls.append((system_prompt, user_prompt, max_tokens))
        return LLMResult(text=self.text)


def _run_scenario(client, ticks: int = 4) -> None:
    assert client.post("/v1/engine/reset").status_code == 200
    assert client.post("/v1/engine/start", params={"scenario_id": "baltic_hybrid_001", "interval": 2.0}).status_code == 200
    for _ in range(ticks):
        assert client.post("/v1/engine/tick").status_code == 200


def test_reporting_context_aggregates_required_structured_data(client):
    _run_scenario(client)
    context = build_reporting_context().to_dict()

    for key in (
        "scenario",
        "replay_timeline",
        "fused_tracks_evolution",
        "threat_level_progression",
        "coa_recommendations_over_time",
        "selected_recommendation",
        "operational_effects",
        "asset_assignments",
        "roe_status",
    ):
        assert key in context
    assert context["replay_timeline"]["snapshot_count"] > 0


def test_report_endpoint_generates_aar_from_structured_payload(client):
    _run_scenario(client)
    fake = FakeLLMClient("1. Executive Summary\nBased on the current system state, report generated from structured replay data.")
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        resp = client.get("/v1/engine/report", params={"type": "aar", "lang": "en"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "aar"
    assert data["llm_used"] is True
    assert "Executive Summary" in data["text"]
    system_prompt, user_prompt, max_tokens = fake.calls[0]
    assert "Use ONLY provided structured data" in system_prompt
    assert "Data:" in user_prompt
    assert "replay_timeline" in user_prompt
    assert max_tokens >= 1500


def test_report_endpoint_generates_combined_mode(client):
    _run_scenario(client)
    fake = FakeLLMClient("Based on the current system state, report generated from structured replay data.")
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        resp = client.get("/v1/engine/report", params={"type": "combined", "lang": "en"})

    data = resp.json()
    assert data["mode"] == "combined"
    assert "briefing" in data
    assert "aar" in data
    assert "COMMANDER BRIEFING" in data["text"]
    assert len(fake.calls) == 2


def test_report_falls_back_when_llm_contradicts_state(client):
    _run_scenario(client)
    fake = FakeLLMClient("Threat level LOW. COA-BOGUS is present.")
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        resp = client.get("/v1/engine/report", params={"type": "briefing", "lang": "en"})

    data = resp.json()
    assert data["mode"] == "briefing"
    assert data["llm_used"] is False
    assert data["fallback_reason"] == "llm_state_mismatch"


def test_report_pdf_endpoint_returns_pdf(client):
    _run_scenario(client)
    fake = FakeLLMClient("Based on the current system state, report generated from structured replay data.")
    reset_llm_orchestrator()
    with patch("app.engine.llm_orchestrator.get_llm_client", return_value=fake):
        resp = client.get("/v1/engine/report/pdf", params={"type": "combined", "lang": "en"})

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")
