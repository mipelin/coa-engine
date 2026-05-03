"""Deterministic COA parameter optimizer.

Generates parameterized COA variants from base templates, simulates and
scores them, applies ROE, and ranks by robustness. No LLM, no RL, no
randomness — fully deterministic.

Integration point: called by analysis_service after base COA generation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..core.config import settings
from ..core.schemas import (
    CourseOfAction,
    ScoredCOA,
    SimulationResult,
    ThreatResult,
)
from .roe_engine import evaluate_roe
from .scoring import score_coas
from .simulation import run_simulations

logger = logging.getLogger("coa_engine.engine.coa_optimizer")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_COA_VARIANTS: int = 24

# ---------------------------------------------------------------------------
# Parameter model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class COAParameterSet:
    """Parameterization of a single COA variant."""
    base_template_id: str
    variant_id: str
    variant_label: str
    isr_intensity: str = "medium"       # low / medium / high
    shadow_distance_nm: float = 5.0     # nautical miles
    response_speed: str = "normal"       # conservative / normal / rapid
    escalation_posture: str = "medium"   # low / medium / high
    logistics_burden: str = "medium"     # low / medium / high
    protection_priority: str = "balanced"  # infrastructure / airspace / convoy / balanced
    asset_package: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Variant adjustment factors
# ---------------------------------------------------------------------------

# These multipliers adjust base template values to produce variant COAs.
# They do NOT change global scoring weights.

_ISR_INTENSITY_MAP: dict[str, dict[str, float]] = {
    "low":    {"success_delta": -0.05, "time_factor": 1.10, "logistics_delta": -0.10, "detection_delta":  0.08, "escalation_delta": -0.02},
    "medium": {"success_delta":  0.00, "time_factor": 1.00, "logistics_delta":  0.00, "detection_delta":  0.00, "escalation_delta":  0.00},
    "high":   {"success_delta":  0.05, "time_factor": 0.90, "logistics_delta":  0.10, "detection_delta": -0.05, "escalation_delta":  0.02},
}

_RESPONSE_SPEED_MAP: dict[str, dict[str, float]] = {
    "conservative": {"time_factor": 1.30, "success_delta": -0.03, "escalation_delta": -0.04},
    "normal":       {"time_factor": 1.00, "success_delta":  0.00, "escalation_delta":  0.00},
    "rapid":        {"time_factor": 0.70, "success_delta":  0.03, "escalation_delta":  0.04},
}

_ESCALATION_POSTURE_MAP: dict[str, dict[str, float]] = {
    "low":    {"escalation_delta": -0.06, "civilian_delta": -0.02, "success_delta": -0.03},
    "medium": {"escalation_delta":  0.00, "civilian_delta":  0.00, "success_delta":  0.00},
    "high":   {"escalation_delta":  0.06, "civilian_delta":  0.02, "success_delta":  0.03},
}

_LOGISTICS_BURDEN_MAP: dict[str, dict[str, float]] = {
    "low":    {"logistics_delta": -0.15, "success_delta": -0.02},
    "medium": {"logistics_delta":  0.00, "success_delta":  0.00},
    "high":   {"logistics_delta":  0.15, "success_delta":  0.02},
}

_PROTECTION_PRIORITY_MAP: dict[str, dict[str, Any]] = {
    "infrastructure": {"cable_risk_factor": 0.6, "civilian_delta": -0.02, "success_delta":  0.03},
    "airspace":       {"cable_risk_factor": 1.0, "civilian_delta":  0.02, "success_delta":  0.00},
    "convoy":         {"cable_risk_factor": 1.0, "civilian_delta": -0.01, "success_delta":  0.01},
    "balanced":       {"cable_risk_factor": 0.8, "civilian_delta":  0.00, "success_delta":  0.00},
}

_SHADOW_DISTANCE_MAP: dict[str, float] = {
    "close": 2.0,
    "standard": 5.0,
    "wide": 10.0,
}


# ---------------------------------------------------------------------------
# Variant presets — curated set per base template
# ---------------------------------------------------------------------------

_VARIANT_PRESETS: list[dict[str, Any]] = [
    # ISR-heavy
    {"label": "ISR-intensive", "isr_intensity": "high", "response_speed": "normal",
     "escalation_posture": "low", "logistics_burden": "high", "protection_priority": "balanced"},
    # Low-escalation monitoring
    {"label": "Low-escalation monitor", "isr_intensity": "medium", "response_speed": "conservative",
     "escalation_posture": "low", "logistics_burden": "low", "protection_priority": "balanced"},
    # Rapid shadow
    {"label": "Rapid shadow", "isr_intensity": "medium", "response_speed": "rapid",
     "escalation_posture": "medium", "logistics_burden": "medium", "protection_priority": "balanced",
     "shadow_distance": "close"},
    # Infrastructure protection
    {"label": "Infrastructure-first", "isr_intensity": "medium", "response_speed": "normal",
     "escalation_posture": "low", "logistics_burden": "medium", "protection_priority": "infrastructure"},
    # Support request
    {"label": "Support request", "isr_intensity": "low", "response_speed": "conservative",
     "escalation_posture": "low", "logistics_burden": "low", "protection_priority": "balanced"},
    # Assertive posture
    {"label": "Assertive posture", "isr_intensity": "high", "response_speed": "rapid",
     "escalation_posture": "high", "logistics_burden": "high", "protection_priority": "balanced"},
    # Airspace priority
    {"label": "Airspace priority", "isr_intensity": "high", "response_speed": "normal",
     "escalation_posture": "medium", "logistics_burden": "medium", "protection_priority": "airspace"},
    # Convoy focus
    {"label": "Convoy focus", "isr_intensity": "medium", "response_speed": "normal",
     "escalation_posture": "medium", "logistics_burden": "medium", "protection_priority": "convoy"},
]


# ---------------------------------------------------------------------------
# Variant generation
# ---------------------------------------------------------------------------


def generate_variants(
    base_coas: list[CourseOfAction],
    max_variants: int = MAX_COA_VARIANTS,
) -> list[tuple[CourseOfAction, COAParameterSet]]:
    """Generate parameterized variants from base COAs.

    Returns list of (variant_COA, parameter_set) tuples.
    Each base COA produces 3-8 variants depending on template applicability.
    Total capped at max_variants.
    """
    variants: list[tuple[CourseOfAction, COAParameterSet]] = []

    for base in base_coas:
        base_variants = _variants_for_coa(base)
        for coa, params in base_variants:
            if len(variants) >= max_variants:
                break
            variants.append((coa, params))
        if len(variants) >= max_variants:
            break

    logger.info(
        "Generated %d COA variants from %d base COAs (cap=%d)",
        len(variants), len(base_coas), max_variants,
    )
    return variants


def _variants_for_coa(
    base: CourseOfAction,
) -> list[tuple[CourseOfAction, COAParameterSet]]:
    """Generate applicable variants for a single base COA."""
    results: list[tuple[CourseOfAction, COAParameterSet]] = []

    for i, preset in enumerate(_VARIANT_PRESETS):
        # Skip variants that don't match template capabilities
        tpl = base.template_id
        label = preset["label"]

        # Shadow-distance only for shadow/combined templates
        shadow_dist = _SHADOW_DISTANCE_MAP.get(
            preset.get("shadow_distance", "standard"), 5.0,
        )
        if tpl not in ("COA-TPL-SHADOW", "COA-TPL-COMBINED"):
            if "shadow_distance" in preset:
                continue
            shadow_dist = 5.0

        # Infrastructure-protection only relevant for cable-protect/combined
        prot = preset["protection_priority"]
        if prot == "infrastructure" and tpl not in (
            "COA-TPL-CABLE-PROTECT", "COA-TPL-COMBINED", "COA-TPL-ISR",
        ):
            continue

        # Airspace priority only for airspace/combined
        if prot == "airspace" and tpl not in (
            "COA-TPL-AIRSPACE", "COA-TPL-COMBINED", "COA-TPL-ISR",
        ):
            continue

        # Convoy focus only for border/combined
        if prot == "convoy" and tpl not in (
            "COA-TPL-BORDER", "COA-TPL-COMBINED",
        ):
            continue

        # Compute adjusted COA parameters
        adj = _compute_adjustments(base, preset)

        params = COAParameterSet(
            base_template_id=tpl,
            variant_id=f"{tpl}-V{i+1:02d}",
            variant_label=label,
            isr_intensity=preset["isr_intensity"],
            shadow_distance_nm=shadow_dist,
            response_speed=preset["response_speed"],
            escalation_posture=preset["escalation_posture"],
            logistics_burden=preset["logistics_burden"],
            protection_priority=prot,
            asset_package=list(base.assigned_assets),
        )

        variant_coa = _build_variant_coa(base, params, adj)
        results.append((variant_coa, params))

    return results


def _compute_adjustments(
    base: CourseOfAction,
    preset: dict[str, Any],
) -> dict[str, float]:
    """Compute adjustment deltas for a variant based on its preset."""
    isr = _ISR_INTENSITY_MAP[preset["isr_intensity"]]
    speed = _RESPONSE_SPEED_MAP[preset["response_speed"]]
    esc = _ESCALATION_POSTURE_MAP[preset["escalation_posture"]]
    log = _LOGISTICS_BURDEN_MAP[preset["logistics_burden"]]
    prot = _PROTECTION_PRIORITY_MAP[preset["protection_priority"]]

    return {
        "success_delta": (
            isr["success_delta"] + speed["success_delta"]
            + esc["success_delta"] + log["success_delta"]
            + prot.get("success_delta", 0.0)
        ),
        "time_factor": isr["time_factor"] * speed["time_factor"],
        "escalation_delta": (
            isr["escalation_delta"] + speed["escalation_delta"]
            + esc["escalation_delta"]
        ),
        "logistics_delta": (
            isr["logistics_delta"] + log["logistics_delta"]
        ),
        "civilian_delta": (
            esc["civilian_delta"] + prot.get("civilian_delta", 0.0)
        ),
        "detection_delta": isr["detection_delta"],
        "cable_risk_factor": prot.get("cable_risk_factor", 1.0),
    }


def _build_variant_coa(
    base: CourseOfAction,
    params: COAParameterSet,
    adj: dict[str, float],
) -> CourseOfAction:
    """Build a concrete COA from a base template with variant adjustments."""
    escalation = max(0.0, min(1.0, base.escalation_risk + adj["escalation_delta"]))
    civilian = max(0.0, min(1.0, base.civilian_risk + adj["civilian_delta"]))
    logistics = max(0.0, min(1.0, base.logistics_burden + adj["logistics_delta"]))
    time = max(5, int(round(base.estimated_time_minutes * adj["time_factor"])))

    title = f"{base.title} [{params.variant_label}]"

    return base.model_copy(update={
        "coa_id": params.variant_id,
        "template_id": base.template_id,
        "title": title,
        "description": f"{base.description} (variant: {params.variant_label})",
        "escalation_risk": round(escalation, 3),
        "civilian_risk": round(civilian, 3),
        "logistics_burden": round(logistics, 3),
        "estimated_time_minutes": time,
        "source": "coa_optimizer",
    })


# ---------------------------------------------------------------------------
# Variant simulation with adjustment factors
# ---------------------------------------------------------------------------


def simulate_variants(
    variants: list[tuple[CourseOfAction, COAParameterSet]],
    events: list[Any],
    threats: list[ThreatResult],
    scenario_state: Any = None,
) -> list[tuple[CourseOfAction, COAParameterSet, SimulationResult]]:
    """Run simulations for all variants, applying parameter-based adjustments."""
    coas = [coa for coa, _ in variants]
    base_sims = run_simulations(coas, events, threats, scenario_state)
    sim_by_id = {s.coa_id: s for s in base_sims}

    results: list[tuple[CourseOfAction, COAParameterSet, SimulationResult]] = []
    for coa, params in variants:
        sim = sim_by_id.get(coa.coa_id)
        if sim is None:
            continue
        adj_sim = _adjust_simulation(coa, params, sim)
        results.append((coa, params, adj_sim))

    return results


def _adjust_simulation(
    coa: CourseOfAction,
    params: COAParameterSet,
    sim: SimulationResult,
) -> SimulationResult:
    """Apply variant-specific adjustments to simulation results."""
    isr = _ISR_INTENSITY_MAP[params.isr_intensity]
    speed = _RESPONSE_SPEED_MAP[params.response_speed]
    esc = _ESCALATION_POSTURE_MAP[params.escalation_posture]
    prot = _PROTECTION_PRIORITY_MAP[params.protection_priority]

    success = sim.success_probability + (
        isr["success_delta"] + speed["success_delta"]
        + esc["success_delta"] + prot.get("success_delta", 0.0)
    )
    success = max(0.05, min(0.95, success))

    escalation = sim.escalation_probability + (
        isr["escalation_delta"] + speed["escalation_delta"]
        + esc["escalation_delta"]
    )
    escalation = max(0.01, min(0.95, escalation))

    cable = sim.risk_to_second_cable * prot.get("cable_risk_factor", 1.0)
    cable = max(0.01, min(0.95, cable))

    missed = sim.missed_detection_probability + isr.get("detection_delta", 0.0)
    missed = max(0.01, min(0.95, missed))

    time = sim.expected_time_to_effect * speed["time_factor"]
    time = max(5.0, time)

    ci_width = sim.confidence_interval[1] - sim.confidence_interval[0]
    ci_mid = success
    ci_low = max(0.01, ci_mid - ci_width / 2)
    ci_high = min(0.99, ci_mid + ci_width / 2)

    return SimulationResult(
        coa_id=coa.coa_id,
        success_probability=round(success, 3),
        expected_time_to_effect=round(time, 1),
        risk_to_second_cable=round(cable, 3),
        escalation_probability=round(escalation, 3),
        missed_detection_probability=round(missed, 3),
        confidence_interval=(round(ci_low, 3), round(ci_high, 3)),
        simulation_runs=sim.simulation_runs,
    )


# ---------------------------------------------------------------------------
# Robustness ranking
# ---------------------------------------------------------------------------


# Weights for robustness score — separate from global scoring weights
_ROBUSTNESS_WEIGHTS = {
    "success": 0.25,
    "feasibility": 0.20,
    "escalation": 0.20,
    "logistics": 0.10,
    "civilian": 0.10,
    "cable": 0.15,
}


def compute_robustness(
    coa: CourseOfAction,
    sim: SimulationResult,
) -> float:
    """Compute a deterministic robustness score for a COA variant.

    Higher is better. Scale 0-100.
    """
    w = _ROBUSTNESS_WEIGHTS
    score = (
        w["success"] * sim.success_probability
        + w["feasibility"] * coa.feasibility_score
        + w["escalation"] * (1.0 - sim.escalation_probability)
        + w["logistics"] * (1.0 - coa.logistics_burden)
        + w["civilian"] * (1.0 - coa.civilian_risk)
        + w["cable"] * (1.0 - sim.risk_to_second_cable)
    )
    return round(score * 100.0, 1)


# ---------------------------------------------------------------------------
# Full optimization pipeline
# ---------------------------------------------------------------------------


@dataclass
class OptimizationResult:
    """Output of the COA optimization pipeline."""
    optimized_variants: list[ScoredCOA] = field(default_factory=list)
    variant_parameters: list[dict[str, Any]] = field(default_factory=list)
    best_variant: ScoredCOA | None = None
    robustness_ranking: list[dict[str, Any]] = field(default_factory=list)
    optimization_summary: dict[str, Any] = field(default_factory=dict)


def optimize_coas(
    base_coas: list[CourseOfAction],
    events: list[Any],
    threats: list[ThreatResult],
    scenario_state: Any = None,
    asset_inventory: dict[str, int] | None = None,
    asset_states: list[Any] | None = None,
) -> OptimizationResult:
    """Full optimization pipeline: generate variants, simulate, score, ROE, rank.

    Returns OptimizationResult with ranked variants and best selection.
    """
    if not base_coas:
        return OptimizationResult(
            optimization_summary={"status": "no_base_coas", "variant_count": 0},
        )

    # Step 1: Generate variants
    variant_tuples = generate_variants(base_coas)

    if not variant_tuples:
        return OptimizationResult(
            optimization_summary={"status": "no_variants_generated", "variant_count": 0},
        )

    # Step 2: Simulate variants
    sim_results = simulate_variants(variant_tuples, events, threats, scenario_state)

    # Step 3: Compute robustness for each
    robustness_data: list[dict[str, Any]] = []
    for coa, params, sim in sim_results:
        robust_score = compute_robustness(coa, sim)
        robustness_data.append({
            "coa": coa,
            "params": params,
            "sim": sim,
            "robustness": robust_score,
        })

    # Step 4: Score using existing scoring logic
    variant_coas = [coa for coa, _, _ in sim_results]
    variant_sims = [sim for _, _, sim in sim_results]
    scored = score_coas(variant_coas, variant_sims)

    # Attach robustness to tradeoff_explanation
    sim_by_coa_id = {sim.coa_id: sim for sim in variant_sims}
    for s in scored:
        rb = next(
            (r for r in robustness_data if r["coa"].coa_id == s.coa.coa_id),
            None,
        )
        robust_val = rb["robustness"] if rb else 0.0
        s.tradeoff_explanation += f"; robustness={robust_val:.1f}"

    # Step 5: Apply ROE
    top_threat_confidence = threats[0].confidence if threats else 0.8
    scored = evaluate_roe(scored, threats, confidence=top_threat_confidence)

    # Step 6: Rank by robustness
    robust_lookup = {
        r["coa"].coa_id: r["robustness"] for r in robustness_data
    }
    robustness_ranking = sorted(
        [
            {
                "variant_id": s.coa.coa_id,
                "title": s.coa.title,
                "total_score": s.total_score,
                "robustness": robust_lookup.get(s.coa.coa_id, 0.0),
                "roe_status": s.coa.roe_status,
                "success_probability": s.simulation.success_probability,
            }
            for s in scored
        ],
        key=lambda x: (x["robustness"], x["total_score"]),
        reverse=True,
    )

    # Step 7: Select best non-rejected variant
    recommendable = [s for s in scored if s.coa.roe_status != "rejected"]
    best = recommendable[0] if recommendable else None

    # Build parameter records
    param_records = []
    params_by_id = {coa.coa_id: p for coa, p, _ in sim_results}
    for s in scored:
        p = params_by_id.get(s.coa.coa_id)
        if p:
            param_records.append({
                "variant_id": p.variant_id,
                "base_template_id": p.base_template_id,
                "variant_label": p.variant_label,
                "isr_intensity": p.isr_intensity,
                "shadow_distance_nm": p.shadow_distance_nm,
                "response_speed": p.response_speed,
                "escalation_posture": p.escalation_posture,
                "logistics_burden": p.logistics_burden,
                "protection_priority": p.protection_priority,
            })

    summary = {
        "status": "ok",
        "variant_count": len(scored),
        "base_coa_count": len(base_coas),
        "best_variant_id": best.coa.coa_id if best else None,
        "best_robustness": robust_lookup.get(best.coa.coa_id, 0.0) if best else None,
        "rejected_count": sum(1 for s in scored if s.coa.roe_status == "rejected"),
        "allowed_count": sum(1 for s in scored if s.coa.roe_status == "allowed"),
    }

    logger.info(
        "COA optimization: %d variants from %d bases, best=%s, robustness=%.1f",
        len(scored), len(base_coas),
        best.coa.coa_id if best else "N/A",
        robust_lookup.get(best.coa.coa_id, 0.0) if best else 0.0,
    )

    return OptimizationResult(
        optimized_variants=scored,
        variant_parameters=param_records,
        best_variant=best,
        robustness_ranking=robustness_ranking,
        optimization_summary=summary,
    )
