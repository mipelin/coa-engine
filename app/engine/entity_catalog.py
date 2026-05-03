"""Entity catalog — per-scenario entity definitions with behavior policies.

DEPRECATED: The contact engine now initializes from ScenarioTemplate
(scenario_generator.py) which is the single source of truth for entities
and stimuli. This module is retained for backward-compatible tests only.
Do not add new scenarios here — add them to scenario_generator.py instead.

Each entity entry specifies:
  - entity_id, name, type, hostile, initial position/speed/heading
  - allegiance: red | blue | neutral | infrastructure
  - behavior_policy: name of a behavior_models policy (or None for static)
  - behavior_params: kwargs forwarded to the policy constructor
"""

from __future__ import annotations

from typing import Any

from ..core.schemas import ContactType


def _cable_route_points(scenario_id: str) -> list[dict[str, Any]]:
    """Return cable waypoints for neutral vessel routes (reuse existing routes)."""
    from ..core.constants import SCENARIO_CABLE_ROUTES

    routes = SCENARIO_CABLE_ROUTES.get(scenario_id, [])
    if not routes:
        return []
    return routes[0]["points"]


def get_catalog(scenario_id: str) -> list[dict[str, Any]]:
    """Return the entity catalog for the given scenario."""
    if scenario_id == "baltic_hybrid_001":
        return _baltic_catalog()
    elif scenario_id == "arctic_submarine_001":
        return _arctic_catalog()
    elif scenario_id in ("mediterranean_001", "mediterranean_swarm_001"):
        return _mediterranean_catalog()
    return []


def _baltic_catalog() -> list[dict[str, Any]]:
    return [
        {
            "entity_id": "VES-SUSP-001",
            "name": "MV NORDIC WIND",
            "type": ContactType.VESSEL,
            "hostile": True,
            "allegiance": "red",
            "lat": 57.45,
            "lon": 18.90,
            "speed": 8.0,
            "heading": 85.0,
            "behavior_policy": "hostile_probe_infrastructure",
            "behavior_params": {"target_infra_name": "Baltic Cable Alpha"},
        },
        {
            "entity_id": "VES-SUSP-002",
            "name": "RIGA STAR",
            "type": ContactType.VESSEL,
            "hostile": True,
            "allegiance": "red",
            "lat": 57.80,
            "lon": 19.50,
            "speed": 1.2,
            "heading": 45.0,
            "behavior_policy": "hostile_loiter_then_divert",
            "behavior_params": {
                "loiter_area_lat": 57.80,
                "loiter_area_lon": 19.50,
                "divert_tick": 12,
                "divert_stimulus": "cable_severance",
                "divert_heading": 310.0,
                "divert_speed": 8.0,
            },
        },
        {
            "entity_id": "VES-ALLIED-001",
            "name": "HMS Visby",
            "type": ContactType.VESSEL,
            "hostile": False,
            "allegiance": "blue",
            "lat": 57.60,
            "lon": 18.50,
            "speed": 12.0,
            "heading": 90.0,
            "behavior_policy": "friendly_patrol_monitor",
            "behavior_params": {
                "patrol_heading_a": 90.0,
                "patrol_heading_b": 270.0,
                "patrol_flip_ticks": 6,
                "react_range_km": 50.0,
            },
        },
        {
            "entity_id": "UAV-001",
            "name": "Unidentified UAV",
            "type": ContactType.UAV,
            "hostile": True,
            "allegiance": "red",
            "lat": 57.68,
            "lon": 18.30,
            "speed": 35.0,
            "heading": 180.0,
            "behavior_policy": None,
            "behavior_params": {},
        },
        {
            "entity_id": "CONVOY-001",
            "name": "Convoy Alpha",
            "type": ContactType.CONVOY,
            "hostile": True,
            "allegiance": "red",
            "lat": 57.20,
            "lon": 22.50,
            "speed": 18.0,
            "heading": 270.0,
            "behavior_policy": None,
            "behavior_params": {},
        },
        {
            "entity_id": "VES-NEUTRAL-001",
            "name": "MV BALTIC TRADER",
            "type": ContactType.VESSEL,
            "hostile": False,
            "allegiance": "neutral",
            "lat": 56.50,
            "lon": 18.00,
            "speed": 10.0,
            "heading": 45.0,
            "flag": "Liberia",
            "behavior_policy": "neutral_transit",
            "behavior_params": {
                "route": [
                    (56.50, 18.00),
                    (56.80, 18.60),
                    (57.10, 19.20),
                    (57.40, 19.80),
                    (57.70, 20.40),
                    (58.00, 21.00),
                ],
            },
        },
    ]


def _arctic_catalog() -> list[dict[str, Any]]:
    return [
        {
            "entity_id": "SUB-SUSP-001",
            "name": "Kilo-class Sub",
            "type": ContactType.SUBMARINE,
            "hostile": True,
            "allegiance": "red",
            "lat": 72.50,
            "lon": 25.00,
            "speed": 5.0,
            "heading": 180.0,
            "behavior_policy": "hostile_probe_infrastructure",
            "behavior_params": {"target_infra_name": "Svalbard Undersea Cable"},
        },
        {
            "entity_id": "VES-SUSP-001",
            "name": "Icebreaker Sigrid",
            "type": ContactType.VESSEL,
            "hostile": True,
            "allegiance": "red",
            "lat": 74.00,
            "lon": 20.00,
            "speed": 3.0,
            "heading": 45.0,
            "behavior_policy": "hostile_loiter_then_divert",
            "behavior_params": {
                "loiter_area_lat": 74.00,
                "loiter_area_lon": 20.00,
                "divert_tick": 14,
                "divert_stimulus": "cable_severance",
                "divert_heading": 225.0,
                "divert_speed": 6.0,
            },
        },
        {
            "entity_id": "VES-ALLIED-001",
            "name": "HNoMS Fridtjof Nansen",
            "type": ContactType.VESSEL,
            "hostile": False,
            "allegiance": "blue",
            "lat": 71.00,
            "lon": 19.00,
            "speed": 14.0,
            "heading": 0.0,
            "behavior_policy": "friendly_patrol_monitor",
            "behavior_params": {
                "patrol_heading_a": 0.0,
                "patrol_heading_b": 180.0,
                "patrol_flip_ticks": 8,
                "react_range_km": 60.0,
            },
        },
        {
            "entity_id": "UAV-001",
            "name": "Recon UAV",
            "type": ContactType.UAV,
            "hostile": True,
            "allegiance": "red",
            "lat": 69.40,
            "lon": 16.00,
            "speed": 40.0,
            "heading": 90.0,
            "behavior_policy": None,
            "behavior_params": {},
        },
        {
            "entity_id": "VES-NEUTRAL-001",
            "name": "FV ARCTIC SUN",
            "type": ContactType.VESSEL,
            "hostile": False,
            "allegiance": "neutral",
            "lat": 70.00,
            "lon": 15.00,
            "speed": 8.0,
            "heading": 30.0,
            "flag": "Norway",
            "behavior_policy": "neutral_transit",
            "behavior_params": {
                "route": [
                    (70.00, 15.00),
                    (71.00, 16.00),
                    (72.00, 17.00),
                    (73.00, 18.00),
                    (74.00, 19.00),
                ],
            },
        },
    ]


def _mediterranean_catalog() -> list[dict[str, Any]]:
    return [
        {
            "entity_id": "VES-SUSP-001",
            "name": "HELIOS VOYAGE",
            "type": ContactType.VESSEL,
            "hostile": True,
            "allegiance": "red",
            "lat": 34.50,
            "lon": 32.00,
            "speed": 2.0,
            "heading": 0.0,
            "behavior_policy": "hostile_probe_infrastructure",
            "behavior_params": {"target_infra_name": "Cyprus Communication Node"},
        },
        {
            "entity_id": "VES-SUSP-002",
            "name": "AEGEAN TRADER",
            "type": ContactType.VESSEL,
            "hostile": True,
            "allegiance": "red",
            "lat": 35.00,
            "lon": 28.00,
            "speed": 8.0,
            "heading": 120.0,
            "behavior_policy": "hostile_loiter_then_divert",
            "behavior_params": {
                "loiter_area_lat": 35.00,
                "loiter_area_lon": 28.00,
                "divert_tick": 16,
                "divert_stimulus": "cable_severance",
                "divert_heading": 180.0,
                "divert_speed": 10.0,
            },
        },
        {
            "entity_id": "VES-ALLIED-001",
            "name": "HS Kanaris",
            "type": ContactType.VESSEL,
            "hostile": False,
            "allegiance": "blue",
            "lat": 35.48,
            "lon": 24.15,
            "speed": 16.0,
            "heading": 90.0,
            "behavior_policy": "friendly_patrol_monitor",
            "behavior_params": {
                "patrol_heading_a": 90.0,
                "patrol_heading_b": 270.0,
                "patrol_flip_ticks": 5,
                "react_range_km": 55.0,
            },
        },
        {
            "entity_id": "UAV-001",
            "name": "Recon Drone",
            "type": ContactType.UAV,
            "hostile": True,
            "allegiance": "red",
            "lat": 35.50,
            "lon": 24.10,
            "speed": 35.0,
            "heading": 180.0,
            "behavior_policy": None,
            "behavior_params": {},
        },
        {
            "entity_id": "VES-NEUTRAL-001",
            "name": "MV EASTERN STAR",
            "type": ContactType.VESSEL,
            "hostile": False,
            "allegiance": "neutral",
            "lat": 34.00,
            "lon": 25.00,
            "speed": 12.0,
            "heading": 90.0,
            "flag": "Malta",
            "behavior_policy": "neutral_transit",
            "behavior_params": {
                "route": [
                    (34.00, 25.00),
                    (34.20, 26.00),
                    (34.40, 27.00),
                    (34.60, 28.00),
                    (34.80, 29.00),
                    (35.00, 30.00),
                ],
            },
        },
    ]
