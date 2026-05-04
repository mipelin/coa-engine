"""End-to-end tests exercising the full pipeline through TestClient."""

import json

from app.core.schemas import Scenario
from app.engine.event_ingestion import load_scenario_events
from app.main import app

from fastapi.testclient import TestClient

client = TestClient(app)

UNSAFE_WORDS = [
    "target", "weapon", "strike", "engage", "kill", "lethal",
    "execute order", "fire", "destroy", "neutralize",
]


def _full_pipeline():
    """Hit every endpoint in sequence and return all responses."""
    health = client.get("/health")
    scenario = client.get("/v1/scenario/sample")
    analysis = client.post("/v1/analysis/run", json={})
    coas = client.post("/v1/coa/generate", json={})
    sim = client.post("/v1/coa/simulation/run", json={})
    rec = client.post("/v1/coa/recommendation/run", json={})
    briefing = client.post("/v1/coa/briefing/generate", json={})
    return {
        "health": health,
        "scenario": scenario,
        "analysis": analysis,
        "coas": coas,
        "sim": sim,
        "rec": rec,
        "briefing": briefing,
    }


def test_all_endpoints_return_200():
    results = _full_pipeline()
    for name, resp in results.items():
        assert resp.status_code == 200, f"{name} returned {resp.status_code}"


def test_dashboard_route_returns_html():
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert "COA ENGINE" in resp.text
    assert "Guide" in resp.text
    assert "Select a scenario and click Start" in resp.text
    assert "Quick Scenarios" in resp.text
    assert "Jamming Event" in resp.text
    assert "Add suspicious vessel now" in resp.text
    assert "Show Advanced Placement" in resp.text
    assert "Maritime Threat Near Cable" in resp.text
    assert "Generating Briefing..." in resp.text
    assert "Undo Last Injection" in resp.text
    assert "Reset Scenario" in resp.text
    assert "Why Changed" in resp.text
    assert "Show Cable Routes" in resp.text
    assert "Show NOAA Replay Traffic" in resp.text
    assert "Why This COA Won" in resp.text
    assert "Asset pool source" in resp.text
    assert 'data-i18n-placeholder="query.input_placeholder"' in resp.text
    assert 'data-q-key="query.chip.threat_question"' in resp.text
    assert 'data-i18n="query.ask_btn"' in resp.text


def test_root_redirects_to_dashboard():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"] == "/dashboard"


def test_health_structure():
    resp = client.get("/health")
    body = resp.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.2.0"


def test_scenario_validates():
    resp = client.get("/v1/scenario/sample")
    scenario = Scenario.model_validate(resp.json())
    assert scenario.scenario_id == "baltic_hybrid_001"
    assert len(scenario.events) == 20
    assert len(scenario.entities) == 11
    assert len(scenario.critical_infrastructure) == 4


def test_analysis_pipeline_completes():
    resp = client.post("/v1/analysis/run", json={})
    body = resp.json()
    assert body["status"] == "ok"
    assert body["events_processed"] == 20
    assert body["features_computed"] == 20
    assert len(body["features"]) == 20
    assert len(body["anomalies"]) == 20
    assert len(body["threats"]) > 0

    # At least one HIGH/CRITICAL threat
    assert any(t["threat_level"] in ("HIGH", "CRITICAL") for t in body["threats"])

    # Cable severance event should be HIGH or CRITICAL anomaly
    e007 = next(a for a in body["anomalies"] if a["event_id"] == "E007")
    assert e007["anomaly_level"] in ("CRITICAL", "HIGH")


def test_coa_generation_completes():
    resp = client.post("/v1/coa/generate", json={})
    body = resp.json()
    assert body["status"] == "ok"
    assert len(body["coas"]) >= 5
    assert len(body["threat_context"]) > 0

    for coa in body["coas"]:
        assert coa["coa_id"]
        assert coa["template_id"]
        assert coa["title"]
        assert coa["source"] == "template_engine"
        assert len(coa["required_assets"]) > 0


def test_simulation_completes():
    resp = client.post("/v1/coa/simulation/run", json={})
    body = resp.json()
    assert body["status"] == "ok"
    assert len(body["simulations"]) >= 5
    for sim in body["simulations"]:
        assert 0.0 <= sim["success_probability"] <= 1.0
        assert 0.0 <= sim["escalation_probability"] <= 1.0
        assert sim["simulation_runs"] > 0
        assert len(sim["confidence_interval"]) == 2


def test_recommendation_completes():
    resp = client.post("/v1/coa/recommendation/run", json={})
    body = resp.json()
    assert body["recommended"]["rank"] == 1
    assert "recommended_package" in body
    if body["recommended_package"] is not None:
        assert len(body["recommended_package"]["coas"]) >= 2
    assert len(body["rationale"]) > 0
    assert len(body["alternatives"]) >= 1
    assert len(body["edge_cases"]) > 0


def test_briefing_completes():
    resp = client.post("/v1/coa/briefing/generate", json={})
    body = resp.json()
    assert body["situation"]
    assert len(body["key_indicators"]) > 0
    assert body["assessment"]
    assert len(body["coas_considered"]) >= 3
    assert body["recommended_coa"]
    assert len(body["risks"]) > 0
    assert body["confidence"] in ("LOW", "MEDIUM", "HIGH")
    assert len(body["assumptions"]) > 0


def test_full_pipeline_no_unsafe_language():
    """All generated outputs must be free of unsafe military language."""
    results = _full_pipeline()

    texts_to_check = []
    # COA titles and descriptions
    for coa in results["coas"].json()["coas"]:
        texts_to_check.append(f"{coa['title']} {coa['description']}")
    # Briefing
    briefing = results["briefing"].json()
    texts_to_check.append(briefing["situation"])
    texts_to_check.append(briefing["assessment"])
    texts_to_check.append(briefing["recommended_coa"])
    texts_to_check.extend(briefing["risks"])

    all_text = " ".join(texts_to_check).lower()
    for word in UNSAFE_WORDS:
        assert word not in all_text, f"Unsafe word '{word}' found in generated outputs"


def test_all_endpoint_outputs_serialize_to_json():
    results = _full_pipeline()
    for name, resp in results.items():
        body = resp.json()
        serialized = json.dumps(body)
        assert len(serialized) > 0, f"{name} produced empty JSON"
        re_parsed = json.loads(serialized)
        assert re_parsed is not None


def test_event_ingestion_via_endpoint():
    events = load_scenario_events()
    payload = {
        "events": [e.model_dump(mode="json") for e in events[:3]]
    }
    resp = client.post("/v1/events/ingest", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["events_received"] == 3
    assert len(body["event_ids"]) == 3


def test_pipeline_deterministic():
    """Running the pipeline twice produces identical results."""
    r1 = client.post("/v1/coa/recommendation/run", json={}).json()
    r2 = client.post("/v1/coa/recommendation/run", json={}).json()
    assert r1["recommended"]["coa"]["coa_id"] == r2["recommended"]["coa"]["coa_id"]
    assert r1["recommended"]["total_score"] == r2["recommended"]["total_score"]


def test_recommendation_endpoint_accepts_asset_inventory():
    resp = client.post("/v1/coa/recommendation/run", json={
        "asset_inventory": {
            "isr_uav": 0,
            "maritime_patrol_asset": 0,
            "coast_guard_liaison": 0,
        }
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "no_viable_coa"
    assert body["recommended"] is None
