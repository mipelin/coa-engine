from __future__ import annotations

import logging
from collections import defaultdict
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger("coa_engine.engine.event_bus")


class EventKind(str, Enum):
    CONTACT_RECEIVED = "contact_received"
    THREAT_LEVEL_CHANGED = "threat_level_changed"
    COA_RANK_CHANGED = "coa_rank_changed"
    STATE_UPDATED = "state_updated"
    ANALYSIS_CYCLE = "analysis_cycle"
    BRIEFING_REQUESTED = "briefing_requested"
    USER_QUESTION = "user_question"


class Event:
    __slots__ = ("kind", "payload", "tick")

    def __init__(self, kind: EventKind, payload: Any = None, tick: int = 0) -> None:
        self.kind = kind
        self.payload = payload
        self.tick = tick

    def __repr__(self) -> str:
        return f"Event({self.kind.value}, tick={self.tick})"


class EventBus:
    """Synchronous in-process event bus with topic-based subscriptions."""

    def __init__(self) -> None:
        self._handlers: dict[EventKind, list[Callable[[Event], None]]] = defaultdict(list)
        self._log: list[Event] = []
        self._max_log = 500

    def subscribe(self, kind: EventKind, handler: Callable[[Event], None]) -> None:
        self._handlers[kind].append(handler)

    def publish(self, event: Event) -> None:
        self._log.append(event)
        if len(self._log) > self._max_log:
            self._log = self._log[-self._max_log:]
        handlers = self._handlers.get(event.kind, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error("Event handler error for %s: %s", event.kind.value, e)

    def recent_events(self, kind: EventKind | None = None, limit: int = 50) -> list[Event]:
        events = self._log
        if kind is not None:
            events = [e for e in events if e.kind == kind]
        return events[-limit:]

    def clear(self) -> None:
        self._log.clear()


_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus
