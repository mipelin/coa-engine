from __future__ import annotations

import logging

from ..core.schemas import Recommendation, ScoredCOA

logger = logging.getLogger("coa_engine.engine.recommendation")


def recommend(scored: list[ScoredCOA]) -> Recommendation:
    """Select the top COA and explain alternatives and edge cases."""
    if not scored:
        return Recommendation(
            recommended=None,
            alternatives=[],
            rationale="No courses of action available for assessment.",
            edge_cases="",
        )

    best = scored[0]
    alternatives = scored[1:]

    rationale_parts = [
        f"{best.coa.title} ranks highest (score {best.total_score:.1f}/100).",
        f"Success probability: {best.simulation.success_probability:.0%}.",
    ]
    if best.coa.feasibility_score < 1.0:
        rationale_parts.append(
            f"Feasible with current asset availability at {best.coa.feasibility_score:.0%}."
        )
    if best.simulation.risk_to_second_cable < 0.2:
        rationale_parts.append("Low risk to the second subsea cable.")
    if best.simulation.escalation_probability < 0.1:
        rationale_parts.append("Low escalation risk.")
    rationale_parts.append(best.tradeoff_explanation + ".")
    rationale = " ".join(rationale_parts)

    edge_parts: list[str] = []
    for alt in alternatives:
        edge_parts.append(
            f"{alt.coa.title} (score {alt.total_score:.1f}) may be preferred if "
            f"prioritizing {alt.tradeoff_explanation.lower()}."
        )
    if not edge_parts:
        edge_parts.append("No alternative COAs evaluated.")

    logger.info("Recommendation: %s (score %.1f)", best.coa.coa_id, best.total_score)

    return Recommendation(
        recommended=best,
        alternatives=alternatives,
        rationale=rationale,
        edge_cases=" ".join(edge_parts),
    )
