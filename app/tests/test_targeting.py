from __future__ import annotations

from datetime import datetime, timezone

from app.core.constants import EntityType, EventType
from app.core.schemas import AssetState, Contact, ContactType, OperationalEvent
from app.engine.analysis_service import AnalysisContext, run_canonical_analysis
from app.engine.targeting import serialize_targets


def _ts(hour: int) -> datetime:
    return datetime(2025, 6, 15, hour, 0, tzinfo=timezone.utc)


def _event(
    *,
    event_id: str,
    entity_id: str,
    event_type: EventType,
    entity_type: EntityType,
    lat: float,
    lon: float,
    source: str = "radar",
    confidence: float = 0.9,
    description: str = "test event",
    attributes: dict | None = None,
    is_threat_candidate: bool = True,
    is_infrastructure: bool = False,
) -> OperationalEvent:
    return OperationalEvent(
        event_id=event_id,
        timestamp=_ts(8),
        event_type=event_type,
        source=source,
        confidence=confidence,
        lat=lat,
        lon=lon,
        entity_id=entity_id,
        entity_type=entity_type,
        description=description,
        attributes=attributes or {},
        is_threat_candidate=is_threat_candidate,
        is_infrastructure=is_infrastructure,
    )


def _contact(
    *,
    entity_id: str,
    lat: float,
    lon: float,
    source: str = "radar",
    confidence: float = 0.92,
    heading: float = 45.0,
    speed: float = 1.0,
    subtype: str = "warship",
    heading_toward_infra: bool = True,
    is_hostile: bool = True,
) -> Contact:
    return Contact(
        contact_id=f"CT-{entity_id}",
        timestamp=_ts(8),
        source=source,
        contact_type=ContactType.VESSEL,
        lat=lat,
        lon=lon,
        speed=speed,
        heading=heading,
        confidence=confidence,
        entity_id=entity_id,
        is_hostile=is_hostile,
        attributes={
            "subtype": subtype,
            "heading_toward_infra": heading_toward_infra,
            "allegiance": "unknown",
        },
    )


def _context():
    cable = _event(
        event_id="EV-CABLE",
        entity_id="INFRA-ALPHA",
        event_type=EventType.CABLE_SEVERANCE,
        entity_type=EntityType.INFRASTRUCTURE,
        lat=57.50,
        lon=19.20,
        source="fused",
        description="Cable severance confirmed",
        is_threat_candidate=False,
        is_infrastructure=True,
    )
    hot = _event(
        event_id="EV-HOT",
        entity_id="VES-HOT",
        event_type=EventType.VESSEL_COURSE_CHANGE,
        entity_type=EntityType.SUSPICIOUS_VESSEL,
        lat=57.48,
        lon=19.18,
        attributes={
            "speed_knots": 0.8,
            "heading": 45.0,
            "course_change": True,
            "behavior_mode": "hostile_probe_infrastructure",
            "intent": "probe",
            "target_infra": "Baltic Cable Alpha",
        },
        description="Suspicious vessel maneuvering toward cable corridor",
    )
    cold = _event(
        event_id="EV-COLD",
        entity_id="VES-COLD",
        event_type=EventType.VESSEL_POSITION,
        entity_type=EntityType.SUSPICIOUS_VESSEL,
        lat=59.10,
        lon=24.80,
        source="ais",
        confidence=0.75,
        attributes={
            "speed_knots": 11.5,
            "heading": 270.0,
        },
        description="Distant vessel in transit",
    )
    return AnalysisContext(
        events=[cable, hot, cold],
        active_contacts=[
            _contact(entity_id="VES-HOT", lat=57.48, lon=19.18, source="radar"),
            _contact(
                entity_id="VES-COLD",
                lat=59.10,
                lon=24.80,
                source="ais",
                confidence=0.75,
                heading=270.0,
                speed=11.5,
                subtype="cargo",
                heading_toward_infra=False,
                is_hostile=False,
            ),
        ],
        asset_states=[
            AssetState(
                asset_id="isr-1",
                asset_type="isr_uav",
                capabilities=["isr_uav", "surveillance_asset"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                domain="air",
                display_name="ISR UAV 1",
                response_eta_min=20,
            ),
            AssetState(
                asset_id="mpv-1",
                asset_type="maritime_patrol_vessel",
                capabilities=["maritime_patrol_vessel", "maritime_patrol_asset"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                domain="maritime",
                display_name="Patrol Vessel 1",
                response_eta_min=40,
            ),
        ],
        source="test_targeting",
        tick=3,
        scenario_id="baltic_hybrid_001",
        scenario_name="Baltic test",
    )


def test_targets_generated_from_contacts_and_ranked_deterministically():
    context = _context()

    first = run_canonical_analysis(context)
    second = run_canonical_analysis(context)

    assert serialize_targets(first.targets) == serialize_targets(second.targets)
    assert [target.id for target in first.top_targets] == [target.id for target in first.targets[:5]]
    assert len(first.targets) >= 2
    assert first.targets[0].id == "VES-HOT"
    assert first.targets[0].priority_score >= first.targets[1].priority_score


def test_high_threat_target_gets_safe_high_priority_action_and_roe():
    result = run_canonical_analysis(_context())

    hot = next(target for target in result.targets if target.id == "VES-HOT")

    assert hot.type == "vessel"
    assert hot.priority_level in {"HIGH", "CRITICAL"}
    assert hot.recommended_action in {"shadow", "protect-asset", "intercept-ready"}
    assert hot.roe_status in {"allowed", "restricted", "requires_authorization", "rejected"}
    assert "behavior" in hot.sources
    assert "anomaly" in hot.sources
    assert "Priority" in hot.rationale
    assert hot.supporting_asset is not None
    assert hot.supporting_asset.assigned_asset_id in {"isr-1", "mpv-1"}


def test_targeting_analysis_does_not_call_llm(monkeypatch):
    def fail_llm_call(*args, **kwargs):
        raise AssertionError("LLM must not be called during deterministic targeting analysis")

    monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm_call)

    result = run_canonical_analysis(_context())

    assert result.targets
