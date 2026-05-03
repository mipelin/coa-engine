from __future__ import annotations

import numpy as np

from ..core.config import settings
from ..core.constants import EventType
from ..core.schemas import CourseOfAction, OperationalEvent, ScenarioState, SimulationResult, ThreatResult

import logging
from hashlib import sha256

logger = logging.getLogger("coa_engine.engine.simulation")

TEMPLATE_CAPABILITIES = {
    "COA-TPL-ISR": {"monitor": True, "shadow": False, "cable_protect": False, "combined": False},
    "COA-TPL-SHADOW": {"monitor": True, "shadow": True, "cable_protect": False, "combined": False},
    "COA-TPL-CABLE-PROTECT": {"monitor": True, "shadow": False, "cable_protect": True, "combined": False},
    "COA-TPL-AIRSPACE": {"monitor": True, "shadow": False, "cable_protect": False, "combined": False},
    "COA-TPL-BORDER": {"monitor": True, "shadow": False, "cable_protect": False, "combined": False},
    "COA-TPL-COMBINED": {"monitor": True, "shadow": True, "cable_protect": True, "combined": True},
    "COA-TPL-BASELINE": {"monitor": False, "shadow": False, "cable_protect": False, "combined": False},
}

TEMPLATE_BASE_SUCCESS = {
    "COA-TPL-ISR": 0.56,
    "COA-TPL-SHADOW": 0.63,
    "COA-TPL-CABLE-PROTECT": 0.68,
    "COA-TPL-AIRSPACE": 0.58,
    "COA-TPL-BORDER": 0.57,
    "COA-TPL-COMBINED": 0.76,
    "COA-TPL-BASELINE": 0.42,
}


def _scenario_baseline(
    events: list[OperationalEvent],
    threats: list[ThreatResult],
    scenario_state: ScenarioState | None = None,
) -> dict:
    """Derive baseline scenario parameters from the threat picture."""
    max_threat = max((t.threat_probability for t in threats), default=0.0)
    has_severance = any(e.event_type == EventType.CABLE_SEVERANCE for e in events)
    n_suspicious = sum(1 for t in threats if "SUSP" in t.entity_id or "UAV" in t.entity_id)
    active_incidents = len(scenario_state.active_incidents) if scenario_state else 0
    infra_status = scenario_state.infrastructure_status if scenario_state else "nominal"
    return {
        "max_threat": max_threat,
        "has_severance": has_severance,
        "n_suspicious": n_suspicious,
        "active_incidents": active_incidents,
        "infrastructure_status": infra_status,
    }


def run_simulations(
    coas: list[CourseOfAction],
    events: list[OperationalEvent],
    threats: list[ThreatResult],
    scenario_state: ScenarioState | None = None,
) -> list[SimulationResult]:
    """Run Monte Carlo-style simulation for each COA."""
    baseline = _scenario_baseline(events, threats, scenario_state)
    results: list[SimulationResult] = []

    for coa in coas:
        results.append(_simulate_coa(coa, baseline))

    return results


def _semantic_seed(coa: CourseOfAction) -> int:
    payload = "|".join([
        coa.template_id,
        ",".join(sorted(coa.target_entities)),
        ",".join(sorted(coa.assigned_assets)),
        str(round(coa.feasibility_score, 3)),
        str(coa.estimated_time_minutes),
    ])
    digest = sha256(payload.encode("utf-8")).digest()
    return settings.simulation_seed + int.from_bytes(digest[:8], "big")


def _simulate_coa(
    coa: CourseOfAction,
    baseline: dict,
) -> SimulationResult:
    n = settings.simulation_runs
    rng = np.random.default_rng(_semantic_seed(coa))

    caps = TEMPLATE_CAPABILITIES.get(
        coa.template_id,
        {"monitor": False, "shadow": False, "cable_protect": False, "combined": False},
    )
    is_monitor = caps["monitor"]
    is_shadow = caps["shadow"]
    is_cable_protect = caps["cable_protect"]
    is_combined = caps["combined"]
    asset_gap = 1.0 - coa.feasibility_score
    asset_coverage = (
        len(coa.assigned_assets) / len(coa.required_assets)
        if coa.required_assets else 1.0
    )
    target_count = max(len(coa.target_entities), 1)
    target_pressure = min(target_count / 3.0, 1.0)
    incident_pressure = min(baseline["active_incidents"] / 5.0, 1.0)
    infrastructure_stressed = baseline["infrastructure_status"] != "nominal"

    # Success probability: higher for more active COAs, lower for baseline threat severity
    base_success = TEMPLATE_BASE_SUCCESS.get(coa.template_id, 0.50)
    if target_count > 1 and not is_combined:
        base_success -= 0.05 * target_pressure
    if target_count > 1 and is_combined:
        base_success += 0.04 * target_pressure
    base_success += 0.05 * asset_coverage
    base_success -= baseline["max_threat"] * 0.15
    base_success -= baseline["n_suspicious"] * 0.02
    base_success -= incident_pressure * 0.05
    base_success -= asset_gap * 0.75
    base_success = min(max(base_success, 0.05), 0.95)

    success_draws = rng.beta(
        max(base_success * 10, 1.0),
        max((1.0 - base_success) * 10, 1.0),
        size=n,
    )
    success_prob = float(np.mean(success_draws))

    # Time to effect
    base_time = coa.estimated_time_minutes * (1.0 + 1.1 * asset_gap + 0.15 * target_pressure)
    if infrastructure_stressed and is_cable_protect:
        base_time *= 0.9
    time_draws = rng.normal(base_time, base_time * 0.2, size=n)
    time_draws = np.maximum(time_draws, 5.0)
    expected_time = float(np.mean(time_draws))

    # Risk to second cable
    base_cable_risk = 0.4 if baseline["has_severance"] else 0.1
    if is_cable_protect:
        base_cable_risk *= 0.3
    if is_combined:
        base_cable_risk *= 0.4
    if is_monitor and not is_cable_protect:
        base_cable_risk *= 0.8
    if target_count > 1 and not is_cable_protect:
        base_cable_risk += 0.05 * target_pressure
    if infrastructure_stressed:
        base_cable_risk += 0.05
    base_cable_risk += asset_gap * 0.40
    base_cable_risk = min(max(base_cable_risk, 0.01), 0.95)
    cable_draws = rng.beta(
        max(base_cable_risk * 10, 1.0),
        max((1.0 - base_cable_risk) * 10, 1.0),
        size=n,
    )
    cable_risk = float(np.mean(cable_draws))

    # Escalation probability
    base_escalation = coa.escalation_risk
    if baseline["n_suspicious"] > 2:
        base_escalation += 0.05
    if is_combined:
        base_escalation += 0.03
    if target_count > 1:
        base_escalation += 0.04 * target_pressure
    base_escalation += asset_gap * 0.18
    base_escalation = min(max(base_escalation, 0.01), 0.95)
    escalation_draws = rng.beta(
        max(base_escalation * 20, 1.0),
        max((1.0 - base_escalation) * 20, 1.0),
        size=n,
    )
    escalation_prob = float(np.mean(escalation_draws))

    # Missed detection probability
    base_missed = 0.3
    if is_shadow:
        base_missed *= 0.3
    if is_combined:
        base_missed *= 0.25
    if is_monitor:
        base_missed *= 0.5
    if is_cable_protect:
        base_missed *= 0.7
    if target_count > 1 and not is_combined:
        base_missed += 0.08 * target_pressure
    base_missed -= 0.10 * asset_coverage
    base_missed += asset_gap * 0.50
    base_missed = min(max(base_missed, 0.01), 0.95)
    missed_draws = rng.beta(
        max(base_missed * 10, 1.0),
        max((1.0 - base_missed) * 10, 1.0),
        size=n,
    )
    missed_prob = float(np.mean(missed_draws))

    # Confidence interval for success probability
    ci_low = float(np.percentile(success_draws, 5))
    ci_high = float(np.percentile(success_draws, 95))

    return SimulationResult(
        coa_id=coa.coa_id,
        success_probability=round(success_prob, 3),
        expected_time_to_effect=round(expected_time, 1),
        risk_to_second_cable=round(cable_risk, 3),
        escalation_probability=round(escalation_prob, 3),
        missed_detection_probability=round(missed_prob, 3),
        confidence_interval=(round(ci_low, 3), round(ci_high, 3)),
        simulation_runs=n,
    )
