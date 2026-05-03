"""Tests for Phase 9 hardening: lifespan cleanup, persistence, reset behavior."""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.core.constants import EntityType, EventType, ThreatLevel
from app.core.schemas import (
    AnomalyResult,
    AnomalyLevel,
    Contact,
    ContactType,
    CourseOfAction,
    EventSummary,
    OperationalEvent,
    Recommendation,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from app.engine.fusion import FusedTrack
from app.engine.operational_effects import OperationalEffects, compute_operational_effects
from app.engine.persistence import (
    PersistentStateStore,
    get_persistent_store,
    reset_persistent_store,
)
from app.engine.replay import ReplaySnapshot, ReplayStore, get_replay_store
from app.engine.targeting import Target


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ts(minutes: int = 0) -> datetime:
    return datetime(2025, 6, 15, 8, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def _threat(entity_id="E1", level="MEDIUM", prob=0.4) -> ThreatResult:
    return ThreatResult(
        entity_id=entity_id, threat_probability=prob,
        threat_level=ThreatLevel(level), confidence=0.8,
        main_drivers=["proximity"],
    )


def _scored_coa(coa_id="COA-1", score=70.0, roe="allowed") -> ScoredCOA:
    coa = CourseOfAction(
        coa_id=coa_id, template_id="COA-TPL-ISR",
        title="Test COA", description="Test",
        target_entities=["E1"], required_assets=["isr_uav"],
        assigned_assets=["isr_uav"], assumptions=[],
        estimated_time_minutes=30, expected_effect="Test",
        risk_categories=[], escalation_risk=0.1,
        civilian_risk=0.02, logistics_burden=0.3,
        roe_status=roe,
    )
    sim = SimulationResult(
        coa_id=coa_id, success_probability=0.7, expected_time_to_effect=30.0,
        risk_to_second_cable=0.1, escalation_probability=0.1,
        missed_detection_probability=0.2, confidence_interval=(0.6, 0.8),
        simulation_runs=100,
    )
    return ScoredCOA(coa=coa, simulation=sim, total_score=score, rank=1,
                     tradeoff_explanation="Test")


def _fused_track(entity_id="E1") -> FusedTrack:
    return FusedTrack(
        track_id="FUSED-001", primary_entity_id=entity_id,
        correlated_entities=[entity_id], track_type="vessel",
        allegiance="unknown", fused_confidence=0.88, source_count=2,
        sources=["ais", "combat_system"], last_seen=_ts(),
        position={"lat": 57.5, "lon": 19.0}, heading=45.0, speed=8.0,
        anomaly_support=0.3, threat_support=0.4, rationale="Test track",
    )


def _target(entity_id="E1") -> Target:
    return Target(
        id=entity_id, type="vessel", classification_confidence=0.85,
        threat_score=0.4, priority_score=45.0, priority_level="MEDIUM",
        recommended_action="track", roe_status="allowed",
        rationale="Test", sources=["ais"],
    )


# ---------------------------------------------------------------------------
# Lifespan: no on_event deprecation warning
# ---------------------------------------------------------------------------


class TestLifespan:
    def test_no_on_event_warning(self):
        """Importing app.main should not trigger on_event deprecation."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Force reimport to check
            import importlib
            import app.main as main_mod
            importlib.reload(main_mod)
            deprecation_warnings = [
                x for x in w
                if issubclass(x.category, DeprecationWarning)
                and "on_event" in str(x.message)
            ]
            assert len(deprecation_warnings) == 0, (
                f"Found on_event deprecation warnings: {deprecation_warnings}"
            )


# ---------------------------------------------------------------------------
# Persistence: schema migration
# ---------------------------------------------------------------------------


class TestPersistenceSchema:
    def test_v2_schema_has_new_columns(self, tmp_path):
        db_path = tmp_path / "test_state.db"
        store = PersistentStateStore(db_path=str(db_path))
        # Check all v2 columns exist
        row = store._conn.execute("PRAGMA table_info(engine_state)").fetchall()
        col_names = {r[1] for r in row}
        assert "fused_tracks" in col_names
        assert "targets" in col_names
        assert "coa_optimization" in col_names
        assert "operational_effects" in col_names
        assert "event_summary" in col_names
        store.close()

    def test_replay_table_exists(self, tmp_path):
        db_path = tmp_path / "test_state.db"
        store = PersistentStateStore(db_path=str(db_path))
        tables = store._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {t[0] for t in tables}
        assert "replay_snapshots" in table_names
        store.close()

    def test_migration_from_v1(self, tmp_path):
        """Simulate a v1 DB and verify migration adds new columns."""
        db_path = tmp_path / "test_v1.db"
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        # Create v1 schema
        conn.executescript("""\
            CREATE TABLE engine_state (
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
        """)
        conn.execute(
            "INSERT INTO engine_state (id) VALUES (1)"
        )
        conn.commit()
        conn.close()

        # Open with PersistentStateStore — should migrate
        store = PersistentStateStore(db_path=str(db_path))
        col_names = {r[1] for r in store._conn.execute("PRAGMA table_info(engine_state)").fetchall()}
        assert "fused_tracks" in col_names
        assert "targets" in col_names
        store.close()


# ---------------------------------------------------------------------------
# Persistence: save/restore artifacts
# ---------------------------------------------------------------------------


class TestPersistenceRestore:
    def _populated_store(self, db_path: str) -> PersistentStateStore:
        """Create and populate a store with all artifacts."""
        store = PersistentStateStore(db_path=db_path)
        store.ingest_contact(Contact(
            contact_id="C-E1", timestamp=_ts(), source="ais",
            contact_type=ContactType.VESSEL, lat=57.5, lon=19.0,
            speed=8.0, heading=45.0, confidence=0.85, entity_id="E1",
            is_hostile=False, attributes={"subtype": "warship"},
        ))
        store._fused_tracks = [_fused_track("E1")]
        store._targets = [_target("E1")]
        store._coa_optimization = None  # tested separately
        store._operational_effects = compute_operational_effects({"sea_state": 5})
        store._latest_event_summary = EventSummary(
            tick=1, event_type="test", summary_text="test summary",
            timestamp=_ts(), llm_used=False, language_used="en",
        )
        threats = [_threat("E1", "HIGH", 0.7)]
        scored = [_scored_coa()]
        rec = Recommendation(recommended=scored[0], alternatives=[],
                             rationale="Test", edge_cases="")
        store.update_analysis(
            threats=threats,
            anomalies=[AnomalyResult(event_id="EV-1", entity_id="E1",
                                     anomaly_score=50.0, anomaly_level=AnomalyLevel.MEDIUM,
                                     explanations=["test"])],
            scored=scored,
            recommendation=rec,
            coas=[scored[0].coa],
            simulations=[scored[0].simulation],
            targets=store._targets,
            fused_tracks=store._fused_tracks,
        )
        return store

    def test_fused_tracks_persist_restore(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = self._populated_store(db_path)
        store.save()
        store.close()

        store2 = PersistentStateStore(db_path=db_path)
        assert store2.restore()
        fused = store2.get_fused_tracks()
        assert len(fused) == 1
        assert fused[0].track_id == "FUSED-001"
        assert fused[0].primary_entity_id == "E1"
        store2.close()

    def test_targets_persist_restore(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = self._populated_store(db_path)
        store.save()
        store.close()

        store2 = PersistentStateStore(db_path=db_path)
        assert store2.restore()
        targets = store2.get_targets()
        assert len(targets) == 1
        assert targets[0].id == "E1"
        assert targets[0].priority_level == "MEDIUM"
        store2.close()

    def test_operational_effects_persist_restore(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = self._populated_store(db_path)
        store.save()
        store.close()

        store2 = PersistentStateStore(db_path=db_path)
        assert store2.restore()
        fx = store2._operational_effects
        assert fx is not None
        assert fx.sea_state == 5
        assert fx.overall_effectiveness < 0.95
        store2.close()

    def test_event_summary_persist_restore(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = self._populated_store(db_path)
        store.save()
        store.close()

        store2 = PersistentStateStore(db_path=db_path)
        assert store2.restore()
        summary = store2.get_latest_event_summary()
        assert summary is not None
        assert summary.summary_text == "test summary"
        store2.close()

    def test_threats_and_recommendation_restore(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = self._populated_store(db_path)
        store.save()
        store.close()

        store2 = PersistentStateStore(db_path=db_path)
        assert store2.restore()
        threats = store2.get_threats()
        assert len(threats) == 1
        assert threats[0].threat_level == ThreatLevel.HIGH
        rec = store2.get_recommendation()
        assert rec is not None
        assert rec.recommended.coa.coa_id == "COA-1"
        store2.close()

    def test_cop_works_after_restore(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = self._populated_store(db_path)
        store.save()
        store.close()

        # Simulate restart: create new store and restore
        from app.engine.cop import assemble_cop
        store2 = PersistentStateStore(db_path=db_path)
        assert store2.restore()

        # Inject into the module-level store for COP assembly
        import app.engine.state_store as ss_mod
        old_store = ss_mod._store
        ss_mod._store = store2
        try:
            cop = assemble_cop(store2)
            assert cop.threat_summary.threat_level == "HIGH"
            assert len(cop.contacts) > 0
            assert len(cop.targets) > 0
            assert cop.operational_effects  # restored effects
        finally:
            ss_mod._store = old_store
            store2.close()


# ---------------------------------------------------------------------------
# Persistence: replay snapshots
# ---------------------------------------------------------------------------


class TestReplayPersistence:
    def test_replay_snapshots_persist_restore(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = PersistentStateStore(db_path=db_path)

        snap = ReplaySnapshot(tick=1, scenario_id="test", threat_level="MEDIUM",
                              recommended_coa_id="COA-1", recommended_coa_title="ISR")
        store.save_replay_snapshot(snap.to_dict())

        snap2 = ReplaySnapshot(tick=2, scenario_id="test", threat_level="HIGH",
                               recommended_coa_id="COA-2", recommended_coa_title="Shadow")
        store.save_replay_snapshot(snap2.to_dict())

        raw = store.load_replay_snapshots()
        assert len(raw) == 2
        assert raw[0]["tick"] == 1
        assert raw[1]["tick"] == 2
        store.close()

    def test_replay_clear(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = PersistentStateStore(db_path=db_path)
        store.save_replay_snapshot(ReplaySnapshot(tick=1).to_dict())
        assert len(store.load_replay_snapshots()) == 1

        store.clear_replay_snapshots()
        assert len(store.load_replay_snapshots()) == 0
        store.close()

    def test_replay_cap(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        store = PersistentStateStore(db_path=db_path)
        for i in range(10):
            store.save_replay_snapshot(ReplaySnapshot(tick=i + 1).to_dict())

        store.cap_replay_snapshots(5)
        raw = store.load_replay_snapshots()
        assert len(raw) == 5
        assert raw[0]["tick"] == 6  # oldest trimmed
        store.close()


# ---------------------------------------------------------------------------
# Reset behavior
# ---------------------------------------------------------------------------


class TestResetBehavior:
    def test_clear_resets_new_artifacts(self):
        from app.engine.state_store import StateStore
        store = StateStore()
        store._coa_optimization = "fake"
        store._operational_effects = compute_operational_effects({"sea_state": 5})
        store.clear()
        assert getattr(store, "_coa_optimization", None) is None
        assert getattr(store, "_operational_effects", None) is None

    def test_replay_clear_on_event_loop_reset(self):
        store = get_replay_store()
        store.add_snapshot(ReplaySnapshot(tick=1, scenario_id="test"))
        assert store.snapshot_count > 0

        from app.engine.event_loop import get_event_loop
        get_event_loop().reset_runtime_state()
        assert store.snapshot_count == 0

    def test_full_reset_no_bleed(self):
        """After full reset, no old state bleeds through."""
        from app.engine.state_store import StateStore
        from app.engine.cop import assemble_cop

        store = StateStore()
        # Populate
        store.ingest_contact(Contact(
            contact_id="C-E1", timestamp=_ts(), source="ais",
            contact_type=ContactType.VESSEL, lat=57.5, lon=19.0,
            speed=8.0, heading=45.0, confidence=0.85, entity_id="E1",
            is_hostile=False, attributes={},
        ))
        store._fused_tracks = [_fused_track("E1")]
        store._targets = [_target("E1")]
        store._coa_optimization = "fake"
        store._operational_effects = compute_operational_effects({"sea_state": 5})

        # Clear
        store.clear()

        # Verify COP is clean
        cop = assemble_cop(store)
        assert len(cop.contacts) == 0
        assert len(cop.targets) == 0
        assert len(cop.fused_tracks) == 0
        assert cop.operational_effects == {}


# ---------------------------------------------------------------------------
# No-LLM guarantee
# ---------------------------------------------------------------------------


class TestPersistenceNoLLM:
    def test_save_restore_no_llm(self, monkeypatch, tmp_path):
        def fail_llm(*args, **kwargs):
            raise AssertionError("LLM must not be called during persistence")

        monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm)

        db_path = str(tmp_path / "test.db")
        store = PersistentStateStore(db_path=db_path)
        store.ingest_contact(Contact(
            contact_id="C-E1", timestamp=_ts(), source="ais",
            contact_type=ContactType.VESSEL, lat=57.5, lon=19.0,
            speed=8.0, heading=45.0, confidence=0.85, entity_id="E1",
            is_hostile=False, attributes={},
        ))
        store.save()
        store2 = PersistentStateStore(db_path=db_path)
        assert store2.restore()
        assert len(store2.get_contacts()) == 1
        store.close()
        store2.close()
