import logging

from fastapi import APIRouter, Response

from ..core.session import get_session
from ..core.schemas import AnalysisRequest
from ..engine.asset_state import build_simulated_asset_states
from ..engine.analysis_service import AnalysisContext, AnalysisResult, run_canonical_analysis
from ..engine.explanation import generate_briefing
from ..engine.state_store import get_state_store

router = APIRouter(prefix="/coa", tags=["coa"])

logger = logging.getLogger("coa_engine.api.coa")


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


def _get_scenario_name() -> str:
    session = get_session()
    scenario = session.get_scenario()
    return scenario.name if scenario else "Operational Area"


def _resolve_asset_inventory(request: AnalysisRequest) -> dict[str, int] | None:
    if request.asset_states:
        return {
            asset.asset_id: asset.quantity_available
            for asset in request.asset_states
        }
    if request.asset_inventory is not None:
        return dict(request.asset_inventory)
    session = get_session()
    inventory = session.get_asset_inventory()
    if inventory is not None:
        return inventory
    live_inventory = get_state_store().get_asset_inventory()
    return live_inventory or None


def _resolve_asset_states(request: AnalysisRequest, events: list | None = None):
    if request.asset_states is not None:
        return request.asset_states
    if request.asset_inventory is not None:
        return build_simulated_asset_states(request.asset_inventory, events or [])
    live_states = get_state_store().get_asset_states()
    return live_states or None


def _run_full_pipeline(request: AnalysisRequest) -> AnalysisResult:
    """Deprecated route helper. Delegates to the canonical DIANA analysis service."""
    events = _get_events(request)
    infrastructure = _get_infrastructure(request)
    asset_inventory = _resolve_asset_inventory(request)
    asset_states = _resolve_asset_states(request, events)
    get_session().set_asset_inventory(asset_inventory or {})
    get_state_store().set_asset_states(asset_states=asset_states, asset_inventory=asset_inventory)
    session = get_session()
    scenario = session.get_scenario()
    store = get_state_store()
    return run_canonical_analysis(
        AnalysisContext(
            events=events,
            infrastructure=infrastructure,
            scenario_state=store.state.scenario,
            asset_inventory=asset_inventory,
            asset_states=asset_states,
            active_contacts=store.get_contacts() or None,
            source="legacy_coa_route",
            tick=store.get_tick(),
            scenario_id=scenario.scenario_id if scenario else store.state.scenario.scenario_id,
            scenario_name=scenario.name if scenario else store.state.scenario.scenario_name,
        )
    )


@router.post("/generate")
async def generate_coas_endpoint(request: AnalysisRequest):
    """Generate advisory courses of action based on current threat picture."""
    result = _run_full_pipeline(request)
    logger.info("Generated %d COAs via canonical analysis", len(result.coas))
    return {
        "status": "ok",
        "pipeline": "canonical",
        "coas": [c.model_dump(mode="json") for c in result.coas],
        "threat_context": [t.model_dump(mode="json") for t in result.threats],
    }


@router.post("/simulation/run")
async def run_simulation(request: AnalysisRequest):
    """Run deterministic parametric outcome estimation for all generated COAs."""
    result = _run_full_pipeline(request)
    return {
        "status": "ok",
        "pipeline": "canonical",
        "simulations": [s.model_dump(mode="json") for s in result.simulations],
    }


@router.post("/recommendation/run")
async def run_recommendation(request: AnalysisRequest):
    """Score COAs and produce advisory recommendation."""
    result = _run_full_pipeline(request)
    return result.recommendation.model_dump(mode="json") if result.recommendation else {}


@router.post("/briefing/generate")
async def generate_briefing_endpoint(request: AnalysisRequest):
    """Generate a commander decision-support briefing."""
    result = _run_full_pipeline(request)
    scenario_name = _get_scenario_name()
    briefing = generate_briefing(
        result.context.events,
        result.anomalies,
        result.threats,
        result.scored_coas,
        result.recommendation,
        scenario_name,
    )
    return briefing.model_dump(mode="json")


@router.post("/briefing/export/json")
async def export_briefing_json_endpoint(request: AnalysisRequest):
    """Export briefing as downloadable JSON."""
    from ..engine.export import export_briefing_json
    result = _run_full_pipeline(request)
    scenario_name = _get_scenario_name()
    briefing = generate_briefing(
        result.context.events,
        result.anomalies,
        result.threats,
        result.scored_coas,
        result.recommendation,
        scenario_name,
    )
    content = export_briefing_json(briefing)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=briefing.json"},
    )


@router.post("/briefing/export/pdf")
async def export_briefing_pdf_endpoint(request: AnalysisRequest):
    """Export briefing as downloadable PDF."""
    from ..engine.export import export_briefing_pdf
    result = _run_full_pipeline(request)
    scenario_name = _get_scenario_name()
    briefing = generate_briefing(
        result.context.events,
        result.anomalies,
        result.threats,
        result.scored_coas,
        result.recommendation,
        scenario_name,
    )
    content = export_briefing_pdf(briefing)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=briefing.pdf"},
    )
