from __future__ import annotations

import logging
import math
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from ..core.config import settings
from ..core.schemas import Contact, ContactType, ContactUpdateRequest, EngineActionRequest
from .behavior_models import BehaviorContext, make_policy
from .combat_contact_generator import CombatContactGenerator
from .contact_enrichment import enrich_contact
from .event_bus import Event, EventKind, get_event_bus
from .geo_validation import clamp_wgs84
from .scenario_generator import ScenarioGenerator, ScenarioTemplate
from .state_store import get_state_store

logger = logging.getLogger("coa_engine.engine.contact_engine")


class EngineMode(str, Enum):
    SIMULATION = "simulation"
    HYBRID = "hybrid"
    LIVE = "live"


class SimulationScenario:
    """Generates synthetic contacts that evolve over time.

    Initialized from a ScenarioTemplate — the single source of truth for
    entities, stimuli, bounds, and environment.
    """

    def __init__(self, template: ScenarioTemplate) -> None:
        self.scenario_id = template.scenario_id
        self._template = template
        self.entities: dict[str, dict[str, Any]] = {}
        self.tick = 0
        self._triggers: list[dict[str, Any]] = []
        self._triggered: set[str] = set()
        self._bounds: dict[str, float] | None = template.bounds
        self._policies: dict[str, Any] = {}
        self._active_stimuli: list[str] = []
        self._fired_stimuli: list[dict[str, Any]] = []
        self._scenario_template = template
        self._init_from_template(template)

    def upsert_entity(self, entity_id: str, entity: dict[str, Any]) -> None:
        self.entities[entity_id] = entity

    def remove_entity(self, entity_id: str) -> None:
        self.entities.pop(entity_id, None)
        self._triggers = [trigger for trigger in self._triggers if trigger.get("entity") != entity_id]

    def update_entity(self, entity_id: str, updates: ContactUpdateRequest) -> dict[str, Any]:
        if entity_id not in self.entities:
            raise KeyError(entity_id)
        ent = self.entities[entity_id]
        if updates.name is not None:
            ent["name"] = updates.name
        if updates.contact_type is not None:
            ent["type"] = updates.contact_type
        if updates.is_hostile is not None:
            ent["hostile"] = updates.is_hostile
        if updates.lat is not None:
            ent["lat"] = updates.lat
        if updates.lon is not None:
            ent["lon"] = updates.lon
        ent["lat"], ent["lon"] = clamp_wgs84(float(ent["lat"]), float(ent["lon"]))
        if updates.speed is not None:
            ent["speed"] = updates.speed
        if updates.heading is not None:
            ent["heading"] = updates.heading % 360
        if updates.attributes:
            for key, value in updates.attributes.items():
                ent[key] = value
        return ent

    def schedule_action(self, action: EngineActionRequest) -> dict[str, Any]:
        execute_tick = action.execute_tick if action.execute_tick is not None else self.tick + 1
        trigger = {
            "tick": max(execute_tick, self.tick + 1),
            "entity": action.entity_id,
            "action": action.action,
            "lat": action.lat,
            "lon": action.lon,
            "new_heading": action.new_heading,
            "new_speed": action.new_speed,
            "radius_nm": action.radius_nm,
            "attributes": dict(action.attributes),
        }
        self._triggers.append(trigger)
        self._triggers.sort(key=lambda item: int(item.get("tick", 0)))
        return trigger

    def _init_from_template(self, template: ScenarioTemplate) -> None:
        """Load entities and stimuli from a ScenarioTemplate."""
        self._triggers = [s.to_trigger() for s in template.stimuli]

        for spec in template.entities:
            eid = spec.entity_id
            self.entities[eid] = {
                "name": spec.name,
                "type": ContactType(spec.type),
                "hostile": spec.hostile,
                "lat": spec.lat,
                "lon": spec.lon,
                "speed": spec.speed,
                "heading": spec.heading,
                "flag": spec.flag,
                "allegiance": spec.allegiance,
            }
            if spec.behavior_policy:
                self._policies[eid] = make_policy(spec.behavior_policy, **spec.behavior_params)

    def tick_forward(self) -> list[Contact]:
        """Advance one tick and generate contacts for all entities."""
        self.tick += 1
        now = datetime.now(timezone.utc)
        contacts: list[Contact] = []

        # Process scheduled triggers (stimuli)
        self._active_stimuli = []
        for trigger in self._triggers:
            t_tick = trigger["tick"]
            t_key = f"{t_tick}:{trigger.get('action', '')}"
            if t_tick == self.tick and t_key not in self._triggered:
                self._triggered.add(t_key)
                contacts.append(self._create_trigger_contact(trigger, now))
                if trigger["action"] in ("cable_severance", "jamming"):
                    self._active_stimuli.append(trigger["action"])
                self._fired_stimuli.append({
                    "tick": self.tick,
                    **trigger,
                })
                self._process_trigger_as_event(trigger, now)

        self._update_stimuli_counts()

        store = get_state_store()
        historical_contacts = [
            {
                "entity_id": contact.entity_id,
                "lat": contact.lat,
                "lon": contact.lon,
                "is_hostile": contact.is_hostile,
                "type": contact.contact_type.value if hasattr(contact.contact_type, "value") else str(contact.contact_type),
                "contact_type": contact.contact_type.value if hasattr(contact.contact_type, "value") else str(contact.contact_type),
            }
            for contact in store.get_contacts()
        ]
        trigger_contacts = [
            {
                "entity_id": contact.entity_id,
                "lat": contact.lat,
                "lon": contact.lon,
                "is_hostile": contact.is_hostile,
                "type": contact.contact_type.value if hasattr(contact.contact_type, "value") else str(contact.contact_type),
                "contact_type": contact.contact_type.value if hasattr(contact.contact_type, "value") else str(contact.contact_type),
            }
            for contact in contacts
        ]
        priority_targets = []
        for target in store.get_targets()[:3]:
            target_contact = store.get_contact(target.id)
            if target_contact is None:
                continue
            priority_targets.append({
                "entity_id": target.id,
                "priority_level": target.priority_level,
                "lat": target_contact.lat,
                "lon": target_contact.lon,
            })

        # Build behavior context for this tick
        ctx = BehaviorContext(
            tick=self.tick,
            infrastructure=self._get_infrastructure(),
            contacts=[
                {"entity_id": eid, "lat": e["lat"], "lon": e["lon"], "is_hostile": e["hostile"], "type": e["type"].value if hasattr(e["type"], "value") else str(e["type"])}
                for eid, e in self.entities.items()
            ] + historical_contacts + trigger_contacts,
            active_stimuli=list(self._active_stimuli),
            active_incidents=list(store.state.scenario.active_incidents),
            priority_targets=priority_targets,
            scenario_bounds=self._bounds,
        )

        # Generate position contacts for all entities
        for eid, ent in self.entities.items():
            policy = self._policies.get(eid)
            if policy:
                result = policy(ent, ctx, rng_state=self.tick)
                ent["lat"] = result.lat
                ent["lon"] = result.lon
                ent["speed"] = result.speed
                ent["heading"] = result.heading
                # Preserve internal state attributes (e.g. _bhv_diverted, _bhv_wp_idx)
                for k, v in result.attributes.items():
                    if k.startswith("_bhv_"):
                        ent[k] = v
                attrs = {
                    "name": ent.get("name", eid),
                    "flag": ent.get("flag", "unknown"),
                    "ais_off": bool(ent.get("ais_off", False)),
                    "allegiance": ent.get("allegiance", ""),
                }
                attrs.update({k: v for k, v in result.attributes.items() if not k.startswith("_bhv_")})
            else:
                # Static / legacy movement
                self._move_entity(ent)
                attrs = {
                    "name": ent.get("name", eid),
                    "flag": ent.get("flag", "unknown"),
                    "ais_off": bool(ent.get("ais_off", False)),
                    "allegiance": ent.get("allegiance", ""),
                }

            contacts.append(Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=now,
                source="simulation",
                contact_type=ent["type"],
                lat=round(ent["lat"], 4),
                lon=round(ent["lon"], 4),
                speed=round(ent["speed"], 1),
                heading=round(ent["heading"], 1),
                confidence=0.85 if ent["hostile"] else 0.95,
                entity_id=eid,
                is_hostile=ent["hostile"],
                attributes=attrs,
            ))

        return contacts

    @property
    def scenario_metadata(self) -> dict[str, Any]:
        if self._scenario_template is not None:
            return self._scenario_template.metadata
        return {"scenario_id": self.scenario_id}

    @property
    def upcoming_stimuli(self) -> list[dict[str, Any]]:
        if self._scenario_template is None:
            return []
        return [s.to_trigger() for s in self._scenario_template.upcoming_stimuli(self.tick)]

    @property
    def active_stimuli_list(self) -> list[dict[str, Any]]:
        if self._scenario_template is None:
            return []
        return [s.to_trigger() for s in self._scenario_template.active_stimuli(self.tick)]

    @property
    def fired_stimuli_list(self) -> list[dict[str, Any]]:
        return list(self._fired_stimuli)

    def _process_trigger_as_event(self, trigger: dict[str, Any], ts: datetime) -> None:
        """Propagate a fired stimulus through event_engine for state tracking."""
        from .event_engine import ExternalEvent, ExternalEventType, process_event

        store = get_state_store()
        action = trigger.get("action", "")

        event_type_map = {
            "cable_severance": ExternalEventType.CABLE_SEVERED,
            "jamming": ExternalEventType.JAMMING_DETECTED,
            "course_change": ExternalEventType.VESSEL_COURSE_CHANGE,
            "slow_near_cable": ExternalEventType.VESSEL_COURSE_CHANGE,
            "suspicious_maneuver": ExternalEventType.VESSEL_COURSE_CHANGE,
        }
        etype = event_type_map.get(action)
        if etype is None:
            return

        attributes: dict[str, Any] = {}
        if action == "cable_severance":
            attributes["cable_name"] = f"cable_{trigger.get('lat', 0)}_{trigger.get('lon', 0)}"
        elif action == "jamming":
            attributes["jamming_id"] = f"jam_{trigger.get('lat', 0)}_{trigger.get('lon', 0)}"

        event = ExternalEvent(
            event_id=f"STIM-{self.tick}-{action}",
            timestamp=ts,
            event_type=etype,
            source="simulation_stimulus",
            affected_entities=[trigger["entity"]] if trigger.get("entity") else [],
            location={"lat": trigger.get("lat", 0.0), "lon": trigger.get("lon", 0.0)},
            severity="high" if action in ("cable_severance", "jamming") else "medium",
            attributes=attributes,
        )

        effect = process_event(
            event,
            active_incidents=store.state.scenario.active_incidents,
            infrastructure_status=store.state.scenario.infrastructure_status,
        )

        if effect.active_incidents_updated or effect.infrastructure_status_updated:
            incidents = list(store.state.scenario.active_incidents)
            incident_id = attributes.get("cable_name") or attributes.get("jamming_id") or event.event_id
            if incident_id not in incidents:
                incidents.append(incident_id)
            store.set_scenario_state(
                active_incidents=incidents,
                infrastructure_status="compromised" if action == "cable_severance" else "heightened",
            )

    def _update_stimuli_counts(self) -> None:
        store = get_state_store()
        store.set_scenario_state(
            upcoming_stimuli_count=len(self.upcoming_stimuli),
            active_stimuli_count=len(self.active_stimuli_list),
            fired_stimuli_count=len(self._fired_stimuli),
        )

    def _get_infrastructure(self) -> list[dict[str, Any]]:
        """Get infrastructure list from the state store, or fall back to constants."""
        store = get_state_store()
        infra = store.get_infrastructure()
        if infra:
            return infra
        from ..core.constants import CRITICAL_INFRASTRUCTURE
        return CRITICAL_INFRASTRUCTURE

    def _move_entity(self, ent: dict[str, Any]) -> None:
        """Move an entity along its heading at its speed, clamped to scenario bounds."""
        target_lat = ent.get("target_lat")
        target_lon = ent.get("target_lon")
        if target_lat is not None and target_lon is not None:
            dlat_to_target = target_lat - ent["lat"]
            dlon_to_target = target_lon - ent["lon"]
            ent["heading"] = math.degrees(math.atan2(dlon_to_target, dlat_to_target)) % 360
        speed = ent.get("speed", 0.0)
        heading = ent.get("heading", 0.0)
        # 1 tick ≈ 2 minutes of simulation time
        dt_hours = 2.0 / 60.0
        dist_nm = speed * dt_hours
        dist_km = dist_nm * 1.852
        heading_rad = math.radians(heading)
        dlat = dist_km * math.cos(heading_rad) / 111.0
        dlon = dist_km * math.sin(heading_rad) / (111.0 * math.cos(math.radians(ent["lat"])))
        ent["lat"] = ent["lat"] + dlat
        ent["lon"] = ent["lon"] + dlon
        ent["lat"], ent["lon"] = clamp_wgs84(float(ent["lat"]), float(ent["lon"]))
        # Clamp to scenario bounds
        if self._bounds:
            ent["lat"] = max(self._bounds["lat_min"], min(self._bounds["lat_max"], ent["lat"]))
            ent["lon"] = max(self._bounds["lon_min"], min(self._bounds["lon_max"], ent["lon"]))
        if target_lat is not None and target_lon is not None:
            distance_remaining = math.hypot(target_lat - ent["lat"], target_lon - ent["lon"])
            if distance_remaining < 0.03:
                ent["lat"] = target_lat
                ent["lon"] = target_lon
                ent.pop("target_lat", None)
                ent.pop("target_lon", None)

    @staticmethod
    def _resolve_numeric(value: Any, fallback: float) -> float:
        """Preserve the existing value when a trigger explicitly passes null."""
        return fallback if value is None else float(value)

    def _create_trigger_contact(self, trigger: dict[str, Any], ts: datetime) -> Contact:
        action = trigger["action"]
        if action == "cable_severance":
            return Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=ts, source="simulation",
                contact_type=ContactType.CABLE_EVENT,
                lat=trigger["lat"], lon=trigger["lon"],
                speed=0.0, heading=0.0, confidence=0.95,
                entity_id="CABLE-EVENT-001", is_hostile=True,
                attributes={"description": "Cable signal loss — fiber cut confirmed"},
            )
        elif action == "jamming":
            return Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=ts, source="simulation",
                contact_type=ContactType.JAMMING,
                lat=trigger["lat"], lon=trigger["lon"],
                speed=0.0, heading=0.0, confidence=0.85,
                entity_id="JAM-001", is_hostile=True,
                attributes={"radius_nm": trigger.get("radius_nm", 20), "band": "L-band+VHF"},
            )
        elif action in ("course_change", "slow_near_cable"):
            eid = trigger["entity"]
            ent = self.entities.get(eid, {})
            new_h = self._resolve_numeric(trigger.get("new_heading"), ent.get("heading", 0.0))
            new_s = self._resolve_numeric(trigger.get("new_speed"), ent.get("speed", 0.0))
            ent["heading"] = new_h
            ent["speed"] = new_s
            return Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=ts, source="simulation",
                contact_type=ent.get("type", ContactType.VESSEL),
                lat=ent["lat"], lon=ent["lon"],
                speed=new_s, heading=new_h, confidence=0.80,
                entity_id=eid, is_hostile=ent.get("hostile", False),
                attributes={"name": ent.get("name", eid), "course_change": True},
            )
        elif action == "suspicious_maneuver":
            eid = trigger["entity"]
            ent = self.entities.get(eid, {})
            new_h = self._resolve_numeric(trigger.get("new_heading"), ent.get("heading", 0.0))
            new_s = self._resolve_numeric(trigger.get("new_speed"), ent.get("speed", 0.0))
            ent["heading"] = new_h
            ent["speed"] = new_s
            return Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=ts, source="simulation",
                contact_type=ent.get("type", ContactType.VESSEL),
                lat=ent["lat"], lon=ent["lon"],
                speed=new_s, heading=new_h, confidence=0.88,
                entity_id=eid, is_hostile=ent.get("hostile", False),
                attributes={
                    "name": ent.get("name", eid),
                    "suspicious_maneuver": True,
                    "ais_off": ent.get("ais_off", False),
                },
            )
        elif action == "approach_point":
            eid = trigger["entity"]
            ent = self.entities.get(eid, {})
            ent["target_lat"] = trigger.get("lat")
            ent["target_lon"] = trigger.get("lon")
            if trigger.get("new_speed") is not None:
                ent["speed"] = trigger["new_speed"]
            return Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=ts, source="simulation",
                contact_type=ent.get("type", ContactType.VESSEL),
                lat=ent["lat"], lon=ent["lon"],
                speed=ent.get("speed", 0.0), heading=ent.get("heading", 0.0), confidence=0.82,
                entity_id=eid, is_hostile=ent.get("hostile", False),
                attributes={
                    "name": ent.get("name", eid),
                    "task": "approach_point",
                    "target_lat": trigger.get("lat"),
                    "target_lon": trigger.get("lon"),
                },
            )
        elif action == "speed_burst":
            eid = trigger["entity"]
            ent = self.entities.get(eid, {})
            ent["speed"] = self._resolve_numeric(trigger.get("new_speed"), ent.get("speed", 0.0))
            return Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=ts, source="simulation",
                contact_type=ent.get("type", ContactType.VESSEL),
                lat=ent["lat"], lon=ent["lon"],
                speed=ent["speed"], heading=ent.get("heading", 0.0), confidence=0.81,
                entity_id=eid, is_hostile=ent.get("hostile", False),
                attributes={"name": ent.get("name", eid), "speed_burst": True},
            )
        elif action == "ais_off":
            eid = trigger["entity"]
            ent = self.entities.get(eid, {})
            ent["ais_off"] = True
            return Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=ts, source="simulation",
                contact_type=ent.get("type", ContactType.VESSEL),
                lat=ent["lat"], lon=ent["lon"],
                speed=ent.get("speed", 0.0), heading=ent.get("heading", 0.0), confidence=0.76,
                entity_id=eid, is_hostile=ent.get("hostile", False),
                attributes={"name": ent.get("name", eid), "ais_off": True},
            )
        elif action == "attack_run":
            eid = trigger.get("entity") or "ATTACK-001"
            ent = self.entities.get(eid, {})
            lat = trigger.get("lat", ent.get("lat", 0.0))
            lon = trigger.get("lon", ent.get("lon", 0.0))
            return Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=ts, source="simulation",
                contact_type=ContactType.SIGINT,
                lat=lat, lon=lon,
                speed=ent.get("speed", 0.0), heading=ent.get("heading", 0.0), confidence=0.74,
                entity_id=eid, is_hostile=ent.get("hostile", True),
                attributes={"name": ent.get("name", eid), "activity": "attack_run"},
            )
        elif action == "reposition":
            eid = trigger["entity"]
            ent = self.entities.get(eid, {})
            ent["lat"] = trigger["lat"]
            ent["lon"] = trigger["lon"]
            ent["lat"], ent["lon"] = clamp_wgs84(float(ent["lat"]), float(ent["lon"]))
            ent["speed"] = self._resolve_numeric(trigger.get("new_speed"), ent.get("speed", 0.0))
            return Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=ts, source="simulation",
                contact_type=ent.get("type", ContactType.UAV),
                lat=trigger["lat"], lon=trigger["lon"],
                speed=ent["speed"], heading=ent.get("heading", 0.0),
                confidence=0.75, entity_id=eid, is_hostile=ent.get("hostile", False),
                attributes={"name": ent.get("name", eid)},
            )
        elif action == "surface":
            eid = trigger["entity"]
            ent = self.entities.get(eid, {})
            ent["speed"] = self._resolve_numeric(trigger.get("new_speed"), ent.get("speed", 2.0))
            ent["type"] = ContactType.VESSEL  # submarine surfaces
            return Contact(
                contact_id=f"C-{uuid.uuid4().hex[:8]}",
                timestamp=ts, source="simulation",
                contact_type=ContactType.SUBMARINE,
                lat=ent["lat"], lon=ent["lon"],
                speed=ent["speed"], heading=ent.get("heading", 0.0),
                confidence=0.70, entity_id=eid, is_hostile=True,
                attributes={"name": ent.get("name", eid), "surfaced": True},
            )
        return Contact(
            contact_id=f"C-{uuid.uuid4().hex[:8]}", timestamp=ts,
            source="simulation", contact_type=ContactType.UNKNOWN,
            lat=0.0, lon=0.0, entity_id="UNKNOWN",
            attributes={"action": action},
        )


class ContactEngine:
    """Main contact ingestion engine with 3 modes."""

    def __init__(self) -> None:
        self.mode = EngineMode.SIMULATION
        self._sim: SimulationScenario | None = None
        self._combat = CombatContactGenerator(seed=settings.simulation_seed)
        self._running = False
        self._store = get_state_store()
        self._bus = get_event_bus()

    def set_mode(self, mode: EngineMode) -> None:
        self.mode = mode
        self._store.set_scenario_state(mode=mode.value)
        logger.info("Contact engine mode: %s", mode.value)

    def load_scenario(self, scenario_id: str, template: ScenarioTemplate | None = None) -> None:
        if template is None:
            template = ScenarioGenerator(seed=settings.simulation_seed).generate(scenario_id)
        self._sim = SimulationScenario(template)
        self._combat.reset(seed=template.seed)
        # Seed infrastructure into state store
        from .event_ingestion import load_scenario
        try:
            scenario = load_scenario(scenario_id)
            self._store.set_infrastructure(
                [ci.model_dump() for ci in scenario.critical_infrastructure]
            )
            infra_status = "heightened" if scenario.critical_infrastructure else "nominal"
        except (ValueError, FileNotFoundError):
            infra_status = "nominal"
        self._store.set_scenario_state(
            scenario_id=template.scenario_id,
            scenario_name=template.display_name,
            mode=self.mode.value,
            infrastructure_status=infra_status,
            seed=template.seed,
            environment=template.environment,
            upcoming_stimuli_count=len(template.upcoming_stimuli(0)),
            active_stimuli_count=0,
            fired_stimuli_count=0,
        )
        # Seed initial contacts
        for eid, ent in self._sim.entities.items():
            contact = Contact(
                contact_id=f"C-seed-{eid}",
                timestamp=datetime.now(timezone.utc),
                source="simulation",
                contact_type=ent["type"],
                lat=ent["lat"], lon=ent["lon"],
                speed=ent["speed"], heading=ent["heading"],
                confidence=0.85 if ent["hostile"] else 0.95,
                entity_id=eid,
                is_hostile=ent["hostile"],
                attributes={
                    "name": ent.get("name", eid),
                    "ais_off": bool(ent.get("ais_off", False)),
                    "allegiance": ent.get("allegiance", "hostile" if ent["hostile"] else "friendly"),
                    "behavior_mode": "",
                },
            )
            self._store.ingest_contact(contact)
        logger.info("Loaded scenario %s with %d entities", scenario_id, len(self._sim.entities))

    def tick(self) -> list[Contact]:
        """Process one tick. Returns enriched contacts."""
        contacts: list[Contact] = []

        if self.mode == EngineMode.SIMULATION and self._sim:
            contacts = self._sim.tick_forward()
        elif self.mode == EngineMode.HYBRID and self._sim:
            contacts = self._sim.tick_forward()

        combat_state = self._store.get_combat_contact_state()
        scenario_state = self._store.state.scenario
        self._combat.configure(
            enabled=bool(combat_state.get("enabled", False)),
            density=str(combat_state.get("density", "medium")),
            scenario_type=str(combat_state.get("scenario_type", "mixed_traffic")),
            seed=scenario_state.seed if scenario_state.seed is not None else settings.simulation_seed,
        )
        if self._combat.enabled and self._sim is not None and self._sim._bounds is not None:
            combat_contacts = self._combat.generate(
                tick=self._store.get_tick() + 1,
                scenario_bounds=self._sim._bounds,
                infrastructure=self._store.get_infrastructure(),
            )
            contacts.extend(combat_contacts)

        infrastructure = self._store.get_infrastructure()
        tracks = self._store.get_tracks()
        significant = False

        for contact in contacts:
            # 1) Ingest into state store (creates track)
            sig = self._store.ingest_contact(contact)
            if sig:
                significant = True

            # 2) Enrich: distance to infra, heading-toward, loitering
            updated_track = self._store.get_tracks().get(contact.entity_id)
            enriched = enrich_contact(contact, updated_track, infrastructure)

            # 3) Publish enriched contact to event bus
            self._bus.publish(Event(
                kind=EventKind.CONTACT_RECEIVED,
                payload=enriched,
                tick=self._store.get_tick(),
            ))

        if significant:
            logger.info("Tick %d: significant contact detected", self._store.get_tick())

        return contacts

    def inject_contact(self, contact: Contact) -> bool:
        """Manually inject a contact (for hybrid/live mode). Persists in simulation."""
        sig = self._store.ingest_contact(contact)
        infrastructure = self._store.get_infrastructure()
        track = self._store.get_tracks().get(contact.entity_id)
        enriched = enrich_contact(contact, track, infrastructure)
        self._bus.publish(Event(
            kind=EventKind.CONTACT_RECEIVED,
            payload=enriched,
            tick=self._store.get_tick(),
        ))
        # Add to simulation entities so injected units move on future ticks
        if self._sim is not None and contact.source not in ("aishub", "noaa_replay", "combat_system") and contact.contact_type not in (
            ContactType.INFRASTRUCTURE, ContactType.JAMMING, ContactType.CABLE_EVENT,
        ):
            self._sim.upsert_entity(contact.entity_id, {
                "name": contact.attributes.get("name", contact.entity_id),
                "type": contact.contact_type,
                "hostile": contact.is_hostile,
                "lat": contact.lat, "lon": contact.lon,
                "speed": contact.speed, "heading": contact.heading,
                "ais_off": bool(contact.attributes.get("ais_off", False)),
            })
        return sig

    def update_contact(self, entity_id: str, updates: ContactUpdateRequest) -> bool:
        current = next((c for c in self._store.get_contacts() if c.entity_id == entity_id), None)
        if current is None:
            raise KeyError(entity_id)
        if self._sim is not None:
            self._sim.update_entity(entity_id, updates)

        merged_attributes = dict(current.attributes)
        if updates.attributes:
            merged_attributes.update(updates.attributes)
        if updates.name is not None:
            merged_attributes["name"] = updates.name

        updated = current.model_copy(update={
            "contact_type": updates.contact_type or current.contact_type,
            "lat": updates.lat if updates.lat is not None else current.lat,
            "lon": updates.lon if updates.lon is not None else current.lon,
            "speed": updates.speed if updates.speed is not None else current.speed,
            "heading": (updates.heading % 360) if updates.heading is not None else current.heading,
            "is_hostile": updates.is_hostile if updates.is_hostile is not None else current.is_hostile,
            "attributes": merged_attributes,
            "timestamp": datetime.now(timezone.utc),
        })
        return self.inject_contact(updated)

    def remove_contact(self, entity_id: str) -> bool:
        removed = self._store.remove_contact(entity_id)
        if self._sim is not None:
            self._sim.remove_entity(entity_id)
        return removed

    def schedule_action(self, action: EngineActionRequest) -> dict[str, Any]:
        if self._sim is None:
            raise RuntimeError("Simulation not loaded")
        return self._sim.schedule_action(action)

    def reset(self) -> None:
        self._store.clear()
        self._bus.clear()
        self._sim = None
        self._combat.reset(seed=settings.simulation_seed)


_engine: ContactEngine | None = None


def get_contact_engine() -> ContactEngine:
    global _engine
    if _engine is None:
        _engine = ContactEngine()
    return _engine
