from fastapi import APIRouter

from ..core.schemas import AnalysisRequest
from ..engine.anomaly_detection import detect_anomalies
from ..engine.coa_generation import generate_coas
from ..engine.event_ingestion import load_scenario_events
from ..engine.explanation import generate_briefing
from ..engine.feature_engineering import compute_features
from ..engine.recommendation import recommend
from ..engine.scoring import score_coas
from ..engine.simulation import run_simulations
from ..engine.threat_assessment import assess_threats

router = APIRouter(prefix="/coa", tags=["coa"])


def _run_full_pipeline(request: AnalysisRequest):
    events = request.events or load_scenario_events()
    features = compute_features(events)
    anomalies = detect_anomalies(events, features)
    threats = assess_threats(events, features, anomalies)
    return events, features, anomalies, threats


@router.post("/generate")
async def generate_coas_endpoint(request: AnalysisRequest):
    """Generate advisory courses of action based on current threat picture."""
    events, _, _, threats = _run_full_pipeline(request)
    coas = generate_coas(events, threats, request.asset_inventory)
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
    events, features, anomalies, threats = _run_full_pipeline(request)
    coas = generate_coas(events, threats, request.asset_inventory)
    sims = run_simulations(coas, events, threats)
    scored = score_coas(coas, sims)
    rec = recommend(scored)
    briefing = generate_briefing(events, anomalies, threats, scored, rec)
    return briefing.model_dump(mode="json")
