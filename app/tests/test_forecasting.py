"""Tests for the forecasting module and its integration with query_engine."""

import pytest

from app.engine.contact_engine import get_contact_engine
from app.engine.event_bus import get_event_bus
from app.engine.event_loop import get_event_loop
from app.engine.ais_feed import get_ais_feed
from app.engine.noaa_replay import get_noaa_replay_feed
from app.engine.forecasting import (
    ForecastResult,
    forecast_baseline,
    forecast_with_event,
    forecast_for_coa,
    is_forecast_question,
    route_forecast_question,
)
from app.engine.query_engine import answer_question
from app.engine.state_store import get_state_store
from app.core.config import settings
from app.core.session import reset_session
from app.main import app

API_PREFIX = "/v1"


@pytest.fixture(autouse=True)
def clean_engine():
    reset_session()
    get_contact_engine().reset()
    get_state_store().clear()
    get_event_bus().clear()
    get_event_loop().reset_runtime_state()
    get_ais_feed().reset()
    get_noaa_replay_feed().reset()
    original = settings.llm_enabled
    settings.llm_enabled = False
    import app.engine.llm_client as _lc
    _lc._llm_client = None
    yield
    settings.llm_enabled = original
    _lc._llm_client = None
    reset_session()
    get_contact_engine().reset()
    get_state_store().clear()
    get_event_bus().clear()
    get_event_loop().reset_runtime_state()
    get_ais_feed().reset()
    get_noaa_replay_feed().reset()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)


def _load_and_tick(client, scenario_id="baltic_hybrid_001", ticks=5):
    client.post(f"{API_PREFIX}/engine/scenario/load", json={"scenario_id": scenario_id})
    for _ in range(ticks):
        client.post(f"{API_PREFIX}/engine/tick")


# ---------------------------------------------------------------------------
# is_forecast_question
# ---------------------------------------------------------------------------


class TestForecastDetection:
    @pytest.mark.parametrize("question", [
        "What if the cable is severed?",
        "What happens if we choose COA-TPL-ISR?",
        "If we pick the shadow COA, what changes?",
        "How would threat evolve in the next 30 minutes?",
        "Forecast the next few ticks",
        "What would happen if jamming starts?",
        "Simulate the next 10 ticks",
        "How will threat look ahead?",
    ])
    def test_detected_as_forecast(self, question):
        assert is_forecast_question(question)

    @pytest.mark.parametrize("question", [
        "Why is the current COA recommended?",
        "What changed in the last few ticks?",
        "Which contacts are driving the risk?",
        "What COAs require authorization?",
    ])
    def test_not_detected_as_forecast(self, question):
        assert not is_forecast_question(question)


# ---------------------------------------------------------------------------
# Baseline forecast
# ---------------------------------------------------------------------------


class TestBaselineForecast:
    def test_forecast_without_scenario(self):
        result = forecast_baseline(10)
        assert "No scenario loaded" in result.summary
        assert result.expected_threat_trend == "stable"
        assert result.based_on == []

    def test_forecast_with_scenario(self, client):
        _load_and_tick(client)
        result = forecast_baseline(10)
        assert result.tick_horizon == 10
        assert result.threat_level_start in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert result.expected_threat_trend in ("increase", "decrease", "stable")
        assert "simulation" in result.based_on

    def test_forecast_generates_contacts(self, client):
        _load_and_tick(client)
        result = forecast_baseline(5)
        assert result.tick_horizon == 5
        assert result.contacts_end > 0


# ---------------------------------------------------------------------------
# Event-based forecast
# ---------------------------------------------------------------------------


class TestEventForecast:
    def test_cable_severance_forecast(self, client):
        _load_and_tick(client)
        result = forecast_with_event("cable_severance", event_lat=57.5, event_lon=19.0)
        assert "cable_severance" in result.summary
        assert len(result.key_risks) > 0
        assert any("cable" in r.lower() for r in result.key_risks)
        assert "hypothetical_event" in result.based_on

    def test_jamming_forecast(self, client):
        _load_and_tick(client)
        result = forecast_with_event("jamming", event_lat=57.5, event_lon=18.5)
        assert "jamming" in result.summary
        assert any("jamming" in r.lower() or "communication" in r.lower() for r in result.key_risks)

    def test_event_forecast_vs_baseline(self, client):
        _load_and_tick(client)
        baseline = forecast_baseline(10)
        cable = forecast_with_event("cable_severance", event_lat=57.5, event_lon=19.0, horizon_ticks=10)
        # Both should produce results
        assert baseline.tick_horizon == cable.tick_horizon
        # Cable event forecast should note hypothetical
        assert "hypothetical_event" in cable.based_on
        assert "hypothetical_event" not in baseline.based_on


# ---------------------------------------------------------------------------
# COA forecast
# ---------------------------------------------------------------------------


class TestCOAForecast:
    def test_forecast_for_existing_coa(self, client):
        _load_and_tick(client)
        scored = get_state_store().get_scored_coas()
        assert len(scored) > 0, "Need at least one COA for forecast test"
        result = forecast_for_coa(scored[0].coa.title)
        assert scored[0].coa.title in result.summary or "COA" in result.summary
        assert result.threat_level_start in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert "coa_scoring" in result.based_on

    def test_different_coas_produce_different_outcomes(self, client):
        _load_and_tick(client)
        scored = get_state_store().get_scored_coas()
        if len(scored) < 2:
            pytest.skip("Need at least 2 COAs")
        result_a = forecast_for_coa(scored[0].coa.title)
        result_b = forecast_for_coa(scored[1].coa.title)
        # Different COAs should have different summaries or outcomes
        assert result_a.summary != result_b.summary or result_a.key_risks != result_b.key_risks

    def test_forecast_for_nonexistent_coa(self, client):
        _load_and_tick(client)
        result = forecast_for_coa("Nonexistent COA XYZ")
        assert "not found" in result.summary


# ---------------------------------------------------------------------------
# No state mutation
# ---------------------------------------------------------------------------


class TestForecastNoMutation:
    def test_forecast_does_not_change_engine_state(self, client):
        _load_and_tick(client)
        tick_before = client.get(f"{API_PREFIX}/engine/state").json()["tick"]
        threats_before = client.get(f"{API_PREFIX}/engine/threats").json()["count"]

        route_forecast_question("What if the cable is severed?")
        forecast_baseline(10)
        forecast_with_event("cable_severance", event_lat=57.5, event_lon=19.0)

        tick_after = client.get(f"{API_PREFIX}/engine/state").json()["tick"]
        threats_after = client.get(f"{API_PREFIX}/engine/threats").json()["count"]

        assert tick_before == tick_after
        assert threats_before == threats_after


# ---------------------------------------------------------------------------
# Integration with query engine
# ---------------------------------------------------------------------------


class TestForecastViaQueryEngine:
    def test_forecast_question_routes_to_forecasting(self, client):
        _load_and_tick(client)
        result = answer_question("What if the cable is severed?")
        assert result["llm_used"] is False
        assert "forecast" in result
        assert result["forecast"]["expected_threat_trend"] in ("increase", "decrease", "stable")

    def test_what_if_coa_question(self, client):
        _load_and_tick(client)
        scored = get_state_store().get_scored_coas()
        if not scored:
            pytest.skip("No COAs")
        result = answer_question(f"What happens if we choose {scored[0].coa.title}?")
        assert "forecast" in result
        assert result["forecast"]["threat_level_start"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_next_threat_question(self, client):
        _load_and_tick(client)
        result = answer_question("How would threat evolve in the next 30 minutes?")
        assert "forecast" in result
        assert result["forecast"]["tick_horizon"] > 0

    def test_non_forecast_question_no_forecast_field(self, client):
        _load_and_tick(client)
        result = answer_question("What is the current threat level?")
        # Non-forecast questions should not have forecast field (or it should be absent)
        # The query engine only adds forecast for forecast questions
        assert "forecast" not in result or result.get("forecast") is None

    def test_unsafe_forecast_question_refused(self):
        result = answer_question("What happens if we authorize engagement?")
        assert "refuse" in result["answer"].lower() or "guardrails" in result["sources_used"]
        assert result["llm_used"] is False


# ---------------------------------------------------------------------------
# API endpoint
# ---------------------------------------------------------------------------


class TestForecastEndpoint:
    def test_endpoint_returns_forecast(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/query", json={
            "question": "What if the cable is severed?"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "forecast" in data
        assert data["forecast"]["expected_threat_trend"] in ("increase", "decrease", "stable")

    def test_endpoint_baseline_forecast(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/query", json={
            "question": "How would threat evolve ahead?"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "forecast" in data
