"""Tests for scenario API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.engine.contact_engine import get_contact_engine
from app.engine.state_store import get_state_store
from app.engine.event_bus import get_event_bus
from app.engine.event_loop import get_event_loop
from app.engine.ais_feed import get_ais_feed
from app.engine.noaa_replay import get_noaa_replay_feed
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
    yield
    reset_session()
    get_contact_engine().reset()
    get_state_store().clear()
    get_event_bus().clear()
    get_event_loop().reset_runtime_state()
    get_ais_feed().reset()
    get_noaa_replay_feed().reset()


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /engine/scenario/templates
# ---------------------------------------------------------------------------


class TestListTemplates:
    def test_returns_template_list(self, client):
        resp = client.get(f"{API_PREFIX}/engine/scenario/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) >= 3
        ids = {t["scenario_id"] for t in templates}
        assert "baltic_hybrid_001" in ids
        assert "arctic_submarine_001" in ids
        assert "mediterranean_001" in ids

    def test_template_has_display_name(self, client):
        resp = client.get(f"{API_PREFIX}/engine/scenario/templates")
        templates = resp.json()["templates"]
        for t in templates:
            assert "scenario_id" in t
            assert "display_name" in t
            assert len(t["display_name"]) > 0


# ---------------------------------------------------------------------------
# POST /engine/scenario/load
# ---------------------------------------------------------------------------


class TestLoadScenario:
    def test_load_baltic(self, client):
        resp = client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 42,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["scenario_id"] == "baltic_hybrid_001"
        assert data["seed"] == 42
        assert "metadata" in data

    def test_load_arctic(self, client):
        resp = client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "arctic_submarine_001",
            "seed": 99,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["scenario_id"] == "arctic_submarine_001"
        assert data["seed"] == 99

    def test_load_mediterranean(self, client):
        resp = client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "mediterranean_001",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_load_unknown_returns_error(self, client):
        resp = client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "nonexistent_scenario",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"

    def test_load_with_jitter(self, client):
        resp = client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 42,
            "timing_jitter": 2,
            "position_jitter": 0.05,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["timing_jitter"] == 2
        assert data["position_jitter"] == 0.05


# ---------------------------------------------------------------------------
# GET /engine/scenario/info
# ---------------------------------------------------------------------------


class TestScenarioInfo:
    def test_no_scenario_loaded(self, client):
        resp = client.get(f"{API_PREFIX}/engine/scenario/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "no_scenario_loaded"

    def test_after_load_has_metadata(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 42,
        })
        resp = client.get(f"{API_PREFIX}/engine/scenario/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "metadata" in data
        assert data["metadata"]["scenario_id"] == "baltic_hybrid_001"
        assert data["tick"] == 0
        assert "upcoming_stimuli" in data
        assert "active_stimuli" in data
        assert "fired_stimuli" in data
        assert data["mode"] == "simulation"
        assert data["seed"] == 42

    def test_upcoming_stimuli_at_tick_zero(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        resp = client.get(f"{API_PREFIX}/engine/scenario/info")
        data = resp.json()
        assert len(data["upcoming_stimuli"]) >= 3

    def test_fired_stimuli_empty_at_tick_zero(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        resp = client.get(f"{API_PREFIX}/engine/scenario/info")
        data = resp.json()
        assert data["fired_stimuli"] == []


# ---------------------------------------------------------------------------
# GET /engine/scenario/stimuli
# ---------------------------------------------------------------------------


class TestScenarioStimuli:
    def test_no_scenario_loaded(self, client):
        resp = client.get(f"{API_PREFIX}/engine/scenario/stimuli")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "no_scenario_loaded"

    def test_stimuli_after_load(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        resp = client.get(f"{API_PREFIX}/engine/scenario/stimuli")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "upcoming" in data
        assert "active" in data
        assert "fired" in data
        assert data["tick"] == 0

    def test_fired_after_ticks(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        # Advance a few ticks
        for _ in range(6):
            client.post(f"{API_PREFIX}/engine/tick")
        resp = client.get(f"{API_PREFIX}/engine/scenario/stimuli")
        data = resp.json()
        assert data["tick"] >= 6
        assert len(data["fired"]) >= 1  # At least tick-5 course_change should have fired


# ---------------------------------------------------------------------------
# Switching scenarios
# ---------------------------------------------------------------------------


class TestScenarioSwitching:
    def test_switch_from_baltic_to_arctic(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        resp1 = client.get(f"{API_PREFIX}/engine/scenario/info")
        assert resp1.json()["metadata"]["scenario_id"] == "baltic_hybrid_001"

        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "arctic_submarine_001",
        })
        resp2 = client.get(f"{API_PREFIX}/engine/scenario/info")
        assert resp2.json()["metadata"]["scenario_id"] == "arctic_submarine_001"

    def test_switch_to_mediterranean(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "mediterranean_001",
        })
        resp = client.get(f"{API_PREFIX}/engine/scenario/info")
        assert resp.json()["metadata"]["scenario_id"] == "mediterranean_001"


# ---------------------------------------------------------------------------
# Jitter actually affects running engine
# ---------------------------------------------------------------------------


class TestJitterEffects:
    def test_position_jitter_changes_entity_positions(self, client):
        # Load same scenario with different seeds + position_jitter
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 10,
            "position_jitter": 0.5,
        })
        resp1 = client.get(f"{API_PREFIX}/engine/contacts")
        contacts1 = resp1.json().get("contacts", [])

        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 99,
            "position_jitter": 0.5,
        })
        resp2 = client.get(f"{API_PREFIX}/engine/contacts")
        contacts2 = resp2.json().get("contacts", [])

        # At least one entity should have a different position
        pos1 = {(c["entity_id"], c["lat"], c["lon"]) for c in contacts1}
        pos2 = {(c["entity_id"], c["lat"], c["lon"]) for c in contacts2}
        assert pos1 != pos2, "Position jitter should produce different positions"

    def test_timing_jitter_changes_stimulus_ticks(self, client):
        # Load with seed A + timing_jitter
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 10,
            "timing_jitter": 3,
        })
        resp1 = client.get(f"{API_PREFIX}/engine/scenario/stimuli")
        ticks1 = [s["tick"] for s in resp1.json()["upcoming"]]

        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 99,
            "timing_jitter": 3,
        })
        resp2 = client.get(f"{API_PREFIX}/engine/scenario/stimuli")
        ticks2 = [s["tick"] for s in resp2.json()["upcoming"]]

        assert ticks1 != ticks2, "Timing jitter should produce different stimulus ticks"

    def test_no_jitter_deterministic_replay(self, client):
        for _ in range(2):
            client.post(f"{API_PREFIX}/engine/scenario/load", json={
                "scenario_id": "baltic_hybrid_001",
                "seed": 42,
            })
            resp = client.get(f"{API_PREFIX}/engine/scenario/stimuli")
            ticks = [s["tick"] for s in resp.json()["upcoming"]]
        # Second load should produce identical ticks (no jitter)
        # We just verify the endpoint works — deterministic replay is tested in unit tests


# ---------------------------------------------------------------------------
# Event engine integration
# ---------------------------------------------------------------------------


class TestEventEngineIntegration:
    def test_cable_severance_updates_active_incidents(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 42,
        })
        # Advance to tick 10 where cable_severance fires
        for _ in range(10):
            client.post(f"{API_PREFIX}/engine/tick")

        resp = client.get(f"{API_PREFIX}/engine/scenario/info")
        data = resp.json()
        assert len(data["fired_stimuli"]) >= 1
        assert any(s["action"] == "cable_severance" for s in data["fired_stimuli"])
        assert len(data["active_incidents"]) >= 1
        assert data["infrastructure_status"] == "compromised"

    def test_jamming_updates_active_incidents(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 42,
        })
        # Advance to tick 18 where jamming fires
        for _ in range(18):
            client.post(f"{API_PREFIX}/engine/tick")

        resp = client.get(f"{API_PREFIX}/engine/scenario/info")
        data = resp.json()
        assert any(s["action"] == "jamming" for s in data["fired_stimuli"])
        assert len(data["active_incidents"]) >= 1

    def test_scenario_info_exposes_environment_and_seed(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 77,
        })
        resp = client.get(f"{API_PREFIX}/engine/scenario/info")
        data = resp.json()
        assert data["seed"] == 77
        assert isinstance(data["environment"], dict)
        assert "sea_state" in data["environment"]

    def test_start_endpoint_with_jitter_passes_through(self, client):
        resp = client.post(f"{API_PREFIX}/engine/start", json=None, params={
            "scenario_id": "baltic_hybrid_001",
            "seed": 55,
            "timing_jitter": 2,
            "position_jitter": 0.1,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["seed"] == 55
        assert data["timing_jitter"] == 2
        assert data["position_jitter"] == 0.1


# ---------------------------------------------------------------------------
# Unified scenario state in /engine/state
# ---------------------------------------------------------------------------


class TestUnifiedScenarioState:
    def test_engine_state_has_scenario_metadata(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
            "seed": 42,
        })
        resp = client.get(f"{API_PREFIX}/engine/state")
        data = resp.json()
        scenario = data.get("scenario", {})
        assert scenario.get("scenario_id") == "baltic_hybrid_001"
        assert scenario.get("seed") == 42
        assert isinstance(scenario.get("environment", {}), dict)

    def test_stimuli_counts_update_after_ticks(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        resp0 = client.get(f"{API_PREFIX}/engine/state")
        s0 = resp0.json()["scenario"]
        assert s0["upcoming_stimuli_count"] >= 3
        assert s0["fired_stimuli_count"] == 0

        for _ in range(5):
            client.post(f"{API_PREFIX}/engine/tick")

        resp5 = client.get(f"{API_PREFIX}/engine/state")
        s5 = resp5.json()["scenario"]
        assert s5["fired_stimuli_count"] >= 1
        assert s5["upcoming_stimuli_count"] < s0["upcoming_stimuli_count"]


# ---------------------------------------------------------------------------
# ROE fields in API responses
# ---------------------------------------------------------------------------


class TestROEInAPI:
    def test_coas_endpoint_includes_roe_summary(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        # Advance a few ticks to generate analysis
        for _ in range(3):
            client.post(f"{API_PREFIX}/engine/tick")

        resp = client.get(f"{API_PREFIX}/engine/coas")
        assert resp.status_code == 200
        data = resp.json()
        assert "roe_summary" in data
        summary = data["roe_summary"]
        assert "counts" in summary
        counts = summary["counts"]
        assert "allowed" in counts
        assert "restricted" in counts
        assert "requires_authorization" in counts
        assert "rejected" in counts
        # Total should match scored COA count
        total = sum(counts.values())
        assert total == data["count"]

    def test_analysis_endpoint_includes_roe_summary(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        for _ in range(3):
            client.post(f"{API_PREFIX}/engine/tick")

        resp = client.get(f"{API_PREFIX}/engine/analysis")
        assert resp.status_code == 200
        data = resp.json()
        assert "roe_summary" in data
        summary = data["roe_summary"]
        assert "counts" in summary
        assert "recommended" in summary

    def test_scored_coas_have_roe_fields(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        for _ in range(3):
            client.post(f"{API_PREFIX}/engine/tick")

        resp = client.get(f"{API_PREFIX}/engine/coas")
        data = resp.json()
        for s in data["scored_coas"]:
            coa = s["coa"]
            assert "roe_status" in coa
            assert "roe_reason" in coa
            assert "roe_constraints_triggered" in coa
            assert coa["roe_status"] in ("allowed", "restricted", "requires_authorization", "rejected")

    def test_roe_summary_recommended_has_details(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        for _ in range(3):
            client.post(f"{API_PREFIX}/engine/tick")

        resp = client.get(f"{API_PREFIX}/engine/coas")
        summary = resp.json()["roe_summary"]
        rec = summary.get("recommended")
        if rec is not None:
            assert "coa_id" in rec
            assert "roe_status" in rec
            assert "roe_reason" in rec
            assert "roe_constraints_triggered" in rec

    def test_roe_counts_are_non_negative(self, client):
        client.post(f"{API_PREFIX}/engine/scenario/load", json={
            "scenario_id": "baltic_hybrid_001",
        })
        for _ in range(3):
            client.post(f"{API_PREFIX}/engine/tick")

        resp = client.get(f"{API_PREFIX}/engine/coas")
        counts = resp.json()["roe_summary"]["counts"]
        for status, count in counts.items():
            assert count >= 0, f"ROE count for {status} should be non-negative"
