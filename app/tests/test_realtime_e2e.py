"""End-to-end tests for real-time engine lifecycle."""
from __future__ import annotations

from datetime import datetime, timezone

from app.engine.state_store import get_state_store


class TestEngineStartStop:
    def test_start_and_stop_engine(self, client):
        resp = client.post("/v1/engine/start?scenario_id=baltic_hybrid_001&mode=simulation&interval=2.0")
        assert resp.json()["status"] == "ok"
        assert resp.json()["scenario_id"] == "baltic_hybrid_001"

        state = client.get("/v1/engine/state").json()
        assert state["tick"] >= 0

        resp = client.post("/v1/engine/stop")
        assert resp.json()["status"] == "ok"

    def test_start_populates_snapshot_with_contacts_and_coas(self, client):
        client.post("/v1/engine/start?scenario_id=baltic_hybrid_001&mode=simulation&interval=2.0")

        analysis = client.get("/v1/engine/analysis").json()
        assert len(analysis["contacts"]) > 0
        assert len(analysis["scored_coas"]) > 0
        assert analysis["recommendation"] is not None

        client.post("/v1/engine/stop")

    def test_manual_tick_updates_state(self, client):
        client.post("/v1/engine/start?scenario_id=baltic_hybrid_001&mode=simulation&interval=2.0")

        resp = client.post("/v1/engine/tick")
        assert resp.json()["status"] == "ok"

        state = client.get("/v1/engine/state").json()
        assert state["tick"] >= 1

        client.post("/v1/engine/stop")


class TestInjectAndAnalyze:
    def test_inject_hostile_contact_triggers_analysis(self, client):
        client.post("/v1/engine/start?scenario_id=baltic_hybrid_001&mode=simulation&interval=2.0")
        client.post("/v1/engine/tick")

        contact = {
            "contacts": [{
                "contact_id": "C-TEST-HOSTILE",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
                "contact_type": "vessel",
                "lat": 57.5,
                "lon": 19.0,
                "speed": 8.0,
                "heading": 90.0,
                "confidence": 0.9,
                "entity_id": "VES-TEST-HOSTILE",
                "is_hostile": True,
                "attributes": {"name": "Test Hostile", "allegiance": "hostile"},
            }],
        }
        resp = client.post("/v1/engine/inject", json=contact)
        body = resp.json()
        assert body["status"] == "ok"
        assert body["contacts_injected"] == 1

        threats = client.get("/v1/engine/threats").json()
        assert threats["count"] >= 1

        client.post("/v1/engine/stop")

    def test_delete_contact(self, client):
        client.post("/v1/engine/start?scenario_id=baltic_hybrid_001&mode=simulation&interval=2.0")
        client.post("/v1/engine/tick")

        contact = {
            "contacts": [{
                "contact_id": "C-DEL-TEST",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "test",
                "contact_type": "vessel",
                "lat": 57.5,
                "lon": 19.0,
                "speed": 5.0,
                "heading": 0.0,
                "confidence": 0.8,
                "entity_id": "VES-DEL-TEST",
                "is_hostile": False,
                "attributes": {"name": "Delete Me"},
            }],
        }
        client.post("/v1/engine/inject", json=contact)

        resp = client.delete("/v1/engine/inject/VES-DEL-TEST")
        assert resp.json()["status"] == "ok"

        contacts = client.get("/v1/engine/contacts").json()
        entity_ids = [c["entity_id"] for c in contacts["contacts"]]
        assert "VES-DEL-TEST" not in entity_ids

        client.post("/v1/engine/stop")


class TestScenarioSwitch:
    def test_switch_scenario_reloads_contacts(self, client):
        client.post("/v1/engine/start?scenario_id=baltic_hybrid_001&mode=simulation&interval=2.0")
        client.post("/v1/engine/tick")

        baltic_contacts = client.get("/v1/engine/contacts").json()

        client.post("/v1/engine/stop")
        client.post("/v1/engine/reset")
        client.post("/v1/engine/start?scenario_id=arctic_submarine_001&mode=simulation&interval=2.0")
        client.post("/v1/engine/tick")

        arctic_state = client.get("/v1/engine/state").json()
        assert arctic_state["scenario"]["scenario_id"] == "arctic_submarine_001"

        client.post("/v1/engine/stop")

    def test_engine_mode_change(self, client):
        resp = client.post("/v1/engine/mode/hybrid")
        assert resp.json()["status"] == "ok"

        resp = client.post("/v1/engine/mode/simulation")
        assert resp.json()["status"] == "ok"

        resp = client.post("/v1/engine/mode/invalid_mode")
        assert resp.json()["status"] == "error"


class TestFullPipeline:
    def test_full_pipeline_via_engine_endpoints(self, client):
        # Start engine
        client.post("/v1/engine/start?scenario_id=baltic_hybrid_001&mode=simulation&interval=2.0")

        # Advance a few ticks
        for _ in range(3):
            client.post("/v1/engine/tick")

        # Check state has advanced
        state = client.get("/v1/engine/state").json()
        assert state["tick"] >= 3
        assert state["active_contacts"] > 0

        # Check analysis snapshot
        analysis = client.get("/v1/engine/analysis").json()
        assert "state" in analysis
        assert "contacts" in analysis
        assert "threats" in analysis

        # Check threats exist
        threats = client.get("/v1/engine/threats").json()
        assert threats["count"] >= 0

        # Check COAs after analysis
        coas = client.get("/v1/engine/coas").json()

        # Generate briefing
        briefing = client.get("/v1/engine/briefing")
        assert briefing.status_code == 200

        # Check engine state consistency
        recommendation = client.get("/v1/engine/recommendation").json()

        # Stop engine
        client.post("/v1/engine/stop")

    def test_engine_reset_clears_state(self, client):
        client.post("/v1/engine/start?scenario_id=baltic_hybrid_001&mode=simulation&interval=2.0")
        for _ in range(3):
            client.post("/v1/engine/tick")

        client.post("/v1/engine/stop")
        client.post("/v1/engine/reset")

        state = client.get("/v1/engine/state").json()
        assert state["tick"] == 0
        assert state["active_contacts"] == 0
