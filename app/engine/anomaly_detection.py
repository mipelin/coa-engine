from __future__ import annotations

from ..core.config import settings
from ..core.constants import AnomalyLevel, EntityType, EventType
from ..core.schemas import AnomalyResult, FeatureVector, OperationalEvent


def _classify_level(score: float) -> AnomalyLevel:
    if score >= settings.anomaly_threshold_critical:
        return AnomalyLevel.CRITICAL
    if score >= settings.anomaly_threshold_high:
        return AnomalyLevel.HIGH
    if score >= settings.anomaly_threshold_medium:
        return AnomalyLevel.MEDIUM
    return AnomalyLevel.LOW


def _rule_score(event: OperationalEvent, feat: FeatureVector) -> tuple[float, list[str]]:
    """Return (raw score 0-100, explanations)."""
    score = 0.0
    explanations: list[str] = []

    # Cable severance is inherently critical
    if event.event_type == EventType.CABLE_SEVERANCE:
        score += 55.0
        explanations.append("Cable severance event — indicates confirmed infrastructure damage")

    # Proximity to critical infrastructure
    if feat.distance_to_nearest_critical_infrastructure < 5.0:
        proximity_pts = 20.0 * (1.0 - feat.distance_to_nearest_critical_infrastructure / 5.0)
        score += proximity_pts
        explanations.append(
            f"Within {feat.distance_to_nearest_critical_infrastructure:.1f} km of critical infrastructure "
            f"(+{proximity_pts:.0f} pts)"
        )
    elif feat.distance_to_nearest_critical_infrastructure < 20.0:
        score += 8.0
        explanations.append("Moderate proximity to critical infrastructure (+8 pts)")

    # Suspicious vessel near subsea cable
    if (event.entity_type == EntityType.SUSPICIOUS_VESSEL
            and feat.distance_to_nearest_critical_infrastructure < 10.0):
        score += 15.0
        explanations.append("Suspicious vessel within 10 km of critical infrastructure (+15 pts)")

    # Course changes toward infrastructure
    if feat.course_change_count >= 2:
        score += 12.0
        explanations.append(
            f"{feat.course_change_count} course changes observed for this entity (+12 pts)"
        )
    elif feat.course_change_count == 1:
        score += 5.0
        explanations.append("Single course change observed (+5 pts)")

    # Heading toward critical asset
    if feat.heading_towards_critical_asset > 0.7:
        score += 10.0
        explanations.append("Heading strongly toward a critical asset (+10 pts)")
    elif feat.heading_towards_critical_asset > 0.3:
        score += 4.0
        explanations.append("Heading partially toward a critical asset (+4 pts)")

    # Speed anomaly (loitering or stopped near cables)
    if feat.speed_anomaly_score > 0.5:
        score += 10.0
        explanations.append(
            f"Speed anomaly indicator (score {feat.speed_anomaly_score:.2f}) — "
            f"loitering or stopped near infrastructure (+10 pts)"
        )
    elif feat.speed_anomaly_score > 0.2:
        score += 4.0
        explanations.append("Mild speed anomaly (+4 pts)")

    # UAV near airport
    if event.event_type == EventType.UAV_DETECTION:
        score += 15.0
        explanations.append("UAV detection event elevates anomaly score (+15 pts)")

    # Jamming
    if feat.jamming_nearby > 0.5:
        score += 12.0
        explanations.append("Jamming activity detected nearby (+12 pts)")
    elif feat.jamming_nearby > 0.0:
        score += 5.0
        explanations.append("Edge of jamming radius (+5 pts)")

    # Multi-source correlation
    if feat.multi_source_correlation_score >= 0.75:
        score += 10.0
        explanations.append("Entity reported by 3+ independent sources (+10 pts)")
    elif feat.multi_source_correlation_score >= 0.5:
        score += 4.0
        explanations.append("Entity confirmed by 2 sources (+4 pts)")

    # Convoy activity
    if feat.convoy_activity_nearby > 0.5:
        score += 5.0
        explanations.append("Convoy activity in proximity (+5 pts)")
    elif feat.convoy_activity_nearby > 0.0:
        score += 2.0
        explanations.append("Convoy activity in region (+2 pts)")

    # Event density
    if feat.event_density_score > 0.7:
        score += 5.0
        explanations.append("High event density for this entity (+5 pts)")

    # Post-cable-severance context
    if 0 < feat.time_since_cable_severance < 120 and event.entity_type == EntityType.SUSPICIOUS_VESSEL:
        score += 5.0
        explanations.append(
            f"Activity occurs {feat.time_since_cable_severance:.0f} min after cable severance (+5 pts)"
        )

    # Source confidence dampener for low-confidence OSINT
    if feat.source_confidence_weight < 0.5:
        score *= 0.7
        explanations.append("Low source confidence reduces overall score")

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

    return results
