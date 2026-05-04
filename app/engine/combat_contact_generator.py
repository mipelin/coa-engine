from __future__ import annotations

"""Synthetic combat-system contact feed generator.

Produces ship CMS-like contacts from radar/sonar/ESM/fused sources without
mutating decision logic or simulation entities.
"""

import hashlib
import logging
import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..core.schemas import Contact, ContactType

logger = logging.getLogger("coa_engine.engine.combat_contact_generator")

_DENSITY_MULTIPLIER = {"low": 0.65, "medium": 1.0, "high": 1.45}
_SCENARIO_MODES = {"civilian_traffic", "mixed_traffic", "high_threat_environment"}

# Domain-aware position generation for Baltic scenarios
from .geo_validation import (
    is_on_land, is_at_sea, is_offshore,
    random_water_point, random_land_point, random_offshore_point,
    validate_movement as geo_validate_movement, clamp_wgs84,
    BALTIC_BOUNDS as GEO_BALTIC_BOUNDS,
)


def _stable_seed(*parts: object) -> int:
    digest = hashlib.sha256(":".join(str(part) for part in parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    return math.degrees(math.atan2(dlon, dlat)) % 360


def _step(lat: float, lon: float, heading: float, speed_kts: float, hours: float = 2.0 / 60.0) -> tuple[float, float]:
    dist_nm = max(speed_kts, 0.0) * hours
    dist_km = dist_nm * 1.852
    heading_rad = math.radians(heading)
    dlat = dist_km * math.cos(heading_rad) / 111.0
    lat_safe = max(0.1, abs(lat))
    dlon = dist_km * math.sin(heading_rad) / (111.0 * math.cos(math.radians(lat_safe)))
    return lat + dlat, lon + dlon


def _midpoint(bounds: dict[str, float]) -> tuple[float, float]:
    return (
        (bounds["lat_min"] + bounds["lat_max"]) / 2.0,
        (bounds["lon_min"] + bounds["lon_max"]) / 2.0,
    )


@dataclass
class CombatTrack:
    track_id: str
    domain: str
    subtype: str
    allegiance: str
    sensor_source: str
    track_quality: str
    lat: float
    lon: float
    heading: float
    speed: float
    altitude_ft: float | None = None
    depth_m: float | None = None
    confidence: float = 0.8
    suspicious: bool = False
    behavior_flags: list[str] = field(default_factory=list)
    waypoints: list[tuple[float, float]] = field(default_factory=list)
    waypoint_index: int = 0
    loiter_center: tuple[float, float] | None = None
    target_infra: tuple[float, float] | None = None
    loiter_radius_nm: float = 0.0
    intermittent_visibility: bool = False
    last_visible_tick: int = 0
    visible_gap: int = 0
    rng_seed: int = 0
    created_tick: int = 0
    entity_prefix: str = "CMS"

    def entity_id(self) -> str:
        return f"{self.entity_prefix}-{self.track_id}"


class CombatContactGenerator:
    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.enabled = False
        self.density = "medium"
        self.scenario_type = "mixed_traffic"
        self._tracks: dict[str, CombatTrack] = {}
        self._injected_counter = 0
        self._scenario_key: tuple[int, str, str] | None = None

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.seed = seed
        self._tracks.clear()
        self._injected_counter = 0
        self._scenario_key = None

    def configure(
        self,
        *,
        enabled: bool | None = None,
        density: str | None = None,
        scenario_type: str | None = None,
        seed: int | None = None,
    ) -> None:
        if seed is not None and seed != self.seed:
            self.reset(seed=seed)
        if enabled is not None:
            self.enabled = enabled
        if density in _DENSITY_MULTIPLIER:
            self.density = density
        if scenario_type in _SCENARIO_MODES:
            self.scenario_type = scenario_type

    def inject_contact(
        self,
        *,
        kind: str,
        scenario_bounds: dict[str, float],
        infrastructure: list[dict[str, Any]] | None = None,
        subtype: str | None = None,
        suspicious: bool = False,
        allegiance: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        heading: float | None = None,
        speed: float | None = None,
        altitude_ft: float | None = None,
        depth_m: float | None = None,
        sensor_source: str | None = None,
        track_quality: str | None = None,
        timestamp: datetime | None = None,
    ) -> Contact:
        self._injected_counter += 1
        track = self._build_track(
            f"INJ-{self._injected_counter:04d}",
            kind=kind,
            scenario_bounds=scenario_bounds,
            infrastructure=infrastructure or [],
            subtype=subtype,
            suspicious=suspicious,
            allegiance=allegiance,
            lat=lat,
            lon=lon,
            heading=heading,
            speed=speed,
            altitude_ft=altitude_ft,
            depth_m=depth_m,
            sensor_source=sensor_source,
            track_quality=track_quality,
            created_tick=0,
        )
        self._tracks[track.track_id] = track
        return self._track_to_contact(track, timestamp or datetime.now(timezone.utc), tick=0)

    def generate(
        self,
        *,
        tick: int,
        scenario_bounds: dict[str, float],
        infrastructure: list[dict[str, Any]] | None = None,
    ) -> list[Contact]:
        if not self.enabled:
            return []
        infrastructure = infrastructure or []
        scenario_key = (self.seed, self.density, self.scenario_type)
        if self._scenario_key != scenario_key:
            injected_tracks = {track_id: track for track_id, track in self._tracks.items() if track_id.startswith("INJ-")}
            self._scenario_key = scenario_key
            self._tracks = injected_tracks

        self._ensure_population(tick=tick, scenario_bounds=scenario_bounds, infrastructure=infrastructure)
        now = datetime.now(timezone.utc)
        contacts: list[Contact] = []

        for track in self._tracks.values():
            self._advance_track(track, tick, scenario_bounds, infrastructure)
            if track.domain == "subsurface":
                visibility_roll = track_rng(track, tick).random()
                if visibility_roll > self._subsurface_visibility(track):
                    track.visible_gap += 1
                    continue
            if track.visible_gap:
                track.behavior_flags.append("signal_reacquired")
                track.visible_gap = 0
            contacts.append(self._track_to_contact(track, now, tick=tick))
        return contacts

    def _ensure_population(
        self,
        *,
        tick: int,
        scenario_bounds: dict[str, float],
        infrastructure: list[dict[str, Any]],
    ) -> None:
        counts = self._desired_counts()
        current = self._counts_by_domain()
        for domain, target in counts.items():
            while current.get(domain, 0) < target:
                track_id = f"{domain[:1].upper()}{tick:04d}{current.get(domain, 0):02d}{len(self._tracks):02d}"
                self._tracks[track_id] = self._build_track(
                    track_id,
                    kind=domain,
                    scenario_bounds=scenario_bounds,
                    infrastructure=infrastructure,
                    created_tick=tick,
                )
                current[domain] = current.get(domain, 0) + 1

    def _desired_counts(self) -> dict[str, int]:
        factor = _DENSITY_MULTIPLIER.get(self.density, 1.0)
        if self.scenario_type == "civilian_traffic":
            return {
                "air": max(2, round(4 * factor)),
                "surface": max(3, round(6 * factor)),
                "subsurface": max(0, round(1 * factor) - 1),
                "unknown": 1,
            }
        if self.scenario_type == "high_threat_environment":
            return {
                "air": max(3, round(5 * factor)),
                "surface": max(4, round(5 * factor)),
                "subsurface": max(1, round(3 * factor)),
                "unknown": max(1, round(2 * factor)),
            }
        return {
            "air": max(3, round(4 * factor)),
            "surface": max(4, round(5 * factor)),
            "subsurface": max(1, round(2 * factor)),
            "unknown": max(1, round(1 * factor)),
        }

    def _counts_by_domain(self) -> dict[str, int]:
        counts = {"air": 0, "surface": 0, "subsurface": 0, "unknown": 0}
        for track in self._tracks.values():
            counts[track.domain] = counts.get(track.domain, 0) + 1
        return counts

    def _build_track(
        self,
        track_id: str,
        *,
        kind: str,
        scenario_bounds: dict[str, float],
        infrastructure: list[dict[str, Any]],
        subtype: str | None = None,
        suspicious: bool = False,
        allegiance: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        heading: float | None = None,
        speed: float | None = None,
        altitude_ft: float | None = None,
        depth_m: float | None = None,
        sensor_source: str | None = None,
        track_quality: str | None = None,
        created_tick: int = 0,
    ) -> CombatTrack:
        rng = random.Random(_stable_seed(self.seed, track_id))
        domain = self._normalize_domain(kind)
        if subtype is None:
            subtype = self._default_subtype(domain, suspicious=suspicious, rng=rng)
        if allegiance is None:
            allegiance = self._default_allegiance(domain, suspicious=suspicious, rng=rng)
        sensor_source = sensor_source or self._default_sensor_source(domain, suspicious=suspicious, allegiance=allegiance)
        track_quality = track_quality or self._default_quality(sensor_source)

        if lat is None or lon is None:
            lat, lon = self._default_position(domain, scenario_bounds, infrastructure, rng)
        if heading is None:
            heading = self._default_heading(domain, rng, suspicious=suspicious, lat=lat, lon=lon, infrastructure=infrastructure)
        if speed is None:
            speed = self._default_speed(domain, subtype, suspicious=suspicious, rng=rng)
        if altitude_ft is None and domain == "air":
            altitude_ft = self._default_altitude(subtype, suspicious=suspicious, rng=rng)
        if depth_m is None and domain == "subsurface":
            depth_m = self._default_depth(suspicious=suspicious, rng=rng)

        behavior_flags = self._default_behavior_flags(domain, subtype, suspicious=suspicious)
        loiter_center = None
        target_infra = None
        loiter_radius_nm = 0.0
        waypoints: list[tuple[float, float]] = []
        if domain == "air":
            waypoints = self._air_route(lat, lon, scenario_bounds, suspicious=suspicious, rng=rng)
            if suspicious:
                target = self._nearest_infra(lat, lon, infrastructure)
                if target is not None:
                    target_infra = target
        elif domain == "surface":
            waypoints = self._surface_route(lat, lon, scenario_bounds, suspicious=suspicious, infrastructure=infrastructure, rng=rng)
            if suspicious:
                behavior_flags.append("course_toward_infrastructure")
                target = self._nearest_infra(lat, lon, infrastructure)
                if target is not None:
                    heading = _bearing(lat, lon, target[0], target[1])
                    target_infra = target
        elif domain == "subsurface":
            loiter_center = (lat, lon)
            loiter_radius_nm = 8.0 if suspicious else 14.0
            if suspicious:
                target = self._nearest_infra(lat, lon, infrastructure)
                if target is not None:
                    target_infra = target
        else:
            behavior_flags.append("unknown_track")

        confidence = self._confidence(domain, sensor_source, track_quality, suspicious=suspicious, allegiance=allegiance)
        return CombatTrack(
            track_id=track_id,
            domain=domain,
            subtype=subtype,
            allegiance=allegiance,
            sensor_source=sensor_source,
            track_quality=track_quality,
            lat=lat,
            lon=lon,
            heading=heading % 360,
            speed=speed,
            altitude_ft=altitude_ft,
            depth_m=depth_m,
            confidence=confidence,
            suspicious=suspicious,
            behavior_flags=behavior_flags,
            waypoints=waypoints,
            loiter_center=loiter_center,
            target_infra=target_infra,
            loiter_radius_nm=loiter_radius_nm,
            intermittent_visibility=(domain == "subsurface"),
            last_visible_tick=created_tick,
            rng_seed=_stable_seed(self.seed, track_id),
            created_tick=created_tick,
        )

    def _normalize_domain(self, kind: str) -> str:
        kind = (kind or "").lower()
        if kind in {"air", "aircraft", "uav", "helicopter"}:
            return "air"
        if kind in {"surface", "vessel", "ship"}:
            return "surface"
        if kind in {"subsurface", "submarine"}:
            return "subsurface"
        if kind in {"ground", "convoy", "truck", "armor", "infantry"}:
            return "ground"
        return "unknown"

    def _default_subtype(self, domain: str, *, suspicious: bool, rng: random.Random) -> str:
        if domain == "air":
            return rng.choice([
                "commercial_airliner",
                "military_jet" if suspicious or self.scenario_type == "high_threat_environment" else "helicopter",
                "uav" if suspicious else "commercial_airliner",
            ])
        if domain == "surface":
            if suspicious or self.scenario_type == "high_threat_environment":
                return rng.choice(["warship", "patrol_ship", "fast_attack_craft"])
            return rng.choice(["cargo", "tanker", "ferry", "fishing_vessel"])
        if domain == "subsurface":
            return "submarine"
        return "unknown_track"

    def _default_allegiance(self, domain: str, *, suspicious: bool, rng: random.Random) -> str:
        if suspicious or self.scenario_type == "high_threat_environment":
            return rng.choice(["hostile", "hostile", "unknown"])
        if self.scenario_type == "civilian_traffic":
            return rng.choice(["neutral", "neutral", "friendly"])
        if domain == "air" and rng.random() < 0.4:
            return "neutral"
        return rng.choice(["neutral", "friendly", "unknown"])

    def _default_sensor_source(self, domain: str, *, suspicious: bool, allegiance: str) -> str:
        if domain == "subsurface":
            return "sonar" if suspicious else "fused"
        if domain == "air":
            return "radar" if allegiance == "hostile" else "fused"
        if domain == "surface":
            return "AIS" if allegiance in {"neutral", "friendly"} else "radar"
        return "fused"

    def _default_quality(self, sensor_source: str) -> str:
        return {
            "AIS": "high",
            "radar": "high",
            "sonar": "medium",
            "ESM": "medium",
            "fused": "high",
        }.get(sensor_source, "medium")

    def _default_position(
        self,
        domain: str,
        scenario_bounds: dict[str, float],
        infrastructure: list[dict[str, Any]],
        rng: random.Random,
    ) -> tuple[float, float]:
        lat_min = scenario_bounds["lat_min"]
        lat_max = scenario_bounds["lat_max"]
        lon_min = scenario_bounds["lon_min"]
        lon_max = scenario_bounds["lon_max"]
        mid_lat, mid_lon = _midpoint(scenario_bounds)
        # Check if bounds overlap with Baltic region for geo-validation
        baltic = (
            lat_max >= GEO_BALTIC_BOUNDS["lat_min"]
            and lat_min <= GEO_BALTIC_BOUNDS["lat_max"]
            and lon_max >= GEO_BALTIC_BOUNDS["lon_min"]
            and lon_min <= GEO_BALTIC_BOUNDS["lon_max"]
        )
        if domain == "air":
            return (
                rng.uniform(lat_min, lat_max),
                lon_min if rng.random() < 0.5 else lon_max,
            )
        if domain == "surface":
            if baltic:
                lat, lon = random_water_point(rng, scenario_bounds)
                return lat, lon
            return (
                rng.uniform(lat_min, lat_max),
                rng.uniform(lon_min, lon_max),
            )
        if domain == "subsurface":
            if baltic:
                lat, lon = random_offshore_point(rng, scenario_bounds)
                return lat, lon
            infra = self._nearest_infra(mid_lat, mid_lon, infrastructure)
            if infra is not None:
                return infra[0] + rng.uniform(-0.12, 0.12), infra[1] + rng.uniform(-0.12, 0.12)
            return mid_lat + rng.uniform(-0.2, 0.2), mid_lon + rng.uniform(-0.2, 0.2)
        # Unknown / other
        if baltic:
            return random_water_point(rng, scenario_bounds)
        return mid_lat + rng.uniform(-0.2, 0.2), mid_lon + rng.uniform(-0.2, 0.2)

    def _default_heading(
        self,
        domain: str,
        rng: random.Random,
        *,
        suspicious: bool,
        lat: float,
        lon: float,
        infrastructure: list[dict[str, Any]],
    ) -> float:
        if suspicious:
            target = self._nearest_infra(lat, lon, infrastructure)
            if target is not None:
                return _bearing(lat, lon, target[0], target[1])
        if domain == "air":
            return rng.choice([45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0])
        if domain == "surface":
            return rng.uniform(0, 359)
        return rng.uniform(0, 359)

    def _default_speed(self, domain: str, subtype: str, *, suspicious: bool, rng: random.Random) -> float:
        if domain == "air":
            if subtype == "commercial_airliner":
                return rng.uniform(380, 460)
            if subtype == "helicopter":
                return rng.uniform(60, 130)
            if subtype == "uav":
                return rng.uniform(40, 110)
            return rng.uniform(350, 600)
        if domain == "surface":
            if subtype in {"cargo", "tanker", "ferry", "fishing_vessel"}:
                return rng.uniform(6, 18)
            return rng.uniform(14, 28)
        if domain == "subsurface":
            return rng.uniform(2, 10) if suspicious else rng.uniform(1, 6)
        return rng.uniform(0, 10)

    def _default_altitude(self, subtype: str, *, suspicious: bool, rng: random.Random) -> float:
        if subtype == "commercial_airliner":
            return rng.uniform(24000, 36000)
        if subtype == "helicopter":
            return rng.uniform(800, 4000)
        if subtype == "uav":
            return rng.uniform(1500, 18000)
        return rng.uniform(12000, 28000)

    def _default_depth(self, *, suspicious: bool, rng: random.Random) -> float:
        return rng.uniform(20, 120) if suspicious else rng.uniform(60, 300)

    def _default_behavior_flags(self, domain: str, subtype: str, *, suspicious: bool) -> list[str]:
        flags: list[str] = []
        if suspicious:
            flags.append("suspicious_behavior")
        if domain == "air":
            flags.append("air_track")
        elif domain == "surface":
            flags.append("surface_track")
        elif domain == "subsurface":
            flags.append("subsurface_track")
            flags.append("intermittent_detection")
        if subtype == "commercial_airliner":
            flags.append("civilian_airway")
        if subtype in {"cargo", "tanker", "ferry", "fishing_vessel"}:
            flags.append("civilian_shipping")
        if subtype in {"warship", "patrol_ship", "fast_attack_craft"}:
            flags.append("military_surface")
        return flags

    def _air_route(
        self,
        lat: float,
        lon: float,
        bounds: dict[str, float],
        *,
        suspicious: bool,
        rng: random.Random,
    ) -> list[tuple[float, float]]:
        lat_min = bounds["lat_min"]
        lat_max = bounds["lat_max"]
        lon_min = bounds["lon_min"]
        lon_max = bounds["lon_max"]
        if suspicious:
            target = (_midpoint(bounds)[0], _midpoint(bounds)[1])
            return [(lat, lon), target]
        route = [
            (rng.uniform(lat_min, lat_max), lon_min),
            (rng.uniform(lat_min, lat_max), lon_max),
        ]
        if rng.random() < 0.5:
            route.reverse()
        return route

    def _surface_route(
        self,
        lat: float,
        lon: float,
        bounds: dict[str, float],
        *,
        suspicious: bool,
        infrastructure: list[dict[str, Any]],
        rng: random.Random,
    ) -> list[tuple[float, float]]:
        if suspicious:
            target = self._nearest_infra(lat, lon, infrastructure)
            if target is not None:
                return [(lat, lon), target]
        lat_min = bounds["lat_min"]
        lat_max = bounds["lat_max"]
        lon_min = bounds["lon_min"]
        lon_max = bounds["lon_max"]
        start = (rng.uniform(lat_min, lat_max), lon_min)
        end = (rng.uniform(lat_min, lat_max), lon_max)
        if rng.random() < 0.5:
            start, end = end, start
        return [start, end]

    def _nearest_infra(self, lat: float, lon: float, infrastructure: list[dict[str, Any]]) -> tuple[float, float] | None:
        best: tuple[float, float] | None = None
        best_d = float("inf")
        for infra in infrastructure:
            dlat = infra["lat"] - lat
            dlon = infra["lon"] - lon
            dist = dlat * dlat + dlon * dlon
            if dist < best_d:
                best_d = dist
                best = (infra["lat"], infra["lon"])
        return best

    def _subsurface_visibility(self, track: CombatTrack) -> float:
        base = 0.25 if track.track_quality == "low" else 0.45 if track.track_quality == "medium" else 0.6
        if track.suspicious:
            base -= 0.05
        return _clamp(base, 0.1, 0.75)

    def _advance_track(
        self,
        track: CombatTrack,
        tick: int,
        scenario_bounds: dict[str, float],
        infrastructure: list[dict[str, Any]],
    ) -> None:
        rng = track_rng(track, tick)
        if track.domain == "air":
            if track.waypoints:
                waypoint = track.waypoints[min(track.waypoint_index, len(track.waypoints) - 1)]
                track.heading = _bearing(track.lat, track.lon, waypoint[0], waypoint[1])
                if abs(track.lat - waypoint[0]) < 0.1 and abs(track.lon - waypoint[1]) < 0.1:
                    track.waypoint_index = min(track.waypoint_index + 1, len(track.waypoints) - 1)
            track.heading = (track.heading + rng.uniform(-6, 6)) % 360
            track.speed = _clamp(track.speed + rng.uniform(-8, 8), 35.0, 620.0)
            track.altitude_ft = _clamp((track.altitude_ft or 0.0) + rng.uniform(-600, 600), 500.0, 42000.0)
            if track.suspicious:
                target = self._nearest_infra(track.lat, track.lon, infrastructure)
                if target is not None:
                    track.heading = _bearing(track.lat, track.lon, target[0], target[1])
                    track.behavior_flags = self._append_flag(track.behavior_flags, "course_toward_infrastructure")
                    track.behavior_flags = self._append_flag(track.behavior_flags, "speed_anomaly")
                    track.speed = _clamp(track.speed - 5.0, 120.0, 620.0)
            track.lat, track.lon = _step(track.lat, track.lon, track.heading, track.speed)
        elif track.domain == "surface":
            if track.waypoints:
                waypoint = track.waypoints[min(track.waypoint_index, len(track.waypoints) - 1)]
                track.heading = _bearing(track.lat, track.lon, waypoint[0], waypoint[1])
                if abs(track.lat - waypoint[0]) < 0.08 and abs(track.lon - waypoint[1]) < 0.08:
                    if track.waypoint_index < len(track.waypoints) - 1:
                        track.waypoint_index += 1
            if track.suspicious and infrastructure:
                target = self._nearest_infra(track.lat, track.lon, infrastructure)
                if target is not None:
                    track.heading = _bearing(track.lat, track.lon, target[0], target[1])
                    track.behavior_flags = self._append_flag(track.behavior_flags, "course_toward_infrastructure")
            if track.suspicious:
                track.speed = _clamp(track.speed + rng.uniform(-1.5, 1.5), 0.5, 28.0)
            else:
                track.speed = _clamp(track.speed + rng.uniform(-0.8, 0.8), 0.0, 22.0)
            if track.speed < 1.5:
                track.behavior_flags = self._append_flag(track.behavior_flags, "loitering")
            track.lat, track.lon = _step(track.lat, track.lon, track.heading, track.speed)
        elif track.domain == "subsurface":
            track.heading = (track.heading + rng.uniform(-4, 4)) % 360
            track.speed = _clamp(track.speed + rng.uniform(-0.8, 0.8), 0.5, 12.0)
            if track.loiter_center:
                if track.suspicious:
                    track.behavior_flags = self._append_flag(track.behavior_flags, "signal_loss")
                    if rng.random() < 0.25:
                        track.behavior_flags = self._append_flag(track.behavior_flags, "reappearance")
            track.lat, track.lon = _step(track.lat, track.lon, track.heading, track.speed)
        else:
            track.heading = (track.heading + rng.uniform(-10, 10)) % 360
            track.speed = _clamp(track.speed + rng.uniform(-1, 1), 0.0, 12.0)
            track.lat, track.lon = _step(track.lat, track.lon, track.heading, track.speed)

        lat_min = scenario_bounds["lat_min"]
        lat_max = scenario_bounds["lat_max"]
        lon_min = scenario_bounds["lon_min"]
        lon_max = scenario_bounds["lon_max"]
        track.lat = _clamp(track.lat, lat_min, lat_max)
        track.lon = _clamp(track.lon, lon_min, lon_max)

        # Domain-aware geospatial validation for Baltic region
        baltic = (
            lat_max >= GEO_BALTIC_BOUNDS["lat_min"]
            and lat_min <= GEO_BALTIC_BOUNDS["lat_max"]
            and lon_max >= GEO_BALTIC_BOUNDS["lon_min"]
            and lon_min <= GEO_BALTIC_BOUNDS["lon_max"]
        )
        if baltic:
            if track.domain in ("surface", "subsurface") and is_on_land(track.lat, track.lon):
                snap = random_water_point(rng, scenario_bounds)
                track.lat, track.lon = snap
            elif track.domain == "ground" and is_at_sea(track.lat, track.lon):
                snap = random_land_point(rng, scenario_bounds)
                track.lat, track.lon = snap

        track.last_visible_tick = tick

    def _append_flag(self, flags: list[str], flag: str) -> list[str]:
        if flag not in flags:
            return [*flags, flag]
        return flags

    def _confidence(
        self,
        domain: str,
        sensor_source: str,
        track_quality: str,
        *,
        suspicious: bool,
        allegiance: str,
    ) -> float:
        base = {
            "AIS": 0.95,
            "radar": 0.82,
            "sonar": 0.72,
            "ESM": 0.68,
            "fused": 0.90,
        }.get(sensor_source, 0.8)
        quality_bonus = {"low": -0.12, "medium": 0.0, "high": 0.08}.get(track_quality, 0.0)
        allegiance_penalty = 0.05 if allegiance == "unknown" else 0.0
        domain_adjust = -0.08 if domain == "subsurface" else 0.0
        suspicious_bonus = 0.03 if suspicious else 0.0
        return round(_clamp(base + quality_bonus - allegiance_penalty + domain_adjust + suspicious_bonus, 0.3, 0.98), 2)

    def _track_to_contact(self, track: CombatTrack, timestamp: datetime, *, tick: int) -> Contact:
        attrs: dict[str, Any] = {
            "name": f"{track.subtype.replace('_', ' ').title()} {track.track_id}",
            "domain": track.domain,
            "subtype": track.subtype,
            "sensor_source": track.sensor_source,
            "track_quality": track.track_quality,
            "allegiance": track.allegiance,
            "altitude_ft": track.altitude_ft,
            "depth_m": track.depth_m,
            "behavior_flags": list(track.behavior_flags),
            "source_system": "combat_system",
            "combat_contact": True,
        }
        if track.suspicious:
            attrs["behavior_mode"] = "hostile_probe_infrastructure"
            attrs["intent"] = "probe"
            target = track.target_infra or track.loiter_center
            if target is not None:
                attrs["target_infra"] = f"{target[0]:.4f},{target[1]:.4f}"
        if track.domain == "surface" and track.subtype in {"cargo", "tanker", "ferry", "fishing_vessel"}:
            attrs["behavior_mode"] = "neutral_transit"
        if track.domain == "surface" and track.allegiance in {"friendly"}:
            attrs["behavior_mode"] = "friendly_patrol_monitor"
        if track.domain == "subsurface":
            attrs["behavior_mode"] = "hostile_loiter_then_divert" if track.suspicious else "neutral_transit"

        contact_type = {
            "air": ContactType.UAV,
            "surface": ContactType.VESSEL,
            "subsurface": ContactType.SUBMARINE,
            "unknown": ContactType.UNKNOWN,
        }.get(track.domain, ContactType.UNKNOWN)
        return Contact(
            contact_id=f"C-{track.track_id}-{tick:04d}",
            timestamp=timestamp,
            source="combat_system",
            contact_type=contact_type,
            lat=round(clamp_wgs84(track.lat, track.lon)[0], 4),
            lon=round(clamp_wgs84(track.lat, track.lon)[1], 4),
            speed=round(track.speed, 1),
            heading=round(track.heading % 360, 1),
            confidence=track.confidence,
            entity_id=track.entity_id(),
            is_hostile=track.allegiance == "hostile",
            attributes=attrs,
        )


def track_rng(track: CombatTrack, tick: int) -> random.Random:
    return random.Random(_stable_seed(track.rng_seed, tick, track.track_id))
