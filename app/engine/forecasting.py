"""Short-horizon forecasting and what-if analysis.

Clones the current SimulationScenario state, applies hypothetical
perturbations (COA choice, injected events), runs forward ticks, and
produces a structured forecast. The LLM may rephrase the output but
must never generate the forecast itself.

Never mutates live engine state.
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from typing import Any

from .analysis_service import AnalysisContext, run_canonical_analysis
from .contact_engine import SimulationScenario, get_contact_engine
from .scenario_generator import ScenarioGenerator, StimulusEvent
from .state_store import StateStore, get_state_store

logger = logging.getLogger("coa_engine.engine.forecasting")

# ---------------------------------------------------------------------------
# Forecast data structures
# ---------------------------------------------------------------------------

_FORECAST_KEYWORDS = (
    "what if", "what happens if", "if we choose", "if we pick",
    "how would", "forecast", "next", "ahead", "projected",
    "what would happen", "simulate", "how will threat",
)


def is_forecast_question(question: str) -> bool:
    q = question.lower().strip()
    return any(kw in q for kw in _FORECAST_KEYWORDS)


@dataclass
class ForecastResult:
    summary: str
    expected_threat_trend: str  # "increase" | "decrease" | "stable"
    key_risks: list[str] = field(default_factory=list)
    expected_outcome: str = ""
    confidence: str = "medium"
    based_on: list[str] = field(default_factory=list)
    tick_horizon: int = 0
    threat_level_start: str = "LOW"
    threat_level_end: str = "LOW"
    contacts_start: int = 0
    contacts_end: int = 0
    stimuli_fired: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Scenario cloning
# ---------------------------------------------------------------------------


def _clone_sim(scenario: SimulationScenario) -> SimulationScenario:
    """Deep-clone a SimulationScenario without affecting live state.

    Overrides side-effect methods to prevent the clone from writing to the
    live StateStore or EventEngine when tick_forward() fires stimuli.
    """
    clone = copy.deepcopy(scenario)
    clone._process_trigger_as_event = lambda *a, **kw: None  # type: ignore[attr-defined]
    clone._update_stimuli_counts = lambda *a, **kw: None  # type: ignore[attr-defined]
    return clone


# ---------------------------------------------------------------------------
# Threat level estimation from contacts (lightweight)
# ---------------------------------------------------------------------------

_THREAT_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
_THREAT_NAMES = {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}


def _estimate_threat_level(contacts: list[Any]) -> str:
    """Estimate forecast threat level through the canonical analysis pipeline."""
    if not contacts:
        return "LOW"
    store = get_state_store()
    events = [StateStore._contact_to_operational_event(c) for c in contacts]
    result = run_canonical_analysis(
        AnalysisContext(
            events=events,
            infrastructure=store.get_infrastructure() or None,
            scenario_state=store.state.scenario,
            asset_inventory=store.get_asset_inventory() or None,
            asset_states=store.get_asset_states() or None,
            source="forecast",
            tick=store.get_tick(),
            scenario_id=store.state.scenario.scenario_id,
            scenario_name=store.state.scenario.scenario_name,
        )
    )
    return result.threats[0].threat_level.value if result.threats else "LOW"


# ---------------------------------------------------------------------------
# Core forecast functions
# ---------------------------------------------------------------------------


def forecast_baseline(horizon_ticks: int = 10) -> ForecastResult:
    """Forecast the current scenario forward with no perturbation."""
    engine = get_contact_engine()
    if engine._sim is None:
        return ForecastResult(
            summary="No scenario loaded. Load a scenario first.",
            expected_threat_trend="stable",
            based_on=[],
        )

    sim = _clone_sim(engine._sim)
    state = get_state_store().state

    threat_start = state.current_threat_level
    contacts_start = len(sim.entities)

    all_contacts: list[Any] = []
    for _ in range(horizon_ticks):
        contacts = sim.tick_forward()
        all_contacts.extend(contacts)

    threat_end = _estimate_threat_level(all_contacts)
    contacts_end = len(sim.entities)
    stimuli_fired = [s.get("action", "?") for s in sim.fired_stimuli_list]

    # Determine trend
    ts = _THREAT_ORDER.get(threat_start, 0)
    te = _THREAT_ORDER.get(threat_end, 0)
    if te > ts:
        trend = "increase"
    elif te < ts:
        trend = "decrease"
    else:
        trend = "stable"

    risks = []
    if any("cable_severance" in a for a in stimuli_fired):
        risks.append("Cable severance expected during forecast window")
    if any("jamming" in a for a in stimuli_fired):
        risks.append("Jamming event expected")
    if trend == "increase":
        risks.append("Threat level projected to increase")

    outcome_parts = []
    outcome_parts.append(f"Over {horizon_ticks} ticks (~{horizon_ticks * 2} min), threat level goes from {threat_start} to {threat_end}.")
    if stimuli_fired:
        unique_actions = sorted(set(stimuli_fired))
        outcome_parts.append(f"Expected stimuli: {', '.join(unique_actions)}")
    outcome_parts.append(f"{len(all_contacts)} contacts generated across {contacts_end} entities.")

    return ForecastResult(
        summary=f"Baseline forecast: {horizon_ticks}-tick projection with current state unchanged.",
        expected_threat_trend=trend,
        key_risks=risks,
        expected_outcome=" ".join(outcome_parts),
        confidence="medium",
        based_on=["simulation", "current_state"],
        tick_horizon=horizon_ticks,
        threat_level_start=threat_start,
        threat_level_end=threat_end,
        contacts_start=contacts_start,
        contacts_end=contacts_end,
        stimuli_fired=stimuli_fired,
    )


def forecast_with_event(
    event_action: str,
    event_entity: str | None = None,
    event_lat: float | None = None,
    event_lon: float | None = None,
    horizon_ticks: int = 10,
) -> ForecastResult:
    """Forecast with an injected event (e.g. cable severance, jamming)."""
    engine = get_contact_engine()
    if engine._sim is None:
        return ForecastResult(
            summary="No scenario loaded.",
            expected_threat_trend="stable",
            based_on=[],
        )

    sim = _clone_sim(engine._sim)
    state = get_state_store().state

    threat_start = state.current_threat_level

    # Inject the event as a trigger at the next tick
    trigger: dict[str, Any] = {
        "tick": sim.tick + 1,
        "action": event_action,
    }
    if event_entity:
        trigger["entity"] = event_entity
    if event_lat is not None:
        trigger["lat"] = event_lat
    if event_lon is not None:
        trigger["lon"] = event_lon
    if event_action == "jamming":
        trigger["radius_nm"] = 20

    sim._triggers.append(trigger)
    sim._triggers.sort(key=lambda t: t.get("tick", 0))

    all_contacts: list[Any] = []
    for _ in range(horizon_ticks):
        contacts = sim.tick_forward()
        all_contacts.extend(contacts)

    threat_end = _estimate_threat_level(all_contacts)
    stimuli_fired = [s.get("action", "?") for s in sim.fired_stimuli_list]

    ts = _THREAT_ORDER.get(threat_start, 0)
    te = _THREAT_ORDER.get(threat_end, 0)
    trend = "increase" if te > ts else ("decrease" if te < ts else "stable")

    risks = []
    if event_action == "cable_severance":
        risks.append("Cable infrastructure compromised")
        risks.append("Cable risk to secondary infrastructure increases")
    elif event_action == "jamming":
        risks.append("Communications degraded in AO")
        risks.append("Increased missed detection probability")

    baseline = forecast_baseline(horizon_ticks)

    if trend != baseline.expected_threat_trend:
        risks.append(f"Threat trend differs from baseline ({trend} vs {baseline.expected_threat_trend})")

    outcome_parts = [
        f"If '{event_action}' occurs next tick, over {horizon_ticks} ticks threat goes from {threat_start} to {threat_end}.",
        f"Baseline (no event): {threat_start} to {baseline.threat_level_end}.",
    ]
    if stimuli_fired:
        unique = sorted(set(stimuli_fired))
        outcome_parts.append(f"All stimuli fired: {', '.join(unique)}")

    return ForecastResult(
        summary=f"What-if forecast: '{event_action}' injected at tick {sim.tick + 1}.",
        expected_threat_trend=trend,
        key_risks=risks,
        expected_outcome=" ".join(outcome_parts),
        confidence="low",
        based_on=["simulation", "current_state", "hypothetical_event"],
        tick_horizon=horizon_ticks,
        threat_level_start=threat_start,
        threat_level_end=threat_end,
        contacts_start=len(sim.entities),
        contacts_end=len(sim.entities),
        stimuli_fired=stimuli_fired,
    )


def forecast_for_coa(coa_title: str, horizon_ticks: int = 10) -> ForecastResult:
    """Forecast outcome assuming a specific COA is chosen."""
    store = get_state_store()
    engine = get_contact_engine()

    if engine._sim is None:
        return ForecastResult(
            summary="No scenario loaded.",
            expected_threat_trend="stable",
            based_on=[],
        )

    scored = store.get_scored_coas()
    target = next((s for s in scored if s.coa.title.lower() == coa_title.lower()), None)
    if target is None:
        # Try partial match
        target = next((s for s in scored if coa_title.lower() in s.coa.title.lower()), None)
    if target is None:
        available = ", ".join(s.coa.title for s in scored)
        return ForecastResult(
            summary=f"COA '{coa_title}' not found. Available: {available}",
            expected_threat_trend="stable",
            based_on=[],
        )

    sim = _clone_sim(engine._sim)
    state = store.state
    threat_start = state.current_threat_level

    # Run baseline forward
    all_contacts: list[Any] = []
    for _ in range(horizon_ticks):
        contacts = sim.tick_forward()
        all_contacts.extend(contacts)

    threat_end_no_coa = _estimate_threat_level(all_contacts)
    stimuli_fired = [s.get("action", "?") for s in sim.fired_stimuli_list]

    # Estimate COA effect using simulation metrics
    sim_result = target.simulation
    success_p = sim_result.success_probability
    escalation_p = sim_result.escalation_probability
    cable_risk = sim_result.risk_to_second_cable
    missed_p = sim_result.missed_detection_probability
    feasibility = target.coa.feasibility_score
    time_to_effect = sim_result.expected_time_to_effect

    # COA effectiveness: weighted combination of success, escalation, cable risk, feasibility
    coa_effect_score = (
        success_p * 0.40
        + (1.0 - escalation_p) * 0.20
        + (1.0 - cable_risk) * 0.20
        + feasibility * 0.20
    )

    # Determine threat level adjustment based on COA effectiveness
    threat_end_idx = _THREAT_ORDER.get(threat_end_no_coa, 0)
    if coa_effect_score >= 0.7:
        # Highly effective COA: threat drops 1-2 steps
        reduction = 2 if coa_effect_score >= 0.85 and success_p > 0.7 else 1
        threat_end_idx = max(threat_end_idx - reduction, 0)
    elif coa_effect_score >= 0.5:
        # Moderately effective: threat drops one step
        threat_end_idx = max(threat_end_idx - 1, 0)
    elif coa_effect_score < 0.3:
        # Weak COA: no improvement or slight worsening
        if escalation_p > 0.3:
            threat_end_idx = min(threat_end_idx + 1, 3)
    threat_end = _THREAT_NAMES.get(threat_end_idx, threat_end_no_coa)

    ts = _THREAT_ORDER.get(threat_start, 0)
    te = _THREAT_ORDER.get(threat_end, 0)
    trend = "increase" if te > ts else ("decrease" if te < ts else "stable")

    risks = []
    if escalation_p > 0.3:
        risks.append(f"Escalation risk: {escalation_p:.0%}")
    if cable_risk > 0.2:
        risks.append(f"Cable risk remains: {cable_risk:.0%}")
    if missed_p > 0.3:
        risks.append(f"Detection gap: {missed_p:.0%} missed detection probability")
    if feasibility < 0.5:
        risks.append(f"Low feasibility: only {feasibility:.0%} asset support")
    if target.coa.roe_status != "allowed":
        risks.append(f"ROE restricted: {target.coa.roe_reason}")

    outcome_parts = [
        f"If '{target.coa.title}' (ROE: {target.coa.roe_status}) is executed,",
        f"success probability is {success_p:.0%} over {time_to_effect:.0f} min.",
        f"Threat level projection: {threat_start} to {threat_end} (without COA: {threat_end_no_coa}).",
        f"COA effectiveness score: {coa_effect_score:.0%}.",
    ]

    return ForecastResult(
        summary=f"COA forecast: '{target.coa.title}' — score {target.total_score:.1f}, success {success_p:.0%}.",
        expected_threat_trend=trend,
        key_risks=risks,
        expected_outcome=" ".join(outcome_parts),
        confidence="medium" if coa_effect_score > 0.4 else "low",
        based_on=["simulation", "current_state", "coa_scoring"],
        tick_horizon=horizon_ticks,
        threat_level_start=threat_start,
        threat_level_end=threat_end,
        contacts_start=len(sim.entities),
        contacts_end=len(sim.entities),
        stimuli_fired=stimuli_fired,
    )


# ---------------------------------------------------------------------------
# Question routing
# ---------------------------------------------------------------------------

def route_forecast_question(question: str) -> ForecastResult:
    """Parse a forecasting question and produce a structured forecast."""
    q = question.lower().strip()

    # Detect COA-specific questions
    coa_keywords = ("coa", "course of action")
    if any(kw in q for kw in coa_keywords):
        store = get_state_store()
        scored = store.get_scored_coas()
        for s in scored:
            if s.coa.title.lower() in q or s.coa.coa_id.lower() in q:
                return forecast_for_coa(s.coa.title)
        if "recommend" in q and scored:
            return forecast_for_coa(scored[0].coa.title)
        if scored:
            return forecast_for_coa(scored[0].coa.title)
        return ForecastResult(
            summary="No COAs available for forecasting. Run analysis first.",
            expected_threat_trend="stable",
            based_on=[],
        )

    # Detect event-specific questions — provide default coordinates
    event_keywords = {
        "cable": "cable_severance",
        "severance": "cable_severance",
        "cut": "cable_severance",
        "severed": "cable_severance",
        "jamming": "jamming",
        "jam": "jamming",
        "intercept": "course_change",
        "vessel reaches": "cable_severance",
        "reaches the cable": "cable_severance",
        "submarine surfaces": "surface",
        "speed burst": "speed_burst",
        "ais off": "ais_off",
        "goes dark": "ais_off",
    }
    for keyword, action in event_keywords.items():
        if keyword in q:
            # Get default coordinates from current contacts or scenario center
            default_lat, default_lon = 57.5, 19.0
            engine = get_contact_engine()
            if engine._sim and engine._sim.entities:
                # Use centroid of hostile entities
                hostile = [e for e in engine._sim.entities.values() if e.get("hostile")]
                if hostile:
                    default_lat = sum(e["lat"] for e in hostile) / len(hostile)
                    default_lon = sum(e["lon"] for e in hostile) / len(hostile)
            return forecast_with_event(action, event_lat=default_lat, event_lon=default_lon)

    # Default: baseline forecast
    horizon = 10
    if "30 minute" in q or "30 min" in q:
        horizon = 15
    elif "next" in q:
        # Try to extract a number
        import re
        nums = re.findall(r"(\d+)\s*tick", q)
        if nums:
            horizon = min(int(nums[0]), 30)
        else:
            horizon = 10

    return forecast_baseline(horizon)
