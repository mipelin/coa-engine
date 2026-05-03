from __future__ import annotations

from datetime import datetime, timezone

from app.core.constants import EntityType, EventType
from app.core.schemas import Contact, ContactType, OperationalEvent
from app.engine.analysis_service import AnalysisContext, run_canonical_analysis
from app.engine.feature_engineering import haversine_km
from app.engine.fusion import build_fused_tracks
from app.engine.isr_simulation import simulate_isr_observations


def _ts() -> datetime:
    return datetime(2026, 5, 3, 12, 0, tzinfo=timezone.utc)


def _contact(
    *,
    entity_id: str = "VES-001",
    source: str = "simulation",
    lat: float = 57.5,
    lon: float = 19.2,
    hostile: bool = True,
    subtype: str = "warship",
) -> Contact:
    return Contact(
        contact_id=f"CT-{entity_id}",
        timestamp=_ts(),
        source=source,
        contact_type=ContactType.VESSEL,
        lat=lat,
        lon=lon,
        speed=12.0,
        heading=45.0,
        confidence=0.88,
        entity_id=entity_id,
        is_hostile=hostile,
        attributes={
            "subtype": subtype,
            "allegiance": "hostile" if hostile else "neutral",
            "behavior_flags": ["heading_toward_infrastructure"] if hostile else [],
        },
    )


def _event(entity_id: str = "VES-001") -> OperationalEvent:
    return OperationalEvent(
        event_id=f"EV-{entity_id}",
        timestamp=_ts(),
        event_type=EventType.VESSEL_COURSE_CHANGE,
        source="simulation",
        confidence=0.82,
        lat=57.5,
        lon=19.2,
        entity_id=entity_id,
        entity_type=EntityType.SUSPICIOUS_VESSEL,
        description="Suspicious vessel altered course toward infrastructure",
        attributes={"heading": 45.0, "speed_knots": 12.0, "subtype": "warship"},
        allegiance="hostile",
    )


def test_isr_simulation_is_deterministic():
    contacts = [_contact()]
    events = [_event()]
    infrastructure = [{"name": "Cable Alpha", "lat": 57.51, "lon": 19.22}]

    first = simulate_isr_observations(tick=3, contacts=contacts, events=events, infrastructure=infrastructure, seed=7)
    second = simulate_isr_observations(tick=3, contacts=contacts, events=events, infrastructure=infrastructure, seed=7)

    assert first == second
    assert len(first) >= 3


def test_isr_simulation_noise_stays_within_reasonable_bounds():
    contact = _contact()
    observations = simulate_isr_observations(
        tick=3,
        contacts=[contact],
        events=[],
        infrastructure=[],
        seed=9,
    )

    assert observations
    for observation in observations:
        distance = haversine_km(
            contact.lat,
            contact.lon,
            observation.position.lat,
            observation.position.lon,
        )
        assert distance <= max(observation.position.sigma_km * 6.0, 2.2)


def test_isr_observations_feed_fusion_stably():
    contact = _contact()
    observations = simulate_isr_observations(
        tick=3,
        contacts=[contact],
        events=[_event()],
        infrastructure=[{"name": "Cable Alpha", "lat": 57.51, "lon": 19.22}],
        seed=11,
    )

    tracks = build_fused_tracks(events=[], contacts=[contact], observations=observations)

    assert len(tracks) == 1
    track = tracks[0]
    assert track.primary_entity_id == "VES-001"
    assert track.source_count >= 3
    assert any(source in track.sources for source in {"ais", "combat_system", "satellite", "osint", "esm"})


def test_isr_enabled_analysis_remains_deterministic_and_llm_free(monkeypatch):
    def fail_llm_call(*args, **kwargs):
        raise AssertionError("LLM must not be called during ISR-enhanced deterministic analysis")

    monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm_call)

    result = run_canonical_analysis(
        AnalysisContext(
            events=[_event()],
            active_contacts=[_contact()],
            infrastructure=[{"name": "Cable Alpha", "type": "subsea_cable", "lat": 57.51, "lon": 19.22}],
            source="test_isr_simulation",
            tick=3,
            scenario_id="baltic_hybrid_001",
            scenario_name="Baltic",
        )
    )

    assert result.metadata["isr_observations"] > 0
    assert result.fused_tracks
    assert result.recommendation is not None
