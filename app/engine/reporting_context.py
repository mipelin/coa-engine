from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .replay import generate_aar, get_replay_store
from .state_store import get_state_store


@dataclass
class ReportingContext:
    """Structured reporting payload used as the only LLM input."""

    generated_at: str
    scenario: dict[str, Any]
    replay_timeline: dict[str, Any]
    deterministic_aar: dict[str, Any] | None
    fused_tracks_evolution: list[dict[str, Any]]
    threat_level_progression: list[dict[str, Any]]
    coa_recommendations_over_time: list[dict[str, Any]]
    selected_recommendation: dict[str, Any] | None
    operational_effects: dict[str, Any]
    asset_assignments: list[dict[str, Any]]
    roe_status: dict[str, Any]
    current_targets: list[dict[str, Any]]
    current_fused_tracks: list[dict[str, Any]]
    current_assets: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "scenario": self.scenario,
            "replay_timeline": self.replay_timeline,
            "deterministic_aar": self.deterministic_aar,
            "fused_tracks_evolution": self.fused_tracks_evolution,
            "threat_level_progression": self.threat_level_progression,
            "coa_recommendations_over_time": self.coa_recommendations_over_time,
            "selected_recommendation": self.selected_recommendation,
            "operational_effects": self.operational_effects,
            "asset_assignments": self.asset_assignments,
            "roe_status": self.roe_status,
            "current_targets": self.current_targets,
            "current_fused_tracks": self.current_fused_tracks,
            "current_assets": self.current_assets,
        }


def _roe_summary(scored: list[Any]) -> dict[str, Any]:
    counts = {"allowed": 0, "restricted": 0, "requires_authorization": 0, "rejected": 0}
    coas: list[dict[str, Any]] = []
    for item in scored:
        status = item.coa.roe_status
        counts[status] = counts.get(status, 0) + 1
        coas.append({
            "coa_id": item.coa.coa_id,
            "title": item.coa.title,
            "rank": item.rank,
            "score": round(item.total_score, 1),
            "roe_status": status,
            "roe_reason": item.coa.roe_reason,
            "constraints": item.coa.roe_constraints_triggered,
            "feasibility_score": round(item.coa.feasibility_score, 3),
        })
    return {"counts": counts, "coas": coas}


def _recommendation_to_dict(recommendation: Any | None) -> dict[str, Any] | None:
    if recommendation is None:
        return None
    if not recommendation.recommended:
        return {
            "status": recommendation.status,
            "message": recommendation.message,
            "reason": recommendation.reason,
            "recommended": None,
        }
    item = recommendation.recommended
    return {
        "status": recommendation.status,
        "message": recommendation.message,
        "reason": recommendation.reason,
        "recommended": {
            "coa_id": item.coa.coa_id,
            "title": item.coa.title,
            "rank": item.rank,
            "score": round(item.total_score, 1),
            "roe_status": item.coa.roe_status,
            "roe_reason": item.coa.roe_reason,
            "success_probability": round(item.simulation.success_probability, 3),
            "feasibility_score": round(item.coa.feasibility_score, 3),
            "assigned_assets": item.coa.assigned_assets,
            "missing_assets": item.coa.missing_assets,
        },
        "rationale": recommendation.rationale,
        "edge_cases": recommendation.edge_cases,
    }


def build_reporting_context() -> ReportingContext:
    store = get_state_store()
    state = store.state
    timeline = get_replay_store().get_timeline()
    snapshots = timeline.snapshots
    scored = store.get_scored_coas()
    recommendation = store.get_recommendation()
    targets = store.get_targets()
    fused_tracks = store.get_fused_tracks()
    operational_effects = getattr(store, "_operational_effects", None)

    deterministic_aar = generate_aar(timeline).to_dict() if snapshots else None
    asset_assignments = []
    for target in targets:
        if target.supporting_asset:
            asset_assignments.append({
                "target_id": target.id,
                "priority_level": target.priority_level,
                "recommended_action": target.recommended_action.replace("_", " "),
                "roe_status": target.roe_status,
                "supporting_asset": target.supporting_asset.to_dict(),
            })

    return ReportingContext(
        generated_at=datetime.now(timezone.utc).isoformat(),
        scenario=state.scenario.model_dump(mode="json"),
        replay_timeline=timeline.to_dict(),
        deterministic_aar=deterministic_aar,
        fused_tracks_evolution=[
            {
                "tick": snap.tick,
                "timestamp": snap.timestamp,
                "fused_tracks_count": snap.fused_tracks_count,
                "contacts_count": snap.contacts_count,
            }
            for snap in snapshots
        ],
        threat_level_progression=[
            {
                "tick": snap.tick,
                "timestamp": snap.timestamp,
                "threat_level": snap.threat_level,
                "top_threat_entity": snap.top_threat_entity,
                "top_threat_probability": snap.top_threat_probability,
                "threat_count": snap.threat_count,
            }
            for snap in snapshots
        ],
        coa_recommendations_over_time=[
            {
                "tick": snap.tick,
                "timestamp": snap.timestamp,
                "coa_id": snap.recommended_coa_id,
                "title": snap.recommended_coa_title,
                "score": snap.recommended_coa_score,
                "roe_status": snap.recommended_roe_status,
                "optimized_variant_id": snap.optimized_variant_id,
                "optimized_variant_score": snap.optimized_variant_score,
            }
            for snap in snapshots
        ],
        selected_recommendation=_recommendation_to_dict(recommendation),
        operational_effects=operational_effects.to_dict() if operational_effects else {},
        asset_assignments=asset_assignments,
        roe_status=_roe_summary(scored),
        current_targets=[target.to_dict() for target in targets[:10]],
        current_fused_tracks=[track.to_dict() for track in fused_tracks[:10]],
        current_assets=[asset.model_dump(mode="json") for asset in store.get_asset_states()],
    )
