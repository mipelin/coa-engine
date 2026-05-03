"""Multi-step deterministic scenario forecasting (DIANA-style wargaming).

Simulates N future ticks, recomputes the full canonical pipeline at each step,
and produces a trajectory of threat, targets, COAs, and recommendations.

Constraints:
- No LLM calls in forecasting logic.
- No randomness — fully deterministic.
- Never mutates live engine state.
- Never authorizes engagement — advisory only.
"""

from __future__ import annotations

import copy
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from ..core.constants import EntityType, EventType
from ..core.schemas import (
    Contact,
    ContactType,
    CourseOfAction,
    OperationalEvent,
    Recommendation,
    ScoredCOA,
    ThreatResult,
)
from .analysis_service import AnalysisContext, AnalysisResult, run_canonical_analysis
from .contact_engine import SimulationScenario, get_contact_engine
from .fusion import FusedTrack
from .scenario_generator import ScenarioGenerator
from .state_store import StateStore, get_state_store
from .targeting import Target

logger = logging.getLogger("coa_engine.engine.forecasting")

# ---------------------------------------------------------------------------
# Forecast data structures
# ---------------------------------------------------------------------------

_FORECAST_KEYWORDS = (
    "what if", "what happens if", "if we choose", "if we pick",
    "how would", "forecast", "next", "ahead", "projected",
    "what would happen", "simulate", "how will threat",
)

_THREAT_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
_THREAT_NAMES = {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}

EARTH_RADIUS_KM = 6371.0


def is_forecast_question(question: str) -> bool:
    q = question.lower().strip()
    return any(kw in q for kw in _FORECAST_KEYWORDS)


@dataclass
class ForecastStep:
    """Snapshot of the full pipeline state at a single forecast tick."""
    tick_index: int
    timestamp: str
    contacts: int
    fused_tracks: list[dict[str, Any]] = field(default_factory=list)
    threats: list[dict[str, Any]] = field(default_factory=list)
    targets: list[dict[str, Any]] = field(default_factory=list)
    coas: list[dict[str, Any]] = field(default_factory=list)
    recommendation: dict[str, Any] | None = None
    threat_level: str = "LOW"
    key_changes: list[str] = field(default_factory=list)


@dataclass
class ForecastResult:
    """Full multi-step forecast output."""
    summary: str
    steps: list[ForecastStep] = field(default_factory=list)
    horizon: int = 0
    initial_state_snapshot: dict[str, Any] = field(default_factory=dict)
    final_state_summary: dict[str, Any] = field(default_factory=dict)
    threat_trend: list[str] = field(default_factory=list)
    recommendation_changes: list[dict[str, Any]] = field(default_factory=list)
    confidence: str = "medium"
    expected_threat_trend: str = "stable"
    key_risks: list[str] = field(default_factory=list)
    expected_outcome: str = ""
    based_on: list[str] = field(default_factory=list)
    tick_horizon: int = 0
    threat_level_start: str = "LOW"
    threat_level_end: str = "LOW"
    contacts_start: int = 0
    contacts_end: int = 0
    stimuli_fired: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Legacy structure kept for backward-compatible API consumers
# ---------------------------------------------------------------------------

# (ForecastResult above already carries the legacy fields)

# ---------------------------------------------------------------------------
# Scenario cloning
# ---------------------------------------------------------------------------


def _clone_sim(scenario: SimulationScenario) -> SimulationScenario:
    clone = copy.deepcopy(scenario)
    clone._process_trigger_as_event = lambda *a, **kw: None
    clone._update_stimuli_counts = lambda *a, **kw: None
    return clone


# ---------------------------------------------------------------------------
# Contact / entity propagation
# ---------------------------------------------------------------------------


def _propagate_contacts(
    contacts: list[Contact],
    delta_minutes: float = 2.0,
) -> list[Contact]:
    """Advance all contacts by delta_minutes using velocity * time.

    Deterministic: position += velocity * time, heading/speed maintained.
    """
    propagated = []
    for c in contacts:
        speed_m_per_min = c.speed * 1852.0 / 60.0  # knots -> m/min
        distance_m = speed_m_per_min * delta_minutes
        heading_rad = math.radians(c.heading or 0.0)
        lat_rad = math.radians(c.lat)
        dlat = (distance_m * math.cos(heading_rad)) / 111320.0
        dlon = (distance_m * math.sin(heading_rad)) / (111320.0 * math.cos(lat_rad)) if abs(lat_rad) < math.pi / 2 - 0.01 else 0.0
        new_lat = c.lat + dlat
        new_lon = c.lon + dlon
        new_ts = c.timestamp + timedelta(minutes=delta_minutes)
        propagated.append(Contact(
            contact_id=f"{c.contact_id}-f",
            timestamp=new_ts,
            source=c.source,
            contact_type=c.contact_type,
            lat=round(new_lat, 6),
            lon=round(new_lon, 6),
            speed=c.speed,
            heading=c.heading,
            confidence=c.confidence,
            entity_id=c.entity_id,
            is_hostile=c.is_hostile,
            attributes=dict(c.attributes),
        ))
    return propagated


# ---------------------------------------------------------------------------
# What-if event injection
# ---------------------------------------------------------------------------

_EVENT_ACTION_MAP: dict[str, dict[str, Any]] = {
    "cable_severance": {
        "event_type": EventType.CABLE_SEVERANCE,
        "entity_type": EntityType.INFRASTRUCTURE,
        "description": "Hypothetical cable severance event",
        "contact_type": ContactType.CABLE_EVENT,
    },
    "jamming": {
        "event_type": EventType.JAMMING_DETECTED,
        "entity_type": EntityType.SUSPICIOUS_VESSEL,
        "description": "Hypothetical jamming event",
        "contact_type": ContactType.JAMMING,
    },
    "new_hostile": {
        "event_type": EventType.VESSEL_POSITION,
        "entity_type": EntityType.SUSPICIOUS_VESSEL,
        "description": "Hypothetical new hostile contact",
        "contact_type": ContactType.VESSEL,
        "is_hostile": True,
    },
    "asset_protection": {
        "event_type": EventType.OPERATIONAL_REPORT,
        "entity_type": EntityType.INFRASTRUCTURE,
        "description": "Hypothetical asset protection request",
        "contact_type": ContactType.INFRASTRUCTURE,
    },
}


def _make_injected_events(
    action: str,
    entity_id: str = "hypothetical-001",
    lat: float = 57.5,
    lon: float = 19.0,
    tick_time: datetime | None = None,
) -> list[OperationalEvent]:
    """Create deterministic OperationalEvents for a what-if injection."""
    mapping = _EVENT_ACTION_MAP.get(action, _EVENT_ACTION_MAP["new_hostile"])
    ts = tick_time or datetime.now(timezone.utc)
    event = OperationalEvent(
        event_id=f"whatif-{action}-{entity_id}",
        timestamp=ts,
        event_type=mapping["event_type"],
        source="forecast_injection",
        confidence=0.75,
        lat=lat,
        lon=lon,
        entity_id=entity_id,
        entity_type=mapping["entity_type"],
        description=mapping["description"],
        attributes={"speed_knots": 10.0, "heading": 180.0, "injected": True},
        is_threat_candidate=True,
        is_infrastructure=False,
    )
    events = [event]
    if action == "jamming":
        events.append(OperationalEvent(
            event_id=f"whatif-jamming-sigint-{entity_id}",
            timestamp=ts,
            event_type=EventType.JAMMING_DETECTED,
            source="sigint",
            confidence=0.85,
            lat=lat + 0.01,
            lon=lon - 0.01,
            entity_id=entity_id,
            entity_type=EntityType.SUSPICIOUS_VESSEL,
            description="SIGINT correlated jamming detection",
            attributes={"speed_knots": 0.0, "heading": 0.0, "radius_nm": 20, "injected": True},
            is_threat_candidate=True,
        ))
    return events


def _make_injected_contacts(
    action: str,
    entity_id: str = "hypothetical-001",
    lat: float = 57.5,
    lon: float = 19.0,
    tick_time: datetime | None = None,
) -> list[Contact]:
    """Create deterministic Contacts for a what-if injection."""
    mapping = _EVENT_ACTION_MAP.get(action, _EVENT_ACTION_MAP["new_hostile"])
    ts = tick_time or datetime.now(timezone.utc)
    contact = Contact(
        contact_id=f"whatif-{action}-{entity_id}",
        timestamp=ts,
        source="forecast_injection",
        contact_type=mapping["contact_type"],
        lat=lat,
        lon=lon,
        speed=10.0,
        heading=180.0,
        confidence=0.75,
        entity_id=entity_id,
        is_hostile=mapping.get("is_hostile", False),
        attributes={"injected": True, "allegiance": "hostile"},
    )
    return [contact]


# ---------------------------------------------------------------------------
# Change tracking
# ---------------------------------------------------------------------------


def _compute_key_changes(
    prev_step: ForecastStep | None,
    result: AnalysisResult | None,
) -> list[str]:
    """Compare current pipeline output to previous step and list changes."""
    changes: list[str] = []

    if result is None:
        return changes

    threats = result.threats
    current_level = threats[0].threat_level.value if threats else "LOW"

    if prev_step is None:
        if current_level != "LOW":
            changes.append(f"Initial threat level: {current_level}")
        if threats:
            changes.append(f"{len(threats)} threats identified")
        return changes

    # Threat level change
    if current_level != prev_step.threat_level:
        changes.append(f"Threat level changed: {prev_step.threat_level} -> {current_level}")

    # New high-priority targets
    prev_target_ids = {t["id"] for t in prev_step.targets}
    new_high = [
        t for t in result.targets
        if t.id not in prev_target_ids and t.priority_level in ("HIGH", "CRITICAL")
    ]
    if new_high:
        changes.append(f"New high-priority targets: {', '.join(t.id for t in new_high)}")

    # New fused sources
    prev_fused_ids = {ft["track_id"] for ft in prev_step.fused_tracks}
    new_fused = [ft for ft in result.fused_tracks if ft.track_id not in prev_fused_ids]
    if new_fused:
        changes.append(f"New fused tracks: {len(new_fused)}")

    # Recommendation change
    rec = result.recommendation
    if rec and rec.recommended:
        new_coa_id = rec.recommended.coa.coa_id
        prev_rec = prev_step.recommendation
        prev_coa_id = prev_rec.get("coa_id") if prev_rec else None
        if new_coa_id != prev_coa_id:
            changes.append(f"Recommendation changed to: {rec.recommended.coa.title}")

    # ROE status shift
    if rec and rec.recommended:
        new_roe = rec.recommended.coa.roe_status
        prev_roe = prev_step.recommendation.get("roe_status") if prev_step.recommendation else None
        if new_roe != prev_roe:
            changes.append(f"ROE status shifted: {prev_roe} -> {new_roe}")

    return changes


# ---------------------------------------------------------------------------
# Trend extraction
# ---------------------------------------------------------------------------


def _compute_confidence(steps: list[ForecastStep]) -> str:
    """Deterministic confidence heuristic."""
    if len(steps) < 2:
        return "low"

    source_count = sum(s.contacts for s in steps) / len(steps)
    threat_levels = [_THREAT_ORDER.get(s.threat_level, 0) for s in steps]

    # Stable tracks: threat level doesn't fluctuate
    level_changes = sum(
        1 for i in range(1, len(threat_levels))
        if threat_levels[i] != threat_levels[i - 1]
    )

    score = 0.0
    # More sources -> higher confidence
    if source_count >= 5:
        score += 0.3
    elif source_count >= 3:
        score += 0.2
    else:
        score += 0.1

    # Stable -> higher confidence
    stability = 1.0 - (level_changes / max(len(threat_levels) - 1, 1))
    score += stability * 0.4

    # Multiple fused sources
    avg_fused = sum(len(s.fused_tracks) for s in steps) / len(steps)
    if avg_fused >= 3:
        score += 0.3
    elif avg_fused >= 1:
        score += 0.15

    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Helper: convert analysis result to step dicts
# ---------------------------------------------------------------------------


def _threat_to_dict(t: ThreatResult) -> dict[str, Any]:
    return {
        "entity_id": t.entity_id,
        "threat_probability": round(t.threat_probability, 3),
        "threat_level": t.threat_level.value,
        "confidence": round(t.confidence, 3),
        "main_drivers": t.main_drivers[:3],
    }


def _target_to_dict(t: Target) -> dict[str, Any]:
    return t.to_dict()


def _fused_to_dict(ft: FusedTrack) -> dict[str, Any]:
    return ft.to_dict()


def _coa_to_dict(s: ScoredCOA) -> dict[str, Any]:
    return {
        "coa_id": s.coa.coa_id,
        "title": s.coa.title,
        "rank": s.rank,
        "total_score": round(s.total_score, 1),
        "roe_status": s.coa.roe_status,
    }


def _recommendation_to_dict(rec: Recommendation | None) -> dict[str, Any] | None:
    if not rec or not rec.recommended:
        return None
    return {
        "coa_id": rec.recommended.coa.coa_id,
        "title": rec.recommended.coa.title,
        "score": round(rec.recommended.total_score, 1),
        "roe_status": rec.recommended.coa.roe_status,
        "roe_reason": rec.recommended.coa.roe_reason,
    }


# ---------------------------------------------------------------------------
# Core multi-step forecast
# ---------------------------------------------------------------------------


def run_forecast(
    context: AnalysisContext,
    *,
    horizon: int = 5,
    delta_minutes: float = 2.0,
    injected_events: list[OperationalEvent] | None = None,
    injected_contacts: list[Contact] | None = None,
) -> ForecastResult:
    """Run a multi-step deterministic forecast through the full pipeline.

    For each of N steps:
    1. Propagate contacts forward by delta_minutes.
    2. Optionally inject what-if events/contacts at step 0.
    3. Run the full canonical analysis pipeline.
    4. Record all outputs and track changes.

    Never mutates the input context or live engine state.
    """
    # Clone inputs to prevent mutation
    events_accumulator = list(context.events)
    contacts_current = list(context.active_contacts or [])
    infrastructure = list(context.infrastructure or []) if context.infrastructure else None

    steps: list[ForecastStep] = []
    threat_trend: list[str] = []
    recommendation_changes: list[dict[str, Any]] = []

    prev_rec_coa_id: str | None = None
    store = get_state_store()
    base_tick = store.get_tick()

    for tick_idx in range(horizon):
        # Propagate contacts
        contacts_current = _propagate_contacts(contacts_current, delta_minutes=delta_minutes)

        # Inject what-if at step 0
        if tick_idx == 0:
            if injected_events:
                events_accumulator = events_accumulator + injected_events
            if injected_contacts:
                contacts_current = contacts_current + injected_contacts

        # Convert propagated contacts to OperationalEvents for pipeline
        contact_events = [
            StateStore._contact_to_operational_event(c) for c in contacts_current
        ]
        all_events = events_accumulator + contact_events

        # Run full canonical analysis
        step_context = AnalysisContext(
            events=all_events,
            infrastructure=infrastructure,
            scenario_state=context.scenario_state,
            asset_inventory=context.asset_inventory,
            asset_states=context.asset_states,
            active_contacts=contacts_current,
            source="forecast",
            tick=base_tick + tick_idx + 1,
            scenario_id=context.scenario_id,
            scenario_name=context.scenario_name,
        )
        result = run_canonical_analysis(step_context)

        # Determine threat level
        threat_level = result.threats[0].threat_level.value if result.threats else "LOW"
        threat_trend.append(threat_level)

        # Track recommendation changes
        rec = result.recommendation
        rec_coa_id = rec.recommended.coa.coa_id if rec and rec.recommended else None
        if rec_coa_id != prev_rec_coa_id:
            recommendation_changes.append({
                "tick_index": tick_idx,
                "from_coa_id": prev_rec_coa_id,
                "to_coa_id": rec_coa_id,
                "to_title": rec.recommended.coa.title if rec and rec.recommended else None,
                "reason": f"Pipeline recomputed at forecast step {tick_idx}",
            })
        prev_rec_coa_id = rec_coa_id

        # Compute key changes
        prev_step = steps[-1] if steps else None
        key_changes = _compute_key_changes(prev_step, result)

        # Build step snapshot
        step = ForecastStep(
            tick_index=tick_idx,
            timestamp=f"T+{(tick_idx + 1) * delta_minutes:.0f}min",
            contacts=len(contacts_current),
            fused_tracks=[_fused_to_dict(ft) for ft in result.fused_tracks],
            threats=[_threat_to_dict(t) for t in result.threats],
            targets=[_target_to_dict(t) for t in result.targets],
            coas=[_coa_to_dict(s) for s in result.scored_coas],
            recommendation=_recommendation_to_dict(result.recommendation),
            threat_level=threat_level,
            key_changes=key_changes,
        )
        steps.append(step)

    # Compute overall trend
    if len(threat_trend) >= 2:
        first = _THREAT_ORDER.get(threat_trend[0], 0)
        last = _THREAT_ORDER.get(threat_trend[-1], 0)
        if last > first:
            trend = "increase"
        elif last < first:
            trend = "decrease"
        else:
            trend = "stable"
    else:
        trend = "stable"

    # Compute confidence
    confidence = _compute_confidence(steps)

    # Build initial state snapshot
    initial_state = {
        "tick": base_tick,
        "threat_level": steps[0].threat_level if steps else "LOW",
        "contacts": steps[0].contacts if steps else 0,
        "scenario_id": context.scenario_id,
    }

    # Build final state summary
    final_step = steps[-1] if steps else None
    final_state = {
        "tick_index": final_step.tick_index if final_step else 0,
        "threat_level": final_step.threat_level if final_step else "LOW",
        "contacts": final_step.contacts if final_step else 0,
        "coas_count": len(final_step.coas) if final_step else 0,
        "recommendation": final_step.recommendation if final_step else None,
    } if final_step else {}

    # Build summary text
    threat_start = steps[0].threat_level if steps else "LOW"
    threat_end = steps[-1].threat_level if steps else "LOW"
    outcome_parts = [
        f"Multi-step forecast ({horizon} steps, ~{horizon * delta_minutes:.0f} min): "
        f"threat trajectory {threat_start} -> {threat_end} ({trend}).",
    ]
    if injected_events or injected_contacts:
        outcome_parts.append("What-if event injected at step 0.")
    if recommendation_changes:
        changes_text = "; ".join(
            f"Step {c['tick_index']}: -> {c['to_title'] or 'none'}"
            for c in recommendation_changes
        )
        outcome_parts.append(f"Recommendation changes: {changes_text}")

    risks = []
    if trend == "increase":
        risks.append("Threat level projected to increase")
    critical_steps = [s for s in steps if s.threat_level == "CRITICAL"]
    if critical_steps:
        risks.append(f"CRITICAL threat reached at {len(critical_steps)} step(s)")

    return ForecastResult(
        summary=f"Multi-step forecast: {horizon}-step projection, trend={trend}, confidence={confidence}.",
        steps=steps,
        horizon=horizon,
        initial_state_snapshot=initial_state,
        final_state_summary=final_state,
        threat_trend=threat_trend,
        recommendation_changes=recommendation_changes,
        confidence=confidence,
        expected_threat_trend=trend,
        key_risks=risks,
        expected_outcome=" ".join(outcome_parts),
        based_on=["simulation", "canonical_pipeline", "current_state"],
        tick_horizon=horizon,
        threat_level_start=threat_start,
        threat_level_end=threat_end,
        contacts_start=steps[0].contacts if steps else 0,
        contacts_end=steps[-1].contacts if steps else 0,
        stimuli_fired=[],
    )


# ---------------------------------------------------------------------------
# High-level forecast entry points
# ---------------------------------------------------------------------------


def _build_analysis_context() -> AnalysisContext | None:
    """Build an AnalysisContext from current live engine state."""
    store = get_state_store()
    engine = get_contact_engine()

    contacts = store.get_contacts()
    if not contacts:
        return None

    events = store.contacts_as_events()
    return AnalysisContext(
        events=events,
        infrastructure=store.get_infrastructure() or None,
        scenario_state=store.state.scenario,
        asset_inventory=store.get_asset_inventory() or None,
        asset_states=store.get_asset_states() or None,
        active_contacts=contacts,
        source="forecast",
        tick=store.get_tick(),
        scenario_id=store.state.scenario.scenario_id,
        scenario_name=store.state.scenario.scenario_name,
    )


def forecast_baseline(horizon_ticks: int = 10) -> ForecastResult:
    """Forecast the current scenario forward with no perturbation.

    Uses multi-step pipeline if contacts are available; falls back to
    simulation-based approach otherwise.
    """
    context = _build_analysis_context()
    if context is not None:
        return run_forecast(context, horizon=horizon_ticks, delta_minutes=2.0)

    # Fallback: simulation-based (no contacts in live state)
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

    threat_end = _estimate_threat_level_sim(all_contacts)
    contacts_end = len(sim.entities)
    stimuli_fired = [s.get("action", "?") for s in sim.fired_stimuli_list]

    ts = _THREAT_ORDER.get(threat_start, 0)
    te = _THREAT_ORDER.get(threat_end, 0)
    trend = "increase" if te > ts else ("decrease" if te < ts else "stable")

    risks = []
    if any("cable_severance" in a for a in stimuli_fired):
        risks.append("Cable severance expected during forecast window")
    if any("jamming" in a for a in stimuli_fired):
        risks.append("Jamming event expected")
    if trend == "increase":
        risks.append("Threat level projected to increase")

    outcome_parts = [
        f"Over {horizon_ticks} ticks (~{horizon_ticks * 2} min), threat level goes from {threat_start} to {threat_end}.",
    ]
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
    """Forecast with an injected what-if event at step 0.

    Runs through the full canonical pipeline at each step.
    """
    context = _build_analysis_context()
    if context is not None:
        lat = event_lat or 57.5
        lon = event_lon or 19.0
        entity_id = event_entity or "hypothetical-001"
        tick_time = datetime.now(timezone.utc)

        injected_events = _make_injected_events(
            event_action, entity_id=entity_id, lat=lat, lon=lon, tick_time=tick_time,
        )
        injected_contacts = _make_injected_contacts(
            event_action, entity_id=entity_id, lat=lat, lon=lon, tick_time=tick_time,
        )
        return run_forecast(
            context,
            horizon=horizon_ticks,
            injected_events=injected_events,
            injected_contacts=injected_contacts,
        )

    # Fallback: simulation-based
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

    trigger: dict[str, Any] = {"tick": sim.tick + 1, "action": event_action}
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

    threat_end = _estimate_threat_level_sim(all_contacts)
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

    scored = store.get_scored_coas()
    target_coa = next((s for s in scored if s.coa.title.lower() == coa_title.lower()), None)
    if target_coa is None:
        target_coa = next((s for s in scored if coa_title.lower() in s.coa.title.lower()), None)
    if target_coa is None:
        available = ", ".join(s.coa.title for s in scored)
        return ForecastResult(
            summary=f"COA '{coa_title}' not found. Available: {available}",
            expected_threat_trend="stable",
            based_on=[],
        )

    # Run baseline multi-step forecast
    context = _build_analysis_context()
    baseline = forecast_baseline(horizon_ticks) if context is None else run_forecast(context, horizon=horizon_ticks)

    # Estimate COA effect
    sim_result = target_coa.simulation
    success_p = sim_result.success_probability
    escalation_p = sim_result.escalation_probability
    cable_risk = sim_result.risk_to_second_cable
    missed_p = sim_result.missed_detection_probability
    feasibility = target_coa.coa.feasibility_score
    time_to_effect = sim_result.expected_time_to_effect

    coa_effect_score = (
        success_p * 0.40
        + (1.0 - escalation_p) * 0.20
        + (1.0 - cable_risk) * 0.20
        + feasibility * 0.20
    )

    threat_end_no_coa = baseline.threat_level_end
    threat_end_idx = _THREAT_ORDER.get(threat_end_no_coa, 0)
    if coa_effect_score >= 0.7:
        reduction = 2 if coa_effect_score >= 0.85 and success_p > 0.7 else 1
        threat_end_idx = max(threat_end_idx - reduction, 0)
    elif coa_effect_score >= 0.5:
        threat_end_idx = max(threat_end_idx - 1, 0)
    elif coa_effect_score < 0.3:
        if escalation_p > 0.3:
            threat_end_idx = min(threat_end_idx + 1, 3)
    threat_end = _THREAT_NAMES.get(threat_end_idx, threat_end_no_coa)

    threat_start = baseline.threat_level_start
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
    if target_coa.coa.roe_status != "allowed":
        risks.append(f"ROE restricted: {target_coa.coa.roe_reason}")

    outcome_parts = [
        f"If '{target_coa.coa.title}' (ROE: {target_coa.coa.roe_status}) is executed,",
        f"success probability is {success_p:.0%} over {time_to_effect:.0f} min.",
        f"Threat level projection: {threat_start} to {threat_end} (without COA: {threat_end_no_coa}).",
        f"COA effectiveness score: {coa_effect_score:.0%}.",
    ]

    result = ForecastResult(
        summary=f"COA forecast: '{target_coa.coa.title}' — score {target_coa.total_score:.1f}, success {success_p:.0%}.",
        steps=baseline.steps,
        horizon=baseline.horizon,
        initial_state_snapshot=baseline.initial_state_snapshot,
        final_state_summary=baseline.final_state_summary,
        threat_trend=baseline.threat_trend,
        recommendation_changes=baseline.recommendation_changes,
        confidence="medium" if coa_effect_score > 0.4 else "low",
        expected_threat_trend=trend,
        key_risks=risks,
        expected_outcome=" ".join(outcome_parts),
        based_on=["simulation", "current_state", "coa_scoring"],
        tick_horizon=horizon_ticks,
        threat_level_start=threat_start,
        threat_level_end=threat_end,
        contacts_start=baseline.contacts_start,
        contacts_end=baseline.contacts_end,
        stimuli_fired=baseline.stimuli_fired,
    )
    return result


# ---------------------------------------------------------------------------
# Simulation-based threat estimation (fallback path)
# ---------------------------------------------------------------------------


def _estimate_threat_level_sim(contacts: list[Any]) -> str:
    """Estimate threat level through the canonical analysis pipeline."""
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
# Question routing
# ---------------------------------------------------------------------------


def route_forecast_question(question: str) -> ForecastResult:
    """Parse a forecasting question and produce a structured forecast."""
    q = question.lower().strip()

    # COA-specific questions
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

    # Event-specific questions
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
            default_lat, default_lon = 57.5, 19.0
            engine = get_contact_engine()
            if engine._sim and engine._sim.entities:
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
        import re
        nums = re.findall(r"(\d+)\s*tick", q)
        if nums:
            horizon = min(int(nums[0]), 30)

    return forecast_baseline(horizon)
