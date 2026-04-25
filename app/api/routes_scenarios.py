from fastapi import APIRouter

from ..engine.event_ingestion import load_sample_scenario

router = APIRouter(prefix="/scenario", tags=["scenarios"])


@router.get("/sample")
async def get_sample_scenario():
    """Return the validated sample Baltic Sea hybrid threat scenario."""
    scenario = load_sample_scenario()
    return scenario.model_dump()
