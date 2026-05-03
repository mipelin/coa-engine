from app.core.schemas import AssetState, CourseOfAction, OperationalEvent, SimulationResult
from app.engine.anomaly_detection import detect_anomalies
from app.engine.coa_generation import generate_coas
from app.engine.event_ingestion import load_scenario_events
from app.engine.portfolio import build_portfolios
from app.engine.explanation import generate_briefing
from app.engine.feature_engineering import compute_features
from app.engine.recommendation import recommend
from app.engine.scoring import score_coas
from app.engine.simulation import run_simulations
from app.engine.threat_assessment import assess_threats
from app.main import app

from fastapi.testclient import TestClient

client = TestClient(app)

EVENTS = load_scenario_events()

UNSAFE_WORDS = [
    "target", "weapon", "strike", "engage", "kill", "lethal",
    "execute order", "fire", "destroy", "neutralize",
]


def _run_full():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(EVENTS, threats)
    sims = run_simulations(coas, EVENTS, threats)
    scored = score_coas(coas, sims)
    rec = recommend(scored)
    briefing = generate_briefing(EVENTS, anomalies, threats, scored, rec)
    return coas, sims, scored, rec, briefing


# --- COA generation ---


def test_generate_coas_returns_at_least_three():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(EVENTS, threats)
    assert len(coas) >= 3


def test_coas_have_required_fields():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(EVENTS, threats)
    for coa in coas:
        assert coa.coa_id
        assert coa.template_id
        assert coa.title
        assert coa.description
        assert coa.source == "template_engine"
        assert coa.required_assets
        assert isinstance(coa.target_entities, list)
        assert isinstance(coa.assigned_assets, list)
        assert coa.objective
        assert coa.rationale
        assert coa.assumptions
        assert coa.estimated_time_minutes >= 0
        assert 0.0 <= coa.escalation_risk <= 1.0
        assert 0.0 <= coa.civilian_risk <= 1.0
        assert 0.0 <= coa.logistics_burden <= 1.0
        assert 0.0 <= coa.feasibility_score <= 1.0
        assert coa.feasibility_status in ("feasible", "partially_feasible", "infeasible", "unknown")


def test_coas_reflect_missing_assets():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(EVENTS, threats, {"isr_uav": 0, "maritime_patrol_asset": 0})
    assert any(coa.missing_assets for coa in coas)
    assert any(coa.feasibility_score < 1.0 for coa in coas)
    assert any(coa.validation_warnings for coa in coas)


def test_coas_match_assets_by_alias_capability():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(
        EVENTS,
        threats,
        asset_states=[
            AssetState(
                asset_id="maritime_patrol_vessel",
                asset_type="maritime_patrol_vessel",
                capabilities=["maritime_patrol_asset", "maritime_patrol_vessel"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                lat=57.55,
                lon=18.95,
                coverage_radius_km=300.0,
                transit_speed_kts=30.0,
                response_eta_min=45,
            ),
            AssetState(
                asset_id="coast_guard_liaison",
                asset_type="coast_guard_liaison",
                capabilities=["coast_guard_liaison"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                response_eta_min=10,
            ),
            AssetState(
                asset_id="isr_uav",
                asset_type="isr_uav",
                capabilities=["isr_uav", "surveillance_asset", "sensor_data_feed"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                lat=57.6,
                lon=18.4,
                coverage_radius_km=300.0,
                transit_speed_kts=90.0,
                response_eta_min=20,
            ),
        ],
    )
    maritime_coas = [coa for coa in coas if "maritime_patrol_asset" in coa.required_assets]
    assert maritime_coas
    assert any("maritime_patrol_vessel" in coa.assigned_assets for coa in maritime_coas)


def test_coas_reflect_spatially_infeasible_assets():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(
        EVENTS,
        threats,
        asset_states=[
            AssetState(
                asset_id="maritime_patrol_asset",
                asset_type="maritime_patrol_asset",
                quantity_total=1,
                quantity_available=1,
                status="available",
                lat=40.0,
                lon=5.0,
                coverage_radius_km=50.0,
                transit_speed_kts=15.0,
                response_eta_min=240,
            ),
            AssetState(
                asset_id="isr_uav",
                asset_type="isr_uav",
                quantity_total=1,
                quantity_available=1,
                status="available",
                lat=57.6,
                lon=18.4,
                coverage_radius_km=300.0,
                transit_speed_kts=90.0,
                response_eta_min=20,
            ),
        ],
    )
    assert any("coverage radius" in " ".join(coa.validation_warnings) or "transit ETA" in " ".join(coa.validation_warnings) for coa in coas)
    assert any("maritime_patrol_asset" in coa.missing_assets for coa in coas if "maritime_patrol_asset" in coa.required_assets)


def test_coas_warn_on_shared_asset_pressure():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(
        EVENTS,
        threats,
        asset_states=[
            AssetState(
                asset_id="maritime_patrol_vessel",
                asset_type="maritime_patrol_vessel",
                capabilities=["maritime_patrol_asset", "maritime_patrol_vessel"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                lat=57.55,
                lon=18.95,
                coverage_radius_km=300.0,
                transit_speed_kts=30.0,
                response_eta_min=45,
            ),
            AssetState(
                asset_id="coast_guard_liaison",
                asset_type="coast_guard_liaison",
                capabilities=["coast_guard_liaison"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                response_eta_min=10,
            ),
            AssetState(
                asset_id="cable_operator_liaison",
                asset_type="cable_operator_liaison",
                capabilities=["cable_operator_liaison"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                response_eta_min=10,
            ),
            AssetState(
                asset_id="isr_uav",
                asset_type="isr_uav",
                capabilities=["isr_uav", "surveillance_asset", "sensor_data_feed"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                lat=57.6,
                lon=18.4,
                coverage_radius_km=300.0,
                transit_speed_kts=90.0,
                response_eta_min=20,
            ),
            AssetState(
                asset_id="intelligence_team",
                asset_type="intelligence_team",
                capabilities=["intelligence_team"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                response_eta_min=20,
            ),
            AssetState(
                asset_id="border_patrol_liaison",
                asset_type="border_patrol_liaison",
                capabilities=["border_patrol_liaison"],
                quantity_total=1,
                quantity_available=1,
                status="available",
                response_eta_min=20,
            ),
        ],
    )
    assert any(
        "Shared demand pressure" in " ".join(coa.validation_warnings)
        for coa in coas
    )


def test_coas_no_unsafe_language():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(EVENTS, threats)
    for coa in coas:
        text = f"{coa.title} {coa.description}".lower()
        for word in UNSAFE_WORDS:
            assert word not in text, f"Unsafe word '{word}' found in COA {coa.coa_id}"


def test_coas_use_advisory_language():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(EVENTS, threats)
    advisory_words = {"recommend", "consider", "support", "coordinate", "monitor", "observe"}
    all_text = " ".join(c.description.lower() for c in coas)
    assert any(w in all_text for w in advisory_words)


def test_allied_support_contacts_unlock_combined_options():
    support_poor_events = [
        event for event in EVENTS
        if event.entity_type.value not in {"allied_vessel", "isr_asset"}
    ]
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)

    support_rich = generate_coas(EVENTS, threats)
    support_poor = generate_coas(support_poor_events, threats)

    support_rich_ids = {coa.template_id for coa in support_rich}
    support_poor_ids = {coa.template_id for coa in support_poor}

    assert "COA-TPL-COMBINED" in support_rich_ids
    assert "COA-TPL-COMBINED" not in support_poor_ids


def test_contact_derived_allied_support_changes_feasibility():
    support_poor_events = [
        event for event in EVENTS
        if event.entity_type.value not in {"allied_vessel", "isr_asset"}
    ]
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)

    without_support = generate_coas(support_poor_events, threats)
    with_support = generate_coas(EVENTS, threats)

    without_isr = next(coa for coa in without_support if coa.template_id == "COA-TPL-ISR")
    with_isr = next(coa for coa in with_support if coa.template_id == "COA-TPL-ISR")

    assert with_isr.feasibility_score >= without_isr.feasibility_score
    assert len(with_isr.assigned_assets) >= len(without_isr.assigned_assets)


def test_higher_contact_pressure_triggers_reinforcement_template():
    support_poor_events = [
        event for event in EVENTS
        if event.entity_type.value not in {"allied_vessel", "isr_asset"}
    ]
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)

    coas = generate_coas(support_poor_events, threats)

    assert any(coa.template_id == "COA-TPL-REINFORCE" for coa in coas)


# --- Simulation ---


def test_simulation_returns_one_per_coa():
    coas, sims, _, _, _ = _run_full()
    assert len(sims) == len(coas)


def test_simulation_probabilities_bounded():
    _, sims, _, _, _ = _run_full()
    for sim in sims:
        assert 0.0 <= sim.success_probability <= 1.0
        assert 0.0 <= sim.risk_to_second_cable <= 1.0
        assert 0.0 <= sim.escalation_probability <= 1.0
        assert 0.0 <= sim.missed_detection_probability <= 1.0
        assert sim.expected_time_to_effect > 0
        assert sim.simulation_runs > 0
        assert len(sim.confidence_interval) == 2
        assert sim.confidence_interval[0] <= sim.confidence_interval[1]


def test_simulation_is_deterministic():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(EVENTS, threats)
    run1 = run_simulations(coas, EVENTS, threats)
    run2 = run_simulations(coas, EVENTS, threats)
    for s1, s2 in zip(run1, run2):
        assert s1.success_probability == s2.success_probability


def test_simulation_depends_on_template_and_assets_not_title_text():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)

    coa_a = CourseOfAction(
        coa_id="T-A",
        template_id="COA-TPL-SHADOW",
        title="Completely Renamed Option",
        description="Renamed without changing semantics",
        target_entities=["VES-SUSP-001"],
        required_assets=["maritime_patrol_asset", "coast_guard_liaison"],
        assigned_assets=["maritime_patrol_asset", "coast_guard_liaison"],
        available_assets=["maritime_patrol_asset", "coast_guard_liaison"],
        missing_assets=[],
        objective="Observe target",
        rationale="Template-driven",
        feasibility_score=1.0,
        feasibility_status="feasible",
        validation_warnings=[],
        assumptions=["Available assets can respond"],
        estimated_time_minutes=60,
        expected_effect="Observation maintained",
        risk_categories=["navigation_safety"],
        escalation_risk=0.15,
        civilian_risk=0.05,
        logistics_burden=0.4,
        source="template_engine",
    )
    coa_b = coa_a.model_copy(update={
        "coa_id": "T-B",
        "title": "Another Arbitrary Label",
    })

    sim_a, sim_b = run_simulations([coa_a, coa_b], EVENTS, threats)

    assert sim_a.success_probability == sim_b.success_probability
    assert sim_a.risk_to_second_cable == sim_b.risk_to_second_cable
    assert sim_a.missed_detection_probability == sim_b.missed_detection_probability


def test_missing_assets_reduce_simulation_performance():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    fully_supported = generate_coas(EVENTS, threats)
    degraded = generate_coas(EVENTS, threats, {"isr_uav": 0, "maritime_patrol_asset": 0})
    full_sims = {sim.coa_id: sim for sim in run_simulations(fully_supported, EVENTS, threats)}
    degraded_sims = {sim.coa_id: sim for sim in run_simulations(degraded, EVENTS, threats)}
    assert degraded_sims["COA-TPL-COMBINED"].success_probability < full_sims["COA-TPL-COMBINED"].success_probability


# --- Scoring ---


def test_score_coas_returns_ranked():
    _, _, scored, _, _ = _run_full()
    assert len(scored) >= 3
    ranks = [s.rank for s in scored]
    assert ranks == sorted(ranks)
    assert ranks[0] == 1


def test_scores_in_range():
    _, _, scored, _, _ = _run_full()
    for s in scored:
        assert 0.0 <= s.total_score <= 100.0


def test_scores_descending():
    _, _, scored, _, _ = _run_full()
    scores = [s.total_score for s in scored]
    assert scores == sorted(scores, reverse=True)


def test_scored_coas_have_tradeoff_explanation():
    _, _, scored, _, _ = _run_full()
    for s in scored:
        assert len(s.tradeoff_explanation) > 0


# --- Recommendation ---


def test_recommendation_selects_rank_one():
    _, _, scored, rec, _ = _run_full()
    assert rec.recommended.rank == 1
    assert rec.recommended.coa.coa_id


def test_recommendation_has_rationale():
    _, _, _, rec, _ = _run_full()
    assert len(rec.rationale) > 0
    assert "score" in rec.rationale.lower() or "probability" in rec.rationale.lower()


def test_recommendation_has_alternatives():
    _, _, scored, rec, _ = _run_full()
    if len(scored) > 1:
        assert len(rec.alternatives) >= 1


def test_recommendation_exposes_feasible_package_when_available():
    asset_states = [
        AssetState(
            asset_id="maritime_patrol_vessel",
            asset_type="maritime_patrol_vessel",
            capabilities=["maritime_patrol_asset", "maritime_patrol_vessel"],
            quantity_total=2,
            quantity_available=2,
            status="available",
            lat=57.55,
            lon=18.95,
            coverage_radius_km=300.0,
            transit_speed_kts=30.0,
            response_eta_min=45,
        ),
        AssetState(
            asset_id="isr_uav",
            asset_type="isr_uav",
            capabilities=["isr_uav", "surveillance_asset", "sensor_data_feed"],
            quantity_total=2,
            quantity_available=2,
            status="available",
            lat=57.6,
            lon=18.4,
            coverage_radius_km=300.0,
            transit_speed_kts=90.0,
            response_eta_min=20,
        ),
        AssetState(
            asset_id="coast_guard_liaison",
            asset_type="coast_guard_liaison",
            capabilities=["coast_guard_liaison"],
            quantity_total=1,
            quantity_available=1,
            status="available",
            response_eta_min=10,
        ),
        AssetState(
            asset_id="civil_aviation_authority",
            asset_type="civil_aviation_authority",
            capabilities=["civil_aviation_authority"],
            quantity_total=1,
            quantity_available=1,
            status="available",
            response_eta_min=10,
        ),
        AssetState(
            asset_id="airspace_coordination_cell",
            asset_type="airspace_coordination_cell",
            capabilities=["airspace_coordination_cell"],
            quantity_total=1,
            quantity_available=1,
            status="available",
            response_eta_min=10,
        ),
    ]

    coa_a = CourseOfAction(
        coa_id="COA-A",
        template_id="COA-TPL-SHADOW",
        title="Shadow Vessel Alpha",
        description="Observe vessel Alpha",
        target_entities=["VES-A"],
        required_assets=["maritime_patrol_asset"],
        assigned_assets=["maritime_patrol_vessel"],
        available_assets=["maritime_patrol_vessel"],
        missing_assets=[],
        objective="Track vessel Alpha",
        rationale="Persistent observation",
        feasibility_score=1.0,
        feasibility_status="feasible",
        validation_warnings=[],
        assumptions=["Patrol vessel is available"],
        estimated_time_minutes=45,
        expected_effect="Observation maintained",
        risk_categories=["navigation_safety"],
        escalation_risk=0.1,
        civilian_risk=0.05,
        logistics_burden=0.2,
        source="template_engine",
    )
    coa_b = CourseOfAction(
        coa_id="COA-B",
        template_id="COA-TPL-AIRSPACE",
        title="Deconflict Civil Airspace",
        description="Coordinate around UAV track",
        target_entities=["UAV-A"],
        required_assets=["civil_aviation_authority", "airspace_coordination_cell"],
        assigned_assets=["civil_aviation_authority", "airspace_coordination_cell"],
        available_assets=["civil_aviation_authority", "airspace_coordination_cell"],
        missing_assets=[],
        objective="Reduce civilian airspace disruption",
        rationale="Separate airspace users from UAV activity",
        feasibility_score=1.0,
        feasibility_status="feasible",
        validation_warnings=[],
        assumptions=["Civil aviation authority is reachable"],
        estimated_time_minutes=30,
        expected_effect="Airspace deconflicted",
        risk_categories=["civil_aviation"],
        escalation_risk=0.05,
        civilian_risk=0.02,
        logistics_burden=0.1,
        source="template_engine",
    )
    sims = [
        SimulationResult(
            coa_id="COA-A",
            success_probability=0.78,
            expected_time_to_effect=45.0,
            risk_to_second_cable=0.12,
            escalation_probability=0.1,
            missed_detection_probability=0.08,
            confidence_interval=(0.68, 0.88),
            simulation_runs=1000,
        ),
        SimulationResult(
            coa_id="COA-B",
            success_probability=0.82,
            expected_time_to_effect=30.0,
            risk_to_second_cable=0.05,
            escalation_probability=0.04,
            missed_detection_probability=0.06,
            confidence_interval=(0.74, 0.9),
            simulation_runs=1000,
        ),
    ]
    scored = score_coas([coa_a, coa_b], sims)
    rec = recommend(scored, asset_states=asset_states)
    assert rec.recommended_package is not None
    assert len(rec.recommended_package.coas) >= 2
    assert rec.recommended_package.total_score >= 0.0
    assert rec.recommended_package.plan is not None
    assert len(rec.recommended_package.plan.tasks) >= 2
    assert rec.recommended_package.plan.dependencies


def test_recommendation_changes_with_constrained_assets():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    constrained_coas = generate_coas(EVENTS, threats, {"isr_uav": 0, "maritime_patrol_asset": 0})
    constrained_scored = score_coas(constrained_coas, run_simulations(constrained_coas, EVENTS, threats))
    constrained_rec = recommend(
        constrained_scored,
        asset_inventory={"isr_uav": 0, "maritime_patrol_asset": 0},
    )
    assert constrained_rec.recommended is not None
    assert constrained_rec.recommended.coa.coa_id != "COA-TPL-COMBINED"
    assert constrained_rec.recommended.coa.feasibility_score == 1.0


def test_recommendation_handles_empty_scored_list():
    rec = recommend([])
    assert rec.recommended is None
    assert rec.alternatives == []
    assert rec.recommended_package is None
    assert "No courses of action" in rec.rationale


def test_portfolio_allocator_rejects_global_asset_overcommitment():
    coa_a = CourseOfAction(
        coa_id="COA-A",
        template_id="COA-TPL-SHADOW",
        title="Shadow Vessel A",
        description="Observe vessel A",
        target_entities=["VES-A"],
        required_assets=["maritime_patrol_asset"],
        assigned_assets=["maritime_patrol_vessel"],
        available_assets=["maritime_patrol_vessel"],
        missing_assets=[],
        objective="Track vessel A",
        rationale="Persistent observation",
        feasibility_score=1.0,
        feasibility_status="feasible",
        validation_warnings=[],
        assumptions=["Patrol vessel is available"],
        estimated_time_minutes=45,
        expected_effect="Observation maintained",
        risk_categories=["navigation_safety"],
        escalation_risk=0.1,
        civilian_risk=0.05,
        logistics_burden=0.2,
        source="template_engine",
    )
    coa_b = coa_a.model_copy(update={
        "coa_id": "COA-B",
        "title": "Shadow Vessel B",
        "target_entities": ["VES-B"],
    })
    sims = [
        SimulationResult(
            coa_id="COA-A",
            success_probability=0.8,
            expected_time_to_effect=45.0,
            risk_to_second_cable=0.1,
            escalation_probability=0.1,
            missed_detection_probability=0.05,
            confidence_interval=(0.7, 0.9),
            simulation_runs=1000,
        ),
        SimulationResult(
            coa_id="COA-B",
            success_probability=0.78,
            expected_time_to_effect=45.0,
            risk_to_second_cable=0.1,
            escalation_probability=0.1,
            missed_detection_probability=0.05,
            confidence_interval=(0.68, 0.88),
            simulation_runs=1000,
        ),
    ]
    scored = score_coas([coa_a, coa_b], sims)
    packages = build_portfolios(
        scored,
        asset_states=[
            AssetState(
                asset_id="maritime_patrol_vessel",
                asset_type="maritime_patrol_vessel",
                capabilities=["maritime_patrol_asset", "maritime_patrol_vessel"],
                quantity_total=1,
                quantity_available=1,
                status="available",
            )
        ],
    )
    assert packages == []


# --- Briefing ---


def test_briefing_has_all_sections():
    _, _, _, _, briefing = _run_full()
    assert briefing.situation
    assert len(briefing.key_indicators) >= 1
    assert briefing.assessment
    assert len(briefing.coas_considered) >= 1
    assert briefing.recommended_coa
    assert len(briefing.risks) >= 1
    assert briefing.confidence in ("LOW", "MEDIUM", "HIGH")
    assert len(briefing.assumptions) >= 1


def test_briefing_no_unsafe_language():
    _, _, _, _, briefing = _run_full()
    all_text = (
        f"{briefing.situation} {briefing.assessment} {briefing.recommended_coa} "
        + " ".join(briefing.risks)
    ).lower()
    for word in UNSAFE_WORDS:
        assert word not in all_text, f"Unsafe word '{word}' found in briefing"


# --- /coa/* endpoints ---


def test_coa_generate_endpoint():
    resp = client.post("/v1/coa/generate", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert len(body["coas"]) >= 3
    for coa in body["coas"]:
        assert "coa_id" in coa
        assert "title" in coa


def test_simulation_endpoint():
    resp = client.post("/v1/coa/simulation/run", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert len(body["simulations"]) >= 3
    for sim in body["simulations"]:
        assert "success_probability" in sim
        assert "confidence_interval" in sim


def test_recommendation_endpoint():
    resp = client.post("/v1/coa/recommendation/run", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["recommended"]["rank"] == 1
    assert "recommended_package" in body
    assert body["recommended_package"] is None or len(body["recommended_package"]["coas"]) >= 2
    assert "rationale" in body
    assert "edge_cases" in body


def test_briefing_endpoint():
    resp = client.post("/v1/coa/briefing/generate", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["situation"]
    assert body["key_indicators"]
    assert body["assessment"]
    assert body["recommended_coa"]
    assert body["confidence"] in ("LOW", "MEDIUM", "HIGH")
