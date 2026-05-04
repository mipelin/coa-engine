from __future__ import annotations

import json
import logging

from .llm_guardrails import LLM_DATA_GUARDRAILS, explanation_references_match, sanitize_llm_text
from .llm_client import LLMResult
from .llm_orchestrator import get_llm_orchestrator
from ..core.schemas import OperationalEvent, ThreatResult
from ..i18n.languages import LANGUAGE_NAMES, final_language_instruction, resolve_language

logger = logging.getLogger("coa_engine.engine.llm_narrative")

SYSTEM_PROMPT_THREAT = """You are an operational intelligence analyst for NATO DIANA.
Write a concise threat narrative summary in 2-3 paragraphs based on the threat data.
Use advisory language only: "assessed as", "estimated probability", "indications suggest".
Never use: target, weapon, strike, engage, kill, lethal, fire, destroy, neutralize.

{data_guardrails}

{language_instruction}"""

SYSTEM_PROMPT_BRIEFING_COMPACT = """You are a staff officer producing a commander decision-support briefing for NATO DIANA.
Based on the structured operational context below, produce a concise commander briefing.
Focus on implications, patterns, and recommended commander attention areas.
Use advisory language only. Never use: target, weapon, strike, engage, kill, lethal, fire, destroy, neutralize.
Keep your response to 3-5 paragraphs maximum.
If the input mixes languages, keep the response entirely in the requested language.

{data_guardrails}

{language_instruction}"""

SYSTEM_PROMPT_ENTITY = """You are an operational intelligence analyst for NATO DIANA.
Write a 1-2 sentence risk narrative for a specific entity, explaining why it is assessed as a threat.
Use advisory language: "estimated", "assessed as", "indicators suggest".
Never use: target, weapon, strike, engage, kill, lethal, fire, destroy, neutralize.

{data_guardrails}

{language_instruction}"""


def deterministic_threat_narrative(
    threats: list[ThreatResult],
    events: list[OperationalEvent],
) -> str:
    if not threats:
        return "Based on the current system state, no active threat entities are assessed at this time."
    top = threats[0]
    event_count = len(events)
    drivers = ", ".join(top.main_drivers[:3]) or "no dominant drivers recorded"
    return (
        f"Based on the current system state, the threat picture is led by {top.entity_id} at "
        f"{top.threat_probability:.0%} probability with overall level {top.threat_level.value}. "
        f"Primary indicators are {drivers}. "
        f"The assessment is drawn from {len(threats)} tracked threat entities across {event_count} current events."
    )


def deterministic_entity_risk_narrative(
    entity_id: str,
    threat: ThreatResult,
) -> str:
    drivers = ", ".join(threat.main_drivers[:3]) or "recorded indicators"
    return (
        f"Based on the current system state, {entity_id} is assessed at {threat.threat_probability:.0%} "
        f"probability with {threat.threat_level.value} threat level. "
        f"Key drivers are {drivers}."
    )


def enrich_threat_narrative(
    threats: list[ThreatResult],
    events: list[OperationalEvent],
    *,
    language: str = "en",
) -> str | None:
    """LLM produces a natural-language threat summary."""
    language_code, language_name = resolve_language(language)
    threat_text = "\n".join(
        f"- {t.entity_id}: {t.threat_probability:.0%} ({t.threat_level.value}), "
        f"drivers: {', '.join(t.main_drivers[:3])}"
        for t in threats[:8]
    )
    user_prompt = f"""Threat assessment results for {len(events)} events across {len(threats)} threat entities:

{threat_text}

Provide a concise threat narrative summary in {language_name}."""

    result = get_llm_orchestrator().run_chat(
        task_type="threat_narrative",
        language=language_code,
        system_prompt=SYSTEM_PROMPT_THREAT.format(
            language_instruction=final_language_instruction(language_code),
            data_guardrails=LLM_DATA_GUARDRAILS,
        ),
        user_prompt=user_prompt,
        max_tokens=320,
    )
    if result.ok:
        text = sanitize_llm_text(result.text)
        if explanation_references_match(
            text,
            threat_level=threats[0].threat_level.value if threats else None,
            valid_target_ids={t.entity_id for t in threats},
        ):
            logger.info("Threat narrative enriched (%d chars)", len(text))
            return text
        logger.warning("Threat narrative validation failed; using deterministic fallback")
    return deterministic_threat_narrative(threats, events)


def build_compact_briefing_context(
    threat_level: str,
    top_threats: list[dict],
    top_coas: list[dict],
    recommended_coa: dict | None,
    roe_summary: dict,
    active_stimuli: list[dict],
    fired_stimuli: list[dict],
    tick: int = 0,
    scenario_name: str = "",
    infrastructure_status: str = "nominal",
    active_incidents: list[str] | None = None,
    key_risks: list[str] | None = None,
    forecast_summary: str | None = None,
    fused_tracks: list[dict] | None = None,
    top_targets: list[dict] | None = None,
    operational_effects: dict | None = None,
    optimization_summary: dict | None = None,
) -> str:
    """Build a compact structured context string for briefing LLM call."""
    lines = [
        f"=== OPERATIONAL SNAPSHOT (Tick {tick}) ===",
        f"Scenario: {scenario_name}",
        f"Threat Level: {threat_level}",
        f"Infrastructure: {infrastructure_status}",
    ]
    if active_incidents:
        lines.append(f"Active Incidents: {', '.join(active_incidents)}")

    if top_threats:
        lines.append("\n--- TOP THREATS ---")
        for t in top_threats[:5]:
            lines.append(
                f"  {t.get('entity_id', '?')}: {t.get('level', '?')} "
                f"({t.get('probability', '?')}), "
                f"drivers: {', '.join(t.get('drivers', [])[:3])}, "
                f"location: {t.get('location', 'Unknown location')}"
            )

    if top_coas:
        lines.append("\n--- TOP COAs ---")
        for c in top_coas[:3]:
            roe = c.get("roe_status", "?")
            line = (
                f"  #{c.get('rank', '?')} {c.get('title', '?')} "
                f"(score {c.get('score', 0):.1f}, success {c.get('success_prob', '?')}, "
                f"ROE: {roe})"
            )
            if roe != "allowed" and c.get("roe_reason"):
                line += f" — {c['roe_reason']}"
            lines.append(line)

    if fused_tracks:
        lines.append("\n--- FUSED TRACKS ---")
        for track in fused_tracks[:5]:
            lines.append(
                f"  {track.get('track_id', '?')}: {track.get('track_type', '?')} / "
                f"{track.get('primary_entity_id', '?')}, confidence {track.get('fused_confidence', 0):.0%}, "
                f"sources {track.get('source_count', 0)} ({', '.join(track.get('sources', [])[:4])}), "
                f"location: {track.get('location', 'Unknown location')}"
            )
            if track.get("rationale"):
                lines.append(f"      Rationale: {track['rationale']}")

    if top_targets:
        lines.append("\n--- TOP TARGETS ---")
        for target in top_targets[:5]:
            lines.append(
                f"  {target.get('id', target.get('entity_id', '?'))}: "
                f"{target.get('priority_level', '?')} priority, "
                f"threat {target.get('threat_score', 0):.2f}, "
                f"action {str(target.get('recommended_action', '?')).replace('_', ' ')}, "
                f"ROE {target.get('roe_status', '?')}, "
                f"location: {target.get('location', 'Unknown location')}"
            )
            support = target.get("supporting_asset")
            if support:
                lines.append(
                    f"      Supporting asset: {support.get('assigned_asset_id', 'none')} "
                    f"({support.get('asset_type', 'none')}) for {support.get('assignment_role', 'monitor')}"
                )
            if target.get("rationale"):
                lines.append(f"      Rationale: {target['rationale']}")
    if recommended_coa:
        lines.append(
            "\n--- RECOMMENDED COA ---\n"
            f"  {recommended_coa.get('title', '?')} "
            f"(score {recommended_coa.get('score', '?')}, "
            f"ROE: {recommended_coa.get('roe_status', '?')})"
        )
        if recommended_coa.get("rationale"):
            lines.append(f"  Rationale: {recommended_coa['rationale']}")

    if roe_summary:
        counts = roe_summary.get("counts", {})
        lines.append(
            f"\n--- ROE SUMMARY ---\n"
            f"  Allowed: {counts.get('allowed', 0)}, "
            f"Restricted: {counts.get('restricted', 0)}, "
            f"Requires Auth: {counts.get('requires_authorization', 0)}, "
            f"Rejected: {counts.get('rejected', 0)}"
        )

    if active_stimuli:
        lines.append(f"\n--- ACTIVE STIMULI ({len(active_stimuli)}) ---")
        for s in active_stimuli[:5]:
            lines.append(f"  {s.get('action', '?')} (entity: {s.get('entity', 'N/A')})")

    if fired_stimuli:
        lines.append(f"\n--- RECENT STIMULI ---")
        for s in fired_stimuli[-5:]:
            lines.append(f"  Tick {s.get('tick', '?')}: {s.get('action', '?')}")

    if key_risks:
        lines.append("\n--- KEY RISKS ---")
        for risk in key_risks[:5]:
            lines.append(f"  {risk}")

    if operational_effects:
        lines.append("\n--- OPERATIONAL EFFECTS ---")
        active = operational_effects.get("active_effects", [])
        if active:
            lines.append(f"  Active effects: {', '.join(active[:6])}")
        lines.append(
            f"  Detection {operational_effects.get('threat_detection_modifier', 1.0):.2f}, "
            f"COA success {operational_effects.get('coa_success_modifier', 1.0):.2f}, "
            f"Time {operational_effects.get('coa_time_modifier', 1.0):.2f}, "
            f"Risk {operational_effects.get('coa_risk_modifier', 1.0):.2f}"
        )

    if optimization_summary:
        lines.append("\n--- OPTIMIZED VARIANTS ---")
        best = optimization_summary.get("best_variant")
        if best:
            lines.append(
                f"  Best variant: {best.get('coa', {}).get('title', best.get('coa_id', '?'))} "
                f"(score {best.get('total_score', 0):.1f})"
            )
        for variant in optimization_summary.get("optimized_variants", [])[:3]:
            lines.append(
                f"  {variant.get('coa', {}).get('title', '?')}: "
                f"score {variant.get('total_score', 0):.1f}, "
                f"success {variant.get('simulation', {}).get('success_probability', 0):.0%}, "
                f"escalation {variant.get('simulation', {}).get('escalation_probability', 0):.0%}"
            )
            if variant.get("tradeoff_explanation"):
                lines.append(f"      Why: {variant['tradeoff_explanation']}")

    if forecast_summary:
        lines.append(f"\n--- FORECAST SUMMARY ---\n  {forecast_summary}")

    return "\n".join(lines)


def enrich_briefing_compact(
    compact_context: str,
    language: str = "en",
    max_tokens: int | None = None,
) -> LLMResult:
    """Single-pass briefing enrichment. Generates directly in the target language."""
    language_code, _ = resolve_language(language)
    system_prompt = SYSTEM_PROMPT_BRIEFING_COMPACT.format(
        language_instruction=final_language_instruction(language_code),
        data_guardrails=LLM_DATA_GUARDRAILS,
    )
    result = get_llm_orchestrator().run_chat(
        task_type="briefing",
        language=language_code,
        system_prompt=system_prompt,
        user_prompt=compact_context,
        max_tokens=max_tokens,
    )
    if result.ok:
        logger.info("Briefing enriched in %s (%d chars)", LANGUAGE_NAMES.get(language_code, "English"), len(result.text))
    else:
        logger.warning("Briefing enrichment failed: %s", result.fallback_reason)
    return result


def enrich_briefing(briefing_text: str, threat_context: str, language: str = "en") -> str | None:
    """Legacy wrapper — kept for backward compat. Returns text only."""
    compact = f"Current briefing:\n{briefing_text}\n\nThreat context:\n{threat_context}"
    result = enrich_briefing_compact(compact, language=language)
    return result.text


def translate_briefing(briefing: "Briefing", language: str) -> dict | None:
    """Translate all briefing text fields to the target language via LLM. Returns a dict of translated fields."""
    if language == "en":
        return None
    lang_name = LANGUAGE_NAMES.get(language, "English")

    fields = json.dumps({
        "situation": briefing.situation,
        "key_indicators": briefing.key_indicators,
        "assessment": briefing.assessment,
        "coas_considered": briefing.coas_considered,
        "recommended_coa": briefing.recommended_coa,
        "risks": briefing.risks,
        "assumptions": briefing.assumptions,
    }, ensure_ascii=False, indent=2)

    system_prompt = (
        "You are a professional NATO military translator. "
        "Translate the following commander briefing fields into "
        f"{lang_name}. Preserve military terminology accuracy. "
        "Use advisory language only. Never use: target, weapon, strike, engage, kill, lethal, fire, destroy, neutralize.\n"
        "You MUST respond with ONLY a valid JSON object with these exact keys: "
        "situation, key_indicators, assessment, coas_considered, recommended_coa, risks, assumptions. "
        "key_indicators, coas_considered, risks, and assumptions must be arrays of strings. "
        "All other fields must be strings. Do not include any text outside the JSON object."
    )

    user_prompt = f"Translate this briefing to {lang_name}:\n\n{fields}"

    result = get_llm_orchestrator().run_chat(
        task_type="translation",
        language=language,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=900,
    )
    if not result.ok:
        logger.warning("Briefing translation to %s failed: %s", lang_name, result.fallback_reason)
        return None

    response = result.text
    try:
        if "```" in response:
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        parsed = json.loads(response)
        logger.info("Briefing translated to %s (%d chars)", lang_name, len(response))
        return parsed
    except (json.JSONDecodeError, IndexError) as exc:
        logger.warning("Failed to parse translated briefing JSON: %s", exc)
        return None


def translate_ui_strings(strings: dict[str, str], language: str) -> dict[str, str] | None:
    """Translate UI strings to the target language via LLM in batches."""
    if language == "en" or not strings:
        return None
    lang_name = LANGUAGE_NAMES.get(language, "English")

    items = list(strings.items())
    batch_size = 100
    result: dict[str, str] = {}

    for i in range(0, len(items), batch_size):
        batch = dict(items[i:i + batch_size])
        batch_json = json.dumps(batch, ensure_ascii=False, indent=2)

        system_prompt = (
            "You are a professional NATO military UI translator. "
            f"Translate the following UI strings into {lang_name}. "
            "Preserve military terminology. Keep translations concise for UI labels. "
            "You MUST respond with ONLY a valid JSON object with the EXACT SAME keys. "
            "Each value must be the translated string. Do not include any text outside the JSON object."
        )
        user_prompt = f"Translate these UI strings to {lang_name}:\n\n{batch_json}"

        llm_result = get_llm_orchestrator().run_chat(
            task_type="translation",
            language=language,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=900,
        )
        if not llm_result.ok:
            logger.warning("UI translation batch to %s failed: %s", lang_name, llm_result.fallback_reason)
            continue
        try:
            response = llm_result.text
            if "```" in response:
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            parsed = json.loads(response)
            result.update(parsed)
            logger.info("UI strings translated to %s, batch %d (%d strings)", lang_name, i // batch_size, len(parsed))
        except (json.JSONDecodeError, IndexError) as exc:
            logger.warning("Failed to parse translated UI strings: %s", exc)
            continue

    return result if result else None


def entity_risk_narrative(
    entity_id: str,
    threat: ThreatResult,
    events: list[OperationalEvent],
    *,
    language: str = "en",
) -> str | None:
    """LLM explains risk per entity in plain language."""
    language_code, language_name = resolve_language(language)
    entity_events = [e for e in events if e.entity_id == entity_id]
    event_summary = "\n".join(
        f"- {e.timestamp.strftime('%HZ')}: {e.event_type.value} — {e.description[:100]}"
        for e in entity_events[:5]
    )

    user_prompt = f"""Entity: {entity_id}
Threat probability: {threat.threat_probability:.0%} ({threat.threat_level.value})
Drivers: {', '.join(t for t in threat.main_drivers)}
Recent events:
{event_summary}

Provide a 1-2 sentence risk narrative for this entity in {language_name}."""

    result = get_llm_orchestrator().run_chat(
        task_type="entity_risk",
        language=language_code,
        system_prompt=SYSTEM_PROMPT_ENTITY.format(
            language_instruction=final_language_instruction(language_code),
            data_guardrails=LLM_DATA_GUARDRAILS,
        ),
        user_prompt=user_prompt,
        max_tokens=200,
    )
    if result.ok:
        text = sanitize_llm_text(result.text)
        if explanation_references_match(
            text,
            threat_level=threat.threat_level.value,
            valid_target_ids={entity_id},
        ):
            logger.info("Entity narrative for %s (%d chars)", entity_id, len(text))
            return text
        logger.warning("Entity narrative validation failed for %s; using deterministic fallback", entity_id)
    return deterministic_entity_risk_narrative(entity_id, threat)
