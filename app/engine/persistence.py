"""SQLite persistence layer for StateStore."""
from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
from datetime import datetime
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
    EventSummary,
    Recommendation,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from .state_store import StateStore

logger = logging.getLogger("coa_engine.engine.persistence")

SCHEMA_V2_SQL = """\
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
    schema_version INTEGER NOT NULL DEFAULT 2,
    fused_tracks TEXT NOT NULL DEFAULT '[]',
    targets TEXT NOT NULL DEFAULT '[]',
    coa_optimization TEXT DEFAULT NULL,
    operational_effects TEXT DEFAULT NULL,
    event_summary TEXT DEFAULT NULL
);
"""

REPLAY_SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS replay_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tick INTEGER NOT NULL,
    snapshot TEXT NOT NULL,
    scenario_id TEXT DEFAULT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

UPSERT_SQL = """\
INSERT INTO engine_state (
    id, contacts, tracks, infrastructure, asset_states, threats, anomalies,
    scored_coas, recommendation, simulations, coas, engine_state, tick,
    contact_history, scenario_id, updated_at, schema_version,
    fused_tracks, targets, coa_optimization, operational_effects, event_summary
) VALUES (
    1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 2,
    ?, ?, ?, ?, ?
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
    schema_version=excluded.schema_version,
    fused_tracks=excluded.fused_tracks,
    targets=excluded.targets,
    coa_optimization=excluded.coa_optimization,
    operational_effects=excluded.operational_effects,
    event_summary=excluded.event_summary;
"""

# Migration: add new columns to v1 tables
_MIGRATION_V2_COLUMNS = [
    ("fused_tracks", "TEXT NOT NULL DEFAULT '[]'"),
    ("targets", "TEXT NOT NULL DEFAULT '[]'"),
    ("coa_optimization", "TEXT DEFAULT NULL"),
    ("operational_effects", "TEXT DEFAULT NULL"),
    ("event_summary", "TEXT DEFAULT NULL"),
]


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

    def _ensure_schema(self) -> None:
        self._conn.executescript(SCHEMA_V2_SQL)
        self._conn.executescript(REPLAY_SCHEMA_SQL)
        # Migrate v1 tables if needed
        for col_name, col_type in _MIGRATION_V2_COLUMNS:
            try:
                self._conn.execute(f"ALTER TABLE engine_state ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass  # Column already exists
        self._conn.commit()

    def restore(self) -> bool:
        """Load state from DB. Returns True if state was restored."""
        row = self._conn.execute("SELECT * FROM engine_state WHERE id = 1").fetchone()
        if row is None:
            return False
        try:
            # Column indices for v2 schema
            # 0=id, 1=contacts, 2=tracks, 3=infra, 4=assets, 5=threats,
            # 6=anomalies, 7=scored, 8=recommendation, 9=sims, 10=coas,
            # 11=engine_state, 12=tick, 13=history, 14=scenario_id,
            # 15=updated_at, 16=schema_version, 17=fused_tracks, 18=targets,
            # 19=coa_optimization, 20=operational_effects, 21=event_summary
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

                # v2 columns — use safe index access
                col_count = len(row)
                if col_count > 17:
                    self._fused_tracks = _deserialize_fused_tracks(row[17])
                if col_count > 18:
                    self._targets = _deserialize_targets(row[18])
                if col_count > 19 and row[19]:
                    self._coa_optimization = _deserialize_optimization(row[19])
                if col_count > 20 and row[20]:
                    self._operational_effects = _deserialize_operational_effects(row[20])
                if col_count > 21 and row[21]:
                    self._latest_event_summary = EventSummary.model_validate(json.loads(row[21]))

            logger.info("State restored from %s (tick=%d, contacts=%d, fused=%d, targets=%d)",
                        self._db_path, self._tick, len(self._contacts),
                        len(self._fused_tracks), len(self._targets))
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

            # v2 artifacts
            fused_json = _serialize_fused_tracks(self._fused_tracks)
            targets_json = _serialize_targets(self._targets)
            opt_json = _serialize_optimization(getattr(self, "_coa_optimization", None))
            opfx_json = _serialize_operational_effects(getattr(self, "_operational_effects", None))
            summary_json = (
                json.dumps(self._latest_event_summary.model_dump(mode="json"))
                if self._latest_event_summary else None
            )

        with self._db_lock:
            self._conn.execute(UPSERT_SQL, (
                contacts_json, tracks_json, infra_json, assets_json,
                threats_json, anomalies_json, scored_json, rec_json,
                sims_json, coas_json, state_json, tick,
                history_json, scenario_id,
                fused_json, targets_json, opt_json, opfx_json, summary_json,
            ))
            self._conn.commit()
        self._save_debounce = time.monotonic()

    # --- Replay snapshot persistence ---

    def save_replay_snapshot(self, snapshot_dict: dict[str, Any]) -> None:
        """Persist a replay snapshot."""
        with self._db_lock:
            self._conn.execute(
                "INSERT INTO replay_snapshots (tick, snapshot, scenario_id) VALUES (?, ?, ?)",
                (snapshot_dict["tick"], json.dumps(snapshot_dict), snapshot_dict.get("scenario_id")),
            )
            self._conn.commit()

    def load_replay_snapshots(self) -> list[dict[str, Any]]:
        """Load all replay snapshots."""
        with self._db_lock:
            rows = self._conn.execute(
                "SELECT snapshot FROM replay_snapshots ORDER BY id ASC"
            ).fetchall()
        return [json.loads(r[0]) for r in rows]

    def clear_replay_snapshots(self) -> None:
        """Delete all replay snapshots."""
        with self._db_lock:
            self._conn.execute("DELETE FROM replay_snapshots")
            self._conn.commit()

    def cap_replay_snapshots(self, max_snapshots: int) -> None:
        """Trim oldest snapshots beyond max_snapshots."""
        with self._db_lock:
            count = self._conn.execute("SELECT COUNT(*) FROM replay_snapshots").fetchone()[0]
            if count > max_snapshots:
                self._conn.execute(
                    "DELETE FROM replay_snapshots WHERE id IN "
                    "(SELECT id FROM replay_snapshots ORDER BY id ASC LIMIT ?)",
                    (count - max_snapshots,),
                )
                self._conn.commit()

    # --- Lifecycle ---

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


# ---------------------------------------------------------------------------
# Serialization helpers for new artifact types
# ---------------------------------------------------------------------------


def _json_safe(obj: Any) -> Any:
    """Recursively convert non-JSON-native types (datetime) to strings."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def _serialize_fused_tracks(tracks: list[Any]) -> str:
    return json.dumps([_json_safe(t.to_dict()) if hasattr(t, "to_dict") else t for t in tracks])


def _deserialize_fused_tracks(raw: str) -> list[Any]:
    from .fusion import FusedTrack
    data = json.loads(raw)
    tracks = []
    for d in data:
        if isinstance(d, dict):
            if "last_seen" in d and isinstance(d["last_seen"], str):
                d["last_seen"] = datetime.fromisoformat(d["last_seen"])
            tracks.append(FusedTrack(**d))
        else:
            tracks.append(d)
    return tracks


def _serialize_targets(targets: list[Any]) -> str:
    return json.dumps([t.to_dict() if hasattr(t, "to_dict") else t for t in targets])


def _deserialize_targets(raw: str) -> list[Any]:
    from .targeting import Target
    data = json.loads(raw)
    return [Target.from_dict(d) if isinstance(d, dict) else d for d in data]


def _serialize_optimization(opt: Any | None) -> str | None:
    if opt is None:
        return None
    return json.dumps({
        "optimized_variants": [s.model_dump(mode="json") for s in opt.optimized_variants],
        "variant_parameters": opt.variant_parameters,
        "best_variant": opt.best_variant.model_dump(mode="json") if opt.best_variant else None,
        "robustness_ranking": opt.robustness_ranking,
        "optimization_summary": opt.optimization_summary,
    })


def _deserialize_optimization(raw: str) -> Any | None:
    from .coa_optimizer import OptimizationResult, ScoredCOA as _SCO
    data = json.loads(raw)
    variants = [_SCO.model_validate(v) for v in data.get("optimized_variants", [])]
    best = _SCO.model_validate(data["best_variant"]) if data.get("best_variant") else None
    return OptimizationResult(
        optimized_variants=variants,
        best_variant=best,
        robustness_ranking=data.get("robustness_ranking", []),
        variant_parameters=data.get("variant_parameters", []),
        optimization_summary=data.get("optimization_summary", {"status": "restored"}),
    )


def _serialize_operational_effects(effects: Any | None) -> str | None:
    if effects is None:
        return None
    return json.dumps(effects.to_dict())


def _deserialize_operational_effects(raw: str) -> Any | None:
    from .operational_effects import OperationalEffects
    data = json.loads(raw)
    effects = OperationalEffects()
    for key, value in data.items():
        if hasattr(effects, key):
            setattr(effects, key, value)
    return effects


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


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
