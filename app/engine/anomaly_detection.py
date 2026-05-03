from __future__ import annotations

import logging

from ..core.config import settings
from ..core.constants import BEHAVIOR_WEIGHTS, AnomalyLevel, EntityType, EventType
from ..core.schemas import AnomalyResult, FeatureVector, OperationalEvent

logger = logging.getLogger("coa_engine.engine.anomaly_detection")


def _classify_level(score: float) -> AnomalyLevel:
    if score >= settings.anomaly_threshold_critical:
        return AnomalyLevel.CRITICAL
    if score >= settings.anomaly_threshold_high:
        return AnomalyLevel.HIGH
    if score >= settings.anomaly_threshold_medium:
        return AnomalyLevel.MEDIUM
    return AnomalyLevel.LOW


def _rule_score(event: OperationalEvent, feat: FeatureVector) -> tuple[float, list[str]]:
    score = 0.0
    explanations: list[str] = []

    # Cable severance is inherently critical
    if event.event_type == EventType.CABLE_SEVERANCE:
        score += settings.anomaly_cable_severance_pts
        explanations.append("Cable severance event — indicates confirmed infrastructure damage")

    # Proximity to critical infrastructure
    if feat.distance_to_nearest_critical_infrastructure < settings.anomaly_proximity_threshold_close:
        proximity_pts = settings.anomaly_proximity_pts_close * (
            1.0 - feat.distance_to_nearest_critical_infrastructure / settings.anomaly_proximity_threshold_close
        )
        score += proximity_pts
        explanations.append(
            f"Within {feat.distance_to_nearest_critical_infrastructure:.1f} km of critical infrastructure "
            f"(+{proximity_pts:.0f} pts)"
        )
    elif feat.distance_to_nearest_critical_infrastructure < settings.anomaly_proximity_threshold_mid:
        score += settings.anomaly_proximity_pts_mid
        explanations.append(
            f"Moderate proximity to critical infrastructure (+{settings.anomaly_proximity_pts_mid:.0f} pts)"
        )

    # Suspicious vessel near subsea cable
    if (event.entity_type == EntityType.SUSPICIOUS_VESSEL
            and feat.distance_to_nearest_critical_infrastructure < settings.anomaly_suspicious_vessel_near_cable_threshold):
        score += settings.anomaly_suspicious_vessel_near_cable_pts
        explanations.append(
            f"Suspicious vessel within {settings.anomaly_suspicious_vessel_near_cable_threshold:.0f} km "
            f"of critical infrastructure (+{settings.anomaly_suspicious_vessel_near_cable_pts:.0f} pts)"
        )

    # Course changes toward infrastructure
    if feat.course_change_count >= settings.anomaly_course_change_multi_min:
        score += settings.anomaly_course_change_multi_pts
        explanations.append(
            f"{feat.course_change_count} course changes observed for this entity "
            f"(+{settings.anomaly_course_change_multi_pts:.0f} pts)"
        )
    elif feat.course_change_count == 1:
        score += settings.anomaly_course_change_single_pts
        explanations.append(
            f"Single course change observed (+{settings.anomaly_course_change_single_pts:.0f} pts)"
        )

    # Heading toward critical asset
    if feat.heading_towards_critical_asset > settings.anomaly_heading_strong_threshold:
        score += settings.anomaly_heading_strong_pts
        explanations.append(
            f"Heading strongly toward a critical asset (+{settings.anomaly_heading_strong_pts:.0f} pts)"
        )
    elif feat.heading_towards_critical_asset > settings.anomaly_heading_partial_threshold:
        score += settings.anomaly_heading_partial_pts
        explanations.append(
            f"Heading partially toward a critical asset (+{settings.anomaly_heading_partial_pts:.0f} pts)"
        )

    # Speed anomaly (loitering or stopped near cables)
    if feat.speed_anomaly_score > settings.anomaly_speed_anomaly_high_threshold:
        score += settings.anomaly_speed_anomaly_high_pts
        explanations.append(
            f"Speed anomaly indicator (score {feat.speed_anomaly_score:.2f}) — "
            f"loitering or stopped near infrastructure (+{settings.anomaly_speed_anomaly_high_pts:.0f} pts)"
        )
    elif feat.speed_anomaly_score > settings.anomaly_speed_anomaly_mid_threshold:
        score += settings.anomaly_speed_anomaly_mid_pts
        explanations.append(
            f"Mild speed anomaly (+{settings.anomaly_speed_anomaly_mid_pts:.0f} pts)"
        )

    # UAV near airport
    if event.event_type == EventType.UAV_DETECTION:
        score += settings.anomaly_uav_detection_pts
        explanations.append(
            f"UAV detection event elevates anomaly score (+{settings.anomaly_uav_detection_pts:.0f} pts)"
        )

    # Jamming
    if feat.jamming_nearby > settings.anomaly_jamming_high_threshold:
        score += settings.anomaly_jamming_high_pts
        explanations.append(
            f"Jamming activity detected nearby (+{settings.anomaly_jamming_high_pts:.0f} pts)"
        )
    elif feat.jamming_nearby > 0.0:
        score += settings.anomaly_jamming_edge_pts
        explanations.append(
            f"Edge of jamming radius (+{settings.anomaly_jamming_edge_pts:.0f} pts)"
        )

    # Multi-source correlation
    if feat.multi_source_correlation_score >= settings.anomaly_multisource_high_threshold:
        score += settings.anomaly_multisource_high_pts
        explanations.append(
            f"Entity reported by 3+ independent sources (+{settings.anomaly_multisource_high_pts:.0f} pts)"
        )
    elif feat.multi_source_correlation_score >= settings.anomaly_multisource_mid_threshold:
        score += settings.anomaly_multisource_mid_pts
        explanations.append(
            f"Entity confirmed by 2 sources (+{settings.anomaly_multisource_mid_pts:.0f} pts)"
        )

    # Convoy activity
    if feat.convoy_activity_nearby > 0.5:
        score += settings.anomaly_convoy_proximity_pts
        explanations.append(
            f"Convoy activity in proximity (+{settings.anomaly_convoy_proximity_pts:.0f} pts)"
        )
    elif feat.convoy_activity_nearby > 0.0:
        score += settings.anomaly_convoy_region_pts
        explanations.append(
            f"Convoy activity in region (+{settings.anomaly_convoy_region_pts:.0f} pts)"
        )

    # Event density
    if feat.event_density_score > 0.7:
        score += settings.anomaly_density_pts
        explanations.append(
            f"High event density for this entity (+{settings.anomaly_density_pts:.0f} pts)"
        )

    # Post-cable-severance context
    if (0 < feat.time_since_cable_severance < settings.anomaly_post_severance_window_min
            and event.entity_type == EntityType.SUSPICIOUS_VESSEL):
        score += settings.anomaly_post_severance_pts
        explanations.append(
            f"Activity occurs {feat.time_since_cable_severance:.0f} min after cable severance "
            f"(+{settings.anomaly_post_severance_pts:.0f} pts)"
        )

    # Source confidence dampener for low-confidence OSINT
    if feat.source_confidence_weight < 0.5:
        score *= settings.anomaly_low_confidence_dampener
        explanations.append("Low source confidence reduces overall score")

    # Behavior-intent hooks (driven by BEHAVIOR_WEIGHTS config)
    behavior_mode = event.attributes.get("behavior_mode", "")
    intent = event.attributes.get("intent", "")
    target_infra = event.attributes.get("target_infra", "")

    if behavior_mode in BEHAVIOR_WEIGHTS:
        bw = BEHAVIOR_WEIGHTS[behavior_mode]

        # Additive boost — only if mode-specific condition is met
        if "anomaly_add" in bw:
            required_intent = bw.get("anomaly_condition_intent")
            needs_target = behavior_mode == "hostile_probe_infrastructure"
            condition_ok = True
            if required_intent and intent != required_intent:
                condition_ok = False
            if needs_target and not target_infra:
                condition_ok = False
            if condition_ok:
                pts = bw["anomaly_add"]
                score += pts
                explanations.append(
                    bw["explanation_anomaly"].format(target=target_infra, pts=int(pts))
                )

        # Multiplicative adjustment — always applies for the mode
        if "anomaly_multiply" in bw:
            score *= bw["anomaly_multiply"]
            explanations.append(bw["explanation_anomaly"])

    score = min(max(score, 0.0), 100.0)
    return score, explanations


def detect_anomalies(
    events: list[OperationalEvent],
    features: list[FeatureVector],
) -> list[AnomalyResult]:
    """Produce an AnomalyResult for every event using rule-based scoring."""
    feat_by_event = {f.event_id: f for f in features}
    results: list[AnomalyResult] = []

    for event in events:
        feat = feat_by_event.get(event.event_id)
        if feat is None:
            results.append(AnomalyResult(
                event_id=event.event_id,
                entity_id=event.entity_id,
                anomaly_score=0.0,
                anomaly_level=AnomalyLevel.LOW,
                explanations=["No feature vector available for this event"],
            ))
            continue

        score, explanations = _rule_score(event, feat)
        level = _classify_level(score)

        if not explanations:
            explanations.append("No significant anomaly indicators detected")

        results.append(AnomalyResult(
            event_id=event.event_id,
            entity_id=event.entity_id,
            anomaly_score=round(score, 1),
            anomaly_level=level,
            explanations=explanations,
        ))

    high_count = sum(1 for r in results if r.anomaly_level in (AnomalyLevel.HIGH, AnomalyLevel.CRITICAL))
    logger.info("Anomaly detection: %d events scored, %d HIGH/CRITICAL", len(results), high_count)

    return results
