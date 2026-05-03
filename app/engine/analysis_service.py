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
from .anomaly_detection import detect_anomalies
from .coa_generation import generate_coas
from .entity_tracking import build_tracks
from .feature_engineering import compute_features
from .recommendation import recommend
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
    threats: list[ThreatResult] = field(default_factory=list)
    coas: list[CourseOfAction] = field(default_factory=list)
    simulations: list[SimulationResult] = field(default_factory=list)
    scored_coas: list[ScoredCOA] = field(default_factory=list)
    recommendation: Recommendation | None = None
    tracks: dict[str, TrackInfo] = field(default_factory=dict)
    temporal: TemporalSummary | None = None
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
        if include_tracks:
            result.tracks = {}
        if include_temporal:
            result.temporal = analyze_temporal_patterns([])
        return result

    features = compute_features(events, context.infrastructure or None)
    anomalies = detect_anomalies(events, features)
    threats = assess_threats(events, features, anomalies)
    coas = generate_coas(
        events,
        threats,
        context.asset_inventory,
        context.asset_states,
        active_contacts=context.active_contacts,
    )
    simulations = run_simulations(coas, events, threats, context.scenario_state)
    scored = score_coas(coas, simulations)

    top_threat_confidence = threats[0].confidence if threats else 0.8
    scored = evaluate_roe(scored, threats, confidence=top_threat_confidence)
    recommendable = [item for item in scored if item.coa.roe_status != "rejected"]
    recommendation = recommend(
        recommendable,
        asset_states=context.asset_states,
        asset_inventory=context.asset_inventory,
    )

    result.features = features
    result.anomalies = anomalies
    result.threats = threats
    result.coas = coas
    result.simulations = simulations
    result.scored_coas = scored
    result.recommendation = recommendation
    if include_tracks:
        result.tracks = build_tracks(events)
    if include_temporal:
        result.temporal = analyze_temporal_patterns(events)

    logger.info(
        "Canonical analysis: source=%s tick=%s events=%d threats=%d coas=%d recommendation=%s",
        context.source,
        context.tick,
        len(events),
        len(threats),
        len(scored),
        recommendation.recommended.coa.coa_id if recommendation and recommendation.recommended else None,
    )
    return result

