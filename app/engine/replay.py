"""Replay, after-action review, and lessons-learned workflow.

Captures compact operational snapshots after each analysis cycle and produces
deterministic after-action reviews. No LLM calls.

Guarantees:
- Snapshots are compact (no raw event histories).
- AAR is fully deterministic given the same timeline.
- No LLM in replay or AAR logic.
- Snapshot count capped at replay_max_snapshots.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..core.config import settings

logger = logging.getLogger("coa_engine.engine.replay")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ReplaySnapshot:
    """Compact snapshot of engine state at a single analysis cycle."""
    tick: int
    timestamp: str = ""
    scenario_id: str | None = None
    threat_level: str = "LOW"
    top_threat_entity: str | None = None
    top_threat_probability: float = 0.0
    threat_count: int = 0
    top_targets: list[dict[str, Any]] = field(default_factory=list)
    recommended_coa_id: str | None = None
    recommended_coa_title: str | None = None
    recommended_coa_score: float = 0.0
    recommended_roe_status: str = "unknown"
    optimized_variant_id: str | None = None
    optimized_variant_score: float = 0.0
    roe_summary: dict[str, int] = field(default_factory=dict)
    fused_tracks_count: int = 0
    operational_effects_summary: dict[str, Any] = field(default_factory=dict)
    key_events: list[str] = field(default_factory=list)
    key_changes: list[str] = field(default_factory=list)
    contacts_count: int = 0
    coas_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick": self.tick,
            "timestamp": self.timestamp,
            "scenario_id": self.scenario_id,
            "threat_level": self.threat_level,
            "top_threat_entity": self.top_threat_entity,
            "top_threat_probability": round(self.top_threat_probability, 3),
            "threat_count": self.threat_count,
            "top_targets": self.top_targets,
            "recommended_coa_id": self.recommended_coa_id,
            "recommended_coa_title": self.recommended_coa_title,
            "recommended_coa_score": round(self.recommended_coa_score, 1),
            "recommended_roe_status": self.recommended_roe_status,
            "optimized_variant_id": self.optimized_variant_id,
            "optimized_variant_score": round(self.optimized_variant_score, 1),
            "roe_summary": self.roe_summary,
            "fused_tracks_count": self.fused_tracks_count,
            "operational_effects_summary": self.operational_effects_summary,
            "key_events": self.key_events,
            "key_changes": self.key_changes,
            "contacts_count": self.contacts_count,
            "coas_count": self.coas_count,
        }


@dataclass
class ReplayTimeline:
    """Ordered sequence of replay snapshots for a scenario."""
    scenario_id: str | None = None
    snapshots: list[ReplaySnapshot] = field(default_factory=list)
    start_tick: int = 0
    end_tick: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "snapshot_count": len(self.snapshots),
            "start_tick": self.start_tick,
            "end_tick": self.end_tick,
            "snapshots": [s.to_dict() for s in self.snapshots],
        }


@dataclass
class AfterActionReview:
    """Deterministic after-action review of a replay timeline."""
    scenario_id: str | None = None
    duration_ticks: int = 0
    situation_summary: str = ""
    major_events: list[str] = field(default_factory=list)
    threat_evolution: list[dict[str, Any]] = field(default_factory=list)
    recommendation_timeline: list[dict[str, Any]] = field(default_factory=list)
    target_evolution: list[dict[str, Any]] = field(default_factory=list)
    effects_observed: list[str] = field(default_factory=list)
    decisions_recommended: list[str] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)
    remaining_risks: list[str] = field(default_factory=list)
    assessment_confidence: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "duration_ticks": self.duration_ticks,
            "situation_summary": self.situation_summary,
            "major_events": self.major_events,
            "threat_evolution": self.threat_evolution,
            "recommendation_timeline": self.recommendation_timeline,
            "target_evolution": self.target_evolution,
            "effects_observed": self.effects_observed,
            "decisions_recommended": self.decisions_recommended,
            "lessons_learned": self.lessons_learned,
            "remaining_risks": self.remaining_risks,
            "assessment_confidence": self.assessment_confidence,
        }


# ---------------------------------------------------------------------------
# Snapshot capture
# ---------------------------------------------------------------------------


def capture_snapshot(
    tick: int,
    *,
    threats: list[Any] | None = None,
    scored: list[Any] | None = None,
    recommendation: Any | None = None,
    coa_optimization: Any | None = None,
    fused_tracks: list[Any] | None = None,
    targets: list[Any] | None = None,
    contacts: list[Any] | None = None,
    operational_effects: Any | None = None,
    scenario_id: str | None = None,
    key_changes: list[str] | None = None,
    trigger: str = "",
) -> ReplaySnapshot:
    """Build a compact snapshot from current analysis state."""
    threat_level = "LOW"
    top_threat_entity = None
    top_threat_prob = 0.0
    if threats:
        threat_level = threats[0].threat_level.value
        top_threat_entity = threats[0].entity_id
        top_threat_prob = threats[0].threat_probability

    rec_coa_id = None
    rec_coa_title = None
    rec_score = 0.0
    rec_roe = "unknown"
    if recommendation and recommendation.recommended:
        rec_coa_id = recommendation.recommended.coa.coa_id
        rec_coa_title = recommendation.recommended.coa.title
        rec_score = recommendation.recommended.total_score
        rec_roe = recommendation.recommended.coa.roe_status

    opt_id = None
    opt_score = 0.0
    if coa_optimization and coa_optimization.best_variant:
        opt_id = coa_optimization.best_variant.coa.coa_id
        opt_score = coa_optimization.best_variant.total_score

    roe_summary: dict[str, int] = {"allowed": 0, "restricted": 0, "requires_authorization": 0, "rejected": 0}
    for s in (scored or []):
        status = s.coa.roe_status
        if status in roe_summary:
            roe_summary[status] += 1

    top_targets = []
    for t in (targets or [])[:5]:
        top_targets.append({
            "entity_id": t.id,
            "priority_level": t.priority_level,
            "recommended_action": t.recommended_action,
        })

    opfx_summary: dict[str, Any] = {}
    if operational_effects is not None:
        opfx_summary = {
            "overall_effectiveness": round(operational_effects.overall_effectiveness, 3),
            "coa_success_modifier": round(operational_effects.coa_success_modifier, 3),
            "active_effects": operational_effects.active_effects,
        }

    # Key events from recent events — extract event types
    key_events: list[str] = []
    if trigger and trigger not in ("periodic", "manual"):
        key_events.append(f"Analysis triggered by: {trigger}")

    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat()

    return ReplaySnapshot(
        tick=tick,
        timestamp=ts,
        scenario_id=scenario_id,
        threat_level=threat_level,
        top_threat_entity=top_threat_entity,
        top_threat_probability=top_threat_prob,
        threat_count=len(threats or []),
        top_targets=top_targets,
        recommended_coa_id=rec_coa_id,
        recommended_coa_title=rec_coa_title,
        recommended_coa_score=rec_score,
        recommended_roe_status=rec_roe,
        optimized_variant_id=opt_id,
        optimized_variant_score=opt_score,
        roe_summary=roe_summary,
        fused_tracks_count=len(fused_tracks or []),
        operational_effects_summary=opfx_summary,
        key_events=key_events,
        key_changes=key_changes or [],
        contacts_count=len(contacts or []),
        coas_count=len(scored or []),
    )


# ---------------------------------------------------------------------------
# Replay store (in-memory, per scenario)
# ---------------------------------------------------------------------------


class ReplayStore:
    """In-memory store for replay snapshots with optional persistence."""

    def __init__(self) -> None:
        self._snapshots: list[ReplaySnapshot] = []
        self._scenario_id: str | None = None
        self._loaded_from_db: bool = False

    def _ensure_loaded(self) -> None:
        if self._loaded_from_db:
            return
        self._loaded_from_db = True
        if not settings.persistence_enabled:
            return
        try:
            from .persistence import get_persistent_store
            store = get_persistent_store()
            raw = store.load_replay_snapshots()
            if raw:
                for d in raw:
                    snap = ReplaySnapshot(**{k: v for k, v in d.items()
                                             if k in ReplaySnapshot.__dataclass_fields__})
                    self._snapshots.append(snap)
                if self._snapshots:
                    self._scenario_id = self._snapshots[-1].scenario_id
                logger.info("Replay: loaded %d snapshots from DB", len(raw))
        except Exception:
            logger.debug("Replay: no persisted snapshots or persistence unavailable")

    def _persist_snapshot(self, snapshot: ReplaySnapshot) -> None:
        if not settings.persistence_enabled:
            return
        try:
            from .persistence import get_persistent_store
            store = get_persistent_store()
            store.save_replay_snapshot(snapshot.to_dict())
            store.cap_replay_snapshots(settings.replay_max_snapshots)
        except Exception:
            logger.debug("Replay: failed to persist snapshot")

    def add_snapshot(self, snapshot: ReplaySnapshot) -> None:
        self._ensure_loaded()
        max_snap = settings.replay_max_snapshots
        self._snapshots.append(snapshot)
        if snapshot.scenario_id:
            self._scenario_id = snapshot.scenario_id
        # Cap: trim oldest
        if len(self._snapshots) > max_snap:
            self._snapshots = self._snapshots[-max_snap:]
        self._persist_snapshot(snapshot)
        logger.debug("Replay snapshot captured at tick %d (%d total)", snapshot.tick, len(self._snapshots))

    def get_timeline(self) -> ReplayTimeline:
        self._ensure_loaded()
        if not self._snapshots:
            return ReplayTimeline(scenario_id=self._scenario_id)
        return ReplayTimeline(
            scenario_id=self._scenario_id,
            snapshots=list(self._snapshots),
            start_tick=self._snapshots[0].tick,
            end_tick=self._snapshots[-1].tick,
        )

    def get_snapshot(self, tick: int) -> ReplaySnapshot | None:
        self._ensure_loaded()
        for s in self._snapshots:
            if s.tick == tick:
                return s
        return None

    def get_snapshots_range(self, start_tick: int | None = None, end_tick: int | None = None) -> list[ReplaySnapshot]:
        result = self._snapshots
        if start_tick is not None:
            result = [s for s in result if s.tick >= start_tick]
        if end_tick is not None:
            result = [s for s in result if s.tick <= end_tick]
        return result

    @property
    def snapshot_count(self) -> int:
        self._ensure_loaded()
        return len(self._snapshots)

    @property
    def first_tick(self) -> int | None:
        self._ensure_loaded()
        return self._snapshots[0].tick if self._snapshots else None

    @property
    def last_tick(self) -> int | None:
        self._ensure_loaded()
        return self._snapshots[-1].tick if self._snapshots else None

    def clear(self) -> None:
        self._snapshots.clear()
        self._scenario_id = None
        if settings.persistence_enabled:
            try:
                from .persistence import get_persistent_store
                get_persistent_store().clear_replay_snapshots()
            except Exception:
                pass

    def get_last_major_change(self) -> dict[str, Any] | None:
        """Return the last snapshot where a key change was recorded."""
        for s in reversed(self._snapshots):
            if s.key_changes:
                return {"tick": s.tick, "changes": s.key_changes}
        return None

    def get_latest_lesson(self) -> str | None:
        """Extract the most recent lesson from the timeline."""
        timeline = self.get_timeline()
        if not timeline.snapshots:
            return None
        aar = generate_aar(timeline)
        if aar.lessons_learned:
            return aar.lessons_learned[-1]
        return None


_replay_store: ReplayStore | None = None


def get_replay_store() -> ReplayStore:
    global _replay_store
    if _replay_store is None:
        _replay_store = ReplayStore()
    return _replay_store


# ---------------------------------------------------------------------------
# After-action review generation
# ---------------------------------------------------------------------------


_THREAT_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def generate_aar(timeline: ReplayTimeline) -> AfterActionReview:
    """Generate a deterministic after-action review from a replay timeline.

    No LLM calls. All analysis is rule-based.
    """
    snapshots = timeline.snapshots
    aar = AfterActionReview(
        scenario_id=timeline.scenario_id,
        duration_ticks=timeline.end_tick - timeline.start_tick if snapshots else 0,
    )

    if not snapshots:
        aar.situation_summary = "No replay data available."
        aar.assessment_confidence = "low"
        return aar

    first = snapshots[0]
    last = snapshots[-1]

    # --- Situation summary ---
    aar.situation_summary = _build_situation_summary(snapshots)

    # --- Major events ---
    aar.major_events = _extract_major_events(snapshots)

    # --- Threat evolution ---
    aar.threat_evolution = _extract_threat_evolution(snapshots)

    # --- Recommendation timeline ---
    aar.recommendation_timeline = _extract_recommendation_timeline(snapshots)

    # --- Target evolution ---
    aar.target_evolution = _extract_target_evolution(snapshots)

    # --- Effects observed ---
    aar.effects_observed = _extract_effects_observed(snapshots)

    # --- Decisions recommended ---
    aar.decisions_recommended = _extract_decisions_recommended(snapshots)

    # --- Lessons learned ---
    aar.lessons_learned = _extract_lessons_learned(snapshots)

    # --- Remaining risks ---
    aar.remaining_risks = _extract_remaining_risks(last, snapshots)

    # --- Assessment confidence ---
    aar.assessment_confidence = _compute_assessment_confidence(snapshots)

    return aar


def _build_situation_summary(snapshots: list[ReplaySnapshot]) -> str:
    first = snapshots[0]
    last = snapshots[-1]
    duration = last.tick - first.tick
    parts = [
        f"Scenario ran for {duration} ticks ({len(snapshots)} snapshots captured).",
        f"Threat level started at {first.threat_level} and ended at {last.threat_level}.",
    ]
    if first.top_threat_entity:
        parts.append(f"Initial top threat: {first.top_threat_entity} ({first.top_threat_probability:.0%}).")
    if last.top_threat_entity and last.top_threat_entity != first.top_threat_entity:
        parts.append(f"Final top threat: {last.top_threat_entity} ({last.top_threat_probability:.0%}).")
    if first.contacts_count != last.contacts_count:
        parts.append(f"Contacts grew from {first.contacts_count} to {last.contacts_count}.")
    return " ".join(parts)


def _extract_major_events(snapshots: list[ReplaySnapshot]) -> list[str]:
    events: list[str] = []
    for s in snapshots:
        for e in s.key_events:
            events.append(f"Tick {s.tick}: {e}")
        for c in s.key_changes:
            events.append(f"Tick {s.tick}: {c}")
    return events[:30]


def _extract_threat_evolution(snapshots: list[ReplaySnapshot]) -> list[dict[str, Any]]:
    evolution: list[dict[str, Any]] = []
    prev_level = None
    for s in snapshots:
        if s.threat_level != prev_level:
            evolution.append({
                "tick": s.tick,
                "threat_level": s.threat_level,
                "top_threat_entity": s.top_threat_entity,
                "top_threat_probability": round(s.top_threat_probability, 3),
            })
            prev_level = s.threat_level
    return evolution


def _extract_recommendation_timeline(snapshots: list[ReplaySnapshot]) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    prev_coa_id = None
    for s in snapshots:
        if s.recommended_coa_id != prev_coa_id:
            timeline.append({
                "tick": s.tick,
                "coa_id": s.recommended_coa_id,
                "coa_title": s.recommended_coa_title,
                "score": round(s.recommended_coa_score, 1),
                "roe_status": s.recommended_roe_status,
            })
            prev_coa_id = s.recommended_coa_id
    return timeline


def _extract_target_evolution(snapshots: list[ReplaySnapshot]) -> list[dict[str, Any]]:
    evolution: list[dict[str, Any]] = []
    prev_entities: set[str] = set()
    for s in snapshots:
        current_entities = {t["entity_id"] for t in s.top_targets}
        new_entities = current_entities - prev_entities
        if new_entities:
            evolution.append({
                "tick": s.tick,
                "new_targets": sorted(new_entities),
                "total_targets": len(s.top_targets),
            })
        prev_entities = current_entities
    return evolution


def _extract_effects_observed(snapshots: list[ReplaySnapshot]) -> list[str]:
    effects: list[str] = []
    seen: set[str] = set()
    for s in snapshots:
        for e in s.operational_effects_summary.get("active_effects", []):
            if e not in seen:
                effects.append(f"Tick {s.tick}: {e}")
                seen.add(e)
    return effects[:20]


def _extract_decisions_recommended(snapshots: list[ReplaySnapshot]) -> list[str]:
    decisions: list[str] = []
    prev_coa = None
    for s in snapshots:
        if s.recommended_coa_title and s.recommended_coa_title != prev_coa:
            decisions.append(
                f"Tick {s.tick}: Recommended '{s.recommended_coa_title}' "
                f"(score {s.recommended_coa_score:.1f}, ROE: {s.recommended_roe_status})"
            )
            prev_coa = s.recommended_coa_title
    return decisions


def _extract_lessons_learned(snapshots: list[ReplaySnapshot]) -> list[str]:
    lessons: list[str] = []
    first = snapshots[0]
    last = snapshots[-1]

    # Threat escalation lesson
    first_order = _THREAT_ORDER.get(first.threat_level, 0)
    last_order = _THREAT_ORDER.get(last.threat_level, 0)
    if last_order > first_order:
        lessons.append(
            f"Threat level escalated from {first.threat_level} to {last.threat_level} "
            f"during the operation, indicating deteriorating conditions."
        )

    # ROE restrictions
    restricted_ticks = [s for s in snapshots if s.recommended_roe_status != "allowed"]
    if restricted_ticks:
        fraction = len(restricted_ticks) / len(snapshots)
        if fraction > 0.3:
            lessons.append(
                f"ROE restrictions applied in {len(restricted_ticks)}/{len(snapshots)} cycles, "
                f"constraining response options."
            )

    # Operational effects
    all_effects: list[str] = []
    for s in snapshots:
        all_effects.extend(s.operational_effects_summary.get("active_effects", []))
    if any("Jamming" in e for e in all_effects):
        lessons.append("Jamming degraded sensor confidence and increased missed detection risk.")
    if any("Sea state" in e for e in all_effects) and any("sensor effectiveness" in e for e in all_effects):
        lessons.append("Harsh sea state reduced sensor effectiveness and response feasibility.")
    if any("Visibility" in e for e in all_effects):
        lessons.append("Poor visibility reduced ISR confidence and detection capability.")
    if any("storm" in e.lower() or "weather" in e.lower() for e in all_effects):
        lessons.append("Adverse weather limited operational sorties and increased response time.")
    if any("Readiness" in e for e in all_effects):
        lessons.append("Low asset readiness reduced available response options and extended timelines.")
    if any("Distance" in e or "fuel" in e.lower() for e in all_effects):
        lessons.append("Extended logistics distance increased response delays and fuel constraints.")

    # Cable severance
    cable_events = [s for s in snapshots if any("cable" in c.lower() for c in s.key_changes)]
    if cable_events:
        lessons.append("Cable severance shifted recommendation toward infrastructure protection.")

    # Recommendation volatility
    rec_changes = 0
    prev_rec = None
    for s in snapshots:
        if s.recommended_coa_id and s.recommended_coa_id != prev_rec:
            rec_changes += 1
            prev_rec = s.recommended_coa_id
    if rec_changes > len(snapshots) * 0.5 and len(snapshots) > 3:
        lessons.append(
            f"Frequent recommendation changes ({rec_changes} in {len(snapshots)} cycles) "
            f"suggest unstable conditions requiring adaptive planning."
        )

    # COA score trend
    first_scores = [s.recommended_coa_score for s in snapshots[:max(len(snapshots) // 4, 1)]]
    last_scores = [s.recommended_coa_score for s in snapshots[-max(len(snapshots) // 4, 1):]]
    if first_scores and last_scores:
        avg_first = sum(first_scores) / len(first_scores)
        avg_last = sum(last_scores) / len(last_scores)
        if avg_last < avg_first * 0.7:
            lessons.append(
                f"COA effectiveness declined from avg {avg_first:.1f} to {avg_last:.1f}, "
                f"suggesting diminishing response options."
            )

    # Effectiveness degradation
    first_fx = first.operational_effects_summary.get("overall_effectiveness", 1.0)
    last_fx = last.operational_effects_summary.get("overall_effectiveness", 1.0)
    if last_fx < 0.7 and first_fx >= 0.9:
        lessons.append(
            f"Operational conditions degraded significantly (effectiveness {first_fx:.0%} -> {last_fx:.0%})."
        )

    return lessons


def _extract_remaining_risks(last: ReplaySnapshot, snapshots: list[ReplaySnapshot]) -> list[str]:
    risks: list[str] = []

    if last.threat_level in ("HIGH", "CRITICAL"):
        risks.append(f"Threat level remains {last.threat_level} at end of operation.")
    if last.recommended_roe_status != "allowed":
        risks.append(f"ROE status is {last.recommended_roe_status}, limiting response options.")
    if last.operational_effects_summary.get("overall_effectiveness", 1.0) < 0.7:
        risks.append("Operational conditions remain degraded.")
    if last.fused_tracks_count > 0:
        risks.append(f"{last.fused_tracks_count} fused tracks still require monitoring.")
    if last.recommended_coa_score < 40:
        risks.append(f"Top COA scores low ({last.recommended_coa_score:.1f}), limited effective options.")

    # Check if threats were escalating at the end
    if len(snapshots) >= 3:
        recent = snapshots[-3:]
        recent_levels = [_THREAT_ORDER.get(s.threat_level, 0) for s in recent]
        if recent_levels[-1] > recent_levels[0]:
            risks.append("Threat level was still increasing at end of observation window.")

    if not risks:
        risks.append("No significant remaining risks identified at end of observation.")

    return risks


def _compute_assessment_confidence(snapshots: list[ReplaySnapshot]) -> str:
    if len(snapshots) < 3:
        return "low"
    # More snapshots and more consistency = higher confidence
    threat_changes = sum(
        1 for i in range(1, len(snapshots))
        if snapshots[i].threat_level != snapshots[i - 1].threat_level
    )
    volatility = threat_changes / len(snapshots)
    if volatility > 0.4:
        return "low"
    if volatility > 0.2:
        return "medium"
    return "high"
