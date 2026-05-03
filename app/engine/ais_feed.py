from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from ..core.config import settings
from ..core.schemas import Contact, ContactType

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


@dataclass
class AISVisibleResult:
    contacts: list[dict[str, Any]]
    suspicious_contacts: list[Contact]
    source_summary: str
    cache_hit: bool
    provider_enabled: bool


class AISHubFeed:
    def __init__(self) -> None:
        self._cache: dict[tuple[float, float, float, float], tuple[float, AISVisibleResult]] = {}
        self._history: dict[str, list[dict[str, float]]] = defaultdict(list)

    def reset(self) -> None:
        self._cache.clear()
        self._history.clear()

    @property
    def enabled(self) -> bool:
        return settings.ais_enabled and bool(settings.ais_aishub_username.strip())

    def fetch_visible_contacts(
        self,
        *,
        latmin: float,
        latmax: float,
        lonmin: float,
        lonmax: float,
        infrastructure: list[dict[str, Any]] | None = None,
    ) -> AISVisibleResult:
        if not self.enabled:
            return AISVisibleResult(
                contacts=[],
                suspicious_contacts=[],
                source_summary="AIS disabled: set COA_AIS_AISHUB_USERNAME to enable the free AISHub feed.",
                cache_hit=False,
                provider_enabled=False,
            )

        cache_key = tuple(round(value, 2) for value in (latmin, latmax, lonmin, lonmax))
        cached = self._cache.get(cache_key)
        now = time.time()
        if cached and now - cached[0] < settings.ais_cache_seconds:
            return AISVisibleResult(
                contacts=cached[1].contacts,
                suspicious_contacts=cached[1].suspicious_contacts,
                source_summary=cached[1].source_summary,
                cache_hit=True,
                provider_enabled=True,
            )

        raw = self._request_aishub(latmin=latmin, latmax=latmax, lonmin=lonmin, lonmax=lonmax)
        contacts: list[dict[str, Any]] = []
        suspicious_contacts: list[Contact] = []

        for row in raw[: settings.ais_visible_limit]:
            normalized = self._normalize_row(row, infrastructure or [])
            contacts.append(normalized)
            if normalized["suspicion_score"] >= settings.ais_suspicion_min_score:
                suspicious_contacts.append(self._to_contact(normalized))

        result = AISVisibleResult(
            contacts=contacts,
            suspicious_contacts=suspicious_contacts,
            source_summary=(
                f"AISHub visible-area AIS feed. Cached for {settings.ais_cache_seconds}s and "
                f"constrained to records up to {settings.ais_max_position_age_min} minute(s) old."
            ),
            cache_hit=False,
            provider_enabled=True,
        )
        self._cache[cache_key] = (now, result)
        return result

    def _request_aishub(self, *, latmin: float, latmax: float, lonmin: float, lonmax: float) -> list[dict[str, Any]]:
        params = {
            "username": settings.ais_aishub_username,
            "format": 1,
            "output": "json",
            "compress": 0,
            "latmin": latmin,
            "latmax": latmax,
            "lonmin": lonmin,
            "lonmax": lonmax,
            "interval": settings.ais_max_position_age_min,
        }
        with httpx.Client(timeout=settings.ais_request_timeout_seconds) as client:
            response = client.get(settings.ais_aishub_base_url, params=params)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, list) or len(payload) < 2:
            return []
        return payload[1] if isinstance(payload[1], list) else []

    def _normalize_row(self, row: dict[str, Any], infrastructure: list[dict[str, Any]]) -> dict[str, Any]:
        mmsi = str(row.get("MMSI", "UNKNOWN"))
        lat = float(row.get("LATITUDE", 0.0))
        lon = float(row.get("LONGITUDE", 0.0))
        speed = float(row.get("SOG", 0.0) or 0.0)
        heading = float(row.get("HEADING", 0.0) or 0.0)
        timestamp = row.get("TIME")
        if isinstance(timestamp, str) and "GMT" in timestamp:
            parsed_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S GMT").replace(tzinfo=timezone.utc)
        else:
            parsed_time = datetime.now(timezone.utc)

        history = self._history[mmsi]
        history.append({"lat": lat, "lon": lon, "heading": heading, "speed": speed})
        if len(history) > 5:
            self._history[mmsi] = history[-5:]
            history = self._history[mmsi]

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
                if heading not in (0.0, 511.0) and _heading_delta(heading, bearing) <= settings.ais_heading_to_infra_deg:
                    suspicion_score += 0.20
                    suspicious_flags.append("Heading toward infrastructure")
                break

        if speed <= settings.ais_loiter_speed_kts and nearest_distance is not None and nearest_distance <= settings.ais_near_infra_km * 1.5:
            suspicion_score += 0.20
            suspicious_flags.append("Low-speed loitering")

        destination = str(row.get("DEST", "") or "").strip()
        if not destination:
            suspicion_score += 0.05
            suspicious_flags.append("No reported destination")

        if len(history) >= 2:
            prev = history[-2]
            move_km = _haversine(prev["lat"], prev["lon"], lat, lon)
            course_delta = _heading_delta(prev["heading"], heading)
            if move_km < 0.8 and speed <= settings.ais_loiter_speed_kts:
                suspicion_score += 0.15
                suspicious_flags.append("Persistent limited movement")
            if course_delta >= 45.0 and nearest_distance is not None and nearest_distance <= settings.ais_near_infra_km * 2:
                suspicion_score += 0.10
                suspicious_flags.append("Abrupt course change near infrastructure")

        suspicion_score = min(suspicion_score, 1.0)

        return {
            "mmsi": mmsi,
            "entity_id": f"AIS-{mmsi}",
            "name": str(row.get("NAME", "") or f"AIS {mmsi}"),
            "callsign": str(row.get("CALLSIGN", "") or ""),
            "imo": str(row.get("IMO", "") or ""),
            "lat": lat,
            "lon": lon,
            "speed": speed,
            "heading": 0.0 if heading == 511.0 else heading,
            "destination": destination,
            "nav_status": row.get("NAVSTAT"),
            "ship_type": row.get("TYPE"),
            "timestamp": parsed_time.isoformat(),
            "suspicion_score": round(suspicion_score, 3),
            "suspicious_flags": suspicious_flags,
            "nearest_infrastructure": nearest_name,
            "nearest_infrastructure_km": round(nearest_distance, 2) if nearest_distance is not None else None,
            "considered_in_analysis": suspicion_score >= settings.ais_suspicion_min_score,
        }

    def _to_contact(self, row: dict[str, Any]) -> Contact:
        attrs = {
            "name": row["name"],
            "allegiance": "neutral",
            "mmsi": row["mmsi"],
            "imo": row["imo"],
            "callsign": row["callsign"],
            "destination": row["destination"],
            "ship_type": row["ship_type"],
            "nav_status": row["nav_status"],
            "ais_live": True,
            "suspicion_score": row["suspicion_score"],
            "suspicious_flags": list(row["suspicious_flags"]),
            "nearest_infrastructure": row["nearest_infrastructure"],
            "nearest_infrastructure_km": row["nearest_infrastructure_km"],
            "suspicious_maneuver": True,
        }
        return Contact(
            contact_id=f"AIS-{row['mmsi']}-{int(datetime.now(timezone.utc).timestamp())}",
            timestamp=datetime.fromisoformat(row["timestamp"]),
            source="aishub",
            contact_type=ContactType.VESSEL,
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            speed=float(row["speed"]),
            heading=float(row["heading"]),
            confidence=0.74,
            entity_id=row["entity_id"],
            is_hostile=False,
            attributes=attrs,
        )


_service: AISHubFeed | None = None


def get_ais_feed() -> AISHubFeed:
    global _service
    if _service is None:
        _service = AISHubFeed()
    return _service
