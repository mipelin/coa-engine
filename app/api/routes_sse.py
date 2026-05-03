from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse

from ..engine.engine_scheduler import get_engine_scheduler
from ..engine.state_store import get_state_store

router = APIRouter(prefix="/stream", tags=["stream"])


@router.get("/events")
async def stream_events():
    """SSE endpoint: push engine state updates on every tick."""
    scheduler = get_engine_scheduler()

    async def event_generator():
        queue = scheduler.subscribe()
        try:
            while True:
                try:
                    tick_data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {"data": json.dumps(tick_data, default=str)}
                except asyncio.TimeoutError:
                    yield {"data": json.dumps({"type": "heartbeat"})}
        except asyncio.CancelledError:
            pass
        finally:
            scheduler.unsubscribe(queue)

    return EventSourceResponse(event_generator())


@router.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """WebSocket endpoint: subscribe to engine tick updates (alias for /engine/ws/stream)."""
    await websocket.accept()
    scheduler = get_engine_scheduler()

    # Auto-start if not running
    if not scheduler.running:
        await scheduler.start()

    queue = scheduler.subscribe()

    try:
        while True:
            tick_data = await asyncio.wait_for(queue.get(), timeout=30.0)
            await websocket.send_json(tick_data)
    except (asyncio.TimeoutError, WebSocketDisconnect):
        pass
    except Exception:
        pass
    finally:
        scheduler.unsubscribe(queue)
