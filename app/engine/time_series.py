from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass

from ..core.constants import EventType
from ..core.schemas import OperationalEvent, TemporalSummary

logger = logging.getLogger("coa_engine.engine.time_series")

SEVERITY_MAP = {
    EventType.CABLE_SEVERANCE: 4,
    EventType.JAMMING_DETECTED: 3,
    EventType.UAV_DETECTION: 3,
    EventType.CONVOY_SIGHTING: 2,
    EventType.VESSEL_COURSE_CHANGE: 2,
    EventType.SATELLITE_DETECTION: 1,
    EventType.SOCIAL_MEDIA_REPORT: 1,
    EventType.VESSEL_POSITION: 0,
    EventType.OPERATIONAL_REPORT: 0,
}


def analyze_temporal_patterns(events: list[OperationalEvent]) -> TemporalSummary:
    """Analyze temporal patterns in the event stream."""
    if len(events) < 2:
        return TemporalSummary(
            event_rate_per_hour=0.0,
            escalation_rate=0.0,
            severity_trend="stable",
            cluster_count=0,
            mean_inter_event_minutes=None,
        )

    sorted_events = sorted(events, key=lambda e: e.timestamp)

    # Inter-event intervals
    intervals: list[float] = []
    for i in range(1, len(sorted_events)):
        delta = (sorted_events[i].timestamp - sorted_events[i - 1].timestamp).total_seconds() / 60.0
        intervals.append(delta)

    mean_interval = statistics.mean(intervals) if intervals else 0.0

    # Event rate per hour
    total_hours = (sorted_events[-1].timestamp - sorted_events[0].timestamp).total_seconds() / 3600.0
    event_rate = len(events) / max(total_hours, 0.01)

    # Severity trend: compare first half severity to second half
    severities = [SEVERITY_MAP.get(e.event_type, 0) for e in sorted_events]
    mid = len(severities) // 2
    if mid > 0:
        first_half_avg = statistics.mean(severities[:mid])
        second_half_avg = statistics.mean(severities[mid:])
        escalation_rate = second_half_avg - first_half_avg
        if escalation_rate > 0.3:
            severity_trend = "increasing"
        elif escalation_rate < -0.3:
            severity_trend = "decreasing"
        else:
            severity_trend = "stable"
    else:
        escalation_rate = 0.0
        severity_trend = "stable"

    # Temporal clusters: bursts where 3+ events occur within 30 minutes
    clusters = 0
    cluster_threshold_minutes = 30.0
    i = 0
    while i < len(intervals):
        cluster_size = 1
        j = i
        while j < len(intervals) and intervals[j] < cluster_threshold_minutes:
            cluster_size += 1
            j += 1
        if cluster_size >= 3:
            clusters += 1
        i = max(j, i + 1)

    logger.info("Temporal analysis: rate=%.1f/hr, trend=%s, clusters=%d",
                event_rate, severity_trend, clusters)

    return TemporalSummary(
        event_rate_per_hour=round(event_rate, 2),
        escalation_rate=round(escalation_rate, 3),
        severity_trend=severity_trend,
        cluster_count=clusters,
        mean_inter_event_minutes=round(mean_interval, 1),
    )
