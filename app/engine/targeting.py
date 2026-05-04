from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ..core.constants import AnomalyLevel, EntityType, ThreatLevel
from ..core.schemas import (
    AnomalyResult,
    Contact,
    ContactType,
    CourseOfAction,
    FeatureVector,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from .asset_assignment import SupportingAssetAssignment, assign_supporting_asset
from .fusion import FusedTrack
from .roe_engine import evaluate_roe

PRIORITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

TYPE_BY_CONTACT: dict[str, str] = {
    ContactType.VESSEL.value: "vessel",
    ContactType.CONVOY.value: "convoy",
    ContactType.SUBMARINE.value: "submarine",
    ContactType.UAV.value: "uav",
    ContactType.RADAR.value: "aircraft",
    ContactType.UNKNOWN.value: "unknown",
}

TYPE_BY_ENTITY: dict[str, str] = {
    EntityType.SUSPICIOUS_VESSEL.value: "vessel",
    EntityType.ALLIED_VESSEL.value: "vessel",
    EntityType.NEUTRAL_VESSEL.value: "vessel",
    EntityType.UAV.value: "uav",
    EntityType.CONVOY.value: "convoy",
    EntityType.INFRASTRUCTURE.value: "ground",
    EntityType.ISR_ASSET.value: "aircraft",
}

ACTION_TEMPLATE_MAP = {
    "monitor": "COA-TPL-BASELINE",
    "track": "COA-TPL-ISR",
    "shadow": "COA-TPL-SHADOW",
    "prepared_for_intercept_monitoring": "COA-TPL-COMBINED",
    "protect-asset": "COA-TPL-CABLE-PROTECT",
}

ACTION_ESCALATION_RISK = {
    "monitor": 0.05,
    "track": 0.08,
    "shadow": 0.16,
    "prepared_for_intercept_monitoring": 0.22,
    "protect-asset": 0.14,
}


@dataclass
class Target:
    id: str
    type: str
    classification_confidence: float
    threat_score: float
    priority_score: float
    priority_level: str
    recommended_action: str
    roe_status: str
    rationale: str
    sources: list[str]
    supporting_asset: SupportingAssetAssignment | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.supporting_asset is not None:
            data["supporting_asset"] = self.supporting_asset.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Target":
        support = data.get("supporting_asset")
        if isinstance(support, dict):
            data = dict(data)
            data["supporting_asset"] = SupportingAssetAssignment.from_dict(support)
        return cls(**data)


def serialize_targets(targets: list[Target]) -> list[dict[str, Any]]:
    return [target.to_dict() for target in targets]


def build_targets(
    context: Any,
    *,
    features: list[FeatureVector],
    anomalies: list[AnomalyResult],
    threats: list[ThreatResult],
    fused_tracks: list[FusedTrack] | None = None,
) -> list[Target]:
    contacts_by_id = {
        contact.entity_id: contact
        for contact in (context.active_contacts or [])
    }
    events_by_id: dict[str, list[Any]] = {}
    for event in context.events:
        events_by_id.setdefault(event.entity_id, []).append(event)

    features_by_id: dict[str, list[FeatureVector]] = {}
    for feature in features:
        features_by_id.setdefault(feature.entity_id, []).append(feature)

    anomalies_by_id: dict[str, list[AnomalyResult]] = {}
    for anomaly in anomalies:
        anomalies_by_id.setdefault(anomaly.entity_id, []).append(anomaly)

    threat_by_id = {threat.entity_id: threat for threat in threats}
    fused_by_entity: dict[str, FusedTrack] = {}
    for track in fused_tracks or []:
        for entity_id in track.correlated_entities:
            fused_by_entity.setdefault(entity_id, track)
    target_ids = {
        *contacts_by_id.keys(),
        *events_by_id.keys(),
        *threat_by_id.keys(),
    }

    targets: list[Target] = []
    for entity_id in sorted(target_ids):
        threat = threat_by_id.get(entity_id)
        entity_events = events_by_id.get(entity_id, [])
        entity_contact = contacts_by_id.get(entity_id)
        if not _is_target_candidate(entity_contact, entity_events, threat):
            continue
        if not threat and not entity_events:
            continue

        entity_features = features_by_id.get(entity_id, [])
        entity_anomalies = anomalies_by_id.get(entity_id, [])
        fused_track = fused_by_entity.get(entity_id)

        target_type = _classify_target_type(entity_contact, entity_events)
        classification_confidence = _classification_confidence(
            entity_contact,
            entity_events,
            threat,
            fused_track,
        )
        threat_score = round(threat.threat_probability if threat else 0.0, 3)
        suspicious_flags = _suspicious_behavior_flags(entity_events, entity_features, entity_contact)
        priority_score = _priority_score(
            threat_score=threat_score,
            anomalies=entity_anomalies,
            features=entity_features,
            suspicious_flags=suspicious_flags,
            fused_track=fused_track,
        )
        priority_level = _priority_level(priority_score)
        recommended_action = _recommended_action(
            priority_level,
            suspicious_flags,
            entity_features,
        )
        roe_status = _evaluate_target_roe(
            entity_id=entity_id,
            target_type=target_type,
            threat=threat,
            classification_confidence=classification_confidence,
            recommended_action=recommended_action,
        )
        sources = _sources(entity_contact, entity_events, suspicious_flags, entity_anomalies, fused_track)
        rationale = _rationale(
            threat=threat,
            anomalies=entity_anomalies,
            suspicious_flags=suspicious_flags,
            recommended_action=recommended_action,
            priority_level=priority_level,
            fused_track=fused_track,
        )
        target_lat, target_lon = _target_position(entity_contact, entity_events, fused_track)
        supporting_asset = assign_supporting_asset(
            target_id=entity_id,
            target_type=target_type,
            recommended_action=recommended_action,
            priority_level=priority_level,
            roe_status=roe_status,
            target_lat=target_lat,
            target_lon=target_lon,
            asset_states=getattr(context, "asset_states", None),
            active_contacts=getattr(context, "active_contacts", None),
        )
        targets.append(Target(
            id=entity_id,
            type=target_type,
            classification_confidence=classification_confidence,
            threat_score=threat_score,
            priority_score=priority_score,
            priority_level=priority_level,
            recommended_action=recommended_action,
            roe_status=roe_status,
            rationale=rationale,
            sources=sources,
            supporting_asset=supporting_asset,
        ))

    targets.sort(
        key=lambda item: (
            PRIORITY_ORDER.get(item.priority_level, -1),
            item.priority_score,
            item.threat_score,
            item.id,
        ),
        reverse=True,
    )
    return targets


def _is_target_candidate(
    contact: Contact | None,
    events: list[Any],
    threat: ThreatResult | None,
) -> bool:
    if threat is not None:
        return True
    if contact is not None:
        allegiance = str(contact.attributes.get("allegiance", "")).lower()
        if contact.contact_type == ContactType.INFRASTRUCTURE:
            return False
        if allegiance in {"friendly", "blue", "neutral", "infrastructure"}:
            return False
        if contact.attributes.get("role") in {"allied", "isr", "support"}:
            return False
    if events:
        if any(event.is_threat_candidate for event in events):
            return True
        primary_type = events[0].entity_type
        return primary_type not in {
            EntityType.ALLIED_VESSEL,
            EntityType.INFRASTRUCTURE,
            EntityType.NEUTRAL_VESSEL,
            EntityType.ISR_ASSET,
        }
    return False


def _classify_target_type(contact: Contact | None, events: list[Any]) -> str:
    if contact is not None:
        subtype = str(contact.attributes.get("subtype", "")).lower()
        if subtype in {"jet", "helicopter", "commercial"}:
            return "aircraft"
        if subtype == "submarine":
            return "submarine"
        return TYPE_BY_CONTACT.get(contact.contact_type.value, "unknown")

    if events:
        first = events[0]
        return TYPE_BY_ENTITY.get(first.entity_type.value, "unknown")
    return "unknown"


def _classification_confidence(
    contact: Contact | None,
    events: list[Any],
    threat: ThreatResult | None,
    fused_track: FusedTrack | None,
) -> float:
    confidence = 0.6
    if contact is not None:
        confidence = max(confidence, float(contact.confidence))
        if contact.attributes.get("subtype") or contact.contact_type != ContactType.UNKNOWN:
            confidence += 0.1
    if events:
        avg_event_conf = sum(event.confidence for event in events) / len(events)
        confidence = max(confidence, avg_event_conf)
    if threat is not None:
        confidence = max(confidence, threat.confidence)
    if fused_track is not None:
        confidence = max(confidence, fused_track.fused_confidence)
    return round(min(confidence, 1.0), 3)


def _priority_score(
    *,
    threat_score: float,
    anomalies: list[AnomalyResult],
    features: list[FeatureVector],
    suspicious_flags: list[str],
    fused_track: FusedTrack | None,
) -> float:
    max_anomaly = max((anomaly.anomaly_score for anomaly in anomalies), default=0.0)
    min_distance = min(
        (feature.distance_to_nearest_critical_infrastructure for feature in features),
        default=999.0,
    )
    proximity_score = 0.0
    if min_distance < 25.0:
        proximity_score = (1.0 - (min_distance / 25.0)) * 12.0

    score = (
        threat_score * 55.0
        + (max_anomaly * 0.25)
        + proximity_score
        + min(len(suspicious_flags) * 4.0, 8.0)
    )
    if fused_track is not None:
        score += min(max(fused_track.source_count - 1, 0) * 3.0, 9.0)
        score += min(fused_track.fused_confidence * 6.0, 6.0)
    return round(min(max(score, 0.0), 100.0), 1)


def _priority_level(priority_score: float) -> str:
    if priority_score >= 75.0:
        return ThreatLevel.CRITICAL.value
    if priority_score >= 55.0:
        return ThreatLevel.HIGH.value
    if priority_score >= 30.0:
        return ThreatLevel.MEDIUM.value
    return ThreatLevel.LOW.value


def _recommended_action(
    priority_level: str,
    suspicious_flags: list[str],
    features: list[FeatureVector],
) -> str:
    if priority_level == ThreatLevel.LOW.value:
        return "monitor"
    if priority_level == ThreatLevel.MEDIUM.value:
        return "track"
    if priority_level == ThreatLevel.HIGH.value:
        return "shadow"

    min_distance = min(
        (feature.distance_to_nearest_critical_infrastructure for feature in features),
        default=999.0,
    )
    heading_to_asset = max(
        (feature.heading_towards_critical_asset for feature in features),
        default=0.0,
    )
    if min_distance < 15.0 or heading_to_asset > 0.45 or "targeting_infrastructure" in suspicious_flags:
        return "protect-asset"
    return "prepared_for_intercept_monitoring"


def _evaluate_target_roe(
    *,
    entity_id: str,
    target_type: str,
    threat: ThreatResult | None,
    classification_confidence: float,
    recommended_action: str,
) -> str:
    template_id = ACTION_TEMPLATE_MAP[recommended_action]
    synthetic_coa = CourseOfAction(
        coa_id=f"TGT-{entity_id}-{recommended_action}",
        template_id=template_id,
        title=f"Target advisory for {entity_id}",
        description=f"Non-lethal advisory action for {target_type} target {entity_id}",
        target_entities=[entity_id],
        required_assets=[],
        assumptions=[],
        estimated_time_minutes=0,
        expected_effect=f"Improve awareness and posture against {entity_id}",
        risk_categories=["targeting_support"],
        escalation_risk=ACTION_ESCALATION_RISK[recommended_action],
        civilian_risk=0.0,
        logistics_burden=0.0,
        source="targeting_pipeline",
    )
    synthetic_simulation = SimulationResult(
        coa_id=synthetic_coa.coa_id,
        success_probability=max(threat.threat_probability if threat else 0.4, 0.1),
        expected_time_to_effect=0.0,
        risk_to_second_cable=0.0,
        escalation_probability=synthetic_coa.escalation_risk,
        missed_detection_probability=max(1.0 - classification_confidence, 0.0),
        confidence_interval=(0.0, 1.0),
        simulation_runs=1,
    )
    synthetic_scored = ScoredCOA(
        coa=synthetic_coa,
        simulation=synthetic_simulation,
        total_score=50.0,
        rank=1,
        tradeoff_explanation="Targeting advisory ROE check",
    )
    evaluated = evaluate_roe(
        [synthetic_scored],
        [threat] if threat else [_fallback_threat(entity_id)],
        confidence=classification_confidence,
        civilian_proximity=False,
    )
    return evaluated[0].coa.roe_status


def _fallback_threat(entity_id: str) -> ThreatResult:
    return ThreatResult(
        entity_id=entity_id,
        threat_probability=0.2,
        threat_level=ThreatLevel.LOW,
        confidence=0.6,
        main_drivers=["No direct threat result available"],
    )


def _suspicious_behavior_flags(
    events: list[Any],
    features: list[FeatureVector],
    contact: Contact | None,
) -> list[str]:
    flags: set[str] = set()
    for event in events:
        attrs = event.attributes or {}
        if attrs.get("behavior_mode") == "hostile_probe_infrastructure":
            flags.add("targeting_infrastructure")
        if attrs.get("course_change") or attrs.get("suspicious_maneuver"):
            flags.add("course_change")
        if attrs.get("intent") in {"divert", "probe", "shadow"}:
            flags.add(f"intent:{attrs['intent']}")
        if attrs.get("is_loitering"):
            flags.add("loitering")
    for feature in features:
        if feature.heading_towards_critical_asset > 0.4:
            flags.add("heading_toward_asset")
        if feature.speed_anomaly_score > 0.45:
            flags.add("speed_anomaly")
        if feature.jamming_nearby > 0.2:
            flags.add("jamming_association")
    if contact is not None:
        attrs = contact.attributes or {}
        if attrs.get("heading_toward_infra"):
            flags.add("heading_toward_asset")
        if attrs.get("is_loitering"):
            flags.add("loitering")
        if attrs.get("signal_loss") or attrs.get("reappeared"):
            flags.add("signal_irregularity")
    return sorted(flags)


def _sources(
    contact: Contact | None,
    events: list[Any],
    suspicious_flags: list[str],
    anomalies: list[AnomalyResult],
    fused_track: FusedTrack | None,
) -> list[str]:
    source_set = {event.source for event in events if getattr(event, "source", None)}
    if contact is not None:
        source_set.add(contact.source)
    if fused_track is not None:
        source_set.update(fused_track.sources)
        source_set.add("fusion")
    if suspicious_flags:
        source_set.add("behavior")
    if anomalies:
        source_set.add("anomaly")
    return sorted(source_set)


def _rationale(
    *,
    threat: ThreatResult | None,
    anomalies: list[AnomalyResult],
    suspicious_flags: list[str],
    recommended_action: str,
    priority_level: str,
    fused_track: FusedTrack | None,
) -> str:
    reasons: list[str] = []
    advisory_action = recommended_action.replace("_", " ")
    priority_reason = f"Priority {priority_level}; advisory action is {advisory_action}"
    if fused_track is not None:
        reasons.append(fused_track.rationale)
    if threat is not None and threat.main_drivers:
        reasons.append(threat.main_drivers[0])
    top_anomaly = max(anomalies, key=lambda item: item.anomaly_score, default=None)
    if top_anomaly is not None and top_anomaly.explanations:
        reasons.append(top_anomaly.explanations[0])
    if suspicious_flags:
        reasons.append(f"Behavior indicators: {', '.join(suspicious_flags[:3])}")
    reasons = reasons[:3]
    reasons.append(priority_reason)
    return "; ".join(reasons)


def _target_position(
    contact: Contact | None,
    events: list[Any],
    fused_track: FusedTrack | None,
) -> tuple[float | None, float | None]:
    if contact is not None:
        return contact.lat, contact.lon
    if events:
        latest = max(events, key=lambda item: item.timestamp)
        return latest.lat, latest.lon
    if fused_track is not None:
        return fused_track.position.get("lat"), fused_track.position.get("lon")
    return None, None
