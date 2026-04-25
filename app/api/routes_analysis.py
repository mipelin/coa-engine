from fastapi import APIRouter

from ..core.schemas import AnalysisRequest
from ..engine.anomaly_detection import detect_anomalies
from ..engine.event_ingestion import load_scenario_events
from ..engine.feature_engineering import compute_features
from ..engine.threat_assessment import assess_threats

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run")
async def run_analysis(request: AnalysisRequest):
    """Run full analysis pipeline: features, anomalies, threat assessment."""
    events = request.events or load_scenario_events()
    features = compute_features(events)
    anomalies = detect_anomalies(events, features)
    threats = assess_threats(events, features, anomalies)

    return {
        "status": "ok",
        "events_processed": len(events),
        "features_computed": len(features),
        "features": [f.model_dump(mode="json") for f in features],
        "anomalies": [a.model_dump(mode="json") for a in anomalies],
        "threats": [t.model_dump(mode="json") for t in threats],
    }
