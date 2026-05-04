"""Tests for operational effects model: environment, logistics, jamming, second-order risks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core.constants import EntityType, EventType
from app.core.schemas import (
    Contact,
    ContactType,
    CourseOfAction,
    FeatureVector,
    OperationalEvent,
    SimulationResult,
)
from app.engine.analysis_service import AnalysisContext, run_canonical_analysis
from app.engine.operational_effects import (
    DISTANCE_EFFECTS,
    ICE_COVER_EFFECTS,
    JAMMING_INTENSITY_EFFECTS,
    READINESS_EFFECTS,
    SEA_STATE_EFFECTS,
    TIME_OF_DAY_EFFECTS,
    VISIBILITY_EFFECTS,
    WEATHER_EFFECTS,
    OperationalEffects,
    apply_effects_to_features,
    apply_effects_to_feasibility,
    compute_operational_effects,
    infer_jamming_intensity,
)
from app.engine.simulation import run_simulations


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ts(minutes: int = 0) -> datetime:
    return datetime(2025, 6, 15, 8, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def _event(
    entity_id="E1", lat=57.5, lon=19.0, source="ais",
    event_type=EventType.VESSEL_POSITION,
    entity_type=EntityType.SUSPICIOUS_VESSEL,
    confidence=0.8, heading=45.0, speed=8.0,
    timestamp_min=0,
) -> OperationalEvent:
    return OperationalEvent(
        event_id=f"EV-{entity_id}",
        timestamp=_ts(timestamp_min),
        event_type=event_type,
        source=source,
        confidence=confidence,
        lat=lat, lon=lon,
        entity_id=entity_id,
        entity_type=entity_type,
        description="test",
        attributes={"speed_knots": speed, "heading": heading},
    )


def _feature(entity_id="E1", confidence=0.8, jamming=0.0) -> FeatureVector:
    return FeatureVector(
        event_id=f"EV-{entity_id}",
        entity_id=entity_id,
        distance_to_nearest_critical_infrastructure=50.0,
        distance_to_second_cable=80.0,
        course_change_count=0,
        speed_anomaly_score=0.1,
        proximity_to_recent_incident=0.05,
        multi_source_correlation_score=0.25,
        event_density_score=0.2,
        source_confidence_weight=confidence,
        jamming_nearby=jamming,
        convoy_activity_nearby=0.0,
        time_since_cable_severance=9999.0,
        heading_towards_critical_asset=0.1,
        allied_proximity_score=0.0,
    )


def _coa(template_id="COA-TPL-ISR") -> CourseOfAction:
    return CourseOfAction(
        coa_id=template_id,
        template_id=template_id,
        title="Test COA",
        description="Test",
        target_entities=["E1"],
        required_assets=["isr_uav"],
        assigned_assets=["isr_uav"],
        assumptions=[],
        estimated_time_minutes=30,
        expected_effect="Test",
        risk_categories=[],
        escalation_risk=0.1,
        civilian_risk=0.02,
        logistics_burden=0.3,
        feasibility_score=1.0,
    )


def _sim(coa_id="COA-TPL-ISR") -> SimulationResult:
    return SimulationResult(
        coa_id=coa_id,
        success_probability=0.7,
        expected_time_to_effect=30.0,
        risk_to_second_cable=0.1,
        escalation_probability=0.1,
        missed_detection_probability=0.2,
        confidence_interval=(0.6, 0.8),
        simulation_runs=100,
    )


# ---------------------------------------------------------------------------
# Effect computation
# ---------------------------------------------------------------------------


class TestComputeEffects:
    def test_default_conditions_no_degradation(self):
        effects = compute_operational_effects({})
        assert effects.overall_effectiveness >= 0.95
        assert effects.sensor_effectiveness == 1.0
        assert effects.coa_success_modifier >= 0.90
        assert len(effects.active_effects) == 0

    def test_high_sea_state_degrades_sensors(self):
        effects = compute_operational_effects({"sea_state": 7})
        assert effects.sensor_effectiveness < 0.6
        assert effects.detection_penalty > 0.3
        assert effects.overall_effectiveness < 0.9
        assert any("Sea state 7" in e for e in effects.active_effects)

    def test_poor_visibility_reduces_confidence(self):
        effects = compute_operational_effects({"visibility": "fog"})
        assert effects.confidence_modifier < 0.5
        assert effects.isr_penalty > 0.4
        assert any("Visibility fog" in e for e in effects.active_effects)

    def test_night_reduces_optical_isr(self):
        effects = compute_operational_effects({"time_of_day": "night"})
        assert effects.optical_isr_modifier < 0.6
        assert any("Night" in e for e in effects.active_effects)

    def test_ice_cover_slows_vessels(self):
        effects = compute_operational_effects({"ice_cover": "heavy"})
        assert effects.vessel_speed_modifier < 0.7
        assert effects.sub_detection_bonus > 0.15

    def test_storm_weather_reduces_operations(self):
        effects = compute_operational_effects({"weather": "storm"})
        assert effects.operation_modifier < 0.7
        assert effects.sortie_rate < 0.6

    def test_high_jamming(self):
        effects = compute_operational_effects({}, jamming_intensity="high")
        assert effects.sensor_degradation > 0.4
        assert effects.comm_reliability < 0.6
        assert any("Jamming high" in e for e in effects.active_effects)

    def test_low_readiness(self):
        effects = compute_operational_effects({}, readiness="critical")
        assert effects.asset_availability < 0.4
        assert effects.response_time_modifier > 1.5
        assert any("Readiness critical" in e for e in effects.active_effects)

    def test_distant_logistics(self):
        effects = compute_operational_effects({}, distance="distant")
        assert effects.logistics_modifier < 0.6
        assert effects.fuel_factor < 0.6
        assert effects.response_delay_min > 100

    def test_low_fuel_endurance(self):
        effects = compute_operational_effects({}, fuel_endurance=0.3)
        assert effects.fuel_factor < 0.4
        assert any("Low fuel" in e for e in effects.active_effects)

    def test_combined_harsh_conditions(self):
        effects = compute_operational_effects(
            {"sea_state": 8, "visibility": "fog", "weather": "storm"},
            jamming_intensity="high",
            readiness="low",
            distance="far",
        )
        assert effects.overall_effectiveness < 0.55
        assert effects.coa_success_modifier < 0.1
        assert effects.coa_time_modifier > 1.5
        assert effects.coa_risk_modifier > 1.5
        assert effects.feasibility_modifier < 0.5
        assert len(effects.active_effects) >= 5

    def test_explicit_params_override_env(self):
        effects = compute_operational_effects(
            {"jamming_intensity": "low"},
            jamming_intensity="severe",
        )
        assert effects.sensor_degradation > 0.6
        assert effects.jamming_intensity == "severe"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_input_same_output(self):
        env = {"sea_state": 6, "visibility": "poor", "weather": "rain"}
        e1 = compute_operational_effects(env, jamming_intensity="medium")
        e2 = compute_operational_effects(env, jamming_intensity="medium")
        assert e1.to_dict() == e2.to_dict()

    def test_different_input_different_output(self):
        e1 = compute_operational_effects({"sea_state": 2})
        e2 = compute_operational_effects({"sea_state": 8})
        assert e1.sensor_effectiveness > e2.sensor_effectiveness
        assert e1.overall_effectiveness > e2.overall_effectiveness


# ---------------------------------------------------------------------------
# Effect tables completeness
# ---------------------------------------------------------------------------


class TestEffectTables:
    @pytest.mark.parametrize("level", range(10))
    def test_sea_state_table_complete(self, level):
        assert level in SEA_STATE_EFFECTS
        entry = SEA_STATE_EFFECTS[level]
        assert "sensor_effectiveness" in entry
        assert "detection_penalty" in entry

    @pytest.mark.parametrize("vis", ["excellent", "good", "moderate", "poor", "very_poor", "fog"])
    def test_visibility_table_complete(self, vis):
        assert vis in VISIBILITY_EFFECTS

    @pytest.mark.parametrize("tod", ["dawn", "day", "dusk", "night", "midday"])
    def test_time_of_day_table_complete(self, tod):
        assert tod in TIME_OF_DAY_EFFECTS

    @pytest.mark.parametrize("ice", ["none", "light", "partial", "heavy", "complete"])
    def test_ice_cover_table_complete(self, ice):
        assert ice in ICE_COVER_EFFECTS

    @pytest.mark.parametrize("wx", ["clear", "overcast", "rain", "storm", "snow", "fog"])
    def test_weather_table_complete(self, wx):
        assert wx in WEATHER_EFFECTS

    @pytest.mark.parametrize("jam", ["none", "low", "medium", "high", "severe"])
    def test_jamming_table_complete(self, jam):
        assert jam in JAMMING_INTENSITY_EFFECTS

    @pytest.mark.parametrize("ready", ["full", "high", "moderate", "low", "critical"])
    def test_readiness_table_complete(self, ready):
        assert ready in READINESS_EFFECTS

    @pytest.mark.parametrize("dist", ["close", "medium", "far", "distant"])
    def test_distance_table_complete(self, dist):
        assert dist in DISTANCE_EFFECTS


# ---------------------------------------------------------------------------
# Feature application
# ---------------------------------------------------------------------------


class TestApplyToFeatures:
    def test_default_conditions_no_change(self):
        features = [_feature()]
        effects = compute_operational_effects({})
        result = apply_effects_to_features(features, effects)
        assert result[0].source_confidence_weight == features[0].source_confidence_weight

    def test_poor_visibility_reduces_confidence(self):
        features = [_feature(confidence=0.8)]
        effects = compute_operational_effects({"visibility": "fog"})
        result = apply_effects_to_features(features, effects)
        assert result[0].source_confidence_weight < 0.5

    def test_jamming_increases_jamming_feature(self):
        features = [_feature(jamming=0.1)]
        effects = compute_operational_effects({}, jamming_intensity="high")
        result = apply_effects_to_features(features, effects)
        assert result[0].jamming_nearby > 0.1

    def test_empty_features_list(self):
        effects = compute_operational_effects({"sea_state": 8})
        result = apply_effects_to_features([], effects)
        assert result == []


# ---------------------------------------------------------------------------
# Feasibility application
# ---------------------------------------------------------------------------


class TestApplyToFeasibility:
    def test_default_conditions_no_change(self):
        coa = _coa()
        effects = compute_operational_effects({})
        result = apply_effects_to_feasibility(coa, effects)
        assert result.feasibility_score == coa.feasibility_score

    def test_low_readiness_reduces_feasibility(self):
        coa = _coa()
        effects = compute_operational_effects({}, readiness="critical")
        result = apply_effects_to_feasibility(coa, effects)
        assert result.feasibility_score < coa.feasibility_score

    def test_distant_logistics_increases_burden(self):
        coa = _coa()
        effects = compute_operational_effects({}, distance="distant")
        result = apply_effects_to_feasibility(coa, effects)
        assert result.logistics_burden > coa.logistics_burden


# ---------------------------------------------------------------------------
# Jamming inference
# ---------------------------------------------------------------------------


class TestInferJamming:
    def test_no_events_no_jamming(self):
        assert infer_jamming_intensity([]) == "none"

    def test_jamming_event_detected(self):
        events = [_event(source="sigint", event_type=EventType.JAMMING_DETECTED)]
        result = infer_jamming_intensity(events)
        assert result in ("low", "medium", "high")

    def test_multiple_jamming_events_high(self):
        events = [
            _event(entity_id=f"J{i}", source="sigint", event_type=EventType.JAMMING_DETECTED)
            for i in range(3)
        ]
        result = infer_jamming_intensity(events)
        assert result == "high"

    def test_non_jamming_events_no_jamming(self):
        events = [_event(), _event(entity_id="E2")]
        assert infer_jamming_intensity(events) == "none"


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------


class TestPipelineIntegration:
    def test_analysis_includes_operational_effects(self):
        events = [_event(), _event(entity_id="E2", source="combat_system")]
        ctx = AnalysisContext(
            events=events,
            scenario_state=None,
            source="test",
            tick=1,
        )
        result = run_canonical_analysis(ctx)
        assert result.operational_effects is not None
        assert isinstance(result.operational_effects, OperationalEffects)

    def test_effects_from_environment_dict(self):
        events = [_event()]
        from app.core.schemas import ScenarioState
        scenario = ScenarioState(
            scenario_id="test",
            environment={"sea_state": 6, "visibility": "poor", "weather": "storm"},
        )
        ctx = AnalysisContext(
            events=events,
            scenario_state=scenario,
            source="test",
            tick=1,
        )
        result = run_canonical_analysis(ctx)
        assert result.operational_effects is not None
        assert result.operational_effects.sea_state == 6
        assert result.operational_effects.visibility == "poor"
        assert result.operational_effects.overall_effectiveness < 0.9

    def test_harsh_conditions_reduce_scores(self):
        events = [_event(), _event(entity_id="E2")]
        from app.core.schemas import ScenarioState

        # Benign conditions
        benign = ScenarioState(
            scenario_id="benign",
            environment={"sea_state": 1, "visibility": "excellent"},
        )
        ctx_benign = AnalysisContext(events=events, scenario_state=benign, source="test", tick=1)
        result_benign = run_canonical_analysis(ctx_benign)

        # Harsh conditions
        harsh = ScenarioState(
            scenario_id="harsh",
            environment={"sea_state": 8, "visibility": "fog", "weather": "storm"},
        )
        ctx_harsh = AnalysisContext(events=events, scenario_state=harsh, source="test", tick=1)
        result_harsh = run_canonical_analysis(ctx_harsh)

        # COA scores should be lower in harsh conditions
        if result_benign.scored_coas and result_harsh.scored_coas:
            benign_top = result_benign.scored_coas[0].total_score
            harsh_top = result_harsh.scored_coas[0].total_score
            assert harsh_top <= benign_top * 1.05  # tolerance

    def test_empty_events_still_computes_effects(self):
        ctx = AnalysisContext(events=[], source="test", tick=1)
        result = run_canonical_analysis(ctx)
        assert result.operational_effects is not None

    def test_effects_deterministic(self):
        events = [_event(), _event(entity_id="E2")]
        from app.core.schemas import ScenarioState
        scenario = ScenarioState(
            scenario_id="test",
            environment={"sea_state": 5, "visibility": "poor"},
        )
        ctx = AnalysisContext(events=events, scenario_state=scenario, source="test", tick=1)
        r1 = run_canonical_analysis(ctx)
        r2 = run_canonical_analysis(ctx)
        assert r1.operational_effects.to_dict() == r2.operational_effects.to_dict()

    def test_analysis_does_not_apply_operational_effects_twice_to_simulation(self):
        events = [_event(), _event(entity_id="E2")]
        from app.core.schemas import ScenarioState

        scenario = ScenarioState(
            scenario_id="harsh",
            environment={"sea_state": 8, "visibility": "fog", "weather": "storm"},
        )
        ctx = AnalysisContext(events=events, scenario_state=scenario, source="test", tick=1)
        result = run_canonical_analysis(ctx)
        baseline_simulations = run_simulations(result.coas, events, result.threats, scenario)
        assert [sim.model_dump(mode="json") for sim in result.simulations] == [
            sim.model_dump(mode="json") for sim in baseline_simulations
        ]


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


class TestSerialization:
    def test_to_dict_complete(self):
        effects = compute_operational_effects(
            {"sea_state": 5, "visibility": "poor"},
            jamming_intensity="medium",
        )
        d = effects.to_dict()
        assert isinstance(d, dict)
        assert "sea_state" in d
        assert "visibility" in d
        assert "overall_effectiveness" in d
        assert "coa_success_modifier" in d
        assert "coa_time_modifier" in d
        assert "coa_risk_modifier" in d
        assert "feasibility_modifier" in d
        assert "active_effects" in d
        assert isinstance(d["active_effects"], list)

    def test_to_dict_json_safe(self):
        import json
        effects = compute_operational_effects({"sea_state": 7}, jamming_intensity="high")
        d = effects.to_dict()
        serialized = json.dumps(d)
        assert isinstance(serialized, str)


# ---------------------------------------------------------------------------
# No-LLM guarantee
# ---------------------------------------------------------------------------


class TestNoLLM:
    def test_no_llm_in_effects(self, monkeypatch):
        def fail_llm(*args, **kwargs):
            raise AssertionError("LLM must not be called in operational effects")

        monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm)

        effects = compute_operational_effects(
            {"sea_state": 9, "visibility": "fog", "weather": "storm"},
            jamming_intensity="severe",
            readiness="critical",
            distance="distant",
        )
        assert effects.overall_effectiveness > 0

    def test_no_llm_in_pipeline_with_effects(self, monkeypatch):
        def fail_llm(*args, **kwargs):
            raise AssertionError("LLM must not be called during analysis with effects")

        monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm)

        events = [_event()]
        from app.core.schemas import ScenarioState
        scenario = ScenarioState(
            scenario_id="test",
            environment={"sea_state": 7, "visibility": "fog"},
        )
        ctx = AnalysisContext(events=events, scenario_state=scenario, source="test", tick=1)
        result = run_canonical_analysis(ctx)
        assert result.operational_effects is not None
        assert result.operational_effects.overall_effectiveness < 0.9


# ---------------------------------------------------------------------------
# Composite effect correctness
# ---------------------------------------------------------------------------


class TestCompositeEffects:
    def test_overall_effectiveness_decreases_monotonically(self):
        """Adding harsh conditions should never increase overall effectiveness."""
        e_base = compute_operational_effects({})
        e_sea = compute_operational_effects({"sea_state": 5})
        e_sea_fog = compute_operational_effects({"sea_state": 5, "visibility": "fog"})
        e_all = compute_operational_effects(
            {"sea_state": 5, "visibility": "fog", "weather": "storm"},
            jamming_intensity="high",
        )
        assert e_base.overall_effectiveness >= e_sea.overall_effectiveness
        assert e_sea.overall_effectiveness >= e_sea_fog.overall_effectiveness
        assert e_sea_fog.overall_effectiveness >= e_all.overall_effectiveness

    def test_coa_time_modifier_increases_with_harsh_conditions(self):
        e_good = compute_operational_effects({})
        e_bad = compute_operational_effects(
            {"weather": "storm"},
            readiness="critical",
            distance="distant",
        )
        assert e_bad.coa_time_modifier > e_good.coa_time_modifier

    def test_coa_risk_modifier_increases_with_jamming(self):
        e_clean = compute_operational_effects({}, jamming_intensity="none")
        e_jammed = compute_operational_effects({}, jamming_intensity="severe")
        assert e_jammed.coa_risk_modifier > e_clean.coa_risk_modifier

    def test_threat_detection_modifier_sensible(self):
        e_clear = compute_operational_effects({"visibility": "excellent"})
        e_fog = compute_operational_effects({"visibility": "fog"})
        assert e_clear.threat_detection_modifier > e_fog.threat_detection_modifier
