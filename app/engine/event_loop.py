from __future__ import annotations

import logging
import json
from typing import Any

from ..core.config import settings
from ..i18n.languages import final_language_instruction, resolve_language
from ..core.schemas import Recommendation
from .event_bus import Event, EventKind, get_event_bus
from .explanation import generate_briefing
from .llm_narrative import build_compact_briefing_context, enrich_threat_narrative
from .llm_orchestrator import get_llm_orchestrator
from .analysis_service import AnalysisContext, run_canonical_analysis
from .targeting import serialize_targets
from .replay import capture_snapshot, get_replay_store
from .state_store import get_state_store

logger = logging.getLogger("coa_engine.engine.event_loop")


class EventLoop:
    """Main analysis event loop — reactive + periodic."""

    def __init__(self) -> None:
        self._store = get_state_store()
        self._bus = get_event_bus()
        self._analysis_interval_ticks: int = 3
        self._analysis_event_window: int = settings.analysis_event_window
        self._min_ticks_between_llm: int = 5
        self._last_llm_tick: int = -999
        self._llm_calls: int = 0
        self._last_analysis_tick: int = -999

        # Track reactive analysis results for run_tick() reporting
        self._reactive_analysis_ran: bool = False
        self._reactive_threat_changed: bool = False
        self._reactive_coa_changed: bool = False
        self._reactive_llm_called: bool = False
        self._last_reason_summary: str = "No major change yet."
        self._last_analysis_trigger: str | None = None
        self._last_event_summary_event_id: str | None = None

        self._bus.subscribe(EventKind.CONTACT_RECEIVED, self._on_contact)

    def set_analysis_interval(self, ticks: int) -> None:
        self._analysis_interval_ticks = max(ticks, 1)

    def reset_runtime_state(self) -> None:
        self._last_llm_tick = -999
        self._llm_calls = 0
        self._last_analysis_tick = -999
        self._reactive_analysis_ran = False
        self._reactive_threat_changed = False
        self._reactive_coa_changed = False
        self._reactive_llm_called = False
        self._last_reason_summary = "No major change yet."
        self._last_analysis_trigger = None
        self._last_event_summary_event_id = None
        get_replay_store().clear()

    def _on_contact(self, event: Event) -> None:
        """Reactive handler — trigger analysis on significant contacts."""
        contact = event.payload
        if contact is None:
            return

        contact_type = getattr(contact, "contact_type", None)
        if hasattr(contact_type, "value"):
            contact_type = contact_type.value

        is_significant = (
            getattr(contact, "is_hostile", False)
            or contact_type in ("cable_event", "jamming")
            or (getattr(contact, "attributes", {}) or {}).get("heading_toward_infra", False)
            or (getattr(contact, "attributes", {}) or {}).get("is_loitering", False)
        )

        if not is_significant:
            return

        current_tick = self._store.get_tick()
        ticks_since = current_tick - self._last_analysis_tick

        if ticks_since >= 1:
            result = self._run_analysis(current_tick, trigger="significant_contact")
            self._reactive_analysis_ran = True
            self._reactive_threat_changed = self._reactive_threat_changed or result["threat_changed"]
            self._reactive_coa_changed = self._reactive_coa_changed or result["coa_changed"]
            self._reactive_llm_called = self._reactive_llm_called or result["llm_called"]

    def run_tick(self) -> dict[str, Any]:
        """Run one tick of the event loop. Called by the scheduler."""
        tick = self._store.advance_tick()

        ticks_since = tick - self._last_analysis_tick
        periodic_due = ticks_since >= self._analysis_interval_ticks
        reactive_pending = self._reactive_analysis_ran
        should_analyze = periodic_due or reactive_pending

        analysis_run = should_analyze
        threat_changed = self._reactive_threat_changed
        coa_changed = self._reactive_coa_changed
        llm_called = self._reactive_llm_called
        if should_analyze:
            analysis_trigger = "periodic" if periodic_due else "reactive_complete"
            periodic_result = self._run_analysis(tick, trigger=analysis_trigger)
            threat_changed = threat_changed or periodic_result["threat_changed"]
            coa_changed = coa_changed or periodic_result["coa_changed"]
            llm_called = llm_called or periodic_result["llm_called"]

        # Merge reactive results from _on_contact that fired during engine.tick()
        analysis_run = analysis_run or self._reactive_analysis_ran

        # Reset reactive tracking
        self._reactive_analysis_ran = False
        self._reactive_threat_changed = False
        self._reactive_coa_changed = False
        self._reactive_llm_called = False

        result: dict[str, Any] = {
            "tick": tick,
            "active_contacts": self._store.state.active_contacts,
            "threat_level": self._store.state.current_threat_level,
            "recommended_coa": self._store.state.recommended_coa_id,
            "analysis_run": analysis_run,
            "llm_called": llm_called,
            "threat_changed": threat_changed,
            "coa_changed": coa_changed,
            "llm_calls_total": self._llm_calls,
            "trigger": self._last_analysis_trigger,
            "reason_summary": self._last_reason_summary,
        }

        return result

    def run_analysis_now(self, trigger: str = "manual") -> dict[str, Any]:
        """Force an analysis pass without advancing the engine tick."""
        tick = self._store.get_tick()
        result = self._run_analysis(tick, trigger=trigger)
        state = self._store.state
        recommendation = self._store.get_recommendation()
        return {
            "tick": tick,
            "analysis_run": True,
            "threat_changed": result["threat_changed"],
            "coa_changed": result["coa_changed"],
            "llm_called": result["llm_called"],
            "threat_level": state.current_threat_level,
            "recommended_coa": state.recommended_coa_id,
            "trigger": self._last_analysis_trigger,
            "reason_summary": self._last_reason_summary,
            "recommended_package": (
                recommendation.recommended_package.package_id
                if recommendation and recommendation.recommended_package
                else None
            ),
        }

    def _run_analysis(self, tick: int, trigger: str) -> dict[str, bool]:
        """Run the full analysis pipeline on current state."""
        self._last_analysis_tick = tick
        self._last_analysis_trigger = trigger
        events = self._store.contact_history_as_events(limit=self._analysis_event_window)
        infrastructure = self._store.get_infrastructure()

        if not events:
            return {"threat_changed": False, "coa_changed": False, "llm_called": False}

        logger.debug("Tick %d: running analysis (%s, %d events)", tick, trigger, len(events))

        analysis = run_canonical_analysis(
            AnalysisContext(
                events=events,
                infrastructure=infrastructure or None,
                scenario_state=self._store.state.scenario,
                asset_inventory=self._store.get_asset_inventory() or None,
                asset_states=self._store.get_asset_states() or None,
                active_contacts=self._store.get_contacts() or None,
                source="live_event_loop",
                tick=tick,
                scenario_id=self._store.state.scenario.scenario_id,
                scenario_name=self._store.state.scenario.scenario_name,
            )
        )
        threats = analysis.threats
        anomalies = analysis.anomalies
        fused_tracks = analysis.fused_tracks
        targets = analysis.targets
        coas = analysis.coas
        sims = analysis.simulations
        scored = analysis.scored_coas
        rec = analysis.recommendation
        top_threat = threats[0] if threats else None
        top_drivers = ", ".join(top_threat.main_drivers[:2] if top_threat else [])
        top_coa_tradeoff = rec.recommended.tradeoff_explanation if rec and rec.recommended else "No recommendation"
        self._last_reason_summary = (
            f"Trigger {trigger}. "
            f"Top threat: {top_threat.entity_id if top_threat else 'none'} "
            f"at {top_threat.threat_probability:.0%}. "
            f"Drivers: {top_drivers or 'no strong drivers'}. "
            f"Recommendation basis: {top_coa_tradeoff}."
        )

        # Mark analysis as completed at this tick
        self._store.mark_analysis_completed(tick)

        # Update state and detect changes
        previous_state = self._store.state
        threat_changed, coa_changed, roe_changed = self._store.update_analysis(
            threats,
            anomalies,
            scored,
            rec,
            coas,
            sims,
            targets=targets,
            fused_tracks=fused_tracks,
        )

        # Persist COA optimization result
        if analysis.coa_optimization is not None:
            self._store._coa_optimization = analysis.coa_optimization

        # Persist operational effects
        if analysis.operational_effects is not None:
            self._store._operational_effects = analysis.operational_effects

        # Capture replay snapshot
        key_changes: list[str] = []
        if threat_changed:
            key_changes.append(f"Threat level changed to {threats[0].threat_level.value if threats else 'LOW'}")
        if coa_changed:
            key_changes.append(f"Recommendation changed to {rec.recommended.coa.title if rec and rec.recommended else 'none'}")
        if roe_changed:
            new_roe = rec.recommended.coa.roe_status if rec and rec.recommended else None
            key_changes.append(f"ROE status changed to {new_roe}")

        snapshot = capture_snapshot(
            tick,
            threats=threats,
            scored=scored,
            recommendation=rec,
            coa_optimization=analysis.coa_optimization,
            fused_tracks=fused_tracks,
            targets=targets,
            contacts=self._store.get_contacts(),
            operational_effects=analysis.operational_effects,
            scenario_id=self._store.state.scenario.scenario_id,
            key_changes=key_changes if key_changes else None,
            trigger=trigger,
        )
        get_replay_store().add_snapshot(snapshot)

        # Publish change events
        if threat_changed:
            self._bus.publish(Event(
                kind=EventKind.THREAT_LEVEL_CHANGED,
                payload={
                    "old_level": previous_state.current_threat_level,
                    "new_level": threats[0].threat_level.value if threats else "LOW",
                    "trigger": trigger,
                },
                tick=tick,
            ))
            logger.info("Tick %d: THREAT LEVEL CHANGED → %s", tick,
                        threats[0].threat_level.value if threats else "LOW")

        if coa_changed:
            self._bus.publish(Event(
                kind=EventKind.COA_RANK_CHANGED,
                payload={
                    "new_coa_id": rec.recommended.coa.coa_id if rec and rec.recommended else None,
                    "score": rec.recommended.total_score if rec and rec.recommended else 0.0,
                    "trigger": trigger,
                },
                tick=tick,
            ))
            logger.info("Tick %d: COA RANK CHANGED → %s", tick,
                        rec.recommended.coa.coa_id if rec and rec.recommended else "None")

        # LLM: only on meaningful changes
        ticks_since_llm = tick - self._last_llm_tick
        should_llm = (
            threat_changed
            or coa_changed
            or (ticks_since_llm >= self._min_ticks_between_llm and trigger == "periodic" and tick > 0 and tick % 10 == 0)
        )

        llm_called = False
        if should_llm and ticks_since_llm >= self._min_ticks_between_llm:
            llm_called = self._run_llm_enrichment(tick, threats, events, rec)

        self._enqueue_event_summary_if_needed(
            tick=tick,
            trigger=trigger,
            events=events,
            threats=threats,
            scored=scored,
            recommendation=rec,
            threat_changed=threat_changed,
            coa_changed=coa_changed,
            roe_changed=roe_changed,
        )

        self._bus.publish(Event(
            kind=EventKind.ANALYSIS_CYCLE,
            payload={
                "tick": tick, "trigger": trigger,
                "threat_changed": threat_changed, "coa_changed": coa_changed,
                "llm_called": llm_called,
                "reason_summary": self._last_reason_summary,
            },
            tick=tick,
        ))
        return {
            "threat_changed": threat_changed,
            "coa_changed": coa_changed,
            "llm_called": llm_called,
        }

    def _enqueue_event_summary_if_needed(
        self,
        *,
        tick: int,
        trigger: str,
        events,
        threats,
        scored,
        recommendation: Recommendation,
        threat_changed: bool,
        coa_changed: bool,
        roe_changed: bool,
    ) -> None:
        meaningful_types = {
            "cable_severance": "cable_severance",
            "jamming_detected": "jamming_detected",
            "uav_detection": "uav_detection",
            "vessel_course_change": "vessel_course_change_toward_infrastructure",
            "convoy_sighting": "convoy_sighting",
            "hostile_intent": "hostile_intent_observed",
        }
        latest_event = events[-1] if events else None
        event_type = None
        if latest_event and latest_event.event_id != self._last_event_summary_event_id:
            mapped = meaningful_types.get(latest_event.event_type.value)
            if mapped:
                event_type = mapped
                self._last_event_summary_event_id = latest_event.event_id
        if threat_changed:
            event_type = event_type or "threat_level_change"
        if coa_changed:
            event_type = event_type or "recommended_coa_change"
        if roe_changed:
            event_type = event_type or "roe_status_change"
        if not event_type:
            return

        top_threat = threats[0] if threats else None
        top_coas = [
            {
                "rank": s.rank,
                "title": s.coa.title,
                "score": round(s.total_score, 1),
                "roe_status": s.coa.roe_status,
            }
            for s in scored[:3]
        ]
        context = {
            "tick": tick,
            "trigger": trigger,
            "event_type": event_type,
            "latest_event": {
                "type": latest_event.event_type.value,
                "entity_id": latest_event.entity_id,
                "description": latest_event.description,
            } if latest_event else None,
            "threat_level": self._store.state.current_threat_level,
            "top_threat": {
                "entity_id": top_threat.entity_id,
                "level": top_threat.threat_level.value,
                "probability": f"{top_threat.threat_probability:.0%}",
            } if top_threat else None,
            "recommended_coa": recommendation.recommended.coa.title if recommendation.recommended else "None",
            "recommended_roe_status": recommendation.recommended.coa.roe_status if recommendation.recommended else "unknown",
            "top_coas": top_coas,
            "active_incidents": self._store.state.scenario.active_incidents,
        }
        get_llm_orchestrator().enqueue_event_summary(
            tick=tick,
            event_type=event_type,
            language=self._store.get_ui_language(),
            context=context,
        )

    def _run_llm_enrichment(
        self, tick: int, threats, events, rec: Recommendation,
    ) -> bool:
        """Call LLM only when triggered by a meaningful change. Returns True if called."""
        self._last_llm_tick = tick
        self._llm_calls += 1
        self._store._state.llm_calls_made = self._llm_calls

        logger.info("Tick %d: running LLM enrichment", tick)

        try:
            threat_narrative = enrich_threat_narrative(threats, events)
            if threat_narrative and rec.recommended:
                rec = rec.model_copy(update={"threat_narrative": threat_narrative})
                self._store.update_recommendation(rec)
            return True
        except Exception as e:
            logger.warning("LLM enrichment failed: %s", e)
            return False

    def run_full_briefing(self, scenario_name: str = "Operational Area", language: str = "en") -> dict[str, Any]:
        """Generate a full briefing with LLM enrichment — only on explicit request."""
        threats = self._store.get_threats()
        scored = self._store.get_scored_coas()
        rec = self._store.get_recommendation()
        events = self._store.contacts_as_events()
        analysis = run_canonical_analysis(
            AnalysisContext(
                events=events,
                infrastructure=self._store.get_infrastructure() or None,
                scenario_state=self._store.state.scenario,
                asset_inventory=self._store.get_asset_inventory() or None,
                asset_states=self._store.get_asset_states() or None,
                active_contacts=self._store.get_contacts() or None,
                source="briefing",
                tick=self._store.get_tick(),
                scenario_id=self._store.state.scenario.scenario_id,
                scenario_name=self._store.state.scenario.scenario_name,
            )
        )
        anomalies = analysis.anomalies
        if not threats:
            threats = analysis.threats
        if not scored:
            scored = analysis.scored_coas
        if not rec:
            rec = analysis.recommendation

        if not rec:
            return {"error": "No recommendation available yet"}

        language_code, _ = resolve_language(language)
        language_instruction = final_language_instruction(language_code)
        logger.info(
            "briefing_language: task_type=briefing requested_language=%s resolved_language=%s prompt_language_instruction=%s",
            language,
            language_code,
            language_instruction,
        )
        briefing = generate_briefing(events, anomalies, threats, scored, rec, scenario_name, language=language_code)

        llm_used = False
        llm_enriched = False
        fallback_reason: str | None = "llm_disabled"

        from ..core.config import settings as _settings
        if _settings.llm_enabled:
            fallback_reason = None

        if _settings.llm_enabled:
            # Build compact context instead of sending full briefing text
            scored_data = [
                {
                    "rank": s.rank,
                    "title": s.coa.title,
                    "score": s.total_score,
                    "success_prob": f"{s.simulation.success_probability:.0%}",
                    "roe_status": s.coa.roe_status,
                    "roe_reason": s.coa.roe_reason,
                }
                for s in scored
            ]
            threats_data = [
                {
                    "entity_id": t.entity_id,
                    "level": t.threat_level.value,
                    "probability": f"{t.threat_probability:.0%}",
                    "drivers": t.main_drivers[:3],
                }
                for t in threats
            ]
            roe_counts: dict[str, int] = {"allowed": 0, "restricted": 0, "requires_authorization": 0, "rejected": 0}
            for s in scored:
                status = s.coa.roe_status
                roe_counts[status] = roe_counts.get(status, 0) + 1

            fired_stimuli = []
            active_stimuli = []
            try:
                from .contact_engine import get_contact_engine
                engine = get_contact_engine()
                if engine._sim is not None:
                    fired_stimuli = engine._sim.fired_stimuli_list
                    active_stimuli = engine._sim.active_stimuli_list
            except Exception:
                pass

            compact = build_compact_briefing_context(
                threat_level=self._store.state.current_threat_level,
                top_threats=threats_data,
                top_coas=scored_data,
                recommended_coa=(
                    {
                        "title": rec.recommended.coa.title,
                        "score": f"{rec.recommended.total_score:.1f}",
                        "roe_status": rec.recommended.coa.roe_status,
                        "rationale": rec.rationale,
                    } if rec.recommended else None
                ),
                roe_summary={"counts": roe_counts},
                active_stimuli=active_stimuli,
                fired_stimuli=fired_stimuli,
                tick=self._store.get_tick(),
                scenario_name=scenario_name,
                infrastructure_status=self._store.state.scenario.infrastructure_status,
                active_incidents=self._store.state.scenario.active_incidents,
                key_risks=briefing.risks,
                forecast_summary=rec.edge_cases or None,
                fused_tracks=[track.to_dict() for track in analysis.fused_tracks[:5]],
                top_targets=serialize_targets(analysis.top_targets),
                operational_effects=analysis.operational_effects.to_dict() if analysis.operational_effects else {},
                optimization_summary={
                    "best_variant": (
                        analysis.coa_optimization.best_variant.model_dump(mode="json")
                        if analysis.coa_optimization and analysis.coa_optimization.best_variant else None
                    ),
                    "optimized_variants": (
                        [item.model_dump(mode="json") for item in analysis.coa_optimization.optimized_variants[:3]]
                        if analysis.coa_optimization else []
                    ),
                },
            )

            logger.info(
                "briefing: llm_enabled=true llm_call_attempted=true language=%s context_chars=%d",
                language_code, len(compact),
            )
            system_prompt = (
                "You are a NATO operational analyst preparing a commander-level briefing.\n\n"
                "Your role:\n"
                "- Explain the situation clearly and concisely\n"
                "- Support decision-making\n"
                "- Do NOT give orders\n"
                "- Do NOT authorize actions\n"
                "- Do NOT invent facts beyond provided context\n\n"
                "IMPORTANT:\n"
                "- You must respond in the requested language\n"
                "- Keep tone professional, operational, and concise\n"
                "- Avoid unnecessary jargon\n"
                "- Avoid speculation not grounded in provided data\n\n"
                "Return ONLY valid JSON with these exact keys:\n"
                "situation (string), recent_developments (array of strings), assessment (string), "
                "key_actors (array of strings), recommended_coa (string), roe_status (string), "
                "risks (array of strings), assumptions (array of strings), confidence (string), "
                "what_changed (array of strings).\n\n"
                "Map the required commander sections into those JSON fields as follows:\n"
                "- SITUATION OVERVIEW -> situation\n"
                "- RECENT DEVELOPMENTS -> recent_developments and what_changed\n"
                "- THREAT ASSESSMENT -> assessment\n"
                "- KEY ACTORS -> key_actors\n"
                "- RECOMMENDED COURSE OF ACTION -> recommended_coa\n"
                "- ROE STATUS -> roe_status\n"
                "- RISKS AND NEXT DEVELOPMENTS -> risks and assumptions\n\n"
                "STYLE RULES:\n"
                "- Use short paragraphs in each string item\n"
                "- Avoid bullet spam\n"
                "- Be readable by a commander under time pressure\n"
                "- Keep it concise but informative\n\n"
                "DO NOT:\n"
                "- generate new COAs\n"
                "- change recommendations\n"
                "- bypass ROE\n"
                "- use the LLM as a decision-maker\n\n"
                "ONLY explain the current system state. "
                f"{language_instruction}"
            )
            result = get_llm_orchestrator().run_chat(
                task_type="briefing",
                language=language_code,
                system_prompt=system_prompt,
                user_prompt=f"Structured context:\n{compact}",
                max_tokens=700,
            )
            if result.ok:
                parsed_text = result.text.strip()
                if "```" in parsed_text:
                    parsed_text = parsed_text.split("```")[1]
                    if parsed_text.startswith("json"):
                        parsed_text = parsed_text[4:]
                try:
                    parsed = json.loads(parsed_text)
                    briefing = briefing.model_copy(update={
                        "situation": parsed.get("situation") or briefing.situation,
                        "what_changed": parsed.get("what_changed") or briefing.what_changed,
                        "recent_developments": parsed.get("recent_developments") or briefing.recent_developments,
                        "assessment": parsed.get("assessment") or briefing.assessment,
                        "key_actors": parsed.get("key_actors") or briefing.key_actors,
                        "recommended_coa": parsed.get("recommended_coa") or briefing.recommended_coa,
                        "roe_status": parsed.get("roe_status") or briefing.roe_status,
                        "risks": parsed.get("risks") or briefing.risks,
                        "assumptions": parsed.get("assumptions") or briefing.assumptions,
                        "confidence": parsed.get("confidence") or briefing.confidence,
                    })
                    llm_enriched = True
                    llm_used = True
                    fallback_reason = None
                    logger.info("briefing: llm_used=true llm_enriched=true")
                except json.JSONDecodeError:
                    fallback_reason = "llm_model_error"
                    logger.warning("briefing: invalid JSON from LLM")
            else:
                fallback_reason = result.fallback_reason
                logger.warning("briefing: llm_used=false fallback_reason=%s", fallback_reason)
        else:
            logger.info("briefing: llm_enabled=false, using deterministic briefing")

        briefing = briefing.model_copy(update={
            "llm_used": llm_used,
            "llm_enriched": llm_enriched,
            "fallback_reason": fallback_reason,
            "language_used": language_code,
        })

        self._llm_calls += 1
        self._store._state.llm_calls_made = self._llm_calls

        return {
            "briefing": briefing.model_dump(mode="json"),
            "llm_calls_total": self._llm_calls,
        }


_loop: EventLoop | None = None


def get_event_loop() -> EventLoop:
    global _loop
    if _loop is None:
        _loop = EventLoop()
    return _loop
