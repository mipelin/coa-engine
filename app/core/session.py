from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from .schemas import OperationalEvent, Scenario


class Session:
    """Thread-safe in-memory session holding accumulated events and scenario context."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._events: list[OperationalEvent] = []
        self._scenario: Scenario | None = None
        self._asset_inventory: dict[str, int] | None = None
        self.created_at: datetime = datetime.now(timezone.utc)
        self.last_event_at: datetime | None = None

    def ingest_events(self, events: list[OperationalEvent]) -> int:
        with self._lock:
            self._events.extend(events)
            self.last_event_at = datetime.now(timezone.utc)
            return len(self._events)

    def load_scenario(self, scenario: Scenario) -> None:
        with self._lock:
            self._scenario = scenario
            self._events = list(scenario.events)

    def get_events(self) -> list[OperationalEvent]:
        with self._lock:
            return list(self._events)

    def get_scenario(self) -> Scenario | None:
        with self._lock:
            return self._scenario

    def clear(self) -> None:
        with self._lock:
            self._events = []
            self._scenario = None
            self._asset_inventory = None

    def set_asset_inventory(self, inventory: dict[str, int]) -> None:
        with self._lock:
            self._asset_inventory = dict(inventory)

    def get_asset_inventory(self) -> dict[str, int] | None:
        with self._lock:
            return dict(self._asset_inventory) if self._asset_inventory else None

    def status(self) -> dict:
        with self._lock:
            return {
                "event_count": len(self._events),
                "scenario_id": self._scenario.scenario_id if self._scenario else None,
                "scenario_name": self._scenario.name if self._scenario else None,
                "asset_inventory": dict(self._asset_inventory) if self._asset_inventory else None,
                "created_at": self.created_at.isoformat(),
                "last_event_at": self.last_event_at.isoformat() if self.last_event_at else None,
            }


_session: Session | None = None
_session_lock = Lock()


def get_session() -> Session:
    global _session
    with _session_lock:
        if _session is None:
            _session = Session()
        return _session


def reset_session() -> None:
    global _session
    with _session_lock:
        _session = Session()
