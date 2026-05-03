"""Formal event update system for external operational events.

Processes structured external events (cable severed, jamming detected, etc.)
and applies their effects to scenario state. No LLM calls.

Event effects:
- update scenario state (active_incidents, infrastructure_status)
- trigger COA recalculation when relevant
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger("coa_engine.engine.event_engine")


class ExternalEventType(str, Enum):
    UAV_DETECTED = "uav_detected"
    CABLE_SEVERED = "cable_severed"
    VESSEL_COURSE_CHANGE = "vessel_course_change"
    CONVOY_SIGHTING = "convoy_sighting"
    JAMMING_DETECTED = "jamming_detected"
    HOSTILE_INTENT_OBSERVED = "hostile_intent_observed"
    SATELLITE_CONFIRMATION = "satellite_confirmation"
    SOCIAL_MEDIA_REPORT = "social_media_report"
    ASSET_STATUS_CHANGE = "asset_status_change"


class ExternalEvent(BaseModel):
    event_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: ExternalEventType
    source: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    affected_entities: list[str] = Field(default_factory=list)
    location: dict[str, float] = Field(default_factory=dict)
    severity: str = "medium"
    description: str = ""
    attributes: dict[str, Any] = Field(default_factory=dict)


class EventEffect:
    """Result of processing an external event."""

    def __init__(self) -> None:
        self.state_updated: bool = False
        self.active_incidents_updated: bool = False
        self.infrastructure_status_updated: bool = False
        self.requires_recalculation: bool = False
        self.updated_entity_ids: list[str] = []
        self.messages: list[str] = []

    def __repr__(self) -> str:
        return (
            f"EventEffect(state_updated={self.state_updated}, "
            f"recalc={self.requires_recalculation}, "
            f"entities={self.updated_entity_ids})"
        )


SEVERITY_LEVELS = {"low": 0, "medium": 1, "high": 2, "critical": 3}

# Events that always trigger COA recalculation
RECALC_TRIGGER_TYPES = {
    ExternalEventType.CABLE_SEVERED,
    ExternalEventType.JAMMING_DETECTED,
    ExternalEventType.HOSTILE_INTENT_OBSERVED,
    ExternalEventType.ASSET_STATUS_CHANGE,
}

# Events that update active incidents
INCIDENT_TYPES = {
    ExternalEventType.CABLE_SEVERED,
    ExternalEventType.HOSTILE_INTENT_OBSERVED,
    ExternalEventType.JAMMING_DETECTED,
}


def process_event(
    event: ExternalEvent,
    active_incidents: list[str] | None = None,
    infrastructure_status: str = "nominal",
) -> EventEffect:
    """Process an external event and compute its effects on scenario state.

    Returns an EventEffect describing what changed. The caller is responsible
    for applying the effects to the actual state store.
    """
    effect = EventEffect()
    incidents = list(active_incidents or [])

    etype = event.event_type

    # Cable severed: add to active incidents, upgrade infrastructure status
    if etype == ExternalEventType.CABLE_SEVERED:
        incident_id = event.attributes.get("cable_name") or event.event_id
        if incident_id not in incidents:
            incidents.append(incident_id)
        effect.infrastructure_status_updated = True
        effect.active_incidents_updated = True
        effect.state_updated = True
        effect.requires_recalculation = True
        effect.messages.append(f"Cable severed: {incident_id}")

    # Jamming: add to incidents, trigger recalc
    elif etype == ExternalEventType.JAMMING_DETECTED:
        incident_id = event.attributes.get("jamming_id") or event.event_id
        if incident_id not in incidents:
            incidents.append(incident_id)
        effect.active_incidents_updated = True
        effect.state_updated = True
        effect.requires_recalculation = True
        effect.messages.append(f"Jamming detected: {incident_id}")

    # Hostile intent: add to incidents, trigger recalc
    elif etype == ExternalEventType.HOSTILE_INTENT_OBSERVED:
        for entity_id in event.affected_entities:
            if entity_id not in incidents:
                incidents.append(entity_id)
        effect.active_incidents_updated = True
        effect.state_updated = True
        effect.requires_recalculation = True
        effect.updated_entity_ids = list(event.affected_entities)
        effect.messages.append(f"Hostile intent observed for: {', '.join(event.affected_entities)}")

    # Vessel course change: update entity context
    elif etype == ExternalEventType.VESSEL_COURSE_CHANGE:
        effect.updated_entity_ids = list(event.affected_entities)
        effect.state_updated = True
        effect.messages.append(f"Course change for: {', '.join(event.affected_entities)}")

    # Satellite confirmation: boost confidence but no incident
    elif etype == ExternalEventType.SATELLITE_CONFIRMATION:
        effect.state_updated = True
        effect.messages.append("Satellite confirmation received")

    # Asset status change: trigger recalc
    elif etype == ExternalEventType.ASSET_STATUS_CHANGE:
        effect.state_updated = True
        effect.requires_recalculation = True
        effect.messages.append("Asset status changed")

    # Other types: mark state updated, selective recalc
    else:
        effect.state_updated = True
        if etype in RECALC_TRIGGER_TYPES:
            effect.requires_recalculation = True

    # Severity-based escalation: high/critical events always trigger recalc
    if SEVERITY_LEVELS.get(event.severity, 0) >= 2:
        effect.requires_recalculation = True

    logger.info(
        "Processed event %s (%s): recalc=%s, incidents_updated=%s",
        event.event_id, etype.value, effect.requires_recalculation, effect.active_incidents_updated,
    )

    return effect
