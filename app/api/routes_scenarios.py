from fastapi import APIRouter

from ..core.session import get_session
from ..engine.event_ingestion import load_sample_scenario, list_scenarios, load_scenario

router = APIRouter(prefix="/scenario", tags=["scenarios"])


@router.get("/sample")
async def get_sample_scenario():
    """Return the validated sample Baltic Sea hybrid threat scenario."""
    scenario = load_sample_scenario()
    return scenario.model_dump()


@router.get("/list")
async def get_scenarios():
    """List all available scenarios."""
    return {"scenarios": list_scenarios()}


@router.post("/load/{scenario_id}")
async def load_scenario_into_session(scenario_id: str):
    """Load a scenario into the active session."""
    scenario = load_scenario(scenario_id)
    session = get_session()
    session.load_scenario(scenario)
    return {
        "status": "ok",
        "scenario_id": scenario.scenario_id,
        "name": scenario.name,
        "events_loaded": len(scenario.events),
    }


@router.get("/session/status")
async def session_status():
    """Return current session state summary."""
    session = get_session()
    return session.status()
