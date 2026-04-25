from __future__ import annotations

import numpy as np

from ..core.config import settings
from ..core.constants import EntityType, EventType
from ..core.schemas import CourseOfAction, OperationalEvent, SimulationResult, ThreatResult

RNG_SEED = 42


def _scenario_baseline(events: list[OperationalEvent], threats: list[ThreatResult]) -> dict:
    """Derive baseline scenario parameters from the threat picture."""
    max_threat = max((t.threat_probability for t in threats), default=0.0)
    has_severance = any(e.event_type == EventType.CABLE_SEVERANCE for e in events)
    n_suspicious = sum(1 for t in threats if "SUSP" in t.entity_id or "UAV" in t.entity_id)
    return {
        "max_threat": max_threat,
        "has_severance": has_severance,
        "n_suspicious": n_suspicious,
    }


def run_simulations(
    coas: list[CourseOfAction],
    events: list[OperationalEvent],
    threats: list[ThreatResult],
) -> list[SimulationResult]:
    """Run Monte Carlo-style simulation for each COA."""
    baseline = _scenario_baseline(events, threats)
    rng = np.random.default_rng(RNG_SEED)
    results: list[SimulationResult] = []

    for coa in coas:
        results.append(_simulate_coa(coa, baseline, rng))

    return results


def _simulate_coa(
    coa: CourseOfAction,
    baseline: dict,
    rng: np.random.Generator,
) -> SimulationResult:
    n = settings.simulation_runs

    # Base effectiveness from COA characteristics
    is_monitor = "monitor" in coa.title.lower() or "observation" in coa.title.lower() or "ISR" in coa.title
    is_shadow = "shadow" in coa.title.lower()
    is_cable_protect = "cable" in coa.title.lower() and "protect" in coa.title.lower()
    is_combined = "combined" in coa.title.lower()
    asset_gap = 1.0 - coa.feasibility_score

    # Success probability: higher for more active COAs, lower for baseline threat severity
    base_success = 0.50
    if is_monitor:
        base_success += 0.15
    if is_shadow:
        base_success += 0.20
    if is_cable_protect:
        base_success += 0.25
    if is_combined:
        base_success += 0.30
    base_success -= baseline["max_threat"] * 0.15
    base_success -= baseline["n_suspicious"] * 0.02
    base_success -= asset_gap * 0.45
    base_success = min(max(base_success, 0.05), 0.95)

    success_draws = rng.beta(
        max(base_success * 10, 1.0),
        max((1.0 - base_success) * 10, 1.0),
        size=n,
    )
    success_prob = float(np.mean(success_draws))

    # Time to effect
    base_time = coa.estimated_time_minutes * (1.0 + 0.8 * asset_gap)
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
    base_cable_risk += asset_gap * 0.25
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
    base_escalation += asset_gap * 0.10
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
    base_missed += asset_gap * 0.35
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
