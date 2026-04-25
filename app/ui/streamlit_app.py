from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.core.constants import EntityType, EventType
from app.engine.anomaly_detection import detect_anomalies
from app.engine.coa_generation import generate_coas
from app.engine.event_ingestion import load_sample_scenario, load_scenario_events
from app.engine.explanation import generate_briefing
from app.engine.feature_engineering import compute_features
from app.engine.recommendation import recommend
from app.engine.scoring import score_coas
from app.engine.simulation import run_simulations
from app.engine.threat_assessment import assess_threats

DEFAULT_ASSET_INVENTORY = {
    "isr_uav": 2,
    "satellite_observation_request": 1,
    "sigint_team": 1,
    "maritime_patrol_asset": 1,
    "coast_guard_liaison": 1,
    "cable_operator_liaison": 1,
    "airspace_coordinator": 1,
    "atc_liaison": 1,
    "sensor_data_feed": 1,
    "border_patrol_liaison": 1,
    "intelligence_team": 1,
    "surveillance_asset": 1,
    "standard_watch_team": 1,
}

ASSET_LABELS = {
    "isr_uav": "ISR UAV",
    "satellite_observation_request": "Satellite observation",
    "sigint_team": "SIGINT team",
    "maritime_patrol_asset": "Maritime patrol asset",
    "coast_guard_liaison": "Coast guard liaison",
    "cable_operator_liaison": "Cable operator liaison",
    "airspace_coordinator": "Airspace coordinator",
    "atc_liaison": "ATC liaison",
    "sensor_data_feed": "Sensor data feed",
    "border_patrol_liaison": "Border patrol liaison",
    "intelligence_team": "Intelligence team",
    "surveillance_asset": "Surveillance asset",
    "standard_watch_team": "Standard watch team",
}


# ---------------------------------------------------------------------------
# Data preparation — extracted for testability
# ---------------------------------------------------------------------------

@st.cache_data
def build_dashboard_data(
    asset_inventory_items: tuple[tuple[str, int], ...] | None = None,
) -> dict[str, Any]:
    """Run the full analysis pipeline and return all results."""
    asset_inventory = dict(asset_inventory_items or tuple(DEFAULT_ASSET_INVENTORY.items()))
    scenario = load_sample_scenario()
    events = load_scenario_events()
    features = compute_features(events)
    anomalies = detect_anomalies(events, features)
    threats = assess_threats(events, features, anomalies)
    coas = generate_coas(events, threats, asset_inventory)
    sims = run_simulations(coas, events, threats)
    scored = score_coas(coas, sims)
    rec = recommend(scored)
    briefing = generate_briefing(events, anomalies, threats, scored, rec)
    return {
        "scenario": scenario,
        "events": events,
        "features": features,
        "anomalies": anomalies,
        "threats": threats,
        "coas": coas,
        "sims": sims,
        "scored": scored,
        "recommendation": rec,
        "briefing": briefing,
        "asset_inventory": asset_inventory,
    }


# ---------------------------------------------------------------------------
# Color / icon helpers
# ---------------------------------------------------------------------------

ENTITY_COLORS = {
    EntityType.SUSPICIOUS_VESSEL: "red",
    EntityType.ALLIED_VESSEL: "blue",
    EntityType.UAV: "orange",
    EntityType.CONVOY: "purple",
    EntityType.SUBSEA_CABLE: "darkgreen",
    EntityType.ISR_ASSET: "cadetblue",
    EntityType.AIRPORT: "gray",
}

EVENT_ICONS = {
    EventType.CABLE_SEVERANCE: "bolt",
    EventType.UAV_DETECTION: "plane",
    EventType.JAMMING_DETECTED: "signal",
    EventType.CONVOY_SIGHTING: "truck",
    EventType.VESSEL_COURSE_CHANGE: "random",
}

THREAT_LEVEL_COLORS = {
    "CRITICAL": "#ff0000",
    "HIGH": "#ff6600",
    "MEDIUM": "#ffcc00",
    "LOW": "#33cc33",
}


def _marker_color(event_type: EventType, entity_type: EntityType) -> str:
    if event_type == EventType.CABLE_SEVERANCE:
        return "darkred"
    if event_type == EventType.JAMMING_DETECTED:
        return "darkpurple"
    return ENTITY_COLORS.get(entity_type, "gray")


def _threat_color(level: str) -> str:
    return THREAT_LEVEL_COLORS.get(level, "#999999")


# ---------------------------------------------------------------------------
# Map builder
# ---------------------------------------------------------------------------

def build_map(events, scenario) -> Any:
    import folium

    m = folium.Map(location=[57.5, 19.5], zoom_start=6, tiles="CartoDB positron")

    # Critical infrastructure
    for infra in scenario.critical_infrastructure:
        color = "darkgreen" if infra.type == "subsea_cable" else "darkblue"
        folium.Marker(
            location=[infra.lat, infra.lon],
            popup=f"<b>{infra.name}</b><br>Type: {infra.type}",
            icon=folium.Icon(color=color, icon="star"),
        ).add_to(m)

    # Events
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

    # Jamming circles
    for ev in events:
        if ev.event_type == EventType.JAMMING_DETECTED:
            radius_km = ev.attributes.get("radius_nm", 20) * 1.852
            folium.Circle(
                location=[ev.lat, ev.lon],
                radius=radius_km * 1000,
                color="purple",
                fill=True,
                fill_opacity=0.08,
                popup=f"Jamming radius: {ev.attributes.get('radius_nm', 20)} nm",
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

    with st.sidebar:
        st.header("Scenario Controls")
        st.caption("Local synthetic scenario only. No live feeds.")
        st.selectbox("Scenario", ["Baltic Sea Hybrid Threat Scenario"], index=0, disabled=True)
        st.markdown("**Assets For Simulation**")
        with st.expander("Adjust available assets", expanded=True):
            for asset_key, default_value in DEFAULT_ASSET_INVENTORY.items():
                st.session_state.asset_inventory[asset_key] = st.number_input(
                    ASSET_LABELS[asset_key],
                    min_value=0,
                    max_value=5,
                    value=int(st.session_state.asset_inventory.get(asset_key, default_value)),
                    step=1,
                    key=f"asset_{asset_key}",
                )

        if st.button("Reset default assets"):
            st.session_state.asset_inventory = dict(DEFAULT_ASSET_INVENTORY)
            build_dashboard_data.clear()
            st.rerun()
        if st.button("Refresh analysis cache"):
            build_dashboard_data.clear()
            st.rerun()

    asset_inventory_items = tuple(sorted(
        (asset, int(count)) for asset, count in st.session_state.asset_inventory.items()
    ))
    data = build_dashboard_data(asset_inventory_items)
    scenario = data["scenario"]
    events = data["events"]
    anomalies = data["anomalies"]
    threats = data["threats"]
    scored = data["scored"]
    rec = data["recommendation"]
    briefing = data["briefing"]
    sims = data["sims"]
    asset_inventory = data["asset_inventory"]

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

        st.divider()
        st.markdown("**Safety Boundary**")
        st.caption("Advisory decision support only. Synthetic data. No command execution.")

    tab_overview, tab_map, tab_timeline, tab_threat, tab_coa, tab_sim, tab_briefing = st.tabs([
        "Scenario Overview",
        "Map",
        "Timeline",
        "Threat Assessment",
        "COA Ranking",
        "Simulation Results",
        "Commander Briefing",
    ])

    # ---- Scenario Overview ----
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

        st.subheader("Selected Asset Inventory")
        asset_df = pd.DataFrame(
            [{"Asset": ASSET_LABELS.get(asset, asset), "Available": count} for asset, count in asset_inventory.items()]
        )
        st.dataframe(asset_df, use_container_width=True, hide_index=True)

        st.divider()

        type_counts: dict[str, int] = {}
        for e in events:
            label = e.event_type.value
            type_counts[label] = type_counts.get(label, 0) + 1
        st.subheader("Event Type Distribution")
        type_df = pd.DataFrame(
            [{"Event Type": k, "Count": v} for k, v in sorted(type_counts.items())]
        )
        st.bar_chart(type_df, x="Event Type", y="Count")

        st.info("All data is synthetic and for prototype demonstration only.")

    # ---- Map ----
    with tab_map:
        st.header("Operational Map — Baltic Sea")
        m = build_map(events, scenario)
        st_folium(m, width=1100, height=600)

        legend_cols = st.columns(5)
        labels = [
            ("#d73027", "Suspicious Vessel"),
            ("#4575b4", "Allied Vessel"),
            ("#fdae61", "UAV"),
            ("#7b3294", "Convoy"),
            ("#1a9850", "Subsea Cable"),
        ]
        for col, (color, label) in zip(legend_cols, labels):
            col.markdown(
                f"<span style='color:{color}; font-size: 1.4rem;'>■</span> "
                f"<b>{label}</b>",
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
        df = pd.DataFrame(rows)

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
            height=500,
            xaxis_title="Time (UTC)",
            yaxis_title="Entity",
            margin=dict(l=20, r=20, t=30, b=30),
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Event Details")
        st.dataframe(df, use_container_width=True, hide_index=True)

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

            def _highlight_level(val):
                color = _threat_color(val)
                return f"background-color: {color}; color: white; font-weight: bold"

            st.dataframe(
                threat_df.style.map(_highlight_level, subset=["Level"]),
                use_container_width=True,
                hide_index=True,
            )

        st.subheader("Anomaly Indicators")
        high_anomalies = [a for a in anomalies if a.anomaly_score >= 40]
        if high_anomalies:
            anom_rows = []
            for a in sorted(high_anomalies, key=lambda x: x.anomaly_score, reverse=True)[:10]:
                anom_rows.append({
                    "Event": a.event_id,
                    "Entity": a.entity_id,
                    "Score": a.anomaly_score,
                    "Level": a.anomaly_level.value,
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

        # Bar chart
        fig_coa = go.Figure()
        fig_coa.add_trace(go.Bar(
            x=[s.coa.title for s in scored],
            y=[s.total_score for s in scored],
            marker_color=["#2e8b57" if s.rank == 1 else "#4682b4" for s in scored],
            text=[f"{s.total_score:.1f}" for s in scored],
            textposition="outside",
        ))
        fig_coa.update_layout(
            yaxis=dict(range=[0, 100], title="Score"),
            xaxis_title="Course of Action",
            height=400,
            template="plotly_white",
            margin=dict(l=20, r=20, t=30, b=100),
        )
        st.plotly_chart(fig_coa, use_container_width=True)

        # Detail table
        coa_rows = []
        for s in scored:
            coa_rows.append({
                "Rank": s.rank,
                "COA": s.coa.title,
                "Score": s.total_score,
                "Feasibility": f"{s.coa.feasibility_score:.0%}",
                "Success Prob": f"{s.simulation.success_probability:.1%}",
                "Escalation": f"{s.simulation.escalation_probability:.1%}",
                "Cable Risk": f"{s.simulation.risk_to_second_cable:.1%}",
                "Missed Det.": f"{s.simulation.missed_detection_probability:.1%}",
                "Missing Assets": ", ".join(s.coa.missing_assets) or "None",
                "Trade-offs": s.tradeoff_explanation,
            })
        st.dataframe(pd.DataFrame(coa_rows), use_container_width=True, hide_index=True)

        if rec.edge_cases:
            st.info(f"**When alternatives may be preferred:** {rec.edge_cases}")

    # ---- Simulation Results ----
    with tab_sim:
        st.header("Monte Carlo Simulation Results")
        st.caption(
            "Synthetic decision-support estimates based on "
            f"{sims[0].simulation_runs if sims else 0} simulation runs per COA. "
            "Not predictions."
        )

        if sims:
            sim_labels = [s.coa_id for s in sims]

            fig_sim = go.Figure()
            fig_sim.add_trace(go.Bar(name="Success Prob.", x=sim_labels,
                                     y=[s.success_probability for s in sims], marker_color="#2e8b57"))
            fig_sim.add_trace(go.Bar(name="Escalation Prob.", x=sim_labels,
                                     y=[s.escalation_probability for s in sims], marker_color="#ff6600"))
            fig_sim.add_trace(go.Bar(name="Cable Risk", x=sim_labels,
                                     y=[s.risk_to_second_cable for s in sims], marker_color="#cc0000"))
            fig_sim.add_trace(go.Bar(name="Missed Det.", x=sim_labels,
                                     y=[s.missed_detection_probability for s in sims], marker_color="#999999"))
            fig_sim.update_layout(
                barmode="group",
                yaxis=dict(range=[0, 1], tickformat=".0%", title="Probability"),
                xaxis_title="COA",
                height=450,
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_sim, use_container_width=True)

            sim_rows = []
            for s in sims:
                ci = s.confidence_interval
                sim_rows.append({
                    "COA": s.coa_id,
                    "Success": f"{s.success_probability:.1%}",
                    "Time to Effect (min)": s.expected_time_to_effect,
                    "Cable Risk": f"{s.risk_to_second_cable:.1%}",
                    "Escalation": f"{s.escalation_probability:.1%}",
                    "Missed Det.": f"{s.missed_detection_probability:.1%}",
                    "95% CI (Success)": f"[{ci[0]:.1%}, {ci[1]:.1%}]",
                    "Runs": s.simulation_runs,
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

        st.subheader("COAs Considered")
        for coa_name in briefing.coas_considered:
            st.markdown(f"- {coa_name}")

        st.subheader("Recommended COA")
        st.success(briefing.recommended_coa)

        st.subheader("Risks")
        for risk in briefing.risks:
            st.markdown(f"- {risk}")

        col_conf, _ = st.columns([1, 3])
        col_conf.metric("Assessment Confidence", briefing.confidence)

        st.subheader("Assumptions")
        for assumption in briefing.assumptions:
            st.markdown(f"- {assumption}")

        st.divider()
        st.caption("COA Engine — Synthetic decision-support prototype. All outputs are advisory.")


if __name__ == "__main__":
    main()
