from __future__ import annotations

import logging

from ..core.constants import EventType
from ..core.schemas import AssetState, Contact, CourseOfAction, OperationalEvent, ThreatResult
from .asset_state import asset_capabilities, asset_profile
from .coa_templates import select_templates
from .coa_validation import validate_coa_set

logger = logging.getLogger("coa_engine.engine.coa_generation")


def _has_cable_severance(events: list[OperationalEvent]) -> bool:
    return any(e.event_type == EventType.CABLE_SEVERANCE for e in events)


def _has_uav_threat(threats: list[ThreatResult]) -> bool:
    return any("UAV" in t.entity_id for t in threats)


def _has_convoy_activity(events: list[OperationalEvent]) -> bool:
    return any(e.event_type == EventType.CONVOY_SIGHTING for e in events)


def _max_threat_level(threats: list[ThreatResult]) -> str:
    if not threats:
        return "LOW"
    return threats[0].threat_level.value


def _support_metrics(events: list[OperationalEvent]) -> dict[str, int]:
    latest_by_entity: dict[str, OperationalEvent] = {}
    for event in events:
        current = latest_by_entity.get(event.entity_id)
        if current is None or event.timestamp >= current.timestamp:
            latest_by_entity[event.entity_id] = event

    allied_vessels = 0
    isr_support = 0
    pressure_entities: set[str] = set()

    for event in latest_by_entity.values():
        if event.entity_type.value == "allied_vessel":
            allied_vessels += 1
        elif event.entity_type.value == "isr_asset":
            isr_support += 1

        if event.entity_type.value in {"suspicious_vessel", "uav", "convoy"}:
            pressure_entities.add(event.entity_id)

    return {
        "allied_vessels": allied_vessels,
        "isr_support": isr_support,
        "friendly_support": allied_vessels + isr_support,
        "pressure_entities": len(pressure_entities),
    }


def _contact_asset_type(event: OperationalEvent) -> str | None:
    if event.entity_type.value == "allied_vessel":
        name = str(event.attributes.get("name", "")).lower()
        if "coast guard" in name or "cutter" in name:
            return "coast_guard_cutter"
        return "maritime_patrol_vessel"
    if event.entity_type.value == "isr_asset":
        name = str(event.attributes.get("name", "")).lower()
        if "sat" in name:
            return "satellite_pass"
        if "awacs" in name:
            return "awacs_coverage"
        return "isr_uav"
    return None


def _asset_state_from_contact_event(event: OperationalEvent) -> AssetState | None:
    asset_type = _contact_asset_type(event)
    if not asset_type:
        return None
    profile = asset_profile(asset_type)
    return AssetState(
        asset_id=f"contact-{event.entity_id}",
        asset_type=asset_type,
        capabilities=sorted(asset_capabilities(asset_type, asset_type)),
        quantity_total=1,
        quantity_available=1,
        status="available",
        domain=profile.get("domain"),
        display_name=str(event.attributes.get("name") or event.entity_id),
        home_base=profile.get("home_base"),
        location_label=str(event.attributes.get("name") or profile.get("home_base") or event.entity_id),
        lat=event.lat,
        lon=event.lon,
        coverage_radius_km=profile.get("coverage_radius_km"),
        transit_speed_kts=profile.get("transit_speed_kts"),
        response_eta_min=profile.get("response_eta_min"),
        endurance_hours=profile.get("endurance_hours"),
        on_station_hours=profile.get("on_station_hours"),
        concurrency_limit=int(profile.get("concurrency_limit", 1)),
        notes=f"Derived from live contact {event.entity_id}",
    )


def _derive_contact_asset_states(
    events: list[OperationalEvent],
    active_contacts: list[Contact] | None = None,
) -> list[AssetState]:
    latest_by_entity: dict[str, OperationalEvent] = {}
    for event in events:
        current = latest_by_entity.get(event.entity_id)
        if current is None or event.timestamp >= current.timestamp:
            latest_by_entity[event.entity_id] = event

    if active_contacts is not None:
        active_ids = {contact.entity_id for contact in active_contacts}
        latest_by_entity = {
            entity_id: event
            for entity_id, event in latest_by_entity.items()
            if entity_id in active_ids
        }

    derived: list[AssetState] = []
    for event in latest_by_entity.values():
        state = _asset_state_from_contact_event(event)
        if state is not None:
            derived.append(state)
    return derived


def generate_coas(
    events: list[OperationalEvent],
    threats: list[ThreatResult],
    asset_inventory: dict[str, int] | None = None,
    asset_states: list[AssetState] | None = None,
    active_contacts: list[Contact] | None = None,
) -> list[CourseOfAction]:
    """Generate advisory courses of action using template-based system."""
    cable_severed = _has_cable_severance(events)
    uav_threat = _has_uav_threat(threats)
    convoy_active = _has_convoy_activity(events)
    threat_level = _max_threat_level(threats)
    support = _support_metrics(events)
    merged_asset_states = list(asset_states or [])
    if not merged_asset_states and not asset_inventory:
        derived_assets = _derive_contact_asset_states(events, active_contacts=active_contacts)
        seen_asset_ids = {state.asset_id for state in merged_asset_states}
        for derived in derived_assets:
            if derived.asset_id not in seen_asset_ids:
                merged_asset_states.append(derived)
                seen_asset_ids.add(derived.asset_id)

    friendly_support = support["friendly_support"]
    pressure_entities = support["pressure_entities"]

    templates = select_templates(
        cable_severed=cable_severed,
        uav_threat=uav_threat,
        convoy_active=convoy_active,
        high_threat=threat_level in ("HIGH", "CRITICAL"),
        critical_threat=threat_level == "CRITICAL",
        friendly_support_available=friendly_support >= 1,
        friendly_support_high=friendly_support >= 2,
        support_gap=pressure_entities > max(1, friendly_support),
        multi_contact_pressure=pressure_entities >= 3,
    )
    if friendly_support == 0:
        templates = [tpl for tpl in templates if tpl.template_id != "COA-TPL-SHADOW"]
    if friendly_support <= 1:
        templates = [tpl for tpl in templates if tpl.template_id != "COA-TPL-COMBINED"]

    # Build entity context for template binding
    hostile_entities = []
    for t in threats:
        if t.threat_level.value in ("HIGH", "CRITICAL"):
            hostile_events = [e for e in events if e.entity_id == t.entity_id]
            name = hostile_events[0].attributes.get("name", t.entity_id) if hostile_events else t.entity_id
            hostile_entities.append({"entity_id": t.entity_id, "name": name})

    # Find nearest infrastructure name for template binding
    infra_name = "critical infrastructure"
    if events:
        for e in events:
            if e.event_type == EventType.CABLE_SEVERANCE:
                infra_name = "remaining subsea cable"
                break

    # Bind templates to produce concrete COAs
    scenario_context = (
        f"threat_level={threat_level}; cable_severed={cable_severed}; "
        f"uav_threat={uav_threat}; convoy_active={convoy_active}; "
        f"friendly_support={friendly_support}; pressure_entities={pressure_entities}"
    )

    coas = []
    for tpl in templates:
        coa = tpl.bind(
            entities=hostile_entities,
            infra=infra_name,
            scenario_context=scenario_context,
        )
        coas.append(coa)

    # Validate against asset inventory
    active_entity_ids = list({e.entity_id for e in events})
    coas = validate_coa_set(
        coas,
        asset_inventory=asset_inventory,
        active_entity_ids=active_entity_ids,
        asset_states=merged_asset_states,
        events=events,
    )

    logger.info(
        "Generated %d rule-based COAs from templates (cable=%s, uav=%s, convoy=%s, threat=%s, friendly=%d, pressure=%d)",
        len(coas), cable_severed, uav_threat, convoy_active, threat_level, friendly_support, pressure_entities,
    )
    return coas
