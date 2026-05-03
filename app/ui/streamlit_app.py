from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.core.constants import EntityType, EventType, SCENARIO_CABLE_ROUTES
from app.core.schemas import (
    AnomalyResult,
    AssetState,
    Briefing,
    CourseOfAction,
    OperationalEvent,
    Recommendation,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from app.engine.asset_state import build_simulated_asset_states
from app.engine.anomaly_detection import detect_anomalies
from app.engine.coa_generation import generate_coas
from app.engine.event_ingestion import load_scenario, list_scenarios
from app.engine.explanation import generate_briefing
from app.engine.feature_engineering import compute_features
from app.engine.llm_narrative import enrich_briefing, enrich_threat_narrative, entity_risk_narrative
from app.engine.recommendation import recommend
from app.engine.scenario_generator import ScenarioGenerator
from app.engine.scoring import score_coas
from app.engine.simulation import run_simulations
from app.engine.threat_assessment import assess_threats

# ---------------------------------------------------------------------------
# Asset definitions — grouped by domain, with clear labels
# ---------------------------------------------------------------------------

ASSET_GROUPS = {
    "Maritime": {
        "maritime_patrol_vessel": ("Patrol Vessel", 1),
        "coast_guard_cutter": ("Coast Guard Cutter", 1),
        "submarine_sonar": ("Submarine / Sonar", 0),
        "diver_team": ("Diver Team", 0),
    },
    "Air / ISR": {
        "isr_uav": ("ISR UAV", 2),
        "maritime_helicopter": ("Maritime Helicopter", 1),
        "satellite_pass": ("Satellite Pass", 1),
        "awacs_coverage": ("AWACS / AEW", 0),
    },
    "Intelligence": {
        "sigint_team": ("SIGINT Team", 1),
        "osint_cell": ("OSINT Cell", 1),
        "intelligence_team": ("Intelligence Analysis Team", 1),
    },
    "Liaison / Coordination": {
        "cable_operator_liaison": ("Cable Operator Link", 1),
        "airspace_coordinator": ("Airspace Coordinator", 1),
        "border_patrol_liaison": ("Border Patrol Link", 1),
        "coast_guard_liaison": ("Coast Guard Link", 1),
        "atc_liaison": ("ATC Liaison", 1),
    },
}

# Flat lookup: asset_key -> label
ASSET_LABELS: dict[str, str] = {}
DEFAULT_ASSET_INVENTORY: dict[str, int] = {}
for _group, _assets in ASSET_GROUPS.items():
    for _key, (_label, _count) in _assets.items():
        ASSET_LABELS[_key] = _label
        DEFAULT_ASSET_INVENTORY[_key] = _count

# Map asset keys to approximate deployment positions relative to scenario center
# Used to show assets on the map
ASSET_ICON_MAP = {
    "maritime_patrol_vessel": ("blue", "anchor"),
    "coast_guard_cutter": ("blue", "anchor"),
    "submarine_sonar": ("darkblue", "anchor"),
    "diver_team": ("darkblue", "anchor"),
    "isr_uav": ("cadetblue", "plane"),
    "maritime_helicopter": ("cadetblue", "plane"),
    "satellite_pass": ("lightgray", "satellite"),
    "awacs_coverage": ("lightgray", "satellite"),
    "sigint_team": ("darkpurple", "signal"),
    "osint_cell": ("darkpurple", "signal"),
    "intelligence_team": ("darkpurple", "signal"),
    "cable_operator_liaison": ("darkgreen", "star"),
    "airspace_coordinator": ("orange", "info-sign"),
    "border_patrol_liaison": ("gray", "info-sign"),
    "coast_guard_liaison": ("blue", "info-sign"),
    "atc_liaison": ("orange", "info-sign"),
}

ASSET_OFFSETS = {
    "maritime_patrol_vessel": (-0.8, 0.5),
    "coast_guard_cutter": (-0.5, -0.6),
    "submarine_sonar": (0.3, -0.9),
    "diver_team": (0.1, 0.8),
    "isr_uav": (0.6, 0.3),
    "maritime_helicopter": (-0.4, 0.7),
    "satellite_pass": (0.0, 0.0),
    "awacs_coverage": (-0.2, 0.9),
    "sigint_team": (-0.6, -0.3),
    "osint_cell": (0.7, -0.4),
    "intelligence_team": (0.5, 0.6),
    "cable_operator_liaison": (0.0, 0.0),
    "airspace_coordinator": (0.9, 0.1),
    "border_patrol_liaison": (-0.9, -0.1),
    "coast_guard_liaison": (0.4, -0.7),
    "atc_liaison": (0.8, 0.5),
}


# ---------------------------------------------------------------------------
# Data preparation — 3 cached layers: analysis (fast), COAs (medium), LLM (slow)
# ---------------------------------------------------------------------------

@st.cache_data
def _run_analysis(scenario_id: str) -> dict[str, Any]:
    """Fast rule-based analysis — only depends on scenario, ~1 second."""
    scenario = load_scenario(scenario_id)
    if not scenario.events:
        raise ValueError(f"Scenario {scenario_id} has no events")

    events = scenario.events
    infrastructure = [ci.model_dump() for ci in scenario.critical_infrastructure] if scenario.critical_infrastructure else None
    features = compute_features(events, infrastructure)
    anomalies = detect_anomalies(events, features)
    threats = assess_threats(events, features, anomalies)

    return {
        "scenario": scenario, "events": events, "features": features,
        "anomalies": anomalies, "threats": threats,
    }


@st.cache_data
def _run_coa_pipeline(
    scenario_id: str,
    asset_inventory_items: tuple[tuple[str, int], ...],
) -> dict[str, Any]:
    """COA generation + simulation + scoring — depends on scenario + assets."""
    asset_inventory = dict(asset_inventory_items)
    analysis = _run_analysis(scenario_id)
    events = analysis["events"]
    threats = analysis["threats"]
    asset_states = build_simulated_asset_states(asset_inventory, events)

    coas = generate_coas(events, threats, asset_inventory, asset_states)
    sims = run_simulations(coas, events, threats)
    scored = score_coas(coas, sims)
    rec = recommend(scored, asset_states=asset_states, asset_inventory=asset_inventory)

    return {
        "coas": coas, "sims": sims, "scored": scored,
        "recommendation": rec, "asset_inventory": asset_inventory,
        "asset_states": asset_states,
    }


@st.cache_data
def _run_llm_enrichment(scenario_id: str) -> dict[str, Any]:
    """Slow LLM enrichment — only depends on scenario, runs once per scenario."""
    analysis = _run_analysis(scenario_id)
    events = analysis["events"]
    threats = analysis["threats"]

    threat_narrative = enrich_threat_narrative(threats, events)

    entity_narratives: dict[str, str] = {}
    for t in threats[:3]:
        narrative = entity_risk_narrative(t.entity_id, t, events)
        if narrative:
            entity_narratives[t.entity_id] = narrative

    return {
        "threat_narrative": threat_narrative,
        "entity_narratives": entity_narratives,
    }


@st.cache_data
def build_dashboard_data(
    scenario_id: str = "baltic_hybrid_001",
    asset_inventory_items: tuple[tuple[str, int], ...] | None = None,
) -> dict[str, Any]:
    """Combine all layers — fast re-run when only assets change."""
    asset_inventory_items = asset_inventory_items or tuple(DEFAULT_ASSET_INVENTORY.items())
    asset_inventory = dict(asset_inventory_items)

    analysis = _run_analysis(scenario_id)
    coa_data = _run_coa_pipeline(scenario_id, asset_inventory_items)
    llm_data = _run_llm_enrichment(scenario_id)

    events = analysis["events"]
    anomalies = analysis["anomalies"]
    threats = analysis["threats"]
    scenario = analysis["scenario"]
    scenario_name = scenario.name
    coas = coa_data["coas"]
    sims = coa_data["sims"]
    scored = coa_data["scored"]
    rec = coa_data["recommendation"]

    if llm_data["threat_narrative"]:
        rec = rec.model_copy(update={"threat_narrative": llm_data["threat_narrative"]})

    briefing = generate_briefing(events, anomalies, threats, scored, rec, scenario_name)

    if llm_data["threat_narrative"]:
        enriched = enrich_briefing(briefing.assessment, llm_data["threat_narrative"])
        if enriched:
            briefing = briefing.model_copy(update={"enriched_assessment": enriched})

    if llm_data["entity_narratives"]:
        briefing = briefing.model_copy(update={"entity_risk_narratives": llm_data["entity_narratives"]})

    return {
        "scenario": scenario, "events": events, "anomalies": anomalies,
        "threats": threats, "coas": coas, "sims": sims,
        "scored": scored, "recommendation": rec, "briefing": briefing,
        "asset_inventory": asset_inventory, "asset_states": coa_data["asset_states"], "source": "engine+llm",
    }


def _optional_visual_dependencies() -> tuple[Any | None, Any | None]:
    go = None
    st_folium = None
    try:
        import plotly.graph_objects as plotly_go

        go = plotly_go
    except ModuleNotFoundError:
        pass
    try:
        from streamlit_folium import st_folium as folium_renderer

        st_folium = folium_renderer
    except ModuleNotFoundError:
        pass
    return go, st_folium


# ---------------------------------------------------------------------------
# Color / icon helpers
# ---------------------------------------------------------------------------

THREAT_LEVEL_COLORS = {
    "CRITICAL": "#ff0000", "HIGH": "#ff6600", "MEDIUM": "#ffcc00", "LOW": "#33cc33",
}

ROE_BADGE_COLORS = {
    "allowed": "#33cc33",
    "requires_authorization": "#ffcc00",
    "restricted": "#ff8c00",
    "rejected": "#ff0000",
}


def _marker_color(event_type, entity_type) -> str:
    et = event_type.value if hasattr(event_type, 'value') else str(event_type)
    if et == "cable_severance":
        return "darkred"
    if et == "jamming_detected":
        return "darkpurple"
    ent = entity_type.value if hasattr(entity_type, 'value') else str(entity_type)
    color_map = {
        "suspicious_vessel": "red", "allied_vessel": "blue", "uav": "orange",
        "convoy": "purple", "subsea_cable": "darkgreen", "isr_asset": "cadetblue", "airport": "gray",
    }
    return color_map.get(ent, "gray")


def _threat_color(level: str) -> str:
    return THREAT_LEVEL_COLORS.get(level, "#999999")


# ---------------------------------------------------------------------------
# Map builder — now includes deployed assets
# ---------------------------------------------------------------------------

def build_map(events, scenario, asset_inventory: dict[str, int], asset_states: list[AssetState] | None = None) -> Any:
    import folium

    # Center map on scenario infrastructure centroid
    if scenario.critical_infrastructure:
        avg_lat = sum(ci.lat for ci in scenario.critical_infrastructure) / len(scenario.critical_infrastructure)
        avg_lon = sum(ci.lon for ci in scenario.critical_infrastructure) / len(scenario.critical_infrastructure)
    elif events:
        avg_lat = sum(e.lat for e in events) / len(events)
        avg_lon = sum(e.lon for e in events) / len(events)
    else:
        avg_lat, avg_lon = 57.5, 19.5

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=5, tiles="CartoDB positron")

    # Layer 0: Subsea cable polylines with status
    scenario_id = scenario.scenario_id if hasattr(scenario, "scenario_id") else "baltic_hybrid_001"
    cable_routes = SCENARIO_CABLE_ROUTES.get(scenario_id, [])
    for cable in cable_routes:
        points = [(p["lat"], p["lon"]) for p in cable["points"]]
        if not points:
            continue
        status = cable.get("status", "intact")
        cable_colors = {
            "intact": "#2e8b57",
            "severed": "#cc0000",
            "threatened": "#ff6600",
        }
        line_color = cable_colors.get(status, "#2e8b57")
        dash_pattern = "10, 8" if status == "threatened" else None
        folium.PolyLine(
            locations=points,
            color=line_color,
            weight=4,
            opacity=0.8,
            popup=f"<b>{cable['name']}</b><br>Status: {status.title()}",
        ).add_to(m)
        # Mark cable endpoints
        for i, pt in enumerate(points):
            landing_indices = cable.get("landing_points", [])
            is_landing = i in landing_indices
            if is_landing or i == 0 or i == len(points) - 1:
                folium.CircleMarker(
                    location=pt,
                    radius=5,
                    color=line_color,
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"{cable['name']} — {'Shore Landing' if is_landing else 'Waypoint'}",
                ).add_to(m)

    # Layer 1: Critical infrastructure
    for infra in scenario.critical_infrastructure:
        color = "darkgreen" if infra.type in ("subsea_cable", "pipeline") else "darkblue"
        folium.Marker(
            location=[infra.lat, infra.lon],
            popup=f"<b>{infra.name}</b><br>Type: {infra.type}<br>Lat: {infra.lat:.4f} Lon: {infra.lon:.4f}",
            icon=folium.Icon(color=color, icon="star"),
        ).add_to(m)

    # Layer 2: Threat events
    EVENT_ICONS = {
        EventType.CABLE_SEVERANCE: "bolt",
        EventType.UAV_DETECTION: "plane",
        EventType.JAMMING_DETECTED: "signal",
        EventType.CONVOY_SIGHTING: "truck",
        EventType.VESSEL_COURSE_CHANGE: "random",
    }

    seen_positions: set[str] = set()
    for ev in events:
        key = f"{ev.entity_id}:{ev.lat:.2f},{ev.lon:.2f}"
        if key in seen_positions:
            continue
        seen_positions.add(key)

        color = _marker_color(ev.event_type, ev.entity_type)
        icon = EVENT_ICONS.get(ev.event_type, "info-sign")
        popup_text = (
            f"<b>{ev.entity_id}</b><br>"
            f"Type: {ev.event_type.value}<br>"
            f"Position: {ev.lat:.4f}N {ev.lon:.4f}E<br>"
            f"Confidence: {ev.confidence:.0%}<br>"
            f"{ev.description[:120]}"
        )
        folium.Marker(
            location=[ev.lat, ev.lon],
            popup=popup_text,
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
        ).add_to(m)

    # Layer 3: Jamming circles
    for ev in events:
        if ev.event_type == EventType.JAMMING_DETECTED:
            radius_km = ev.attributes.get("radius_nm", 20) * 1.852
            folium.Circle(
                location=[ev.lat, ev.lon],
                radius=radius_km * 1000,
                color="purple", fill=True, fill_opacity=0.08,
                popup=f"Jamming radius: {ev.attributes.get('radius_nm', 20)} nm",
            ).add_to(m)

    # Layer 4: Deployed assets — show available assets around the AO
    deployed_count = 0
    for asset_state in asset_states or []:
        if asset_state.quantity_available <= 0:
            continue
        asset_key = asset_state.asset_id
        label = asset_state.display_name or ASSET_LABELS.get(asset_key, asset_key)
        icon_color, icon_name = ASSET_ICON_MAP.get(asset_key, ("white", "info-sign"))
        a_lat = asset_state.lat if asset_state.lat is not None else avg_lat
        a_lon = asset_state.lon if asset_state.lon is not None else avg_lon

        popup = (
            f"<b>{label}</b><br>Qty: {asset_state.quantity_available}<br>Status: {asset_state.status}"
            f"<br>Base: {asset_state.location_label or asset_state.home_base or 'Unknown'}"
            f"<br>Pos: {a_lat:.4f}N {a_lon:.4f}E"
            f"<br>ETA: {asset_state.response_eta_min or 'N/A'} min"
        )
        folium.Marker(
            location=[a_lat, a_lon],
            popup=popup,
            icon=folium.Icon(color=icon_color, icon=icon_name, prefix="fa"),
        ).add_to(m)
        deployed_count += 1

    # Layer 5: Asset coverage circles for key assets
    coverage_assets = {
        "isr_uav": 100,          # km radius
        "awacs_coverage": 300,
        "maritime_helicopter": 150,
        "sigint_team": 80,
    }
    for asset_key, radius_km in coverage_assets.items():
        asset_state = next((state for state in (asset_states or []) if state.asset_id == asset_key), None)
        count = asset_inventory.get(asset_key, 0)
        if count <= 0 or asset_state is None:
            continue
        a_lat = asset_state.lat if asset_state.lat is not None else avg_lat
        a_lon = asset_state.lon if asset_state.lon is not None else avg_lon
        folium.Circle(
            location=[a_lat, a_lon],
            radius=radius_km * 1000,
            color="cadetblue", fill=True, fill_opacity=0.04,
            popup=f"{ASSET_LABELS[asset_key]} coverage: ~{radius_km} km",
        ).add_to(m)

    return m


# ---------------------------------------------------------------------------
# Streamlit app
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="COA Engine", layout="wide", page_icon=":shield:")
    go, st_folium = _optional_visual_dependencies()

    st.title("COA Engine — Decision Superiority Module")
    st.caption(
        "Synthetic decision-support prototype. No autonomous targeting or command execution. "
        "All data is simulated."
    )

    if "asset_inventory" not in st.session_state:
        st.session_state.asset_inventory = dict(DEFAULT_ASSET_INVENTORY)
    if "scenario_seed" not in st.session_state:
        st.session_state.scenario_seed = 42
    if "scenario_timing_jitter" not in st.session_state:
        st.session_state.scenario_timing_jitter = 0
    if "scenario_position_jitter" not in st.session_state:
        st.session_state.scenario_position_jitter = 0.0

    # ---- Sidebar ----
    with st.sidebar:
        st.header("Scenario & Assets")
        st.caption("Select scenario and adjust available forces.")

        # --- Scenario Generator Templates ---
        st.subheader("Scenario Template")
        gen_templates = ScenarioGenerator.list_templates()
        gen_options = {t["scenario_id"]: t["display_name"] for t in gen_templates}
        if not gen_options:
            gen_options = {"baltic_hybrid_001": "Baltic Cable Protection"}

        # Also include legacy scenario IDs from event_ingestion
        scenario_list = list_scenarios()
        scenario_options = {s["scenario_id"]: s["name"] for s in scenario_list}
        if not scenario_options:
            scenario_options = {"baltic_hybrid_001": "Baltic Sea Hybrid Threat Scenario"}

        # Merge: prefer generator templates (they have display_name), fill gaps from legacy
        all_scenario_options = dict(gen_options)
        for sid, name in scenario_options.items():
            all_scenario_options.setdefault(sid, name)

        selected_scenario = st.selectbox(
            "Scenario",
            options=list(all_scenario_options.keys()),
            format_func=lambda x: all_scenario_options[x],
            index=0,
        )

        st.divider()
        st.markdown("**Simulation Controls**")
        st.session_state.scenario_seed = st.number_input(
            "Seed", min_value=0, max_value=99999,
            value=st.session_state.scenario_seed, step=1,
        )
        st.session_state.scenario_timing_jitter = st.number_input(
            "Timing Jitter (ticks)", min_value=0, max_value=10,
            value=st.session_state.scenario_timing_jitter, step=1,
        )
        st.session_state.scenario_position_jitter = st.number_input(
            "Position Jitter (deg)", min_value=0.0, max_value=1.0,
            value=st.session_state.scenario_position_jitter, step=0.01,
            format="%.2f",
        )

        col_start, col_rst = st.columns(2)
        with col_start:
            if st.button("Start Scenario", type="primary"):
                build_dashboard_data.clear()
                _run_coa_pipeline.clear()
                _run_analysis.clear()
                st.rerun()
        with col_rst:
            if st.button("Reset All"):
                st.session_state.asset_inventory = dict(DEFAULT_ASSET_INVENTORY)
                st.session_state.scenario_seed = 42
                st.session_state.scenario_timing_jitter = 0
                st.session_state.scenario_position_jitter = 0.0
                build_dashboard_data.clear()
                _run_coa_pipeline.clear()
                _run_analysis.clear()
                st.rerun()

        # Show scenario metadata if available from generator
        try:
            gen = ScenarioGenerator(
                seed=st.session_state.scenario_seed,
                timing_jitter=st.session_state.scenario_timing_jitter,
                position_jitter=st.session_state.scenario_position_jitter,
            )
            template = gen.generate(selected_scenario)
            st.divider()
            st.markdown("**Scenario Metadata**")
            meta = template.metadata
            st.caption(f"**{meta['display_name']}**")
            st.caption(meta["description"][:120])
            st.caption(f"Entities: {meta['entity_count']} | Stimuli: {meta['stimuli_count']} | Seed: {meta['seed']}")
            if meta.get("environment"):
                env = meta["environment"]
                env_str = " | ".join(f"{k}: {v}" for k, v in env.items())
                st.caption(f"Env: {env_str}")
        except ValueError:
            pass

        st.divider()
        st.markdown("**Available Forces**")
        for group_name, assets in ASSET_GROUPS.items():
            st.markdown(f"<small><b>{group_name}</b></small>", unsafe_allow_html=True)
            for asset_key, (label, default) in assets.items():
                st.session_state.asset_inventory[asset_key] = st.number_input(
                    label,
                    min_value=0, max_value=10,
                    value=int(st.session_state.asset_inventory.get(asset_key, default)),
                    step=1, key=f"asset_{asset_key}",
                )

        col_reset, col_run = st.columns(2)
        with col_reset:
            if st.button("Reset"):
                st.session_state.asset_inventory = dict(DEFAULT_ASSET_INVENTORY)
                build_dashboard_data.clear()
                _run_coa_pipeline.clear()
                st.rerun()
        with col_run:
            if st.button("Re-analyze"):
                build_dashboard_data.clear()
                _run_coa_pipeline.clear()
                st.rerun()

    # ---- Run pipeline ----
    asset_inventory_items = tuple(sorted(
        (asset, int(count)) for asset, count in st.session_state.asset_inventory.items()
    ))
    data = build_dashboard_data(selected_scenario, asset_inventory_items)
    scenario = data["scenario"]
    events = data["events"]
    anomalies = data["anomalies"]
    threats = data["threats"]
    scored = data["scored"]
    rec = data["recommendation"]
    briefing = data["briefing"]
    sims = data["sims"]
    asset_inventory = data["asset_inventory"]
    asset_states = data["asset_states"]
    data_source = data.get("source", "engine")

    with st.sidebar:
        st.divider()
        st.metric("Events", len(events))
        st.metric("Threat Entities", len(threats))
        st.metric("COAs", len(scored))

        # ROE status counts
        roe_counts = {"allowed": 0, "restricted": 0, "requires_authorization": 0, "rejected": 0}
        for s in scored:
            status = s.coa.roe_status
            if status in roe_counts:
                roe_counts[status] += 1
        roe_badge_cols = st.columns(4)
        for col, (status, count) in zip(roe_badge_cols, roe_counts.items()):
            color = ROE_BADGE_COLORS.get(status, "#999")
            col.markdown(
                f"<div style='background:{color}; color:white; padding:4px 6px; "
                f"border-radius:3px; text-align:center; font-size:0.75em;'>"
                f"{status.replace('_', ' ').title()}<br><b>{count}</b></div>",
                unsafe_allow_html=True,
            )

        if rec.recommended:
            st.success(f"Recommended: {rec.recommended.coa.coa_id}")
            roe_s = rec.recommended.coa.roe_status
            roe_c = ROE_BADGE_COLORS.get(roe_s, "#999")
            st.markdown(
                f"<div style='border-left:3px solid {roe_c}; padding-left:8px; margin:4px 0;'>"
                f"<small><b>ROE:</b> {roe_s.replace('_', ' ').title()}<br>"
                f"<b>Reason:</b> {rec.recommended.coa.roe_reason or 'No constraints triggered'}</small></div>",
                unsafe_allow_html=True,
            )
            st.caption(
                f"Feasibility {rec.recommended.coa.feasibility_score:.0%} with current assets"
            )
        if go is None:
            st.warning("Plotly is not installed. Advanced charts are shown as tables/basic charts.")
        if st_folium is None:
            st.warning("streamlit-folium is not installed. The map will render as static HTML.")
        st.caption(f"Source: {data_source}")
        st.divider()
        st.markdown("**Safety Boundary**")
        st.caption("Advisory only. Synthetic data. No command execution.")

    # ---- Tabs ----
    tab_overview, tab_map, tab_timeline, tab_threat, tab_coa, tab_sim, tab_briefing, tab_live = st.tabs([
        "Overview", "Map", "Timeline", "Threat Assessment",
        "COA Ranking", "Simulation", "Commander Briefing", "Live Scenario",
    ])

    # ---- Overview ----
    with tab_overview:
        st.header("Scenario Overview")
        st.markdown(f"**{scenario.name}**")
        st.markdown(scenario.description)
        st.markdown(f"**Timeframe:** {scenario.timeframe}")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Events", len(events))
        col2.metric("Entities", len(set(e.entity_id for e in events)))
        col3.metric("Critical Infrastructure", len(scenario.critical_infrastructure))
        col4.metric("COAs Generated", len(scored))

        # Asset summary
        total_deployed = sum(1 for v in asset_inventory.values() if v > 0)
        st.subheader(f"Deployed Forces ({total_deployed} asset types available)")
        asset_rows = []
        for state in asset_states:
            asset_rows.append({
                "Asset": state.display_name or state.asset_id,
                "Qty": state.quantity_available,
                "Status": state.status,
                "Base": state.location_label or state.home_base or "Unknown",
                "Coverage km": state.coverage_radius_km,
                "Transit kts": state.transit_speed_kts,
                "ETA min": state.response_eta_min,
                "On station h": state.on_station_hours,
            })
        st.dataframe(pd.DataFrame(asset_rows), use_container_width=True, hide_index=True)

        st.divider()
        type_counts: dict[str, int] = {}
        for e in events:
            label = e.event_type.value
            type_counts[label] = type_counts.get(label, 0) + 1
        st.subheader("Event Type Distribution")
        type_df = pd.DataFrame([{"Event Type": k, "Count": v} for k, v in sorted(type_counts.items())])
        st.bar_chart(type_df, x="Event Type", y="Count")
        st.info("All data is synthetic and for prototype demonstration only.")

    # ---- Map ----
    with tab_map:
        st.header(f"Operational Map — {scenario.name}")
        m = build_map(events, scenario, asset_inventory, asset_states)
        if st_folium is not None:
            st_folium(m, width=1100, height=600)
        else:
            st.components.v1.html(m._repr_html_(), height=620, scrolling=False)

        legend_cols = st.columns(6)
        legend_items = [
            ("#d73027", "Hostile"), ("#4575b4", "Allied/Asset"),
            ("#fdae61", "UAV"), ("#7b3294", "Convoy"),
            ("#1a9850", "Infrastructure"), ("#cadetblue", "ISR Coverage"),
        ]
        for col, (color, label) in zip(legend_cols, legend_items):
            col.markdown(
                f"<span style='color:{color}; font-size: 1.4rem;'>■</span> <b>{label}</b>",
                unsafe_allow_html=True,
            )

    # ---- Timeline ----
    with tab_timeline:
        st.header("Event Timeline")
        rows = []
        for e in events:
            rows.append({
                "Time": e.timestamp.strftime("%H:%MZ"),
                "Event Type": e.event_type.value,
                "Entity": e.entity_id,
                "Confidence": e.confidence,
                "Description": e.description[:90],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        if go is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[e.timestamp for e in events],
                y=[e.entity_id for e in events],
                mode="markers",
                marker=dict(
                    size=10,
                    color=[_threat_color(a.anomaly_level.value) for a in anomalies],
                    symbol="diamond",
                ),
                text=[f"{e.event_type.value}<br>{e.description[:60]}" for e in events],
                hoverinfo="text",
            ))
            fig.update_layout(
                height=500, xaxis_title="Time (UTC)", yaxis_title="Entity",
                margin=dict(l=20, r=20, t=30, b=30), template="plotly_white",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            timeline_df = pd.DataFrame(rows)
            st.line_chart(timeline_df.groupby("Time").size())

    # ---- Threat Assessment ----
    with tab_threat:
        st.header("Threat Assessment")
        st.caption("Estimated probabilities from explainable rule-based analysis. Not certainty.")

        if threats:
            threat_rows = []
            for t in threats:
                threat_rows.append({
                    "Entity": t.entity_id,
                    "Est. Probability": f"{t.threat_probability:.1%}",
                    "Level": t.threat_level.value,
                    "Confidence": f"{t.confidence:.1%}",
                    "Main Drivers": "; ".join(t.main_drivers),
                })
            threat_df = pd.DataFrame(threat_rows)

            def _hl(val):
                return f"background-color: {_threat_color(val)}; color: white; font-weight: bold"

            st.dataframe(threat_df.style.map(_hl, subset=["Level"]), use_container_width=True, hide_index=True)

        if rec.threat_narrative:
            st.subheader("Threat Narrative (LLM-Enriched)")
            st.markdown(rec.threat_narrative)

        st.subheader("Anomaly Indicators")
        high_anomalies = [a for a in anomalies if a.anomaly_score >= 40]
        if high_anomalies:
            anom_rows = []
            for a in sorted(high_anomalies, key=lambda x: x.anomaly_score, reverse=True)[:10]:
                anom_rows.append({
                    "Event": a.event_id, "Entity": a.entity_id,
                    "Score": a.anomaly_score, "Level": a.anomaly_level.value,
                    "Indicators": "; ".join(a.explanations[:3]),
                })
            st.dataframe(pd.DataFrame(anom_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No elevated anomaly indicators.")

    # ---- COA Ranking ----
    with tab_coa:
        st.header("COA Ranking — Advisory Courses of Action")
        st.caption("All COAs are advisory. No autonomous execution.")

        # Scenario awareness bar
        st.subheader("Scenario Awareness")
        sa_cols = st.columns(5)
        sa_cols[0].metric("Scenario", scenario.name[:30])
        sa_cols[1].metric("Seed", st.session_state.scenario_seed)
        threat_level = threats[0].threat_level.value if threats else "LOW"
        tl_color = _threat_color(threat_level)
        sa_cols[2].markdown(
            f"<div style='text-align:center;'><b>Threat Level</b><br>"
            f"<span style='font-size:1.4em; color:{tl_color}; font-weight:bold;'>{threat_level}</span></div>",
            unsafe_allow_html=True,
        )
        sa_cols[3].metric("Active Stimuli", len([s for s in scored if s.coa.roe_constraints_triggered]))
        sa_cols[4].metric("ROE Constraints", sum(len(s.coa.roe_constraints_triggered) for s in scored))

        st.divider()

        # Recommended COA with ROE details
        if rec.recommended:
            rcoe = rec.recommended.coa
            roe_status = rcoe.roe_status
            roe_color = ROE_BADGE_COLORS.get(roe_status, "#999")

            st.subheader("Recommended COA")
            st.markdown(
                f"<div style='border:2px solid {roe_color}; border-radius:8px; padding:12px; margin-bottom:8px;'>"
                f"<h4 style='margin:0; color:#1a1a1a;'>{rcoe.title}</h4>"
                f"<table style='width:100%; margin-top:8px;'>"
                f"<tr><td style='width:30%; color:#666;'>Score</td><td><b>{rec.recommended.total_score:.1f}</b>/100</td></tr>"
                f"<tr><td style='color:#666;'>Success Prob.</td><td>{rec.recommended.simulation.success_probability:.0%}</td></tr>"
                f"<tr><td style='color:#666;'>Feasibility</td><td>{rcoe.feasibility_score:.0%}</td></tr>"
                f"<tr><td style='color:#666;'>ROE Status</td>"
                f"<td><span style='background:{roe_color}; color:white; padding:2px 8px; "
                f"border-radius:3px; font-weight:bold;'>{roe_status.replace('_', ' ').title()}</span></td></tr>"
                f"<tr><td style='color:#666;'>ROE Reason</td><td>{rcoe.roe_reason or 'No constraints triggered'}</td></tr>"
                f"</table>"
                f"</div>",
                unsafe_allow_html=True,
            )
            if rcoe.roe_constraints_triggered:
                st.caption(f"Constraints: {', '.join(rcoe.roe_constraints_triggered)}")
            st.markdown(f"**Rationale:** {rec.rationale}")

        # Key change banner
        rejected = [s for s in scored if s.coa.roe_status == "rejected"]
        restricted = [s for s in scored if s.coa.roe_status == "restricted"]
        if rejected:
            st.error(f"**{len(rejected)} COA(s) rejected by ROE:** {', '.join(s.coa.title for s in rejected)}")
        if restricted:
            st.warning(f"**{len(restricted)} COA(s) restricted by ROE:** {', '.join(s.coa.title for s in restricted)}")

        if rec.recommended_package:
            st.subheader("Recommended Coordinated Package")
            st.markdown(
                f"**{rec.recommended_package.package_id}** "
                f"(score {rec.recommended_package.total_score:.1f}/100, "
                f"feasibility {rec.recommended_package.feasibility_score:.0%})"
            )
            if rec.recommended_package.plan:
                st.caption(rec.recommended_package.plan.summary)
                task_rows = []
                for task in rec.recommended_package.plan.tasks:
                    task_rows.append({
                        "Task": task.title,
                        "Type": task.task_type,
                        "Start +min": task.start_offset_min,
                        "Duration min": task.duration_min,
                        "Assets": ", ".join(task.assigned_assets) or "None",
                        "Targets": ", ".join(task.target_entities) or "None",
                    })
                st.dataframe(pd.DataFrame(task_rows), use_container_width=True, hide_index=True)

        st.subheader("Scored COAs")
        if go is not None:
            fig_coa = go.Figure()
            bar_colors = [ROE_BADGE_COLORS.get(s.coa.roe_status, "#4682b4") for s in scored]
            fig_coa.add_trace(go.Bar(
                x=[s.coa.title for s in scored],
                y=[s.total_score for s in scored],
                marker_color=bar_colors,
                text=[f"{s.total_score:.1f}" for s in scored],
                textposition="outside",
            ))
            fig_coa.update_layout(
                yaxis=dict(range=[0, 100], title="Score"), xaxis_title="Course of Action",
                height=400, template="plotly_white", margin=dict(l=20, r=20, t=30, b=100),
            )
            st.plotly_chart(fig_coa, use_container_width=True)
        else:
            st.bar_chart(pd.DataFrame({
                "COA": [s.coa.title for s in scored],
                "Score": [s.total_score for s in scored],
            }).set_index("COA"))

        coa_rows = []
        for s in scored:
            roe_s = s.coa.roe_status
            roe_c = ROE_BADGE_COLORS.get(roe_s, "#999")
            roe_label = roe_s.replace("_", " ").title()
            coa_rows.append({
                "Rank": s.rank, "COA": s.coa.title, "Score": s.total_score,
                "Feasibility": f"{s.coa.feasibility_score:.0%}",
                "Success": f"{s.simulation.success_probability:.1%}",
                "Escalation": f"{s.simulation.escalation_probability:.1%}",
                "ROE": roe_label,
                "ROE Reason": s.coa.roe_reason[:80] if s.coa.roe_reason else "—",
                "Missing": ", ".join(s.coa.missing_assets) or "None",
                "Trade-offs": s.tradeoff_explanation,
            })
        coa_df = pd.DataFrame(coa_rows)

        def _roe_style(val):
            color = ROE_BADGE_COLORS.get(val.lower().replace(" ", "_"), "#999")
            return f"background-color: {color}; color: white; font-weight: bold"

        st.dataframe(
            coa_df.style.map(_roe_style, subset=["ROE"]),
            use_container_width=True, hide_index=True,
        )
        if rec.edge_cases:
            st.info(f"**When alternatives may be preferred:** {rec.edge_cases}")

    # ---- Simulation ----
    with tab_sim:
        st.header("Monte Carlo Simulation Results")
        st.caption(
            f"Based on {sims[0].simulation_runs if sims else 0} runs per COA. Not predictions."
        )
        if sims:
            sim_labels = [s.coa_id for s in sims]
            if go is not None:
                fig_sim = go.Figure()
                fig_sim.add_trace(go.Bar(name="Success", x=sim_labels,
                                         y=[s.success_probability for s in sims], marker_color="#2e8b57"))
                fig_sim.add_trace(go.Bar(name="Escalation", x=sim_labels,
                                         y=[s.escalation_probability for s in sims], marker_color="#ff6600"))
                fig_sim.add_trace(go.Bar(name="Cable Risk", x=sim_labels,
                                         y=[s.risk_to_second_cable for s in sims], marker_color="#cc0000"))
                fig_sim.add_trace(go.Bar(name="Missed Det.", x=sim_labels,
                                         y=[s.missed_detection_probability for s in sims], marker_color="#999999"))
                fig_sim.update_layout(
                    barmode="group",
                    yaxis=dict(range=[0, 1], tickformat=".0%", title="Probability"),
                    xaxis_title="COA", height=450, template="plotly_white",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig_sim, use_container_width=True)
            else:
                st.bar_chart(pd.DataFrame({
                    "Success": [s.success_probability for s in sims],
                    "Escalation": [s.escalation_probability for s in sims],
                    "Cable Risk": [s.risk_to_second_cable for s in sims],
                    "Missed Detection": [s.missed_detection_probability for s in sims],
                }, index=sim_labels))
            sim_rows = []
            for s in sims:
                ci = s.confidence_interval
                sim_rows.append({
                    "COA": s.coa_id, "Success": f"{s.success_probability:.1%}",
                    "Time (min)": s.expected_time_to_effect,
                    "Cable Risk": f"{s.risk_to_second_cable:.1%}",
                    "Escalation": f"{s.escalation_probability:.1%}",
                    "95% CI": f"[{ci[0]:.1%}, {ci[1]:.1%}]",
                })
            st.dataframe(pd.DataFrame(sim_rows), use_container_width=True, hide_index=True)

    # ---- Commander Briefing ----
    with tab_briefing:
        st.header("Commander Decision-Support Briefing")
        st.caption("Advisory product for human decision-maker review. Not an execution order.")

        st.subheader("Situation")
        st.markdown(briefing.situation)

        st.subheader("Key Indicators")
        for ind in briefing.key_indicators:
            st.markdown(f"- {ind}")

        st.subheader("Assessment")
        st.markdown(briefing.assessment)
        if briefing.enriched_assessment:
            st.markdown("**Enriched Analysis (LLM):**")
            st.info(briefing.enriched_assessment)

        if briefing.entity_risk_narratives:
            st.subheader("Entity Risk Narratives (LLM)")
            for eid, narrative in briefing.entity_risk_narratives.items():
                st.markdown(f"**{eid}:** {narrative}")

        st.subheader("COAs Considered")
        for coa_name in briefing.coas_considered:
            st.markdown(f"- {coa_name}")

        st.subheader("Recommended COA")
        st.success(briefing.recommended_coa)

        st.subheader("Risks")
        for risk in briefing.risks:
            st.markdown(f"- {risk}")

        st.metric("Assessment Confidence", briefing.confidence)

        st.subheader("Assumptions")
        for assumption in briefing.assumptions:
            st.markdown(f"- {assumption}")

        st.divider()
        st.subheader("Export Briefing")
        from app.engine.export import export_briefing_json, export_briefing_pdf
        col_json, col_pdf = st.columns(2)
        with col_json:
            st.download_button(
                "Download JSON", export_briefing_json(briefing),
                file_name=f"briefing_{selected_scenario}.json", mime="application/json",
            )
        with col_pdf:
            st.download_button(
                "Download PDF", export_briefing_pdf(briefing),
                file_name=f"briefing_{selected_scenario}.pdf", mime="application/pdf",
            )

        st.divider()
        st.caption("COA Engine — Synthetic decision-support prototype. All outputs are advisory.")

    # ---- Live Scenario ----
    with tab_live:
        st.header("Live Scenario Timeline")
        st.caption("Stimuli timeline from the scenario generator. Shows upcoming, active, and fired events.")

        try:
            gen = ScenarioGenerator(
                seed=st.session_state.scenario_seed,
                timing_jitter=st.session_state.scenario_timing_jitter,
                position_jitter=st.session_state.scenario_position_jitter,
            )
            template = gen.generate(selected_scenario)
        except ValueError:
            st.error("Cannot load scenario template for live view.")
            st.stop()

        meta = template.metadata
        st.markdown(f"**{meta['display_name']}** — {meta['description']}")

        # Try to get live engine state
        live_tick = 0
        live_mode = "—"
        live_seed = st.session_state.scenario_seed
        fired_stimuli = []
        try:
            from app.engine.contact_engine import get_contact_engine
            engine = get_contact_engine()
            sim = engine._sim
            if sim is not None and sim.scenario_id == selected_scenario:
                live_tick = sim.tick
                live_mode = engine.mode.value
                fired_stimuli = sim.fired_stimuli_list
        except Exception:
            pass

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Current Tick", live_tick)
        col_m2.metric("Mode", live_mode)
        col_m3.metric("Seed", live_seed)
        col_m4.metric("Stimuli Fired", len(fired_stimuli))

        st.divider()

        # Stimulus Action severity/confidence mapping
        SEVERITY_MAP = {
            "cable_severance": ("CRITICAL", "#ff0000"),
            "jamming": ("HIGH", "#ff6600"),
            "course_change": ("MEDIUM", "#ffcc00"),
            "slow_near_cable": ("HIGH", "#ff6600"),
            "suspicious_maneuver": ("MEDIUM", "#ffcc00"),
            "surface": ("MEDIUM", "#ffcc00"),
            "reposition": ("LOW", "#33cc33"),
            "approach_point": ("MEDIUM", "#ffcc00"),
            "speed_burst": ("LOW", "#33cc33"),
            "ais_off": ("HIGH", "#ff6600"),
            "attack_run": ("CRITICAL", "#ff0000"),
        }

        # Build complete timeline
        all_stimuli = []
        fired_ticks = {f["tick"] for f in fired_stimuli}

        for s in template.stimuli:
            is_fired = s.tick <= live_tick and s.tick in fired_ticks if fired_stimuli else s.tick <= live_tick
            is_active = s.tick == live_tick
            severity, color = SEVERITY_MAP.get(s.action, ("LOW", "#999999"))

            status = "upcoming"
            if is_active:
                status = "active"
            elif is_fired:
                status = "fired"

            all_stimuli.append({
                "Tick": s.tick,
                "Action": s.action,
                "Entity": s.entity or "—",
                "Severity": severity,
                "Status": status,
                "Lat": f"{s.lat:.2f}" if s.lat is not None else "—",
                "Lon": f"{s.lon:.2f}" if s.lon is not None else "—",
                "Heading": f"{s.new_heading:.0f}" if s.new_heading is not None else "—",
                "Speed": f"{s.new_speed:.1f}" if s.new_speed is not None else "—",
                "Radius (nm)": f"{s.radius_nm:.0f}" if s.radius_nm is not None else "—",
            })

        # Status indicators
        st.subheader("Event Alerts")
        active_events = [s for s in all_stimuli if s["Status"] == "active"]
        fired_events = [s for s in all_stimuli if s["Status"] == "fired"]
        upcoming_events = [s for s in all_stimuli if s["Status"] == "upcoming"]

        # Demo clarity: show alerts for significant events
        for evt in active_events:
            severity = evt["Severity"]
            action = evt["Action"]
            entity = evt["Entity"]
            msg = f"**ACTIVE** — {action.replace('_', ' ').title()}"
            if entity != "—":
                msg += f" | Entity: {entity}"
            if severity == "CRITICAL":
                st.error(msg)
            elif severity == "HIGH":
                st.warning(msg)
            else:
                st.info(msg)

        if not active_events and not fired_events and live_tick == 0:
            st.info("No stimuli active yet. Start the scenario engine to see live events.")

        # Show recently fired events with indicators
        if fired_events:
            st.subheader("Recently Fired")
            for evt in fired_events[-5:]:
                severity = evt["Severity"]
                label = f"Tick {evt['Tick']}: {evt['Action'].replace('_', ' ').title()}"
                if evt["Entity"] != "—":
                    label += f" — {evt['Entity']}"
                if severity == "CRITICAL":
                    st.error(label)
                elif severity == "HIGH":
                    st.warning(label)
                else:
                    st.success(label)

        st.divider()

        # Full timeline table
        st.subheader("Full Stimuli Timeline")
        if all_stimuli:
            timeline_df = pd.DataFrame(all_stimuli)

            def _status_style(val):
                if val == "active":
                    return "background-color: #ff6600; color: white; font-weight: bold"
                if val == "fired":
                    return "background-color: #33cc33; color: white"
                return "background-color: #e0e0e0; color: #666"

            def _severity_style(val):
                colors = {"CRITICAL": "#ff0000", "HIGH": "#ff6600", "MEDIUM": "#ffcc00", "LOW": "#33cc33"}
                c = colors.get(val, "#999")
                return f"background-color: {c}; color: white; font-weight: bold"

            styled = timeline_df.style.map(_status_style, subset=["Status"]).map(_severity_style, subset=["Severity"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

        # Demo clarity: Key changes summary
        st.divider()
        st.subheader("Key Change Indicators")

        if live_tick > 0 and fired_events:
            has_cable = any(e["Action"] == "cable_severance" for e in fired_events)
            has_jamming = any(e["Action"] == "jamming" for e in fired_events)
            has_course = any(e["Action"] in ("course_change", "suspicious_maneuver") for e in fired_events)
            has_surface = any(e["Action"] == "surface" for e in fired_events)

            indicators = []
            if has_cable:
                indicators.append(("CABLE SEVERANCE DETECTED", "#ff0000"))
            if has_jamming:
                indicators.append(("JAMMING ACTIVE", "#ff6600"))
            if has_course:
                indicators.append(("VESSEL COURSE CHANGES", "#ffcc00"))
            if has_surface:
                indicators.append(("SUBMARINE SURFACED", "#ffcc00"))

            if indicators:
                ind_cols = st.columns(min(len(indicators), 4))
                for col, (text, color) in zip(ind_cols, indicators):
                    col.markdown(
                        f"<div style='background:{color}; color:white; padding:8px; "
                        f"border-radius:4px; text-align:center; font-weight:bold; font-size:0.85em;'>"
                        f"{text}</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No critical events triggered yet.")
        else:
            st.info("Start the engine to see key change indicators.")

        # Current threat level / COA recommendation
        if live_tick > 0:
            st.divider()
            tc1, tc2 = st.columns(2)
            try:
                store_state = st.session_state.get("_last_engine_state")
                if store_state:
                    tl = store_state.get("current_threat_level", "LOW")
                    tl_colors = {"CRITICAL": "#ff0000", "HIGH": "#ff6600", "MEDIUM": "#ffcc00", "LOW": "#33cc33"}
                    tc1.markdown(
                        f"<div style='background:{tl_colors.get(tl, '#999')}; color:white; "
                        f"padding:12px; border-radius:4px; text-align:center;'>"
                        f"<b>THREAT LEVEL</b><br><span style='font-size:1.4em'>{tl}</span></div>",
                        unsafe_allow_html=True,
                    )
                    coa_id = store_state.get("recommended_coa_id", "—")
                    tc2.markdown(
                        f"<div style='background:#4682b4; color:white; padding:12px; "
                        f"border-radius:4px; text-align:center;'>"
                        f"<b>RECOMMENDED COA</b><br><span style='font-size:1.2em'>{coa_id}</span></div>",
                        unsafe_allow_html=True,
                    )
            except Exception:
                pass

    # ---- Operator Query ----
    st.divider()
    st.subheader("Ask the System")
    st.caption("Ask natural-language questions about the current operational state. Explanation-only, no actions taken.")

    suggested_questions = [
        "Why is the current COA recommended?",
        "What is the current situation summary?",
        "What happens if the cable is severed?",
        "What if we choose the top COA?",
        "How would threat evolve in the next 30 minutes?",
        "What COAs require authorization and why?",
    ]
    sq_cols = st.columns(3)
    for i, sq in enumerate(suggested_questions):
        if sq_cols[i % 3].button(sq, key=f"sq_{i}"):
            st.session_state["_query_input"] = sq

    query_input = st.text_input(
        "Question",
        value=st.session_state.get("_query_input", ""),
        key="query_text_input",
    )
    if st.button("Ask", type="primary", key="query_ask_btn") and query_input.strip():
        with st.spinner("Analyzing..."):
            try:
                from app.engine.query_engine import answer_question
                result = answer_question(query_input.strip())
                st.markdown(result["answer"])
                st.caption(
                    f"Sources: {', '.join(result['sources_used'])} | "
                    f"LLM used: {'Yes' if result['llm_used'] else 'No (fallback)'}"
                )
                # Show structured forecast if present
                forecast = result.get("forecast")
                if forecast:
                    trend = forecast.get("expected_threat_trend", "stable")
                    trend_color = {"increase": "#ff6600", "decrease": "#33cc33"}.get(trend, "#999")
                    fc_cols = st.columns(4)
                    fc_cols[0].metric("Threat Start", forecast.get("threat_level_start", "?"))
                    fc_cols[1].metric("Threat End", forecast.get("threat_level_end", "?"))
                    fc_cols[2].markdown(
                        f"<div style='text-align:center;'><b>Trend</b><br>"
                        f"<span style='color:{trend_color}; font-weight:bold;'>{trend.title()}</span></div>",
                        unsafe_allow_html=True,
                    )
                    fc_cols[3].metric("Confidence", forecast.get("confidence", "?").title())
                    risks = forecast.get("key_risks", [])
                    if risks:
                        st.caption("**Key risks:** " + " | ".join(risks))
            except Exception as e:
                st.error(f"Query failed: {e}")


if __name__ == "__main__":
    main()
