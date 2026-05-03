"""Tests for SQLite persistence layer."""
from __future__ import annotations

import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from app.core.schemas import (
    Contact,
    ContactTrack,
    ContactType,
    ThreatResult,
    ThreatLevel,
    AnomalyResult,
    AnomalyLevel,
    CourseOfAction,
    ScoredCOA,
    SimulationResult,
    Recommendation,
    EngineState,
    AssetState,
)
from app.engine.persistence import PersistentStateStore


def _make_contact(entity_id: str = "VES-001", lat: float = 57.5, lon: float = 19.0) -> Contact:
    return Contact(
        contact_id=f"C-{entity_id}",
        timestamp=datetime.now(timezone.utc),
        source="test",
        contact_type=ContactType.VESSEL,
        lat=lat,
        lon=lon,
        speed=5.0,
        heading=90.0,
        confidence=0.9,
        entity_id=entity_id,
        is_hostile=False,
    )


def _make_threat(entity_id: str = "VES-001") -> ThreatResult:
    return ThreatResult(
        entity_id=entity_id,
        threat_probability=0.7,
        threat_level=ThreatLevel.HIGH,
        confidence=0.8,
        main_drivers=["proximity", "heading"],
    )


def _make_anomaly(event_id: str = "E-001") -> AnomalyResult:
    return AnomalyResult(
        event_id=event_id,
        entity_id="VES-001",
        anomaly_score=75.0,
        anomaly_level=AnomalyLevel.HIGH,
        explanations=["Close to cable"],
    )


def _make_coa(coa_id: str = "COA-001") -> CourseOfAction:
    return CourseOfAction(
        coa_id=coa_id,
        template_id="tpl_isr",
        title="ISR Deploy",
        description="Deploy ISR",
        required_assets=["isr_uav"],
        assumptions=["Weather clear"],
        estimated_time_minutes=30,
        expected_effect="Enhanced coverage",
        risk_categories=["escalation"],
        escalation_risk=0.2,
        civilian_risk=0.1,
        logistics_burden=0.3,
    )


def _make_simulation(coa_id: str = "COA-001") -> SimulationResult:
    return SimulationResult(
        coa_id=coa_id,
        success_probability=0.8,
        expected_time_to_effect=25.0,
        risk_to_second_cable=0.1,
        escalation_probability=0.15,
        missed_detection_probability=0.05,
        confidence_interval=(0.6, 0.95),
        simulation_runs=1000,
    )


def _make_scored_coa(coa_id: str = "COA-001", rank: int = 1) -> ScoredCOA:
    return ScoredCOA(
        coa=_make_coa(coa_id),
        simulation=_make_simulation(coa_id),
        total_score=85.0,
        rank=rank,
        tradeoff_explanation="Good coverage",
    )


def _make_recommendation() -> Recommendation:
    return Recommendation(
        recommended=_make_scored_coa("COA-001", 1),
        alternatives=[_make_scored_coa("COA-002", 2)],
        rationale="Best option",
        edge_cases="None",
    )


def _tmp_db() -> str:
    return str(Path(tempfile.mkdtemp()) / "test_state.db")


class TestSaveAndRestore:
    def test_save_and_restore_roundtrip(self):
        db = _tmp_db()
        store = PersistentStateStore(db_path=db)
        # Suppress auto-save so explicit save is authoritative
        store._debounce_seconds = 9999.0

        store.ingest_contact(_make_contact("VES-001"))
        store.ingest_contact(_make_contact("VES-002", lat=58.0))
        store.set_infrastructure([{"name": "Cable A", "lat": 57.0, "lon": 18.0, "type": "cable"}])
        store.set_asset_states(asset_states=[
            AssetState(asset_id="uav_1", asset_type="uav", quantity_total=2, quantity_available=1),
        ])
        store.save()

        store2 = PersistentStateStore(db_path=db)
        assert store2.restore() is True

        contacts = store2.get_contacts()
        assert len(contacts) == 2
        entity_ids = {c.entity_id for c in contacts}
        assert entity_ids == {"VES-001", "VES-002"}

        infra = store2.get_infrastructure()
        assert len(infra) == 1
        assert infra[0]["name"] == "Cable A"

        assets = store2.get_asset_states()
        assert len(assets) == 1
        assert assets[0].asset_id == "uav_1"

        store.close()
        store2.close()

    def test_restore_analysis_results(self):
        db = _tmp_db()
        store = PersistentStateStore(db_path=db)
        store._debounce_seconds = 9999.0

        store.ingest_contact(_make_contact("VES-001"))
        threat = _make_threat("VES-001")
        anomaly = _make_anomaly("E-001")
        scored = _make_scored_coa("COA-001", 1)
        coa = _make_coa("COA-001")
        sim = _make_simulation("COA-001")
        rec = _make_recommendation()
        store.update_analysis([threat], [anomaly], [scored], rec, [coa], [sim])
        store.save()

        store2 = PersistentStateStore(db_path=db)
        store2.restore()

        threats = store2.get_threats()
        assert len(threats) == 1
        assert threats[0].entity_id == "VES-001"
        assert threats[0].threat_probability == 0.7

        scored_coas = store2.get_scored_coas()
        assert len(scored_coas) == 1
        assert scored_coas[0].total_score == 85.0

        rec2 = store2.get_recommendation()
        assert rec2 is not None
        assert rec2.rationale == "Best option"

        store.close()
        store2.close()

    def test_restore_from_empty_db(self):
        db = _tmp_db()
        store = PersistentStateStore(db_path=db)
        assert store.restore() is False
        assert len(store.get_contacts()) == 0
        store.close()

    def test_restore_preserves_tick(self):
        db = _tmp_db()
        store = PersistentStateStore(db_path=db)
        store._debounce_seconds = 9999.0
        store.advance_tick()
        store.advance_tick()
        store.advance_tick()
        store.save()

        store2 = PersistentStateStore(db_path=db)
        store2.restore()
        assert store2.get_tick() == 3
        store.close()
        store2.close()

    def test_clear_persists(self):
        db = _tmp_db()
        store = PersistentStateStore(db_path=db)
        store._debounce_seconds = 9999.0
        store.ingest_contact(_make_contact("VES-001"))
        store.save()
        store.clear()
        store.save()

        store2 = PersistentStateStore(db_path=db)
        store2.restore()
        assert len(store2.get_contacts()) == 0
        assert store2.get_tick() == 0
        store.close()
        store2.close()

    def test_wal_mode_enabled(self):
        db = _tmp_db()
        store = PersistentStateStore(db_path=db)
        conn = sqlite3.connect(db)
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        assert mode == "wal"
        store.close()


class TestAutoSave:
    def test_auto_save_triggers_on_ingest(self):
        db = _tmp_db()
        store = PersistentStateStore(db_path=db)
        store._debounce_seconds = 0.0
        store.ingest_contact(_make_contact("VES-001"))
        store.flush()

        store2 = PersistentStateStore(db_path=db)
        restored = store2.restore()
        assert restored is True
        contacts = store2.get_contacts()
        assert len(contacts) >= 1
        store.close()
        store2.close()

    def test_auto_save_triggers_on_clear(self):
        db = _tmp_db()
        store = PersistentStateStore(db_path=db)
        store._debounce_seconds = 0.0
        store.ingest_contact(_make_contact("VES-001"))
        store.save()
        store.clear()
        store.flush()

        store2 = PersistentStateStore(db_path=db)
        store2.restore()
        assert len(store2.get_contacts()) == 0
        store.close()
        store2.close()

    def test_debounce_prevents_rapid_saves(self):
        db = _tmp_db()
        store = PersistentStateStore(db_path=db)
        store._debounce_seconds = 999.0

        store.ingest_contact(_make_contact("VES-001"))
        conn = sqlite3.connect(db)
        row = conn.execute("SELECT contacts FROM engine_state WHERE id = 1").fetchone()
        conn.close()
        if row is not None:
            contacts = json.loads(row[0])
            assert len(contacts) == 0
        store.close()


class TestContactTrackSerialization:
    def test_contact_track_positions_roundtrip(self):
        """ContactTrack has list[tuple[datetime,float,float]] — verify it survives JSON."""
        db = _tmp_db()
        store = PersistentStateStore(db_path=db)
        store._debounce_seconds = 9999.0

        contact = Contact(
            contact_id="C-001",
            timestamp=datetime(2025, 6, 15, 8, 0, 0, tzinfo=timezone.utc),
            source="test",
            contact_type=ContactType.VESSEL,
            lat=57.5,
            lon=19.0,
            speed=5.0,
            heading=90.0,
            entity_id="VES-001",
        )
        store.ingest_contact(contact)
        store.save()

        store2 = PersistentStateStore(db_path=db)
        store2.restore()
        tracks = store2.get_tracks()
        assert "VES-001" in tracks
        track = tracks["VES-001"]
        assert len(track.positions) == 1
        pos = track.positions[0]
        assert pos[1] == 57.5
        assert pos[2] == 19.0
        store.close()
        store2.close()
