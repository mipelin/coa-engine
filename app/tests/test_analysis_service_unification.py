from __future__ import annotations

from app.engine.state_store import get_state_store


def _events_payload(events):
    return {
        "events": [event.model_dump(mode="json") for event in events],
        "use_session": False,
    }


def _recommendation_id(recommendation: dict | None) -> str | None:
    if not recommendation or not recommendation.get("recommended"):
        return None
    return recommendation["recommended"]["coa"]["coa_id"]


def _target_snapshot(targets: list[dict]) -> list[tuple[str, str, str, str]]:
    return [
        (
            item["id"],
            item["priority_level"],
            item["recommended_action"],
            item["roe_status"],
        )
        for item in targets
    ]


def _fusion_snapshot(tracks: list[dict]) -> list[tuple[str, str, int, tuple[str, ...]]]:
    return [
        (
            item["primary_entity_id"],
            item["track_type"],
            item["source_count"],
            tuple(item["sources"]),
        )
        for item in tracks
    ]


def test_legacy_analysis_and_coa_routes_use_same_canonical_outputs(client, baltic_events):
    payload = _events_payload(baltic_events)

    analysis = client.post("/v1/analysis/run", json=payload).json()
    coas = client.post("/v1/coa/generate", json=payload).json()
    recommendation = client.post("/v1/coa/recommendation/run", json=payload).json()

    analysis_coas = [(item["coa_id"], item["roe_status"]) for item in analysis["coas"]]
    coa_route_coas = [(item["coa_id"], item["roe_status"]) for item in coas["coas"]]

    assert analysis["pipeline"] == "canonical"
    assert coas["pipeline"] == "canonical"
    assert analysis_coas == coa_route_coas
    assert _recommendation_id(analysis["recommendation"]) == _recommendation_id(recommendation)


def test_recommendation_and_roe_identical_across_legacy_routes(client, baltic_events):
    payload = _events_payload(baltic_events)

    analysis = client.post("/v1/analysis/run", json=payload).json()
    recommendation = client.post("/v1/coa/recommendation/run", json=payload).json()

    analysis_rec = analysis["recommendation"]["recommended"]
    route_rec = recommendation["recommended"]

    assert analysis_rec["coa"]["coa_id"] == route_rec["coa"]["coa_id"]
    assert analysis_rec["coa"]["roe_status"] == route_rec["coa"]["roe_status"]
    assert analysis_rec["coa"]["roe_reason"] == route_rec["coa"]["roe_reason"]
    assert analysis_rec["total_score"] == route_rec["total_score"]


def test_live_engine_analysis_matches_legacy_route_when_given_same_live_events(client):
    client.post("/v1/engine/scenario/load", json={"scenario_id": "baltic_hybrid_001", "seed": 42})
    client.post("/v1/engine/tick")

    live = client.get("/v1/engine/analysis").json()
    live_events = get_state_store().contact_history_as_events()
    legacy = client.post("/v1/analysis/run", json=_events_payload(live_events)).json()

    live_top = live["threats"][0] if live["threats"] else None
    legacy_top = legacy["threats"][0] if legacy["threats"] else None

    assert legacy["metadata"]["canonical_pipeline"] is True
    assert live["state"]["current_threat_level"] == (legacy_top["threat_level"] if legacy_top else "LOW")
    assert (live_top["entity_id"] if live_top else None) == (legacy_top["entity_id"] if legacy_top else None)
    assert [
        (item["coa"]["coa_id"], item["coa"]["roe_status"])
        for item in live["scored_coas"]
    ] == [
        (item["coa"]["coa_id"], item["coa"]["roe_status"])
        for item in legacy["scored_coas"]
    ]
    assert _fusion_snapshot(live["fused_tracks"]) == _fusion_snapshot(legacy["fused_tracks"])
    assert _target_snapshot(live["targets"]) == _target_snapshot(legacy["targets"])
    assert _target_snapshot(live["top_targets"]) == _target_snapshot(legacy["top_targets"])
    assert _recommendation_id(live["recommendation"]) == _recommendation_id(legacy["recommendation"])


def test_analysis_routes_do_not_call_llm(client, baltic_events, monkeypatch):
    def fail_llm_call(*args, **kwargs):
        raise AssertionError("LLM must not be called during deterministic analysis")

    monkeypatch.setattr("app.engine.llm_client.LLMClient._chat_raw", fail_llm_call)

    payload = _events_payload(baltic_events)
    assert client.post("/v1/analysis/run", json=payload).status_code == 200
    assert client.post("/v1/coa/generate", json=payload).status_code == 200
    assert client.post("/v1/coa/simulation/run", json=payload).status_code == 200
    assert client.post("/v1/coa/recommendation/run", json=payload).status_code == 200
