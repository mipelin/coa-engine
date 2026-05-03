"""Common Operating Picture (COP) assembly.

Builds a unified, commander-facing view from existing engine state.
No analysis recomputation — reads current state and structures it for the UI.

Guarantees:
- Fully consistent with backend state.
- No duplicated analysis logic.
- No LLM calls in COP assembly.
- Deterministic given the same state.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..core.constants import ThreatLevel
from .coa_optimizer import OptimizationResult
from .fusion import FusedTrack, serialize_fused_tracks
from .operational_effects import OperationalEffects
from .replay import get_replay_store
from .state_store import StateStore, get_state_store
from .targeting import Target, serialize_targets

logger = logging.getLogger("coa_engine.engine.cop")

# ---------------------------------------------------------------------------
# Allegiance colors for map rendering
# ---------------------------------------------------------------------------

ALLEGIANCE_COLORS = {
    "hostile": "#e74c3c",
    "red": "#e74c3c",
    "suspicious": "#f39c12",
    "neutral": "#95a5a6",
    "friendly": "#2ecc71",
    "blue": "#2ecc71",
    "unknown": "#bdc3c7",
}

SOURCE_LABELS = {
    "ais": "AIS / NOAA",
    "aishub": "AIS / NOAA",
    "noaa_replay": "AIS / NOAA",
    "combat_system": "CMS (synthetic)",
    "satellite": "Satellite-like",
    "social": "OSINT-like",
    "social_media": "OSINT-like",
    "osint": "OSINT-like",
    "manual": "Manual / injected",
    "manual_injection": "Manual / injected",
    "simulation": "Simulation entity",
    "dashboard": "Simulation entity",
    "fused": "Heuristic fusion",
}

# ---------------------------------------------------------------------------
# Track type icons
# ---------------------------------------------------------------------------

TRACK_ICONS = {
    "vessel": "ship",
    "submarine": "submarine",
    "uav": "uav",
    "aircraft": "aircraft",
    "ground": "ground",
    "unknown": "unknown",
}


# ---------------------------------------------------------------------------
# COP data structures
# ---------------------------------------------------------------------------


@dataclass
class COPThreatSummary:
    """Top-level threat picture."""
    threat_level: str
    top_threat_entity: str | None
    top_threat_probability: float
    threat_count: int
    threat_distribution: dict[str, int] = field(default_factory=dict)


@dataclass
class COPContactVisual:
    """Contact/track with visual rendering attributes."""
    entity_id: str
    track_type: str
    icon: str
    color: str
    lat: float
    lon: float
    heading: float | None
    speed: float
    allegiance: str
    is_hostile: bool
    confidence: float
    fused_confidence: float | None
    source_count: int
    sources: list[str]
    threat_level: str | None
    threat_probability: float | None
    source: str
    source_label: str
    provenance_label: str
    contact_type: str
    display_name: str
    subtype: str
    track_quality: str | None
    timestamp: str | None
    altitude_ft: float | None
    depth_m: float | None
    behavior_flags: list[str]
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class COPTargetPanel:
    """Target detail panel data."""
    entity_id: str
    type: str
    classification_confidence: float
    threat_score: float
    priority_score: float
    priority_level: str
    recommended_action: str
    roe_status: str
    rationale: str
    sources: list[str]
    supporting_asset: dict[str, Any] | None = None


@dataclass
class COPVariantCard:
    """Optimized variant for decision panel."""
    variant_id: str
    title: str
    total_score: float
    robustness: float
    success_probability: float
    escalation_probability: float
    roe_status: str
    roe_reason: str
    tradeoff_explanation: str
    parameters: dict[str, Any] | None = None


@dataclass
class COPDecisionPanel:
    """Current recommendation + top optimized variants."""
    current_recommendation: dict[str, Any] | None
    optimized_variants: list[COPVariantCard] = field(default_factory=list)
    base_coas: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class COPForecastSummary:
    """Short-form forecast for the COP."""
    available: bool
    threat_trend: list[str] = field(default_factory=list)
    trend_direction: str = "stable"
    horizon: int = 0
    key_risks: list[str] = field(default_factory=list)
    recommendation_changes: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class COPEventNarrative:
    """Latest event summary / situation narrative."""
    event_type: str = "none"
    summary_text: str = ""
    llm_used: bool = False
    language_used: str = "en"


@dataclass
class COPResult:
    """Full Common Operating Picture."""
    tick: int = 0
    scenario_id: str | None = None
    scenario_name: str | None = None
    infrastructure_status: str = "nominal"
    threat_summary: COPThreatSummary = field(default_factory=lambda: COPThreatSummary(
        threat_level="LOW", top_threat_entity=None, top_threat_probability=0.0, threat_count=0,
    ))
    contacts: list[COPContactVisual] = field(default_factory=list)
    fused_tracks: list[dict[str, Any]] = field(default_factory=list)
    targets: list[COPTargetPanel] = field(default_factory=list)
    top_targets: list[COPTargetPanel] = field(default_factory=list)
    decision_panel: COPDecisionPanel = field(default_factory=COPDecisionPanel)
    forecast_summary: COPForecastSummary = field(default_factory=COPForecastSummary)
    event_narrative: COPEventNarrative = field(default_factory=COPEventNarrative)
    key_anomalies: list[dict[str, Any]] = field(default_factory=list)
    operational_effects: dict[str, Any] = field(default_factory=dict)
    replay_summary: dict[str, Any] = field(default_factory=dict)
    scored_coas: list[dict[str, Any]] = field(default_factory=list)
    threats: list[dict[str, Any]] = field(default_factory=list)
    anomalies: list[dict[str, Any]] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    recommendation: dict[str, Any] | None = None
    assets: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Assembly functions
# ---------------------------------------------------------------------------


def _build_threat_summary(store: StateStore) -> COPThreatSummary:
    threats = store.get_threats()
    distribution: dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for t in threats:
        level = t.threat_level.value
        distribution[level] = distribution.get(level, 0) + 1

    top_entity = threats[0].entity_id if threats else None
    top_prob = threats[0].threat_probability if threats else 0.0
    level = store.state.current_threat_level

    return COPThreatSummary(
        threat_level=level,
        top_threat_entity=top_entity,
        top_threat_probability=round(top_prob, 3),
        threat_count=len(threats),
        threat_distribution=distribution,
    )


def _build_contact_visuals(store: StateStore) -> list[COPContactVisual]:
    contacts = store.get_contacts()
    fused = store.get_fused_tracks()
    threats = store.get_threats()

    # Index fused tracks and threats by entity
    fused_by_entity: dict[str, FusedTrack] = {}
    for ft in fused:
        for eid in ft.correlated_entities:
            fused_by_entity.setdefault(eid, ft)

    threat_by_entity = {t.entity_id: t for t in threats}

    visuals: list[COPContactVisual] = []
    for c in contacts:
        allegiance = str(c.attributes.get("allegiance", "unknown")).lower()
        if c.is_hostile:
            allegiance = "hostile"

        ft = fused_by_entity.get(c.entity_id)
        threat = threat_by_entity.get(c.entity_id)

        track_type = ft.track_type if ft else _guess_track_type(c)
        icon = TRACK_ICONS.get(track_type, "unknown")

        visuals.append(COPContactVisual(
            entity_id=c.entity_id,
            track_type=track_type,
            icon=icon,
            color=ALLEGIANCE_COLORS.get(allegiance, ALLEGIANCE_COLORS["unknown"]),
            lat=round(c.lat, 5),
            lon=round(c.lon, 5),
            heading=c.heading,
            speed=c.speed,
            allegiance=allegiance,
            is_hostile=c.is_hostile,
            confidence=round(c.confidence, 3),
            fused_confidence=round(ft.fused_confidence, 3) if ft else None,
            source_count=ft.source_count if ft else 1,
            sources=ft.sources if ft else [c.source],
            threat_level=threat.threat_level.value if threat else None,
            threat_probability=round(threat.threat_probability, 3) if threat else None,
            source=str(c.source),
            source_label=SOURCE_LABELS.get(str(c.source).lower(), str(c.source).replace("_", " ").title()),
            provenance_label=SOURCE_LABELS.get(str(c.source).lower(), str(c.source).replace("_", " ").title()),
            contact_type=str(c.contact_type.value if hasattr(c.contact_type, "value") else c.contact_type),
            display_name=str(c.attributes.get("name", c.entity_id)),
            subtype=str(c.attributes.get("subtype", track_type)),
            track_quality=c.attributes.get("track_quality"),
            timestamp=c.timestamp.isoformat() if c.timestamp else None,
            altitude_ft=c.attributes.get("altitude_ft"),
            depth_m=c.attributes.get("depth_m"),
            behavior_flags=list(c.attributes.get("behavior_flags", c.attributes.get("flags", [])) or []),
            attributes=dict(c.attributes),
        ))

    return visuals


def _guess_track_type(contact: Any) -> str:
    ctype = str(contact.contact_type.value).lower() if hasattr(contact.contact_type, "value") else str(contact.contact_type).lower()
    mapping = {
        "vessel": "vessel", "submarine": "submarine", "uav": "uav",
        "convoy": "vessel", "radar": "aircraft", "infrastructure": "ground",
    }
    return mapping.get(ctype, "unknown")


def _build_targets(store: StateStore) -> list[COPTargetPanel]:
    targets = store.get_targets()
    panels: list[COPTargetPanel] = []
    for t in targets:
        panels.append(COPTargetPanel(
            entity_id=t.id,
            type=t.type,
            classification_confidence=round(t.classification_confidence, 3),
            threat_score=round(t.threat_score, 3),
            priority_score=round(t.priority_score, 1),
            priority_level=t.priority_level,
            recommended_action=t.recommended_action,
            roe_status=t.roe_status,
            rationale=t.rationale,
            sources=t.sources,
            supporting_asset=t.supporting_asset.to_dict() if t.supporting_asset else None,
        ))
    return panels


def _build_decision_panel(
    store: StateStore,
    optimization: OptimizationResult | None,
) -> COPDecisionPanel:
    scored = store.get_scored_coas()
    rec = store.get_recommendation()

    current_rec = None
    if rec and rec.recommended:
        current_rec = {
            "coa_id": rec.recommended.coa.coa_id,
            "title": rec.recommended.coa.title,
            "score": round(rec.recommended.total_score, 1),
            "roe_status": rec.recommended.coa.roe_status,
            "roe_reason": rec.recommended.coa.roe_reason,
            "success_probability": round(rec.recommended.simulation.success_probability, 3),
            "rationale": rec.rationale,
        }

    base_coas = [
        {
            "coa_id": s.coa.coa_id,
            "title": s.coa.title,
            "rank": s.rank,
            "score": round(s.total_score, 1),
            "roe_status": s.coa.roe_status,
        }
        for s in scored[:5]
    ]

    variants: list[COPVariantCard] = []
    if optimization and optimization.optimized_variants:
        robust_lookup = {
            r.get("variant_id"): r.get("robustness", 0.0)
            for r in optimization.robustness_ranking
        }
        param_lookup = {
            p["variant_id"]: p
            for p in optimization.variant_parameters
        }
        for s in optimization.optimized_variants[:3]:
            vid = s.coa.coa_id
            variants.append(COPVariantCard(
                variant_id=vid,
                title=s.coa.title,
                total_score=round(s.total_score, 1),
                robustness=round(robust_lookup.get(vid, 0.0), 1),
                success_probability=round(s.simulation.success_probability, 3),
                escalation_probability=round(s.simulation.escalation_probability, 3),
                roe_status=s.coa.roe_status,
                roe_reason=s.coa.roe_reason,
                tradeoff_explanation=s.tradeoff_explanation,
                parameters=param_lookup.get(vid),
            ))

    return COPDecisionPanel(
        current_recommendation=current_rec,
        optimized_variants=variants,
        base_coas=base_coas,
    )


def _build_forecast_summary(store: StateStore) -> COPForecastSummary:
    opt = getattr(store, "_coa_forecast", None)
    if opt is None:
        return COPForecastSummary(available=False)
    return COPForecastSummary(
        available=True,
        threat_trend=getattr(opt, "threat_trend", []),
        trend_direction=getattr(opt, "expected_threat_trend", "stable"),
        horizon=getattr(opt, "tick_horizon", 0),
        key_risks=getattr(opt, "key_risks", []),
        recommendation_changes=getattr(opt, "recommendation_changes", []),
    )


def _build_event_narrative(store: StateStore) -> COPEventNarrative:
    summary = store.get_latest_event_summary()
    if summary is None:
        return COPEventNarrative()
    return COPEventNarrative(
        event_type=summary.event_type,
        summary_text=summary.summary_text,
        llm_used=summary.llm_used,
        language_used=summary.language_used,
    )


def _build_key_anomalies(store: StateStore) -> list[dict[str, Any]]:
    anomalies = store.get_anomalies()
    high_anomalies = [a for a in anomalies if a.anomaly_score >= 30]
    return [
        {
            "entity_id": a.entity_id,
            "score": a.anomaly_score,
            "level": a.anomaly_level.value,
            "indicators": a.explanations[:3],
        }
        for a in high_anomalies[:10]
    ]


def _build_scored_coas(store: StateStore) -> list[dict[str, Any]]:
    return [s.model_dump(mode="json") for s in store.get_scored_coas()]


def _build_threats(store: StateStore) -> list[dict[str, Any]]:
    return [t.model_dump(mode="json") for t in store.get_threats()]


def _build_anomalies(store: StateStore) -> list[dict[str, Any]]:
    return [a.model_dump(mode="json") for a in store.get_anomalies()]


def _build_state_summary(store: StateStore) -> dict[str, Any]:
    state = store.state
    return {
        "tick": state.tick,
        "current_threat_level": state.current_threat_level,
        "top_threat_probability": state.top_threat_probability,
        "top_threat_entity": state.top_threat_entity,
        "contacts_processed": state.contacts_processed,
        "llm_calls_made": state.llm_calls_made,
        "ui_language": state.ui_language,
        "scenario": state.scenario.model_dump(mode="json"),
    }


def _build_replay_summary() -> dict[str, Any]:
    """Build a compact replay summary for the COP."""
    store = get_replay_store()
    if store.snapshot_count == 0:
        return {
            "snapshots_count": 0,
            "first_tick": None,
            "last_tick": None,
            "last_major_change": None,
            "latest_lesson": None,
        }
    return {
        "snapshots_count": store.snapshot_count,
        "first_tick": store.first_tick,
        "last_tick": store.last_tick,
        "last_major_change": store.get_last_major_change(),
        "latest_lesson": store.get_latest_lesson(),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def assemble_cop(store: StateStore | None = None) -> COPResult:
    """Assemble the Common Operating Picture from current engine state.

    No analysis recomputation. Reads existing state only.
    """
    if store is None:
        store = get_state_store()

    state = store.state
    scenario = state.scenario
    opt = getattr(store, "_coa_optimization", None)
    opfx = getattr(store, "_operational_effects", None)

    fused = store.get_fused_tracks()

    return COPResult(
        tick=state.tick,
        scenario_id=scenario.scenario_id,
        scenario_name=scenario.scenario_name,
        infrastructure_status=scenario.infrastructure_status,
        threat_summary=_build_threat_summary(store),
        contacts=_build_contact_visuals(store),
        fused_tracks=serialize_fused_tracks(fused),
        targets=_build_targets(store),
        top_targets=_build_targets(store)[:5],
        decision_panel=_build_decision_panel(store, opt),
        forecast_summary=_build_forecast_summary(store),
        event_narrative=_build_event_narrative(store),
        key_anomalies=_build_key_anomalies(store),
        operational_effects=opfx.to_dict() if opfx else {},
        replay_summary=_build_replay_summary(),
        scored_coas=_build_scored_coas(store),
        threats=_build_threats(store),
        anomalies=_build_anomalies(store),
        state=_build_state_summary(store),
        recommendation=store.get_recommendation().model_dump(mode="json") if store.get_recommendation() else None,
        assets=[asset.model_dump(mode="json") for asset in store.get_asset_states()],
    )


def cop_to_dict(cop: COPResult) -> dict[str, Any]:
    """Serialize COPResult to dict for API responses."""
    return {
        "tick": cop.tick,
        "scenario_id": cop.scenario_id,
        "scenario_name": cop.scenario_name,
        "infrastructure_status": cop.infrastructure_status,
        "threat_summary": {
            "threat_level": cop.threat_summary.threat_level,
            "top_threat_entity": cop.threat_summary.top_threat_entity,
            "top_threat_probability": cop.threat_summary.top_threat_probability,
            "threat_count": cop.threat_summary.threat_count,
            "distribution": cop.threat_summary.threat_distribution,
        },
        "contacts": [
            {
                "entity_id": c.entity_id,
                "track_type": c.track_type,
                "icon": c.icon,
                "color": c.color,
                "lat": c.lat,
                "lon": c.lon,
                "heading": c.heading,
                "speed": c.speed,
                "allegiance": c.allegiance,
                "is_hostile": c.is_hostile,
                "confidence": c.confidence,
                "fused_confidence": c.fused_confidence,
                "source_count": c.source_count,
                "sources": c.sources,
                "threat_level": c.threat_level,
                "threat_probability": c.threat_probability,
                "source": c.source,
                "source_label": c.source_label,
                "provenance_label": c.provenance_label,
                "contact_type": c.contact_type,
                "display_name": c.display_name,
                "subtype": c.subtype,
                "track_quality": c.track_quality,
                "timestamp": c.timestamp,
                "altitude_ft": c.altitude_ft,
                "depth_m": c.depth_m,
                "behavior_flags": c.behavior_flags,
                "attributes": c.attributes,
            }
            for c in cop.contacts
        ],
        "fused_tracks": cop.fused_tracks,
        "targets": [
            {
                "entity_id": t.entity_id,
                "type": t.type,
                "classification_confidence": t.classification_confidence,
                "threat_score": t.threat_score,
                "priority_score": t.priority_score,
                "priority_level": t.priority_level,
                "recommended_action": t.recommended_action,
                "roe_status": t.roe_status,
                "rationale": t.rationale,
                "sources": t.sources,
                "supporting_asset": t.supporting_asset,
            }
            for t in cop.targets
        ],
        "top_targets": [
            {
                "entity_id": t.entity_id,
                "type": t.type,
                "classification_confidence": t.classification_confidence,
                "threat_score": t.threat_score,
                "priority_score": t.priority_score,
                "priority_level": t.priority_level,
                "recommended_action": t.recommended_action,
                "roe_status": t.roe_status,
                "rationale": t.rationale,
                "sources": t.sources,
                "supporting_asset": t.supporting_asset,
            }
            for t in cop.top_targets
        ],
        "decision_panel": {
            "current_recommendation": cop.decision_panel.current_recommendation,
            "optimized_variants": [
                {
                    "variant_id": v.variant_id,
                    "title": v.title,
                    "total_score": v.total_score,
                    "robustness": v.robustness,
                    "success_probability": v.success_probability,
                    "escalation_probability": v.escalation_probability,
                    "roe_status": v.roe_status,
                    "roe_reason": v.roe_reason,
                    "tradeoff_explanation": v.tradeoff_explanation,
                    "parameters": v.parameters,
                }
                for v in cop.decision_panel.optimized_variants
            ],
            "base_coas": cop.decision_panel.base_coas,
        },
        "forecast_summary": {
            "available": cop.forecast_summary.available,
            "threat_trend": cop.forecast_summary.threat_trend,
            "trend_direction": cop.forecast_summary.trend_direction,
            "horizon": cop.forecast_summary.horizon,
            "key_risks": cop.forecast_summary.key_risks,
            "recommendation_changes": cop.forecast_summary.recommendation_changes,
        },
        "event_narrative": {
            "event_type": cop.event_narrative.event_type,
            "summary_text": cop.event_narrative.summary_text,
            "llm_used": cop.event_narrative.llm_used,
            "language_used": cop.event_narrative.language_used,
        },
        "key_anomalies": cop.key_anomalies,
        "operational_effects": cop.operational_effects,
        "replay_summary": cop.replay_summary,
        "scored_coas": cop.scored_coas,
        "threats": cop.threats,
        "anomalies": cop.anomalies,
        "state": cop.state,
        "recommendation": cop.recommendation,
        "assets": cop.assets,
        "provenance_labels": SOURCE_LABELS,
    }
