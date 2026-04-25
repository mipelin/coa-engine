from __future__ import annotations

import json
import logging

from .llm_client import get_llm_client
from ..core.schemas import OperationalEvent, ThreatResult

logger = logging.getLogger("coa_engine.engine.llm_narrative")

SYSTEM_PROMPT_THREAT = """You are an operational intelligence analyst for NATO DIANA.
Write a concise threat narrative summary in 2-3 paragraphs based on the threat data.
Use advisory language only: "assessed as", "estimated probability", "indications suggest".
Never use: target, weapon, strike, engage, kill, lethal, fire, destroy, neutralize."""

SYSTEM_PROMPT_BRIEFING = """You are a staff officer producing a commander decision-support briefing for NATO DIANA.
Enhance the briefing text with deeper operational analysis in 2-3 paragraphs.
Focus on implications, patterns, and recommended commander attention areas.
Use advisory language only. Never use: target, weapon, strike, engage, kill, lethal, fire, destroy, neutralize."""

SYSTEM_PROMPT_ENTITY = """You are an operational intelligence analyst for NATO DIANA.
Write a 1-2 sentence risk narrative for a specific entity, explaining why it is assessed as a threat.
Use advisory language: "estimated", "assessed as", "indicators suggest".
Never use: target, weapon, strike, engage, kill, lethal, fire, destroy, neutralize."""


def enrich_threat_narrative(threats: list[ThreatResult], events: list[OperationalEvent]) -> str | None:
    """LLM produces a natural-language threat summary."""
    llm = get_llm_client()

    threat_text = "\n".join(
        f"- {t.entity_id}: {t.threat_probability:.0%} ({t.threat_level.value}), "
        f"drivers: {', '.join(t.main_drivers[:3])}"
        for t in threats[:8]
    )
    user_prompt = f"""Threat assessment results for {len(events)} events across {len(threats)} threat entities:

{threat_text}

Provide a concise threat narrative summary."""

    result = llm.chat_sync(SYSTEM_PROMPT_THREAT, user_prompt)
    if result:
        logger.info("Threat narrative enriched (%d chars)", len(result))
    return result


def enrich_briefing(briefing_text: str, threat_context: str) -> str | None:
    """LLM enhances a commander briefing with deeper analysis."""
    llm = get_llm_client()

    user_prompt = f"""Current briefing:
{briefing_text}

Threat context:
{threat_context}

Provide additional operational analysis and commander attention areas."""

    result = llm.chat_sync(SYSTEM_PROMPT_BRIEFING, user_prompt)
    if result:
        logger.info("Briefing enriched (%d chars)", len(result))
    return result


def entity_risk_narrative(entity_id: str, threat: ThreatResult, events: list[OperationalEvent]) -> str | None:
    """LLM explains risk per entity in plain language."""
    llm = get_llm_client()

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

Provide a 1-2 sentence risk narrative for this entity."""

    result = llm.chat_sync(SYSTEM_PROMPT_ENTITY, user_prompt)
    if result:
        logger.info("Entity narrative for %s (%d chars)", entity_id, len(result))
    return result
