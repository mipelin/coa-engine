from __future__ import annotations

import json
import time

from ..i18n.languages import resolve_language
from .aar_generator import GeneratedReport
from .llm_guardrails import LLM_DATA_GUARDRAILS, explanation_references_match, sanitize_llm_text
from .llm_orchestrator import get_llm_orchestrator
from .reporting_context import ReportingContext


SYSTEM_PROMPT_BRIEFING_EXTENDED = """You are generating a NATO commander briefing.

Rules:
- Use ONLY structured data
- Be concise and decision-focused
- Prioritize clarity over completeness
- No invented facts
- No speculation
- No first-person language
- {data_guardrails}
"""


def deterministic_briefing(context: ReportingContext) -> str:
    data = context.to_dict()
    scenario = data["scenario"]
    latest_threat = (data.get("threat_level_progression") or [{}])[-1]
    rec = data.get("selected_recommendation") or {}
    recommended = rec.get("recommended") or {}
    effects = data.get("operational_effects") or {}
    aar = data.get("deterministic_aar") or {}

    return "\n\n".join([
        f"1. Situation Overview\nScenario: {scenario.get('scenario_name') or scenario.get('scenario_id') or 'unknown'}. Replay snapshots: {data['replay_timeline'].get('snapshot_count', 0)}.",
        f"2. Current Threat Assessment\nThreat level: {latest_threat.get('threat_level', 'LOW')}. Top threat: {latest_threat.get('top_threat_entity') or 'none recorded'}.",
        f"3. Key Developments\n{_list(aar.get('major_events', [])) or 'No major replay events recorded.'}",
        f"4. Recommended Course of Action\n{recommended.get('title') or rec.get('message') or 'No current recommendation available.'}",
        f"5. Risk Summary\n{_list(aar.get('remaining_risks', [])) or _list(effects.get('active_effects', [])) or 'No active risks recorded in structured data.'}",
        f"6. Confidence Level\n{aar.get('assessment_confidence', 'low')}",
    ])


def _list(items: list) -> str:
    return "\n".join(f"- {item}" for item in items if item)


def _valid_output(text: str, context: ReportingContext) -> bool:
    data = context.to_dict()
    latest_threat = (data.get("threat_level_progression") or [{}])[-1].get("threat_level")
    valid_targets = {item.get("entity_id") or item.get("id") for item in data.get("current_targets", [])}
    valid_targets.discard(None)
    valid_coas = {
        item.get("coa_id")
        for item in data.get("coa_recommendations_over_time", [])
        if item.get("coa_id")
    }
    rec = data.get("selected_recommendation") or {}
    if rec.get("recommended"):
        valid_coas.add(rec["recommended"].get("coa_id"))
    return explanation_references_match(
        text,
        threat_level=latest_threat,
        valid_target_ids=valid_targets,
        valid_coa_ids=valid_coas,
    )


def generate_briefing_report(context: ReportingContext, language: str = "en") -> GeneratedReport:
    started = time.monotonic()
    language_code, language_name = resolve_language(language)
    structured_json_payload = json.dumps(context.to_dict(), ensure_ascii=False, indent=2, default=str)
    user_prompt = f"""Generate a commander-level briefing.

Language: {language_name}

Structure:

1. Situation Overview
2. Current Threat Assessment
3. Key Developments
4. Recommended Course of Action
5. Risk Summary
6. Confidence Level

Keep it concise, operational, and actionable.

Data:
{structured_json_payload}
"""
    result = get_llm_orchestrator().run_chat(
        task_type="briefing_extended",
        language=language_code,
        system_prompt=SYSTEM_PROMPT_BRIEFING_EXTENDED.format(data_guardrails=LLM_DATA_GUARDRAILS),
        user_prompt=user_prompt,
        max_tokens=750,
    )
    duration_ms = int((time.monotonic() - started) * 1000)
    if result.ok:
        text = sanitize_llm_text(result.text)
        if _valid_output(text, context):
            return GeneratedReport(text=text, mode="briefing", llm_used=True, fallback_reason=None, duration_ms=duration_ms)
        return GeneratedReport(
            text=deterministic_briefing(context),
            mode="briefing",
            llm_used=False,
            fallback_reason="llm_state_mismatch",
            duration_ms=duration_ms,
        )
    return GeneratedReport(
        text=deterministic_briefing(context),
        mode="briefing",
        llm_used=False,
        fallback_reason=result.fallback_reason,
        duration_ms=duration_ms,
    )
