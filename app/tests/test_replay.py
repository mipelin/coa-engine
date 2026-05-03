"""Tests for replay, after-action review, and lessons-learned workflow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core.constants import EntityType, EventType, ThreatLevel
from app.core.schemas import (
    AnomalyResult,
    AnomalyLevel,
    Contact,
    ContactType,
    CourseOfAction,
    OperationalEvent,
    Recommendation,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from app.engine.analysis_service import AnalysisContext, run_canonical_analysis
from app.engine.coa_optimizer import OptimizationResult
from app.engine.fusion import FusedTrack
from app.engine.operational_effects import OperationalEffects, compute_operational_effects
from app.engine.replay import (
    AfterActionReview,
    ReplaySnapshot,
    ReplayStore,
    ReplayTimeline,
    capture_snapshot,
    generate_aar,
    get_replay_store,
)
from app.engine.targeting import Target
from app.engine.state_store import StateStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ts(minutes: int = 0) -> datetime:
    return datetime(2025, 6, 15, 8, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def _threat(entity_id="E1", level="MEDIUM", prob=0.4) -> ThreatResult:
    return ThreatResult(
        entity_id=entity_id,
        threat_probability=prob,
        threat_level=ThreatLevel(level),
        confidence=0.8,
        main_drivers=["proximity"],
    )


def _scored_coa(coa_id="COA-1", title="Test COA", score=70.0, roe="allowed") -> ScoredCOA:
    coa = CourseOfAction(
        coa_id=coa_id, template_id="COA-TPL-ISR",
        title=title, description="Test",
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


def _recommendation(scored=None) -> Recommendation:
    s = scored or _scored_coa()
    return Recommendation(recommended=s, alternatives=[], rationale="Test", edge_cases="")


def _target(entity_id="E1") -> Target:
    return Target(
        id=entity_id, type="vessel", classification_confidence=0.85,
        threat_score=0.4, priority_score=45.0, priority_level="MEDIUM",
        recommended_action="track", roe_status="allowed",
        rationale="Test", sources=["ais"],
    )


def _build_snapshots(n=10, *, threat_start="LOW", threat_end="HIGH",
                     coa_id="COA-1", effects=None) -> list[ReplaySnapshot]:
    """Build a synthetic sequence of snapshots for testing."""
    snaps = []
    threat_levels = _interpolate_levels(threat_start, threat_end, n)
    for i in range(n):
        fx = effects or {}
        snaps.append(ReplaySnapshot(
            tick=i + 1,
            timestamp=_ts(i * 2).isoformat(),
            scenario_id="test_scenario",
            threat_level=threat_levels[i],
            top_threat_entity="E1",
            top_threat_probability=0.3 + 0.5 * i / max(n - 1, 1),
            threat_count=2,
            recommended_coa_id=coa_id if i < n - 1 else "COA-2",
            recommended_coa_title=f"COA {coa_id}" if i < n - 1 else "COA COA-2",
            recommended_coa_score=70.0 - i * 2,
            recommended_roe_status="allowed" if i < n // 2 else "restricted",
            operational_effects_summary=fx,
            contacts_count=3 + i,
            coas_count=4,
        ))
    return snaps


def _interpolate_levels(start: str, end: str, n: int) -> list[str]:
    order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    names = {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}
    s = order.get(start, 0)
    e = order.get(end, 0)
    levels = []
    for i in range(n):
        frac = i / max(n - 1, 1)
        idx = s + (e - s) * frac
        levels.append(names.get(min(round(idx), 3), start))
    return levels


# ---------------------------------------------------------------------------
# Snapshot capture
# ---------------------------------------------------------------------------


class TestSnapshotCapture:
    def test_capture_basic_snapshot(self):
        threats = [_threat("E1", "HIGH", 0.7)]
        scored = [_scored_coa()]
        rec = _recommendation(scored[0])

        snap = capture_snapshot(
            tick=5,
            threats=threats,
            scored=scored,
            recommendation=rec,
            scenario_id="test",
        )
        assert snap.tick == 5
        assert snap.threat_level == "HIGH"
        assert snap.top_threat_entity == "E1"
        assert snap.recommended_coa_id == "COA-1"
        assert snap.scenario_id == "test"

    def test_capture_empty_state(self):
        snap = capture_snapshot(tick=0)
        assert snap.tick == 0
        assert snap.threat_level == "LOW"
        assert snap.recommended_coa_id is None

    def test_capture_with_optimization(self):
        coa = CourseOfAction(
            coa_id="OPT-1", template_id="COA-TPL-ISR",
            title="Optimized", description="",
            target_entities=[], required_assets=[], assumptions=[],
            estimated_time_minutes=30, expected_effect="",
            risk_categories=[], escalation_risk=0.1,
            civilian_risk=0.02, logistics_burden=0.3,
        )
        sim = SimulationResult(
            coa_id="OPT-1", success_probability=0.8, expected_time_to_effect=25.0,
            risk_to_second_cable=0.1, escalation_probability=0.1,
            missed_detection_probability=0.1, confidence_interval=(0.7, 0.9),
            simulation_runs=100,
        )
        opt_scored = ScoredCOA(coa=coa, simulation=sim, total_score=85.0, rank=1,
                               tradeoff_explanation="Optimized variant")
        opt = OptimizationResult(
            optimized_variants=[opt_scored],
            best_variant=opt_scored,
            robustness_ranking=[],
            variant_parameters=[],
            optimization_summary={"status": "ok"},
        )
        snap = capture_snapshot(tick=1, coa_optimization=opt)
        assert snap.optimized_variant_id == "OPT-1"
        assert snap.optimized_variant_score == 85.0

    def test_capture_with_operational_effects(self):
        effects = compute_operational_effects(
            {"sea_state": 7, "visibility": "fog"},
            jamming_intensity="high",
        )
        snap = capture_snapshot(tick=1, operational_effects=effects)
        assert snap.operational_effects_summary["overall_effectiveness"] < 0.8
        assert len(snap.operational_effects_summary.get("active_effects", [])) > 0

    def test_capture_with_targets(self):
        targets = [_target("E1"), _target("E2")]
        snap = capture_snapshot(tick=1, targets=targets)
        assert len(snap.top_targets) == 2
        assert snap.top_targets[0]["entity_id"] == "E1"

    def test_capture_roe_summary(self):
        scored = [
            _scored_coa("COA-1", roe="allowed"),
            _scored_coa("COA-2", roe="restricted"),
            _scored_coa("COA-3", roe="rejected"),
        ]
        snap = capture_snapshot(tick=1, scored=scored)
        assert snap.roe_summary["allowed"] == 1
        assert snap.roe_summary["restricted"] == 1
        assert snap.roe_summary["rejected"] == 1

    def test_snapshot_to_dict(self):
        snap = capture_snapshot(tick=1, scenario_id="s1")
        d = snap.to_dict()
        assert isinstance(d, dict)
        assert d["tick"] == 1
        assert d["scenario_id"] == "s1"

    def test_snapshot_serializable(self):
        import json
        snap = capture_snapshot(tick=1)
        d = snap.to_dict()
        serialized = json.dumps(d)
        assert isinstance(serialized, str)


# ---------------------------------------------------------------------------
# ReplayStore
# ---------------------------------------------------------------------------


class TestReplayStore:
    def test_add_and_retrieve(self):
        store = ReplayStore()
        store.add_snapshot(ReplaySnapshot(tick=1))
        store.add_snapshot(ReplaySnapshot(tick=2))
        assert store.snapshot_count == 2

    def test_get_snapshot_by_tick(self):
        store = ReplayStore()
        store.add_snapshot(ReplaySnapshot(tick=5, scenario_id="test"))
        snap = store.get_snapshot(5)
        assert snap is not None
        assert snap.tick == 5

    def test_get_snapshot_not_found(self):
        store = ReplayStore()
        assert store.get_snapshot(99) is None

    def test_timeline(self):
        store = ReplayStore()
        store.add_snapshot(ReplaySnapshot(tick=1, scenario_id="s1"))
        store.add_snapshot(ReplaySnapshot(tick=2, scenario_id="s1"))
        store.add_snapshot(ReplaySnapshot(tick=3, scenario_id="s1"))
        timeline = store.get_timeline()
        assert timeline.start_tick == 1
        assert timeline.end_tick == 3
        assert len(timeline.snapshots) == 3

    def test_cap_snapshots(self):
        store = ReplayStore()
        # Override max for test
        import app.engine.replay as replay_mod
        from app.core.config import settings
        original = settings.replay_max_snapshots
        settings.replay_max_snapshots = 5
        try:
            for i in range(10):
                store.add_snapshot(ReplaySnapshot(tick=i + 1))
            assert store.snapshot_count == 5
            assert store.first_tick == 6  # oldest 5 trimmed
            assert store.last_tick == 10
        finally:
            settings.replay_max_snapshots = original

    def test_clear(self):
        store = ReplayStore()
        store.add_snapshot(ReplaySnapshot(tick=1))
        store.clear()
        assert store.snapshot_count == 0
        assert store.first_tick is None

    def test_empty_timeline(self):
        store = ReplayStore()
        timeline = store.get_timeline()
        assert len(timeline.snapshots) == 0

    def test_last_major_change(self):
        store = ReplayStore()
        store.add_snapshot(ReplaySnapshot(tick=1, key_changes=[]))
        store.add_snapshot(ReplaySnapshot(tick=2, key_changes=["Threat level changed to HIGH"]))
        store.add_snapshot(ReplaySnapshot(tick=3, key_changes=[]))
        change = store.get_last_major_change()
        assert change is not None
        assert change["tick"] == 2
        assert "Threat level" in change["changes"][0]

    def test_last_major_change_none(self):
        store = ReplayStore()
        store.add_snapshot(ReplaySnapshot(tick=1))
        assert store.get_last_major_change() is None

    def test_latest_lesson(self):
        fx = {"active_effects": ["Jamming high: sensor degradation"]}
        store = ReplayStore()
        store.add_snapshot(ReplaySnapshot(tick=1, operational_effects_summary=fx))
        store.add_snapshot(ReplaySnapshot(tick=2, operational_effects_summary=fx))
        lesson = store.get_latest_lesson()
        assert lesson is not None
        assert "Jamming" in lesson


# ---------------------------------------------------------------------------
# AAR generation
# ---------------------------------------------------------------------------


class TestAARGeneration:
    def test_aar_from_empty_timeline(self):
        timeline = ReplayTimeline()
        aar = generate_aar(timeline)
        assert isinstance(aar, AfterActionReview)
        assert "No replay data" in aar.situation_summary

    def test_aar_basic_structure(self):
        snaps = _build_snapshots(5)
        timeline = ReplayTimeline(scenario_id="test", snapshots=snaps, start_tick=1, end_tick=5)
        aar = generate_aar(timeline)
        assert aar.scenario_id == "test"
        assert aar.duration_ticks == 4
        assert aar.situation_summary
        assert isinstance(aar.threat_evolution, list)
        assert isinstance(aar.recommendation_timeline, list)
        assert isinstance(aar.lessons_learned, list)
        assert isinstance(aar.remaining_risks, list)

    def test_aar_threat_escalation(self):
        snaps = _build_snapshots(10, threat_start="LOW", threat_end="HIGH")
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=10)
        aar = generate_aar(timeline)
        assert len(aar.threat_evolution) > 1
        assert aar.threat_evolution[0]["threat_level"] == "LOW"
        assert aar.threat_evolution[-1]["threat_level"] == "HIGH"
        # Should have a lesson about escalation
        assert any("escalated" in l.lower() for l in aar.lessons_learned)

    def test_aar_recommendation_changes(self):
        snaps = _build_snapshots(8)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=8)
        aar = generate_aar(timeline)
        # Last snapshot switches to COA-2
        assert len(aar.recommendation_timeline) >= 1
        rec_ids = [r["coa_id"] for r in aar.recommendation_timeline]
        assert "COA-2" in rec_ids

    def test_aar_target_evolution(self):
        snaps = _build_snapshots(5)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=5)
        aar = generate_aar(timeline)
        assert isinstance(aar.target_evolution, list)

    def test_aar_operational_effects_observed(self):
        fx = {"active_effects": ["Sea state 7: sensor effectiveness 48%"]}
        snaps = _build_snapshots(5, effects=fx)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=5)
        aar = generate_aar(timeline)
        assert len(aar.effects_observed) > 0
        assert any("Sea state" in e for e in aar.effects_observed)

    def test_aar_jamming_lesson(self):
        fx = {"active_effects": ["Jamming high: sensor degradation"]}
        snaps = _build_snapshots(5, effects=fx)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=5)
        aar = generate_aar(timeline)
        assert any("Jamming" in l for l in aar.lessons_learned)

    def test_aar_sea_state_lesson(self):
        fx = {"active_effects": ["Sea state 8 (Gale): sensor effectiveness 35%"]}
        snaps = _build_snapshots(5, effects=fx)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=5)
        aar = generate_aar(timeline)
        assert any("sea state" in l.lower() for l in aar.lessons_learned)

    def test_aar_visibility_lesson(self):
        fx = {"active_effects": ["Visibility fog: confidence 35%, ISR penalty 45%"]}
        snaps = _build_snapshots(5, effects=fx)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=5)
        aar = generate_aar(timeline)
        assert any("visibility" in l.lower() or "ISR" in l for l in aar.lessons_learned)

    def test_aar_roe_lesson(self):
        snaps = _build_snapshots(10)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=10)
        aar = generate_aar(timeline)
        # More than 30% of snapshots have restricted ROE
        assert any("ROE" in l for l in aar.lessons_learned)

    def test_aar_remaining_risks_high_threat(self):
        snaps = _build_snapshots(5, threat_start="MEDIUM", threat_end="HIGH")
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=5)
        aar = generate_aar(timeline)
        assert any("HIGH" in r for r in aar.remaining_risks)

    def test_aar_deterministic(self):
        snaps = _build_snapshots(8)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=8)
        aar1 = generate_aar(timeline)
        aar2 = generate_aar(timeline)
        assert aar1.to_dict() == aar2.to_dict()

    def test_aar_decisions_recommended(self):
        snaps = _build_snapshots(6)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=6)
        aar = generate_aar(timeline)
        assert isinstance(aar.decisions_recommended, list)
        assert len(aar.decisions_recommended) >= 1

    def test_aar_assessment_confidence(self):
        snaps = _build_snapshots(2)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=2)
        aar = generate_aar(timeline)
        assert aar.assessment_confidence == "low"  # < 3 snapshots

    def test_aar_assessment_confidence_stable(self):
        # All same threat level = stable = high confidence
        snaps = [ReplaySnapshot(tick=i + 1, threat_level="MEDIUM",
                                recommended_coa_id="COA-1", recommended_coa_title="ISR",
                                recommended_coa_score=60.0) for i in range(10)]
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=10)
        aar = generate_aar(timeline)
        assert aar.assessment_confidence == "high"


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------


class TestPipelineIntegration:
    def test_analysis_runs_with_replay(self):
        """Running canonical analysis should work alongside replay module."""
        events = [
            OperationalEvent(
                event_id="EV1", timestamp=_ts(), event_type=EventType.VESSEL_POSITION,
                source="ais", confidence=0.8, lat=57.5, lon=19.0,
                entity_id="E1", entity_type=EntityType.SUSPICIOUS_VESSEL,
                description="test", attributes={"speed_knots": 5.0, "heading": 180.0},
            ),
        ]
        ctx = AnalysisContext(events=events, source="test", tick=1)
        result = run_canonical_analysis(ctx)
        assert result.operational_effects is not None
        # Snapshot capture happens in event_loop, not in analysis_service directly


# ---------------------------------------------------------------------------
# No-LLM guarantee
# ---------------------------------------------------------------------------


class TestNoLLM:
    def test_aar_no_llm(self, monkeypatch):
        def fail_llm(*args, **kwargs):
            raise AssertionError("LLM must not be called during AAR")

        monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm)

        snaps = _build_snapshots(5)
        timeline = ReplayTimeline(snapshots=snaps, start_tick=1, end_tick=5)
        aar = generate_aar(timeline)
        assert aar.lessons_learned is not None

    def test_snapshot_no_llm(self, monkeypatch):
        def fail_llm(*args, **kwargs):
            raise AssertionError("LLM must not be called during snapshot capture")

        monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm)

        snap = capture_snapshot(tick=1, threats=[_threat()])
        assert snap.tick == 1


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------


class TestReplayEndpoints:
    @pytest.fixture(autouse=True)
    def clean_engine(self):
        from app.core.session import reset_session
        from app.engine.contact_engine import get_contact_engine
        from app.engine.event_bus import get_event_bus
        from app.engine.event_loop import get_event_loop
        from app.engine.ais_feed import get_ais_feed
        from app.engine.noaa_replay import get_noaa_replay_feed
        from app.engine.state_store import get_state_store
        from app.core.config import settings

        reset_session()
        get_contact_engine().reset()
        get_state_store().clear()
        get_event_bus().clear()
        get_event_loop().reset_runtime_state()
        get_ais_feed().reset()
        get_noaa_replay_feed().reset()
        get_replay_store().clear()
        original = settings.llm_enabled
        settings.llm_enabled = False
        import app.engine.llm_client as _lc
        _lc._llm_client = None
        yield
        settings.llm_enabled = original
        _lc._llm_client = None
        reset_session()
        get_contact_engine().reset()
        get_state_store().clear()
        get_event_bus().clear()
        get_event_loop().reset_runtime_state()
        get_ais_feed().reset()
        get_noaa_replay_feed().reset()
        get_replay_store().clear()

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_timeline_empty(self, client):
        resp = client.get("/v1/engine/replay/timeline")
        assert resp.status_code == 200
        data = resp.json()
        assert data["snapshot_count"] == 0

    def test_snapshot_not_found(self, client):
        resp = client.get("/v1/engine/replay/snapshot/99")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "not_found"

    def test_aar_no_data(self, client):
        resp = client.get("/v1/engine/replay/aar")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "no_data"

    def test_replay_after_scenario(self, client):
        """Start scenario, tick a few times, verify replay data exists."""
        client.post("/v1/engine/start", json={"scenario_id": "baltic_hybrid_001", "interval": 2.0})
        for _ in range(4):
            client.post("/v1/engine/tick")

        # Check timeline
        resp = client.get("/v1/engine/replay/timeline")
        assert resp.status_code == 200
        data = resp.json()
        assert data["snapshot_count"] > 0
        assert data["start_tick"] >= 0

        # Check AAR
        resp = client.get("/v1/engine/replay/aar")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        aar = data["aar"]
        assert aar["situation_summary"]
        assert isinstance(aar["threat_evolution"], list)

    def test_replay_snapshot_by_tick(self, client):
        client.post("/v1/engine/start", json={"scenario_id": "baltic_hybrid_001", "interval": 2.0})
        for _ in range(3):
            client.post("/v1/engine/tick")

        resp = client.get("/v1/engine/replay/timeline")
        first_tick = resp.json()["start_tick"]
        resp = client.get(f"/v1/engine/replay/snapshot/{first_tick}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["snapshot"]["tick"] == first_tick

    def test_replay_clear(self, client):
        client.post("/v1/engine/start", json={"scenario_id": "baltic_hybrid_001", "interval": 2.0})
        for _ in range(3):
            client.post("/v1/engine/tick")

        assert client.get("/v1/engine/replay/timeline").json()["snapshot_count"] > 0

        resp = client.post("/v1/engine/replay/clear")
        assert resp.status_code == 200

        assert client.get("/v1/engine/replay/timeline").json()["snapshot_count"] == 0

    def test_cop_has_replay_summary(self, client):
        client.post("/v1/engine/start", json={"scenario_id": "baltic_hybrid_001", "interval": 2.0})
        for _ in range(3):
            client.post("/v1/engine/tick")

        resp = client.get("/v1/engine/cop")
        assert resp.status_code == 200
        data = resp.json()
        assert "replay_summary" in data
        rs = data["replay_summary"]
        assert rs["snapshots_count"] > 0
        assert rs["first_tick"] is not None
        assert rs["last_tick"] is not None

    def test_cop_replay_summary_empty(self, client):
        resp = client.get("/v1/engine/cop")
        assert resp.status_code == 200
        data = resp.json()
        rs = data["replay_summary"]
        assert rs["snapshots_count"] == 0
        assert rs["first_tick"] is None
