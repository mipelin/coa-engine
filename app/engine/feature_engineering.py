from __future__ import annotations

import math
from collections import Counter, defaultdict

from ..core.constants import CRITICAL_INFRASTRUCTURE, EntityType, EventType
from ..core.schemas import FeatureVector, OperationalEvent

EARTH_RADIUS_KM = 6371.0
DEFAULT_TIME_SINCE_SEVERANCE = 9999.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in km between two points."""
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


def _distance_to_nearest_infra(event: OperationalEvent) -> tuple[float, float]:
    """Return (nearest distance km, second-cable distance km)."""
    cable_dists = []
    min_dist = float("inf")
    for infra in CRITICAL_INFRASTRUCTURE:
        d = haversine_km(event.lat, event.lon, infra["lat"], infra["lon"])
        if d < min_dist:
            min_dist = d
        if infra["type"] == "subsea_cable":
            cable_dists.append(d)
    second_cable = sorted(cable_dists)[1] if len(cable_dists) >= 2 else min_dist
    return min_dist, second_cable


def _course_change_count(event: OperationalEvent, entity_course_changes: dict[str, int]) -> int:
    return entity_course_changes.get(event.entity_id, 0)


def _speed_anomaly_score(event: OperationalEvent) -> float:
    speed = event.attributes.get("speed_knots")
    if speed is None:
        return 0.0
    if event.entity_type == EntityType.SUSPICIOUS_VESSEL:
        if speed <= 1.5:
            return min(1.0, 0.6 + 0.4 * (1.5 - speed) / 1.5)
        if speed <= 3.0:
            return 0.5
        if speed >= 12.0:
            return 0.3
        return 0.1
    return 0.0


def _heading_towards_critical_asset(event: OperationalEvent) -> float:
    heading = event.attributes.get("new_heading") or event.attributes.get("heading")
    if heading is None:
        return 0.0
    min_score = 0.0
    for infra in CRITICAL_INFRASTRUCTURE:
        dlat = infra["lat"] - event.lat
        dlon = infra["lon"] - event.lon
        bearing = math.degrees(math.atan2(dlon, dlat)) % 360
        diff = abs(bearing - heading)
        if diff > 180:
            diff = 360 - diff
        if diff < 30:
            score = 1.0 - diff / 30.0
            if score > min_score:
                min_score = score
    return min_score


def compute_features(events: list[OperationalEvent]) -> list[FeatureVector]:
    """Compute a FeatureVector for every event in the list."""
    if not events:
        return []

    sorted_events = sorted(events, key=lambda e: e.timestamp)

    entity_course_changes: dict[str, int] = Counter(
        e.entity_id for e in sorted_events if e.event_type == EventType.VESSEL_COURSE_CHANGE
    )

    entity_sources: dict[str, set[str]] = defaultdict(set)
    for e in sorted_events:
        entity_sources[e.entity_id].add(e.source)

    entity_event_count: dict[str, int] = Counter(e.entity_id for e in sorted_events)

    first_severance = None
    for e in sorted_events:
        if e.event_type == EventType.CABLE_SEVERANCE:
            first_severance = e.timestamp
            break

    jamming_positions = [
        (e.lat, e.lon, e.attributes.get("radius_nm", 20))
        for e in sorted_events
        if e.event_type == EventType.JAMMING_DETECTED
    ]

    has_convoy = any(e.event_type == EventType.CONVOY_SIGHTING for e in sorted_events)
    convoy_positions = [
        (e.lat, e.lon)
        for e in sorted_events
        if e.event_type == EventType.CONVOY_SIGHTING
    ]

    total_entities = max(len(set(e.entity_id for e in sorted_events)), 1)

    features: list[FeatureVector] = []
    for event in sorted_events:
        dist_nearest, dist_second_cable = _distance_to_nearest_infra(event)

        proximity_incident = 1.0 / (1.0 + dist_nearest)

        unique_sources = entity_sources[event.entity_id]
        multi_source = min(len(unique_sources) / 4.0, 1.0)

        count = entity_event_count[event.entity_id]
        density = min(count / max(len(sorted_events) / total_entities, 1), 1.0)

        jamming_score = 0.0
        for jlat, jlon, jradius_nm in jamming_positions:
            d = haversine_km(event.lat, event.lon, jlat, jlon)
            radius_km = jradius_nm * 1.852
            if d < radius_km:
                jamming_score = max(jamming_score, 1.0 - d / radius_km)

        convoy_score = 0.0
        if has_convoy:
            for clat, clon in convoy_positions:
                d = haversine_km(event.lat, event.lon, clat, clon)
                if d < 300:
                    convoy_score = max(convoy_score, 1.0 - d / 300.0)

        if first_severance is not None:
            delta = (event.timestamp - first_severance).total_seconds() / 60.0
            time_since = max(delta, 0.0)
        else:
            time_since = DEFAULT_TIME_SINCE_SEVERANCE

        heading_score = _heading_towards_critical_asset(event)

        features.append(FeatureVector(
            event_id=event.event_id,
            entity_id=event.entity_id,
            distance_to_nearest_critical_infrastructure=round(dist_nearest, 2),
            distance_to_second_cable=round(dist_second_cable, 2),
            course_change_count=_course_change_count(event, entity_course_changes),
            speed_anomaly_score=round(_speed_anomaly_score(event), 3),
            proximity_to_recent_incident=round(proximity_incident, 3),
            multi_source_correlation_score=round(multi_source, 3),
            event_density_score=round(density, 3),
            source_confidence_weight=event.confidence,
            jamming_nearby=round(jamming_score, 3),
            convoy_activity_nearby=round(convoy_score, 3),
            time_since_cable_severance=round(time_since, 1),
            heading_towards_critical_asset=round(heading_score, 3),
        ))

    return features
