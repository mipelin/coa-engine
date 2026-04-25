import logging

from fastapi import APIRouter, Response

from ..core.session import get_session
from ..core.schemas import AnalysisRequest
from ..engine.anomaly_detection import detect_anomalies
from ..engine.coa_generation import generate_coas
from ..engine.explanation import generate_briefing
from ..engine.feature_engineering import compute_features
from ..engine.recommendation import recommend
from ..engine.scoring import score_coas
from ..engine.simulation import run_simulations
from ..engine.threat_assessment import assess_threats

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


def _run_full_pipeline(request: AnalysisRequest):
    events = _get_events(request)
    infrastructure = _get_infrastructure(request)
    features = compute_features(events, infrastructure)
    anomalies = detect_anomalies(events, features)
    threats = assess_threats(events, features, anomalies)
    return events, features, anomalies, threats


@router.post("/generate")
async def generate_coas_endpoint(request: AnalysisRequest):
    """Generate advisory courses of action based on current threat picture."""
    events, _, _, threats = _run_full_pipeline(request)
    coas = generate_coas(events, threats, request.asset_inventory)
    logger.info("Generated %d COAs", len(coas))
    return {
        "status": "ok",
        "coas": [c.model_dump(mode="json") for c in coas],
        "threat_context": [t.model_dump(mode="json") for t in threats],
    }


@router.post("/simulation/run")
async def run_simulation(request: AnalysisRequest):
    """Run Monte Carlo simulation for all generated COAs."""
    events, _, _, threats = _run_full_pipeline(request)
    coas = generate_coas(events, threats, request.asset_inventory)
    sims = run_simulations(coas, events, threats)
    return {
        "status": "ok",
        "simulations": [s.model_dump(mode="json") for s in sims],
    }


@router.post("/recommendation/run")
async def run_recommendation(request: AnalysisRequest):
    """Score COAs and produce advisory recommendation."""
    events, _, _, threats = _run_full_pipeline(request)
    coas = generate_coas(events, threats, request.asset_inventory)
    sims = run_simulations(coas, events, threats)
    scored = score_coas(coas, sims)
    rec = recommend(scored)
    return rec.model_dump(mode="json")


@router.post("/briefing/generate")
async def generate_briefing_endpoint(request: AnalysisRequest):
    """Generate a commander decision-support briefing."""
    events, _, anomalies, threats = _run_full_pipeline(request)
    coas = generate_coas(events, threats, request.asset_inventory)
    sims = run_simulations(coas, events, threats)
    scored = score_coas(coas, sims)
    rec = recommend(scored)
    scenario_name = _get_scenario_name()
    briefing = generate_briefing(events, anomalies, threats, scored, rec, scenario_name)
    return briefing.model_dump(mode="json")


@router.post("/briefing/export/json")
async def export_briefing_json_endpoint(request: AnalysisRequest):
    """Export briefing as downloadable JSON."""
    from ..engine.export import export_briefing_json
    events, _, anomalies, threats = _run_full_pipeline(request)
    coas = generate_coas(events, threats, request.asset_inventory)
    sims = run_simulations(coas, events, threats)
    scored = score_coas(coas, sims)
    rec = recommend(scored)
    scenario_name = _get_scenario_name()
    briefing = generate_briefing(events, anomalies, threats, scored, rec, scenario_name)
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
    events, _, anomalies, threats = _run_full_pipeline(request)
    coas = generate_coas(events, threats, request.asset_inventory)
    sims = run_simulations(coas, events, threats)
    scored = score_coas(coas, sims)
    rec = recommend(scored)
    scenario_name = _get_scenario_name()
    briefing = generate_briefing(events, anomalies, threats, scored, rec, scenario_name)
    content = export_briefing_pdf(briefing)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=briefing.pdf"},
    )
