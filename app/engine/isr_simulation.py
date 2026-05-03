from __future__ import annotations

"""Synthetic ISR observation layer.

Produces deterministic, source-specific observations from the current operational
state. These observations are synthetic by design and are intended to enrich the
existing fusion layer without claiming raw ISR processing.
"""

import hashlib
import math
from dataclasses import dataclass, field
from datetime import timedelta
import random
from typing import Any, Iterable

from ..core.config import settings
from ..core.schemas import Contact, OperationalEvent
from .feature_engineering import haversine_km


def _stable_seed(*parts: object) -> int:
    digest = hashlib.sha256(":".join(str(part) for part in parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _jitter_position(lat: float, lon: float, sigma_km: float, rng: random.Random) -> tuple[float, float]:
    if sigma_km <= 0:
        return lat, lon
    dlat = rng.gauss(0.0, sigma_km / 111.0)
    lat_safe = max(0.1, abs(lat))
    dlon = rng.gauss(0.0, sigma_km / (111.0 * math.cos(math.radians(lat_safe))))
    return lat + dlat, lon + dlon


def _normalize_entity_type(contact: Contact | None = None, event: OperationalEvent | None = None) -> str:
    if contact is not None:
        subtype = str(contact.attributes.get("subtype", "")).lower()
        if subtype == "submarine" or str(contact.contact_type.value) == "submarine":
            return "submarine"
        if subtype in {"jet", "helicopter", "commercial"}:
            return "aircraft"
        if subtype in {"uav", "drone"} or str(contact.contact_type.value) == "uav":
            return "UAV"
        if str(contact.contact_type.value) == "vessel" or str(contact.contact_type.value) == "convoy":
            return "vessel"
        if str(contact.contact_type.value) == "infrastructure":
            return "ground"
    if event is not None:
        etype = event.entity_type.value
        subtype = str(event.attributes.get("subtype", "")).lower()
        if subtype == "submarine":
            return "submarine"
        if subtype in {"uav", "drone"} or etype == "uav":
            return "UAV"
        if subtype in {"jet", "helicopter", "commercial"}:
            return "aircraft"
        if etype in {"suspicious_vessel", "allied_vessel", "neutral_vessel", "convoy"}:
            return "vessel"
        if etype == "infrastructure":
            return "ground"
    return "unknown"


def _contact_allegiance(contact: Contact) -> str:
    return str(contact.attributes.get("allegiance", "unknown") or "unknown").lower()


def _near_infrastructure(lat: float, lon: float, infrastructure: list[dict[str, Any]]) -> bool:
    return any(
        haversine_km(lat, lon, float(item.get("lat", 0.0)), float(item.get("lon", 0.0))) <= 20.0
        for item in infrastructure
    )


@dataclass(frozen=True)
class ObservationPosition:
    lat: float
    lon: float
    sigma_km: float


@dataclass(frozen=True)
class ObservationKinematics:
    speed: float
    heading: float


@dataclass(frozen=True)
class BaseObservation:
    id: str
    timestamp: Any
    source_type: str
    entity_type: str
    position: ObservationPosition
    kinematics: ObservationKinematics
    confidence: float
    attributes: dict[str, Any] = field(default_factory=dict)
    provenance: str = "synthetic"


class _BasePlugin:
    source_type = "GENERIC"
    sigma_km = 0.1
    latency_min = 0
    confidence = 0.7
    false_positive_rate = 0.0
    miss_rate = 0.0

    def generate(
        self,
        *,
        tick: int,
        contacts: list[Contact],
        events: list[OperationalEvent],
        infrastructure: list[dict[str, Any]],
        seed: int,
    ) -> list[BaseObservation]:
        observations: list[BaseObservation] = []
        for contact in contacts:
            if not self._should_observe_contact(contact):
                continue
            rng = random.Random(_stable_seed(seed, tick, self.source_type, contact.entity_id))
            if rng.random() < self._miss_rate(contact):
                continue
            observations.append(self._from_contact(contact, tick=tick, rng=rng, infrastructure=infrastructure))
        observations.extend(self._event_observations(tick=tick, events=events, infrastructure=infrastructure, seed=seed))
        observations.extend(self._false_positives(tick=tick, contacts=contacts, infrastructure=infrastructure, seed=seed))
        observations.sort(key=lambda item: (item.timestamp, item.source_type, item.id))
        return observations

    def _should_observe_contact(self, contact: Contact) -> bool:
        return True

    def _miss_rate(self, contact: Contact) -> float:
        return self.miss_rate

    def _base_confidence(self, contact: Contact) -> float:
        return self.confidence

    def _attribute_overrides(self, contact: Contact, infrastructure: list[dict[str, Any]]) -> dict[str, Any]:
        entity_type = _normalize_entity_type(contact=contact)
        return {
            "entity_id": contact.entity_id,
            "subtype": str(contact.attributes.get("subtype", entity_type)),
            "allegiance": _contact_allegiance(contact),
            "source_contact": contact.source,
            "source_label": self.source_type,
            "synthetic_observation": True,
            "track_quality": contact.attributes.get("track_quality", "medium"),
            "behavior_flags": list(contact.attributes.get("behavior_flags", contact.attributes.get("flags", [])) or []),
            "near_infrastructure": _near_infrastructure(contact.lat, contact.lon, infrastructure),
        }

    def _from_contact(
        self,
        contact: Contact,
        *,
        tick: int,
        rng: random.Random,
        infrastructure: list[dict[str, Any]],
    ) -> BaseObservation:
        lat, lon = _jitter_position(contact.lat, contact.lon, self.sigma_km, rng)
        timestamp = contact.timestamp - timedelta(minutes=self.latency_min)
        entity_type = _normalize_entity_type(contact=contact)
        return BaseObservation(
            id=f"{self.source_type}-{contact.contact_id}",
            timestamp=timestamp,
            source_type=self.source_type,
            entity_type=entity_type,
            position=ObservationPosition(lat=round(lat, 6), lon=round(lon, 6), sigma_km=self.sigma_km),
            kinematics=ObservationKinematics(speed=round(contact.speed, 2), heading=round(contact.heading, 1)),
            confidence=round(_clamp(self._base_confidence(contact) * contact.confidence, 0.2, 0.98), 3),
            attributes=self._attribute_overrides(contact, infrastructure),
        )

    def _event_observations(
        self,
        *,
        tick: int,
        events: list[OperationalEvent],
        infrastructure: list[dict[str, Any]],
        seed: int,
    ) -> list[BaseObservation]:
        return []

    def _false_positives(
        self,
        *,
        tick: int,
        contacts: list[Contact],
        infrastructure: list[dict[str, Any]],
        seed: int,
    ) -> list[BaseObservation]:
        return []


class AISPlugin(_BasePlugin):
    source_type = "AIS"
    sigma_km = 0.04
    latency_min = 1
    confidence = 0.96
    miss_rate = 0.03

    def _should_observe_contact(self, contact: Contact) -> bool:
        return _normalize_entity_type(contact=contact) == "vessel" and not bool(contact.attributes.get("ais_off", False))

    def _miss_rate(self, contact: Contact) -> float:
        return 0.0 if str(contact.source).lower() in {"aishub", "noaa_replay", "ais"} else self.miss_rate


class CMSRadarLikePlugin(_BasePlugin):
    source_type = "CMS"
    sigma_km = 0.28
    latency_min = 0
    confidence = 0.82
    false_positive_rate = 0.05
    miss_rate = 0.12

    def _should_observe_contact(self, contact: Contact) -> bool:
        return _normalize_entity_type(contact=contact) in {"vessel", "aircraft", "UAV", "unknown"}

    def _base_confidence(self, contact: Contact) -> float:
        if str(contact.source).lower() == "combat_system":
            return 0.9
        return self.confidence

    def _false_positives(
        self,
        *,
        tick: int,
        contacts: list[Contact],
        infrastructure: list[dict[str, Any]],
        seed: int,
    ) -> list[BaseObservation]:
        if not contacts:
            return []
        rng = random.Random(_stable_seed(seed, tick, self.source_type, "false_positive"))
        if rng.random() >= self.false_positive_rate:
            return []
        anchor = contacts[rng.randrange(len(contacts))]
        lat, lon = _jitter_position(anchor.lat, anchor.lon, 1.2, rng)
        return [
            BaseObservation(
                id=f"{self.source_type}-FP-{tick}",
                timestamp=anchor.timestamp,
                source_type=self.source_type,
                entity_type="unknown",
                position=ObservationPosition(lat=round(lat, 6), lon=round(lon, 6), sigma_km=1.2),
                kinematics=ObservationKinematics(speed=round(max(anchor.speed - 2.0, 0.0), 2), heading=round(anchor.heading, 1)),
                confidence=0.41,
                attributes={
                    "entity_id": f"UNK-CMS-{tick}",
                    "subtype": "unknown",
                    "allegiance": "unknown",
                    "synthetic_observation": True,
                    "track_quality": "low",
                    "behavior_flags": ["false_positive"],
                    "near_infrastructure": _near_infrastructure(lat, lon, infrastructure),
                },
            )
        ]


class SatelliteLikePlugin(_BasePlugin):
    source_type = "SAT"
    sigma_km = 0.6
    latency_min = 8
    confidence = 0.72
    miss_rate = 0.45

    def _should_observe_contact(self, contact: Contact) -> bool:
        entity_type = _normalize_entity_type(contact=contact)
        return entity_type in {"vessel", "submarine", "aircraft", "UAV"}

    def generate(
        self,
        *,
        tick: int,
        contacts: list[Contact],
        events: list[OperationalEvent],
        infrastructure: list[dict[str, Any]],
        seed: int,
    ) -> list[BaseObservation]:
        if tick % 3 != 0:
            return []
        return super().generate(tick=tick, contacts=contacts, events=events, infrastructure=infrastructure, seed=seed)


class OSINTLikePlugin(_BasePlugin):
    source_type = "OSINT"
    sigma_km = 1.8
    latency_min = 12
    confidence = 0.46
    miss_rate = 0.0

    def _should_observe_contact(self, contact: Contact) -> bool:
        flags = contact.attributes.get("behavior_flags", contact.attributes.get("flags", [])) or []
        return bool(contact.is_hostile or flags or contact.contact_type.value in {"jamming", "cable_event", "convoy"})

    def _event_observations(
        self,
        *,
        tick: int,
        events: list[OperationalEvent],
        infrastructure: list[dict[str, Any]],
        seed: int,
    ) -> list[BaseObservation]:
        observations: list[BaseObservation] = []
        for event in events[-6:]:
            if event.event_type.value not in {"social_media_report", "convoy_sighting", "cable_severance", "jamming_detected"}:
                continue
            rng = random.Random(_stable_seed(seed, tick, self.source_type, event.event_id))
            lat, lon = _jitter_position(event.lat, event.lon, self.sigma_km, rng)
            observations.append(
                BaseObservation(
                    id=f"{self.source_type}-{event.event_id}",
                    timestamp=event.timestamp - timedelta(minutes=self.latency_min),
                    source_type=self.source_type,
                    entity_type=_normalize_entity_type(event=event),
                    position=ObservationPosition(lat=round(lat, 6), lon=round(lon, 6), sigma_km=self.sigma_km),
                    kinematics=ObservationKinematics(
                        speed=round(float(event.attributes.get("speed_knots", 0.0) or 0.0), 2),
                        heading=round(float(event.attributes.get("heading", 0.0) or 0.0), 1),
                    ),
                    confidence=round(_clamp(self.confidence * event.confidence, 0.2, 0.7), 3),
                    attributes={
                        "entity_id": event.entity_id,
                        "subtype": str(event.attributes.get("subtype", "reported_contact")),
                        "allegiance": (event.allegiance or "unknown").lower() or "unknown",
                        "synthetic_observation": True,
                        "track_quality": "low",
                        "behavior_flags": ["social_report"],
                        "near_infrastructure": _near_infrastructure(lat, lon, infrastructure),
                    },
                )
            )
        return observations


class ESMLikePlugin(_BasePlugin):
    source_type = "ESM"
    sigma_km = 0.9
    latency_min = 2
    confidence = 0.78
    miss_rate = 0.22

    def _should_observe_contact(self, contact: Contact) -> bool:
        flags = contact.attributes.get("behavior_flags", contact.attributes.get("flags", [])) or []
        subtype = str(contact.attributes.get("subtype", "")).lower()
        return (
            contact.contact_type.value in {"jamming", "sigint", "uav"}
            or contact.is_hostile
            or "jamming" in flags
            or subtype in {"warship", "jet", "uav"}
        )

    def _attribute_overrides(self, contact: Contact, infrastructure: list[dict[str, Any]]) -> dict[str, Any]:
        attrs = super()._attribute_overrides(contact, infrastructure)
        flags = list(attrs.get("behavior_flags", []))
        if contact.contact_type.value in {"jamming", "sigint"}:
            flags.append("emissions_detected")
        attrs["behavior_flags"] = sorted(set(flags))
        return attrs


PLUGIN_TYPES = (
    AISPlugin,
    CMSRadarLikePlugin,
    SatelliteLikePlugin,
    OSINTLikePlugin,
    ESMLikePlugin,
)


def simulate_isr_observations(
    *,
    tick: int,
    contacts: Iterable[Contact] | None,
    events: Iterable[OperationalEvent] | None,
    infrastructure: list[dict[str, Any]] | None = None,
    seed: int | None = None,
    enabled: bool | None = None,
) -> list[BaseObservation]:
    if enabled is None:
        enabled = settings.enable_isr_simulation
    if not enabled:
        return []
    contact_list = list(contacts or [])
    event_list = list(events or [])
    if not contact_list and not event_list:
        return []
    infra = infrastructure or []
    scenario_seed = settings.simulation_seed if seed is None else seed
    observations: list[BaseObservation] = []
    for plugin_type in PLUGIN_TYPES:
        plugin = plugin_type()
        observations.extend(
            plugin.generate(
                tick=tick,
                contacts=contact_list,
                events=event_list,
                infrastructure=infra,
                seed=scenario_seed,
            )
        )
    observations.sort(key=lambda item: (item.timestamp, item.source_type, item.id))
    return observations
