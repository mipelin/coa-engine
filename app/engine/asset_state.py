from __future__ import annotations

from typing import Any

from ..core.schemas import AssetState, OperationalEvent

DEFAULT_ASSET_PROFILES: dict[str, dict[str, Any]] = {
    "isr_uav": {
        "domain": "air",
        "home_base": "Visby Airfield",
        "coverage_radius_km": 180.0,
        "transit_speed_kts": 90.0,
        "response_eta_min": 25,
        "endurance_hours": 8.0,
        "on_station_hours": 5.5,
        "concurrency_limit": 1,
    },
    "maritime_patrol_vessel": {
        "domain": "maritime",
        "home_base": "Slite Patrol Anchorage",
        "coverage_radius_km": 260.0,
        "transit_speed_kts": 30.0,
        "response_eta_min": 60,
        "endurance_hours": 72.0,
        "on_station_hours": 24.0,
        "concurrency_limit": 1,
    },
    "coast_guard_cutter": {
        "domain": "maritime",
        "home_base": "Visby Coast Guard Pier",
        "coverage_radius_km": 220.0,
        "transit_speed_kts": 24.0,
        "response_eta_min": 70,
        "endurance_hours": 96.0,
        "on_station_hours": 36.0,
        "concurrency_limit": 1,
    },
    "maritime_patrol_asset": {
        "domain": "maritime",
        "home_base": "Regional Patrol Anchorage",
        "coverage_radius_km": 260.0,
        "transit_speed_kts": 28.0,
        "response_eta_min": 60,
        "endurance_hours": 72.0,
        "on_station_hours": 24.0,
        "concurrency_limit": 1,
    },
    "coast_guard_liaison": {
        "domain": "coordination",
        "home_base": "Gotland Coordination Cell",
        "coverage_radius_km": 9999.0,
        "transit_speed_kts": 0.0,
        "response_eta_min": 15,
        "endurance_hours": 12.0,
        "on_station_hours": 12.0,
    },
    "cable_operator_liaison": {
        "domain": "coordination",
        "home_base": "Cable NOC",
        "coverage_radius_km": 9999.0,
        "transit_speed_kts": 0.0,
        "response_eta_min": 20,
        "endurance_hours": 12.0,
        "on_station_hours": 12.0,
    },
    "sigint_team": {
        "domain": "intelligence",
        "home_base": "Signals Detachment East",
        "coverage_radius_km": 120.0,
        "transit_speed_kts": 20.0,
        "response_eta_min": 45,
        "endurance_hours": 16.0,
        "on_station_hours": 10.0,
    },
    "airspace_coordinator": {
        "domain": "coordination",
        "home_base": "Civil Aviation Coordination Center",
        "coverage_radius_km": 9999.0,
        "transit_speed_kts": 0.0,
        "response_eta_min": 10,
        "endurance_hours": 12.0,
        "on_station_hours": 12.0,
    },
    "atc_liaison": {
        "domain": "coordination",
        "home_base": "Regional ATC Center",
        "coverage_radius_km": 9999.0,
        "transit_speed_kts": 0.0,
        "response_eta_min": 10,
        "endurance_hours": 12.0,
        "on_station_hours": 12.0,
    },
    "border_patrol_liaison": {
        "domain": "coordination",
        "home_base": "Border Monitoring Cell",
        "coverage_radius_km": 9999.0,
        "transit_speed_kts": 0.0,
        "response_eta_min": 20,
        "endurance_hours": 12.0,
        "on_station_hours": 12.0,
    },
    "intelligence_team": {
        "domain": "intelligence",
        "home_base": "Joint Analysis Cell",
        "coverage_radius_km": 9999.0,
        "transit_speed_kts": 0.0,
        "response_eta_min": 30,
        "endurance_hours": 10.0,
        "on_station_hours": 10.0,
    },
    "surveillance_asset": {
        "domain": "air",
        "home_base": "Regional ISR Hub",
        "coverage_radius_km": 220.0,
        "transit_speed_kts": 85.0,
        "response_eta_min": 35,
        "endurance_hours": 7.0,
        "on_station_hours": 4.0,
    },
    "satellite_pass": {
        "domain": "space",
        "home_base": "Remote Space Tasking",
        "coverage_radius_km": 9999.0,
        "transit_speed_kts": 0.0,
        "response_eta_min": 15,
        "endurance_hours": 1.0,
        "on_station_hours": 0.5,
    },
    "maritime_helicopter": {
        "domain": "air",
        "home_base": "Naval Air Detachment",
        "coverage_radius_km": 200.0,
        "transit_speed_kts": 120.0,
        "response_eta_min": 20,
        "endurance_hours": 4.5,
        "on_station_hours": 2.5,
    },
    "awacs_coverage": {
        "domain": "air",
        "home_base": "AEW Orbit South",
        "coverage_radius_km": 450.0,
        "transit_speed_kts": 0.0,
        "response_eta_min": 30,
        "endurance_hours": 8.0,
        "on_station_hours": 6.0,
    },
    "sensor_data_feed": {
        "domain": "coordination",
        "home_base": "Fusion Network",
        "coverage_radius_km": 9999.0,
        "transit_speed_kts": 0.0,
        "response_eta_min": 5,
        "endurance_hours": 24.0,
        "on_station_hours": 24.0,
    },
    "standard_watch_team": {
        "domain": "coordination",
        "home_base": "Operations Floor",
        "coverage_radius_km": 9999.0,
        "transit_speed_kts": 0.0,
        "response_eta_min": 0,
        "endurance_hours": 24.0,
        "on_station_hours": 24.0,
    },
}

DEFAULT_FALLBACK_PROFILE = {
    "domain": "general",
    "home_base": "Forward Operations Node",
    "coverage_radius_km": 150.0,
    "transit_speed_kts": 30.0,
    "response_eta_min": 45,
    "endurance_hours": 8.0,
    "on_station_hours": 4.0,
    "concurrency_limit": 1,
}

DEFAULT_BASE_OFFSETS: dict[str, tuple[float, float]] = {
    "Visby Airfield": (0.35, -0.40),
    "Slite Patrol Anchorage": (0.10, 0.20),
    "Visby Coast Guard Pier": (0.30, -0.25),
    "Regional Patrol Anchorage": (-0.15, 0.30),
    "Gotland Coordination Cell": (0.20, -0.10),
    "Cable NOC": (0.05, 0.05),
    "Signals Detachment East": (-0.20, 0.35),
    "Civil Aviation Coordination Center": (0.45, -0.30),
    "Regional ATC Center": (0.40, -0.35),
    "Border Monitoring Cell": (-0.45, -0.20),
    "Joint Analysis Cell": (0.15, -0.05),
    "Regional ISR Hub": (0.25, -0.15),
    "Remote Space Tasking": (0.0, 0.0),
    "Naval Air Detachment": (0.28, -0.22),
    "AEW Orbit South": (0.55, -0.10),
    "Fusion Network": (0.18, -0.12),
    "Operations Floor": (0.18, -0.12),
    "Forward Operations Node": (0.0, 0.0),
}

ASSET_CAPABILITIES: dict[str, set[str]] = {
    "isr_uav": {"isr_uav", "surveillance_asset", "sensor_data_feed"},
    "maritime_patrol_asset": {"maritime_patrol_asset"},
    "maritime_patrol_vessel": {"maritime_patrol_asset", "maritime_patrol_vessel"},
    "coast_guard_cutter": {"maritime_patrol_asset", "coast_guard_cutter"},
    "coast_guard_liaison": {"coast_guard_liaison"},
    "cable_operator_liaison": {"cable_operator_liaison"},
    "sigint_team": {"sigint_team", "intelligence_team"},
    "intelligence_team": {"intelligence_team"},
    "osint_cell": {"intelligence_team"},
    "airspace_coordinator": {"airspace_coordinator"},
    "atc_liaison": {"atc_liaison", "airspace_coordinator"},
    "border_patrol_liaison": {"border_patrol_liaison"},
    "surveillance_asset": {"surveillance_asset", "sensor_data_feed"},
    "satellite_observation_request": {"satellite_observation_request"},
    "satellite_pass": {"satellite_observation_request", "satellite_pass", "sensor_data_feed"},
    "maritime_helicopter": {"surveillance_asset", "sensor_data_feed"},
    "awacs_coverage": {"surveillance_asset", "sensor_data_feed"},
    "sensor_data_feed": {"sensor_data_feed"},
    "standard_watch_team": {"standard_watch_team"},
}


def asset_profile(asset_id: str) -> dict[str, Any]:
    return {**DEFAULT_FALLBACK_PROFILE, **DEFAULT_ASSET_PROFILES.get(asset_id, {})}


def asset_capabilities(asset_id: str, asset_type: str | None = None) -> set[str]:
    capabilities = set(ASSET_CAPABILITIES.get(asset_id, set()))
    if asset_type:
        capabilities |= set(ASSET_CAPABILITIES.get(asset_type, set()))
        capabilities.add(asset_type)
    capabilities.add(asset_id)
    return capabilities


def asset_state_from_inventory(asset_id: str, quantity: int) -> AssetState:
    profile = asset_profile(asset_id)
    qty = max(int(quantity), 0)
    return AssetState(
        asset_id=asset_id,
        asset_type=asset_id,
        capabilities=sorted(asset_capabilities(asset_id)),
        quantity_total=qty,
        quantity_available=qty,
        status="available" if qty > 0 else "unavailable",
        domain=profile["domain"],
        display_name=asset_id.replace("_", " ").title(),
        home_base=profile.get("home_base"),
        location_label=profile.get("home_base"),
        coverage_radius_km=profile["coverage_radius_km"],
        transit_speed_kts=profile["transit_speed_kts"],
        response_eta_min=profile["response_eta_min"],
        endurance_hours=profile.get("endurance_hours"),
        on_station_hours=profile.get("on_station_hours"),
        concurrency_limit=int(profile.get("concurrency_limit", 1)),
    )


def centroid_for_events(events: list[OperationalEvent]) -> tuple[float | None, float | None]:
    if not events:
        return None, None
    return (
        sum(event.lat for event in events) / len(events),
        sum(event.lon for event in events) / len(events),
    )


def build_simulated_asset_states(
    asset_inventory: dict[str, int] | None,
    events: list[OperationalEvent] | None = None,
) -> list[AssetState]:
    """Create plausible positioned AssetState objects for simulation/demo use."""
    if not asset_inventory:
        return []
    center_lat, center_lon = centroid_for_events(events or [])
    if center_lat is None or center_lon is None:
        center_lat, center_lon = 57.5, 19.5

    states: list[AssetState] = []
    for asset_id, quantity in sorted(asset_inventory.items()):
        state = asset_state_from_inventory(asset_id, quantity)
        base_name = state.home_base or "Forward Operations Node"
        dlat, dlon = DEFAULT_BASE_OFFSETS.get(base_name, (0.0, 0.0))
        if state.domain in {"space", "coordination"}:
            lat = center_lat + dlat
            lon = center_lon + dlon
        else:
            lat = center_lat + dlat
            lon = center_lon + dlon
        state = state.model_copy(update={
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "location_label": base_name,
        })
        states.append(state)
    return states
