from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..core.config import settings
from ..core.constants import SCENARIO_BOUNDS
from ..core.schemas import Contact, ContactType

DATA_DIR = Path(__file__).parent.parent / "data"
EARTH_RADIUS_KM = 6371.0


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


def _bearing_to(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlon = math.radians(lon2 - lon1)
    rlat1 = math.radians(lat1)
    rlat2 = math.radians(lat2)
    x = math.sin(dlon) * math.cos(rlat2)
    y = math.cos(rlat1) * math.sin(rlat2) - math.sin(rlat1) * math.cos(rlat2) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0


def _heading_delta(a: float, b: float) -> float:
    diff = abs((a - b) % 360.0)
    return min(diff, 360.0 - diff)


class NOAAReplayFeed:
    def __init__(self) -> None:
        self._datasets: dict[str, dict[str, Any]] = {}
        self._cursor: dict[str, int] = defaultdict(int)

    def reset(self) -> None:
        self._cursor.clear()

    def _load_dataset(self, scenario_id: str) -> dict[str, Any]:
        if scenario_id not in self._datasets:
            path = DATA_DIR / f"noaa_replay_{scenario_id}.json"
            if not path.exists():
                self._datasets[scenario_id] = {"scenario_id": scenario_id, "source": "", "tracks": []}
            else:
                self._datasets[scenario_id] = json.loads(path.read_text())
        return self._datasets[scenario_id]

    def visible_contacts(
        self,
        *,
        scenario_id: str,
        infrastructure: list[dict[str, Any]] | None = None,
        latmin: float | None = None,
        latmax: float | None = None,
        lonmin: float | None = None,
        lonmax: float | None = None,
        step: int = 1,
    ) -> dict[str, Any]:
        dataset = self._load_dataset(scenario_id)
        tracks = dataset.get("tracks", [])
        if not tracks:
            return {
                "contacts": [],
                "suspicious_contacts": [],
                "source_summary": "NOAA-derived replay dataset not available for this scenario.",
                "provider_enabled": False,
            }

        bounds = SCENARIO_BOUNDS.get(scenario_id)
        latmin = bounds["lat_min"] if latmin is None and bounds else latmin
        latmax = bounds["lat_max"] if latmax is None and bounds else latmax
        lonmin = bounds["lon_min"] if lonmin is None and bounds else lonmin
        lonmax = bounds["lon_max"] if lonmax is None and bounds else lonmax

        cursor = self._cursor[scenario_id]
        contacts: list[dict[str, Any]] = []
        suspicious_contacts: list[Contact] = []
        visible_points = 0

        for track in tracks:
            points = track.get("points", [])
            if not points:
                continue
            point = points[cursor % len(points)]
            lat = float(point["lat"])
            lon = float(point["lon"])
            if latmin is not None and lat < latmin:
                continue
            if latmax is not None and lat > latmax:
                continue
            if lonmin is not None and lon < lonmin:
                continue
            if lonmax is not None and lon > lonmax:
                continue
            normalized = self._normalize_point(track, point, infrastructure or [])
            contacts.append(normalized)
            visible_points += 1
            if normalized["suspicion_score"] >= settings.ais_suspicion_min_score:
                suspicious_contacts.append(self._to_contact(normalized))

        self._cursor[scenario_id] += max(step, 1)
        return {
            "contacts": contacts,
            "suspicious_contacts": suspicious_contacts,
            "source_summary": dataset.get("source") or "NOAA-derived replay dataset",
            "provider_enabled": True,
            "visible_points": visible_points,
        }

    def _normalize_point(self, track: dict[str, Any], point: dict[str, Any], infrastructure: list[dict[str, Any]]) -> dict[str, Any]:
        lat = float(point["lat"])
        lon = float(point["lon"])
        speed = float(point.get("speed", 0.0))
        heading = float(point.get("heading", 0.0))
        suspicion_score = 0.0
        suspicious_flags: list[str] = []
        nearest_name = None
        nearest_distance = None

        for infra in infrastructure:
            distance = _haversine(lat, lon, float(infra["lat"]), float(infra["lon"]))
            if nearest_distance is None or distance < nearest_distance:
                nearest_distance = distance
                nearest_name = str(infra.get("name", "critical infrastructure"))
            if distance <= settings.ais_near_infra_km:
                suspicion_score += 0.35
                suspicious_flags.append(f"Near {infra.get('name', 'critical infrastructure')}")
                bearing = _bearing_to(lat, lon, float(infra["lat"]), float(infra["lon"]))
                if _heading_delta(heading, bearing) <= settings.ais_heading_to_infra_deg:
                    suspicion_score += 0.20
                    suspicious_flags.append("Heading toward infrastructure")
                break

        if speed <= settings.ais_loiter_speed_kts and nearest_distance is not None and nearest_distance <= settings.ais_near_infra_km * 1.5:
            suspicion_score += 0.20
            suspicious_flags.append("Low-speed loitering")

        suspicion_score = min(suspicion_score, 1.0)
        return {
            "entity_id": track["entity_id"],
            "name": track["name"],
            "mmsi": track["mmsi"],
            "imo": track.get("imo", ""),
            "call_sign": track.get("call_sign", ""),
            "vessel_type": track.get("vessel_type", ""),
            "nav_status": track.get("status", ""),
            "lat": lat,
            "lon": lon,
            "speed": speed,
            "heading": heading,
            "timestamp": point["timestamp"],
            "destination": "",
            "suspicion_score": round(suspicion_score, 3),
            "suspicious_flags": suspicious_flags,
            "nearest_infrastructure": nearest_name,
            "nearest_infrastructure_km": round(nearest_distance, 2) if nearest_distance is not None else None,
            "considered_in_analysis": suspicion_score >= settings.ais_suspicion_min_score,
            "replay": True,
        }

    def _to_contact(self, row: dict[str, Any]) -> Contact:
        timestamp = row["timestamp"]
        try:
            parsed_time = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
        except ValueError:
            parsed_time = datetime.now(timezone.utc)
        return Contact(
            contact_id=f"{row['entity_id']}-{self._cursor.get(row['entity_id'], 0)}",
            timestamp=parsed_time,
            source="noaa_replay",
            contact_type=ContactType.VESSEL,
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            speed=float(row["speed"]),
            heading=float(row["heading"]),
            confidence=0.72,
            entity_id=row["entity_id"],
            is_hostile=False,
            attributes={
                "name": row["name"],
                "allegiance": "neutral",
                "noaa_replay": True,
                "mmsi": row["mmsi"],
                "imo": row["imo"],
                "call_sign": row["call_sign"],
                "ship_type": row["vessel_type"],
                "nav_status": row["nav_status"],
                "suspicion_score": row["suspicion_score"],
                "suspicious_flags": list(row["suspicious_flags"]),
                "nearest_infrastructure": row["nearest_infrastructure"],
                "nearest_infrastructure_km": row["nearest_infrastructure_km"],
                "suspicious_maneuver": True,
            },
        )


_feed: NOAAReplayFeed | None = None


def get_noaa_replay_feed() -> NOAAReplayFeed:
    global _feed
    if _feed is None:
        _feed = NOAAReplayFeed()
    return _feed
