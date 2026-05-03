from __future__ import annotations

import logging

from ..core.schemas import AssetState, Recommendation, ScoredCOA
from .portfolio import build_portfolios

logger = logging.getLogger("coa_engine.engine.recommendation")


def recommend(
    scored: list[ScoredCOA],
    asset_states: list[AssetState] | None = None,
    asset_inventory: dict[str, int] | None = None,
) -> Recommendation:
    """Select the top COA and explain alternatives and edge cases."""
    if not scored:
        return Recommendation(
            recommended=None,
            alternatives=[],
            recommended_package=None,
            alternative_packages=[],
            rationale="No courses of action available for assessment.",
            edge_cases="",
        )

    best = scored[0]
    alternatives = scored[1:]
    packages = build_portfolios(
        scored,
        asset_states=asset_states,
        asset_inventory=asset_inventory,
    )
    best_package = packages[0] if packages else None
    if best_package and (
        best_package.total_score < best.total_score + 0.5
        or best_package.feasibility_score < 0.65
    ):
        best_package = None
    alternative_packages = packages[1:] if len(packages) > 1 and best_package is not None else []

    rationale_parts = [
        f"{best.coa.title} ranks highest (score {best.total_score:.1f}/100).",
        f"Success probability: {best.simulation.success_probability:.0%}.",
    ]
    if best_package:
        lead_titles = ", ".join(item.coa.title for item in best_package.coas[:3])
        rationale_parts.append(
            f"Best coordinated bundle is rank {best_package.rank} at {best_package.total_score:.1f}/100 ({lead_titles})."
        )
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
    if best_package:
        edge_parts.append(
            f"Bundle {best_package.package_id} is a coordinated multi-COA plan with {len(best_package.coas)} advisory branches."
        )
    for package in alternative_packages[:2]:
        edge_parts.append(
            f"Package {package.package_id} (score {package.total_score:.1f}) covers "
            f"{len(package.coas)} coordinated COAs with {package.tradeoff_explanation.lower()}."
        )
    if not edge_parts:
        edge_parts.append("No alternative COAs evaluated.")

    logger.info("Recommendation: %s (score %.1f)", best.coa.coa_id, best.total_score)

    return Recommendation(
        recommended=best,
        alternatives=alternatives,
        recommended_package=best_package,
        alternative_packages=alternative_packages,
        rationale=rationale,
        edge_cases=" ".join(edge_parts),
    )
