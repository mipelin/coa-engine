"""Tests for geospatial domain validation, cable geometry, and DIANA scenario fidelity."""

import random
import pytest

from app.engine.geo_validation import (
    is_on_land,
    is_at_sea,
    is_offshore,
    validate_placement,
    validate_movement,
    snap_to_water,
    snap_to_land,
    cable_crosses_land,
    random_water_point,
    random_land_point,
    random_offshore_point,
    BALTIC_MARITIME_CORRIDORS,
    BALTIC_LAND_CORRIDORS,
    BALTIC_SUBMARINE_ZONES,
)
from app.core.constants import SCENARIO_CABLE_ROUTES, CRITICAL_INFRASTRUCTURE
from app.engine.scenario_generator import ScenarioGenerator
from app.engine.combat_contact_generator import CombatContactGenerator
from app.engine.geo_context import describe_location
from app.core.schemas import Contact, OperationalEvent


# ---------------------------------------------------------------------------
# 1. Vessels spawn on water
# ---------------------------------------------------------------------------

class TestVesselsOnWater:
    def test_combat_surface_vessel_spawns_on_water(self):
        gen = CombatContactGenerator(seed=42)
        bounds = {"lat_min": 55.0, "lat_max": 60.0, "lon_min": 17.0, "lon_max": 26.0}
        infra = [i for i in CRITICAL_INFRASTRUCTURE if i["type"] == "subsea_cable"]
        for _ in range(20):
            contact = gen.inject_contact(
                kind="vessel",
                scenario_bounds=bounds,
                infrastructure=infra,
            )
            assert is_at_sea(contact.lat, contact.lon), (
                f"Vessel spawned on land at ({contact.lat}, {contact.lon})"
            )

    def test_scenario_vessels_initially_on_water(self):
        gen = ScenarioGenerator(seed=42)
        template = gen.generate("baltic_hybrid_001")
        for entity in template.entities:
            if entity.type in ("vessel",):
                assert is_at_sea(entity.lat, entity.lon), (
                    f"{entity.name} ({entity.entity_id}) spawned on land at ({entity.lat}, {entity.lon})"
                )

    def test_scenario_json_vessels_on_water(self):
        from app.engine.event_ingestion import load_scenario
        scenario = load_scenario("baltic_hybrid_001")
        for event in scenario.events:
            if event.entity_type.value == "suspicious_vessel" or event.entity_type.value == "allied_vessel":
                assert is_at_sea(event.lat, event.lon), (
                    f"Event {event.event_id}: vessel on land at ({event.lat}, {event.lon})"
                )


# ---------------------------------------------------------------------------
# 2. Submarines spawn on water
# ---------------------------------------------------------------------------

class TestSubmarinesOnWater:
    def test_combat_submarine_spawns_on_water(self):
        gen = CombatContactGenerator(seed=42)
        bounds = {"lat_min": 55.0, "lat_max": 60.0, "lon_min": 17.0, "lon_max": 26.0}
        infra = [i for i in CRITICAL_INFRASTRUCTURE if i["type"] == "subsea_cable"]
        for _ in range(10):
            contact = gen.inject_contact(
                kind="submarine",
                scenario_bounds=bounds,
                infrastructure=infra,
            )
            assert is_at_sea(contact.lat, contact.lon), (
                f"Submarine spawned on land at ({contact.lat}, {contact.lon})"
            )

    def test_scenario_submarine_initially_on_water(self):
        gen = ScenarioGenerator(seed=42)
        template = gen.generate("baltic_hybrid_001")
        for entity in template.entities:
            if entity.type == "submarine":
                assert is_at_sea(entity.lat, entity.lon), (
                    f"{entity.name} ({entity.entity_id}) spawned on land at ({entity.lat}, {entity.lon})"
                )


# ---------------------------------------------------------------------------
# 3. Ground units spawn on land
# ---------------------------------------------------------------------------

class TestGroundUnitsOnLand:
    def test_scenario_convoy_on_land(self):
        gen = ScenarioGenerator(seed=42)
        template = gen.generate("baltic_hybrid_001")
        for entity in template.entities:
            if entity.type == "convoy":
                assert is_on_land(entity.lat, entity.lon), (
                    f"{entity.name} ({entity.entity_id}) spawned at sea at ({entity.lat}, {entity.lon})"
                )

    def test_scenario_json_convoys_on_land(self):
        from app.engine.event_ingestion import load_scenario
        scenario = load_scenario("baltic_hybrid_001")
        for event in scenario.events:
            if event.entity_type.value == "convoy":
                assert is_on_land(event.lat, event.lon), (
                    f"Event {event.event_id}: convoy at sea at ({event.lat}, {event.lon})"
                )


# ---------------------------------------------------------------------------
# 4. Ground units do not move into sea
# ---------------------------------------------------------------------------

class TestGroundMovement:
    def test_ground_movement_stays_on_land(self):
        # Start on land (Latvia), try to move into the Baltic Sea
        lat, lon = 57.30, 24.50  # Known land point in Latvia
        assert is_on_land(lat, lon), "Test setup: start should be on land"

        new_lat, new_lon = validate_movement(lat, lon, 57.50, 19.50, "convoy")
        assert is_on_land(new_lat, new_lon), (
            f"Ground unit moved to sea at ({new_lat}, {new_lon})"
        )

    def test_ground_unit_rejected_at_sea(self):
        result = validate_placement(57.50, 19.50, "convoy")
        assert not result.valid, "Convoy placement at sea should be rejected"
        assert result.warning is not None


# ---------------------------------------------------------------------------
# 5. Vessels do not move onto land
# ---------------------------------------------------------------------------

class TestVesselMovement:
    def test_vessel_movement_stays_on_water(self):
        # Start at sea, heading toward land
        lat, lon = 57.50, 19.50  # At sea
        assert is_at_sea(lat, lon), "Test setup: start should be at sea"

        new_lat, new_lon = validate_movement(lat, lon, 57.60, 17.00, "vessel")
        assert is_at_sea(new_lat, new_lon), (
            f"Vessel moved to land at ({new_lat}, {new_lon})"
        )

    def test_vessel_rejected_on_land(self):
        result = validate_placement(57.30, 22.50, "vessel")
        assert not result.valid, "Vessel placement on land should be rejected"
        assert result.warning is not None


# ---------------------------------------------------------------------------
# 6. Cable polylines do not cross invalid land zones (except landing points)
# ---------------------------------------------------------------------------

class TestCableGeometry:
    def test_baltic_cables_dont_cross_land(self):
        baltic_cables = SCENARIO_CABLE_ROUTES.get("baltic_hybrid_001", [])
        assert len(baltic_cables) >= 2, "Should have at least 2 cables"

        for cable in baltic_cables:
            points = [(p["lat"], p["lon"]) for p in cable["points"]]
            landing_points = cable.get("landing_points", [])
            violations = cable_crosses_land(points, landing_points)
            assert len(violations) == 0, (
                f"Cable '{cable['name']}' has points on land at indices {violations}"
            )

    def test_cables_have_status(self):
        baltic_cables = SCENARIO_CABLE_ROUTES.get("baltic_hybrid_001", [])
        for cable in baltic_cables:
            assert "status" in cable, f"Cable '{cable['name']}' missing status"
            assert cable["status"] in ("intact", "severed", "threatened")

    def test_cables_have_landing_points(self):
        baltic_cables = SCENARIO_CABLE_ROUTES.get("baltic_hybrid_001", [])
        for cable in baltic_cables:
            assert "landing_points" in cable, f"Cable '{cable['name']}' missing landing_points"
            assert len(cable["landing_points"]) >= 2, f"Cable '{cable['name']}' needs at least 2 landing points"

    def test_cable_alpha_severed(self):
        baltic_cables = SCENARIO_CABLE_ROUTES.get("baltic_hybrid_001", [])
        alpha = next(c for c in baltic_cables if "Alpha" in c["name"])
        assert alpha["status"] == "severed"

    def test_cable_beta_threatened(self):
        baltic_cables = SCENARIO_CABLE_ROUTES.get("baltic_hybrid_001", [])
        beta = next(c for c in baltic_cables if "Beta" in c["name"])
        assert beta["status"] == "threatened"


# ---------------------------------------------------------------------------
# 7. Map-click placement rejects or warns on invalid domain
# ---------------------------------------------------------------------------

class TestDomainPlacement:
    def test_vessel_on_land_rejected(self):
        result = validate_placement(57.30, 22.50, "vessel")
        assert not result.valid
        assert "water" in result.warning.lower()

    def test_submarine_on_land_rejected(self):
        result = validate_placement(57.30, 22.50, "submarine")
        assert not result.valid

    def test_ground_at_sea_rejected(self):
        result = validate_placement(57.50, 19.50, "convoy")
        assert not result.valid
        assert "land" in result.warning.lower()

    def test_aircraft_accepted_anywhere(self):
        result = validate_placement(57.50, 19.50, "uav")
        assert result.valid


class TestWGS84Bounds:
    def test_contact_schema_rejects_invalid_wgs84_coordinates(self):
        with pytest.raises(Exception):
            Contact(
                contact_id="BAD",
                timestamp="2026-05-03T00:00:00Z",
                source="test",
                contact_type="vessel",
                lat=91.0,
                lon=19.0,
                entity_id="BAD-1",
            )

    def test_operational_event_schema_rejects_invalid_wgs84_coordinates(self):
        with pytest.raises(Exception):
            OperationalEvent(
                event_id="BAD-EVT",
                timestamp="2026-05-03T00:00:00Z",
                event_type="vessel_position",
                source="test",
                confidence=0.8,
                lat=57.0,
                lon=181.0,
                entity_id="BAD-EVT-1",
                entity_type="suspicious_vessel",
                description="bad",
            )

    def test_scenario_generator_jitter_keeps_coordinates_in_wgs84_range(self):
        template = ScenarioGenerator(seed=42, position_jitter=200.0).generate("baltic_hybrid_001")
        for entity in template.entities:
            assert -90.0 <= entity.lat <= 90.0
            assert -180.0 <= entity.lon <= 180.0


class TestGeoContext:
    def test_geo_context_describes_gotland_area(self):
        assert describe_location(57.63, 18.30) == "Baltic Sea near Visby"

    def test_vessel_on_water_accepted(self):
        result = validate_placement(57.50, 19.50, "vessel")
        assert result.valid

    def test_ground_on_land_accepted(self):
        result = validate_placement(57.00, 24.00, "convoy")
        assert result.valid


# ---------------------------------------------------------------------------
# 8. Coordinates displayed in valid lat/lon format
# ---------------------------------------------------------------------------

class TestCoordinateFormat:
    def test_contact_coordinates_are_lat_lon(self):
        gen = CombatContactGenerator(seed=42)
        bounds = {"lat_min": 55.0, "lat_max": 60.0, "lon_min": 17.0, "lon_max": 26.0}
        infra = [i for i in CRITICAL_INFRASTRUCTURE if i["type"] == "subsea_cable"]
        contact = gen.inject_contact(
            kind="vessel",
            scenario_bounds=bounds,
            infrastructure=infra,
        )
        # Valid lat range
        assert -90 <= contact.lat <= 90, f"Invalid latitude: {contact.lat}"
        assert -180 <= contact.lon <= 180, f"Invalid longitude: {contact.lon}"
        # In Baltic range
        assert 55.0 <= contact.lat <= 60.0, f"Lat out of Baltic: {contact.lat}"
        assert 17.0 <= contact.lon <= 26.0, f"Lon out of Baltic: {contact.lon}"

    def test_infrastructure_coordinates_valid(self):
        for infra in CRITICAL_INFRASTRUCTURE:
            assert -90 <= infra["lat"] <= 90, f"Invalid lat for {infra['name']}"
            assert -180 <= infra["lon"] <= 180, f"Invalid lon for {infra['name']}"

    def test_cable_route_coordinates_valid(self):
        for scenario_id, cables in SCENARIO_CABLE_ROUTES.items():
            for cable in cables:
                for pt in cable["points"]:
                    assert -90 <= pt["lat"] <= 90, f"Invalid lat in {cable['name']}"
                    assert -180 <= pt["lon"] <= 180, f"Invalid lon in {cable['name']}"


# ---------------------------------------------------------------------------
# 9. DIANA scenario includes all required event elements
# ---------------------------------------------------------------------------

class TestDIANAScenarioFidelity:
    def _get_baltic_template(self):
        gen = ScenarioGenerator(seed=42)
        return gen.generate("baltic_hybrid_001")

    def test_scenario_description_mentions_nato(self):
        t = self._get_baltic_template()
        desc = t.description.lower()
        assert "nato" in desc or "eastern flank" in desc or "baltic" in desc

    def test_scenario_has_naval_force(self):
        t = self._get_baltic_template()
        has_vessel = any(e.type == "vessel" for e in t.entities)
        assert has_vessel, "Scenario should have naval vessels"

    def test_scenario_has_suspicious_vessels_near_cable(self):
        t = self._get_baltic_template()
        suspicious_vessels = [e for e in t.entities if e.hostile and e.type == "vessel"]
        assert len(suspicious_vessels) >= 2, "Should have at least 2 suspicious vessels"

    def test_scenario_has_ground_convoy(self):
        t = self._get_baltic_template()
        has_convoy = any(e.type == "convoy" for e in t.entities)
        assert has_convoy, "Scenario should have convoy/ground activity"

    def test_scenario_has_uav(self):
        t = self._get_baltic_template()
        has_uav = any(e.type == "uav" for e in t.entities)
        assert has_uav, "Scenario should have UAV"

    def test_scenario_has_cable_severance(self):
        t = self._get_baltic_template()
        has_severance = any(s.action == "cable_severance" for s in t.stimuli)
        assert has_severance, "Scenario should have cable severance stimulus"

    def test_scenario_has_jamming(self):
        t = self._get_baltic_template()
        has_jamming = any(s.action == "jamming" for s in t.stimuli)
        assert has_jamming, "Scenario should have jamming stimulus"

    def test_scenario_has_social_media(self):
        t = self._get_baltic_template()
        has_social = any(s.action == "social_media_report" for s in t.stimuli)
        assert has_social, "Scenario should have social media reports"

    def test_scenario_has_satellite_detection(self):
        t = self._get_baltic_template()
        has_sat = any(s.action == "satellite_detection" for s in t.stimuli)
        assert has_sat, "Scenario should have satellite detection"

    def test_scenario_has_course_changes(self):
        t = self._get_baltic_template()
        has_course = any(s.action == "course_change" for s in t.stimuli)
        assert has_course, "Scenario should have course changes"

    def test_scenario_has_two_cables(self):
        cables = SCENARIO_CABLE_ROUTES.get("baltic_hybrid_001", [])
        assert len(cables) >= 2, "Should have at least 2 cables"
        statuses = {c["name"]: c["status"] for c in cables}
        assert any(s == "severed" for s in statuses.values()), "At least one cable should be severed"
        assert any(s == "threatened" for s in statuses.values()), "At least one cable should be threatened"

    def test_scenario_has_submarine(self):
        t = self._get_baltic_template()
        has_sub = any(e.type == "submarine" for e in t.entities)
        assert has_sub, "Scenario should have submarine contact"

    def test_scenario_has_weather_conditions(self):
        t = self._get_baltic_template()
        env = t.environment
        assert "sea_state" in env, "Environment should include sea_state"
        assert "visibility" in env, "Environment should include visibility"

    def test_scenario_has_roe_context(self):
        """Description mentions escalation and ROE."""
        t = self._get_baltic_template()
        desc = t.description.lower()
        assert "roe" in desc or "escalation" in desc or "rules of engagement" in desc

    def test_scenario_json_diana_elements(self):
        """Verify the JSON scenario has all DIANA event types."""
        from app.engine.event_ingestion import load_scenario
        scenario = load_scenario("baltic_hybrid_001")
        event_types = {e.event_type.value for e in scenario.events}
        assert "cable_severance" in event_types
        assert "uav_detection" in event_types
        assert "convoy_sighting" in event_types
        assert "jamming_detected" in event_types
        assert "satellite_detection" in event_types
        assert "social_media_report" in event_types
        assert "vessel_course_change" in event_types

    def test_scenario_json_cable_status_entities(self):
        from app.engine.event_ingestion import load_scenario
        scenario = load_scenario("baltic_hybrid_001")
        entities = scenario.entities
        assert "CABLE-ALPHA" in entities
        assert entities["CABLE-ALPHA"]["status"] == "SEVERED"
        assert "CABLE-BETA" in entities
        assert entities["CABLE-BETA"]["status"] == "AT RISK"


# ---------------------------------------------------------------------------
# 10. Suspicious vessel near cable influences threat/COA
# ---------------------------------------------------------------------------

class TestThreatInfluence:
    def test_suspicious_vessel_near_cable_scenario(self):
        """Verify scenario has suspicious vessels positioned near cables."""
        gen = ScenarioGenerator(seed=42)
        template = gen.generate("baltic_hybrid_001")
        from app.engine.behavior_models import haversine_km

        cables = [i for i in CRITICAL_INFRASTRUCTURE if i["type"] == "subsea_cable"]
        suspicious = [e for e in template.entities if e.hostile and e.type == "vessel"]

        # At least one suspicious vessel should be within 50km of a cable
        near_cable = False
        for vessel in suspicious:
            for cable in cables:
                dist = haversine_km(vessel.lat, vessel.lon, cable["lat"], cable["lon"])
                if dist < 50:
                    near_cable = True
        assert near_cable, "At least one suspicious vessel should be near a cable"


# ---------------------------------------------------------------------------
# Random point generation tests
# ---------------------------------------------------------------------------

class TestRandomPoints:
    def test_random_water_point_is_at_sea(self):
        rng = random.Random(42)
        for _ in range(10):
            lat, lon = random_water_point(rng)
            assert is_at_sea(lat, lon), f"Random water point on land: ({lat}, {lon})"

    def test_random_land_point_is_on_land(self):
        rng = random.Random(42)
        for _ in range(10):
            lat, lon = random_land_point(rng)
            assert is_on_land(lat, lon), f"Random land point at sea: ({lat}, {lon})"

    def test_random_offshore_point_is_offshore(self):
        rng = random.Random(42)
        for _ in range(10):
            lat, lon = random_offshore_point(rng)
            assert is_at_sea(lat, lon), f"Random offshore point on land: ({lat}, {lon})"


# ---------------------------------------------------------------------------
# Snap functions
# ---------------------------------------------------------------------------

class TestSnapFunctions:
    def test_snap_to_water_from_land(self):
        # Point on Gotland
        lat, lon = 57.40, 18.30
        assert is_on_land(lat, lon), "Test setup: should be on Gotland"
        result = snap_to_water(lat, lon)
        assert result is not None
        assert is_at_sea(result[0], result[1])

    def test_snap_to_land_from_sea(self):
        lat, lon = 57.50, 19.50
        assert is_at_sea(lat, lon), "Test setup: should be at sea"
        result = snap_to_land(lat, lon)
        assert result is not None
        assert is_on_land(result[0], result[1])


# ---------------------------------------------------------------------------
# Corridor validation
# ---------------------------------------------------------------------------

class TestCorridors:
    def test_maritime_corridors_have_points(self):
        for name, corridor in BALTIC_MARITIME_CORRIDORS.items():
            assert len(corridor) >= 2, f"Corridor {name} needs at least 2 points"

    def test_land_corridors_have_points(self):
        for name, corridor in BALTIC_LAND_CORRIDORS.items():
            assert len(corridor) >= 2, f"Corridor {name} needs at least 2 points"

    def test_submarine_zones_defined(self):
        assert len(BALTIC_SUBMARINE_ZONES) >= 2, "Need at least 2 submarine zones"
