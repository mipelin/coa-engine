from __future__ import annotations

import asyncio
import logging
from typing import Any

from .contact_engine import EngineMode, get_contact_engine
from .event_loop import get_event_loop
from .scenario_generator import ScenarioTemplate
from .state_store import get_state_store

logger = logging.getLogger("coa_engine.engine.engine_scheduler")


class EngineScheduler:
    """Runs the engine tick loop as an async background task."""

    def __init__(self) -> None:
        self._running = False
        self._task: asyncio.Task | None = None
        self._interval: float = 2.0
        self._subscribers: list[asyncio.Queue] = []
        self._last_tick: int = 0

    @property
    def running(self) -> bool:
        return self._running

    @property
    def interval(self) -> float:
        return self._interval

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=50)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        try:
            self._subscribers.remove(q)
        except ValueError:
            pass

    async def start(
        self,
        scenario_id: str = "baltic_hybrid_001",
        mode: str = "simulation",
        interval: float = 2.0,
        template: ScenarioTemplate | None = None,
    ) -> None:
        if self._running:
            await self.stop()

        self._interval = max(interval, 0.5)
        engine = get_contact_engine()
        engine.reset()
        engine.set_mode(EngineMode(mode))
        engine.load_scenario(scenario_id, template=template)
        # Prime the initial analysis so the UI has contacts/COAs immediately after Start.
        get_event_loop().run_analysis_now(trigger="startup")

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Engine scheduler started (scenario=%s, mode=%s, interval=%.1fs)",
                     scenario_id, mode, self._interval)

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None
        # Drain subscriber queues
        for q in self._subscribers:
            while not q.empty():
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    break
        logger.info("Engine scheduler stopped")

    async def _run_loop(self) -> None:
        engine = get_contact_engine()
        loop = get_event_loop()
        store = get_state_store()

        try:
            while self._running:
                contacts = engine.tick()
                result = loop.run_tick()
                state = store.state

                tick_data: dict[str, Any] = {
                    "tick": state.tick,
                    "contacts": [c.model_dump(mode="json") for c in contacts],
                    "state": state.model_dump(mode="json"),
                    "assets": [asset.model_dump(mode="json") for asset in store.get_asset_states()],
                    "analysis": result,
                    "threats": [t.model_dump(mode="json") for t in store.get_threats()],
                    "scored_coas": [s.model_dump(mode="json") for s in store.get_scored_coas()],
                    "recommendation": (
                        store.get_recommendation().model_dump(mode="json")
                        if store.get_recommendation() else None
                    ),
                    "tracks": {
                        k: v.model_dump(mode="json")
                        for k, v in store.get_tracks().items()
                    },
                    "latest_event_summary": (
                        store.get_latest_event_summary().model_dump(mode="json")
                        if store.get_latest_event_summary() else None
                    ),
                }

                # Push to all subscriber queues
                dead_queues: list[asyncio.Queue] = []
                for q in self._subscribers:
                    try:
                        q.put_nowait(tick_data)
                    except asyncio.QueueFull:
                        dead_queues.append(q)
                for q in dead_queues:
                    self.unsubscribe(q)

                await asyncio.sleep(self._interval)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Engine loop error: %s", e, exc_info=True)
            self._running = False


_scheduler: EngineScheduler | None = None


def get_engine_scheduler() -> EngineScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = EngineScheduler()
    return _scheduler
