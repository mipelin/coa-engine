from __future__ import annotations

"""Deterministic target-supporting asset assignment.

Produces advisory-only supporting-asset suggestions for top targets. This module
never authorizes action and never issues weapon or engagement language.
"""

from dataclasses import asdict, dataclass
from typing import Any

from ..core.schemas import AssetState, Contact, ContactType
from .asset_state import asset_capabilities, asset_profile


@dataclass
class SupportingAssetAssignment:
    target_id: str
    assigned_asset_id: str
    asset_type: str
    assignment_role: str
    suitability_score: float
    constraints: list[str]
    rationale: str
    roe_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SupportingAssetAssignment":
        return cls(**data)


def assign_supporting_asset(
    *,
    target_id: str,
    target_type: str,
    recommended_action: str,
    priority_level: str,
    roe_status: str,
    target_lat: float | None,
    target_lon: float | None,
    asset_states: list[AssetState] | None,
    active_contacts: list[Contact] | None,
) -> SupportingAssetAssignment:
    pool = list(asset_states or [])
    if not pool:
        pool = _infer_support_assets(active_contacts or [])

    role = _assignment_role(target_type=target_type, recommended_action=recommended_action)
    if not pool:
        return SupportingAssetAssignment(
            target_id=target_id,
            assigned_asset_id="none",
            asset_type="none",
            assignment_role=role,
            suitability_score=0.0,
            constraints=["no suitable asset available"],
            rationale=f"No suitable asset available to {role.replace('_', ' ')} for {target_id}.",
            roe_status=roe_status,
        )

    scored = [
        (_suitability(asset, target_type=target_type, role=role, priority_level=priority_level, lat=target_lat, lon=target_lon), asset)
        for asset in pool
    ]
    scored.sort(key=lambda item: (item[0], item[1].asset_id), reverse=True)
    best_score, best_asset = scored[0]
    if best_score <= 0:
        return SupportingAssetAssignment(
            target_id=target_id,
            assigned_asset_id="none",
            asset_type="none",
            assignment_role=role,
            suitability_score=0.0,
            constraints=["no suitable asset available"],
            rationale=f"No suitable asset available to {role.replace('_', ' ')} for {target_id}.",
            roe_status=roe_status,
        )

    constraints = _constraints(best_asset, lat=target_lat, lon=target_lon)
    rationale = _rationale(best_asset, role=role, target_type=target_type, best_score=best_score, constraints=constraints)
    return SupportingAssetAssignment(
        target_id=target_id,
        assigned_asset_id=best_asset.asset_id,
        asset_type=best_asset.asset_type,
        assignment_role=role,
        suitability_score=round(best_score, 1),
        constraints=constraints,
        rationale=rationale,
        roe_status=roe_status,
    )


def _assignment_role(*, target_type: str, recommended_action: str) -> str:
    if target_type == "convoy":
        return "convoy_watch"
    if target_type in {"uav", "aircraft"}:
        return "airspace_watch"
    if target_type == "ground":
        return "convoy_watch"
    if recommended_action == "protect-asset":
        return "protect_infrastructure"
    if recommended_action == "shadow":
        return "shadow"
    if target_type == "vessel" and recommended_action == "track":
        return "track"
    if target_type == "vessel" and recommended_action == "monitor":
        return "monitor"
    if target_type == "submarine":
        return "track"
    return "monitor"


def _suitability(
    asset: AssetState,
    *,
    target_type: str,
    role: str,
    priority_level: str,
    lat: float | None,
    lon: float | None,
) -> float:
    if asset.quantity_available <= 0 or asset.status not in {"available", "ready", "on_station"}:
        return 0.0
    capability_score = _capability_score(asset, role=role, target_type=target_type)
    if capability_score <= 0:
        return 0.0
    score = capability_score
    if asset.domain in {"air", "space"} and target_type in {"uav", "aircraft"}:
        score += 18.0
    if asset.domain == "maritime" and target_type in {"vessel", "submarine"}:
        score += 18.0
    if asset.domain == "coordination" and role in {"airspace_watch", "convoy_watch"}:
        score += 10.0
    if role == "protect_infrastructure" and asset.asset_type in {"maritime_patrol_vessel", "coast_guard_cutter", "isr_uav"}:
        score += 12.0
    if priority_level in {"HIGH", "CRITICAL"} and asset.response_eta_min is not None:
        score += max(0.0, 12.0 - min(float(asset.response_eta_min) / 5.0, 12.0))
    if lat is not None and lon is not None and asset.lat is not None and asset.lon is not None:
        dist = ((asset.lat - lat) ** 2 + (asset.lon - lon) ** 2) ** 0.5
        score += max(0.0, 10.0 - dist * 8.0)
    return round(score, 2)


def _capability_score(asset: AssetState, *, role: str, target_type: str) -> float:
    caps = set(asset.capabilities or [])
    if role == "protect_infrastructure":
        preferred = {"maritime_patrol_vessel", "maritime_patrol_asset", "coast_guard_cutter", "isr_uav", "surveillance_asset"}
    elif role == "airspace_watch":
        preferred = {"isr_uav", "maritime_helicopter", "awacs_coverage", "airspace_coordinator", "atc_liaison", "surveillance_asset"}
    elif role == "convoy_watch":
        preferred = {"border_patrol_liaison", "intelligence_team", "isr_uav", "surveillance_asset", "standard_watch_team"}
    elif role == "shadow":
        preferred = {"maritime_patrol_vessel", "coast_guard_cutter", "maritime_helicopter", "isr_uav", "surveillance_asset"}
    elif role == "track":
        preferred = {"isr_uav", "surveillance_asset", "maritime_patrol_vessel", "maritime_patrol_asset", "sensor_data_feed", "maritime_helicopter"}
    else:
        preferred = {"isr_uav", "surveillance_asset", "sensor_data_feed", "standard_watch_team", "intelligence_team"}
    if caps & preferred:
        return 55.0
    if target_type in {"vessel", "submarine"} and asset.domain == "maritime":
        return 38.0
    if target_type in {"uav", "aircraft"} and asset.domain == "air":
        return 38.0
    if asset.domain == "coordination":
        return 24.0
    return 0.0


def _constraints(asset: AssetState, *, lat: float | None, lon: float | None) -> list[str]:
    constraints: list[str] = []
    if asset.response_eta_min is not None and asset.response_eta_min > 60:
        constraints.append("response_eta_gt_60min")
    if asset.coverage_radius_km is not None and asset.coverage_radius_km < 100:
        constraints.append("limited_coverage")
    if lat is not None and lon is not None and asset.lat is not None and asset.lon is not None:
        dist = ((asset.lat - lat) ** 2 + (asset.lon - lon) ** 2) ** 0.5
        if dist > 1.5:
            constraints.append("distant_from_target_area")
    return constraints


def _rationale(asset: AssetState, *, role: str, target_type: str, best_score: float, constraints: list[str]) -> str:
    role_text = role.replace("_", " ")
    reason = f"{asset.display_name or asset.asset_id} is the best available advisory support asset to {role_text} for a {target_type} target"
    if asset.response_eta_min is not None:
        reason += f"; response ETA {asset.response_eta_min} min"
    reason += f"; suitability {best_score:.1f}"
    if constraints:
        reason += f"; constraints: {', '.join(constraints[:3])}"
    return reason


def _infer_support_assets(contacts: list[Contact]) -> list[AssetState]:
    inferred: list[AssetState] = []
    for contact in contacts:
        attrs = contact.attributes or {}
        allegiance = str(attrs.get("allegiance", "")).lower()
        role = str(attrs.get("role", "")).lower()
        if contact.is_hostile or allegiance == "neutral":
            continue
        if allegiance not in {"friendly", "blue"} and role not in {"allied", "isr", "support"}:
            continue
        asset_type = _asset_type_from_contact(contact)
        if not asset_type:
            continue
        profile = asset_profile(asset_type)
        inferred.append(
            AssetState(
                asset_id=f"contact-{contact.entity_id}",
                asset_type=asset_type,
                capabilities=sorted(asset_capabilities(asset_type, asset_type)),
                quantity_total=1,
                quantity_available=1,
                status="available",
                domain=profile.get("domain"),
                display_name=str(attrs.get("name") or contact.entity_id),
                home_base=profile.get("home_base"),
                location_label=str(attrs.get("name") or profile.get("home_base") or contact.entity_id),
                lat=contact.lat,
                lon=contact.lon,
                coverage_radius_km=profile.get("coverage_radius_km"),
                transit_speed_kts=profile.get("transit_speed_kts"),
                response_eta_min=profile.get("response_eta_min"),
                endurance_hours=profile.get("endurance_hours"),
                on_station_hours=profile.get("on_station_hours"),
                concurrency_limit=int(profile.get("concurrency_limit", 1)),
                notes=f"Inferred from friendly/support contact {contact.entity_id}",
            )
        )
    inferred.sort(key=lambda item: item.asset_id)
    return inferred


def _asset_type_from_contact(contact: Contact) -> str | None:
    attrs = contact.attributes or {}
    name = str(attrs.get("name", "")).lower()
    if contact.contact_type == ContactType.UAV:
        return "isr_uav"
    if contact.contact_type == ContactType.VESSEL:
        if "coast guard" in name or "cutter" in name:
            return "coast_guard_cutter"
        return "maritime_patrol_vessel"
    if contact.contact_type == ContactType.RADAR:
        return "maritime_helicopter"
    if attrs.get("role") == "support":
        return "standard_watch_team"
    return None
