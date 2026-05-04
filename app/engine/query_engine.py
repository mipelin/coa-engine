"""Natural Language Query layer over current operational state.

Builds structured context from live engine state, routes operator questions
through an LLM for explanation-only answers, and provides deterministic
fallbacks when no LLM is available.

Guardrails:
- Refuses requests to authorize engagement or bypass ROE.
- Refuses requests for lethal targeting orders.
- Never generates, selects, or modifies COAs.
- Never changes engine state.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from ..core.config import settings
from ..i18n.languages import final_language_instruction, resolve_language
from .forecasting import ForecastResult, forecast_for_coa, is_forecast_question, route_forecast_question
from .geo_context import describe_location
from .llm_guardrails import LLM_DATA_GUARDRAILS, explanation_references_match, sanitize_llm_text
from .llm_client import get_llm_client
from .llm_orchestrator import get_llm_orchestrator
from .state_store import get_state_store

logger = logging.getLogger("coa_engine.engine.query_engine")

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

_SPANISH_MARKERS = re.compile(
    r"\b(cual|cuáles|cuántos|dónde|por qué|cómo|qué|cuando|amenaza|"
    r"recomendar|recomendada|recomendado|recomendación|autorización|situación|contacto|"
    r"contactos|cambió|cambios|reciente|recientes|actual|nivel|"
    r"riesgo|peligro|curso de acción|estado|resumen|resumir|"
    r"informe|helicóptero|barco|buque|submarino|drone|activos|activas|"
    r"damé|deme|muéstrame|muestra|reglas|restricciones|"
    r"enfrentamiento|combate|enganche|permitido|restringido|rechazado)\b",
    re.IGNORECASE,
)

_ENGLISH_MARKERS = re.compile(
    r"\b(what|which|why|where|when|how|threat|recommended|recommendation|"
    r"authorization|situation|contact|contacts|changed|recent|current|level|"
    r"risk|danger|course of action|status|summary|report|helicopter|ship|"
    r"vessel|submarine|drone|assets|show me|rules|restrictions|engagement|"
    r"combat|allowed|restricted|rejected)\b",
    re.IGNORECASE,
)


def detect_language(question: str, ui_language_hint: str | None = None, force_language: str | None = None) -> str:
    """Return language code for a question.

    Priority:
    1. force_language — explicit override (e.g. user toggled a language mode)
    2. question text detection — the user's actual words always win
    3. UI language hint — used when the question is ambiguous
    4. fallback to English
    """
    if force_language:
        return resolve_language(force_language)[0]
    if _SPANISH_MARKERS.search(question):
        return "es"
    if _ENGLISH_MARKERS.search(question):
        return "en"
    if ui_language_hint:
        return resolve_language(ui_language_hint)[0]
    return "en"


def resolve_response_language(
    question: str,
    ui_language_hint: str | None = None,
    force_language: str | None = None,
) -> str:
    """Resolve the language used for the response.

    Explicit UI or forced language selection governs the response language.
    Question-language detection is used only when no response language was selected.
    """
    if force_language:
        return resolve_language(force_language)[0]
    if ui_language_hint:
        return resolve_language(ui_language_hint)[0]
    return detect_language(question)

# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------

_REFUSAL_PHRASES = [
    "authorize engagement",
    "bypass roe",
    "override roe",
    "engage target",
    "fire on",
    "launch strike",
    "initiate lethal",
    "execute lethal",
    "destroy target",
    "neutralize target",
    "neutralize the",
    "authorize lethal",
    "approve engagement",
    "weapons free",
    "weapons release",
    "initiate attack",
    "launch attack",
    "execute attack",
    "fire weapons",
    "kill target",
    "kill the",
]

SAFETY_REFUSAL = (
    "This query involves authorizing engagement, bypassing ROE, or generating "
    "targeting orders. The query layer is explanation-only and cannot authorize, "
    "direct, or execute any operational action. Please consult your chain of command "
    "for authorization decisions."
)

SAFETY_REFUSAL_ES = (
    "Esta consulta involucra autorizar un compromiso, eludir las ROE o generar "
    "órdenes de ataque. La capa de consultas es solo explicativa y no puede autorizar, "
    "dirigir ni ejecutar ninguna acción operativa. Consulte su cadena de mando "
    "para decisiones de autorización."
)

SYSTEM_PROMPT_QUERY = """You are an advisory decision-support analyst for NATO DIANA.
Answer the operator's question based ONLY on the structured operational context provided.
Use advisory language: "assessed as", "estimated", "indicators suggest".
Never use: target, weapon, strike, engage, kill, lethal, fire, destroy, neutralize.

Rules:
- You are explanation-only. You cannot authorize, direct, or execute any action.
- You must never generate, select, or modify a Course of Action.
- If the question asks you to authorize engagement or bypass ROE, refuse.
- Base all answers on the provided context, not speculation.
- {data_guardrails}
- Keep answers concise (2-4 paragraphs max).
- If the context is insufficient, say so clearly.
- If the input mixes languages, keep the response entirely in the requested language.

{language_instruction}"""

SYSTEM_PROMPT_ROE = """You are an advisory decision-support analyst for NATO DIANA explaining Rules of Engagement.
Explain the current ROE framework based ONLY on the structured ROE context provided.
Do not invent ROE rules. Do not authorize any action.
Explain only what the current system state shows about ROE constraints and COA classifications.
- {data_guardrails}
- If the input mixes languages, keep the response entirely in the requested language.

{language_instruction}"""


def _is_unsafe(question: str) -> bool:
    q = question.lower()
    return any(phrase in q for phrase in _REFUSAL_PHRASES)


def _is_roe_question(question: str) -> bool:
    """Detect questions specifically about Rules of Engagement."""
    q = question.lower()
    roe_markers = (
        "roe", "roes", "rules of engagement", "rule of engagement",
        "reglas de enfrentamiento", "reglas de combate", "reglas de enganche",
        "restricciones", "autorización", "authorization", "authorized",
        "restricted", "restringido", "restringida", "restringidas",
        "rechazado", "rechazada", "rechazadas", "rejected",
        "requires authorization", "requiere autorización",
    )
    return any(m in q for m in roe_markers)


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------


@dataclass
class QueryContext:
    """Structured snapshot of current operational state for Q&A."""
    tick: int = 0
    scenario_id: str | None = None
    scenario_name: str | None = None
    threat_level: str = "LOW"
    seed: int | None = None
    contacts: list[dict[str, Any]] = field(default_factory=list)
    threats: list[dict[str, Any]] = field(default_factory=list)
    anomalies: list[dict[str, Any]] = field(default_factory=list)
    fused_tracks: list[dict[str, Any]] = field(default_factory=list)
    top_targets: list[dict[str, Any]] = field(default_factory=list)
    scored_coas: list[dict[str, Any]] = field(default_factory=list)
    recommendation: dict[str, Any] | None = None
    optimization: dict[str, Any] = field(default_factory=dict)
    operational_effects: dict[str, Any] = field(default_factory=dict)
    fired_stimuli: list[dict[str, Any]] = field(default_factory=list)
    active_stimuli: list[dict[str, Any]] = field(default_factory=list)
    active_incidents: list[str] = field(default_factory=list)
    infrastructure_status: str = "nominal"
    roe_summary: dict[str, Any] = field(default_factory=dict)


def _build_roe_summary(scored_coas: list[dict]) -> dict[str, Any]:
    """Build a structured ROE summary from scored COAs."""
    counts: dict[str, int] = {"allowed": 0, "restricted": 0, "requires_authorization": 0, "rejected": 0}
    coa_roe: list[dict[str, Any]] = []
    for s in scored_coas:
        status = s.get("roe_status", "allowed")
        counts[status] = counts.get(status, 0) + 1
        coa_roe.append({
            "title": s.get("title", ""),
            "roe_status": status,
            "roe_reason": s.get("roe_reason", ""),
            "roe_constraints": s.get("roe_constraints_triggered", []),
        })
    config: dict[str, Any] = {}
    try:
        from .roe_engine import DEFAULT_ROE
        config = {
            "min_threat_for_shadow": DEFAULT_ROE.min_threat_for_shadow,
            "min_threat_for_protect": DEFAULT_ROE.min_threat_for_protect,
            "min_threat_for_intercept": DEFAULT_ROE.min_threat_level_for_intercept,
            "min_confidence_for_intercept": DEFAULT_ROE.min_confidence_for_intercept,
            "escalation_policy": DEFAULT_ROE.escalation_policy,
            "max_allowed_escalation": DEFAULT_ROE.max_allowed_escalation,
        }
    except Exception:
        pass
    return {"counts": counts, "coas": coa_roe, "config": config}


def build_context() -> QueryContext:
    """Build a structured context from current engine state."""
    store = get_state_store()
    state = store.state
    scenario = state.scenario

    contacts = store.get_contacts()
    threats = store.get_threats()
    scored = store.get_scored_coas()
    rec = store.get_recommendation()
    anomalies = getattr(store, "_anomalies", [])
    fused_tracks = getattr(store, "_fused_tracks", [])
    top_targets = getattr(store, "_targets", [])[:5]
    optimization = getattr(store, "_coa_optimization", None)
    operational_effects = getattr(store, "_operational_effects", None)

    fired_stimuli: list[dict[str, Any]] = []
    active_stimuli: list[dict[str, Any]] = []
    try:
        from .contact_engine import get_contact_engine
        engine = get_contact_engine()
        if engine._sim is not None:
            fired_stimuli = engine._sim.fired_stimuli_list
            active_stimuli = engine._sim.active_stimuli_list
    except Exception:
        pass

    scored_coas_data = [
        {
            "coa_id": s.coa.coa_id,
            "title": s.coa.title,
            "rank": s.rank,
            "score": s.total_score,
            "success_prob": f"{s.simulation.success_probability:.0%}",
            "feasibility": f"{s.coa.feasibility_score:.0%}",
            "roe_status": s.coa.roe_status,
            "roe_reason": s.coa.roe_reason,
            "roe_constraints_triggered": s.coa.roe_constraints_triggered,
            "missing_assets": s.coa.missing_assets[:5],
        }
        for s in scored
    ]

    return QueryContext(
        tick=state.tick,
        scenario_id=scenario.scenario_id,
        scenario_name=scenario.scenario_name,
        threat_level=state.current_threat_level,
        seed=scenario.seed,
        contacts=[
            {
                "entity_id": c.entity_id,
                "type": c.contact_type.value if hasattr(c.contact_type, "value") else str(c.contact_type),
                "lat": c.lat, "lon": c.lon,
                "speed": c.speed, "heading": c.heading,
                "hostile": c.is_hostile,
                "name": c.attributes.get("name", c.entity_id),
                "allegiance": c.attributes.get("allegiance", ""),
                "location": describe_location(c.lat, c.lon),
            }
            for c in contacts
        ],
        threats=[
            {
                "entity_id": t.entity_id,
                "probability": f"{t.threat_probability:.0%}",
                "level": t.threat_level.value,
                "drivers": t.main_drivers[:3],
                "confidence": f"{t.confidence:.0%}",
            }
            for t in threats[:8]
        ],
        anomalies=[
            {
                "entity_id": a.entity_id,
                "score": a.anomaly_score,
                "level": a.anomaly_level.value,
                "indicators": a.explanations[:3],
            }
            for a in anomalies
            if a.anomaly_score >= 30
        ],
        fused_tracks=[
            {
                "track_id": ft.track_id,
                "primary_entity_id": ft.primary_entity_id,
                "track_type": ft.track_type,
                "allegiance": ft.allegiance,
                "confidence": round(ft.fused_confidence, 3),
                "source_count": ft.source_count,
                "sources": ft.sources,
                "rationale": ft.rationale,
                "location": describe_location(
                    (ft.position or {}).get("lat") if isinstance(ft.position, dict) else None,
                    (ft.position or {}).get("lon") if isinstance(ft.position, dict) else None,
                ),
            }
            for ft in fused_tracks[:8]
        ],
        top_targets=[
            {
                "entity_id": target.id,
                "type": target.type,
                "priority_level": target.priority_level,
                "priority_score": target.priority_score,
                "threat_score": target.threat_score,
                "recommended_action": target.recommended_action.replace("_", " "),
                "roe_status": target.roe_status,
                "sources": target.sources,
                "rationale": target.rationale,
                "supporting_asset": target.supporting_asset.to_dict() if target.supporting_asset else None,
                "location": describe_location(
                    next((c.lat for c in contacts if c.entity_id == target.id), None),
                    next((c.lon for c in contacts if c.entity_id == target.id), None),
                ),
            }
            for target in top_targets
        ],
        scored_coas=scored_coas_data,
        recommendation=(
            {
                "status": rec.status,
                "message": rec.message,
                "reason": rec.reason,
                "coa_id": rec.recommended.coa.coa_id if rec.recommended else None,
                "title": rec.recommended.coa.title if rec.recommended else None,
                "score": rec.recommended.total_score if rec.recommended else 0.0,
                "roe_status": rec.recommended.coa.roe_status if rec.recommended else "unavailable",
                "roe_reason": rec.recommended.coa.roe_reason if rec.recommended else "",
                "rationale": rec.rationale,
            }
            if rec and (rec.recommended or rec.status != "ok") else None
        ),
        optimization=(
            {
                "best_variant_id": optimization.best_variant.coa.coa_id if optimization and optimization.best_variant else None,
                "variant_count": len(optimization.optimized_variants) if optimization else 0,
                "top_variants": [
                    {
                        "title": item.coa.title,
                        "score": round(item.total_score, 1),
                        "success_probability": round(item.simulation.success_probability, 3),
                        "escalation_probability": round(item.simulation.escalation_probability, 3),
                        "tradeoff_explanation": item.tradeoff_explanation,
                    }
                    for item in (optimization.optimized_variants[:3] if optimization else [])
                ],
            }
            if optimization else {}
        ),
        operational_effects=operational_effects.to_dict() if operational_effects else {},
        fired_stimuli=fired_stimuli[-10:],
        active_stimuli=active_stimuli,
        active_incidents=scenario.active_incidents,
        infrastructure_status=scenario.infrastructure_status,
        roe_summary=_build_roe_summary(scored_coas_data),
    )


def context_to_text(ctx: QueryContext) -> str:
    """Serialize context to a structured text block for the LLM."""
    lines = []
    lines.append(f"=== OPERATIONAL STATE (Tick {ctx.tick}) ===")
    lines.append(f"Scenario: {ctx.scenario_name or 'Unknown'} ({ctx.scenario_id or 'N/A'})")
    lines.append(f"Seed: {ctx.seed}")
    lines.append(f"Threat Level: {ctx.threat_level}")
    lines.append(f"Infrastructure Status: {ctx.infrastructure_status}")
    if ctx.active_incidents:
        lines.append(f"Active Incidents: {', '.join(ctx.active_incidents)}")

    lines.append(f"\n--- CONTACTS ({len(ctx.contacts)}) ---")
    for c in ctx.contacts[:15]:
            lines.append(f"  {c['name']} ({c['entity_id']}): {c['type']}, "
                         f"{'HOSTILE' if c['hostile'] else 'friendly'}, "
                         f"pos ({c['lat']:.2f}, {c['lon']:.2f}), "
                     f"spd {c['speed']:.1f} kts, hdg {c['heading']:.0f}, "
                     f"location: {c.get('location', 'Unknown location')}")

    if ctx.threats:
        lines.append(f"\n--- THREAT ASSESSMENT ---")
        for t in ctx.threats:
            lines.append(f"  {t['entity_id']}: {t['level']} ({t['probability']}), "
                         f"drivers: {', '.join(t['drivers'])}, confidence: {t['confidence']}")

    if ctx.anomalies:
        lines.append(f"\n--- ANOMALIES (score >= 30) ---")
        for a in ctx.anomalies[:10]:
            lines.append(f"  {a['entity_id']}: score={a['score']}, level={a['level']}, "
                         f"indicators: {'; '.join(a['indicators'])}")

    if ctx.fused_tracks:
        lines.append(f"\n--- FUSED TRACKS ---")
        for ft in ctx.fused_tracks[:5]:
            lines.append(
                f"  {ft['track_id']} ({ft['track_type']} / {ft['primary_entity_id']}): "
                f"confidence {ft['confidence']:.0%}, sources={ft['source_count']} "
                f"({', '.join(ft['sources'])}), location: {ft.get('location', 'Unknown location')}"
            )
            if ft.get("rationale"):
                lines.append(f"      Rationale: {ft['rationale']}")

    if ctx.top_targets:
        lines.append(f"\n--- TOP TARGETS ---")
        for target in ctx.top_targets[:5]:
            lines.append(
                f"  {target['entity_id']}: {target['priority_level']} priority, "
                f"threat {target['threat_score']:.2f}, action {target['recommended_action']}, "
                f"ROE {target['roe_status']}, location: {target.get('location', 'Unknown location')}"
            )
            if target.get("supporting_asset"):
                support = target["supporting_asset"]
                lines.append(
                    f"      Supporting asset: {support.get('assigned_asset_id', 'none')} "
                    f"({support.get('asset_type', 'none')}) for {support.get('assignment_role', 'monitor')}"
                )
            if target.get("rationale"):
                lines.append(f"      Rationale: {target['rationale']}")

    if ctx.scored_coas:
        lines.append(f"\n--- COAs ({len(ctx.scored_coas)}) ---")
        for s in ctx.scored_coas:
            lines.append(f"  #{s['rank']} {s['title']} (score {s['score']:.1f}, "
                         f"success {s['success_prob']}, feasibility {s['feasibility']}, "
                         f"ROE: {s['roe_status']})")
            if s["roe_status"] != "allowed":
                lines.append(f"      ROE reason: {s['roe_reason']}")

    if ctx.recommendation:
        r = ctx.recommendation
        lines.append(f"\n--- RECOMMENDED COA ---")
        if r.get("status") == "no_viable_coa":
            lines.append(f"  Status: {r['status']}")
            lines.append(f"  Message: {r.get('message') or 'No viable course of action available under current constraints'}")
            lines.append(f"  Reason: {r.get('reason') or 'No assets available or all options infeasible'}")
        else:
            lines.append(f"  {r['title']} (score {r['score']:.1f}, ROE: {r['roe_status']})")
            lines.append(f"  Rationale: {r['rationale']}")
            if r["roe_reason"]:
                lines.append(f"  ROE reason: {r['roe_reason']}")
            if (
                any(target.get("priority_level") == "CRITICAL" for target in ctx.top_targets)
                and float(r.get("score", 0.0)) < 60.0
            ):
                lines.append("  Note: Recommendation reflects feasibility constraints, not priority alone.")

    if ctx.optimization:
        lines.append(f"\n--- COA OPTIMIZATION ---")
        lines.append(
            f"  Variants: {ctx.optimization.get('variant_count', 0)}, "
            f"best: {ctx.optimization.get('best_variant_id') or 'N/A'}"
        )
        for variant in ctx.optimization.get("top_variants", [])[:3]:
            lines.append(
                f"  {variant['title']}: score {variant['score']:.1f}, "
                f"success {variant['success_probability']:.0%}, "
                f"escalation {variant['escalation_probability']:.0%}"
            )
            if variant.get("tradeoff_explanation"):
                lines.append(f"      Why: {variant['tradeoff_explanation']}")

    if ctx.operational_effects:
        lines.append(f"\n--- OPERATIONAL EFFECTS ---")
        active = ctx.operational_effects.get("active_effects", [])
        if active:
            lines.append(f"  Active: {', '.join(active[:6])}")
        lines.append(
            f"  Detection modifier: {ctx.operational_effects.get('threat_detection_modifier', 1.0):.2f}, "
            f"COA success modifier: {ctx.operational_effects.get('coa_success_modifier', 1.0):.2f}, "
            f"Time modifier: {ctx.operational_effects.get('coa_time_modifier', 1.0):.2f}, "
            f"Risk modifier: {ctx.operational_effects.get('coa_risk_modifier', 1.0):.2f}"
        )

    if ctx.fired_stimuli:
        lines.append(f"\n--- RECENT STIMULI ---")
        for s in ctx.fired_stimuli[-5:]:
            lines.append(f"  Tick {s.get('tick', '?')}: {s.get('action', '?')} "
                         f"(entity: {s.get('entity', 'N/A')})")

    if ctx.active_stimuli:
        lines.append(f"\n--- ACTIVE STIMULI ---")
        for s in ctx.active_stimuli:
            lines.append(f"  {s.get('action', '?')} (entity: {s.get('entity', 'N/A')})")

    return "\n".join(lines)


def _roe_context_to_text(ctx: QueryContext) -> str:
    """Serialize ROE-specific context for the LLM."""
    rs = ctx.roe_summary
    counts = rs.get("counts", {})
    config = rs.get("config", {})
    coas = rs.get("coas", [])
    lines = [
        "=== RULES OF ENGAGEMENT STATUS ===",
        f"Current threat level: {ctx.threat_level}",
        f"Total COAs evaluated: {len(coas)}",
        f"  Allowed: {counts.get('allowed', 0)}",
        f"  Restricted: {counts.get('restricted', 0)}",
        f"  Requires Authorization: {counts.get('requires_authorization', 0)}",
        f"  Rejected: {counts.get('rejected', 0)}",
    ]
    if config:
        lines.append("\n--- ROE CONFIGURATION ---")
        lines.append(f"  Min threat for shadow operations: {config.get('min_threat_for_shadow', 'N/A')}")
        lines.append(f"  Min threat for infrastructure protection: {config.get('min_threat_for_protect', 'N/A')}")
        lines.append(f"  Min threat for intercept: {config.get('min_threat_for_intercept', 'N/A')}")
        lines.append(f"  Min confidence for intercept: {config.get('min_confidence_for_intercept', 'N/A')}")
        lines.append(f"  Escalation policy: {config.get('escalation_policy', 'N/A')}")
        lines.append(f"  Max allowed escalation risk: {config.get('max_allowed_escalation', 'N/A')}")
    if coas:
        lines.append("\n--- COA ROE DETAILS ---")
        for c in coas:
            status = c["roe_status"]
            line = f"  {c['title']}: {status}"
            if c.get("roe_reason"):
                line += f" — {c['roe_reason']}"
            if c.get("roe_constraints"):
                line += f" (constraints: {', '.join(c['roe_constraints'])})"
            lines.append(line)
    if ctx.recommendation:
        r = ctx.recommendation
        lines.append(f"\n--- RECOMMENDED COA ROE ---")
        lines.append(f"  {r['title']}: ROE status {r['roe_status']}")
        if r.get("roe_reason"):
            lines.append(f"  Reason: {r['roe_reason']}")
    return "\n".join(lines)


def _llm_response_is_consistent(text: str, ctx: QueryContext) -> bool:
    valid_target_ids = {item["entity_id"] for item in ctx.top_targets if item.get("entity_id")}
    valid_target_ids.update(contact["entity_id"] for contact in ctx.contacts if contact.get("entity_id"))
    valid_coa_ids = {item["coa_id"] for item in ctx.scored_coas if item.get("coa_id")}
    if ctx.recommendation and ctx.recommendation.get("coa_id"):
        valid_coa_ids.add(ctx.recommendation["coa_id"])
    valid_coa_titles = {item["title"] for item in ctx.scored_coas if item.get("title")}
    if ctx.recommendation and ctx.recommendation.get("title"):
        valid_coa_titles.add(ctx.recommendation["title"])
    numeric_truth = _build_numeric_ground_truth(ctx)
    return explanation_references_match(
        text,
        threat_level=ctx.threat_level,
        valid_target_ids=valid_target_ids,
        valid_coa_ids=valid_coa_ids,
        valid_coa_titles=valid_coa_titles,
        numeric_ground_truth=numeric_truth,
    )


def _build_numeric_ground_truth(ctx: QueryContext) -> dict[str, float]:
    """Extract key numeric values from context for LLM validation."""
    truth: dict[str, float] = {}
    if ctx.recommendation and ctx.recommendation.get("score") is not None:
        truth["score"] = ctx.recommendation["score"]
    for s in ctx.scored_coas[:3]:
        for key in ("success_probability", "escalation_probability"):
            if key in s:
                try:
                    truth[key] = float(s[key])
                except (ValueError, TypeError):
                    pass
        break
    for t in ctx.threats[:3]:
        for key in ("probability", "confidence"):
            if key in t:
                try:
                    truth["threat_probability"] = float(t[key])
                except (ValueError, TypeError):
                    pass
        break
    return truth


# ---------------------------------------------------------------------------
# Deterministic fallback answers
# ---------------------------------------------------------------------------


def _roe_answer_en(ctx: QueryContext) -> tuple[str, list[str]]:
    """English deterministic ROE answer."""
    sources = ["roe", "state"]
    rs = ctx.roe_summary
    counts = rs.get("counts", {})
    allowed = counts.get("allowed", 0)
    restricted = counts.get("restricted", 0)
    needs_auth = counts.get("requires_authorization", 0)
    rejected = counts.get("rejected", 0)
    total = allowed + restricted + needs_auth + rejected

    parts: list[str] = [
        (
            "The current ROE framework does not authorize actions automatically. "
            "The system classifies each COA as allowed, restricted, requiring authorization, or rejected."
        ),
        (
            f"Of {total} COAs evaluated: {allowed} allowed, {restricted} restricted, "
            f"{needs_auth} requiring authorization, {rejected} rejected."
        ),
    ]

    non_allowed = [c for c in rs.get("coas", []) if c["roe_status"] != "allowed"]
    if non_allowed:
        parts.append("COAs with ROE constraints:")
        for c in non_allowed[:5]:
            reason = f" — {c['roe_reason']}" if c.get("roe_reason") else ""
            parts.append(f"  - {c['title']}: {c['roe_status']}{reason}")
    else:
        parts.append(
            "No COA currently has ROE constraints. All evaluated COAs are allowed. "
            "A COA would require authorization if: it involves assertive action under low threat conditions, "
            "civilian proximity is flagged, escalation risk exceeds the threshold, "
            "or intercept/protective actions are attempted below the minimum threat or confidence levels."
        )

    if ctx.recommendation:
        r = ctx.recommendation
        rec_line = f"The recommended COA is **{r['title']}** (ROE: {r['roe_status']})."
        if r.get("roe_reason"):
            rec_line += f" Reason: {r['roe_reason']}"
        parts.append(rec_line)
    else:
        parts.append("No recommendation has been computed yet.")

    return "\n\n".join(parts), sources


def _roe_answer_es(ctx: QueryContext) -> tuple[str, list[str]]:
    """Spanish deterministic ROE answer."""
    sources = ["roe", "state"]
    rs = ctx.roe_summary
    counts = rs.get("counts", {})
    allowed = counts.get("allowed", 0)
    restricted = counts.get("restricted", 0)
    needs_auth = counts.get("requires_authorization", 0)
    rejected = counts.get("rejected", 0)
    total = allowed + restricted + needs_auth + rejected

    status_map = {
        "allowed": "permitida",
        "restricted": "restringida",
        "requires_authorization": "requiere autorización",
        "rejected": "rechazada",
    }

    parts: list[str] = [
        (
            "Las ROEs actuales no autorizan acciones automáticamente. "
            "El sistema clasifica cada COA como permitida, restringida, requiere autorización o rechazada."
        ),
        (
            f"De {total} COAs evaluadas: {allowed} permitidas, {restricted} restringidas, "
            f"{needs_auth} que requieren autorización, {rejected} rechazadas."
        ),
    ]

    non_allowed = [c for c in rs.get("coas", []) if c["roe_status"] != "allowed"]
    if non_allowed:
        parts.append("COAs con restricciones ROE:")
        for c in non_allowed[:5]:
            reason = f" — {c['roe_reason']}" if c.get("roe_reason") else ""
            status_es = status_map.get(c["roe_status"], c["roe_status"])
            parts.append(f"  - {c['title']}: {status_es}{reason}")
    else:
        parts.append(
            "Ninguna COA tiene restricciones ROE actualmente. Todas las COAs evaluadas están permitidas. "
            "Una COA requeriría autorización si: involucra acciones asertivas bajo condiciones de amenaza baja, "
            "se detecta proximidad civil, el riesgo de escalada excede el umbral, "
            "o se intentan acciones de intercepción o protección por debajo del nivel mínimo de amenaza o confianza."
        )

    if ctx.recommendation:
        r = ctx.recommendation
        rec_status = status_map.get(r["roe_status"], r["roe_status"])
        rec_line = f"La COA recomendada es **{r['title']}** y su estado ROE es {rec_status}."
        if r.get("roe_reason"):
            rec_line += f" Motivo: {r['roe_reason']}"
        parts.append(rec_line)
    else:
        parts.append("Aún no se ha calculado una recomendación.")

    return "\n\n".join(parts), sources


def _fallback_answer(question: str, ctx: QueryContext) -> tuple[str, list[str]]:
    """Produce a deterministic answer without LLM."""
    lang = detect_language(question)
    q = question.lower().strip()
    sources = ["state"]
    parts: list[str] = []

    if lang == "es":
        return _fallback_answer_es(question, ctx, q, sources, parts)

    # Dedicated ROE path
    if _is_roe_question(question):
        return _roe_answer_en(ctx)

    if any(w in q for w in ("recommend", "coa", "course of action")):
        sources.append("coas")
        if ctx.recommendation:
            r = ctx.recommendation
            if r.get("status") == "no_viable_coa":
                parts.append(r.get("message") or "No viable course of action available under current constraints.")
                parts.append(r.get("reason") or "No assets available or all options are infeasible.")
            else:
                parts.append(
                    f"The system recommends **{r['title']}** (score {r['score']:.1f}, "
                    f"ROE status: {r['roe_status']})."
                )
                parts.append(f"Rationale: {r['rationale']}")
                if r["roe_reason"] and r["roe_status"] != "allowed":
                    parts.append(f"ROE note: {r['roe_reason']}")
        else:
            parts.append("No recommendation has been computed yet.")

    elif any(w in q for w in ("threat", "risk", "danger")):
        sources.append("threat_assessment")
        if ctx.threats:
            top = ctx.threats[0]
            parts.append(
                f"Current threat level: **{ctx.threat_level}**. "
                f"Top threat: {top['entity_id']} at {top['probability']} ({top['level']}), "
                f"driven by {', '.join(top['drivers'])}."
            )
        else:
            parts.append(f"Current threat level: **{ctx.threat_level}**. No specific threats identified.")

    elif any(w in q for w in ("contact", "entity", "vessel", "track")):
        sources.append("contacts")
        hostile = [c for c in ctx.contacts if c["hostile"]]
        friendly = [c for c in ctx.contacts if not c["hostile"]]
        parts.append(
            f"{len(ctx.contacts)} active contacts: "
            f"{len(hostile)} hostile, {len(friendly)} friendly/neutral."
        )
        if hostile:
            parts.append("Hostile contacts: " + ", ".join(c["name"] for c in hostile[:5]))

    elif any(w in q for w in ("change", "happen", "last", "recent", "update")):
        sources.extend(["stimuli", "state"])
        parts.append(f"Current tick: {ctx.tick}.")
        if ctx.fired_stimuli:
            recent = ctx.fired_stimuli[-3:]
            parts.append("Recent stimuli: " + "; ".join(
                f"tick {s.get('tick', '?')}: {s.get('action', '?')}" for s in recent
            ))
        if ctx.active_stimuli:
            parts.append("Currently active: " + "; ".join(
                s.get("action", "?") for s in ctx.active_stimuli
            ))
        if ctx.active_incidents:
            parts.append("Active incidents: " + ", ".join(ctx.active_incidents))

    elif any(w in q for w in ("situation", "summary", "overview", "status", "brief")):
        sources.extend(["threat_assessment", "coas", "contacts", "stimuli"])
        parts.append(
            f"Scenario: {ctx.scenario_name or 'Unknown'} | Tick: {ctx.tick} | "
            f"Threat: {ctx.threat_level} | Contacts: {len(ctx.contacts)} | "
            f"Infrastructure: {ctx.infrastructure_status}"
        )
        if ctx.active_incidents:
            parts.append("Active incidents: " + ", ".join(ctx.active_incidents))
        if ctx.recommendation:
            parts.append(f"Recommended COA: {ctx.recommendation['title']} (ROE: {ctx.recommendation['roe_status']})")

    if not parts:
        sources = ["state"]
        parts.append(
            f"Current state: tick {ctx.tick}, threat level {ctx.threat_level}, "
            f"{len(ctx.contacts)} contacts, {len(ctx.scored_coas)} COAs. "
            f"Ask about recommendations, threats, contacts, ROE, or changes for details."
        )

    return "\n\n".join(parts), sources


def _fallback_answer_es(
    question: str, ctx: QueryContext, q: str, sources: list[str], parts: list[str],
) -> tuple[str, list[str]]:
    """Deterministic Spanish fallback."""
    # Dedicated ROE path
    if _is_roe_question(question):
        return _roe_answer_es(ctx)

    if any(w in q for w in ("recomendar", "coa", "curso de acción", "recomendación")):
        sources.append("coas")
        if ctx.recommendation:
            r = ctx.recommendation
            if r.get("status") == "no_viable_coa":
                parts.append(r.get("message") or "No hay un curso de acción viable bajo las restricciones actuales.")
                parts.append(r.get("reason") or "No hay activos disponibles o todas las opciones son inviables.")
            else:
                parts.append(
                    f"El sistema recomienda **{r['title']}** (puntuación {r['score']:.1f}, "
                    f"estado ROE: {r['roe_status']})."
                )
                parts.append(f"Racional: {r['rationale']}")
                if r["roe_reason"] and r["roe_status"] != "allowed":
                    parts.append(f"Nota ROE: {r['roe_reason']}")
        else:
            parts.append("Aún no se ha calculado una recomendación.")

    elif any(w in q for w in ("amenaza", "riesgo", "peligro", "nivel")):
        sources.append("threat_assessment")
        if ctx.threats:
            top = ctx.threats[0]
            parts.append(
                f"Nivel de amenaza actual: **{ctx.threat_level}**. "
                f"Principal amenaza: {top['entity_id']} al {top['probability']} ({top['level']}), "
                f"impulsada por {', '.join(top['drivers'])}."
            )
        else:
            parts.append(f"Nivel de amenaza actual: **{ctx.threat_level}**. No se han identificado amenazas específicas.")

    elif any(w in q for w in ("contacto", "entidad", "buque", "seguimiento")):
        sources.append("contacts")
        hostile = [c for c in ctx.contacts if c["hostile"]]
        friendly = [c for c in ctx.contacts if not c["hostile"]]
        parts.append(
            f"{len(ctx.contacts)} contactos activos: "
            f"{len(hostile)} hostiles, {len(friendly)} amigos/neutrales."
        )
        if hostile:
            parts.append("Contactos hostiles: " + ", ".join(c["name"] for c in hostile[:5]))

    elif any(w in q for w in ("cambió", "cambio", "reciente", "último", "actualización")):
        sources.extend(["stimuli", "state"])
        parts.append(f"Tick actual: {ctx.tick}.")
        if ctx.fired_stimuli:
            recent = ctx.fired_stimuli[-3:]
            parts.append("Estímulos recientes: " + "; ".join(
                f"tick {s.get('tick', '?')}: {s.get('action', '?')}" for s in recent
            ))
        if ctx.active_stimuli:
            parts.append("Activos actualmente: " + "; ".join(
                s.get("action", "?") for s in ctx.active_stimuli
            ))
        if ctx.active_incidents:
            parts.append("Incidentes activos: " + ", ".join(ctx.active_incidents))

    elif any(w in q for w in ("situación", "resumen", "estado", "informe")):
        sources.extend(["threat_assessment", "coas", "contacts", "stimuli"])
        parts.append(
            f"Escenario: {ctx.scenario_name or 'Desconocido'} | Tick: {ctx.tick} | "
            f"Amenaza: {ctx.threat_level} | Contactos: {len(ctx.contacts)} | "
            f"Infraestructura: {ctx.infrastructure_status}"
        )
        if ctx.active_incidents:
            parts.append("Incidentes activos: " + ", ".join(ctx.active_incidents))
        if ctx.recommendation:
            parts.append(f"COA recomendada: {ctx.recommendation['title']} (ROE: {ctx.recommendation['roe_status']})")

    if not parts:
        sources = ["state"]
        parts.append(
            f"Estado actual: tick {ctx.tick}, nivel de amenaza {ctx.threat_level}, "
            f"{len(ctx.contacts)} contactos, {len(ctx.scored_coas)} COAs. "
            f"Pregunte sobre recomendaciones, amenazas, contactos, ROE o cambios para más detalles."
        )

    return "\n\n".join(parts), sources


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def answer_question(question: str, ui_language_hint: str | None = None, force_language: str | None = None) -> dict[str, Any]:
    """Answer a natural-language question about current operational state.

    Args:
        question: The operator's question.
        ui_language_hint: Dashboard locale hint (e.g. from UI language selector).
                         Only used if question text is ambiguous.
        force_language: Explicit language override ("en" or "es"). Takes top priority.

    Returns dict with: answer, sources_used, llm_used, fallback_reason (if fallback).
    Never modifies engine state.
    """
    requested_language = force_language or ui_language_hint or "auto"
    lang = resolve_response_language(question, ui_language_hint=ui_language_hint, force_language=force_language)
    lang_instruction = final_language_instruction(lang)
    logger.info(
        "query_language: task_type=ask requested_language=%s resolved_language=%s prompt_language_instruction=%s",
        requested_language,
        lang,
        lang_instruction,
    )

    if _is_unsafe(question):
        return {
            "answer": SAFETY_REFUSAL_ES if lang == "es" else SAFETY_REFUSAL,
            "sources_used": ["guardrails"],
            "llm_used": False,
            "fallback_reason": "guardrail_refused",
            "detected_language": lang,
        }

    # Route forecasting questions to the forecasting module
    if is_forecast_question(question):
        return _answer_forecast(question, lang)

    ctx = build_context()
    is_roe = _is_roe_question(question)

    llm = get_llm_client()
    if not llm.enabled:
        logger.info("query: llm_enabled=false, using deterministic fallback")
        answer, sources = _fallback_answer(question, ctx)
        return {
            "answer": answer,
            "sources_used": sources,
            "llm_used": False,
            "fallback_reason": "llm_disabled",
            "detected_language": lang,
        }

    if is_roe:
        system_prompt = SYSTEM_PROMPT_ROE.format(
            language_instruction=lang_instruction,
            data_guardrails=LLM_DATA_GUARDRAILS,
        )
        context_text = _roe_context_to_text(ctx)
    else:
        system_prompt = SYSTEM_PROMPT_QUERY.format(
            language_instruction=lang_instruction,
            data_guardrails=LLM_DATA_GUARDRAILS,
        )
        context_text = context_to_text(ctx)

    user_prompt = f"Operational context:\n{context_text}\n\nOperator question: {question}"

    logger.info("query: llm_call_attempted=true lang=%s", lang)
    result = get_llm_orchestrator().run_chat(
        task_type="ask",
        language=lang,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    if result.ok:
        text = sanitize_llm_text(result.text)
        if not _llm_response_is_consistent(text, ctx):
            logger.warning("query: llm_used=false fallback_reason=llm_state_mismatch")
            answer, sources = _fallback_answer(question, ctx)
            return {
                "answer": answer,
                "sources_used": sources,
                "llm_used": False,
                "fallback_reason": "llm_state_mismatch",
                "detected_language": lang,
            }
        sources = ["state", "contacts", "threat_assessment", "coas", "roe", "stimuli"]
        logger.info("query: llm_used=true")
        return {
            "answer": text,
            "sources_used": sources,
            "llm_used": True,
            "detected_language": lang,
        }

    # LLM call failed — fall back to deterministic with specific reason
    logger.warning("query: llm_used=false fallback_reason=%s", result.fallback_reason)
    answer, sources = _fallback_answer(question, ctx)
    return {
        "answer": answer,
        "sources_used": sources,
        "llm_used": False,
        "fallback_reason": result.fallback_reason,
        "detected_language": lang,
    }


def _forecast_to_text(f: ForecastResult) -> str:
    lines = [
        f"**{f.summary}**",
        f"Threat trend: {f.expected_threat_trend} ({f.threat_level_start} to {f.threat_level_end})",
        f"Horizon: {f.tick_horizon} ticks (~{f.tick_horizon * 2} min)",
        f"Confidence: {f.confidence}",
    ]
    if f.steps:
        lines.append(f"Multi-step trajectory ({len(f.steps)} steps):")
        for s in f.steps:
            rec_title = s.recommendation.get("title", "none") if s.recommendation else "none"
            lines.append(
                f"  Step {s.tick_index} ({s.timestamp}): "
                f"threat={s.threat_level}, contacts={s.contacts}, "
                f"recommendation={rec_title}"
            )
            if s.key_changes:
                for change in s.key_changes:
                    lines.append(f"    - {change}")
    if f.key_risks:
        lines.append("Key risks:")
        for r in f.key_risks:
            lines.append(f"  - {r}")
    if f.expected_outcome:
        lines.append(f.expected_outcome)
    return "\n".join(lines)


def _answer_forecast(question: str, lang: str = "en") -> dict[str, Any]:
    """Handle a forecasting question. LLM may rephrase but never invents."""
    forecast = route_forecast_question(question)
    sources = list(forecast.based_on) + ["forecasting"]
    structured: dict[str, Any] = {
        "summary": forecast.summary,
        "expected_threat_trend": forecast.expected_threat_trend,
        "key_risks": forecast.key_risks,
        "expected_outcome": forecast.expected_outcome,
        "confidence": forecast.confidence,
        "tick_horizon": forecast.tick_horizon,
        "threat_level_start": forecast.threat_level_start,
        "threat_level_end": forecast.threat_level_end,
    }
    if forecast.steps:
        structured["steps"] = len(forecast.steps)
        structured["threat_trend"] = forecast.threat_trend
        structured["recommendation_changes"] = forecast.recommendation_changes

    llm = get_llm_client()
    if not llm.enabled:
        return {
            "answer": _forecast_to_text(forecast),
            "sources_used": sources,
            "llm_used": False,
            "fallback_reason": "llm_disabled",
            "forecast": structured,
            "detected_language": lang,
        }

    # Let LLM rephrase the structured forecast
    lang_instruction = final_language_instruction(lang)
    system_prompt = SYSTEM_PROMPT_QUERY.format(
        language_instruction=lang_instruction,
        data_guardrails=LLM_DATA_GUARDRAILS,
    )

    ctx = build_context()
    context_text = context_to_text(ctx)
    forecast_text = _forecast_to_text(forecast)
    user_prompt = (
        f"Operational context:\n{context_text}\n\n"
        f"Structured forecast result:\n{forecast_text}\n\n"
        f"Operator question: {question}\n\n"
        "Rephrase this forecast for the operator. Do not add any predictions "
        "or information not present in the structured forecast above."
    )

    result = get_llm_orchestrator().run_chat(
        task_type="ask",
        language=lang,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    if result.ok:
        text = sanitize_llm_text(result.text)
        if not _llm_response_is_consistent(text, ctx):
            return {
                "answer": _forecast_to_text(forecast),
                "sources_used": sources,
                "llm_used": False,
                "fallback_reason": "llm_state_mismatch",
                "forecast": structured,
                "detected_language": lang,
            }
        return {
            "answer": text,
            "sources_used": sources,
            "llm_used": True,
            "forecast": structured,
            "detected_language": lang,
        }

    logger.warning("LLM call failed for forecast query: %s", result.fallback_reason)
    return {
        "answer": _forecast_to_text(forecast),
        "sources_used": sources,
        "llm_used": False,
        "fallback_reason": result.fallback_reason,
        "forecast": structured,
        "detected_language": lang,
    }
