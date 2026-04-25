from app.core.schemas import OperationalEvent, Scenario
from app.engine.event_ingestion import load_sample_scenario, load_scenario_events
from app.main import app

from fastapi.testclient import TestClient

client = TestClient(app)


# --- Health endpoint ---


def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


# --- Scenario endpoint ---


def test_sample_scenario_returns_valid_json():
    resp = client.get("/v1/scenario/sample")
    assert resp.status_code == 200
    body = resp.json()
    assert body["scenario_id"] == "baltic_hybrid_001"
    assert "events" in body
    assert len(body["events"]) == 20


def test_sample_scenario_validates_as_scenario_model():
    resp = client.get("/v1/scenario/sample")
    scenario = Scenario.model_validate(resp.json())
    assert scenario.scenario_id == "baltic_hybrid_001"
    assert len(scenario.events) > 0
    assert "VES-SUSP-001" in scenario.entities


def test_sample_scenario_event_ids_are_unique():
    scenario = load_sample_scenario()
    event_ids = [event.event_id for event in scenario.events]
    assert len(event_ids) == len(set(event_ids))


# --- Scenario listing ---


def test_scenario_list_endpoint():
    resp = client.get("/v1/scenario/list")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["scenarios"]) >= 1


def test_scenario_load_endpoint():
    resp = client.post("/v1/scenario/load/baltic_hybrid_001")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["events_loaded"] > 0


def test_session_status_endpoint():
    resp = client.get("/v1/scenario/session/status")
    assert resp.status_code == 200
    body = resp.json()
    assert "event_count" in body


# --- Event ingestion ---


def test_load_scenario_events_returns_operational_events():
    events = load_scenario_events()
    assert len(events) > 0
    for e in events:
        assert isinstance(e, OperationalEvent)


def test_load_sample_scenario_returns_scenario():
    scenario = load_sample_scenario()
    assert isinstance(scenario, Scenario)
    assert scenario.name == "Baltic Sea Hybrid Threat Scenario"


def test_ingest_accepts_valid_event_batch(sample_event_json):
    resp = client.post("/v1/events/ingest", json={"events": [sample_event_json]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["events_received"] == 1
    assert "total_events_in_session" in body


def test_ingest_rejects_invalid_event():
    resp = client.post("/v1/events/ingest", json={"events": [{"event_id": "BAD"}]})
    assert resp.status_code == 422


def test_events_list_endpoint():
    resp = client.get("/v1/events/list")
    assert resp.status_code == 200
    body = resp.json()
    assert "count" in body
    assert "events" in body


# --- Placeholder analysis/COA endpoints ---


def test_analysis_run_returns_ok():
    resp = client.post("/v1/analysis/run", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["events_processed"] > 0
    assert len(body["features"]) == body["events_processed"]
    assert len(body["anomalies"]) == body["events_processed"]
    assert len(body["threats"]) > 0


def test_coa_generate_returns_coas():
    resp = client.post("/v1/coa/generate", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert len(body["coas"]) >= 3


def test_simulation_run_returns_results():
    resp = client.post("/v1/coa/simulation/run", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert len(body["simulations"]) >= 3


def test_recommendation_run_returns_recommendation():
    resp = client.post("/v1/coa/recommendation/run", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["recommended"] is not None
    assert body["recommended"]["rank"] == 1


def test_briefing_generate_returns_briefing():
    resp = client.post("/v1/coa/briefing/generate", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert "situation" in body
    assert "recommended_coa" in body
