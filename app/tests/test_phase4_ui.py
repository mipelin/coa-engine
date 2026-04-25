from app.ui.streamlit_app import build_dashboard_data


def test_build_dashboard_data_returns_all_keys():
    data = build_dashboard_data()
    expected_keys = {
        "scenario", "events", "anomalies", "threats",
        "coas", "sims", "scored", "recommendation", "briefing",
        "asset_inventory", "source",
    }
    assert set(data.keys()) == expected_keys


def test_build_dashboard_data_events_non_empty():
    data = build_dashboard_data()
    assert len(data["events"]) > 0


def test_build_dashboard_data_threats_non_empty():
    data = build_dashboard_data()
    assert len(data["threats"]) > 0


def test_build_dashboard_data_scored_ranked():
    data = build_dashboard_data()
    scored = data["scored"]
    assert len(scored) >= 3
    assert scored[0].rank == 1


def test_build_dashboard_data_briefing_complete():
    data = build_dashboard_data()
    briefing = data["briefing"]
    assert briefing.situation
    assert briefing.key_indicators
    assert briefing.recommended_coa
    assert briefing.confidence in ("LOW", "MEDIUM", "HIGH")


def test_build_dashboard_data_is_cached():
    d1 = build_dashboard_data()
    d2 = build_dashboard_data()
    assert d1["briefing"].situation == d2["briefing"].situation


def test_build_dashboard_data_accepts_asset_inventory():
    data = build_dashboard_data(
        asset_inventory_items=(("isr_uav", 0), ("maritime_patrol_asset", 0)),
    )
    assert data["asset_inventory"]["isr_uav"] == 0
    assert any(coa.feasibility_score < 1.0 for coa in data["coas"])
