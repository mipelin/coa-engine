"""Tests for ROE engine and event engine."""

from datetime import datetime, timezone

import pytest

from app.core.constants import EventType
from app.core.schemas import (
    CourseOfAction,
    OperationalEvent,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from app.engine.event_engine import (
    EventEffect,
    ExternalEvent,
    ExternalEventType,
    process_event,
)
from app.engine.roe_engine import (
    DEFAULT_ROE,
    ROEAction,
    ROEConfig,
    TEMPLATE_ROE_ACTION,
    evaluate_roe,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_coa(template_id: str, escalation_risk: float = 0.05, civilian_risk: float = 0.0) -> CourseOfAction:
    return CourseOfAction(
        coa_id=template_id,
        template_id=template_id,
        title=f"COA {template_id}",
        description="test",
        required_assets=["isr_uav"],
        assumptions=["test"],
        estimated_time_minutes=30,
        expected_effect="test",
        risk_categories=["test"],
        escalation_risk=escalation_risk,
        civilian_risk=civilian_risk,
        logistics_burden=0.2,
    )


def _make_sim(coa_id: str) -> SimulationResult:
    return SimulationResult(
        coa_id=coa_id,
        success_probability=0.7,
        expected_time_to_effect=30.0,
        risk_to_second_cable=0.1,
        escalation_probability=0.1,
        missed_detection_probability=0.1,
        confidence_interval=(0.4, 0.9),
        simulation_runs=100,
    )


def _make_scored(template_id: str, escalation_risk: float = 0.05, civilian_risk: float = 0.0) -> ScoredCOA:
    coa = _make_coa(template_id, escalation_risk, civilian_risk)
    sim = _make_sim(template_id)
    return ScoredCOA(coa=coa, simulation=sim, total_score=70.0, rank=1, tradeoff_explanation="test")


def _make_threat(level: str = "HIGH", confidence: float = 0.8) -> ThreatResult:
    return ThreatResult(
        entity_id="VES-1",
        threat_probability=0.7,
        threat_level=level,
        confidence=confidence,
        main_drivers=["test"],
    )


# ---------------------------------------------------------------------------
# ROE category mapping
# ---------------------------------------------------------------------------


class TestROECategoryMapping:
    def test_isr_maps_to_observe_isr(self):
        assert TEMPLATE_ROE_ACTION["COA-TPL-ISR"] == ROEAction.observe_isr

    def test_baseline_maps_to_monitor(self):
        assert TEMPLATE_ROE_ACTION["COA-TPL-BASELINE"] == ROEAction.monitor

    def test_border_maps_to_monitor(self):
        assert TEMPLATE_ROE_ACTION["COA-TPL-BORDER"] == ROEAction.monitor

    def test_airspace_maps_to_coordinate(self):
        assert TEMPLATE_ROE_ACTION["COA-TPL-AIRSPACE"] == ROEAction.coordinate

    def test_reinforce_maps_to_request_support(self):
        assert TEMPLATE_ROE_ACTION["COA-TPL-REINFORCE"] == ROEAction.request_support

    def test_shadow_maps_to_shadow(self):
        assert TEMPLATE_ROE_ACTION["COA-TPL-SHADOW"] == ROEAction.shadow

    def test_cable_protect_maps_to_protect_infrastructure(self):
        assert TEMPLATE_ROE_ACTION["COA-TPL-CABLE-PROTECT"] == ROEAction.protect_infrastructure

    def test_combined_maps_to_combined_assertive(self):
        assert TEMPLATE_ROE_ACTION["COA-TPL-COMBINED"] == ROEAction.combined_assertive

    def test_unknown_template_defaults_to_monitor(self):
        assert TEMPLATE_ROE_ACTION.get("COA-TPL-UNKNOWN", ROEAction.monitor) == ROEAction.monitor


# ---------------------------------------------------------------------------
# ROE Engine — monitor / observe_isr / coordinate / request_support
# ---------------------------------------------------------------------------


class TestROEMonitorCategories:
    def test_isr_allowed_at_low_threat(self):
        scored = [_make_scored("COA-TPL-ISR")]
        result = evaluate_roe(scored, [_make_threat("LOW")])
        assert result[0].coa.roe_status == "allowed"

    def test_baseline_always_allowed(self):
        scored = [_make_scored("COA-TPL-BASELINE")]
        result = evaluate_roe(scored, [_make_threat("LOW")])
        assert result[0].coa.roe_status == "allowed"

    def test_border_always_allowed(self):
        scored = [_make_scored("COA-TPL-BORDER")]
        result = evaluate_roe(scored, [_make_threat("LOW")])
        assert result[0].coa.roe_status == "allowed"

    def test_airspace_always_allowed(self):
        scored = [_make_scored("COA-TPL-AIRSPACE")]
        result = evaluate_roe(scored, [_make_threat("LOW")])
        assert result[0].coa.roe_status == "allowed"

    def test_reinforce_always_allowed(self):
        scored = [_make_scored("COA-TPL-REINFORCE")]
        result = evaluate_roe(scored, [_make_threat("LOW")])
        assert result[0].coa.roe_status == "allowed"


# ---------------------------------------------------------------------------
# ROE Engine — shadow
# ---------------------------------------------------------------------------


class TestROEShadow:
    def test_shadow_allowed_at_medium(self):
        scored = [_make_scored("COA-TPL-SHADOW")]
        result = evaluate_roe(scored, [_make_threat("MEDIUM")])
        assert result[0].coa.roe_status == "allowed"

    def test_shadow_allowed_at_high(self):
        scored = [_make_scored("COA-TPL-SHADOW")]
        result = evaluate_roe(scored, [_make_threat("HIGH")])
        assert result[0].coa.roe_status == "allowed"

    def test_shadow_rejected_at_low(self):
        scored = [_make_scored("COA-TPL-SHADOW")]
        result = evaluate_roe(scored, [_make_threat("LOW")])
        assert result[0].coa.roe_status == "rejected"
        assert "min_threat_for_shadow" in result[0].coa.roe_constraints_triggered


# ---------------------------------------------------------------------------
# ROE Engine — protect_infrastructure (CABLE-PROTECT)
# ---------------------------------------------------------------------------


class TestROEProtectInfrastructure:
    def test_protect_allowed_at_medium_with_good_confidence(self):
        scored = [_make_scored("COA-TPL-CABLE-PROTECT")]
        result = evaluate_roe(scored, [_make_threat("MEDIUM")], confidence=0.8)
        assert result[0].coa.roe_status == "allowed"

    def test_protect_allowed_at_high(self):
        scored = [_make_scored("COA-TPL-CABLE-PROTECT")]
        result = evaluate_roe(scored, [_make_threat("HIGH")], confidence=0.8)
        assert result[0].coa.roe_status == "allowed"

    def test_protect_requires_authorization_at_low(self):
        """Not bluntly rejected — protection may proceed with authorization."""
        scored = [_make_scored("COA-TPL-CABLE-PROTECT")]
        result = evaluate_roe(scored, [_make_threat("LOW")], confidence=0.8)
        assert result[0].coa.roe_status == "requires_authorization"
        assert "low_threat_for_protection" in result[0].coa.roe_constraints_triggered

    def test_protect_requires_authorization_with_low_confidence(self):
        scored = [_make_scored("COA-TPL-CABLE-PROTECT")]
        result = evaluate_roe(scored, [_make_threat("MEDIUM")], confidence=0.3)
        assert result[0].coa.roe_status == "requires_authorization"
        assert "low_confidence_protection" in result[0].coa.roe_constraints_triggered

    def test_protect_near_civilian_requires_authorization(self):
        scored = [_make_scored("COA-TPL-CABLE-PROTECT")]
        result = evaluate_roe(
            scored, [_make_threat("HIGH")], confidence=0.8, civilian_proximity=True,
        )
        assert result[0].coa.roe_status == "requires_authorization"
        assert "civilian_proximity" in result[0].coa.roe_constraints_triggered


# ---------------------------------------------------------------------------
# ROE Engine — combined_assertive (COMBINED)
# ---------------------------------------------------------------------------


class TestROECombinedAssertive:
    def test_combined_restricted_at_medium(self):
        """Allowed to proceed but flagged as restricted due to operational risk."""
        scored = [_make_scored("COA-TPL-COMBINED")]
        result = evaluate_roe(scored, [_make_threat("MEDIUM")], confidence=0.8)
        assert result[0].coa.roe_status == "restricted"
        assert "combined_assertive_action" in result[0].coa.roe_constraints_triggered

    def test_combined_restricted_at_high(self):
        """Even at HIGH threat, combined response is restricted, not flat allowed."""
        scored = [_make_scored("COA-TPL-COMBINED")]
        result = evaluate_roe(scored, [_make_threat("HIGH")], confidence=0.8)
        assert result[0].coa.roe_status == "restricted"

    def test_combined_requires_authorization_at_low(self):
        """Not rejected outright — shadow/ISR parts may still be valid."""
        scored = [_make_scored("COA-TPL-COMBINED")]
        result = evaluate_roe(scored, [_make_threat("LOW")], confidence=0.8)
        assert result[0].coa.roe_status == "requires_authorization"
        assert "low_threat_for_combined" in result[0].coa.roe_constraints_triggered

    def test_combined_requires_authorization_with_low_confidence(self):
        scored = [_make_scored("COA-TPL-COMBINED")]
        result = evaluate_roe(scored, [_make_threat("HIGH")], confidence=0.3)
        assert result[0].coa.roe_status == "requires_authorization"
        assert "low_confidence_combined" in result[0].coa.roe_constraints_triggered

    def test_combined_near_civilian_requires_authorization(self):
        scored = [_make_scored("COA-TPL-COMBINED")]
        result = evaluate_roe(
            scored, [_make_threat("HIGH")], confidence=0.9, civilian_proximity=True,
        )
        assert result[0].coa.roe_status == "requires_authorization"
        assert "civilian_proximity" in result[0].coa.roe_constraints_triggered


# ---------------------------------------------------------------------------
# ROE Engine — escalation policy
# ---------------------------------------------------------------------------


class TestROEEscalation:
    def test_high_escalation_restricted_by_default(self):
        scored = [_make_scored("COA-TPL-ISR", escalation_risk=0.4)]
        result = evaluate_roe(scored, [_make_threat("MEDIUM")])
        assert result[0].coa.roe_status == "restricted"
        assert "escalation_risk_exceeded" in result[0].coa.roe_constraints_triggered

    def test_high_escalation_rejected_with_reject_policy(self):
        roe = ROEConfig(escalation_policy="reject")
        scored = [_make_scored("COA-TPL-ISR", escalation_risk=0.4)]
        result = evaluate_roe(scored, [_make_threat("MEDIUM")], roe=roe)
        assert result[0].coa.roe_status == "rejected"

    def test_high_escalation_flagged_with_flag_policy(self):
        roe = ROEConfig(escalation_policy="flag")
        scored = [_make_scored("COA-TPL-ISR", escalation_risk=0.4)]
        result = evaluate_roe(scored, [_make_threat("MEDIUM")], roe=roe)
        assert result[0].coa.roe_status == "allowed"
        assert "escalation_risk_exceeded" in result[0].coa.roe_constraints_triggered


# ---------------------------------------------------------------------------
# ROE Engine — mixed COAs
# ---------------------------------------------------------------------------


class TestROEMultipleCOAs:
    def test_mixed_statuses_across_coas(self):
        scored = [
            _make_scored("COA-TPL-ISR"),
            _make_scored("COA-TPL-SHADOW"),
            _make_scored("COA-TPL-CABLE-PROTECT"),
        ]
        result = evaluate_roe(scored, [_make_threat("LOW")])
        statuses = {s.coa.template_id: s.coa.roe_status for s in result}
        assert statuses["COA-TPL-ISR"] == "allowed"
        assert statuses["COA-TPL-SHADOW"] == "rejected"
        # protect_infrastructure is requires_authorization at LOW, not rejected
        assert statuses["COA-TPL-CABLE-PROTECT"] == "requires_authorization"


# ---------------------------------------------------------------------------
# Event Engine tests
# ---------------------------------------------------------------------------


class TestEventEngineCableSevered:
    def test_cable_severed_updates_active_incidents(self):
        event = ExternalEvent(
            event_id="E-CABLE-001",
            event_type=ExternalEventType.CABLE_SEVERED,
            source="cable_monitor",
            attributes={"cable_name": "Baltic Cable Alpha"},
        )
        effect = process_event(event, active_incidents=[])
        assert effect.active_incidents_updated
        assert effect.requires_recalculation
        assert "Baltic Cable Alpha" in effect.messages[0]

    def test_cable_severed_does_not_duplicate_incident(self):
        event = ExternalEvent(
            event_id="E-CABLE-002",
            event_type=ExternalEventType.CABLE_SEVERED,
            source="cable_monitor",
            attributes={"cable_name": "Baltic Cable Alpha"},
        )
        effect = process_event(event, active_incidents=["Baltic Cable Alpha"])
        assert effect.active_incidents_updated
        assert effect.requires_recalculation


class TestEventEngineJamming:
    def test_jamming_triggers_recalculation(self):
        event = ExternalEvent(
            event_id="E-JAM-001",
            event_type=ExternalEventType.JAMMING_DETECTED,
            source="sigint",
            attributes={"jamming_id": "JAM-AREA-1"},
        )
        effect = process_event(event, active_incidents=[])
        assert effect.requires_recalculation
        assert effect.active_incidents_updated


class TestEventEngineCourseChange:
    def test_vessel_course_change_updates_entity_context(self):
        event = ExternalEvent(
            event_id="E-COURSE-001",
            event_type=ExternalEventType.VESSEL_COURSE_CHANGE,
            source="ais",
            affected_entities=["VES-SUSP-001"],
        )
        effect = process_event(event)
        assert effect.updated_entity_ids == ["VES-SUSP-001"]
        assert effect.state_updated


class TestEventEngineHostileIntent:
    def test_hostile_intent_adds_entities_to_incidents(self):
        event = ExternalEvent(
            event_id="E-HOSTILE-001",
            event_type=ExternalEventType.HOSTILE_INTENT_OBSERVED,
            source="intelligence",
            affected_entities=["VES-SUSP-001", "VES-SUSP-002"],
            severity="high",
        )
        effect = process_event(event, active_incidents=[])
        assert effect.active_incidents_updated
        assert effect.requires_recalculation
        assert "VES-SUSP-001" in effect.updated_entity_ids
        assert "VES-SUSP-002" in effect.updated_entity_ids


class TestEventEngineAssetStatus:
    def test_asset_status_change_triggers_recalc(self):
        event = ExternalEvent(
            event_id="E-ASSET-001",
            event_type=ExternalEventType.ASSET_STATUS_CHANGE,
            source="logistics",
        )
        effect = process_event(event)
        assert effect.requires_recalculation


class TestEventEngineSeverity:
    def test_critical_severity_triggers_recalc_regardless_of_type(self):
        event = ExternalEvent(
            event_id="E-CRIT-001",
            event_type=ExternalEventType.SOCIAL_MEDIA_REPORT,
            source="osint",
            severity="critical",
        )
        effect = process_event(event)
        assert effect.requires_recalculation

    def test_low_severity_no_recalc_for_non_trigger_type(self):
        event = ExternalEvent(
            event_id="E-LOW-001",
            event_type=ExternalEventType.SOCIAL_MEDIA_REPORT,
            source="osint",
            severity="low",
        )
        effect = process_event(event)
        assert not effect.requires_recalculation


# ---------------------------------------------------------------------------
# Integration: rejected COAs not recommended
# ---------------------------------------------------------------------------


class TestROERecommendationFilter:
    def test_rejected_coas_not_in_recommendation(self):
        from app.engine.recommendation import recommend

        scored = [
            _make_scored("COA-TPL-ISR"),
            _make_scored("COA-TPL-SHADOW"),
        ]
        threats = [_make_threat("LOW")]
        scored = evaluate_roe(scored, threats)

        allowed = [s for s in scored if s.coa.roe_status != "rejected"]
        rec = recommend(allowed)

        assert rec.recommended is not None
        assert rec.recommended.coa.template_id == "COA-TPL-ISR"
        assert all(s.coa.roe_status != "rejected" for s in allowed)

    def test_requires_authorization_still_recommended(self):
        """requires_authorization COAs are not rejected — they appear with a warning."""
        from app.engine.recommendation import recommend

        scored = [_make_scored("COA-TPL-CABLE-PROTECT")]
        threats = [_make_threat("LOW")]
        scored = evaluate_roe(scored, threats)

        allowed = [s for s in scored if s.coa.roe_status != "rejected"]
        assert len(allowed) == 1
        assert allowed[0].coa.roe_status == "requires_authorization"

        rec = recommend(allowed)
        assert rec.recommended is not None
        assert rec.recommended.coa.roe_status == "requires_authorization"

    def test_all_rejected_yields_no_recommendation(self):
        from app.engine.recommendation import recommend

        scored = [_make_scored("COA-TPL-SHADOW")]
        threats = [_make_threat("LOW")]
        scored = evaluate_roe(scored, threats)

        allowed = [s for s in scored if s.coa.roe_status != "rejected"]
        assert len(allowed) == 0

        rec = recommend(allowed)
        assert rec.recommended is None
