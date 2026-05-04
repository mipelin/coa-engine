"""Deterministic proximity-based contact correlation.

Produces fused tracks from multi-source observations using fixed-threshold
spatiotemporal clustering. This is NOT sensor-level data fusion with
uncertainty propagation — it correlates contact reports within an 8 km / 45 min
window based on kinematic compatibility.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import math
from typing import Any

from ..core.constants import EntityType, EventType
from ..core.schemas import AnomalyResult, Contact, FeatureVector, OperationalEvent, ThreatResult
from .isr_simulation import BaseObservation
from .feature_engineering import haversine_km

FUSION_RADIUS_KM = 8.0
FUSION_TIME_WINDOW_MIN = 45.0
FUSION_HEADING_DELTA_DEG = 35.0
FUSION_SPEED_DELTA_KTS = 8.0

SOURCE_RELIABILITY = {
    "ais": 0.55,
    "aishub": 0.55,
    "noaa_replay": 0.58,
    "combat_system": 0.82,
    "radar": 0.8,
    "sonar": 0.82,
    "esm": 0.84,
    "sigint": 0.86,
    "jamming": 0.88,
    "satellite": 0.72,
    "social": 0.42,
    "social_media": 0.42,
    "osint": 0.45,
    "manual": 0.75,
    "manual_injection": 0.75,
    "simulation": 0.68,
    "fused": 0.78,
}


@dataclass
class FusedTrack:
    track_id: str
    primary_entity_id: str
    correlated_entities: list[str]
    track_type: str
    allegiance: str
    fused_confidence: float
    source_count: int
    sources: list[str]
    last_seen: datetime
    position: dict[str, float]
    heading: float | None
    speed: float | None
    anomaly_support: float
    threat_support: float
    rationale: str
    provenance: str = "synthetic multi-source observations with deterministic fusion"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FusedTrack":
        return cls(**data)


@dataclass
class _Observation:
    observation_id: str
    entity_id: str
    lat: float
    lon: float
    timestamp: datetime
    source: str
    confidence: float
    track_type: str
    subtype: str
    heading: float | None = None
    speed: float | None = None
    allegiance: str = "unknown"
    behavior_flags: list[str] = field(default_factory=list)


@dataclass
class _FusionCluster:
    observations: list[_Observation] = field(default_factory=list)

    def add(self, observation: _Observation) -> None:
        self.observations.append(observation)


def serialize_fused_tracks(tracks: list[FusedTrack]) -> list[dict[str, Any]]:
    return [track.to_dict() for track in tracks]


def build_fused_tracks(
    *,
    events: list[OperationalEvent],
    contacts: list[Contact] | None = None,
    observations: list[BaseObservation] | None = None,
    anomalies: list[AnomalyResult] | None = None,
    threats: list[ThreatResult] | None = None,
    features: list[FeatureVector] | None = None,
) -> list[FusedTrack]:
    observations = _normalize_observations(events, contacts or [], observations or [])
    clusters: list[_FusionCluster] = []
    for observation in observations:
        cluster = _best_cluster_match(observation, clusters)
        if cluster is None:
            cluster = _FusionCluster()
            clusters.append(cluster)
        cluster.add(observation)

    anomaly_by_entity = _aggregate_anomaly_support(anomalies or [])
    threat_by_entity = _aggregate_threat_support(threats or [])
    feature_by_entity = _group_features(features or [])

    fused_tracks: list[FusedTrack] = []
    for index, cluster in enumerate(clusters, start=1):
        fused_tracks.append(
            _build_track(
                cluster=cluster,
                index=index,
                anomaly_by_entity=anomaly_by_entity,
                threat_by_entity=threat_by_entity,
                feature_by_entity=feature_by_entity,
            )
        )

    fused_tracks.sort(
        key=lambda track: (
            track.primary_entity_id,
            -track.fused_confidence,
            -track.source_count,
            track.track_id,
        )
    )
    return fused_tracks


def _normalize_observations(
    events: list[OperationalEvent],
    contacts: list[Contact],
    simulated_observations: list[BaseObservation],
) -> list[_Observation]:
    observations: list[_Observation] = []
    for event in events:
        observations.append(_observation_from_event(event))
    for contact in contacts:
        observations.append(_observation_from_contact(contact))
    for observation in simulated_observations:
        observations.append(_observation_from_isr(observation))
    observations.sort(
        key=lambda item: (
            item.timestamp,
            item.entity_id,
            item.source,
            item.observation_id,
        )
    )
    return observations


def _observation_from_event(event: OperationalEvent) -> _Observation:
    attrs = event.attributes or {}
    source = str(event.source or "unknown")
    track_type = _normalize_track_type(
        entity_type=event.entity_type.value,
        event_type=event.event_type.value,
        subtype=str(attrs.get("subtype", "")),
    )
    behavior_flags = []
    if attrs.get("behavior_mode"):
        behavior_flags.append(str(attrs["behavior_mode"]))
    if event.event_type == EventType.JAMMING_DETECTED:
        behavior_flags.append("jamming")
    if event.event_type == EventType.SOCIAL_MEDIA_REPORT:
        behavior_flags.append("osint")
    return _Observation(
        observation_id=event.event_id,
        entity_id=event.entity_id,
        lat=event.lat,
        lon=event.lon,
        timestamp=event.timestamp,
        source=source,
        confidence=event.confidence,
        track_type=track_type,
        subtype=str(attrs.get("subtype", "")),
        heading=_event_heading(attrs),
        speed=_to_float(attrs.get("speed_knots")),
        allegiance=(event.allegiance or "unknown").lower() or "unknown",
        behavior_flags=behavior_flags,
    )


def _observation_from_contact(contact: Contact) -> _Observation:
    attrs = contact.attributes or {}
    source = str(contact.source or "unknown")
    return _Observation(
        observation_id=contact.contact_id,
        entity_id=contact.entity_id,
        lat=contact.lat,
        lon=contact.lon,
        timestamp=contact.timestamp,
        source=source,
        confidence=contact.confidence,
        track_type=_normalize_track_type(
            entity_type=contact.contact_type.value,
            event_type="",
            subtype=str(attrs.get("subtype", "")),
        ),
        subtype=str(attrs.get("subtype", "")),
        heading=contact.heading,
        speed=contact.speed,
        allegiance=str(attrs.get("allegiance", "unknown")).lower() or "unknown",
        behavior_flags=_contact_behavior_flags(contact),
    )


def _observation_from_isr(observation: BaseObservation) -> _Observation:
    attrs = observation.attributes or {}
    source = {
        "AIS": "ais",
        "CMS": "combat_system",
        "SAT": "satellite",
        "OSINT": "osint",
        "ESM": "esm",
    }.get(str(observation.source_type).upper(), str(observation.source_type).lower())
    track_type = str(observation.entity_type or "unknown").lower()
    if track_type == "uav":
        track_type = "uav"
    return _Observation(
        observation_id=observation.id,
        entity_id=str(attrs.get("entity_id", observation.id)),
        lat=observation.position.lat,
        lon=observation.position.lon,
        timestamp=observation.timestamp,
        source=source,
        confidence=observation.confidence,
        track_type=_normalize_track_type(
            entity_type=track_type,
            event_type="",
            subtype=str(attrs.get("subtype", track_type)),
        ),
        subtype=str(attrs.get("subtype", track_type)),
        heading=observation.kinematics.heading,
        speed=observation.kinematics.speed,
        allegiance=str(attrs.get("allegiance", "unknown")).lower() or "unknown",
        behavior_flags=list(attrs.get("behavior_flags", [])),
    )


def _best_cluster_match(
    observation: _Observation,
    clusters: list[_FusionCluster],
) -> _FusionCluster | None:
    best: tuple[float, _FusionCluster] | None = None
    for cluster in clusters:
        score = _match_score(observation, cluster)
        if score <= 0:
            continue
        if best is None or score > best[0]:
            best = (score, cluster)
    return best[1] if best else None


def _match_score(observation: _Observation, cluster: _FusionCluster) -> float:
    if not cluster.observations:
        return 0.0

    entity_ids = {item.entity_id for item in cluster.observations}
    if observation.entity_id in entity_ids:
        return 100.0

    representative = cluster.observations[-1]
    if not _types_compatible(observation.track_type, representative.track_type):
        return 0.0

    time_delta_min = abs((observation.timestamp - representative.timestamp).total_seconds()) / 60.0
    if time_delta_min > FUSION_TIME_WINDOW_MIN:
        return 0.0

    distance_km = haversine_km(observation.lat, observation.lon, representative.lat, representative.lon)
    if distance_km > FUSION_RADIUS_KM:
        return 0.0

    score = 40.0
    score += max(0.0, 25.0 * (1.0 - (distance_km / FUSION_RADIUS_KM)))
    score += max(0.0, 10.0 * (1.0 - (time_delta_min / FUSION_TIME_WINDOW_MIN)))

    heading_delta = _heading_delta(observation.heading, representative.heading)
    if heading_delta is not None:
        if heading_delta > FUSION_HEADING_DELTA_DEG:
            return 0.0
        score += max(0.0, 10.0 * (1.0 - (heading_delta / FUSION_HEADING_DELTA_DEG)))

    speed_delta = _speed_delta(observation.speed, representative.speed)
    if speed_delta is not None:
        if speed_delta > FUSION_SPEED_DELTA_KTS:
            return 0.0
        score += max(0.0, 10.0 * (1.0 - (speed_delta / FUSION_SPEED_DELTA_KTS)))

    return score


def _build_track(
    *,
    cluster: _FusionCluster,
    index: int,
    anomaly_by_entity: dict[str, float],
    threat_by_entity: dict[str, float],
    feature_by_entity: dict[str, list[FeatureVector]],
) -> FusedTrack:
    observations = sorted(
        cluster.observations,
        key=lambda item: (item.timestamp, item.entity_id, item.source, item.observation_id),
    )
    correlated_entities = sorted({item.entity_id for item in observations})
    primary_entity_id = _primary_entity_id(observations)
    track_type = _majority_type(observations)
    allegiance = _resolve_allegiance(observations)
    sources = sorted({item.source for item in observations})
    source_count = len(sources)
    last_seen = max(item.timestamp for item in observations)
    anomaly_support = max((anomaly_by_entity.get(entity_id, 0.0) for entity_id in correlated_entities), default=0.0)
    threat_support = max((threat_by_entity.get(entity_id, 0.0) for entity_id in correlated_entities), default=0.0)

    weighted_position = _weighted_position(observations)
    weighted_heading = _weighted_average(
        [(item.heading, _observation_weight(item)) for item in observations if item.heading is not None]
    )
    weighted_speed = _weighted_average(
        [(item.speed, _observation_weight(item)) for item in observations if item.speed is not None]
    )

    fused_confidence = _fused_confidence(
        observations=observations,
        source_count=source_count,
        anomaly_support=anomaly_support,
        threat_support=threat_support,
    )
    rationale = _rationale(
        primary_entity_id=primary_entity_id,
        track_type=track_type,
        sources=sources,
        source_count=source_count,
        anomaly_support=anomaly_support,
        threat_support=threat_support,
        correlated_entities=correlated_entities,
        feature_by_entity=feature_by_entity,
    )
    suffix = "-".join(correlated_entities[:2])
    track_id = f"FUSED-{index:03d}-{suffix}"

    return FusedTrack(
        track_id=track_id,
        primary_entity_id=primary_entity_id,
        correlated_entities=correlated_entities,
        track_type=track_type,
        allegiance=allegiance,
        fused_confidence=round(fused_confidence, 3),
        source_count=source_count,
        sources=sources,
        last_seen=last_seen,
        position={"lat": round(weighted_position[0], 5), "lon": round(weighted_position[1], 5)},
        heading=round(weighted_heading, 1) if weighted_heading is not None else None,
        speed=round(weighted_speed, 1) if weighted_speed is not None else None,
        anomaly_support=round(anomaly_support, 3),
        threat_support=round(threat_support, 3),
        rationale=rationale,
    )


def _aggregate_anomaly_support(anomalies: list[AnomalyResult]) -> dict[str, float]:
    grouped: dict[str, float] = {}
    for anomaly in anomalies:
        grouped[anomaly.entity_id] = max(grouped.get(anomaly.entity_id, 0.0), anomaly.anomaly_score / 100.0)
    return grouped


def _aggregate_threat_support(threats: list[ThreatResult]) -> dict[str, float]:
    return {threat.entity_id: threat.threat_probability for threat in threats}


def _group_features(features: list[FeatureVector]) -> dict[str, list[FeatureVector]]:
    grouped: dict[str, list[FeatureVector]] = {}
    for feature in features:
        grouped.setdefault(feature.entity_id, []).append(feature)
    return grouped


def _fused_confidence(
    *,
    observations: list[_Observation],
    source_count: int,
    anomaly_support: float,
    threat_support: float,
) -> float:
    weighted_conf = _weighted_average(
        [(item.confidence, _source_reliability(item.source)) for item in observations]
    )
    base = weighted_conf if weighted_conf is not None else 0.5
    base += min(max(source_count - 1, 0) * 0.08, 0.2)
    if any("jamming" in flag for item in observations for flag in item.behavior_flags):
        base += 0.08
    if any("hostile_probe_infrastructure" in flag for item in observations for flag in item.behavior_flags):
        base += 0.06
    base += min(anomaly_support * 0.12, 0.12)
    base += min(threat_support * 0.08, 0.08)
    return min(base, 1.0)


def _rationale(
    *,
    primary_entity_id: str,
    track_type: str,
    sources: list[str],
    source_count: int,
    anomaly_support: float,
    threat_support: float,
    correlated_entities: list[str],
    feature_by_entity: dict[str, list[FeatureVector]],
) -> str:
    clauses = [
        f"Track {primary_entity_id} is supported by {', '.join(sources)}",
    ]
    if len(correlated_entities) > 1:
        clauses.append(f"correlating entities {', '.join(correlated_entities)}")
    if source_count >= 2:
        clauses.append(f"across {source_count} independent sources")
    if anomaly_support >= 0.5:
        clauses.append("with elevated anomaly support")
    if threat_support >= 0.5:
        clauses.append("and threat-supporting indicators")
    nearest = min(
        (
            feature.distance_to_nearest_critical_infrastructure
            for entity_id in correlated_entities
            for feature in feature_by_entity.get(entity_id, [])
        ),
        default=None,
    )
    if nearest is not None and nearest < 20.0:
        clauses.append(f"near critical infrastructure ({nearest:.1f} km)")
    return f"{' '.join(clauses)} for a fused {track_type} track."


def _primary_entity_id(observations: list[_Observation]) -> str:
    counts: dict[str, int] = {}
    confidence: dict[str, float] = {}
    for observation in observations:
        counts[observation.entity_id] = counts.get(observation.entity_id, 0) + 1
        confidence[observation.entity_id] = max(
            confidence.get(observation.entity_id, 0.0),
            observation.confidence,
        )
    ranked = sorted(
        counts.keys(),
        key=lambda entity_id: (-counts[entity_id], -confidence[entity_id], entity_id),
    )
    return ranked[0]


def _majority_type(observations: list[_Observation]) -> str:
    grouped: dict[str, float] = {}
    for observation in observations:
        grouped[observation.track_type] = grouped.get(observation.track_type, 0.0) + _observation_weight(observation)
    return sorted(grouped.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _resolve_allegiance(observations: list[_Observation]) -> str:
    precedence = {"hostile": 4, "red": 4, "friendly": 3, "blue": 3, "neutral": 2, "unknown": 1}
    best = "unknown"
    best_score = 0
    for observation in observations:
        allegiance = observation.allegiance or "unknown"
        score = precedence.get(allegiance, 1)
        if score > best_score:
            best = allegiance
            best_score = score
    return best


def _weighted_position(observations: list[_Observation]) -> tuple[float, float]:
    lat_pairs = [(item.lat, _observation_weight(item)) for item in observations]
    lon_pairs = [(item.lon, _observation_weight(item)) for item in observations]
    lat = _weighted_average(lat_pairs) or observations[-1].lat
    lon = _weighted_average(lon_pairs) or observations[-1].lon
    return lat, lon


def _weighted_average(pairs: list[tuple[float | None, float]]) -> float | None:
    valid = [(value, weight) for value, weight in pairs if value is not None and weight > 0]
    if not valid:
        return None
    total_weight = sum(weight for _, weight in valid)
    if total_weight <= 0:
        return None
    return sum(value * weight for value, weight in valid) / total_weight


def _observation_weight(observation: _Observation) -> float:
    return max(observation.confidence * _source_reliability(observation.source), 0.01)


def _source_reliability(source: str) -> float:
    normalized = source.lower()
    for key, value in SOURCE_RELIABILITY.items():
        if key in normalized:
            return value
    return 0.6


def _types_compatible(left: str, right: str) -> bool:
    if left == right:
        return True
    if {left, right} <= {"vessel", "surface", "unknown"}:
        return True
    if {left, right} <= {"uav", "aircraft", "unknown"}:
        return True
    return "unknown" in {left, right}


def _normalize_track_type(*, entity_type: str, event_type: str, subtype: str) -> str:
    subtype_lower = subtype.lower()
    if subtype_lower == "submarine":
        return "submarine"
    if subtype_lower in {"uav", "drone"}:
        return "uav"
    if subtype_lower in {"jet", "helicopter", "commercial"}:
        return "aircraft"
    if entity_type in {EntityType.UAV.value, "uav"}:
        return "uav"
    if entity_type in {EntityType.CONVOY.value, EntityType.SUSPICIOUS_VESSEL.value, EntityType.ALLIED_VESSEL.value, EntityType.NEUTRAL_VESSEL.value, "vessel"}:
        return "vessel"
    if entity_type in {"submarine"} or event_type == EventType.SUBMARINE_DETECTION.value:
        return "submarine"
    if event_type in {EventType.UAV_DETECTION.value, EventType.SATELLITE_DETECTION.value}:
        return "aircraft"
    if entity_type == EntityType.INFRASTRUCTURE.value:
        return "ground"
    return "unknown"


def _event_heading(attrs: dict[str, Any]) -> float | None:
    return _to_float(attrs.get("new_heading") if attrs.get("new_heading") is not None else attrs.get("heading"))


def _contact_behavior_flags(contact: Contact) -> list[str]:
    attrs = contact.attributes or {}
    flags: list[str] = []
    if attrs.get("heading_toward_infra"):
        flags.append("heading_toward_infrastructure")
    if attrs.get("is_loitering"):
        flags.append("loitering")
    if attrs.get("signal_loss") or attrs.get("reappeared"):
        flags.append("signal_irregularity")
    if "jamming" in contact.contact_type.value:
        flags.append("jamming")
    return flags


def _heading_delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    diff = abs(left - right) % 360
    if diff > 180:
        diff = 360 - diff
    return diff


def _speed_delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return abs(left - right)


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
