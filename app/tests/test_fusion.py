from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.core.constants import EntityType, EventType
from app.core.schemas import Contact, ContactType, OperationalEvent
from app.engine.analysis_service import AnalysisContext, run_canonical_analysis
from app.engine.fusion import build_fused_tracks, serialize_fused_tracks


def _ts(minutes: int) -> datetime:
    return datetime(2025, 6, 15, 8, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def _event(
    *,
    event_id: str,
    entity_id: str,
    source: str,
    lat: float,
    lon: float,
    confidence: float = 0.8,
    event_type: EventType = EventType.VESSEL_POSITION,
    entity_type: EntityType = EntityType.SUSPICIOUS_VESSEL,
    heading: float | None = 45.0,
    speed_knots: float | None = 8.0,
    timestamp_min: int = 0,
    description: str = "test event",
) -> OperationalEvent:
    attrs = {}
    if heading is not None:
        attrs["heading"] = heading
    if speed_knots is not None:
        attrs["speed_knots"] = speed_knots
    return OperationalEvent(
        event_id=event_id,
        timestamp=_ts(timestamp_min),
        event_type=event_type,
        source=source,
        confidence=confidence,
        lat=lat,
        lon=lon,
        entity_id=entity_id,
        entity_type=entity_type,
        description=description,
        attributes=attrs,
    )


def _contact(
    *,
    contact_id: str,
    entity_id: str,
    source: str,
    lat: float,
    lon: float,
    confidence: float = 0.85,
    heading: float = 45.0,
    speed: float = 8.0,
    subtype: str = "warship",
    timestamp_min: int = 0,
) -> Contact:
    return Contact(
        contact_id=contact_id,
        timestamp=_ts(timestamp_min),
        source=source,
        contact_type=ContactType.VESSEL,
        lat=lat,
        lon=lon,
        speed=speed,
        heading=heading,
        confidence=confidence,
        entity_id=entity_id,
        is_hostile=False,
        attributes={"subtype": subtype, "allegiance": "unknown"},
    )


def test_ais_and_cms_near_same_vessel_fuse_into_one_track():
    events = [
        _event(event_id="EV-AIS", entity_id="AIS-123", source="aishub", lat=57.5000, lon=19.2000),
        _event(event_id="EV-CMS", entity_id="CMS-999", source="combat_system", lat=57.5030, lon=19.2040, confidence=0.92),
    ]
    tracks = build_fused_tracks(events=events, contacts=None)

    assert len(tracks) == 1
    track = tracks[0]
    assert set(track.correlated_entities) == {"AIS-123", "CMS-999"}
    assert track.source_count == 2
    assert track.fused_confidence > 0.75


def test_ais_satellite_and_jamming_raise_fused_confidence():
    events = [
        _event(event_id="EV-AIS", entity_id="VES-1", source="aishub", lat=57.5000, lon=19.2000, confidence=0.68),
        _event(event_id="EV-SAT", entity_id="SAT-1", source="satellite", lat=57.5010, lon=19.2020, confidence=0.78, event_type=EventType.SATELLITE_DETECTION),
        _event(event_id="EV-JAM", entity_id="SIG-1", source="sigint", lat=57.5020, lon=19.2040, confidence=0.86, event_type=EventType.JAMMING_DETECTED),
    ]
    tracks = build_fused_tracks(events=events, contacts=None)

    assert len(tracks) == 1
    assert tracks[0].fused_confidence >= 0.9
    assert set(tracks[0].sources) == {"aishub", "satellite", "sigint"}


def test_osint_alone_does_not_create_high_confidence_hostile_track():
    events = [
        _event(
            event_id="EV-OSINT",
            entity_id="OSINT-1",
            source="social_media",
            lat=57.5000,
            lon=19.2000,
            confidence=0.45,
            event_type=EventType.SOCIAL_MEDIA_REPORT,
            description="Unverified local report",
        ),
    ]
    tracks = build_fused_tracks(events=events, contacts=None)

    assert len(tracks) == 1
    assert tracks[0].fused_confidence < 0.6
    assert tracks[0].source_count == 1


def test_unrelated_contacts_remain_separate_tracks():
    events = [
        _event(event_id="EV-1", entity_id="VES-1", source="aishub", lat=57.5000, lon=19.2000),
        _event(event_id="EV-2", entity_id="VES-2", source="combat_system", lat=59.1000, lon=24.9000, heading=270.0),
    ]
    tracks = build_fused_tracks(events=events, contacts=None)

    assert len(tracks) == 2
    assert {track.primary_entity_id for track in tracks} == {"VES-1", "VES-2"}


def test_fused_tracks_are_deterministic():
    events = [
        _event(event_id="EV-AIS", entity_id="AIS-123", source="aishub", lat=57.5000, lon=19.2000),
        _event(event_id="EV-CMS", entity_id="CMS-999", source="combat_system", lat=57.5030, lon=19.2040, confidence=0.92),
    ]
    contacts = [
        _contact(contact_id="CT-1", entity_id="CMS-999", source="combat_system", lat=57.5030, lon=19.2040, confidence=0.91),
    ]

    first = serialize_fused_tracks(build_fused_tracks(events=events, contacts=contacts))
    second = serialize_fused_tracks(build_fused_tracks(events=events, contacts=contacts))

    assert first == second


def test_targeting_includes_fusion_sources_and_rationale():
    events = [
        _event(
            event_id="EV-CABLE",
            entity_id="INFRA-1",
            source="fused",
            lat=57.50,
            lon=19.20,
            confidence=0.95,
            event_type=EventType.CABLE_SEVERANCE,
            entity_type=EntityType.INFRASTRUCTURE,
            description="Cable severance",
        ),
        _event(
            event_id="EV-AIS",
            entity_id="AIS-123",
            source="aishub",
            lat=57.5000,
            lon=19.2000,
            confidence=0.7,
            event_type=EventType.VESSEL_COURSE_CHANGE,
            description="AIS vessel near cable",
        ),
        _event(
            event_id="EV-SIG",
            entity_id="SIG-123",
            source="sigint",
            lat=57.5030,
            lon=19.2040,
            confidence=0.88,
            event_type=EventType.JAMMING_DETECTED,
            description="Jamming near vessel",
        ),
    ]
    contacts = [
        _contact(contact_id="CT-1", entity_id="AIS-123", source="aishub", lat=57.5000, lon=19.2000, confidence=0.7),
        _contact(contact_id="CT-2", entity_id="CMS-123", source="combat_system", lat=57.5020, lon=19.2030, confidence=0.9),
    ]

    result = run_canonical_analysis(
        AnalysisContext(
            events=events,
            active_contacts=contacts,
            source="test_fusion_targeting",
            tick=2,
            scenario_id="baltic_hybrid_001",
            scenario_name="Baltic",
        )
    )

    assert result.fused_tracks
    target = next(target for target in result.targets if target.id in {"AIS-123", "CMS-123", "SIG-123"})
    assert "fusion" in target.sources
    assert any(source in target.sources for source in {"aishub", "combat_system", "sigint"})
    assert "Track" in target.rationale


def test_fusion_analysis_does_not_call_llm(monkeypatch):
    def fail_llm_call(*args, **kwargs):
        raise AssertionError("LLM must not be called during deterministic fusion analysis")

    monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm_call)

    events = [
        _event(event_id="EV-AIS", entity_id="AIS-123", source="aishub", lat=57.5000, lon=19.2000),
        _event(event_id="EV-CMS", entity_id="CMS-999", source="combat_system", lat=57.5030, lon=19.2040, confidence=0.92),
    ]
    result = run_canonical_analysis(AnalysisContext(events=events, source="test_fusion"))

    assert result.fused_tracks
