from __future__ import annotations

from collections import defaultdict

from ..core.config import settings
from ..core.constants import EntityType, EventType, ThreatLevel
from ..core.schemas import AnomalyResult, FeatureVector, OperationalEvent, ThreatResult

EXCLUDE_FROM_THREAT_RANKING = {
    EntityType.ALLIED_VESSEL,
    EntityType.ISR_ASSET,
    EntityType.SUBSEA_CABLE,
    EntityType.AIRPORT,
    EntityType.BORDER_CROSSING,
}

EVENT_TYPE_WEIGHTS: dict[str, float] = {
    EventType.CABLE_SEVERANCE: 0.15,
    EventType.JAMMING_DETECTED: 0.20,
    EventType.UAV_DETECTION: 0.18,
    EventType.CONVOY_SIGHTING: 0.12,
    EventType.VESSEL_COURSE_CHANGE: 0.10,
    EventType.SATELLITE_DETECTION: 0.08,
    EventType.SOCIAL_MEDIA_REPORT: 0.04,
    EventType.VESSEL_POSITION: 0.05,
    EventType.OPERATIONAL_REPORT: 0.03,
}


def _classify_threat(probability: float) -> ThreatLevel:
    if probability >= settings.threat_threshold_critical:
        return ThreatLevel.CRITICAL
    if probability >= settings.threat_threshold_high:
        return ThreatLevel.HIGH
    if probability >= settings.threat_threshold_medium:
        return ThreatLevel.MEDIUM
    return ThreatLevel.LOW


def assess_threats(
    events: list[OperationalEvent],
    features: list[FeatureVector],
    anomalies: list[AnomalyResult],
) -> list[ThreatResult]:
    """Aggregate anomaly scores by entity and produce one ThreatResult per relevant entity."""
    entity_anomalies: dict[str, list[AnomalyResult]] = defaultdict(list)
    for a in anomalies:
        entity_anomalies[a.entity_id].append(a)

    entity_features: dict[str, list[FeatureVector]] = defaultdict(list)
    for f in features:
        entity_features[f.entity_id].append(f)

    entity_events: dict[str, list[OperationalEvent]] = defaultdict(list)
    for e in events:
        entity_events[e.entity_id].append(e)

    has_cable_severance = any(e.event_type == EventType.CABLE_SEVERANCE for e in events)

    results: list[ThreatResult] = []

    for entity_id in entity_anomalies:
        ent_events = entity_events.get(entity_id, [])
        if not ent_events:
            continue
        primary_type = ent_events[0].entity_type

        if primary_type in EXCLUDE_FROM_THREAT_RANKING:
            continue

        anom_list = entity_anomalies[entity_id]
        max_anom_score = max(a.anomaly_score for a in anom_list) / 100.0
        avg_anom_score = sum(a.anomaly_score for a in anom_list) / len(anom_list) / 100.0

        event_type_boost = sum(
            EVENT_TYPE_WEIGHTS.get(e.event_type, 0.0) for e in ent_events
        )

        feats = entity_features.get(entity_id, [])
        avg_heading = (
            sum(f.heading_towards_critical_asset for f in feats) / len(feats)
            if feats else 0.0
        )
        avg_jamming = (
            sum(f.jamming_nearby for f in feats) / len(feats)
            if feats else 0.0
        )
        avg_convoy = (
            sum(f.convoy_activity_nearby for f in feats) / len(feats)
            if feats else 0.0
        )

        probability = (
            max_anom_score * 0.40
            + avg_anom_score * 0.15
            + min(event_type_boost, 0.30) * 0.30
            + avg_heading * 0.08
            + avg_jamming * 0.07
        )

        if has_cable_severance and primary_type == EntityType.SUSPICIOUS_VESSEL:
            min_dist = min(
                (f.distance_to_nearest_critical_infrastructure for f in feats), default=999.0
            )
            if min_dist < 10.0:
                probability += 0.10

        if primary_type == EntityType.UAV:
            probability += 0.05 * avg_heading

        probability += avg_convoy * 0.05
        probability = min(max(probability, 0.0), 1.0)

        level = _classify_threat(probability)

        source_confs = [e.confidence for e in ent_events]
        avg_confidence = sum(source_confs) / len(source_confs)
        n_sources = len(set(e.source for e in ent_events))
        correlation_bonus = min(n_sources / 4.0, 0.15)
        confidence = min(avg_confidence + correlation_bonus, 1.0)

        drivers: list[str] = []
        if max_anom_score > 0.6:
            drivers.append("High anomaly score on one or more events")
        if event_type_boost > 0.15:
            drivers.append("Event types associated with elevated threat indicators")
        if avg_heading > 0.3:
            drivers.append("Heading toward critical infrastructure")
        if avg_jamming > 0.3:
            drivers.append("Correlated with jamming activity")
        if has_cable_severance and primary_type == EntityType.SUSPICIOUS_VESSEL:
            drivers.append("Context: confirmed cable severance in scenario area")
        if avg_convoy > 0.3:
            drivers.append("Correlated with convoy activity")
        if n_sources >= 3:
            drivers.append(f"Confirmed by {n_sources} independent sources")
        if not drivers:
            drivers.append("No strong threat indicators identified")

        results.append(ThreatResult(
            entity_id=entity_id,
            threat_probability=round(probability, 3),
            threat_level=level,
            confidence=round(confidence, 3),
            main_drivers=drivers,
        ))

    results.sort(key=lambda r: r.threat_probability, reverse=True)
    return results
