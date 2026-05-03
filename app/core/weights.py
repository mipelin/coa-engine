from __future__ import annotations

from pydantic import BaseModel


class ScenarioWeights(BaseModel):
    """Per-scenario weight overrides. Any field left None uses the global Settings default."""

    # Threat assessment weights
    threat_weight_max_anomaly: float | None = None
    threat_weight_avg_anomaly: float | None = None
    threat_weight_event_type_boost: float | None = None
    threat_weight_heading: float | None = None
    threat_weight_jamming: float | None = None
    threat_weight_convoy: float | None = None
    threat_cable_severance_vessel_boost: float | None = None
    threat_uav_heading_boost: float | None = None
    allied_deterrence_factor: float | None = None

    # Scoring weights
    scoring_weight_success: float | None = None
    scoring_weight_time: float | None = None
    scoring_weight_cable_protect: float | None = None
    scoring_weight_escalation: float | None = None
    scoring_weight_civilian: float | None = None
    scoring_weight_logistics: float | None = None
    scoring_weight_missed_detection: float | None = None

    # Anomaly rule weights
    anomaly_cable_severance_pts: float | None = None
    anomaly_proximity_threshold_close: float | None = None
    anomaly_proximity_pts_close: float | None = None
    anomaly_proximity_threshold_mid: float | None = None
    anomaly_proximity_pts_mid: float | None = None
    anomaly_suspicious_vessel_near_cable_threshold: float | None = None
    anomaly_suspicious_vessel_near_cable_pts: float | None = None
    anomaly_course_change_multi_pts: float | None = None
    anomaly_course_change_multi_min: int | None = None
    anomaly_course_change_single_pts: float | None = None
    anomaly_heading_strong_threshold: float | None = None
    anomaly_heading_strong_pts: float | None = None
    anomaly_heading_partial_threshold: float | None = None
    anomaly_heading_partial_pts: float | None = None
    anomaly_speed_anomaly_high_threshold: float | None = None
    anomaly_speed_anomaly_high_pts: float | None = None
    anomaly_speed_anomaly_mid_threshold: float | None = None
    anomaly_speed_anomaly_mid_pts: float | None = None
    anomaly_uav_detection_pts: float | None = None
    anomaly_jamming_high_threshold: float | None = None
    anomaly_jamming_high_pts: float | None = None
    anomaly_jamming_edge_pts: float | None = None
    anomaly_multisource_high_threshold: float | None = None
    anomaly_multisource_high_pts: float | None = None
    anomaly_multisource_mid_threshold: float | None = None
    anomaly_multisource_mid_pts: float | None = None
    anomaly_convoy_proximity_pts: float | None = None
    anomaly_convoy_region_pts: float | None = None
    anomaly_density_pts: float | None = None
    anomaly_post_severance_window_min: float | None = None
    anomaly_post_severance_pts: float | None = None
    anomaly_low_confidence_dampener: float | None = None


def merge_weights(weights: ScenarioWeights | None = None) -> dict:
    """Return a dict of effective weights by overlaying scenario overrides on global settings."""
    from .config import settings

    result: dict = {}
    if weights is not None:
        override_data = weights.model_dump(exclude_none=True)
        result.update(override_data)

    for field_name in ScenarioWeights.model_fields:
        if field_name not in result:
            result[field_name] = getattr(settings, field_name)

    return result
