from __future__ import annotations

import json
import time
from dataclasses import dataclass

from ..i18n.languages import resolve_language
from .llm_client import LLMResult
from .llm_guardrails import LLM_DATA_GUARDRAILS, explanation_references_match, sanitize_llm_text
from .llm_orchestrator import get_llm_orchestrator
from .reporting_context import ReportingContext


SYSTEM_PROMPT_AAR = """You are generating a NATO-style After Action Report.

Rules:
- Use ONLY provided structured data
- Do NOT invent facts
- Do NOT contradict values
- Do NOT speculate beyond data
- Maintain formal operational tone
- No first-person language
- No new recommendations outside system output
- {data_guardrails}
"""


@dataclass
class GeneratedReport:
    text: str
    mode: str
    llm_used: bool
    fallback_reason: str | None
    duration_ms: int

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "mode": self.mode,
            "llm_used": self.llm_used,
            "fallback_reason": self.fallback_reason,
            "duration_ms": self.duration_ms,
        }


def _payload(context: ReportingContext) -> str:
    return json.dumps(context.to_dict(), ensure_ascii=False, indent=2, default=str)


def deterministic_aar(context: ReportingContext) -> str:
    data = context.to_dict()
    aar = data.get("deterministic_aar") or {}
    scenario = data["scenario"]
    rec = data.get("selected_recommendation") or {}
    recommended = rec.get("recommended") or {}
    effects = data.get("operational_effects") or {}
    roe = data.get("roe_status", {}).get("counts", {})

    sections = [
        ("1. Executive Summary", aar.get("situation_summary") or "No replay data available for detailed after-action assessment."),
        ("2. Operational Timeline Overview", _lines(data["replay_timeline"].get("snapshots", [])[-10:], "tick", "threat_level")),
        ("3. Threat Evolution Analysis", _lines(data["threat_level_progression"][-10:], "tick", "threat_level")),
        ("4. System Response and COA Adaptation", _lines(data["coa_recommendations_over_time"][-10:], "tick", "title")),
        ("5. Key Decision Points", _list(aar.get("decisions_recommended", []))),
        ("6. Operational Effects Assessment", _list(effects.get("active_effects", [])) or "No active operational effects recorded."),
        ("7. Risk and Escalation Analysis", _list(aar.get("remaining_risks", [])) or f"ROE status counts: {roe}."),
        ("8. Lessons Learned", _list(aar.get("lessons_learned", [])) or "No deterministic lessons recorded."),
        (
            "9. Final Operational Assessment",
            (
                f"Scenario {scenario.get('scenario_name') or scenario.get('scenario_id') or 'unknown'} ended with "
                f"recommendation {recommended.get('title') or rec.get('message') or 'none'} and assessment confidence "
                f"{aar.get('assessment_confidence', 'low')}."
            ),
        ),
    ]
    return "\n\n".join(f"{title}\n{text}" for title, text in sections)


def _list(items: list) -> str:
    return "\n".join(f"- {item}" for item in items if item)


def _lines(items: list[dict], key_a: str, key_b: str) -> str:
    if not items:
        return "No timeline entries available."
    return "\n".join(f"- {key_a} {item.get(key_a, 'N/A')}: {item.get(key_b, 'N/A')}" for item in items)


def _valid_output(text: str, context: ReportingContext) -> bool:
    data = context.to_dict()
    threat_level = (data.get("threat_level_progression") or [{}])[-1].get("threat_level")
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
        threat_level=threat_level,
        valid_target_ids=valid_targets,
        valid_coa_ids=valid_coas,
    )


def generate_aar_report(context: ReportingContext, language: str = "en") -> GeneratedReport:
    started = time.monotonic()
    language_code, language_name = resolve_language(language)
    user_prompt = f"""Generate a detailed After Action Report.

Language: {language_name}

Use this structure:

1. Executive Summary
2. Operational Timeline Overview
3. Threat Evolution Analysis
4. System Response and COA Adaptation
5. Key Decision Points
6. Operational Effects Assessment
7. Risk and Escalation Analysis
8. Lessons Learned
9. Final Operational Assessment

Data:
{_payload(context)}
"""
    result: LLMResult = get_llm_orchestrator().run_chat(
        task_type="aar",
        language=language_code,
        system_prompt=SYSTEM_PROMPT_AAR.format(data_guardrails=LLM_DATA_GUARDRAILS),
        user_prompt=user_prompt,
        max_tokens=2200,
    )
    duration_ms = int((time.monotonic() - started) * 1000)
    if result.ok:
        text = sanitize_llm_text(result.text)
        if _valid_output(text, context):
            return GeneratedReport(text=text, mode="aar", llm_used=True, fallback_reason=None, duration_ms=duration_ms)
        return GeneratedReport(
            text=deterministic_aar(context),
            mode="aar",
            llm_used=False,
            fallback_reason="llm_state_mismatch",
            duration_ms=duration_ms,
        )
    return GeneratedReport(
        text=deterministic_aar(context),
        mode="aar",
        llm_used=False,
        fallback_reason=result.fallback_reason,
        duration_ms=duration_ms,
    )
