from __future__ import annotations

import logging
import math
from collections import defaultdict
from datetime import datetime, timezone
from threading import Lock
from typing import Any

from ..core.config import settings
from ..core.constants import EntityType, EventType
from ..core.schemas import (
    AnomalyResult,
    AssetState,
    Contact,
    ContactTrack,
    CourseOfAction,
    EngineState,
    EventSummary,
    Recommendation,
    ScenarioState,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from .asset_state import asset_state_from_inventory

logger = logging.getLogger("coa_engine.engine.state_store")

EARTH_RADIUS_KM = 6371.0
MAX_TRACK_LENGTH = 100


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


class StateStore:
    """Thread-safe state store for the live engine."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._contacts: dict[str, Contact] = {}
        self._tracks: dict[str, ContactTrack] = {}
        self._infrastructure: list[dict[str, Any]] = []
        self._asset_states: dict[str, AssetState] = {}
        self._threats: list[ThreatResult] = []
        self._anomalies: list[AnomalyResult] = []
        self._scored_coas: list[ScoredCOA] = []
        self._recommendation: Recommendation | None = None
        self._simulations: list[SimulationResult] = []
        self._coas: list[CourseOfAction] = []
        self._state = EngineState()
        self._tick = 0
        self._contact_history: list[Contact] = []
        self._max_history = settings.contact_history_max_events
        self._prev_threat_level: str = "LOW"
        self._prev_recommended_coa_id: str | None = None
        self._prev_recommended_roe_status: str | None = None
        self._latest_event_summary: EventSummary | None = None

    @property
    def state(self) -> EngineState:
        with self._lock:
            return self._state.model_copy()

    def _on_state_changed(self) -> None:
        """Hook for subclasses. Called after every state mutation. No-op in base."""

    def set_infrastructure(self, infra: list[dict[str, Any]]) -> None:
        with self._lock:
            self._infrastructure = list(infra)
            self._state.scenario.infrastructure_status = "heightened" if infra else "nominal"
        self._on_state_changed()

    def get_infrastructure(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._infrastructure)

    @staticmethod
    def inventory_to_asset_states(asset_inventory: dict[str, int] | None) -> list[AssetState]:
        if not asset_inventory:
            return []
        return [
            asset_state_from_inventory(asset_id, quantity)
            for asset_id, quantity in sorted(asset_inventory.items())
        ]

    def set_asset_states(
        self,
        asset_states: list[AssetState] | None = None,
        asset_inventory: dict[str, int] | None = None,
    ) -> None:
        states = asset_states or self.inventory_to_asset_states(asset_inventory)
        with self._lock:
            self._asset_states = {state.asset_id: state.model_copy() for state in states}
            self._state.active_asset_types = len(self._asset_states)
            self._state.available_asset_units = sum(
                state.quantity_available for state in self._asset_states.values()
            )
        self._on_state_changed()

    def get_asset_states(self) -> list[AssetState]:
        with self._lock:
            return [state.model_copy() for state in self._asset_states.values()]

    def get_asset_inventory(self) -> dict[str, int]:
        with self._lock:
            return {
                asset_id: state.quantity_available
                for asset_id, state in self._asset_states.items()
            }

    def set_scenario_state(
        self,
        *,
        scenario_id: str | None = None,
        scenario_name: str | None = None,
        mode: str | None = None,
        infrastructure_status: str | None = None,
        active_incidents: list[str] | None = None,
        seed: int | None = None,
        timing_jitter: int | None = None,
        position_jitter: float | None = None,
        environment: dict[str, Any] | None = None,
        upcoming_stimuli_count: int | None = None,
        active_stimuli_count: int | None = None,
        fired_stimuli_count: int | None = None,
    ) -> None:
        with self._lock:
            current = self._state.scenario
            self._state.scenario = current.model_copy(update={
                "scenario_id": scenario_id if scenario_id is not None else current.scenario_id,
                "scenario_name": scenario_name if scenario_name is not None else current.scenario_name,
                "mode": mode if mode is not None else current.mode,
                "infrastructure_status": (
                    infrastructure_status if infrastructure_status is not None else current.infrastructure_status
                ),
                "active_incidents": list(active_incidents) if active_incidents is not None else current.active_incidents,
                "last_updated": datetime.now(timezone.utc),
                "seed": seed if seed is not None else current.seed,
                "timing_jitter": timing_jitter if timing_jitter is not None else current.timing_jitter,
                "position_jitter": position_jitter if position_jitter is not None else current.position_jitter,
                "environment": environment if environment is not None else current.environment,
                "upcoming_stimuli_count": upcoming_stimuli_count if upcoming_stimuli_count is not None else current.upcoming_stimuli_count,
                "active_stimuli_count": active_stimuli_count if active_stimuli_count is not None else current.active_stimuli_count,
                "fired_stimuli_count": fired_stimuli_count if fired_stimuli_count is not None else current.fired_stimuli_count,
            })
        self._on_state_changed()

    def set_ui_language(self, language: str) -> None:
        with self._lock:
            self._state.ui_language = language
        self._on_state_changed()

    def get_ui_language(self) -> str:
        with self._lock:
            return self._state.ui_language or "en"

    def set_combat_contact_state(
        self,
        *,
        enabled: bool | None = None,
        density: str | None = None,
        scenario_type: str | None = None,
    ) -> None:
        with self._lock:
            current = self._state.scenario
            self._state.scenario = current.model_copy(update={
                "combat_contacts_enabled": enabled if enabled is not None else current.combat_contacts_enabled,
                "combat_contacts_density": density if density is not None else current.combat_contacts_density,
                "combat_contacts_scenario_type": scenario_type if scenario_type is not None else current.combat_contacts_scenario_type,
                "combat_contacts_last_update": datetime.now(timezone.utc),
            })
        self._on_state_changed()

    def get_combat_contact_state(self) -> dict[str, Any]:
        with self._lock:
            scenario = self._state.scenario
            return {
                "enabled": scenario.combat_contacts_enabled,
                "density": scenario.combat_contacts_density,
                "scenario_type": scenario.combat_contacts_scenario_type,
                "last_update": scenario.combat_contacts_last_update,
            }

    # ---- Contacts ----

    def ingest_contact(self, contact: Contact) -> bool:
        """Ingest a contact, update tracks. Returns True if state changed meaningfully."""
        with self._lock:
            self._contacts[contact.entity_id] = contact
            self._contact_history.append(contact)
            if len(self._contact_history) > self._max_history:
                self._contact_history = self._contact_history[-self._max_history:]

            track = self._tracks.get(contact.entity_id)
            if track is None:
                track = ContactTrack(entity_id=contact.entity_id)
                self._tracks[contact.entity_id] = track
            track.positions.append((contact.timestamp, contact.lat, contact.lon))
            track.speeds.append(contact.speed)
            track.headings.append(contact.heading)
            track.last_contact = contact.timestamp
            if len(track.positions) > MAX_TRACK_LENGTH:
                track.positions = track.positions[-MAX_TRACK_LENGTH:]
                track.speeds = track.speeds[-MAX_TRACK_LENGTH:]
                track.headings = track.headings[-MAX_TRACK_LENGTH:]

            # Detect loitering
            if len(track.speeds) >= 3:
                recent_speeds = track.speeds[-5:]
                track.is_loitering = sum(s <= 1.5 for s in recent_speeds) >= len(recent_speeds) * 0.5

            # Detect heading toward infrastructure
            track.heading_toward_infra = self._heading_toward_infra(contact)

            self._state.contacts_processed += 1
            self._state.active_contacts = len(self._contacts)
            self._state.active_tracks = len(self._tracks)

            sig = self._is_significant(contact, track)
        self._on_state_changed()
        return sig

    def _heading_toward_infra(self, contact: Contact) -> bool:
        if not self._infrastructure or contact.heading is None:
            return False
        for infra in self._infrastructure:
            dlat = infra["lat"] - contact.lat
            dlon = infra["lon"] - contact.lon
            bearing = math.degrees(math.atan2(dlon, dlat)) % 360
            diff = abs(bearing - contact.heading)
            if diff > 180:
                diff = 360 - diff
            if diff < 30:
                return True
        return False

    def _is_significant(self, contact: Contact, track: ContactTrack) -> bool:
        """Determine if this contact should trigger a recalculation."""
        if contact.is_hostile:
            return True
        if track.heading_toward_infra:
            return True
        if track.is_loitering and contact.contact_type in ("vessel", "submarine"):
            return True
        if contact.contact_type in ("cable_event", "jamming"):
            return True
        if contact.speed > 12.0 and contact.is_hostile:
            return True
        return False

    def get_contacts(self) -> list[Contact]:
        with self._lock:
            return list(self._contacts.values())

    def get_contact(self, entity_id: str) -> Contact | None:
        with self._lock:
            contact = self._contacts.get(entity_id)
            return contact.model_copy() if contact else None

    def remove_contact(self, entity_id: str) -> bool:
        with self._lock:
            removed = self._contacts.pop(entity_id, None) is not None
            self._tracks.pop(entity_id, None)
            if removed:
                self._state.active_contacts = len(self._contacts)
                self._state.active_tracks = len(self._tracks)
        if removed:
            self._on_state_changed()
        return removed

    def get_tracks(self) -> dict[str, ContactTrack]:
        with self._lock:
            return {k: v.model_copy() for k, v in self._tracks.items()}

    def get_history(self, limit: int = 100) -> list[Contact]:
        with self._lock:
            return list(self._contact_history[-limit:])

    @staticmethod
    def _contact_to_operational_event(contact: Contact):
        """Normalize a contact into an OperationalEvent for downstream analysis."""
        from ..core.schemas import OperationalEvent

        type_value = contact.contact_type.value
        attrs = dict(contact.attributes)
        allegiance = str(attrs.get("allegiance", "")).lower()
        friendly_contact = allegiance in ("friendly", "blue") or (
            not contact.is_hostile and attrs.get("role") in {"allied", "isr", "support"}
        )
        neutral_contact = allegiance == "neutral"
        friendly_uav = type_value == "uav" and (
            friendly_contact or attrs.get("role") in {"isr", "support"}
        )

        type_map = {
            "uav": EventType.UAV_DETECTION,
            "convoy": EventType.CONVOY_SIGHTING,
            "jamming": EventType.JAMMING_DETECTED,
            "cable_event": EventType.CABLE_SEVERANCE,
            "sigint": EventType.OPERATIONAL_REPORT,
        }
        entity_type_map = {
            "uav": EntityType.UAV,
            "convoy": EntityType.CONVOY,
            "submarine": EntityType.SUSPICIOUS_VESSEL,
        }

        if type_value in {"vessel", "submarine"}:
            if attrs.get("course_change") or attrs.get("suspicious_maneuver"):
                event_type = EventType.VESSEL_COURSE_CHANGE
            else:
                event_type = EventType.VESSEL_POSITION
        elif friendly_uav:
            event_type = EventType.OPERATIONAL_REPORT
        else:
            event_type = type_map.get(type_value, EventType.OPERATIONAL_REPORT)

        entity_type = entity_type_map.get(type_value, EntityType.SUSPICIOUS_VESSEL)
        allegiance = attrs.get("allegiance", "")
        is_infrastructure = type_value == "infrastructure"
        is_threat_candidate = True

        if friendly_uav:
            entity_type = EntityType.ISR_ASSET
            is_threat_candidate = False
        elif type_value == "vessel" and friendly_contact and not neutral_contact:
            entity_type = EntityType.ALLIED_VESSEL
            is_threat_candidate = False
        elif is_infrastructure:
            entity_type = EntityType.INFRASTRUCTURE
            is_threat_candidate = False
        elif neutral_contact:
            entity_type = EntityType.NEUTRAL_VESSEL
            is_threat_candidate = False

        return OperationalEvent(
            event_id=contact.contact_id,
            timestamp=contact.timestamp,
            event_type=event_type,
            source=contact.source,
            confidence=contact.confidence,
            lat=contact.lat,
            lon=contact.lon,
            entity_id=contact.entity_id,
            entity_type=entity_type,
            description=attrs.get("description") or f"{type_value} contact from {contact.source}",
            attributes={
                "speed_knots": contact.speed,
                "heading": contact.heading,
                **attrs,
            },
            allegiance=allegiance,
            is_threat_candidate=is_threat_candidate,
            is_infrastructure=is_infrastructure,
        )

    def contacts_as_events(self):
        """Convert the active contact snapshot into OperationalEvents."""
        return [self._contact_to_operational_event(c) for c in self.get_contacts()]

    def contact_history_as_events(self, limit: int | None = None):
        """Convert the append-only contact history into OperationalEvents."""
        history = self.get_history(limit or self._max_history)
        return [self._contact_to_operational_event(c) for c in history]

    # ---- Analysis results ----

    def update_analysis(
        self,
        threats: list[ThreatResult],
        anomalies: list[AnomalyResult],
        scored: list[ScoredCOA],
        recommendation: Recommendation,
        coas: list[CourseOfAction],
        simulations: list[SimulationResult],
    ) -> tuple[bool, bool, bool]:
        """Update analysis state. Returns (threat_changed, coa_changed, roe_changed)."""
        with self._lock:
            self._threats = threats
            self._anomalies = anomalies
            self._scored_coas = scored
            self._recommendation = recommendation
            self._coas = coas
            self._simulations = simulations

            # Detect threat level change
            new_level = "LOW"
            new_prob = 0.0
            new_entity = None
            if threats:
                new_level = threats[0].threat_level.value
                new_prob = threats[0].threat_probability
                new_entity = threats[0].entity_id
            threat_changed = new_level != self._prev_threat_level
            self._prev_threat_level = new_level

            # Detect COA rank change
            new_coa_id = recommendation.recommended.coa.coa_id if recommendation.recommended else None
            new_coa_score = recommendation.recommended.total_score if recommendation.recommended else 0.0
            coa_changed = new_coa_id != self._prev_recommended_coa_id
            self._prev_recommended_coa_id = new_coa_id
            new_roe_status = recommendation.recommended.coa.roe_status if recommendation.recommended else None
            roe_changed = new_roe_status != self._prev_recommended_roe_status
            self._prev_recommended_roe_status = new_roe_status

            self._state.current_threat_level = new_level
            self._state.top_threat_entity = new_entity
            self._state.top_threat_probability = new_prob
            self._state.recommended_coa_id = new_coa_id
            self._state.recommended_coa_score = new_coa_score
            self._state.scenario = self._state.scenario.model_copy(update={
                "active_incidents": [t.entity_id for t in threats[:5]],
                "last_updated": datetime.now(timezone.utc),
            })

        self._on_state_changed()
        return threat_changed, coa_changed, roe_changed

    def get_threats(self) -> list[ThreatResult]:
        with self._lock:
            return list(self._threats)

    def get_anomalies(self) -> list[AnomalyResult]:
        with self._lock:
            return list(self._anomalies)

    def get_scored_coas(self) -> list[ScoredCOA]:
        with self._lock:
            return list(self._scored_coas)

    def get_recommendation(self) -> Recommendation | None:
        with self._lock:
            return self._recommendation

    def update_recommendation(self, recommendation: Recommendation) -> None:
        with self._lock:
            self._recommendation = recommendation
        self._on_state_changed()

    def set_latest_event_summary(self, summary: EventSummary) -> None:
        with self._lock:
            self._latest_event_summary = summary.model_copy()
        self._on_state_changed()

    def get_latest_event_summary(self) -> EventSummary | None:
        with self._lock:
            return self._latest_event_summary.model_copy() if self._latest_event_summary else None

    def advance_tick(self) -> int:
        with self._lock:
            self._tick += 1
            self._state.tick = self._tick
            tick = self._tick
        self._on_state_changed()
        return tick

    def mark_analysis_completed(self, tick: int) -> None:
        with self._lock:
            self._state.last_analysis_tick = tick

    def get_tick(self) -> int:
        with self._lock:
            return self._tick

    def clear(self) -> None:
        with self._lock:
            self._contacts.clear()
            self._tracks.clear()
            self._asset_states.clear()
            self._threats.clear()
            self._anomalies.clear()
            self._scored_coas.clear()
            self._coas.clear()
            self._simulations.clear()
            self._contact_history.clear()
            self._recommendation = None
            self._state = EngineState()
            self._tick = 0
            self._prev_threat_level = "LOW"
            self._prev_recommended_coa_id = None
            self._prev_recommended_roe_status = None
            self._latest_event_summary = None
        self._on_state_changed()


_store: StateStore | None = None


def get_state_store() -> StateStore:
    global _store
    if _store is None:
        _store = StateStore()
    return _store
