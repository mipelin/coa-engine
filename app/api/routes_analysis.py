import logging

from fastapi import APIRouter

from ..core.session import get_session
from ..core.schemas import AnalysisRequest
from ..engine.analysis_service import AnalysisContext, run_canonical_analysis
from ..engine.coa_optimizer import OptimizationResult
from ..engine.fusion import serialize_fused_tracks
from ..engine.state_store import get_state_store
from ..engine.targeting import serialize_targets

router = APIRouter(prefix="/analysis", tags=["analysis"])

logger = logging.getLogger("coa_engine.api.analysis")


def _serialize_optimization(opt: OptimizationResult | None) -> dict | None:
    if opt is None:
        return None
    return {
        "optimized_variants": [s.model_dump(mode="json") for s in opt.optimized_variants],
        "variant_parameters": opt.variant_parameters,
        "best_variant": opt.best_variant.model_dump(mode="json") if opt.best_variant else None,
        "robustness_ranking": opt.robustness_ranking,
        "optimization_summary": opt.optimization_summary,
    }


def _get_events(request: AnalysisRequest) -> list:
    """Resolve events from request, session, or default."""
    if request.events:
        return request.events
    session = get_session()
    if request.use_session:
        events = session.get_events()
        if events:
            return events
    from ..engine.event_ingestion import load_scenario_events
    return load_scenario_events()


def _get_infrastructure(request: AnalysisRequest) -> list[dict] | None:
    """Get infrastructure from the loaded scenario."""
    session = get_session()
    scenario = session.get_scenario()
    if scenario and scenario.critical_infrastructure:
        return [ci.model_dump() for ci in scenario.critical_infrastructure]
    return None


@router.post("/run")
async def run_analysis(request: AnalysisRequest):
    """Run full analysis pipeline: features, anomalies, threats, tracks, temporal."""
    events = _get_events(request)
    infrastructure = _get_infrastructure(request)
    session = get_session()
    scenario = session.get_scenario()
    store = get_state_store()
    result = run_canonical_analysis(
        AnalysisContext(
            events=events,
            infrastructure=infrastructure,
            scenario_state=store.state.scenario,
            asset_inventory=store.get_asset_inventory() or None,
            asset_states=store.get_asset_states() or None,
            active_contacts=store.get_contacts() or None,
            source="legacy_session_analysis",
            tick=store.get_tick(),
            scenario_id=scenario.scenario_id if scenario else store.state.scenario.scenario_id,
            scenario_name=scenario.name if scenario else store.state.scenario.scenario_name,
        ),
        include_tracks=True,
        include_temporal=True,
    )

    logger.info("Analysis run: %d events, %d threats, %d tracks",
                len(events), len(result.threats), len(result.tracks))

    return {
        "status": "ok",
        "pipeline": "canonical",
        "events_processed": len(events),
        "features_computed": len(result.features),
        "features": [f.model_dump(mode="json") for f in result.features],
        "anomalies": [a.model_dump(mode="json") for a in result.anomalies],
        "fused_tracks": serialize_fused_tracks(result.fused_tracks),
        "threats": [t.model_dump(mode="json") for t in result.threats],
        "targets": serialize_targets(result.targets),
        "top_targets": serialize_targets(result.top_targets),
        "tracks": {eid: t.model_dump(mode="json") for eid, t in result.tracks.items()},
        "temporal": result.temporal.model_dump(mode="json") if result.temporal else None,
        "coas": [c.model_dump(mode="json") for c in result.coas],
        "simulations": [s.model_dump(mode="json") for s in result.simulations],
        "scored_coas": [s.model_dump(mode="json") for s in result.scored_coas],
        "recommendation": result.recommendation.model_dump(mode="json") if result.recommendation else None,
        "coa_optimization": _serialize_optimization(result.coa_optimization),
        "operational_effects": result.operational_effects.to_dict() if result.operational_effects else {},
        "metadata": result.metadata,
    }
