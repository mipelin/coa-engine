from __future__ import annotations

import logging
from collections import defaultdict

from ..core.config import settings
from ..core.constants import BEHAVIOR_WEIGHTS, EntityType, EventType, ThreatLevel
from ..core.schemas import AnomalyResult, FeatureVector, OperationalEvent, ThreatResult
from .behavior_features import BehaviorFeatures, extract_behavior_features
from .fusion import FusedTrack

logger = logging.getLogger("coa_engine.engine.threat_assessment")

EXCLUDE_FROM_THREAT_RANKING = {
    EntityType.ALLIED_VESSEL,
    EntityType.ISR_ASSET,
    EntityType.INFRASTRUCTURE,
    EntityType.NEUTRAL_VESSEL,
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
    fused_tracks: list[FusedTrack] | None = None,
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

    entity_behavior = extract_behavior_features(events)
    fused_by_entity: dict[str, FusedTrack] = {}
    for track in fused_tracks or []:
        for entity_id in track.correlated_entities:
            fused_by_entity.setdefault(entity_id, track)

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
            max_anom_score * settings.threat_weight_max_anomaly
            + avg_anom_score * settings.threat_weight_avg_anomaly
            + min(event_type_boost, 0.30) * settings.threat_weight_event_type_boost
            + avg_heading * settings.threat_weight_heading
            + avg_jamming * settings.threat_weight_jamming
        )

        if has_cable_severance and primary_type == EntityType.SUSPICIOUS_VESSEL:
            min_dist = min(
                (f.distance_to_nearest_critical_infrastructure for f in feats), default=999.0
            )
            if min_dist < 10.0:
                probability += settings.threat_cable_severance_vessel_boost

        # Hostile electronic warfare: entities that ARE jamming sources get a direct boost
        has_jamming_event = any(e.event_type == EventType.JAMMING_DETECTED for e in ent_events)
        if has_jamming_event:
            probability += settings.threat_jamming_entity_boost

        if primary_type == EntityType.UAV:
            probability += settings.threat_uav_heading_boost * avg_heading

        probability += avg_convoy * settings.threat_weight_convoy

        # Allied deterrence: nearby friendly forces reduce threat
        avg_allied = (
            sum(f.allied_proximity_score for f in feats) / len(feats)
            if feats else 0.0
        )
        if avg_allied > 0.1:
            probability -= avg_allied * settings.allied_deterrence_factor

        # Note: final clamp and level classification is after behavior-intent modifiers

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
        if has_jamming_event:
            drivers.append("Confirmed jamming activity in area")
        if avg_allied > 0.3:
            drivers.append(f"Allied deterrence effect (proximity score: {avg_allied:.0%})")

        fused = fused_by_entity.get(entity_id)
        if fused is not None:
            probability += min(max(fused.source_count - 1, 0) * 0.02, 0.06)
            if fused.fused_confidence > 0.7:
                probability += min((fused.fused_confidence - 0.7) * 0.2, 0.06)
            confidence = min(max(confidence, fused.fused_confidence) + min(max(fused.source_count - 1, 0) * 0.02, 0.08), 1.0)
            if fused.source_count >= 2:
                drivers.append(f"Correlated across {fused.source_count} independent sources")
            if "sigint" in " ".join(fused.sources) or "jamming" in " ".join(fused.sources):
                drivers.append("Electronic or signals indicators corroborate the track")
            if fused.anomaly_support >= 0.6:
                drivers.append("Fused track aligns with elevated anomaly indicators")

        # Behavior-intent boosts (driven by BEHAVIOR_WEIGHTS config)
        bf = entity_behavior.get(entity_id, BehaviorFeatures())

        for mode in bf.behavior_modes:
            if mode not in BEHAVIOR_WEIGHTS:
                continue
            bw = BEHAVIOR_WEIGHTS[mode]

            # Additive threat boost
            if "threat_add" in bw:
                required_intent = bw.get("anomaly_condition_intent")
                condition_ok = True
                if required_intent and required_intent not in bf.intents:
                    condition_ok = False
                if mode == "hostile_probe_infrastructure" and not bf.targets:
                    condition_ok = False
                if condition_ok:
                    probability += bw["threat_add"]
                    drivers.append(
                        bw["explanation_threat"].format(targets=", ".join(bf.targets))
                    )

            # Threat reduction
            if "threat_subtract" in bw:
                probability -= bw["threat_subtract"]
                if "No strong threat indicators identified" in drivers:
                    drivers.remove("No strong threat indicators identified")
                drivers.append(bw["explanation_threat"])

        # Clamp after behavior modifiers
        probability = min(max(probability, 0.0), 1.0)
        level = _classify_threat(probability)

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
    logger.info("Threat assessment: %d entities, top threat=%s (%.1f%%)",
                len(results), results[0].entity_id if results else "N/A",
                results[0].threat_probability * 100 if results else 0)
    return results
