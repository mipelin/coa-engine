from fastapi import APIRouter

from ..core.session import get_session
from ..core.schemas import EventBatch

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/ingest")
async def ingest_events(batch: EventBatch):
    """Ingest a batch of operational events into the active session."""
    session = get_session()
    total = session.ingest_events(batch.events)
    return {
        "status": "ok",
        "events_received": len(batch.events),
        "total_events_in_session": total,
        "event_ids": [e.event_id for e in batch.events],
    }


@router.get("/list")
async def list_events():
    """Return all events currently in the session."""
    session = get_session()
    events = session.get_events()
    return {
        "count": len(events),
        "events": [e.model_dump(mode="json") for e in events],
    }


@router.delete("/clear")
async def clear_events():
    """Clear the current session."""
    session = get_session()
    session.clear()
    return {"status": "ok", "message": "Session cleared"}
