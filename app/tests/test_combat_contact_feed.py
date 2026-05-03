from __future__ import annotations

from app.engine.combat_contact_generator import CombatContactGenerator


def _scenario_bounds():
    return {
        "lat_min": 57.0,
        "lat_max": 58.0,
        "lon_min": 18.0,
        "lon_max": 20.0,
    }


def _infrastructure():
    return [
        {"name": "Cable Alpha", "lat": 57.42, "lon": 19.15},
        {"name": "Terminal Node", "lat": 57.63, "lon": 19.48},
    ]


def test_combat_generator_produces_valid_contacts():
    generator = CombatContactGenerator(seed=42)
    generator.configure(enabled=True, density="high", scenario_type="mixed_traffic")

    contacts = generator.generate(
        tick=1,
        scenario_bounds=_scenario_bounds(),
        infrastructure=_infrastructure(),
    )

    assert contacts
    sample = contacts[0]
    assert sample.source == "combat_system"
    assert sample.entity_id.startswith("CMS-")
    assert sample.attributes["domain"] in {"air", "surface", "subsurface", "unknown"}
    assert sample.attributes["subtype"]
    assert "track_quality" in sample.attributes
    assert "sensor_source" in sample.attributes


def test_combat_generator_intermittent_subsurface_detection():
    generator = CombatContactGenerator(seed=7)
    generator.configure(enabled=True, density="low", scenario_type="high_threat_environment")
    generator.inject_contact(
        kind="submarine",
        scenario_bounds=_scenario_bounds(),
        infrastructure=_infrastructure(),
        suspicious=True,
        track_quality="low",
    )
    submarine_id = "CMS-INJ-0001"

    visibility = [
        any(contact.entity_id == submarine_id for contact in generator.generate(
            tick=tick,
            scenario_bounds=_scenario_bounds(),
            infrastructure=_infrastructure(),
        ))
        for tick in range(1, 20)
    ]

    assert any(visibility)
    assert any(not seen for seen in visibility)


def test_combat_contacts_enter_analysis_pipeline_and_can_be_filtered(client):
    client.post("/v1/engine/scenario/load", json={"scenario_id": "baltic_hybrid_001", "seed": 42, "mode": "simulation"})
    client.post("/v1/engine/combat_contacts/toggle", json={"enabled": True, "density": "high", "scenario_type": "mixed_traffic"})
    inject = client.post(
        "/v1/engine/combat_contacts/inject",
        json={"kind": "vessel", "suspicious": True, "lat": 57.51, "lon": 19.05, "heading": 95.0, "speed": 8.0},
    ).json()
    combat_id = inject["contact"]["entity_id"]

    analysis = client.get("/v1/engine/analysis").json()
    combat_contacts = client.get("/v1/engine/contacts?source=combat_system").json()["contacts"]
    detail = client.get(f"/v1/engine/contacts/{combat_id}").json()

    assert any(contact["entity_id"] == combat_id for contact in combat_contacts)
    assert detail["status"] == "ok"
    assert detail["contact"]["entity_id"] == combat_id
    assert any(item["entity_id"] == combat_id for item in analysis["anomalies"])
    assert any(item["entity_id"] == combat_id for item in analysis["threats"])


def test_generator_off_yields_no_combat_contacts_on_tick(client):
    client.post("/v1/engine/scenario/load", json={"scenario_id": "baltic_hybrid_001", "seed": 42, "mode": "simulation"})
    client.post("/v1/engine/combat_contacts/toggle", json={"enabled": False, "density": "high", "scenario_type": "mixed_traffic"})
    client.post("/v1/engine/tick")
    combat_contacts = client.get("/v1/engine/contacts?source=combat_system").json()["contacts"]
    assert combat_contacts == []


def test_combat_contact_toggle_updates_state(client):
    client.post("/v1/engine/scenario/load", json={"scenario_id": "baltic_hybrid_001", "seed": 42, "mode": "simulation"})
    response = client.post(
        "/v1/engine/combat_contacts/toggle",
        json={"enabled": True, "density": "low", "scenario_type": "civilian_traffic"},
    ).json()
    state = client.get("/v1/engine/state").json()

    assert response["combat_contacts"]["enabled"] is True
    assert response["combat_contacts"]["density"] == "low"
    assert response["combat_contacts"]["scenario_type"] == "civilian_traffic"
    assert state["scenario"]["combat_contacts_enabled"] is True
    assert state["scenario"]["combat_contacts_density"] == "low"
    assert state["scenario"]["combat_contacts_scenario_type"] == "civilian_traffic"


def test_merging_ais_and_combat_contacts_works(client):
    client.post("/v1/engine/scenario/load", json={"scenario_id": "baltic_hybrid_001", "seed": 42, "mode": "simulation"})
    client.post(
        "/v1/engine/inject",
        json={
            "contacts": [
                {
                    "contact_id": "AIS-001",
                    "timestamp": "2026-05-02T00:00:00Z",
                    "source": "noaa_replay",
                    "contact_type": "vessel",
                    "lat": 57.45,
                    "lon": 19.12,
                    "speed": 10.0,
                    "heading": 90.0,
                    "confidence": 0.92,
                    "entity_id": "AIS-001",
                    "is_hostile": False,
                    "attributes": {"name": "AIS Vessel", "allegiance": "neutral", "unit_class": "vessel"},
                }
            ]
        },
    )
    client.post("/v1/engine/combat_contacts/toggle", json={"enabled": True, "density": "medium", "scenario_type": "mixed_traffic"})
    combat = client.post(
        "/v1/engine/combat_contacts/inject",
        json={"kind": "aircraft", "suspicious": False, "lat": 57.58, "lon": 19.21},
    ).json()["contact"]

    contacts = client.get("/v1/engine/contacts").json()["contacts"]
    combat_contacts = client.get("/v1/engine/contacts?source=combat_system").json()["contacts"]
    ais_contacts = [contact for contact in contacts if contact["source"] == "noaa_replay"]

    assert any(contact["entity_id"] == combat["entity_id"] for contact in combat_contacts)
    assert any(contact["entity_id"] == "AIS-001" for contact in ais_contacts)
    assert any(contact["entity_id"] == combat["entity_id"] for contact in contacts)
