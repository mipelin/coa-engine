from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.core.constants import EntityType, EventType
from app.core.schemas import (
    AnomalyResult,
    Briefing,
    CourseOfAction,
    OperationalEvent,
    Recommendation,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from app.engine.anomaly_detection import detect_anomalies
from app.engine.coa_generation import generate_coas
from app.engine.event_ingestion import load_scenario, list_scenarios
from app.engine.explanation import generate_briefing
from app.engine.feature_engineering import compute_features
from app.engine.llm_coa_generation import generate_coas_with_llm
from app.engine.llm_narrative import enrich_briefing, enrich_threat_narrative, entity_risk_narrative
from app.engine.recommendation import recommend
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

    coas = generate_coas_with_llm(events, threats, asset_inventory)
    sims = run_simulations(coas, events, threats)
    scored = score_coas(coas, sims)
    rec = recommend(scored)

    return {
        "coas": coas, "sims": sims, "scored": scored,
        "recommendation": rec, "asset_inventory": asset_inventory,
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
        "asset_inventory": asset_inventory, "source": "engine+llm",
    }


# ---------------------------------------------------------------------------
# Color / icon helpers
# ---------------------------------------------------------------------------

THREAT_LEVEL_COLORS = {
    "CRITICAL": "#ff0000", "HIGH": "#ff6600", "MEDIUM": "#ffcc00", "LOW": "#33cc33",
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

def build_map(events, scenario, asset_inventory: dict[str, int]) -> Any:
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

    # Layer 1: Critical infrastructure
    for infra in scenario.critical_infrastructure:
        color = "darkgreen" if infra.type in ("subsea_cable", "pipeline") else "darkblue"
        folium.Marker(
            location=[infra.lat, infra.lon],
            popup=f"<b>{infra.name}</b><br>Type: {infra.type}",
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
    for asset_key, count in asset_inventory.items():
        if count <= 0:
            continue
        if asset_key not in ASSET_OFFSETS:
            continue
        label = ASSET_LABELS.get(asset_key, asset_key)
        icon_color, icon_name = ASSET_ICON_MAP.get(asset_key, ("white", "info-sign"))
        offset_lat, offset_lon = ASSET_OFFSETS[asset_key]

        # Position asset offset from the center
        a_lat = avg_lat + offset_lat * 1.5
        a_lon = avg_lon + offset_lon * 1.5

        popup = f"<b>{label}</b><br>Qty: {count}<br>Status: Available"
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
        count = asset_inventory.get(asset_key, 0)
        if count <= 0 or asset_key not in ASSET_OFFSETS:
            continue
        offset_lat, offset_lon = ASSET_OFFSETS[asset_key]
        a_lat = avg_lat + offset_lat * 1.5
        a_lon = avg_lon + offset_lon * 1.5
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
    import plotly.graph_objects as go
    from streamlit_folium import st_folium

    st.set_page_config(page_title="COA Engine", layout="wide", page_icon=":shield:")

    st.title("COA Engine — Decision Superiority Module")
    st.caption(
        "Synthetic decision-support prototype. No autonomous targeting or command execution. "
        "All data is simulated."
    )

    if "asset_inventory" not in st.session_state:
        st.session_state.asset_inventory = dict(DEFAULT_ASSET_INVENTORY)

    # ---- Sidebar ----
    with st.sidebar:
        st.header("Scenario & Assets")
        st.caption("Select scenario and adjust available forces.")

        scenario_list = list_scenarios()
        scenario_options = {s["scenario_id"]: s["name"] for s in scenario_list}
        if not scenario_options:
            scenario_options = {"baltic_hybrid_001": "Baltic Sea Hybrid Threat Scenario"}
        selected_scenario = st.selectbox(
            "Scenario",
            options=list(scenario_options.keys()),
            format_func=lambda x: scenario_options[x],
            index=0,
        )

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
    data_source = data.get("source", "engine")

    with st.sidebar:
        st.divider()
        st.metric("Events", len(events))
        st.metric("Threat Entities", len(threats))
        st.metric("COAs", len(scored))
        if rec.recommended:
            st.success(f"Recommended: {rec.recommended.coa.coa_id}")
            st.caption(
                f"Feasibility {rec.recommended.coa.feasibility_score:.0%} with current assets"
            )
        st.caption(f"Source: {data_source}")
        st.divider()
        st.markdown("**Safety Boundary**")
        st.caption("Advisory only. Synthetic data. No command execution.")

    # ---- Tabs ----
    tab_overview, tab_map, tab_timeline, tab_threat, tab_coa, tab_sim, tab_briefing = st.tabs([
        "Overview", "Map", "Timeline", "Threat Assessment",
        "COA Ranking", "Simulation", "Commander Briefing",
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
        for group_name, assets in ASSET_GROUPS.items():
            for asset_key, (label, _) in assets.items():
                count = asset_inventory.get(asset_key, 0)
                status = "Available" if count > 0 else "Unavailable"
                asset_rows.append({"Group": group_name, "Asset": label, "Qty": count, "Status": status})
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
        m = build_map(events, scenario, asset_inventory)
        st_folium(m, width=1100, height=600)

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

        if rec.recommended:
            st.success(
                f"**Recommended:** {rec.recommended.coa.title} "
                f"(Score: {rec.recommended.total_score:.1f}/100, "
                f"Success: {rec.recommended.simulation.success_probability:.0%}, "
                f"Feasibility: {rec.recommended.coa.feasibility_score:.0%})"
            )
            st.markdown(f"**Rationale:** {rec.rationale}")

        st.subheader("Scored COAs")
        fig_coa = go.Figure()
        fig_coa.add_trace(go.Bar(
            x=[s.coa.title for s in scored],
            y=[s.total_score for s in scored],
            marker_color=["#2e8b57" if s.rank == 1 else "#4682b4" for s in scored],
            text=[f"{s.total_score:.1f}" for s in scored],
            textposition="outside",
        ))
        fig_coa.update_layout(
            yaxis=dict(range=[0, 100], title="Score"), xaxis_title="Course of Action",
            height=400, template="plotly_white", margin=dict(l=20, r=20, t=30, b=100),
        )
        st.plotly_chart(fig_coa, use_container_width=True)

        coa_rows = []
        for s in scored:
            coa_rows.append({
                "Rank": s.rank, "COA": s.coa.title, "Score": s.total_score,
                "Feasibility": f"{s.coa.feasibility_score:.0%}",
                "Success": f"{s.simulation.success_probability:.1%}",
                "Escalation": f"{s.simulation.escalation_probability:.1%}",
                "Missing": ", ".join(s.coa.missing_assets) or "None",
                "Trade-offs": s.tradeoff_explanation,
            })
        st.dataframe(pd.DataFrame(coa_rows), use_container_width=True, hide_index=True)
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


if __name__ == "__main__":
    main()
