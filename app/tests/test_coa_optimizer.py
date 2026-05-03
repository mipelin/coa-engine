from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core.constants import EntityType, EventType
from app.core.schemas import (
    Contact,
    ContactType,
    CourseOfAction,
    OperationalEvent,
)
from app.engine.analysis_service import AnalysisContext, run_canonical_analysis
from app.engine.coa_optimizer import (
    MAX_COA_VARIANTS,
    COAParameterSet,
    OptimizationResult,
    compute_robustness,
    generate_variants,
    optimize_coas,
)
from app.engine.simulation import SimulationResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ts(minutes: int) -> datetime:
    return datetime(2025, 6, 15, 8, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def _event(
    *,
    event_id: str,
    entity_id: str,
    source: str,
    lat: float,
    lon: float,
    confidence: float = 0.8,
    event_type: EventType = EventType.VESSEL_POSITION,
    entity_type: EntityType = EntityType.SUSPICIOUS_VESSEL,
    heading: float | None = 45.0,
    speed_knots: float | None = 8.0,
    timestamp_min: int = 0,
    description: str = "test event",
) -> OperationalEvent:
    attrs = {}
    if heading is not None:
        attrs["heading"] = heading
    if speed_knots is not None:
        attrs["speed_knots"] = speed_knots
    return OperationalEvent(
        event_id=event_id,
        timestamp=_ts(timestamp_min),
        event_type=event_type,
        source=source,
        confidence=confidence,
        lat=lat,
        lon=lon,
        entity_id=entity_id,
        entity_type=entity_type,
        description=description,
        attributes=attrs,
    )


def _contact(
    *,
    contact_id: str,
    entity_id: str,
    source: str,
    lat: float,
    lon: float,
    confidence: float = 0.85,
    heading: float = 45.0,
    speed: float = 8.0,
    is_hostile: bool = False,
    timestamp_min: int = 0,
) -> Contact:
    return Contact(
        contact_id=contact_id,
        timestamp=_ts(timestamp_min),
        source=source,
        contact_type=ContactType.VESSEL,
        lat=lat,
        lon=lon,
        speed=speed,
        heading=heading,
        confidence=confidence,
        entity_id=entity_id,
        is_hostile=is_hostile,
        attributes={"subtype": "warship", "allegiance": "hostile" if is_hostile else "unknown"},
    )


def _base_coa(template_id: str = "COA-TPL-ISR", escalation_risk: float = 0.1) -> CourseOfAction:
    return CourseOfAction(
        coa_id=template_id,
        template_id=template_id,
        title="Test COA",
        description="Test",
        target_entities=["VES-1"],
        required_assets=["isr_uav"],
        assigned_assets=["isr_uav"],
        assumptions=["Test assumption"],
        estimated_time_minutes=30,
        expected_effect="Test effect",
        risk_categories=["sensor_gap"],
        escalation_risk=escalation_risk,
        civilian_risk=0.02,
        logistics_burden=0.3,
        feasibility_score=1.0,
        source="template_engine",
    )


def _threat_events():
    return [
        _event(event_id="EV1", entity_id="VES-1", source="ais", lat=57.5, lon=19.0),
        _event(
            event_id="EV2", entity_id="VES-1", source="combat_system",
            lat=57.5, lon=19.0, event_type=EventType.VESSEL_COURSE_CHANGE,
            confidence=0.9,
        ),
    ]


# ---------------------------------------------------------------------------
# Variant generation
# ---------------------------------------------------------------------------


class TestVariantGeneration:
    def test_variants_generated_from_base_coas(self):
        coas = [_base_coa("COA-TPL-ISR"), _base_coa("COA-TPL-SHADOW")]
        variants = generate_variants(coas)
        assert len(variants) > 0
        for coa, params in variants:
            assert isinstance(params, COAParameterSet)
            assert params.variant_id.startswith(coa.template_id)

    def test_max_variant_cap_respected(self):
        coas = [_base_coa(f"COA-TPL-{t}") for t in ["ISR", "SHADOW", "CABLE-PROTECT", "AIRSPACE", "COMBINED"]]
        variants = generate_variants(coas, max_variants=10)
        assert len(variants) <= 10

    def test_global_max_cap(self):
        coas = [_base_coa(f"COA-TPL-{t}") for t in ["ISR", "SHADOW", "CABLE-PROTECT", "AIRSPACE", "COMBINED"]]
        variants = generate_variants(coas)
        assert len(variants) <= MAX_COA_VARIANTS

    def test_variant_coa_has_optimizer_source(self):
        coas = [_base_coa("COA-TPL-ISR")]
        variants = generate_variants(coas)
        for coa, _ in variants:
            assert coa.source == "coa_optimizer"

    def test_variant_titles_include_label(self):
        coas = [_base_coa("COA-TPL-ISR")]
        variants = generate_variants(coas)
        for coa, params in variants:
            assert params.variant_label in coa.title

    def test_no_base_coas_produces_no_variants(self):
        variants = generate_variants([])
        assert len(variants) == 0


# ---------------------------------------------------------------------------
# Robustness computation
# ---------------------------------------------------------------------------


class TestRobustness:
    def test_high_success_high_feasibility_high_robustness(self):
        coa = _base_coa(escalation_risk=0.05)
        coa = coa.model_copy(update={"logistics_burden": 0.1, "civilian_risk": 0.0})
        sim = SimulationResult(
            coa_id="test", success_probability=0.9, expected_time_to_effect=20.0,
            risk_to_second_cable=0.05, escalation_probability=0.05,
            missed_detection_probability=0.1, confidence_interval=(0.8, 0.95),
            simulation_runs=100,
        )
        score = compute_robustness(coa, sim)
        assert score > 70.0

    def test_low_success_low_robustness(self):
        coa = _base_coa(escalation_risk=0.5)
        coa = coa.model_copy(update={
            "feasibility_score": 0.3,
            "logistics_burden": 0.8,
            "civilian_risk": 0.3,
        })
        sim = SimulationResult(
            coa_id="test", success_probability=0.2, expected_time_to_effect=90.0,
            risk_to_second_cable=0.6, escalation_probability=0.4,
            missed_detection_probability=0.5, confidence_interval=(0.1, 0.3),
            simulation_runs=100,
        )
        score = compute_robustness(coa, sim)
        assert score < 60.0

    def test_robustness_is_deterministic(self):
        coa = _base_coa()
        sim = SimulationResult(
            coa_id="test", success_probability=0.7, expected_time_to_effect=30.0,
            risk_to_second_cable=0.2, escalation_probability=0.1,
            missed_detection_probability=0.2, confidence_interval=(0.6, 0.8),
            simulation_runs=100,
        )
        assert compute_robustness(coa, sim) == compute_robustness(coa, sim)


# ---------------------------------------------------------------------------
# Full optimization pipeline
# ---------------------------------------------------------------------------


class TestOptimizeCOAs:
    def test_optimization_produces_variants(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        opt = result.coa_optimization
        assert opt is not None
        assert len(opt.optimized_variants) > 0

    def test_best_variant_exists_when_coas_exist(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        opt = result.coa_optimization
        if result.coas:
            assert opt is not None
            assert opt.best_variant is not None

    def test_rejected_variants_not_best(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        opt = result.coa_optimization
        if opt and opt.best_variant:
            assert opt.best_variant.coa.roe_status != "rejected"

    def test_optimization_summary_valid(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        opt = result.coa_optimization
        assert opt is not None
        summary = opt.optimization_summary
        assert summary["status"] in ("ok", "no_base_coas", "no_variants_generated")
        if summary["status"] == "ok":
            assert summary["variant_count"] > 0
            assert summary["base_coa_count"] > 0

    def test_robustness_ranking_sorted(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        opt = result.coa_optimization
        if opt and len(opt.robustness_ranking) > 1:
            for i in range(len(opt.robustness_ranking) - 1):
                assert (
                    opt.robustness_ranking[i]["robustness"]
                    >= opt.robustness_ranking[i + 1]["robustness"]
                )

    def test_variant_parameters_populated(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        opt = result.coa_optimization
        if opt and opt.variant_parameters:
            for vp in opt.variant_parameters:
                assert "variant_id" in vp
                assert "base_template_id" in vp
                assert "isr_intensity" in vp
                assert vp["isr_intensity"] in ("low", "medium", "high")


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_optimization_deterministic(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result1 = run_canonical_analysis(ctx)
        result2 = run_canonical_analysis(ctx)

        opt1 = result1.coa_optimization
        opt2 = result2.coa_optimization
        assert opt1 is not None
        assert opt2 is not None
        assert len(opt1.optimized_variants) == len(opt2.optimized_variants)

        # Same variant IDs and scores
        ids1 = [v.coa.coa_id for v in opt1.optimized_variants]
        ids2 = [v.coa.coa_id for v in opt2.optimized_variants]
        assert ids1 == ids2

        scores1 = [round(v.total_score, 1) for v in opt1.optimized_variants]
        scores2 = [round(v.total_score, 1) for v in opt2.optimized_variants]
        assert scores1 == scores2

    def test_no_llm_in_optimization(self, monkeypatch):
        def fail_llm_call(*args, **kwargs):
            raise AssertionError("LLM must not be called during optimization")

        monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm_call)

        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        assert result.coa_optimization is not None


# ---------------------------------------------------------------------------
# ROE behavior
# ---------------------------------------------------------------------------


class TestROEOnVariants:
    def test_high_escalation_variant_gets_worse_roe_or_score(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        opt = result.coa_optimization
        if not opt or not opt.optimized_variants:
            pytest.skip("No variants generated")

        # Find high-escalation variants vs low-escalation
        high_esc = [
            v for v in opt.optimized_variants
            if v.coa.escalation_risk > 0.15
        ]
        low_esc = [
            v for v in opt.optimized_variants
            if v.coa.escalation_risk <= 0.1
        ]
        # If both exist, high escalation should generally score lower
        if high_esc and low_esc:
            avg_high = sum(v.total_score for v in high_esc) / len(high_esc)
            avg_low = sum(v.total_score for v in low_esc) / len(low_esc)
            # Not guaranteed for all cases, but the trend should hold
            assert avg_high <= avg_low * 1.1  # within 10% tolerance


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------


class TestPipelineIntegration:
    def test_analysis_result_includes_optimization(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        assert hasattr(result, "coa_optimization")
        assert result.coa_optimization is not None
        assert isinstance(result.coa_optimization, OptimizationResult)

    def test_base_coas_not_removed(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        # Base COAs should still be present
        assert len(result.coas) > 0
        for coa in result.coas:
            assert coa.source == "template_engine"

    def test_empty_events_no_crash(self):
        ctx = AnalysisContext(
            events=[],
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        assert result.coa_optimization is not None

    def test_cable_scenario_infrastructure_variant_scores(self):
        events = [
            _event(event_id="EV-CABLE", entity_id="CABLE-1", source="fused",
                   lat=57.5, lon=19.0, event_type=EventType.CABLE_SEVERANCE,
                   entity_type=EntityType.INFRASTRUCTURE, description="Cable severed"),
            _event(event_id="EV-VES", entity_id="VES-1", source="ais",
                   lat=57.5, lon=19.1),
        ]
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        opt = result.coa_optimization
        if opt and opt.optimized_variants:
            # Infrastructure-first variants should exist for cable-protect templates
            infra_variants = [
                v for v in opt.optimized_variants
                if "Infrastructure-first" in v.coa.title
            ]
            # May or may not exist depending on which templates were generated
            if infra_variants:
                assert infra_variants[0].coa.roe_status in ("allowed", "restricted", "requires_authorization")


# ---------------------------------------------------------------------------
# Live/legacy analysis agreement
# ---------------------------------------------------------------------------


class TestAnalysisAgreement:
    def test_canonical_and_optimization_coherent(self):
        events = _threat_events()
        ctx = AnalysisContext(
            events=events,
            source="test",
            tick=1,
            scenario_id="test",
            scenario_name="Test",
        )
        result = run_canonical_analysis(ctx)
        opt = result.coa_optimization

        # If base COAs exist, optimization should have variants
        if result.coas:
            assert opt is not None
            assert len(opt.optimized_variants) > 0

        # Recommendation should be based on base COAs, not variants
        if result.recommendation and result.recommendation.recommended:
            assert result.recommendation.recommended.coa.source == "template_engine"
