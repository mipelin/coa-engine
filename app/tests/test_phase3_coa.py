from app.core.schemas import OperationalEvent
from app.engine.anomaly_detection import detect_anomalies
from app.engine.coa_generation import generate_coas
from app.engine.event_ingestion import load_scenario_events
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
        assert coa.title
        assert coa.description
        assert coa.required_assets
        assert coa.assumptions
        assert coa.estimated_time_minutes >= 0
        assert 0.0 <= coa.escalation_risk <= 1.0
        assert 0.0 <= coa.civilian_risk <= 1.0
        assert 0.0 <= coa.logistics_burden <= 1.0
        assert 0.0 <= coa.feasibility_score <= 1.0


def test_coas_reflect_missing_assets():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    coas = generate_coas(EVENTS, threats, {"isr_uav": 0, "maritime_patrol_asset": 0})
    assert any(coa.missing_assets for coa in coas)
    assert any(coa.feasibility_score < 1.0 for coa in coas)


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


def test_missing_assets_reduce_simulation_performance():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    fully_supported = generate_coas(EVENTS, threats)
    degraded = generate_coas(EVENTS, threats, {"isr_uav": 0, "maritime_patrol_asset": 0})
    full_sims = {sim.coa_id: sim for sim in run_simulations(fully_supported, EVENTS, threats)}
    degraded_sims = {sim.coa_id: sim for sim in run_simulations(degraded, EVENTS, threats)}
    assert degraded_sims["COA-006"].success_probability < full_sims["COA-006"].success_probability


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


def test_recommendation_changes_with_constrained_assets():
    features = compute_features(EVENTS)
    anomalies = detect_anomalies(EVENTS, features)
    threats = assess_threats(EVENTS, features, anomalies)
    constrained_coas = generate_coas(EVENTS, threats, {"isr_uav": 0, "maritime_patrol_asset": 0})
    constrained_scored = score_coas(constrained_coas, run_simulations(constrained_coas, EVENTS, threats))
    constrained_rec = recommend(constrained_scored)
    assert constrained_rec.recommended is not None
    assert constrained_rec.recommended.coa.coa_id != "COA-006"
    assert constrained_rec.recommended.coa.feasibility_score == 1.0


def test_recommendation_handles_empty_scored_list():
    rec = recommend([])
    assert rec.recommended is None
    assert rec.alternatives == []
    assert "No courses of action" in rec.rationale


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
    resp = client.post("/coa/generate", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert len(body["coas"]) >= 3
    for coa in body["coas"]:
        assert "coa_id" in coa
        assert "title" in coa


def test_simulation_endpoint():
    resp = client.post("/coa/simulation/run", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert len(body["simulations"]) >= 3
    for sim in body["simulations"]:
        assert "success_probability" in sim
        assert "confidence_interval" in sim


def test_recommendation_endpoint():
    resp = client.post("/coa/recommendation/run", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["recommended"]["rank"] == 1
    assert "rationale" in body
    assert "edge_cases" in body


def test_briefing_endpoint():
    resp = client.post("/coa/briefing/generate", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["situation"]
    assert body["key_indicators"]
    assert body["assessment"]
    assert body["recommended_coa"]
    assert body["confidence"] in ("LOW", "MEDIUM", "HIGH")
