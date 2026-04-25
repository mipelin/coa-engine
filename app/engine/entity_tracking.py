from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

from ..core.constants import EntityType
from ..core.schemas import OperationalEvent, TrackInfo

logger = logging.getLogger("coa_engine.engine.entity_tracking")

EARTH_RADIUS_KM = 6371.0


@dataclass
class Position:
    timestamp: object
    lat: float
    lon: float
    speed_knots: float | None
    heading: float | None


@dataclass
class EntityTrack:
    entity_id: str
    positions: list[Position] = field(default_factory=list)
    velocity_bearing: float | None = None
    velocity_speed: float | None = None

    def add_position(self, pos: Position) -> None:
        self.positions.append(pos)

    def compute_velocity(self) -> None:
        if len(self.positions) < 2:
            return
        p1 = self.positions[-2]
        p2 = self.positions[-1]
        dt_hours = (p2.timestamp - p1.timestamp).total_seconds() / 3600.0
        if dt_hours <= 0:
            return
        d = _haversine(p1.lat, p1.lon, p2.lat, p2.lon)
        self.velocity_speed = d / dt_hours / 1.852  # km/h to knots
        dlat = p2.lat - p1.lat
        dlon = p2.lon - p1.lon
        self.velocity_bearing = (math.degrees(math.atan2(dlon, dlat)) % 360)

    def total_distance_km(self) -> float:
        total = 0.0
        for i in range(1, len(self.positions)):
            total += _haversine(
                self.positions[i - 1].lat, self.positions[i - 1].lon,
                self.positions[i].lat, self.positions[i].lon,
            )
        return total

    def avg_speed_knots(self) -> float | None:
        speeds = [p.speed_knots for p in self.positions if p.speed_knots is not None]
        return sum(speeds) / len(speeds) if speeds else None

    def is_loitering(self, threshold_knots: float = 1.5, min_positions: int = 3) -> bool:
        speeds = [p.speed_knots for p in self.positions if p.speed_knots is not None]
        if len(speeds) < min_positions:
            return False
        low_speed_count = sum(1 for s in speeds if s <= threshold_knots)
        return low_speed_count >= len(speeds) * 0.5

    def to_track_info(self) -> TrackInfo:
        return TrackInfo(
            entity_id=self.entity_id,
            position_count=len(self.positions),
            total_distance_km=round(self.total_distance_km(), 2),
            avg_speed_knots=round(self.avg_speed_knots(), 1) if self.avg_speed_knots() else None,
            is_loitering=self.is_loitering(),
            velocity_bearing=round(self.velocity_bearing, 1) if self.velocity_bearing else None,
            velocity_speed=round(self.velocity_speed, 1) if self.velocity_speed else None,
        )


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


def build_tracks(events: list[OperationalEvent]) -> dict[str, TrackInfo]:
    """Construct tracks from events and return TrackInfo per entity."""
    tracks: dict[str, EntityTrack] = {}
    for event in sorted(events, key=lambda e: e.timestamp):
        if event.entity_id not in tracks:
            tracks[event.entity_id] = EntityTrack(entity_id=event.entity_id)
        track = tracks[event.entity_id]
        speed = event.attributes.get("speed_knots")
        heading = event.attributes.get("heading") or event.attributes.get("new_heading")
        track.add_position(Position(
            timestamp=event.timestamp,
            lat=event.lat,
            lon=event.lon,
            speed_knots=speed,
            heading=heading,
        ))
    for track in tracks.values():
        track.compute_velocity()

    result = {eid: track.to_track_info() for eid, track in tracks.items()}
    loitering = sum(1 for t in result.values() if t.is_loitering)
    logger.info("Built %d tracks, %d loitering entities", len(result), loitering)
    return result
