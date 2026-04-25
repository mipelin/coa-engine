from __future__ import annotations

import json
import logging
import re

from .coa_generation import generate_coas as rule_based_generate
from .llm_client import get_llm_client
from ..core.schemas import CourseOfAction, OperationalEvent, ThreatResult

logger = logging.getLogger("coa_engine.engine.llm_coa_generation")

SYSTEM_PROMPT = """You are an advisory military decision-support assistant for NATO DIANA.
Generate courses of action (COAs) based on the threat picture provided.
Rules:
- All COAs are ADVISORY ONLY. Never suggest offensive action.
- Use language like "recommend", "consider", "monitor", "coordinate", "observe".
- Never use words: target, weapon, strike, engage, kill, lethal, fire, destroy, neutralize, execute order.
- Each COA must be a JSON object with: title, description, required_assets (list), assumptions (list), estimated_time_minutes (int), expected_effect, risk_categories (list), escalation_risk (0-1 float), civilian_risk (0-1 float), logistics_burden (0-1 float).
- Output a JSON array of COA objects, nothing else.
- Generate 3-6 COAs appropriate to the threat situation.
- Focus on observation, protection, monitoring, coordination, and information sharing."""


def _build_threat_context(events: list[OperationalEvent], threats: list[ThreatResult]) -> str:
    lines = [f"Events: {len(events)} total"]
    lines.append(f"Threats: {len(threats)} entities")
    for t in threats[:5]:
        lines.append(
            f"- {t.entity_id}: {t.threat_probability:.0%} probability ({t.threat_level.value}), "
            f"drivers: {', '.join(t.main_drivers[:3])}"
        )
    event_types = {}
    for e in events:
        label = e.event_type.value
        event_types[label] = event_types.get(label, 0) + 1
    lines.append(f"Event types: {json.dumps(event_types)}")
    entity_types = {}
    for e in events:
        label = e.entity_type.value
        entity_types[label] = entity_types.get(label, 0) + 1
    lines.append(f"Entity types: {json.dumps(entity_types)}")
    return "\n".join(lines)


def _extract_json_array(text: str) -> list[dict]:
    """Extract JSON array from LLM response, handling markdown fences."""
    # Try to find JSON array in response
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    # Try parsing the whole text
    return json.loads(text)


def generate_coas_with_llm(
    events: list[OperationalEvent],
    threats: list[ThreatResult],
    asset_inventory: dict[str, int] | None = None,
) -> list[CourseOfAction]:
    """Generate COAs using LLM, falling back to rule-based generation."""
    llm = get_llm_client()

    threat_summary = _build_threat_context(events, threats)

    user_prompt = f"""Threat picture summary:
{threat_summary}

Available assets: {json.dumps(asset_inventory or {})}

Generate advisory COAs as a JSON array. Each COA must have: title, description, required_assets, assumptions, estimated_time_minutes, expected_effect, risk_categories, escalation_risk, civilian_risk, logistics_burden."""

    response = llm.chat_sync(SYSTEM_PROMPT, user_prompt)

    if response is None:
        logger.info("LLM unavailable, falling back to rule-based COA generation")
        return rule_based_generate(events, threats, asset_inventory)

    try:
        coas_data = _extract_json_array(response)
        if not isinstance(coas_data, list) or not coas_data:
            raise ValueError("Empty or invalid COA list")

        coas = []
        for i, c in enumerate(coas_data):
            if not isinstance(c, dict):
                continue
            coa = CourseOfAction(
                coa_id=f"COA-LLM-{i + 1:03d}",
                title=str(c.get("title", f"LLM Generated COA {i + 1}")),
                description=str(c.get("description", "")),
                required_assets=c.get("required_assets", []) if isinstance(c.get("required_assets"), list) else [],
                assumptions=c.get("assumptions", []) if isinstance(c.get("assumptions"), list) else [],
                estimated_time_minutes=int(c.get("estimated_time_minutes", 60)),
                expected_effect=str(c.get("expected_effect", "")),
                risk_categories=c.get("risk_categories", []) if isinstance(c.get("risk_categories"), list) else [],
                escalation_risk=min(max(float(c.get("escalation_risk", 0.1)), 0.0), 1.0),
                civilian_risk=min(max(float(c.get("civilian_risk", 0.0)), 0.0), 1.0),
                logistics_burden=min(max(float(c.get("logistics_burden", 0.3)), 0.0), 1.0),
            )
            coas.append(coa)

        if not coas:
            logger.warning("LLM returned no valid COAs, falling back")
            return rule_based_generate(events, threats, asset_inventory)

        # Apply asset feasibility
        from .coa_generation import _normalize_asset_inventory, _apply_asset_feasibility
        required_assets = {asset for coa in coas for asset in coa.required_assets}
        normalized = _normalize_asset_inventory(asset_inventory, required_assets)
        result = [_apply_asset_feasibility(coa, normalized) for coa in coas]
        logger.info("LLM generated %d COAs", len(result))
        return result

    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        logger.warning("Failed to parse LLM COAs: %s, falling back", e)
        return rule_based_generate(events, threats, asset_inventory)
