import logging

from fastapi import APIRouter

from ..core.session import get_session
from ..core.schemas import AnalysisRequest
from ..engine.anomaly_detection import detect_anomalies
from ..engine.entity_tracking import build_tracks
from ..engine.feature_engineering import compute_features
from ..engine.threat_assessment import assess_threats
from ..engine.time_series import analyze_temporal_patterns

router = APIRouter(prefix="/analysis", tags=["analysis"])

logger = logging.getLogger("coa_engine.api.analysis")


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
    features = compute_features(events, infrastructure)
    anomalies = detect_anomalies(events, features)
    threats = assess_threats(events, features, anomalies)
    tracks = build_tracks(events)
    temporal = analyze_temporal_patterns(events)

    logger.info("Analysis run: %d events, %d threats, %d tracks",
                len(events), len(threats), len(tracks))

    return {
        "status": "ok",
        "events_processed": len(events),
        "features_computed": len(features),
        "features": [f.model_dump(mode="json") for f in features],
        "anomalies": [a.model_dump(mode="json") for a in anomalies],
        "threats": [t.model_dump(mode="json") for t in threats],
        "tracks": {eid: t.model_dump(mode="json") for eid, t in tracks.items()},
        "temporal": temporal.model_dump(mode="json"),
    }
