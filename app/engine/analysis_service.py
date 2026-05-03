from __future__ import annotations

"""Canonical DIANA analysis pipeline.

This module is the single owner for deterministic analysis:
features -> anomalies -> threats -> COAs -> simulation -> scoring -> ROE -> recommendation.

It intentionally performs no LLM calls and does not mutate engine state. Callers that
need to persist results into StateStore must do that explicitly after this service returns.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from ..core.schemas import (
    AnomalyResult,
    AssetState,
    Contact,
    CourseOfAction,
    FeatureVector,
    OperationalEvent,
    Recommendation,
    ScenarioState,
    ScoredCOA,
    SimulationResult,
    TemporalSummary,
    ThreatResult,
    TrackInfo,
)
from .fusion import FusedTrack, build_fused_tracks
from .isr_simulation import simulate_isr_observations
from .targeting import Target, build_targets
from .anomaly_detection import detect_anomalies
from .coa_generation import generate_coas
from .coa_optimizer import OptimizationResult, optimize_coas
from .entity_tracking import build_tracks
from .feature_engineering import compute_features
from .recommendation import recommend
from .operational_effects import (
    OperationalEffects,
    apply_effects_to_features,
    apply_effects_to_feasibility,
    apply_effects_to_simulation,
    compute_operational_effects,
    infer_jamming_intensity,
)
from .roe_engine import evaluate_roe
from .scoring import score_coas
from .simulation import run_simulations
from .threat_assessment import assess_threats
from .time_series import analyze_temporal_patterns

logger = logging.getLogger("coa_engine.engine.analysis_service")


@dataclass
class AnalysisContext:
    events: list[OperationalEvent]
    infrastructure: list[dict[str, Any]] | None = None
    scenario_state: ScenarioState | None = None
    asset_inventory: dict[str, int] | None = None
    asset_states: list[AssetState] | None = None
    active_contacts: list[Contact] | None = None
    source: str = "unknown"
    tick: int | None = None
    scenario_id: str | None = None
    scenario_name: str | None = None


@dataclass
class AnalysisResult:
    context: AnalysisContext
    features: list[FeatureVector] = field(default_factory=list)
    anomalies: list[AnomalyResult] = field(default_factory=list)
    fused_tracks: list[FusedTrack] = field(default_factory=list)
    threats: list[ThreatResult] = field(default_factory=list)
    targets: list[Target] = field(default_factory=list)
    top_targets: list[Target] = field(default_factory=list)
    coas: list[CourseOfAction] = field(default_factory=list)
    simulations: list[SimulationResult] = field(default_factory=list)
    scored_coas: list[ScoredCOA] = field(default_factory=list)
    recommendation: Recommendation | None = None
    tracks: dict[str, TrackInfo] = field(default_factory=dict)
    temporal: TemporalSummary | None = None
    coa_optimization: OptimizationResult | None = None
    operational_effects: OperationalEffects | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def run_canonical_analysis(
    context: AnalysisContext,
    *,
    include_tracks: bool = False,
    include_temporal: bool = False,
) -> AnalysisResult:
    """Run the one canonical deterministic analysis pipeline.

    The pipeline matches live event-loop behavior: ROE is evaluated before
    recommendation, and rejected COAs are excluded from recommendation selection.
    """
    events = list(context.events)
    result = AnalysisResult(
        context=context,
        metadata={
            "source": context.source,
            "tick": context.tick,
            "scenario_id": context.scenario_id,
            "scenario_name": context.scenario_name,
            "events_processed": len(events),
            "canonical_pipeline": True,
        },
    )

    if not events:
        result.recommendation = recommend(
            [],
            asset_states=context.asset_states,
            asset_inventory=context.asset_inventory,
        )
        result.coa_optimization = optimize_coas(
            [], events, [], scenario_state=context.scenario_state,
            asset_inventory=context.asset_inventory,
            asset_states=context.asset_states,
        )
        result.operational_effects = compute_operational_effects(
            context.scenario_state.environment if context.scenario_state else None,
        )
        if include_tracks:
            result.tracks = {}
        if include_temporal:
            result.temporal = analyze_temporal_patterns([])
        return result

    features = compute_features(events, context.infrastructure or None)
    anomalies = detect_anomalies(events, features)
    isr_observations = simulate_isr_observations(
        tick=context.tick or 0,
        contacts=context.active_contacts,
        events=events,
        infrastructure=context.infrastructure or None,
        seed=context.scenario_state.seed if context.scenario_state and context.scenario_state.seed is not None else None,
    )
    fused_tracks = build_fused_tracks(
        events=events,
        contacts=context.active_contacts,
        observations=isr_observations,
        anomalies=anomalies,
        features=features,
    )
    threats = assess_threats(events, features, anomalies, fused_tracks=fused_tracks)
    fused_tracks = build_fused_tracks(
        events=events,
        contacts=context.active_contacts,
        observations=isr_observations,
        anomalies=anomalies,
        threats=threats,
        features=features,
    )
    targets = build_targets(
        context,
        features=features,
        anomalies=anomalies,
        threats=threats,
        fused_tracks=fused_tracks,
    )
    coas = generate_coas(
        events,
        threats,
        context.asset_inventory,
        context.asset_states,
        active_contacts=context.active_contacts,
    )

    # --- Operational effects ---
    env = context.scenario_state.environment if context.scenario_state else None
    jamming = infer_jamming_intensity(events)
    effects = compute_operational_effects(env, jamming_intensity=jamming)

    # Apply to features (confidence adjustments)
    if effects.overall_effectiveness < 0.99:
        features = apply_effects_to_features(features, effects)
        anomalies = detect_anomalies(events, features)
        threats = assess_threats(events, features, anomalies, fused_tracks=fused_tracks)

    # Apply to COA feasibility
    if effects.feasibility_modifier < 0.99:
        coas = [apply_effects_to_feasibility(c, effects) for c in coas]

    simulations = run_simulations(coas, events, threats, context.scenario_state)

    # Apply to simulation results
    if effects.overall_effectiveness < 0.99:
        sim_map = {s.coa_id: s for s in simulations}
        simulations = [apply_effects_to_simulation(c, sim_map.get(c.coa_id), effects) or sim_map.get(c.coa_id) for c in coas if sim_map.get(c.coa_id)]

    scored = score_coas(coas, simulations)

    top_threat_confidence = threats[0].confidence if threats else 0.8
    scored = evaluate_roe(scored, threats, confidence=top_threat_confidence)
    recommendable = [item for item in scored if item.coa.roe_status != "rejected"]
    recommendation = recommend(
        recommendable,
        asset_states=context.asset_states,
        asset_inventory=context.asset_inventory,
    )

    # COA optimization — generate variants, simulate, score, ROE, rank
    coa_optimization = optimize_coas(
        base_coas=coas,
        events=events,
        threats=threats,
        scenario_state=context.scenario_state,
        asset_inventory=context.asset_inventory,
        asset_states=context.asset_states,
    )

    result.features = features
    result.anomalies = anomalies
    result.fused_tracks = fused_tracks
    result.threats = threats
    result.targets = targets
    result.top_targets = targets[:5]
    result.coas = coas
    result.simulations = simulations
    result.scored_coas = scored
    result.recommendation = recommendation
    result.coa_optimization = coa_optimization
    result.operational_effects = effects
    result.metadata["isr_observations"] = len(isr_observations)
    if include_tracks:
        result.tracks = build_tracks(events)
    if include_temporal:
        result.temporal = analyze_temporal_patterns(events)

    logger.info(
        "Canonical analysis: source=%s tick=%s events=%d isr_obs=%d fused_tracks=%d threats=%d targets=%d coas=%d coa_variants=%d recommendation=%s opfx=%.2f",
        context.source,
        context.tick,
        len(events),
        len(isr_observations),
        len(fused_tracks),
        len(threats),
        len(targets),
        len(scored),
        len(coa_optimization.optimized_variants) if coa_optimization else 0,
        recommendation.recommended.coa.coa_id if recommendation and recommendation.recommended else None,
        effects.overall_effectiveness,
    )
    return result
