from __future__ import annotations

import logging
from typing import Any

from ..core.schemas import AssetState, CourseOfAction, OperationalEvent
from .asset_state import asset_capabilities
from .contact_enrichment import haversine_km

logger = logging.getLogger("coa_engine.engine.coa_validation")


def _target_centroid(
    coa: CourseOfAction,
    events: list[OperationalEvent] | None,
) -> tuple[float | None, float | None]:
    if not events:
        return None, None
    target_events = [event for event in events if event.entity_id in coa.target_entities]
    relevant = target_events or events
    return (
        sum(event.lat for event in relevant) / len(relevant),
        sum(event.lon for event in relevant) / len(relevant),
    )


def _asset_is_spatially_feasible(
    asset: AssetState,
    target_lat: float | None,
    target_lon: float | None,
    max_eta_min: int,
) -> tuple[bool, list[str]]:
    warnings: list[str] = []
    if asset.quantity_available <= 0 or asset.status not in {"available", "degraded"}:
        warnings.append(f"{asset.asset_id} unavailable")
        return False, warnings

    if target_lat is None or target_lon is None:
        return True, warnings

    if asset.response_eta_min is not None and asset.response_eta_min > max_eta_min:
        warnings.append(f"{asset.asset_id} base ETA {asset.response_eta_min}m exceeds target timeline")

    if asset.lat is None or asset.lon is None:
        return asset.response_eta_min is None or asset.response_eta_min <= max_eta_min, warnings

    distance_km = haversine_km(asset.lat, asset.lon, target_lat, target_lon)
    if asset.coverage_radius_km is not None and distance_km > asset.coverage_radius_km:
        warnings.append(
            f"{asset.asset_id} outside coverage radius ({distance_km:.0f}km > {asset.coverage_radius_km:.0f}km)"
        )
        return False, warnings

    if asset.transit_speed_kts and asset.transit_speed_kts > 0:
        transit_eta_min = int(round((distance_km / (asset.transit_speed_kts * 1.852)) * 60))
        if transit_eta_min > max_eta_min:
            warnings.append(f"{asset.asset_id} transit ETA {transit_eta_min}m exceeds target timeline")
            return False, warnings

    return True, warnings


def _candidate_priority(asset: AssetState, required_asset: str) -> tuple[int, int, int]:
    if asset.asset_id == required_asset:
        match_rank = 0
    elif asset.asset_type == required_asset:
        match_rank = 1
    elif required_asset in set(asset.capabilities):
        match_rank = 2
    else:
        match_rank = 3
    eta_rank = asset.response_eta_min if asset.response_eta_min is not None else 999999
    return (match_rank, eta_rank, -asset.quantity_available)


def validate_coa(
    coa: CourseOfAction,
    asset_inventory: dict[str, int] | None = None,
    active_entity_ids: list[str] | None = None,
    asset_states: list[AssetState] | None = None,
    events: list[OperationalEvent] | None = None,
) -> CourseOfAction:
    """Validate and adjust a COA based on available assets and current state.

    Checks:
    - Asset feasibility (do we have what we need?)
    - Logical consistency (does the COA reference real entities?)
    - Time feasibility (is the estimated time reasonable?)
    """
    issues: list[str] = []

    state_by_id = {asset.asset_id: asset for asset in (asset_states or [])}
    if not state_by_id and asset_inventory:
        from .state_store import StateStore
        state_by_id = {
            asset.asset_id: asset
            for asset in StateStore.inventory_to_asset_states(asset_inventory)
        }
    target_lat, target_lon = _target_centroid(coa, events)
    available_list: list[str] = []
    missing_list: list[str] = []
    remaining_units = {
        asset_id: asset.quantity_available
        for asset_id, asset in state_by_id.items()
    }

    for required_asset in coa.required_assets:
        candidate_states = [
            asset
            for asset in state_by_id.values()
            if required_asset in asset_capabilities(asset.asset_id, asset.asset_type)
            and remaining_units.get(asset.asset_id, 0) > 0
        ]
        candidate_states.sort(key=lambda asset: _candidate_priority(asset, required_asset))

        chosen_asset: AssetState | None = None
        for asset_state in candidate_states:
            feasible, spatial_warnings = _asset_is_spatially_feasible(
                asset_state,
                target_lat,
                target_lon,
                coa.estimated_time_minutes,
            )
            issues.extend(spatial_warnings)
            if feasible:
                chosen_asset = asset_state
                break

        if chosen_asset is not None:
            remaining_units[chosen_asset.asset_id] -= 1
            available_list.append(chosen_asset.asset_id)
            if chosen_asset.asset_id != required_asset:
                issues.append(
                    f"{required_asset} satisfied via {chosen_asset.asset_id}"
                )
            continue

        if asset_inventory is not None:
            if asset_inventory.get(required_asset, 1) > 0:
                available_list.append(required_asset)
            else:
                missing_list.append(required_asset)
        else:
            if candidate_states:
                missing_list.append(required_asset)
            else:
                available_list.append(required_asset)

    feasibility = 1.0
    if coa.required_assets:
        feasibility = len(available_list) / len(coa.required_assets)
    if feasibility < 0.5:
        issues.append(f"Only {feasibility:.0%} of required assets available")

    if coa.estimated_time_minutes > 120:
        issues.append("Response time exceeds 2 hours — may be too slow for rapid escalation")

    if active_entity_ids is not None and coa.target_entities:
        unknown_targets = [entity_id for entity_id in coa.target_entities if entity_id not in active_entity_ids]
        if unknown_targets:
            issues.append(
                "COA references entities not present in the active scenario: "
                + ", ".join(unknown_targets)
            )

    assumptions = list(coa.assumptions)
    if missing_list:
        assumptions.append(
            "Current asset inventory does not fully support this COA: "
            + ", ".join(missing_list)
        )

    if feasibility == 1.0 and not issues:
        feasibility_status = "feasible"
    elif feasibility > 0.0:
        feasibility_status = "partially_feasible"
    else:
        feasibility_status = "infeasible"

    coa = coa.model_copy(update={
        "assigned_assets": available_list,
        "available_assets": available_list,
        "missing_assets": missing_list,
        "feasibility_score": round(feasibility, 3),
        "feasibility_status": feasibility_status,
        "validation_warnings": issues,
        "assumptions": assumptions,
    })

    if issues:
        logger.debug("COA %s validation: %s", coa.coa_id, "; ".join(issues))

    return coa


def validate_coa_set(
    coas: list[CourseOfAction],
    asset_inventory: dict[str, int] | None = None,
    active_entity_ids: list[str] | None = None,
    asset_states: list[AssetState] | None = None,
    events: list[OperationalEvent] | None = None,
) -> list[CourseOfAction]:
    """Validate a set of COAs. Keeps all COAs but flags infeasible ones."""
    validated = []
    for coa in coas:
        v = validate_coa(coa, asset_inventory, active_entity_ids, asset_states, events)
        validated.append(v)

    pool_available: dict[str, int] = {}
    if asset_states:
        pool_available = {
            asset.asset_id: asset.quantity_available
            for asset in asset_states
        }
    elif asset_inventory:
        pool_available = {asset_id: max(int(qty), 0) for asset_id, qty in asset_inventory.items()}

    if pool_available:
        demand_counts: dict[str, int] = {}
        for coa in validated:
            for asset_id in coa.assigned_assets:
                demand_counts[asset_id] = demand_counts.get(asset_id, 0) + 1

        updated: list[CourseOfAction] = []
        for coa in validated:
            pressure_warnings = list(coa.validation_warnings)
            for asset_id in set(coa.assigned_assets):
                available = pool_available.get(asset_id)
                demand = demand_counts.get(asset_id, 0)
                if available is not None and demand > available:
                    pressure_warnings.append(
                        f"Shared demand pressure on {asset_id}: {demand} COAs for {available} available unit(s)"
                    )
            updated.append(coa.model_copy(update={"validation_warnings": pressure_warnings}))
        return updated
    return validated
