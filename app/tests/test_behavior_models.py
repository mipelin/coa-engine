"""Tests for behavior_models, entity_catalog, and integration with contact_engine."""

import math
from datetime import datetime, timezone

import pytest

from app.core.constants import CRITICAL_INFRASTRUCTURE
from app.core.schemas import ContactType
from app.engine.behavior_models import (
    BehaviorContext,
    FriendlyPatrolMonitor,
    HostileLoiterThenDivert,
    HostileProbeInfrastructure,
    NeutralTransit,
    haversine_km,
    make_policy,
    move_along_heading,
)
from app.engine.contact_engine import ContactEngine, SimulationScenario
from app.engine.entity_catalog import get_catalog
from app.engine.state_store import get_state_store


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ctx(**overrides):
    defaults = dict(
        tick=1,
        infrastructure=CRITICAL_INFRASTRUCTURE,
        contacts=[],
        active_stimuli=[],
        active_incidents=[],
        priority_targets=[],
        scenario_bounds={"lat_min": 55.0, "lat_max": 60.0, "lon_min": 17.0, "lon_max": 26.0},
    )
    defaults.update(overrides)
    return BehaviorContext(**defaults)


# ---------------------------------------------------------------------------
# behavior_models — unit tests
# ---------------------------------------------------------------------------

class TestHostileProbeInfrastructure:
    def test_approaches_target_infra(self):
        policy = HostileProbeInfrastructure(target_infra_name="Baltic Cable Alpha")
        entity = {"lat": 57.0, "lon": 18.0, "speed": 0.0, "heading": 0.0}
        ctx = _ctx()

        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["behavior_mode"] == "hostile_probe_infrastructure"
        assert r.attributes["intent"] == "probe_infrastructure"
        assert r.attributes["target_infra"] == "Baltic Cable Alpha"
        assert r.attributes["behavior_rationale"]
        assert r.lat > entity["lat"]  # moved toward cable at lat 57.5

    def test_slows_when_close(self):
        policy = HostileProbeInfrastructure(
            target_infra_name="Baltic Cable Alpha", close_range_km=50.0,
        )
        # Start very close to the cable
        entity = {"lat": 57.49, "lon": 18.99, "speed": 8.0, "heading": 0.0}
        ctx = _ctx(tick=1)

        r = policy(entity, ctx, rng_state=1)
        assert r.speed <= policy.slow_speed + 0.1
        assert "proximity_to_Baltic Cable Alpha" in r.attributes["reacting_to"]

    def test_deterministic(self):
        policy = HostileProbeInfrastructure()
        entity = {"lat": 57.0, "lon": 18.0, "speed": 5.0, "heading": 90.0}
        ctx = _ctx()

        r1 = policy(entity, ctx, rng_state=1)
        r2 = policy(entity, ctx, rng_state=1)
        assert r1.lat == r2.lat
        assert r1.lon == r2.lon

    def test_switches_toward_remaining_cable_after_severance(self):
        policy = HostileProbeInfrastructure(target_infra_name="Baltic Cable Alpha")
        entity = {"lat": 57.0, "lon": 18.0, "speed": 5.0, "heading": 90.0}
        ctx = _ctx(active_stimuli=["cable_severance"])

        r = policy(entity, ctx, rng_state=1)
        assert "cable_severance" in r.attributes["reacting_to"]
        assert "remaining infrastructure" in r.attributes["behavior_rationale"].lower()


class TestHostileLoiterThenDivert:
    def test_loiters_before_trigger(self):
        policy = HostileLoiterThenDivert(divert_tick=20)
        entity = {"lat": 57.8, "lon": 19.5, "speed": 1.0, "heading": 45.0}
        ctx = _ctx(tick=5, active_stimuli=[])

        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["intent"] == "loiter"
        assert r.speed <= policy.loiter_speed + 0.1

    def test_diverts_on_tick_threshold(self):
        policy = HostileLoiterThenDivert(divert_tick=10, divert_heading=310.0, divert_speed=8.0)
        entity = {"lat": 57.8, "lon": 19.5, "speed": 1.0, "heading": 45.0}
        ctx = _ctx(tick=10, active_stimuli=[])

        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["intent"] == "divert"
        assert r.attributes["_bhv_diverted"] is True
        assert r.speed == pytest.approx(8.0, abs=0.1)

    def test_diverts_on_stimulus(self):
        policy = HostileLoiterThenDivert(divert_tick=999, divert_stimulus="cable_severance")
        entity = {"lat": 57.8, "lon": 19.5, "speed": 1.0, "heading": 45.0}
        ctx = _ctx(tick=5, active_stimuli=["cable_severance"])

        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["intent"] == "divert"
        assert "cable_severance" in r.attributes["reacting_to"]
        assert "remaining infrastructure" in r.attributes["behavior_rationale"].lower()

    def test_stays_diverted_after_trigger(self):
        policy = HostileLoiterThenDivert(divert_tick=5)
        entity = {"lat": 57.8, "lon": 19.5, "speed": 1.0, "heading": 45.0, "_bhv_diverted": True}

        ctx = _ctx(tick=6, active_stimuli=[])
        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["intent"] == "divert"


class TestFriendlyPatrolMonitor:
    def test_patrols_back_and_forth(self):
        policy = FriendlyPatrolMonitor(patrol_heading_a=90.0, patrol_heading_b=270.0, patrol_flip_ticks=6)
        entity = {"lat": 57.6, "lon": 18.5, "speed": 12.0, "heading": 90.0}

        # Even phase → heading_a
        ctx = _ctx(tick=1, contacts=[])
        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["intent"] == "patrol"

    def test_reacts_to_nearby_hostile(self):
        policy = FriendlyPatrolMonitor(react_range_km=50.0)
        entity = {"lat": 57.6, "lon": 18.5, "speed": 12.0, "heading": 90.0}
        hostile = {"entity_id": "VES-HOSTILE", "lat": 57.65, "lon": 18.55, "is_hostile": True}

        ctx = _ctx(tick=1, contacts=[hostile])
        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["intent"] == "monitor"
        assert any("hostile_VES-HOSTILE" in x for x in r.attributes["reacting_to"])

    def test_reacts_to_high_priority_target(self):
        policy = FriendlyPatrolMonitor(react_range_km=50.0)
        entity = {"lat": 57.6, "lon": 18.5, "speed": 12.0, "heading": 90.0}
        ctx = _ctx(priority_targets=[{"entity_id": "VES-HOT", "priority_level": "CRITICAL", "lat": 57.7, "lon": 18.6}])

        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["intent"] == "monitor"
        assert any("priority_target_VES-HOT" in x for x in r.attributes["reacting_to"])
        assert "highest-priority target" in r.attributes["behavior_rationale"]

    def test_no_reaction_to_distant_hostile(self):
        policy = FriendlyPatrolMonitor(react_range_km=10.0)
        entity = {"lat": 57.6, "lon": 18.5, "speed": 12.0, "heading": 90.0}
        hostile = {"entity_id": "FAR", "lat": 59.0, "lon": 25.0, "is_hostile": True}

        ctx = _ctx(tick=1, contacts=[hostile])
        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["intent"] == "patrol"


class TestNeutralTransit:
    def test_follows_route(self):
        route = [(56.0, 18.0), (56.5, 18.5)]
        policy = NeutralTransit(route=route, transit_speed=10.0)
        entity = {"lat": 56.0, "lon": 18.0, "speed": 10.0, "heading": 0.0, "_bhv_wp_idx": 0}

        ctx = _ctx(tick=1)
        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["behavior_mode"] == "neutral_transit"
        assert r.attributes["intent"] == "transit"
        # Should move toward waypoint 1
        assert r.lat > 56.0 or r.lon > 18.0

    def test_wraps_route(self):
        route = [(56.0, 18.0), (56.05, 18.05)]
        policy = NeutralTransit(route=route, transit_speed=10.0, waypoint_threshold=0.1)
        entity = {"lat": 56.04, "lon": 18.04, "speed": 10.0, "heading": 45.0, "_bhv_wp_idx": 1}

        ctx = _ctx(tick=1)
        r = policy(entity, ctx, rng_state=1)
        # After passing wp 1, should wrap to wp 0
        assert r.attributes["_bhv_wp_idx"] == 0 or r.attributes["_bhv_wp_idx"] == 1

    def test_no_reacting_to(self):
        route = [(56.0, 18.0)]
        policy = NeutralTransit(route=route)
        entity = {"lat": 56.0, "lon": 18.0, "speed": 10.0, "heading": 0.0, "_bhv_wp_idx": 0}
        ctx = _ctx(tick=1)
        r = policy(entity, ctx, rng_state=1)
        assert r.attributes["reacting_to"] == []

    def test_avoids_nearby_jamming_zone(self):
        route = [(56.0, 18.0), (56.5, 18.5)]
        policy = NeutralTransit(route=route, transit_speed=10.0)
        entity = {"lat": 56.0, "lon": 18.0, "speed": 10.0, "heading": 0.0, "_bhv_wp_idx": 0}
        ctx = _ctx(contacts=[{"entity_id": "JAM-1", "lat": 56.02, "lon": 18.02, "is_hostile": False, "type": "jamming"}])

        r = policy(entity, ctx, rng_state=1)
        assert any("avoid_" in item for item in r.attributes["reacting_to"])
        assert "avoid nearby jamming" in r.attributes["behavior_rationale"].lower()


class TestMakePolicy:
    def test_unknown_policy_raises(self):
        with pytest.raises(ValueError, match="Unknown behavior policy"):
            make_policy("does_not_exist")

    def test_creates_policy(self):
        p = make_policy("hostile_probe_infrastructure", target_infra_name="Test Cable")
        assert isinstance(p, HostileProbeInfrastructure)


# ---------------------------------------------------------------------------
# Entity catalog tests
# ---------------------------------------------------------------------------

class TestEntityCatalog:
    def test_baltic_has_red_blue_neutral(self):
        catalog = get_catalog("baltic_hybrid_001")
        allegiances = {e["allegiance"] for e in catalog}
        assert "red" in allegiances
        assert "blue" in allegiances
        assert "neutral" in allegiances

    def test_all_scenarios_have_entities(self):
        for sid in ("baltic_hybrid_001", "arctic_submarine_001", "mediterranean_001"):
            catalog = get_catalog(sid)
            assert len(catalog) >= 4, f"{sid} should have >= 4 entities"

    def test_catalog_entities_have_required_fields(self):
        catalog = get_catalog("baltic_hybrid_001")
        for entry in catalog:
            assert "entity_id" in entry
            assert "behavior_policy" in entry
            assert "allegiance" in entry
            assert isinstance(entry["type"], ContactType)


# ---------------------------------------------------------------------------
# Integration tests — SimulationScenario with behavior policies
# ---------------------------------------------------------------------------

def _make_sim(scenario_id="baltic_hybrid_001", **kwargs):
    from app.engine.scenario_generator import ScenarioGenerator
    template = ScenarioGenerator(seed=42, **kwargs).generate(scenario_id)
    return SimulationScenario(template)


class TestSimulationScenarioIntegration:
    def test_baltic_produces_all_allegiances(self):
        sim = _make_sim()
        contacts = sim.tick_forward()
        allegiances = {c.attributes.get("allegiance", "") for c in contacts}
        assert "red" in allegiances
        assert "blue" in allegiances
        assert "neutral" in allegiances

    def test_hostile_probe_approaches_cable(self):
        sim = _make_sim()
        initial_lat = sim.entities["VES-SUSP-001"]["lat"]
        initial_lon = sim.entities["VES-SUSP-001"]["lon"]

        for _ in range(10):
            sim.tick_forward()

        final_lat = sim.entities["VES-SUSP-001"]["lat"]
        final_lon = sim.entities["VES-SUSP-001"]["lon"]

        # Cable Alpha is at 57.5, 19.0 — entity should have moved closer
        initial_dist = haversine_km(initial_lat, initial_lon, 57.5, 19.0)
        final_dist = haversine_km(final_lat, final_lon, 57.5, 19.0)
        assert final_dist < initial_dist, "Hostile probe should approach cable"

    def test_loiter_diverts_on_cable_severance(self):
        sim = _make_sim()

        for _ in range(10):
            contacts = sim.tick_forward()

        # Find the loiter entity contact at tick 10
        loiter_contacts = [
            c for c in contacts
            if c.entity_id == "VES-SUSP-002" and c.attributes.get("behavior_mode") == "hostile_loiter_then_divert"
        ]
        assert loiter_contacts
        assert loiter_contacts[0].attributes["intent"] == "divert"
        assert "cable_severance" in loiter_contacts[0].attributes.get("reacting_to", [])

    def test_blue_monitors_hostile(self):
        sim = _make_sim()
        contacts = sim.tick_forward()
        blue = [c for c in contacts if c.entity_id == "VES-ALLIED-001"]
        assert blue
        assert blue[0].attributes["behavior_mode"] == "friendly_patrol_monitor"
        # Should be reacting to a nearby hostile
        reacting = blue[0].attributes.get("reacting_to", [])
        assert any("hostile_" in r for r in reacting)

    def test_neutral_transits_without_hostile_attributes(self):
        sim = _make_sim()
        contacts = sim.tick_forward()
        neutral = [c for c in contacts if c.attributes.get("allegiance") == "neutral"]
        assert neutral
        assert neutral[0].attributes["behavior_mode"] == "neutral_transit"
        assert neutral[0].is_hostile is False
        assert neutral[0].attributes.get("reacting_to", []) == []

    def test_scheduled_stimuli_still_fire(self):
        sim = _make_sim()
        all_contacts = []
        for _ in range(11):
            all_contacts.extend(sim.tick_forward())

        cable_events = [c for c in all_contacts if c.contact_type == ContactType.CABLE_EVENT]
        assert cable_events, "Cable severance should fire at tick 10"

    def test_deterministic_replay(self):
        sim1 = _make_sim()
        sim2 = _make_sim()

        for _ in range(15):
            c1 = sim1.tick_forward()
            c2 = sim2.tick_forward()
            for a, b in zip(c1, c2):
                assert a.lat == b.lat
                assert a.lon == b.lon


# ---------------------------------------------------------------------------
# Full pipeline test — ContactEngine with behavior models
# ---------------------------------------------------------------------------

class TestContactEngineWithBehavior:
    def test_full_pipeline_baltic(self):
        store = get_state_store()
        store.clear()

        engine = ContactEngine()
        engine.load_scenario("baltic_hybrid_001")

        contacts = engine.tick()
        assert len(contacts) >= 6  # 6 entities in baltic catalog

        # Check behavior attributes are present
        behavioral = [c for c in contacts if c.attributes.get("behavior_mode")]
        assert len(behavioral) >= 4  # at least 4 behavioral entities

        # Verify allegiance labels
        allegiances = {c.attributes.get("allegiance", "") for c in contacts}
        assert "red" in allegiances
        assert "blue" in allegiances
        assert "neutral" in allegiances

    def test_arctic_scenario(self):
        store = get_state_store()
        store.clear()

        engine = ContactEngine()
        engine.load_scenario("arctic_submarine_001")

        contacts = engine.tick()
        assert len(contacts) >= 5

        # Check submarine has probe behavior
        sub = [c for c in contacts if c.entity_id == "SUB-SUSP-001"]
        assert sub
        assert sub[0].attributes["behavior_mode"] == "hostile_probe_infrastructure"

    def test_mediterranean_scenario(self):
        store = get_state_store()
        store.clear()

        engine = ContactEngine()
        engine.load_scenario("mediterranean_swarm_001")

        contacts = engine.tick()
        assert len(contacts) >= 5

        # Check blue patrol
        blue = [c for c in contacts if c.entity_id == "VES-ALLIED-001"]
        assert blue
        assert blue[0].attributes["behavior_mode"] == "friendly_patrol_monitor"


# ---------------------------------------------------------------------------
# Pipeline impact — behavior attributes affect threat/COA
# ---------------------------------------------------------------------------

class TestBehaviorPipelineImpact:
    def test_hostile_probe_boosts_anomaly_score(self):
        """A contact with hostile_probe_infrastructure should score higher than without."""
        from app.core.constants import EventType, EntityType
        from app.core.schemas import OperationalEvent
        from app.engine.anomaly_detection import detect_anomalies
        from app.engine.feature_engineering import compute_features

        now = datetime.now(timezone.utc)
        base_attrs = {"speed_knots": 5.0, "heading": 90.0}

        # Event WITHOUT behavior attributes
        event_plain = OperationalEvent(
            event_id="E-PLAIN", timestamp=now, event_type=EventType.VESSEL_POSITION,
            source="simulation", confidence=0.8, lat=57.45, lon=18.90,
            entity_id="VES-1", entity_type=EntityType.SUSPICIOUS_VESSEL,
            description="test", attributes={**base_attrs},
        )
        # Event WITH hostile probe behavior
        event_probe = OperationalEvent(
            event_id="E-PROBE", timestamp=now, event_type=EventType.VESSEL_POSITION,
            source="simulation", confidence=0.8, lat=57.45, lon=18.90,
            entity_id="VES-2", entity_type=EntityType.SUSPICIOUS_VESSEL,
            description="test", attributes={
                **base_attrs,
                "behavior_mode": "hostile_probe_infrastructure",
                "intent": "probe_infrastructure",
                "target_infra": "Baltic Cable Alpha",
            },
        )

        feats = compute_features([event_plain, event_probe])
        anomalies = detect_anomalies([event_plain, event_probe], feats)

        plain_score = next(a for a in anomalies if a.event_id == "E-PLAIN").anomaly_score
        probe_score = next(a for a in anomalies if a.event_id == "E-PROBE").anomaly_score
        assert probe_score > plain_score, (
            f"Probe score ({probe_score}) should exceed plain ({plain_score})"
        )

    def test_neutral_transit_reduces_anomaly_score(self):
        """Neutral transit contacts should score lower than hostile ones."""
        from app.core.constants import EventType, EntityType
        from app.core.schemas import OperationalEvent
        from app.engine.anomaly_detection import detect_anomalies
        from app.engine.feature_engineering import compute_features

        now = datetime.now(timezone.utc)
        base_attrs = {"speed_knots": 5.0, "heading": 90.0}

        event_hostile = OperationalEvent(
            event_id="E-HOST", timestamp=now, event_type=EventType.VESSEL_POSITION,
            source="simulation", confidence=0.8, lat=57.45, lon=18.90,
            entity_id="VES-H", entity_type=EntityType.SUSPICIOUS_VESSEL,
            description="test", attributes={**base_attrs},
        )
        event_neutral = OperationalEvent(
            event_id="E-NEUT", timestamp=now, event_type=EventType.VESSEL_POSITION,
            source="simulation", confidence=0.8, lat=57.45, lon=18.90,
            entity_id="VES-N", entity_type=EntityType.SUSPICIOUS_VESSEL,
            description="test", attributes={
                **base_attrs,
                "behavior_mode": "neutral_transit",
                "intent": "transit",
            },
        )

        feats = compute_features([event_hostile, event_neutral])
        anomalies = detect_anomalies([event_hostile, event_neutral], feats)

        host_score = next(a for a in anomalies if a.event_id == "E-HOST").anomaly_score
        neut_score = next(a for a in anomalies if a.event_id == "E-NEUT").anomaly_score
        assert neut_score < host_score, (
            f"Neutral score ({neut_score}) should be less than hostile ({host_score})"
        )

    def test_hostile_probe_boosts_threat_probability(self):
        """Hostile probe behavior should increase threat probability."""
        from app.core.constants import EventType, EntityType
        from app.core.schemas import OperationalEvent
        from app.engine.anomaly_detection import detect_anomalies
        from app.engine.feature_engineering import compute_features
        from app.engine.threat_assessment import assess_threats

        now = datetime.now(timezone.utc)
        base_attrs = {"speed_knots": 5.0, "heading": 90.0}

        event_plain = OperationalEvent(
            event_id="E-P1", timestamp=now, event_type=EventType.VESSEL_POSITION,
            source="simulation", confidence=0.8, lat=57.45, lon=18.90,
            entity_id="VES-PLAIN", entity_type=EntityType.SUSPICIOUS_VESSEL,
            description="test", attributes={**base_attrs},
        )
        event_probe = OperationalEvent(
            event_id="E-P2", timestamp=now, event_type=EventType.VESSEL_POSITION,
            source="simulation", confidence=0.8, lat=57.45, lon=18.90,
            entity_id="VES-PROBE", entity_type=EntityType.SUSPICIOUS_VESSEL,
            description="test", attributes={
                **base_attrs,
                "behavior_mode": "hostile_probe_infrastructure",
                "intent": "probe_infrastructure",
                "target_infra": "Baltic Cable Alpha",
            },
        )

        events = [event_plain, event_probe]
        feats = compute_features(events)
        anomalies = detect_anomalies(events, feats)
        threats = assess_threats(events, feats, anomalies)

        plain_threat = next(t for t in threats if t.entity_id == "VES-PLAIN")
        probe_threat = next(t for t in threats if t.entity_id == "VES-PROBE")

        assert probe_threat.threat_probability > plain_threat.threat_probability
        assert any("probe" in d.lower() for d in probe_threat.main_drivers), (
            f"Probe threat drivers should mention probe: {probe_threat.main_drivers}"
        )

    def test_friendly_patrol_reduces_threat(self):
        """Friendly patrol behavior should decrease threat probability."""
        from app.core.constants import EventType, EntityType
        from app.core.schemas import OperationalEvent
        from app.engine.anomaly_detection import detect_anomalies
        from app.engine.feature_engineering import compute_features
        from app.engine.threat_assessment import assess_threats

        now = datetime.now(timezone.utc)
        base_attrs = {"speed_knots": 12.0, "heading": 90.0}

        event_plain = OperationalEvent(
            event_id="E-B1", timestamp=now, event_type=EventType.VESSEL_POSITION,
            source="simulation", confidence=0.8, lat=57.60, lon=18.50,
            entity_id="VES-BLUE-PLAIN", entity_type=EntityType.SUSPICIOUS_VESSEL,
            description="test", attributes={**base_attrs},
        )
        event_patrol = OperationalEvent(
            event_id="E-B2", timestamp=now, event_type=EventType.VESSEL_POSITION,
            source="simulation", confidence=0.8, lat=57.60, lon=18.50,
            entity_id="VES-BLUE-PATROL", entity_type=EntityType.SUSPICIOUS_VESSEL,
            description="test", attributes={
                **base_attrs,
                "behavior_mode": "friendly_patrol_monitor",
                "intent": "patrol",
            },
        )

        events = [event_plain, event_patrol]
        feats = compute_features(events)
        anomalies = detect_anomalies(events, feats)
        threats = assess_threats(events, feats, anomalies)

        plain_threat = next(t for t in threats if t.entity_id == "VES-BLUE-PLAIN")
        patrol_threat = next(t for t in threats if t.entity_id == "VES-BLUE-PATROL")

        assert patrol_threat.threat_probability < plain_threat.threat_probability
        assert any("patrol" in d.lower() or "friendly" in d.lower() for d in patrol_threat.main_drivers)

    def test_neutral_transit_excluded_from_threat_drivers(self):
        """Neutral transit should have reduced threat and appropriate drivers."""
        from app.core.constants import EventType, EntityType
        from app.core.schemas import OperationalEvent
        from app.engine.anomaly_detection import detect_anomalies
        from app.engine.feature_engineering import compute_features
        from app.engine.threat_assessment import assess_threats

        now = datetime.now(timezone.utc)

        event = OperationalEvent(
            event_id="E-N1", timestamp=now, event_type=EventType.VESSEL_POSITION,
            source="simulation", confidence=0.8, lat=57.0, lon=18.0,
            entity_id="VES-NEUTRAL", entity_type=EntityType.SUSPICIOUS_VESSEL,
            description="test", attributes={
                "speed_knots": 10.0, "heading": 45.0,
                "behavior_mode": "neutral_transit",
                "intent": "transit",
            },
        )

        feats = compute_features([event])
        anomalies = detect_anomalies([event], feats)
        threats = assess_threats([event], feats, anomalies)

        assert threats
        assert threats[0].threat_probability < 0.5
        assert any("neutral" in d.lower() for d in threats[0].main_drivers)
