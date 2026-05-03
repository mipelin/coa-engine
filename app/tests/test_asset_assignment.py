from __future__ import annotations

from datetime import datetime, timezone

from app.core.constants import EntityType, EventType
from app.core.schemas import AssetState, Contact, ContactType, OperationalEvent
from app.engine.analysis_service import AnalysisContext, run_canonical_analysis


def _ts() -> datetime:
    return datetime(2026, 5, 3, 12, 0, tzinfo=timezone.utc)


def _asset(asset_id: str, asset_type: str, capabilities: list[str], *, domain: str = "air", eta: int = 20) -> AssetState:
    return AssetState(
        asset_id=asset_id,
        asset_type=asset_type,
        capabilities=capabilities,
        quantity_total=1,
        quantity_available=1,
        status="available",
        domain=domain,
        display_name=asset_id,
        response_eta_min=eta,
    )


def _event(entity_id: str, event_type: EventType, entity_type: EntityType, lat: float, lon: float, attributes: dict | None = None) -> OperationalEvent:
    return OperationalEvent(
        event_id=f"EV-{entity_id}",
        timestamp=_ts(),
        event_type=event_type,
        source="simulation",
        confidence=0.9,
        lat=lat,
        lon=lon,
        entity_id=entity_id,
        entity_type=entity_type,
        description="test",
        attributes=attributes or {},
        allegiance="hostile",
        is_threat_candidate=entity_type != EntityType.INFRASTRUCTURE,
        is_infrastructure=entity_type == EntityType.INFRASTRUCTURE,
    )


def _contact(entity_id: str, ctype: ContactType, lat: float, lon: float, *, subtype: str, hostile: bool = True) -> Contact:
    return Contact(
        contact_id=f"CT-{entity_id}",
        timestamp=_ts(),
        source="simulation",
        contact_type=ctype,
        lat=lat,
        lon=lon,
        speed=8.0,
        heading=45.0,
        confidence=0.9,
        entity_id=entity_id,
        is_hostile=hostile,
        attributes={"subtype": subtype, "allegiance": "hostile" if hostile else "friendly", "heading_toward_infra": True},
    )


def test_high_priority_vessel_near_cable_gets_maritime_or_isr_support():
    result = run_canonical_analysis(
        AnalysisContext(
            events=[
                _event("INFRA-1", EventType.CABLE_SEVERANCE, EntityType.INFRASTRUCTURE, 57.5, 19.2),
                _event("VES-1", EventType.VESSEL_COURSE_CHANGE, EntityType.SUSPICIOUS_VESSEL, 57.48, 19.18, {"heading": 45.0, "speed_knots": 0.8, "behavior_mode": "hostile_probe_infrastructure"}),
            ],
            active_contacts=[_contact("VES-1", ContactType.VESSEL, 57.48, 19.18, subtype="warship")],
            asset_states=[
                _asset("mpv-1", "maritime_patrol_vessel", ["maritime_patrol_vessel", "maritime_patrol_asset"], domain="maritime", eta=35),
                _asset("isr-1", "isr_uav", ["isr_uav", "surveillance_asset"], domain="air", eta=20),
            ],
            infrastructure=[{"name": "Cable Alpha", "type": "subsea_cable", "lat": 57.5, "lon": 19.2}],
            source="test_asset_assignment_vessel",
            tick=4,
        )
    )
    target = next(item for item in result.targets if item.id == "VES-1")
    assert target.supporting_asset is not None
    assert target.supporting_asset.assignment_role in {"shadow", "protect_infrastructure", "track"}
    assert target.supporting_asset.asset_type in {"maritime_patrol_vessel", "isr_uav"}


def test_uav_near_airport_gets_airspace_or_isr_support():
    result = run_canonical_analysis(
        AnalysisContext(
            events=[_event("UAV-1", EventType.UAV_DETECTION, EntityType.UAV, 57.63, 18.35, {"heading": 90.0, "speed_knots": 55.0, "subtype": "uav"})],
            active_contacts=[_contact("UAV-1", ContactType.UAV, 57.63, 18.35, subtype="uav")],
            asset_states=[
                _asset("helo-1", "maritime_helicopter", ["maritime_helicopter", "surveillance_asset"], domain="air", eta=15),
                _asset("atc-1", "airspace_coordinator", ["airspace_coordinator"], domain="coordination", eta=10),
            ],
            source="test_asset_assignment_uav",
            tick=4,
        )
    )
    target = next(item for item in result.targets if item.id == "UAV-1")
    assert target.supporting_asset is not None
    assert target.supporting_asset.assignment_role == "airspace_watch"
    assert target.supporting_asset.asset_type in {"maritime_helicopter", "airspace_coordinator"}


def test_convoy_gets_convoy_watch_support_if_available():
    result = run_canonical_analysis(
        AnalysisContext(
            events=[_event("CONVOY-1", EventType.CONVOY_SIGHTING, EntityType.CONVOY, 57.7, 20.1, {"heading": 180.0, "speed_knots": 22.0})],
            active_contacts=[_contact("CONVOY-1", ContactType.CONVOY, 57.7, 20.1, subtype="convoy")],
            asset_states=[_asset("border-1", "border_patrol_liaison", ["border_patrol_liaison"], domain="coordination", eta=18)],
            source="test_asset_assignment_convoy",
            tick=4,
        )
    )
    target = next(item for item in result.targets if item.id == "CONVOY-1")
    assert target.type == "convoy"
    assert target.supporting_asset is not None
    assert target.supporting_asset.assignment_role == "convoy_watch"
    assert target.supporting_asset.asset_type == "border_patrol_liaison"


def test_no_asset_case_is_safe_and_explicit():
    result = run_canonical_analysis(
        AnalysisContext(
            events=[_event("VES-1", EventType.VESSEL_COURSE_CHANGE, EntityType.SUSPICIOUS_VESSEL, 57.48, 19.18, {"heading": 45.0, "speed_knots": 0.8})],
            active_contacts=[_contact("VES-1", ContactType.VESSEL, 57.48, 19.18, subtype="warship")],
            source="test_asset_assignment_none",
            tick=4,
        )
    )
    target = next(item for item in result.targets if item.id == "VES-1")
    assert target.supporting_asset is not None
    assert target.supporting_asset.assigned_asset_id == "none"
    assert "no suitable asset available" in target.supporting_asset.constraints


def test_asset_assignment_analysis_does_not_call_llm(monkeypatch):
    def fail_llm_call(*args, **kwargs):
        raise AssertionError("LLM must not be called during deterministic asset assignment")

    monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm_call)

    result = run_canonical_analysis(
        AnalysisContext(
            events=[_event("VES-1", EventType.VESSEL_COURSE_CHANGE, EntityType.SUSPICIOUS_VESSEL, 57.48, 19.18, {"heading": 45.0, "speed_knots": 0.8})],
            active_contacts=[_contact("VES-1", ContactType.VESSEL, 57.48, 19.18, subtype="warship")],
            asset_states=[_asset("isr-1", "isr_uav", ["isr_uav", "surveillance_asset"])],
            source="test_asset_assignment_llm_free",
            tick=4,
        )
    )
    assert result.targets[0].supporting_asset is not None
