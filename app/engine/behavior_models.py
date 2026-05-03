"""Behavior-model layer for live simulation.

Deterministic, seed-driven behavior policies that drive red/blue/neutral
entity movement and emit behavior attributes on contacts.

Policies:
  - hostile_probe_infrastructure: red vessel moves toward critical infrastructure
  - hostile_loiter_then_divert: red vessel loiters, then diverts on trigger
  - friendly_patrol_monitor: blue asset patrols a sector, reacts to threats
  - neutral_transit: civilian vessel follows a normal route
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .geo_validation import (
    is_on_land,
    is_at_sea,
    snap_to_water,
    snap_to_land,
    validate_movement,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

EARTH_RADIUS_KM = 6371.0
NM_PER_KM = 1.0 / 1.852


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(min(1.0, a)))


def bearing_to(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = rlon2 - rlon1
    x = math.sin(dlon) * math.cos(rlat2)
    y = math.cos(rlat1) * math.sin(rlat2) - math.sin(rlat1) * math.cos(rlat2) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def move_along_heading(
    lat: float, lon: float, heading: float, speed_kts: float, dt_hours: float = 2.0 / 60.0,
) -> tuple[float, float]:
    dist_nm = speed_kts * dt_hours
    dist_km = dist_nm * 1.852
    heading_rad = math.radians(heading)
    dlat = dist_km * math.cos(heading_rad) / 111.0
    cos_lat = math.cos(math.radians(lat)) if abs(lat) < 89.9 else 0.017
    dlon = dist_km * math.sin(heading_rad) / (111.0 * cos_lat) if cos_lat else 0.0
    return lat + dlat, lon + dlon


def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


# ---------------------------------------------------------------------------
# Context passed to every policy on each tick
# ---------------------------------------------------------------------------

@dataclass
class BehaviorContext:
    """World state visible to behavior policies."""
    tick: int
    infrastructure: list[dict[str, Any]] = field(default_factory=list)
    contacts: list[dict[str, Any]] = field(default_factory=list)
    active_stimuli: list[str] = field(default_factory=list)
    active_incidents: list[str] = field(default_factory=list)
    priority_targets: list[dict[str, Any]] = field(default_factory=list)
    scenario_bounds: dict[str, float] | None = None


# ---------------------------------------------------------------------------
# Policy result
# ---------------------------------------------------------------------------

@dataclass
class BehaviorResult:
    lat: float
    lon: float
    speed: float
    heading: float
    attributes: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Policy 1: hostile_probe_infrastructure
# ---------------------------------------------------------------------------

@dataclass
class HostileProbeInfrastructure:
    """Red vessel steers toward the nearest critical infrastructure (cable, etc.).

    Approaches at cruise speed, slows when close, may change course near the
    target.  All decisions are deterministic given the seed.
    """

    target_infra_name: str | None = None  # None → pick nearest cable automatically
    approach_speed: float = 8.0
    slow_speed: float = 0.5
    close_range_km: float = 10.0
    probe_offset_heading: float = 30.0  # offset when very close to target

    def _pick_target(self, ctx: BehaviorContext) -> dict[str, Any] | None:
        if self.target_infra_name and "cable_severance" not in ctx.active_stimuli:
            for infra in ctx.infrastructure:
                if infra.get("name") == self.target_infra_name:
                    return infra
        if "cable_severance" in ctx.active_stimuli:
            cables = [i for i in ctx.infrastructure if i.get("type") == "subsea_cable"]
            if self.target_infra_name:
                alternate = [infra for infra in cables if infra.get("name") != self.target_infra_name]
                if alternate:
                    return alternate[0]
        # Default: first subsea_cable or nearest infra
        cables = [i for i in ctx.infrastructure if i.get("type") == "subsea_cable"]
        return cables[0] if cables else (ctx.infrastructure[0] if ctx.infrastructure else None)

    def __call__(
        self, entity: dict[str, Any], ctx: BehaviorContext, rng_state: int,
    ) -> BehaviorResult:
        lat = entity["lat"]
        lon = entity["lon"]
        speed = entity.get("speed", self.approach_speed)
        heading = entity.get("heading", 0.0)

        target = self._pick_target(ctx)
        intent = "probe_infrastructure"
        target_name = target.get("name", "unknown") if target else "none"
        reacting_to = []
        rationale = "Continuing deterministic infrastructure probing pattern."

        if target:
            dist = haversine_km(lat, lon, target["lat"], target["lon"])
            bearing = bearing_to(lat, lon, target["lat"], target["lon"])

            if dist > self.close_range_km:
                heading = bearing
                speed = self.approach_speed
                if "cable_severance" in ctx.active_stimuli:
                    reacting_to.append("cable_severance")
                    rationale = f"Shifting probe toward remaining infrastructure after cable severance at {target_name}."
                else:
                    rationale = f"Approaching {target_name} on a deterministic probe route."
            else:
                # Close — slow down and offset to simulate probe/loom behavior
                speed = self.slow_speed
                # Deterministic offset based on tick parity
                offset = self.probe_offset_heading if ctx.tick % 2 == 0 else -self.probe_offset_heading
                heading = (bearing + offset) % 360
                reacting_to.append(f"proximity_to_{target_name}")
                rationale = f"Loitering near {target_name} to sustain probing behavior."

            lat, lon = move_along_heading(lat, lon, heading, speed)

        if ctx.scenario_bounds:
            b = ctx.scenario_bounds
            lat = clamp(lat, b["lat_min"], b["lat_max"])
            lon = clamp(lon, b["lon_min"], b["lon_max"])

        # Surface vessel domain constraint: stay on water
        if is_on_land(lat, lon):
            snap = snap_to_water(lat, lon)
            if snap:
                lat, lon = snap

        return BehaviorResult(
            lat=lat, lon=lon, speed=round(speed, 2), heading=round(heading, 1),
            attributes={
                "behavior_mode": "hostile_probe_infrastructure",
                "intent": intent,
                "target_infra": target_name,
                "reacting_to": reacting_to,
                "behavior_rationale": rationale,
            },
        )


# ---------------------------------------------------------------------------
# Policy 2: hostile_loiter_then_divert
# ---------------------------------------------------------------------------

@dataclass
class HostileLoiterThenDivert:
    """Red vessel loiters in an area, then diverts after a trigger or tick threshold.

    While loitering the vessel drifts slowly in small circles.  Once the
    divert trigger fires (stimulus event or tick threshold), it changes
    heading sharply and increases speed.
    """

    loiter_speed: float = 1.2
    loiter_radius_factor: float = 0.05  # degrees per tick of drift
    divert_tick: int = 12
    divert_stimulus: str | None = "cable_severance"
    divert_heading: float = 310.0
    divert_speed: float = 8.0
    loiter_area_lat: float | None = None
    loiter_area_lon: float | None = None

    def __call__(
        self, entity: dict[str, Any], ctx: BehaviorContext, rng_state: int,
    ) -> BehaviorResult:
        lat = entity["lat"]
        lon = entity["lon"]
        speed = entity.get("speed", self.loiter_speed)
        heading = entity.get("heading", 0.0)
        reacting_to: list[str] = []
        rationale = "Maintaining deterministic loiter pattern."

        # Check divert condition
        stimulus_active = (
            self.divert_stimulus is not None and self.divert_stimulus in ctx.active_stimuli
        )
        tick_threshold = ctx.tick >= self.divert_tick
        diverted = entity.get("_bhv_diverted", False)

        if not diverted and (stimulus_active or tick_threshold):
            if stimulus_active and ctx.infrastructure:
                cables = [infra for infra in ctx.infrastructure if infra.get("type") == "subsea_cable"]
                if cables:
                    alt_target = cables[-1]
                    heading = bearing_to(lat, lon, alt_target["lat"], alt_target["lon"])
                    reacting_to.append(f"remaining_infrastructure_{alt_target.get('name', 'unknown')}")
                    rationale = f"Diverting toward remaining infrastructure after {self.divert_stimulus}."
                else:
                    heading = self.divert_heading
                    rationale = "Divert trigger active; no alternate infrastructure available."
            else:
                heading = self.divert_heading
                rationale = "Divert tick threshold reached."
            speed = self.divert_speed
            diverted = True
            if stimulus_active:
                reacting_to.append(self.divert_stimulus)
            reacting_to.append("divert_triggered")

        if diverted:
            lat, lon = move_along_heading(lat, lon, heading, speed)
            intent = "divert"
        else:
            # Loiter: slow drift in a small circle
            center_lat = self.loiter_area_lat if self.loiter_area_lat is not None else lat
            center_lon = self.loiter_area_lon if self.loiter_area_lon is not None else lon
            # Slowly rotate heading
            heading = (heading + 15.0) % 360
            speed = self.loiter_speed
            # Small drift toward center to stay in area
            dlat = (center_lat - lat) * 0.1
            dlon = (center_lon - lon) * 0.1
            lat, lon = move_along_heading(lat + dlat, lon + dlon, heading, speed)
            intent = "loiter"
            if stimulus_active:
                rationale = f"Holding loiter while reacting to {self.divert_stimulus}."

        if ctx.scenario_bounds:
            b = ctx.scenario_bounds
            lat = clamp(lat, b["lat_min"], b["lat_max"])
            lon = clamp(lon, b["lon_min"], b["lon_max"])

        # Surface vessel domain constraint: stay on water
        if is_on_land(lat, lon):
            snap = snap_to_water(lat, lon)
            if snap:
                lat, lon = snap

        return BehaviorResult(
            lat=lat, lon=lon, speed=round(speed, 2), heading=round(heading, 1),
            attributes={
                "behavior_mode": "hostile_loiter_then_divert",
                "intent": intent,
                "target_infra": "",
                "reacting_to": reacting_to,
                "behavior_rationale": rationale,
                "_bhv_diverted": diverted,
            },
        )


# ---------------------------------------------------------------------------
# Policy 3: friendly_patrol_monitor
# ---------------------------------------------------------------------------

@dataclass
class FriendlyPatrolMonitor:
    """Blue asset patrols a sector with back-and-forth sweeps.

    Reacts to nearby hostile contacts by altering course toward them
    (monitoring / shadowing).  Returns to patrol pattern once the
    threat moves away.
    """

    patrol_heading_a: float = 90.0
    patrol_heading_b: float = 270.0
    patrol_speed: float = 12.0
    patrol_flip_ticks: int = 6
    react_range_km: float = 50.0
    react_speed: float = 16.0

    def __call__(
        self, entity: dict[str, Any], ctx: BehaviorContext, rng_state: int,
    ) -> BehaviorResult:
        lat = entity["lat"]
        lon = entity["lon"]
        speed = entity.get("speed", self.patrol_speed)
        heading = entity.get("heading", self.patrol_heading_a)
        reacting_to: list[str] = []
        rationale = "Maintaining deterministic patrol sweep."

        # Check for nearby hostile contacts
        nearest_hostile: dict[str, Any] | None = None
        nearest_dist = float("inf")
        highest_priority = None
        for target in ctx.priority_targets:
            if target.get("priority_level") not in {"HIGH", "CRITICAL"}:
                continue
            highest_priority = target
            break
        if highest_priority is not None:
            target_lat = highest_priority.get("lat")
            target_lon = highest_priority.get("lon")
            if target_lat is not None and target_lon is not None:
                heading = bearing_to(lat, lon, target_lat, target_lon)
                speed = self.react_speed
                reacting_to.append(f"priority_target_{highest_priority.get('entity_id', 'unknown')}")
                intent = "monitor"
                rationale = f"Shifting toward highest-priority target {highest_priority.get('entity_id', 'unknown')}."
                lat, lon = move_along_heading(lat, lon, heading, speed)
                if ctx.scenario_bounds:
                    b = ctx.scenario_bounds
                    lat = clamp(lat, b["lat_min"], b["lat_max"])
                    lon = clamp(lon, b["lon_min"], b["lon_max"])
                if is_on_land(lat, lon):
                    snap = snap_to_water(lat, lon)
                    if snap:
                        lat, lon = snap
                return BehaviorResult(
                    lat=lat, lon=lon, speed=round(speed, 2), heading=round(heading, 1),
                    attributes={
                        "behavior_mode": "friendly_patrol_monitor",
                        "intent": intent,
                        "target_infra": "",
                        "reacting_to": reacting_to,
                        "behavior_rationale": rationale,
                    },
                )
        for c in ctx.contacts:
            if not c.get("is_hostile", False):
                continue
            d = haversine_km(lat, lon, c.get("lat", 0), c.get("lon", 0))
            if d < nearest_dist:
                nearest_dist = d
                nearest_hostile = c

        if nearest_hostile and nearest_dist < self.react_range_km:
            # React: steer toward hostile
            heading = bearing_to(lat, lon, nearest_hostile["lat"], nearest_hostile["lon"])
            speed = self.react_speed
            reacting_to.append(f"hostile_{nearest_hostile.get('entity_id', 'unknown')}")
            intent = "monitor"
            rationale = f"Repositioning to monitor nearby hostile {nearest_hostile.get('entity_id', 'unknown')}."
        else:
            # Patrol: back and forth
            phase = (ctx.tick // self.patrol_flip_ticks) % 2
            heading = self.patrol_heading_a if phase == 0 else self.patrol_heading_b
            speed = self.patrol_speed
            intent = "patrol"
            rationale = "No high-priority hostile nearby; continuing patrol route."

        lat, lon = move_along_heading(lat, lon, heading, speed)

        if ctx.scenario_bounds:
            b = ctx.scenario_bounds
            lat = clamp(lat, b["lat_min"], b["lat_max"])
            lon = clamp(lon, b["lon_min"], b["lon_max"])

        # Surface vessel domain constraint: stay on water
        if is_on_land(lat, lon):
            snap = snap_to_water(lat, lon)
            if snap:
                lat, lon = snap

        return BehaviorResult(
            lat=lat, lon=lon, speed=round(speed, 2), heading=round(heading, 1),
            attributes={
                "behavior_mode": "friendly_patrol_monitor",
                "intent": intent,
                "target_infra": "",
                "reacting_to": reacting_to,
                "behavior_rationale": rationale,
            },
        )


# ---------------------------------------------------------------------------
# Policy 4: neutral_transit
# ---------------------------------------------------------------------------

@dataclass
class NeutralTransit:
    """Civilian vessel transits along a fixed route at constant speed.

    Should not trigger high threat unless correlated with other suspicious
    indicators.  Simple waypoint-following with wrap-around at route end.
    """

    route: list[tuple[float, float]] = field(default_factory=list)
    transit_speed: float = 10.0
    waypoint_threshold: float = 0.05  # degrees

    def __call__(
        self, entity: dict[str, Any], ctx: BehaviorContext, rng_state: int,
    ) -> BehaviorResult:
        lat = entity["lat"]
        lon = entity["lon"]
        speed = entity.get("speed", self.transit_speed)
        reacting_to: list[str] = []
        rationale = "Following deterministic civilian transit route."

        # Determine current waypoint index
        wp_idx = entity.get("_bhv_wp_idx", 0)
        if not self.route:
            # No route defined — hold position
            return BehaviorResult(
                lat=lat, lon=lon, speed=0.0, heading=entity.get("heading", 0.0),
                attributes={
                    "behavior_mode": "neutral_transit",
                    "intent": "transit",
                    "target_infra": "",
                    "reacting_to": reacting_to,
                    "behavior_rationale": rationale,
                },
            )

        wp_idx = min(wp_idx, len(self.route) - 1)
        target_lat, target_lon = self.route[wp_idx]
        dist = math.hypot(target_lat - lat, target_lon - lon)

        if dist < self.waypoint_threshold:
            wp_idx = (wp_idx + 1) % len(self.route)
            target_lat, target_lon = self.route[wp_idx]

        heading = bearing_to(lat, lon, target_lat, target_lon)
        hazard = next(
            (
                c for c in ctx.contacts
                if c.get("type") in {"jamming", "cable_event"} or c.get("contact_type") in {"jamming", "cable_event"}
            ),
            None,
        )
        if hazard is not None:
            hazard_lat = float(hazard.get("lat", lat))
            hazard_lon = float(hazard.get("lon", lon))
            if haversine_km(lat, lon, hazard_lat, hazard_lon) <= 35.0:
                heading = (bearing_to(hazard_lat, hazard_lon, lat, lon) + 35.0) % 360
                reacting_to.append(f"avoid_{hazard.get('entity_id', hazard.get('type', 'hazard'))}")
                rationale = "Adjusting transit route to avoid nearby jamming/high-risk zone."
        speed = self.transit_speed
        lat, lon = move_along_heading(lat, lon, heading, speed)

        if ctx.scenario_bounds:
            b = ctx.scenario_bounds
            lat = clamp(lat, b["lat_min"], b["lat_max"])
            lon = clamp(lon, b["lon_min"], b["lon_max"])

        # Surface vessel domain constraint: stay on water
        if is_on_land(lat, lon):
            snap = snap_to_water(lat, lon)
            if snap:
                lat, lon = snap

        return BehaviorResult(
            lat=lat, lon=lon, speed=round(speed, 2), heading=round(heading, 1),
            attributes={
                "behavior_mode": "neutral_transit",
                "intent": "transit",
                "target_infra": "",
                "reacting_to": reacting_to,
                "behavior_rationale": rationale,
                "_bhv_wp_idx": wp_idx,
            },
        )


# ---------------------------------------------------------------------------
# Policy registry
# ---------------------------------------------------------------------------

POLICY_REGISTRY: dict[str, type] = {
    "hostile_probe_infrastructure": HostileProbeInfrastructure,
    "hostile_loiter_then_divert": HostileLoiterThenDivert,
    "friendly_patrol_monitor": FriendlyPatrolMonitor,
    "neutral_transit": NeutralTransit,
}


def make_policy(name: str, **kwargs: Any):
    cls = POLICY_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown behavior policy: {name}")
    return cls(**kwargs)
