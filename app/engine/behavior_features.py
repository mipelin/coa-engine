"""Translate raw behavior attributes from events into structured feature flags.

This module is the single place where behavior_mode strings are interpreted.
Downstream consumers (anomaly_detection, threat_assessment) use BehaviorFeatures
instead of parsing raw attribute strings.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.schemas import OperationalEvent


@dataclass
class BehaviorFeatures:
    behavior_modes: set[str] = field(default_factory=set)
    intents: set[str] = field(default_factory=set)
    targets: set[str] = field(default_factory=set)
    is_probing_infrastructure: bool = False
    is_diverting_after_loiter: bool = False
    is_friendly_patrol: bool = False
    is_neutral_transit: bool = False


def extract_behavior_features(
    events: list[OperationalEvent],
) -> dict[str, BehaviorFeatures]:
    """Aggregate behavior attributes across events, keyed by entity_id."""
    by_entity: dict[str, BehaviorFeatures] = {}

    for event in events:
        bf = by_entity.setdefault(event.entity_id, BehaviorFeatures())
        mode = event.attributes.get("behavior_mode", "")
        intent = event.attributes.get("intent", "")
        target = event.attributes.get("target_infra", "")

        if mode:
            bf.behavior_modes.add(mode)
        if intent:
            bf.intents.add(intent)
        if target:
            bf.targets.add(target)

        if mode == "hostile_probe_infrastructure" and target:
            bf.is_probing_infrastructure = True
        if mode == "hostile_loiter_then_divert" and intent == "divert":
            bf.is_diverting_after_loiter = True
        if mode == "friendly_patrol_monitor":
            bf.is_friendly_patrol = True
        if mode == "neutral_transit":
            bf.is_neutral_transit = True

    return by_entity
