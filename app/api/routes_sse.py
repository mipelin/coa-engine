from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket
from sse_starlette.sse import EventSourceResponse

from ..core.session import get_session

router = APIRouter(prefix="/stream", tags=["stream"])


@router.get("/events")
async def stream_events():
    """SSE endpoint that pushes session state updates."""
    async def event_generator():
        last_count = 0
        while True:
            session = get_session()
            current_count = len(session.get_events())
            if current_count != last_count:
                data = {"event_count": current_count}
                yield {"data": json.dumps(data)}
                last_count = current_count
            await asyncio.sleep(2)

    return EventSourceResponse(event_generator())


@router.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """WebSocket endpoint for real-time session updates."""
    await websocket.accept()
    last_count = 0
    try:
        while True:
            session = get_session()
            current_count = len(session.get_events())
            if current_count != last_count:
                await websocket.send_json({"event_count": current_count})
                last_count = current_count
            await asyncio.sleep(2)
    except Exception:
        pass
