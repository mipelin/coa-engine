"""SQLite persistence layer for StateStore."""
from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from ..core.config import settings
from ..core.schemas import (
    AnomalyResult,
    AssetState,
    Contact,
    ContactTrack,
    CourseOfAction,
    EngineState,
    Recommendation,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from .state_store import StateStore

logger = logging.getLogger("coa_engine.engine.persistence")

SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS engine_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    contacts TEXT NOT NULL DEFAULT '{}',
    tracks TEXT NOT NULL DEFAULT '{}',
    infrastructure TEXT NOT NULL DEFAULT '[]',
    asset_states TEXT NOT NULL DEFAULT '{}',
    threats TEXT NOT NULL DEFAULT '[]',
    anomalies TEXT NOT NULL DEFAULT '[]',
    scored_coas TEXT NOT NULL DEFAULT '[]',
    recommendation TEXT DEFAULT NULL,
    simulations TEXT NOT NULL DEFAULT '[]',
    coas TEXT NOT NULL DEFAULT '[]',
    engine_state TEXT NOT NULL DEFAULT '{}',
    tick INTEGER NOT NULL DEFAULT 0,
    contact_history TEXT NOT NULL DEFAULT '[]',
    scenario_id TEXT DEFAULT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    schema_version INTEGER NOT NULL DEFAULT 1
);
"""

UPSERT_SQL = """\
INSERT INTO engine_state (
    id, contacts, tracks, infrastructure, asset_states, threats, anomalies,
    scored_coas, recommendation, simulations, coas, engine_state, tick,
    contact_history, scenario_id, updated_at, schema_version
) VALUES (
    1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1
) ON CONFLICT(id) DO UPDATE SET
    contacts=excluded.contacts,
    tracks=excluded.tracks,
    infrastructure=excluded.infrastructure,
    asset_states=excluded.asset_states,
    threats=excluded.threats,
    anomalies=excluded.anomalies,
    scored_coas=excluded.scored_coas,
    recommendation=excluded.recommendation,
    simulations=excluded.simulations,
    coas=excluded.coas,
    engine_state=excluded.engine_state,
    tick=excluded.tick,
    contact_history=excluded.contact_history,
    scenario_id=excluded.scenario_id,
    updated_at=excluded.updated_at,
    schema_version=excluded.schema_version;
"""


def _serialize_dict(data: dict[str, Any]) -> str:
    return json.dumps({k: v.model_dump(mode="json") for k, v in data.items()})


def _serialize_list(data: list[Any]) -> str:
    return json.dumps([v.model_dump(mode="json") for v in data])


def _deserialize_dict(model_cls: type, raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    return {k: model_cls.model_validate(v) for k, v in data.items()}


def _deserialize_list(model_cls: type, raw: str) -> list[Any]:
    data = json.loads(raw)
    return [model_cls.model_validate(v) for v in data]


class PersistentStateStore(StateStore):
    """StateStore with SQLite auto-persistence."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        super().__init__()
        if db_path is None:
            db_path = settings.persistence_db_path
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._ensure_schema()
        self._db_lock = threading.Lock()
        self._save_debounce: float = time.monotonic()
        self._debounce_seconds: float = settings.persistence_debounce_seconds
        self._pending_save: threading.Event = threading.Event()

    def _ensure_schema(self) -> None:
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def restore(self) -> bool:
        """Load state from DB. Returns True if state was restored."""
        row = self._conn.execute("SELECT * FROM engine_state WHERE id = 1").fetchone()
        if row is None:
            return False
        try:
            with self._lock:
                self._contacts = _deserialize_dict(Contact, row[1])
                self._tracks = _deserialize_dict(ContactTrack, row[2])
                self._infrastructure = json.loads(row[3])
                self._asset_states = _deserialize_dict(AssetState, row[4])
                self._threats = _deserialize_list(ThreatResult, row[5])
                self._anomalies = _deserialize_list(AnomalyResult, row[6])
                self._scored_coas = _deserialize_list(ScoredCOA, row[7])
                self._recommendation = (
                    Recommendation.model_validate(json.loads(row[8]))
                    if row[8] else None
                )
                self._simulations = _deserialize_list(SimulationResult, row[9])
                self._coas = _deserialize_list(CourseOfAction, row[10])
                self._state = EngineState.model_validate(json.loads(row[11]))
                self._tick = row[12]
                self._contact_history = _deserialize_list(Contact, row[13])
            logger.info("State restored from %s (tick=%d, contacts=%d)",
                        self._db_path, self._tick, len(self._contacts))
            return True
        except Exception:
            logger.exception("Failed to restore state from %s", self._db_path)
            return False

    def save(self) -> None:
        """Serialize current state to SQLite."""
        with self._lock:
            contacts_json = _serialize_dict(self._contacts)
            tracks_json = _serialize_dict(self._tracks)
            infra_json = json.dumps(self._infrastructure)
            assets_json = _serialize_dict(self._asset_states)
            threats_json = _serialize_list(self._threats)
            anomalies_json = _serialize_list(self._anomalies)
            scored_json = _serialize_list(self._scored_coas)
            rec_json = (
                json.dumps(self._recommendation.model_dump(mode="json"))
                if self._recommendation else None
            )
            sims_json = _serialize_list(self._simulations)
            coas_json = _serialize_list(self._coas)
            state_json = json.dumps(self._state.model_dump(mode="json"))
            tick = self._tick
            history_json = _serialize_list(self._contact_history)
            scenario_id = self._state.scenario.scenario_id
        with self._db_lock:
            self._conn.execute(UPSERT_SQL, (
                contacts_json, tracks_json, infra_json, assets_json,
                threats_json, anomalies_json, scored_json, rec_json,
                sims_json, coas_json, state_json, tick,
                history_json, scenario_id,
            ))
            self._conn.commit()
        self._save_debounce = time.monotonic()

    def _on_state_changed(self) -> None:
        now = time.monotonic()
        if now - self._save_debounce < self._debounce_seconds:
            return
        self._save_debounce = now
        threading.Thread(target=self.save, daemon=True).start()

    def flush(self) -> None:
        """Block until any in-flight auto-save completes."""
        with self._db_lock:
            pass

    def close(self) -> None:
        self.save()
        self._conn.close()


_persistent_store: PersistentStateStore | None = None


def get_persistent_store() -> PersistentStateStore:
    global _persistent_store
    if _persistent_store is None:
        _persistent_store = PersistentStateStore()
    return _persistent_store


def reset_persistent_store() -> None:
    global _persistent_store
    if _persistent_store is not None:
        _persistent_store.close()
        _persistent_store = None
