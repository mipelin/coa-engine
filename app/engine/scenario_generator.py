"""Scenario Generator + Stimuli Timeline.

Produces reusable, configurable, reproducible operational scenarios.
Each scenario template defines initial entities, a stimuli timeline,
environment conditions, and a seed for deterministic replay.

No LLM calls.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Any

from .geo_validation import clamp_wgs84

logger = logging.getLogger("coa_engine.engine.scenario_generator")


@dataclass
class StimulusEvent:
    tick: int
    action: str
    entity: str | None = None
    lat: float | None = None
    lon: float | None = None
    new_heading: float | None = None
    new_speed: float | None = None
    radius_nm: float | None = None

    def to_trigger(self) -> dict[str, Any]:
        d: dict[str, Any] = {"tick": self.tick, "action": self.action}
        if self.entity is not None:
            d["entity"] = self.entity
        if self.lat is not None:
            d["lat"] = self.lat
        if self.lon is not None:
            d["lon"] = self.lon
        if self.new_heading is not None:
            d["new_heading"] = self.new_heading
        if self.new_speed is not None:
            d["new_speed"] = self.new_speed
        if self.radius_nm is not None:
            d["radius_nm"] = self.radius_nm
        return d


@dataclass
class EntitySpec:
    entity_id: str
    name: str
    type: str  # ContactType value
    hostile: bool
    allegiance: str
    lat: float
    lon: float
    speed: float
    heading: float
    flag: str = "unknown"
    behavior_policy: str | None = None
    behavior_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScenarioTemplate:
    scenario_id: str
    display_name: str
    description: str
    entities: list[EntitySpec]
    stimuli: list[StimulusEvent]
    bounds: dict[str, float]
    initial_threat_level: str = "LOW"
    environment: dict[str, Any] = field(default_factory=dict)
    seed: int = 42

    @property
    def metadata(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "display_name": self.display_name,
            "description": self.description,
            "initial_threat_level": self.initial_threat_level,
            "entity_count": len(self.entities),
            "stimuli_count": len(self.stimuli),
            "environment": self.environment,
            "seed": self.seed,
        }

    def upcoming_stimuli(self, current_tick: int) -> list[StimulusEvent]:
        return [s for s in self.stimuli if s.tick > current_tick]

    def active_stimuli(self, current_tick: int) -> list[StimulusEvent]:
        return [s for s in self.stimuli if s.tick == current_tick]


# ---------------------------------------------------------------------------
# Built-in scenario templates
# ---------------------------------------------------------------------------


def _baltic_template(seed: int = 42) -> ScenarioTemplate:
    return ScenarioTemplate(
        scenario_id="baltic_hybrid_001",
        display_name="Baltic Cable Protection — DIANA Scenario",
        description=(
            "NATO Eastern Flank / Baltic Sea. A naval force is deployed to protect "
            "commercial shipping and undersea infrastructure following increased tensions. "
            "Two subsea cables have been detected — Cable Alpha is severed, Cable Beta is "
            "under threat. Suspicious vessels are loitering near the cable area with course "
            "changes. An unidentified UAV has been detected near Visby civilian airport. "
            "Ground convoy activity reported near the border zone. Jamming/radio interference "
            "detected. Social media reports of unmarked convoys. Allied air defence is on alert. "
            "COA analysis considers available assets, logistics, weather, sea conditions, "
            "escalation management, and ROE constraints."
        ),
        entities=[
            # Suspicious vessel 1: probing toward Cable Alpha (at sea, south of cable)
            EntitySpec("VES-SUSP-001", "MV NORDIC WIND", "vessel", True, "red",
                       57.10, 18.80, 8.0, 30.0, flag="Russia",
                       behavior_policy="hostile_probe_infrastructure",
                       behavior_params={"target_infra_name": "Baltic Cable Alpha"}),
            # Suspicious vessel 2: loitering near Cable Beta (at sea)
            EntitySpec("VES-SUSP-002", "RIGA STAR", "vessel", True, "red",
                       57.70, 19.60, 1.2, 45.0, flag="Russia",
                       behavior_policy="hostile_loiter_then_divert",
                       behavior_params={"loiter_area_lat": 57.70, "loiter_area_lon": 19.60,
                                        "divert_tick": 12, "divert_stimulus": "cable_severance",
                                        "divert_heading": 310.0, "divert_speed": 8.0}),
            # Allied patrol vessel: on station in central Baltic (at sea)
            EntitySpec("VES-ALLIED-001", "HMS Visby", "vessel", False, "blue",
                       57.50, 19.00, 12.0, 90.0, flag="Sweden",
                       behavior_policy="friendly_patrol_monitor",
                       behavior_params={"patrol_heading_a": 90.0, "patrol_heading_b": 270.0,
                                        "patrol_flip_ticks": 6, "react_range_km": 50.0}),
            # Unidentified UAV: approaching Visby airport from sea (air — no domain restriction)
            EntitySpec("UAV-001", "Unidentified UAV", "uav", True, "red",
                       57.80, 17.80, 35.0, 200.0, flag="Unknown"),
            # Ground convoy: on land near border zone (Latvia/Estonia border area)
            EntitySpec("CONVOY-001", "Convoy Alpha", "convoy", True, "red",
                       57.30, 24.50, 18.0, 270.0, flag="Russia"),
            # Neutral vessel: transiting through Baltic (at sea, valid route)
            EntitySpec("VES-NEUTRAL-001", "MV BALTIC TRADER", "vessel", False, "neutral",
                       56.50, 18.00, 10.0, 30.0, flag="Liberia",
                       behavior_policy="neutral_transit",
                       behavior_params={"route": [(56.50, 18.00), (56.80, 18.40), (57.10, 18.80),
                                                   (57.40, 19.20), (57.70, 19.60), (58.00, 20.00)]}),
            # Submarine: detected in deeper water (offshore Baltic)
            EntitySpec("SUB-001", "Unknown Submarine Contact", "submarine", True, "red",
                       57.50, 20.00, 4.0, 180.0, flag="Unknown"),
        ],
        stimuli=[
            StimulusEvent(5, "course_change", entity="VES-SUSP-001", new_heading=30.0, new_speed=5.0),
            StimulusEvent(8, "slow_near_cable", entity="VES-SUSP-001", new_speed=0.5),
            StimulusEvent(10, "cable_severance", lat=57.50, lon=19.20),
            StimulusEvent(12, "reposition", entity="UAV-001", lat=57.66, lon=18.35, new_speed=35.0),
            StimulusEvent(14, "course_change", entity="VES-SUSP-002", new_heading=310.0, new_speed=4.0),
            StimulusEvent(16, "convoy_sighting", lat=57.30, lon=24.50),
            StimulusEvent(18, "jamming", lat=57.50, lon=19.00, radius_nm=20),
            StimulusEvent(20, "social_media_report", lat=57.30, lon=24.50),
            StimulusEvent(22, "course_change", entity="VES-SUSP-001", new_heading=180.0, new_speed=0.0),
            StimulusEvent(25, "satellite_detection", lat=57.80, lon=19.60),
            StimulusEvent(28, "jamming", lat=57.50, lon=19.00, radius_nm=35),
        ],
        bounds={"lat_min": 55.0, "lat_max": 60.0, "lon_min": 17.0, "lon_max": 26.0},
        environment={"sea_state": 3, "visibility": "good", "time_of_day": "dawn",
                     "weather": "overcast", "wind_kts": 15},
        seed=seed,
    )


def _arctic_template(seed: int = 42) -> ScenarioTemplate:
    return ScenarioTemplate(
        scenario_id="arctic_submarine_001",
        display_name="Arctic Support Denial",
        description="Submarine and surface vessels threaten Arctic communication cables. Limited allied presence.",
        entities=[
            EntitySpec("SUB-SUSP-001", "Kilo-class Sub", "submarine", True, "red",
                       72.50, 25.00, 5.0, 180.0, flag="Russia",
                       behavior_policy="hostile_probe_infrastructure",
                       behavior_params={"target_infra_name": "Svalbard Undersea Cable"}),
            EntitySpec("VES-SUSP-001", "Icebreaker Sigrid", "vessel", True, "red",
                       74.00, 20.00, 3.0, 45.0, flag="Russia",
                       behavior_policy="hostile_loiter_then_divert",
                       behavior_params={"loiter_area_lat": 74.00, "loiter_area_lon": 20.00,
                                        "divert_tick": 14, "divert_stimulus": "cable_severance",
                                        "divert_heading": 225.0, "divert_speed": 6.0}),
            EntitySpec("VES-ALLIED-001", "HNoMS Fridtjof Nansen", "vessel", False, "blue",
                       71.00, 19.00, 14.0, 0.0, flag="Norway",
                       behavior_policy="friendly_patrol_monitor",
                       behavior_params={"patrol_heading_a": 0.0, "patrol_heading_b": 180.0,
                                        "patrol_flip_ticks": 8, "react_range_km": 60.0}),
            EntitySpec("UAV-001", "Recon UAV", "uav", True, "red",
                       69.40, 16.00, 40.0, 90.0, flag="Russia"),
            EntitySpec("VES-NEUTRAL-001", "FV ARCTIC SUN", "vessel", False, "neutral",
                       70.00, 15.00, 8.0, 30.0, flag="Norway",
                       behavior_policy="neutral_transit",
                       behavior_params={"route": [(70.00, 15.00), (71.00, 16.00), (72.00, 17.00),
                                                   (73.00, 18.00), (74.00, 19.00)]}),
        ],
        stimuli=[
            StimulusEvent(6, "course_change", entity="SUB-SUSP-001", new_heading=225.0, new_speed=8.0),
            StimulusEvent(10, "jamming", lat=74.00, lon=20.00, radius_nm=25),
            StimulusEvent(14, "cable_severance", lat=78.00, lon=15.00),
            StimulusEvent(18, "surface", entity="SUB-SUSP-001", new_speed=2.0),
        ],
        bounds={"lat_min": 68.0, "lat_max": 80.0, "lon_min": 10.0, "lon_max": 35.0},
        environment={"sea_state": 5, "visibility": "poor", "ice_cover": "partial"},
        seed=seed,
    )


def _mediterranean_template(seed: int = 42) -> ScenarioTemplate:
    return ScenarioTemplate(
        scenario_id="mediterranean_001",
        display_name="Mediterranean Airspace Pressure",
        description="Vessels probe offshore infrastructure while UAVs pressure civilian airspace.",
        entities=[
            EntitySpec("VES-SUSP-001", "HELIOS VOYAGE", "vessel", True, "red",
                       34.50, 32.00, 2.0, 0.0, flag="Unknown",
                       behavior_policy="hostile_probe_infrastructure",
                       behavior_params={"target_infra_name": "Cyprus Communication Node"}),
            EntitySpec("VES-SUSP-002", "AEGEAN TRADER", "vessel", True, "red",
                       35.00, 28.00, 8.0, 120.0, flag="Unknown",
                       behavior_policy="hostile_loiter_then_divert",
                       behavior_params={"loiter_area_lat": 35.00, "loiter_area_lon": 28.00,
                                        "divert_tick": 16, "divert_stimulus": "cable_severance",
                                        "divert_heading": 180.0, "divert_speed": 10.0}),
            EntitySpec("VES-ALLIED-001", "HS Kanaris", "vessel", False, "blue",
                       35.48, 24.15, 16.0, 90.0, flag="Greece",
                       behavior_policy="friendly_patrol_monitor",
                       behavior_params={"patrol_heading_a": 90.0, "patrol_heading_b": 270.0,
                                        "patrol_flip_ticks": 5, "react_range_km": 55.0}),
            EntitySpec("UAV-001", "Recon Drone", "uav", True, "red",
                       35.50, 24.10, 35.0, 180.0, flag="Unknown"),
            EntitySpec("VES-NEUTRAL-001", "MV EASTERN STAR", "vessel", False, "neutral",
                       34.00, 25.00, 12.0, 90.0, flag="Malta",
                       behavior_policy="neutral_transit",
                       behavior_params={"route": [(34.00, 25.00), (34.20, 26.00), (34.40, 27.00),
                                                   (34.60, 28.00), (34.80, 29.00), (35.00, 30.00)]}),
        ],
        stimuli=[
            StimulusEvent(5, "course_change", entity="VES-SUSP-001", new_heading=15.0, new_speed=2.0),
            StimulusEvent(8, "jamming", lat=34.50, lon=32.00, radius_nm=15),
            StimulusEvent(12, "cable_severance", lat=35.17, lon=33.37),
            StimulusEvent(16, "course_change", entity="VES-SUSP-002", new_heading=180.0, new_speed=10.0),
            StimulusEvent(20, "jamming", lat=34.50, lon=32.00, radius_nm=30),
        ],
        bounds={"lat_min": 33.0, "lat_max": 37.0, "lon_min": 22.0, "lon_max": 36.0},
        environment={"sea_state": 2, "visibility": "excellent", "time_of_day": "midday"},
        seed=seed,
    )


_TEMPLATE_BUILDERS: dict[str, callable] = {
    "baltic_hybrid_001": _baltic_template,
    "arctic_submarine_001": _arctic_template,
    "mediterranean_001": _mediterranean_template,
    "mediterranean_swarm_001": _mediterranean_template,  # alias
}


class ScenarioGenerator:
    """Generates scenario templates with optional randomization."""

    def __init__(self, seed: int = 42, timing_jitter: int = 0, position_jitter: float = 0.0,
                 confidence_jitter: float = 0.0) -> None:
        self.seed = seed
        self.timing_jitter = timing_jitter
        self.position_jitter = position_jitter
        self.confidence_jitter = confidence_jitter

    def generate(self, scenario_id: str) -> ScenarioTemplate:
        builder = _TEMPLATE_BUILDERS.get(scenario_id)
        if builder is None:
            raise ValueError(f"Unknown scenario template: {scenario_id}")

        template = builder(seed=self.seed)

        if self.timing_jitter or self.position_jitter:
            template = self._apply_variation(template)

        return template

    def _apply_variation(self, template: ScenarioTemplate) -> ScenarioTemplate:
        rng = random.Random(template.seed)

        # Timing jitter: shift each stimulus tick by ±timing_jitter
        if self.timing_jitter:
            new_stimuli = []
            for s in template.stimuli:
                offset = rng.randint(-self.timing_jitter, self.timing_jitter)
                new_tick = max(1, s.tick + offset)
                new_stimuli.append(StimulusEvent(
                    tick=new_tick, action=s.action, entity=s.entity,
                    lat=s.lat, lon=s.lon, new_heading=s.new_heading,
                    new_speed=s.new_speed, radius_nm=s.radius_nm,
                ))
            new_stimuli.sort(key=lambda s: s.tick)
            template.stimuli = new_stimuli

        # Position jitter: shift each entity position by ±position_jitter degrees
        if self.position_jitter:
            jitter = self.position_jitter
            for ent in template.entities:
                ent.lat += rng.uniform(-jitter, jitter)
                ent.lon += rng.uniform(-jitter, jitter)
                ent.lat, ent.lon = clamp_wgs84(ent.lat, ent.lon)

        return template

    @staticmethod
    def list_templates() -> list[dict[str, str]]:
        return [
            {"scenario_id": sid, "display_name": _TEMPLATE_BUILDERS[sid](seed=0).display_name}
            for sid in sorted(_TEMPLATE_BUILDERS.keys())
        ]
