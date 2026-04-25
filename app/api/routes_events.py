from fastapi import APIRouter

from ..core.schemas import EventBatch, OperationalEvent

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/ingest")
async def ingest_events(batch: EventBatch):
    """Ingest a batch of operational events for analysis."""
    return {
        "status": "ok",
        "events_received": len(batch.events),
        "event_ids": [e.event_id for e in batch.events],
    }
