from __future__ import annotations

from ..core.schemas import CourseOfAction, ScoredCOA, SimulationResult

# Scoring weights (must sum to 1.0)
W_SUCCESS = 0.30
W_TIME = 0.10
W_CABLE_PROTECT = 0.20
W_ESCALATION = 0.15
W_CIVILIAN = 0.10
W_LOGISTICS = 0.05
W_MISSED_DET = 0.10


def _normalize_time(time_min: float, max_time: float = 120.0) -> float:
    """Return 1.0 for fastest, 0.0 for slowest."""
    if max_time <= 0:
        return 1.0
    return max(0.0, 1.0 - time_min / max_time)


def score_coas(
    coas: list[CourseOfAction],
    simulations: list[SimulationResult],
) -> list[ScoredCOA]:
    """Score and rank COAs using a weighted formula."""
    sim_by_id = {s.coa_id: s for s in simulations}
    scored: list[ScoredCOA] = []

    for coa in coas:
        sim = sim_by_id.get(coa.coa_id)
        if sim is None:
            continue

        success = sim.success_probability
        time_score = _normalize_time(sim.expected_time_to_effect)
        cable_protect = 1.0 - sim.risk_to_second_cable
        escalation = 1.0 - sim.escalation_probability
        civilian = 1.0 - coa.civilian_risk
        logistics = 1.0 - coa.logistics_burden
        detection = 1.0 - sim.missed_detection_probability
        feasibility = coa.feasibility_score

        raw = (
            W_SUCCESS * success
            + W_TIME * time_score
            + W_CABLE_PROTECT * cable_protect
            + W_ESCALATION * escalation
            + W_CIVILIAN * civilian
            + W_LOGISTICS * logistics
            + W_MISSED_DET * detection
        )
        # Infeasible COAs should not outrank executable ones simply because their
        # theoretical performance is strong on paper.
        raw *= 0.2 + 0.8 * feasibility
        total = round(raw * 100.0, 1)

        tradeoffs: list[str] = []
        if feasibility == 0.0:
            tradeoffs.append("Not supportable with current asset inventory")
        elif feasibility < 1.0:
            tradeoffs.append(f"Only {feasibility:.0%} asset support available")
        if sim.success_probability > 0.7:
            tradeoffs.append("High success probability")
        elif sim.success_probability < 0.5:
            tradeoffs.append("Lower success probability — may require reinforcement")
        if sim.escalation_probability > 0.15:
            tradeoffs.append("Moderate escalation risk")
        if sim.risk_to_second_cable > 0.3:
            tradeoffs.append("Elevated risk to second cable")
        if coa.logistics_burden > 0.6:
            tradeoffs.append("High logistics requirement")
        if sim.missed_detection_probability > 0.2:
            tradeoffs.append("Higher chance of missed detection")
        if coa.missing_assets:
            tradeoffs.append("Limited by unavailable assets")
        if not tradeoffs:
            tradeoffs.append("Balanced risk profile")

        scored.append(ScoredCOA(
            coa=coa,
            simulation=sim,
            total_score=total,
            rank=0,
            tradeoff_explanation="; ".join(tradeoffs),
        ))

    scored.sort(key=lambda s: s.total_score, reverse=True)
    for i, s in enumerate(scored, 1):
        s.rank = i

    return scored
