from __future__ import annotations

from ..core.constants import EntityType, EventType
from ..core.schemas import (
    AnomalyResult,
    Briefing,
    CourseOfAction,
    OperationalEvent,
    Recommendation,
    ScoredCOA,
    ThreatResult,
)


def generate_briefing(
    events: list[OperationalEvent],
    anomalies: list[AnomalyResult],
    threats: list[ThreatResult],
    scored: list[ScoredCOA],
    recommendation: Recommendation,
) -> Briefing:
    """Generate a commander-style decision-support briefing."""
    if not events:
        return Briefing(
            situation="No events available for analysis.",
            key_indicators=[],
            assessment="Insufficient data for assessment.",
            coas_considered=[],
            recommended_coa="None",
            risks=["No data"],
            confidence="LOW",
            assumptions=["No events provided"],
        )

    sorted_events = sorted(events, key=lambda e: e.timestamp)
    time_range = (
        f"{sorted_events[0].timestamp.strftime('%HZ %d %b')} to "
        f"{sorted_events[-1].timestamp.strftime('%HZ %d %b')}"
    )

    # Situation
    n_suspicious_vessels = len(set(
        e.entity_id for e in events if e.entity_type == EntityType.SUSPICIOUS_VESSEL
    ))
    has_severance = any(e.event_type == EventType.CABLE_SEVERANCE for e in events)
    has_uav = any(e.entity_type == EntityType.UAV for e in events)
    has_jamming = any(e.event_type == EventType.JAMMING_DETECTED for e in events)
    has_convoy = any(e.event_type == EventType.CONVOY_SIGHTING for e in events)

    situation_parts = [
        f"Decision-support summary for Baltic Sea area, {time_range}.",
        f"{len(events)} events processed across "
        f"{len(set(e.entity_id for e in events))} entities.",
        f"{n_suspicious_vessels} suspicious vessel(s) identified.",
    ]
    if has_severance:
        situation_parts.append("Confirmed cable severance on Baltic Cable Alpha.")
    if has_uav:
        situation_parts.append("Unidentified UAV operating near civilian airport.")
    if has_jamming:
        situation_parts.append("GPS/VHF jamming detected south of Gotland.")
    if has_convoy:
        situation_parts.append("Multiple unmarked convoy sightings near border areas.")
    situation = " ".join(situation_parts)

    # Key indicators
    indicators: list[str] = []
    critical_anomalies = [a for a in anomalies if a.anomaly_level.value in ("HIGH", "CRITICAL")]
    if critical_anomalies:
        indicators.append(f"{len(critical_anomalies)} high/critical anomaly indicators")
    if has_severance:
        indicators.append("Cable Alpha fiber cut confirmed at repeater R-14")
    if has_jamming:
        indicators.append("Jamming expanding to 35nm radius affecting civilian navigation")
    if has_uav:
        indicators.append("UAV executing racetrack pattern near Visby Airport")
    if n_suspicious_vessels:
        indicators.append(f"{n_suspicious_vessels} suspicious vessel(s) near cable corridor")
    if not indicators:
        indicators.append("No significant threat indicators")

    # Assessment
    top_threats = threats[:3] if threats else []
    assessment_parts = ["Assessment: "]
    if top_threats:
        level_counts = {}
        for t in top_threats:
            level_counts[t.threat_level.value] = level_counts.get(t.threat_level.value, 0) + 1
        levels_str = ", ".join(f"{v}x {k}" for k, v in level_counts.items())
        assessment_parts.append(f"Top threats: {levels_str}.")
        for t in top_threats[:2]:
            assessment_parts.append(
                f"{t.entity_id}: {t.threat_probability:.0%} probability "
                f"({', '.join(t.main_drivers[:2])})."
            )
    else:
        assessment_parts.append("No elevated threat entities identified.")
    assessment = " ".join(assessment_parts)

    # COAs considered
    coa_titles = [s.coa.title for s in scored] if scored else ["None generated"]

    # Recommended COA
    rec_text = "None"
    if recommendation.recommended:
        r = recommendation.recommended
        rec_text = (
            f"{r.coa.title} (score {r.total_score:.1f}/100, "
            f"success probability {r.simulation.success_probability:.0%}, "
            f"feasibility {r.coa.feasibility_score:.0%}). "
            f"{recommendation.rationale}"
        )

    # Risks
    risks: list[str] = []
    if has_severance:
        risks.append("Second subsea cable (Cable Beta) may be at risk of compromise")
    if has_jamming:
        risks.append("Continued jamming may affect civilian maritime and aviation safety")
    if has_uav:
        risks.append("UAV activity may escalate to controlled airspace violation")
    if has_convoy:
        risks.append("Convoy movements near border indicate potential ground-domain activity")
    if not risks:
        risks.append("No significant risks identified in current scenario")
    if recommendation.recommended:
        r = recommendation.recommended
        if r.simulation.escalation_probability > 0.1:
            risks.append(f"Recommended COA carries escalation probability of {r.simulation.escalation_probability:.0%}")

    # Confidence
    if top_threats:
        avg_conf = sum(t.confidence for t in top_threats) / len(top_threats)
        if avg_conf > 0.8:
            confidence = "HIGH"
        elif avg_conf > 0.6:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
    else:
        confidence = "LOW"

    # Assumptions
    assumptions: list[str] = [
        "All data is synthetic and for prototype demonstration only",
        "Source reliability is as reported in the synthetic event stream",
        "Weather and sea state do not prevent observation activities",
    ]
    if recommendation.recommended:
        assumptions.extend(recommendation.recommended.coa.assumptions[:3])
        if recommendation.recommended.coa.missing_assets:
            assumptions.append(
                "Some recommended supporting assets are currently unavailable: "
                + ", ".join(recommendation.recommended.coa.missing_assets)
            )

    return Briefing(
        situation=situation,
        key_indicators=indicators,
        assessment=assessment,
        coas_considered=coa_titles,
        recommended_coa=rec_text,
        risks=risks,
        confidence=confidence,
        assumptions=assumptions,
    )
