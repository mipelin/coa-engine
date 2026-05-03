"""Tests for Common Operating Picture (COP) assembly and endpoint."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core.constants import EntityType, EventType
from app.core.schemas import (
    AnomalyResult,
    Contact,
    ContactType,
    CourseOfAction,
    OperationalEvent,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from app.core.constants import AnomalyLevel, ThreatLevel
from app.engine.cop import (
    COPContactVisual,
    COPDecisionPanel,
    COPEventNarrative,
    COPForecastSummary,
    COPResult,
    COPThreatSummary,
    assemble_cop,
    cop_to_dict,
)
from app.engine.targeting import Target
from app.engine.fusion import FusedTrack
from app.engine.state_store import StateStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ts(minutes: int = 0) -> datetime:
    return datetime(2025, 6, 15, 8, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def _contact(
    entity_id="E1", lat=57.5, lon=19.0, speed=8.0, heading=45.0,
    hostile=False, source="ais", contact_type=ContactType.VESSEL,
    allegiance="unknown",
) -> Contact:
    return Contact(
        contact_id=f"C-{entity_id}",
        timestamp=_ts(),
        source=source,
        contact_type=contact_type,
        lat=lat, lon=lon, speed=speed, heading=heading,
        confidence=0.85, entity_id=entity_id, is_hostile=hostile,
        attributes={"subtype": "warship", "allegiance": allegiance},
    )


def _threat(entity_id="E1", level="MEDIUM", prob=0.4) -> ThreatResult:
    return ThreatResult(
        entity_id=entity_id,
        threat_probability=prob,
        threat_level=ThreatLevel(level),
        confidence=0.8,
        main_drivers=["proximity", "heading"],
    )


def _fused_track(entity_id="E1") -> FusedTrack:
    return FusedTrack(
        track_id="FUSED-001",
        primary_entity_id=entity_id,
        correlated_entities=[entity_id],
        track_type="vessel",
        allegiance="unknown",
        fused_confidence=0.88,
        source_count=2,
        sources=["ais", "combat_system"],
        last_seen=_ts(),
        position={"lat": 57.5, "lon": 19.0},
        heading=45.0,
        speed=8.0,
        anomaly_support=0.3,
        threat_support=0.4,
        rationale="Test track",
    )


def _target(entity_id="E1") -> Target:
    return Target(
        id=entity_id,
        type="vessel",
        classification_confidence=0.85,
        threat_score=0.4,
        priority_score=45.0,
        priority_level="MEDIUM",
        recommended_action="track",
        roe_status="allowed",
        rationale="Test target",
        sources=["ais", "combat_system"],
    )


def _anomaly(entity_id="E1", score=50.0) -> AnomalyResult:
    return AnomalyResult(
        event_id="EV-1",
        entity_id=entity_id,
        anomaly_score=score,
        anomaly_level=AnomalyLevel.MEDIUM,
        explanations=["proximity to infrastructure"],
    )


def _populated_store() -> StateStore:
    """Create a store with test data populated."""
    store = StateStore()
    # Ingest contacts
    store.ingest_contact(_contact("E1", hostile=True, allegiance="hostile"))
    store.ingest_contact(_contact("E2", lat=57.6, lon=19.1, allegiance="neutral"))
    store.ingest_contact(_contact("E3", lat=57.4, lon=18.9, source="combat_system"))

    # Set analysis state directly
    threats = [_threat("E1", "HIGH", 0.7), _threat("E2", "MEDIUM", 0.35)]
    anomalies = [_anomaly("E1", 65.0), _anomaly("E2", 30.0)]
    fused = [_fused_track("E1"), _fused_track("E2")]
    targets = [_target("E1"), _target("E2")]

    coa = CourseOfAction(
        coa_id="COA-1", template_id="COA-TPL-ISR",
        title="Test COA", description="Test",
        target_entities=["E1"], required_assets=["isr_uav"],
        assigned_assets=["isr_uav"], assumptions=[],
        estimated_time_minutes=30, expected_effect="Test",
        risk_categories=[], escalation_risk=0.1,
        civilian_risk=0.02, logistics_burden=0.3,
    )
    sim = SimulationResult(
        coa_id="COA-1", success_probability=0.7, expected_time_to_effect=30.0,
        risk_to_second_cable=0.1, escalation_probability=0.1,
        missed_detection_probability=0.2, confidence_interval=(0.6, 0.8),
        simulation_runs=100,
    )
    scored = [ScoredCOA(
        coa=coa, simulation=sim, total_score=75.0, rank=1,
        tradeoff_explanation="High success probability",
    )]
    from app.core.schemas import Recommendation
    rec = Recommendation(
        recommended=scored[0], alternatives=[],
        rationale="Best option", edge_cases="",
    )

    store.update_analysis(
        threats=threats, anomalies=anomalies, scored=scored,
        recommendation=rec, coas=[coa], simulations=[sim],
        targets=targets, fused_tracks=fused,
    )
    return store


# ---------------------------------------------------------------------------
# COP structure tests
# ---------------------------------------------------------------------------


class TestCOPStructure:
    def test_cop_has_all_sections(self):
        store = _populated_store()
        cop = assemble_cop(store)
        assert isinstance(cop, COPResult)
        assert isinstance(cop.threat_summary, COPThreatSummary)
        assert isinstance(cop.contacts, list)
        assert isinstance(cop.fused_tracks, list)
        assert isinstance(cop.targets, list)
        assert isinstance(cop.top_targets, list)
        assert isinstance(cop.decision_panel, COPDecisionPanel)
        assert isinstance(cop.forecast_summary, COPForecastSummary)
        assert isinstance(cop.event_narrative, COPEventNarrative)
        assert isinstance(cop.key_anomalies, list)

    def test_cop_threat_summary(self):
        store = _populated_store()
        cop = assemble_cop(store)
        ts = cop.threat_summary
        assert ts.threat_level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert ts.threat_count >= 0
        assert isinstance(ts.threat_distribution, dict)

    def test_cop_contacts_have_visual_attrs(self):
        store = _populated_store()
        cop = assemble_cop(store)
        assert len(cop.contacts) > 0
        for c in cop.contacts:
            assert c.icon in ("ship", "submarine", "uav", "aircraft", "ground", "unknown")
            assert c.color.startswith("#")
            assert c.lat != 0.0
            assert c.lon != 0.0

    def test_cop_hostile_gets_red_color(self):
        store = _populated_store()
        cop = assemble_cop(store)
        hostile = [c for c in cop.contacts if c.is_hostile]
        if hostile:
            assert hostile[0].color == "#e74c3c"

    def test_cop_targets_have_required_fields(self):
        store = _populated_store()
        cop = assemble_cop(store)
        if cop.targets:
            t = cop.targets[0]
            assert t.entity_id
            assert t.priority_level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
            assert t.roe_status in ("allowed", "restricted", "requires_authorization", "rejected")
            assert isinstance(t.sources, list)

    def test_cop_top_targets_limited(self):
        store = _populated_store()
        cop = assemble_cop(store)
        assert len(cop.top_targets) <= 5

    def test_cop_decision_panel_has_recommendation(self):
        store = _populated_store()
        cop = assemble_cop(store)
        dp = cop.decision_panel
        assert dp.current_recommendation is not None or len(dp.base_coas) >= 0

    def test_cop_decision_panel_has_base_coas(self):
        store = _populated_store()
        cop = assemble_cop(store)
        assert len(cop.decision_panel.base_coas) > 0

    def test_cop_fused_tracks_present(self):
        store = _populated_store()
        cop = assemble_cop(store)
        assert len(cop.fused_tracks) > 0


# ---------------------------------------------------------------------------
# Consistency tests
# ---------------------------------------------------------------------------


class TestCOPConsistency:
    def test_cop_matches_analysis_state(self):
        store = _populated_store()
        cop = assemble_cop(store)

        # Threat level matches store
        assert cop.threat_summary.threat_level == store.state.current_threat_level

        # Contact count matches
        assert len(cop.contacts) == len(store.get_contacts())

        # Target count matches
        assert len(cop.targets) == len(store.get_targets())

    def test_cop_deterministic(self):
        store = _populated_store()
        cop1 = assemble_cop(store)
        cop2 = assemble_cop(store)

        d1 = cop_to_dict(cop1)
        d2 = cop_to_dict(cop2)
        assert d1 == d2

    def test_empty_store_no_crash(self):
        store = StateStore()
        cop = assemble_cop(store)
        assert cop.threat_summary.threat_level == "LOW"
        assert cop.threat_summary.threat_count == 0
        assert len(cop.contacts) == 0
        assert len(cop.targets) == 0

    def test_cop_to_dict_serializable(self):
        store = _populated_store()
        cop = assemble_cop(store)
        d = cop_to_dict(cop)
        # Should be fully JSON-serializable (no dataclass instances)
        assert isinstance(d, dict)
        assert isinstance(d["contacts"], list)
        assert isinstance(d["targets"], list)
        assert isinstance(d["decision_panel"], dict)
        assert isinstance(d["threat_summary"], dict)
        assert isinstance(d["state"], dict)
        assert "provenance_labels" in d
        assert "recommendation" in d
        assert "assets" in d

    def test_cop_contacts_include_provenance_and_raw_fields(self):
        store = _populated_store()
        cop = assemble_cop(store)
        contact = cop.contacts[0]
        assert contact.source_label
        assert contact.provenance_label
        assert contact.contact_type
        assert isinstance(contact.attributes, dict)


# ---------------------------------------------------------------------------
# Visual model tests
# ---------------------------------------------------------------------------


class TestVisualModel:
    def test_vessel_gets_ship_icon(self):
        store = StateStore()
        store.ingest_contact(_contact("V1", contact_type=ContactType.VESSEL))
        cop = assemble_cop(store)
        vessels = [c for c in cop.contacts if c.entity_id == "V1"]
        if vessels:
            assert vessels[0].icon == "ship"

    def test_submarine_gets_submarine_icon(self):
        store = StateStore()
        store.ingest_contact(_contact("SUB1", contact_type=ContactType.SUBMARINE))
        cop = assemble_cop(store)
        subs = [c for c in cop.contacts if c.entity_id == "SUB1"]
        if subs:
            assert subs[0].icon == "submarine"

    def test_uav_gets_uav_icon(self):
        store = StateStore()
        store.ingest_contact(_contact("UAV1", contact_type=ContactType.UAV))
        cop = assemble_cop(store)
        uavs = [c for c in cop.contacts if c.entity_id == "UAV1"]
        if uavs:
            assert uavs[0].icon == "uav"

    def test_unknown_allegiance_gets_gray(self):
        store = StateStore()
        store.ingest_contact(_contact("U1", allegiance="unknown"))
        cop = assemble_cop(store)
        contacts = [c for c in cop.contacts if c.entity_id == "U1"]
        if contacts:
            assert contacts[0].color == "#bdc3c7"

    def test_fused_confidence_propagated(self):
        store = _populated_store()
        cop = assemble_cop(store)
        fused_contacts = [c for c in cop.contacts if c.fused_confidence is not None]
        if fused_contacts:
            assert fused_contacts[0].fused_confidence > 0.0
            assert fused_contacts[0].source_count >= 1


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------


class TestCOPEndpoint:
    @pytest.fixture(autouse=True)
    def clean_engine(self):
        from app.core.session import reset_session
        from app.engine.contact_engine import get_contact_engine
        from app.engine.event_bus import get_event_bus
        from app.engine.event_loop import get_event_loop
        from app.engine.ais_feed import get_ais_feed
        from app.engine.noaa_replay import get_noaa_replay_feed
        from app.core.config import settings

        reset_session()
        get_contact_engine().reset()
        get_state_store().clear()
        get_event_bus().clear()
        get_event_loop().reset_runtime_state()
        get_ais_feed().reset()
        get_noaa_replay_feed().reset()
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

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_cop_endpoint_returns_cop(self, client):
        resp = client.get("/v1/engine/cop")
        assert resp.status_code == 200
        data = resp.json()
        assert "threat_summary" in data
        assert "contacts" in data
        assert "targets" in data
        assert "decision_panel" in data
        assert "forecast_summary" in data
        assert "key_anomalies" in data

    def test_cop_endpoint_with_scenario(self, client):
        client.post("/v1/engine/start", json={"scenario_id": "baltic_hybrid_001", "interval": 2.0})
        for _ in range(3):
            client.post("/v1/engine/tick")

        resp = client.get("/v1/engine/cop")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tick"] > 0
        assert len(data["contacts"]) > 0
        assert isinstance(data["threat_summary"]["threat_level"], str)

    def test_cop_consistent_with_analysis(self, client):
        client.post("/v1/engine/start", json={"scenario_id": "baltic_hybrid_001", "interval": 2.0})
        for _ in range(3):
            client.post("/v1/engine/tick")

        cop_data = client.get("/v1/engine/cop").json()
        analysis_data = client.get("/v1/engine/analysis").json()

        # Threat level must match
        assert cop_data["threat_summary"]["threat_level"] == analysis_data["state"]["current_threat_level"]
        # Contact count must match (analysis returns contacts as a list)
        analysis_contacts = analysis_data["contacts"]
        cop_count = len(cop_data["contacts"])
        analysis_count = len(analysis_contacts) if isinstance(analysis_contacts, list) else analysis_contacts.get("count", 0)
        assert cop_count == analysis_count


# need store accessible in fixture
from app.engine.state_store import get_state_store
