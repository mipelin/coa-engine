import inspect
import importlib

from app.ui.streamlit_app import build_dashboard_data
from app.ui import streamlit_app
from app.ui.dashboard_build import build_dashboard_html


def test_build_dashboard_data_returns_all_keys():
    data = build_dashboard_data()
    expected_keys = {
        "scenario", "events", "anomalies", "threats",
        "coas", "sims", "scored", "recommendation", "briefing",
        "asset_inventory", "asset_states", "source",
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
        scenario_id="baltic_hybrid_001",
        asset_inventory_items=(("isr_uav", 0), ("maritime_patrol_vessel", 0)),
    )
    assert data["asset_inventory"]["isr_uav"] == 0
    assert len(data["asset_states"]) == 2
    assert any(coa.feasibility_score < 1.0 for coa in data["coas"])


def test_build_dashboard_data_uses_template_engine_coas():
    data = build_dashboard_data()
    assert all(coa.source == "template_engine" for coa in data["coas"])


def test_llm_coa_generation_module_removed():
    import importlib
    assert importlib.util.find_spec("app.engine.llm_coa_generation") is None


def test_streamlit_visual_dependency_helper_returns_tuple():
    go, st_folium = streamlit_app._optional_visual_dependencies()
    assert go is None or hasattr(go, "Figure")
    assert st_folium is None or callable(st_folium)


def test_dashboard_html_contains_llm_indicator_and_event_summary_panel():
    html = build_dashboard_html()
    assert 'id="llm-indicator"' in html
    assert 'id="llm-health-banner"' in html
    assert 'id="btn-llm-test"' in html
    assert 'id="event-summary-body"' in html
    assert "LLM working" in html or "LLM idle" in html
    assert 'id="contact-detail-body"' in html


def test_dashboard_html_has_no_top_instruction_bar():
    html = build_dashboard_html()
    assert '<div class="subhdr">' not in html


def test_dashboard_js_briefing_requests_are_not_cached_by_language():
    html = build_dashboard_html()
    assert "state.briefingsByLang" not in html
    assert "const result = await api(`/v1/engine/briefing?lang=${encodeURIComponent(lang)}`);" in html


def test_dashboard_js_keeps_ui_and_briefing_languages_independent():
    html = build_dashboard_html()
    assert "if (briefingLang && briefingLang.value !== state.uiLanguage)" not in html
    assert "await applyUiLanguage(evt.target.value, {refreshBriefing: false});" in html
    assert "await applyUiLanguage(evt.target.value, {refreshBriefing: true});" not in html


def test_dashboard_js_polls_llm_status_every_second_without_reconnect_on_language_change():
    html = build_dashboard_html()
    assert "window.setInterval(refreshLlmStatus, 1000);" in html
    assert "connectSocket()" in html
    apply_start = html.index("async function applyUiLanguage")
    apply_end = html.index("async function startEngine")
    apply_body = html[apply_start:apply_end]
    assert "connectSocket" not in apply_body
    assert "location.reload" not in apply_body


def test_dashboard_uses_cop_as_primary_snapshot_source():
    html = build_dashboard_html()
    assert "const snapshot = await api('/v1/engine/cop');" in html
    assert "const snapshot = await api('/v1/engine/analysis');" not in html


def test_event_summary_panel_uses_internal_scroll_not_page_scroll():
    html = build_dashboard_html()
    assert ".event-summary-panel{flex:0 0 28%" in html
    assert "overflow:hidden;display:flex;flex-direction:column" in html
    assert ".esp-body{font-size:12px;line-height:1.6;color:#dbeafe;overflow:auto;flex:1;min-height:0" in html


def test_dashboard_js_sends_ui_language_hint_without_forcing_ask_language():
    html = build_dashboard_html()
    assert "ui_language_hint: state.uiLanguage || 'en'" in html
    assert "force_language: state.uiLanguage || 'en'" not in html


def test_dashboard_has_map_placement_banner_and_seed_help():
    html = build_dashboard_html()
    assert 'id="map-mode-banner"' in html
    assert "Scenario seed" in html
    assert "Same seed = same scenario" in html
    assert 'id="contact-detail-panel"' in html
    assert "contact-detail-panel" in html


def test_dashboard_has_map_add_and_move_payload_paths():
    html = build_dashboard_html()
    assert "await injectUnit(evt.latlng);" in html
    assert "await moveUnitTo(state.selectedEntityId, evt.latlng);" in html
    assert "await api(`/v1/engine/contacts/${encodeURIComponent(entityId)}`" in html
    assert 'id="combat-feed-enabled"' in html
    assert 'id="combat-feed-density"' in html
    assert 'id="combat-feed-scenario"' in html
    assert 'id="combat-inject-suspicious"' in html


def test_dashboard_formats_coordinates_as_gps_lat_lon():
    html = build_dashboard_html()
    assert "function fmtCoord(value)" in html
    assert "Number(value).toFixed(6)" in html
    assert "Latitude" in html
    assert "Longitude" in html


def test_dashboard_uses_professional_svg_map_icons():
    html = build_dashboard_html()
    assert "function markerSymbolSvg(unitClass, palette, selected = false, source = 'simulation')" in html
    assert "L.divIcon" in html
    assert "unit-icon" in html


def test_dashboard_exposes_cop_panels_and_demo_mode():
    html = build_dashboard_html()
    assert 'id="fused-track-list"' in html
    assert 'id="target-panel"' in html
    assert 'id="decision-panel"' in html
    assert 'id="effects-panel"' in html
    assert 'id="replay-panel"' in html
    assert 'id="aar-output"' in html
    assert 'id="demo-mode-run"' in html
    assert 'id="demo-warm-start"' in html
    assert 'id="toggle-fused-tracks"' in html
    assert 'id="toggle-raw-contacts"' in html


def test_dashboard_auto_falls_back_to_raw_contacts_until_fusion_exists():
    html = build_dashboard_html()
    assert "state.showRawContacts = true;" in html
    assert "state.autoRawContactsFallback = true;" in html
    assert "No fused tracks yet. Raw contacts are shown until fusion initializes." in html


def test_dashboard_demo_mode_queues_briefing_without_blocking():
    html = build_dashboard_html()
    assert "Briefing queued (non-blocking)" in html
    assert "void ensureBriefing(" in html
    assert "await fetchBriefing();" not in html


def test_dashboard_operational_effects_are_human_readable():
    html = build_dashboard_html()
    assert "function effectSeverityLabel(value)" in html
    assert "Detection ↓" in html
    assert "Success ↓" in html
    assert "Time ↑" in html
    assert "Risk ↑" in html
    assert "Slight degradation" in html
    assert "Severely degraded" in html


def test_dashboard_polls_llm_health_and_status():
    html = build_dashboard_html()
    assert "await api('/v1/engine/llm/health')" in html
    assert "window.setInterval(refreshLlmStatus, 1000);" in html
    assert "window.setInterval(refreshLlmHealth, 3000);" in html
