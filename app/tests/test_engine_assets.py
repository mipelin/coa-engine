from datetime import datetime, timezone

from app.core.schemas import Contact, ContactType
from app.engine.asset_state import build_simulated_asset_states
from app.engine.event_ingestion import load_scenario_events
from app.engine.state_store import StateStore


def test_inventory_to_asset_states_normalizes_available_quantities():
    states = StateStore.inventory_to_asset_states({
        "isr_uav": 2,
        "maritime_patrol_asset": 0,
    })

    by_id = {state.asset_id: state for state in states}

    assert by_id["isr_uav"].quantity_total == 2
    assert by_id["isr_uav"].quantity_available == 2
    assert by_id["isr_uav"].status == "available"
    assert by_id["maritime_patrol_asset"].status == "unavailable"


def test_simulated_asset_states_include_realistic_operational_fields():
    states = build_simulated_asset_states(
        {"isr_uav": 2, "maritime_patrol_vessel": 1},
        load_scenario_events()[:3],
    )
    by_id = {state.asset_id: state for state in states}
    assert by_id["isr_uav"].home_base == "Visby Airfield"
    assert by_id["isr_uav"].response_eta_min == 25
    assert by_id["isr_uav"].on_station_hours and by_id["isr_uav"].on_station_hours > 0
    assert by_id["isr_uav"].lat is not None
    assert by_id["maritime_patrol_vessel"].home_base == "Slite Patrol Anchorage"
    assert by_id["maritime_patrol_vessel"].endurance_hours and by_id["maritime_patrol_vessel"].endurance_hours >= 24


def test_engine_assets_endpoint_updates_central_state(client):
    resp = client.post("/v1/engine/assets", json=[
        {
            "asset_id": "isr_uav",
            "asset_type": "isr_uav",
            "quantity_total": 2,
            "quantity_available": 1,
            "status": "available",
            "domain": "air",
            "display_name": "ISR UAV",
        },
        {
            "asset_id": "maritime_patrol_asset",
            "asset_type": "maritime_patrol_asset",
            "quantity_total": 1,
            "quantity_available": 0,
            "status": "unavailable",
            "domain": "maritime",
            "display_name": "Patrol Vessel",
        },
    ])
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert len(body["assets"]) == 2

    state = client.get("/v1/engine/state").json()
    assert state["active_asset_types"] == 2
    assert state["available_asset_units"] == 1
    assert state["scenario"]["mode"] == "simulation"

    assets = client.get("/v1/engine/assets").json()
    assert assets["count"] == 2
    by_id = {asset["asset_id"]: asset for asset in assets["assets"]}
    assert by_id["isr_uav"]["quantity_available"] == 1
    assert by_id["maritime_patrol_asset"]["status"] == "unavailable"


def test_recommendation_endpoint_accepts_asset_states(client):
    resp = client.post("/v1/coa/recommendation/run", json={
        "asset_states": [
            {
                "asset_id": "isr_uav",
                "asset_type": "isr_uav",
                "quantity_total": 0,
                "quantity_available": 0,
                "status": "unavailable",
            },
            {
                "asset_id": "maritime_patrol_asset",
                "asset_type": "maritime_patrol_asset",
                "quantity_total": 0,
                "quantity_available": 0,
                "status": "unavailable",
            },
            {
                "asset_id": "coast_guard_liaison",
                "asset_type": "coast_guard_liaison",
                "quantity_total": 0,
                "quantity_available": 0,
                "status": "unavailable",
            },
        ],
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["recommended"]["coa"]["source"] == "template_engine"
    assert body["recommended"]["coa"]["feasibility_status"] in ("feasible", "partially_feasible", "infeasible")


def test_manual_injection_forces_immediate_reanalysis(client):
    client.post("/v1/engine/reset")
    client.post("/v1/engine/scenario/baltic_hybrid_001")
    resp = client.post("/v1/engine/inject", json={
        "contacts": [
            {
                "contact_id": "MANUAL-JAM-001",
                "timestamp": "2026-04-27T00:00:00Z",
                "source": "test",
                "contact_type": "jamming",
                "lat": 57.5,
                "lon": 19.2,
                "speed": 0.5,
                "heading": 0.0,
                "confidence": 0.95,
                "entity_id": "JAM-TEST-001",
                "is_hostile": True,
                "attributes": {"name": "Manual Jamming", "radius_nm": 25},
            }
        ]
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["analysis"]["analysis_run"] is True
    assert body["analysis"]["threat_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert body["analysis"]["trigger"] == "manual_injection"
    assert "Trigger manual_injection." in body["analysis"]["reason_summary"]


def test_visible_ais_route_reports_disabled_when_not_configured(client, monkeypatch):
    from app.api import routes_engine

    class DisabledReplay:
        def visible_contacts(self, **kwargs):
            return {
                "contacts": [],
                "suspicious_contacts": [],
                "source_summary": "NOAA replay disabled for test",
                "cache_hit": False,
                "provider_enabled": False,
            }

    monkeypatch.setattr(routes_engine, "get_noaa_replay_feed", lambda: DisabledReplay())
    resp = client.get("/v1/engine/ais/visible?latmin=57&latmax=58&lonmin=18&lonmax=19")
    assert resp.status_code == 200
    body = resp.json()
    assert body["enabled"] is False
    assert body["contacts"] == []


def test_visible_ais_route_ingests_suspicious_contacts(client, monkeypatch):
    from app.api import routes_engine

    suspicious_contact = Contact(
        contact_id="AIS-TEST-001",
        timestamp=datetime.now(timezone.utc),
        source="aishub",
        contact_type=ContactType.VESSEL,
        lat=57.5,
        lon=19.0,
        speed=0.4,
        heading=90.0,
        confidence=0.74,
        entity_id="AIS-123456789",
        is_hostile=False,
        attributes={
            "name": "AIS Suspicious Vessel",
            "allegiance": "neutral",
            "ais_live": True,
            "suspicious_maneuver": True,
            "suspicion_score": 0.8,
            "suspicious_flags": ["Near Baltic Cable Alpha", "Low-speed loitering"],
        },
    )

    class EnabledReplay:
        def visible_contacts(self, **kwargs):
            return {
                "contacts": [{
                    "entity_id": suspicious_contact.entity_id,
                    "name": "AIS Suspicious Vessel",
                    "mmsi": "123456789",
                    "lat": 57.5,
                    "lon": 19.0,
                    "speed": 0.4,
                    "heading": 90.0,
                    "suspicion_score": 0.8,
                    "suspicious_flags": ["Near Baltic Cable Alpha", "Low-speed loitering"],
                    "considered_in_analysis": True,
                }],
                "suspicious_contacts": [suspicious_contact],
                "source_summary": "NOAA replay test feed",
                "cache_hit": False,
                "provider_enabled": True,
            }

    client.post("/v1/engine/reset")
    client.post("/v1/engine/scenario/baltic_hybrid_001")
    monkeypatch.setattr(routes_engine, "get_noaa_replay_feed", lambda: EnabledReplay())

    resp = client.get("/v1/engine/ais/visible?latmin=57&latmax=58&lonmin=18&lonmax=19")
    assert resp.status_code == 200
    body = resp.json()
    assert body["enabled"] is True
    assert body["suspicious_count"] == 1
    assert body["analysis_changed"] is True
    contacts = client.get("/v1/engine/contacts").json()["contacts"]
    assert any(contact["entity_id"] == "AIS-123456789" for contact in contacts)
