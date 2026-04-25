from __future__ import annotations

import logging

from ..core.constants import EntityType, EventType
from ..core.schemas import CourseOfAction, OperationalEvent, ThreatResult

logger = logging.getLogger("coa_engine.engine.coa_generation")


def _has_cable_severance(events: list[OperationalEvent]) -> bool:
    return any(e.event_type == EventType.CABLE_SEVERANCE for e in events)


def _has_uav_threat(threats: list[ThreatResult]) -> bool:
    entity_types = {t.entity_id for t in threats}
    return any("UAV" in eid for eid in entity_types)


def _has_convoy_activity(events: list[OperationalEvent]) -> bool:
    return any(e.event_type == EventType.CONVOY_SIGHTING for e in events)


def _max_threat_level(threats: list[ThreatResult]) -> str:
    if not threats:
        return "LOW"
    return threats[0].threat_level.value


def _normalize_asset_inventory(
    asset_inventory: dict[str, int] | None,
    required_assets: set[str],
) -> dict[str, int]:
    if asset_inventory is None:
        return {asset: 1 for asset in required_assets}
    return {asset: max(int(asset_inventory.get(asset, 1)), 0) for asset in required_assets}


def _apply_asset_feasibility(
    coa: CourseOfAction,
    asset_inventory: dict[str, int],
) -> CourseOfAction:
    available_assets = [asset for asset in coa.required_assets if asset_inventory.get(asset, 0) > 0]
    missing_assets = [asset for asset in coa.required_assets if asset_inventory.get(asset, 0) <= 0]
    feasibility = 1.0 if not coa.required_assets else len(available_assets) / len(coa.required_assets)
    assumptions = list(coa.assumptions)
    if missing_assets:
        assumptions.append(
            "Current asset inventory does not fully support this COA: "
            + ", ".join(missing_assets)
        )

    return coa.model_copy(update={
        "available_assets": available_assets,
        "missing_assets": missing_assets,
        "feasibility_score": round(feasibility, 3),
        "assumptions": assumptions,
    })


def generate_coas(
    events: list[OperationalEvent],
    threats: list[ThreatResult],
    asset_inventory: dict[str, int] | None = None,
) -> list[CourseOfAction]:
    """Generate advisory courses of action based on the current threat picture."""
    coas: list[CourseOfAction] = []

    cable_severed = _has_cable_severance(events)
    uav_threat = _has_uav_threat(threats)
    convoy_active = _has_convoy_activity(events)
    high_threats = [t for t in threats if t.threat_level.value in ("HIGH", "CRITICAL")]

    # COA 1: Enhanced ISR and monitoring
    coas.append(CourseOfAction(
        coa_id="COA-001",
        title="Increase ISR Coverage and Observation",
        description=(
            "Recommend increasing ISR coverage to maintain persistent observation "
            "of suspicious vessel activity. Coordinate with available tactical UAV assets "
            "and satellite observation requests to improve coverage of the cable corridor."
        ),
        required_assets=["isr_uav", "satellite_observation_request", "sigint_team"],
        assumptions=[
            "ISR assets can be redirected within 30 minutes",
            "Weather permits UAV operations in the area",
            "Satellite revisit time is acceptable for tracking",
        ],
        estimated_time_minutes=30,
        expected_effect="Persistent observation of suspicious entities and cable corridor",
        risk_categories=["sensor_gap", "weather"],
        escalation_risk=0.05,
        civilian_risk=0.0,
        logistics_burden=0.2,
    ))

    # COA 2: Shadow suspicious vessels
    if high_threats:
        coas.append(CourseOfAction(
            coa_id="COA-002",
            title="Shadow Suspicious Vessels with Allied Maritime Assets",
            description=(
                "Recommend allied maritime patrol assets maintain visual and radar contact "
                "with identified suspicious vessels. Maintain safe distance. Document activity "
                "and report observations through established channels."
            ),
            required_assets=["maritime_patrol_asset", "coast_guard_liaison"],
            assumptions=[
                "Allied naval assets are available within 60 minutes",
                "Rules of observation are clearly communicated",
                "Vessels will not attempt evasion at high speed",
            ],
            estimated_time_minutes=60,
            expected_effect="Direct observation and deterrence through presence",
            risk_categories=["proximity_incident", "navigation_safety"],
            escalation_risk=0.15,
            civilian_risk=0.05,
            logistics_burden=0.4,
        ))

    # COA 3: Protect second cable
    if cable_severed:
        coas.append(CourseOfAction(
            coa_id="COA-003",
            title="Prioritize Protection of Second Subsea Cable",
            description=(
                "Given confirmed severance of Cable Alpha, recommend prioritizing "
                "monitoring and protection of Cable Beta. Consider assigning the nearest "
                "available allied maritime asset to observe the Cable Beta corridor. "
                "Coordinate with cable operator for continuous integrity monitoring."
            ),
            required_assets=["maritime_patrol_asset", "cable_operator_liaison", "isr_uav"],
            assumptions=[
                "Cable Beta has not yet been compromised",
                "Nearest allied asset can reach Cable Beta within 90 minutes",
                "Cable operator can provide continuous integrity status",
            ],
            estimated_time_minutes=90,
            expected_effect="Reduced risk of second cable compromise",
            risk_categories=["asset_availability", "response_time"],
            escalation_risk=0.10,
            civilian_risk=0.0,
            logistics_burden=0.5,
        ))

    # COA 4: Coordinate civilian airspace safety
    if uav_threat:
        coas.append(CourseOfAction(
            coa_id="COA-004",
            title="Coordinate Civilian Airspace Safety Response",
            description=(
                "Recommend coordination with civil aviation authority to manage "
                "airspace around affected airport. Support establishment of temporary "
                "flight restrictions. Share available sensor data with air traffic control."
            ),
            required_assets=["airspace_coordinator", "atc_liaison", "sensor_data_feed"],
            assumptions=[
                "Civil aviation authority is responsive",
                "UAV does not escalate to controlled airspace breach",
                "Commercial diversions can be managed without major disruption",
            ],
            estimated_time_minutes=20,
            expected_effect="Safe civilian airspace management during UAV incident",
            risk_categories=["airspace_safety", "public_disruption"],
            escalation_risk=0.05,
            civilian_risk=0.1,
            logistics_burden=0.2,
        ))

    # COA 5: Border monitoring for convoy activity
    if convoy_active:
        coas.append(CourseOfAction(
            coa_id="COA-005",
            title="Increase Border Monitoring and Information Sharing",
            description=(
                "Recommend increased monitoring of border areas where convoy activity "
                "has been reported. Coordinate information sharing with border security "
                "and allied intelligence. Maintain an awareness-focused posture."
            ),
            required_assets=["border_patrol_liaison", "intelligence_team", "surveillance_asset"],
            assumptions=[
                "Convoy activity is observable through existing ISR",
                "Border security forces can increase patrol frequency",
                "Convoy movements remain indicators requiring corroboration",
            ],
            estimated_time_minutes=45,
            expected_effect="Enhanced situational awareness of ground movements",
            risk_categories=["intelligence_gap", "response_latency"],
            escalation_risk=0.08,
            civilian_risk=0.02,
            logistics_burden=0.3,
        ))

    # COA 6: Combined posture
    if cable_severed and high_threats:
        coas.append(CourseOfAction(
            coa_id="COA-006",
            title="Combined Observation, Cable Protection, and Border Monitoring",
            description=(
                "Recommend a combined approach: shadow suspicious vessels while "
                "simultaneously increasing observation of Cable Beta and expanding "
                "border monitoring. This is the most resource-intensive option but "
                "addresses all identified threat vectors."
            ),
            required_assets=[
                "maritime_patrol_asset", "isr_uav", "cable_operator_liaison",
                "border_patrol_liaison", "intelligence_team", "coast_guard_liaison",
            ],
            assumptions=[
                "Sufficient assets available for multi-axis response",
                "Coordination staff can manage concurrent advisory workflows",
                "Logistics support is available for extended operations",
            ],
            estimated_time_minutes=90,
            expected_effect="Comprehensive coverage across all threat domains",
            risk_categories=["resource_strain", "coordination_complexity"],
            escalation_risk=0.20,
            civilian_risk=0.05,
            logistics_burden=0.8,
        ))

    # Fallback: baseline monitoring
    if not coas:
        coas.append(CourseOfAction(
            coa_id="COA-000",
            title="Maintain Baseline Monitoring",
            description="No elevated threat indicators detected. Recommend continuing routine monitoring.",
            required_assets=["standard_watch_team"],
            assumptions=["No change in current threat picture"],
            estimated_time_minutes=0,
            expected_effect="Continued situational awareness at baseline level",
            risk_categories=["detection_lag"],
            escalation_risk=0.0,
            civilian_risk=0.0,
            logistics_burden=0.0,
        ))

    required_assets = {asset for coa in coas for asset in coa.required_assets}
    normalized_inventory = _normalize_asset_inventory(asset_inventory, required_assets)
    result = [_apply_asset_feasibility(coa, normalized_inventory) for coa in coas]
    logger.info("Generated %d rule-based COAs (cable=%s, uav=%s, convoy=%s)",
                len(result), cable_severed, uav_threat, convoy_active)
    return result
