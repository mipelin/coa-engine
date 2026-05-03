"""Tests for the forecasting module and its integration with query_engine."""

from datetime import datetime, timedelta, timezone

import pytest

from app.core.constants import EntityType, EventType
from app.core.schemas import Contact, ContactType, OperationalEvent
from app.engine.analysis_service import AnalysisContext
from app.engine.contact_engine import get_contact_engine
from app.engine.event_bus import get_event_bus
from app.engine.event_loop import get_event_loop
from app.engine.ais_feed import get_ais_feed
from app.engine.noaa_replay import get_noaa_replay_feed
from app.engine.forecasting import (
    ForecastResult,
    ForecastStep,
    _compute_confidence,
    _compute_key_changes,
    _make_injected_contacts,
    _make_injected_events,
    _propagate_contacts,
    forecast_baseline,
    forecast_with_event,
    forecast_for_coa,
    is_forecast_question,
    route_forecast_question,
    run_forecast,
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
        # Summary contains forecast-related text (may be pipeline or simulation based)
        assert result.tick_horizon > 0
        assert result.threat_level_start in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert "current_state" in result.based_on

    def test_jamming_forecast(self, client):
        _load_and_tick(client)
        result = forecast_with_event("jamming", event_lat=57.5, event_lon=18.5)
        assert result.tick_horizon > 0
        assert result.threat_level_start in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_event_forecast_vs_baseline(self, client):
        _load_and_tick(client)
        baseline = forecast_baseline(10)
        cable = forecast_with_event("cable_severance", event_lat=57.5, event_lon=19.0, horizon_ticks=10)
        # Both should produce results
        assert baseline.tick_horizon == cable.tick_horizon
        # Pipeline path includes "current_state" in based_on
        assert "current_state" in cable.based_on


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

    def test_forecast_endpoint_direct(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/forecast", json={
            "mode": "baseline",
            "horizon": 5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "expected_threat_trend" in data
        assert "confidence" in data

    def test_forecast_endpoint_what_if(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/forecast", json={
            "mode": "what_if",
            "event_action": "jamming",
            "horizon": 5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "expected_threat_trend" in data

    def test_forecast_pipeline_endpoint(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/forecast/pipeline", json={
            "horizon": 3,
            "delta_minutes": 2.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok" or "steps" in data


# ---------------------------------------------------------------------------
# Unit tests: contact propagation
# ---------------------------------------------------------------------------


def _unit_ts(minutes: int) -> datetime:
    return datetime(2025, 6, 15, 8, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def _unit_contact(*, cid="C1", eid="E1", lat=57.5, lon=19.0, speed=8.0, heading=45.0, hostile=False):
    return Contact(
        contact_id=cid, timestamp=_unit_ts(0), source="ais",
        contact_type=ContactType.VESSEL, lat=lat, lon=lon, speed=speed, heading=heading,
        confidence=0.85, entity_id=eid, is_hostile=hostile,
        attributes={"subtype": "warship", "allegiance": "hostile" if hostile else "unknown"},
    )


def _unit_event(*, eid="E1", source="ais", lat=57.5, lon=19.0, confidence=0.8):
    return OperationalEvent(
        event_id=f"EV-{eid}", timestamp=_unit_ts(0),
        event_type=EventType.VESSEL_POSITION, source=source,
        confidence=confidence, lat=lat, lon=lon, entity_id=eid,
        entity_type=EntityType.SUSPICIOUS_VESSEL,
        description="test", attributes={"heading": 45.0, "speed_knots": 8.0},
    )


def _unit_ctx(events=None, contacts=None):
    return AnalysisContext(
        events=events or [], active_contacts=contacts or [],
        source="test", tick=1, scenario_id="test", scenario_name="Test",
    )


class TestContactPropagationUnit:
    def test_stationary_contact_stays_put(self):
        contacts = [_unit_contact(speed=0.0, heading=0.0)]
        propagated = _propagate_contacts(contacts, delta_minutes=2.0)
        assert abs(propagated[0].lat - 57.5) < 0.001
        assert abs(propagated[0].lon - 19.0) < 0.001

    def test_moving_contact_advances_position(self):
        contacts = [_unit_contact(speed=10.0, heading=0.0)]
        propagated = _propagate_contacts(contacts, delta_minutes=2.0)
        assert propagated[0].lat > 57.5
        assert abs(propagated[0].lon - 19.0) < 0.001

    def test_heading_and_speed_preserved(self):
        contacts = [_unit_contact(speed=15.0, heading=90.0)]
        propagated = _propagate_contacts(contacts, delta_minutes=2.0)
        assert propagated[0].speed == 15.0
        assert propagated[0].heading == 90.0

    def test_timestamp_advances(self):
        contacts = [_unit_contact(speed=5.0, heading=0.0)]
        propagated = _propagate_contacts(contacts, delta_minutes=5.0)
        expected_ts = contacts[0].timestamp + timedelta(minutes=5.0)
        assert propagated[0].timestamp == expected_ts

    def test_original_contacts_not_mutated(self):
        contacts = [_unit_contact(speed=10.0, heading=0.0)]
        original_lat = contacts[0].lat
        _propagate_contacts(contacts, delta_minutes=2.0)
        assert contacts[0].lat == original_lat


# ---------------------------------------------------------------------------
# Unit tests: multi-step forecast
# ---------------------------------------------------------------------------


class TestMultiStepForecastUnit:
    def test_produces_n_steps(self):
        ctx = _unit_ctx(
            events=[_unit_event(eid="E1")],
            contacts=[_unit_contact(eid="E1", hostile=True)],
        )
        result = run_forecast(ctx, horizon=5)
        assert len(result.steps) == 5
        for i, step in enumerate(result.steps):
            assert step.tick_index == i

    def test_state_not_mutated(self):
        contacts = [_unit_contact(eid="E1", hostile=True)]
        events = [_unit_event(eid="E1")]
        ctx = _unit_ctx(events=events, contacts=contacts)
        original_events = list(ctx.events)
        original_contacts = list(ctx.active_contacts or [])
        run_forecast(ctx, horizon=5)
        assert ctx.events == original_events
        assert (ctx.active_contacts or []) == original_contacts

    def test_threat_trend_is_list_of_levels(self):
        ctx = _unit_ctx(
            events=[_unit_event(eid="E1")],
            contacts=[_unit_contact(eid="E1", hostile=True)],
        )
        result = run_forecast(ctx, horizon=3)
        assert len(result.threat_trend) == 3
        for level in result.threat_trend:
            assert level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_deterministic_output(self):
        ctx = _unit_ctx(
            events=[_unit_event(eid="E1")],
            contacts=[_unit_contact(eid="E1", hostile=True)],
        )
        result1 = run_forecast(ctx, horizon=3)
        result2 = run_forecast(ctx, horizon=3)
        assert result1.threat_trend == result2.threat_trend
        assert result1.expected_threat_trend == result2.expected_threat_trend

    def test_no_llm_usage(self):
        ctx = _unit_ctx(
            events=[_unit_event(eid="E1")],
            contacts=[_unit_contact(eid="E1", hostile=True)],
        )
        result = run_forecast(ctx, horizon=3)
        assert result.steps  # Should complete without LLM

    def test_empty_events_produces_forecast(self):
        ctx = _unit_ctx(events=[], contacts=[])
        result = run_forecast(ctx, horizon=3)
        assert len(result.steps) == 3
        for step in result.steps:
            assert step.threat_level == "LOW"

    def test_each_step_has_full_pipeline_outputs(self):
        ctx = _unit_ctx(
            events=[_unit_event(eid="E1")],
            contacts=[_unit_contact(eid="E1", hostile=True)],
        )
        result = run_forecast(ctx, horizon=3)
        for step in result.steps:
            assert isinstance(step.fused_tracks, list)
            assert isinstance(step.threats, list)
            assert isinstance(step.targets, list)
            assert isinstance(step.coas, list)
            assert isinstance(step.threat_level, str)
            assert isinstance(step.key_changes, list)

    def test_result_has_complete_metadata(self):
        ctx = _unit_ctx(
            events=[_unit_event(eid="E1")],
            contacts=[_unit_contact(eid="E1", hostile=True)],
        )
        result = run_forecast(ctx, horizon=3)
        assert result.horizon == 3
        assert isinstance(result.initial_state_snapshot, dict)
        assert isinstance(result.final_state_summary, dict)
        assert "canonical_pipeline" in result.based_on

    def test_different_horizons_produce_different_step_counts(self):
        ctx = _unit_ctx(
            events=[_unit_event(eid="E1")],
            contacts=[_unit_contact(eid="E1", hostile=True)],
        )
        r3 = run_forecast(ctx, horizon=3)
        r7 = run_forecast(ctx, horizon=7)
        assert len(r3.steps) == 3
        assert len(r7.steps) == 7


# ---------------------------------------------------------------------------
# Unit tests: event injection
# ---------------------------------------------------------------------------


class TestEventInjectionUnit:
    def test_injected_event_changes_outcome(self):
        ctx = _unit_ctx(
            events=[_unit_event(eid="E1")],
            contacts=[_unit_contact(eid="E1", hostile=True)],
        )
        baseline = run_forecast(ctx, horizon=3)
        inj_events = _make_injected_events("jamming", entity_id="E1", lat=57.5, lon=19.0)
        inj_contacts = _make_injected_contacts("jamming", entity_id="E1", lat=57.5, lon=19.0)
        with_event = run_forecast(ctx, horizon=3, injected_events=inj_events, injected_contacts=inj_contacts)
        assert len(with_event.steps) == 3
        assert with_event.steps[0].contacts > baseline.steps[0].contacts

    def test_cable_severance_injection(self):
        events = _make_injected_events("cable_severance", entity_id="INFRA-1", lat=57.5, lon=19.0)
        assert len(events) == 1
        assert events[0].event_type == EventType.CABLE_SEVERANCE

    def test_jamming_injection_creates_correlated_events(self):
        events = _make_injected_events("jamming", entity_id="VES-1", lat=57.5, lon=19.0)
        assert len(events) == 2
        assert events[1].source == "sigint"

    def test_new_hostile_injection(self):
        contacts = _make_injected_contacts("new_hostile", entity_id="HOSTILE-1", lat=57.5, lon=19.0)
        assert len(contacts) == 1
        assert contacts[0].is_hostile is True


# ---------------------------------------------------------------------------
# Unit tests: change tracking and trends
# ---------------------------------------------------------------------------


class TestChangeTrackingUnit:
    def test_compute_confidence_single_step(self):
        steps = [ForecastStep(tick_index=0, timestamp="T+2min", contacts=3, threat_level="LOW")]
        assert _compute_confidence(steps) == "low"

    def test_compute_confidence_many_stable_sources(self):
        steps = [
            ForecastStep(tick_index=i, timestamp=f"T+{i*2}min", contacts=8,
                         threat_level="MEDIUM", fused_tracks=[{"track_id": f"F{j}"} for j in range(4)])
            for i in range(5)
        ]
        assert _compute_confidence(steps) in ("medium", "high")

    def test_key_changes_initial_step(self):
        from app.engine.forecasting import _compute_key_changes
        changes = _compute_key_changes(None, None)
        assert isinstance(changes, list)

    def test_recommendation_changes_tracked(self):
        ctx = _unit_ctx(
            events=[_unit_event(eid="E1")],
            contacts=[_unit_contact(eid="E1", hostile=True)],
        )
        result = run_forecast(ctx, horizon=3)
        assert isinstance(result.recommendation_changes, list)

    def test_forecast_trend_is_valid(self):
        ctx = _unit_ctx(
            events=[_unit_event(eid="E1")],
            contacts=[_unit_contact(eid="E1", hostile=True)],
        )
        result = run_forecast(ctx, horizon=3)
        assert result.expected_threat_trend in ("increase", "decrease", "stable")
        assert result.confidence in ("low", "medium", "high")
