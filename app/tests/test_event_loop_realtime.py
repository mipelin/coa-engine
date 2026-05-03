from datetime import datetime, timedelta, timezone

from app.core.constants import EventType
from app.core.schemas import Contact, ContactType
from app.engine.contact_engine import EngineMode, get_contact_engine
from app.engine.event_loop import get_event_loop
from app.engine.feature_engineering import compute_features
from app.engine.state_store import StateStore, get_state_store


def _contact(
    contact_id: str,
    entity_id: str,
    timestamp: datetime,
    *,
    heading: float = 90.0,
    speed: float = 8.0,
    attrs: dict | None = None,
) -> Contact:
    return Contact(
        contact_id=contact_id,
        timestamp=timestamp,
        source="test",
        contact_type=ContactType.VESSEL,
        lat=57.5,
        lon=19.0,
        speed=speed,
        heading=heading,
        confidence=0.9,
        entity_id=entity_id,
        is_hostile=True,
        attributes=attrs or {"name": entity_id},
    )


def test_state_store_history_is_bounded_and_preserves_recent_events():
    store = StateStore()
    store._max_history = 2
    now = datetime.now(timezone.utc)

    store.ingest_contact(_contact("C-0", "VES-1", now))
    store.ingest_contact(_contact("C-1", "VES-1", now + timedelta(minutes=1), attrs={"course_change": True}))
    store.ingest_contact(_contact("C-2", "VES-1", now + timedelta(minutes=2)))

    history = store.get_history(10)
    history_events = store.contact_history_as_events(limit=10)

    assert [contact.contact_id for contact in history] == ["C-1", "C-2"]
    assert [event.event_id for event in history_events] == ["C-1", "C-2"]
    assert history_events[0].event_type == EventType.VESSEL_COURSE_CHANGE


def test_event_loop_uses_history_window_not_active_snapshot():
    engine = get_contact_engine()
    loop = get_event_loop()
    store = get_state_store()

    engine.set_mode(EngineMode.SIMULATION)
    engine.load_scenario("baltic_hybrid_001")

    for _ in range(18):
        engine.tick()
        loop.run_tick()

    snapshot_events = store.contacts_as_events()
    history_events = store.contact_history_as_events(limit=500)

    assert len(history_events) > len(snapshot_events)
    assert sum(1 for event in snapshot_events if event.event_type == EventType.VESSEL_COURSE_CHANGE) == 0
    assert sum(1 for event in history_events if event.event_type == EventType.VESSEL_COURSE_CHANGE) >= 2
    assert any(event.event_type == EventType.JAMMING_DETECTED for event in history_events)

    history_features = compute_features(history_events, store.get_infrastructure())
    snapshot_features = compute_features(snapshot_events, store.get_infrastructure())

    assert max(
        feature.course_change_count
        for feature in history_features
        if feature.entity_id == "VES-SUSP-001"
    ) >= 2
    assert max(
        feature.course_change_count
        for feature in snapshot_features
        if feature.entity_id == "VES-SUSP-001"
    ) == 0
    assert store.state.last_analysis_tick >= store.get_tick() - 1
    assert store.state.last_analysis_tick > 0


def test_history_grows_across_ticks_without_overwriting_active_snapshot():
    engine = get_contact_engine()
    loop = get_event_loop()
    store = get_state_store()

    engine.set_mode(EngineMode.SIMULATION)
    engine.load_scenario("baltic_hybrid_001")

    seeded_active = len(store.get_contacts())
    seeded_history = len(store.get_history(100))

    for _ in range(6):
        engine.tick()
        loop.run_tick()

    history = store.get_history(200)

    assert seeded_history == seeded_active
    assert len(history) > len(store.get_contacts())
    assert len([contact for contact in history if contact.entity_id == "VES-SUSP-001"]) > 1
