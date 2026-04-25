from app.core.schemas import OperationalEvent
from app.engine.anomaly_detection import detect_anomalies
from app.engine.event_ingestion import load_scenario_events
from app.engine.feature_engineering import compute_features
from app.engine.threat_assessment import assess_threats
from app.main import app

from fastapi.testclient import TestClient

client = TestClient(app)

EVENTS = load_scenario_events()


def _run_pipeline(events=None):
    ev = events or EVENTS
    features = compute_features(ev)
    anomalies = detect_anomalies(ev, features)
    threats = assess_threats(ev, features, anomalies)
    return features, anomalies, threats


# --- Feature engineering ---


def test_compute_features_returns_one_per_event():
    features = compute_features(EVENTS)
    assert len(features) == len(EVENTS)


def test_distances_are_non_negative():
    features = compute_features(EVENTS)
    for f in features:
        assert f.distance_to_nearest_critical_infrastructure >= 0
        assert f.distance_to_second_cable >= 0


def test_scores_are_normalized():
    features = compute_features(EVENTS)
    for f in features:
        assert 0.0 <= f.speed_anomaly_score <= 1.0
        assert 0.0 <= f.proximity_to_recent_incident <= 1.0
        assert 0.0 <= f.multi_source_correlation_score <= 1.0
        assert 0.0 <= f.event_density_score <= 1.0
        assert 0.0 <= f.jamming_nearby <= 1.0
        assert 0.0 <= f.convoy_activity_nearby <= 1.0
        assert 0.0 <= f.heading_towards_critical_asset <= 1.0


def test_ves_susp_001_has_course_changes():
    features = compute_features(EVENTS)
    susp1_feats = [f for f in features if f.entity_id == "VES-SUSP-001"]
    max_changes = max(f.course_change_count for f in susp1_feats)
    assert max_changes >= 2


def test_suspicious_vessel_near_cable_has_high_proximity():
    features = compute_features(EVENTS)
    e017_feats = [f for f in features if f.event_id == "E017"]
    assert len(e017_feats) == 1
    assert e017_feats[0].distance_to_nearest_critical_infrastructure < 20.0


# --- Anomaly detection ---


def test_anomaly_results_match_event_count():
    _, anomalies, _ = _run_pipeline()
    assert len(anomalies) == len(EVENTS)


def test_cable_severance_is_critical():
    _, anomalies, _ = _run_pipeline()
    e007 = next(a for a in anomalies if a.event_id == "E007")
    assert e007.anomaly_level == "CRITICAL"
    assert e007.anomaly_score >= 50.0


def test_all_anomaly_scores_in_range():
    _, anomalies, _ = _run_pipeline()
    for a in anomalies:
        assert 0.0 <= a.anomaly_score <= 100.0


def test_anomaly_explanations_are_non_empty():
    _, anomalies, _ = _run_pipeline()
    for a in anomalies:
        assert len(a.explanations) >= 1


def test_suspicious_vessel_events_have_elevated_anomaly():
    _, anomalies, _ = _run_pipeline()
    susp_anomalies = [a for a in anomalies if a.entity_id == "VES-SUSP-001"]
    max_score = max(a.anomaly_score for a in susp_anomalies)
    assert max_score >= 40.0


# --- Threat assessment ---


def test_ves_susp_001_in_threat_results():
    _, _, threats = _run_pipeline()
    entity_ids = [t.entity_id for t in threats]
    assert "VES-SUSP-001" in entity_ids


def test_at_least_one_high_or_critical_threat():
    _, _, threats = _run_pipeline()
    levels = {t.threat_level for t in threats}
    assert "HIGH" in levels or "CRITICAL" in levels


def test_allied_vessels_not_in_threat_results():
    _, _, threats = _run_pipeline()
    entity_ids = [t.entity_id for t in threats]
    assert "VES-ALLIED-001" not in entity_ids
    assert "VES-ALLIED-002" not in entity_ids


def test_isr_asset_not_in_threat_results():
    _, _, threats = _run_pipeline()
    entity_ids = [t.entity_id for t in threats]
    assert "ISR-001" not in entity_ids


def test_infrastructure_not_in_threat_results():
    _, _, threats = _run_pipeline()
    entity_ids = [t.entity_id for t in threats]
    assert "CABLE-ALPHA" not in entity_ids
    assert "CABLE-BETA" not in entity_ids


def test_threat_probabilities_in_range():
    _, _, threats = _run_pipeline()
    for t in threats:
        assert 0.0 <= t.threat_probability <= 1.0
        assert 0.0 <= t.confidence <= 1.0


def test_threat_results_sorted_descending():
    _, _, threats = _run_pipeline()
    probs = [t.threat_probability for t in threats]
    assert probs == sorted(probs, reverse=True)


# --- /analysis/run endpoint ---


def test_analysis_run_endpoint():
    resp = client.post("/v1/analysis/run", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["events_processed"] == 20
    assert body["features_computed"] == 20
    assert len(body["features"]) == 20
    assert len(body["anomalies"]) == 20
    assert len(body["threats"]) > 0
    assert any(t["threat_level"] in ("HIGH", "CRITICAL") for t in body["threats"])


def test_analysis_run_with_custom_events():
    custom = [
        OperationalEvent(
            event_id="T1",
            timestamp="2025-06-15T08:00:00Z",
            event_type="vessel_position",
            source="test",
            confidence=0.8,
            lat=57.5,
            lon=19.0,
            entity_id="VES-X",
            entity_type="suspicious_vessel",
            description="Test",
            attributes={"speed_knots": 0.5, "heading": 90.0},
        )
    ]
    payload = {"events": [e.model_dump(mode="json") for e in custom]}
    resp = client.post("/v1/analysis/run", json=payload)
    assert resp.status_code == 200
    assert resp.json()["events_processed"] == 1


def test_analysis_includes_tracks_and_temporal():
    resp = client.post("/v1/analysis/run", json={})
    body = resp.json()
    assert "tracks" in body
    assert "temporal" in body
    assert len(body["tracks"]) > 0


# --- Phase 1 tests still pass ---


def test_phase1_health_still_works():
    resp = client.get("/health")
    assert resp.status_code == 200
