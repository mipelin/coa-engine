"""Rules of Engagement engine — evaluates COAs against scenario ROE constraints.

ROE evaluation happens after scoring and before recommendation.
Each COA receives:
  - roe_status: allowed / restricted / requires_authorization / rejected
  - roe_reason: human-readable explanation
  - roe_constraints_triggered: list of constraint names that fired

No LLM calls are made inside this module.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..core.schemas import CourseOfAction, ScoredCOA, ThreatResult

logger = logging.getLogger("coa_engine.engine.roe_engine")


# ---------------------------------------------------------------------------
# ROE action categories — explicit, not inferred from template IDs alone
# ---------------------------------------------------------------------------

class ROEAction:
    monitor = "monitor"
    observe_isr = "observe_isr"
    coordinate = "coordinate"
    request_support = "request_support"
    shadow = "shadow"
    protect_infrastructure = "protect_infrastructure"
    combined_assertive = "combined_assertive"
    intercept_or_block = "intercept_or_block"


TEMPLATE_ROE_ACTION: dict[str, str] = {
    "COA-TPL-BASELINE": ROEAction.monitor,
    "COA-TPL-BORDER": ROEAction.monitor,
    "COA-TPL-ISR": ROEAction.observe_isr,
    "COA-TPL-AIRSPACE": ROEAction.coordinate,
    "COA-TPL-REINFORCE": ROEAction.request_support,
    "COA-TPL-SHADOW": ROEAction.shadow,
    "COA-TPL-CABLE-PROTECT": ROEAction.protect_infrastructure,
    "COA-TPL-COMBINED": ROEAction.combined_assertive,
}


@dataclass
class ROEConfig:
    min_threat_level_for_intercept: str = "HIGH"
    min_confidence_for_intercept: float = 0.6
    min_threat_for_shadow: str = "MEDIUM"
    min_threat_for_protect: str = "MEDIUM"
    min_threat_for_combined: str = "MEDIUM"
    max_allowed_escalation: float = 0.25
    civilian_proximity_restriction: bool = True
    escalation_policy: str = "restrict"

    THREAT_ORDER: list[str] = field(default_factory=lambda: ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

    def threat_meets(self, required: str, actual: str) -> bool:
        try:
            return self.THREAT_ORDER.index(actual) >= self.THREAT_ORDER.index(required)
        except ValueError:
            return False


DEFAULT_ROE = ROEConfig()


def _roe_action_for(template_id: str) -> str:
    return TEMPLATE_ROE_ACTION.get(template_id, ROEAction.monitor)


def evaluate_roe(
    scored: list[ScoredCOA],
    threats: list[ThreatResult],
    confidence: float = 0.8,
    civilian_proximity: bool = False,
    roe: ROEConfig | None = None,
) -> list[ScoredCOA]:
    """Evaluate each scored COA against ROE rules.

    Updates coa.roe_status, coa.roe_reason, coa.roe_constraints_triggered.
    Returns the same list (mutated in-place) with ROE annotations.
    """
    if roe is None:
        roe = DEFAULT_ROE

    threat_level = threats[0].threat_level.value if threats else "LOW"

    for scoa in scored:
        coa = scoa.coa
        action = _roe_action_for(coa.template_id)
        constraints: list[str] = []
        reasons: list[str] = []
        status = "allowed"

        # --- monitor / observe_isr / coordinate / request_support: always allowed ---
        if action in (ROEAction.monitor, ROEAction.observe_isr,
                      ROEAction.coordinate, ROEAction.request_support):
            pass

        # --- shadow: requires MEDIUM+ threat ---
        elif action == ROEAction.shadow:
            if not roe.threat_meets(roe.min_threat_for_shadow, threat_level):
                status = "rejected"
                constraints.append("min_threat_for_shadow")
                reasons.append(
                    f"Shadow requires {roe.min_threat_for_shadow}+ threat, current is {threat_level}"
                )

        # --- protect_infrastructure: allowed at MEDIUM+, auth at LOW ---
        elif action == ROEAction.protect_infrastructure:
            if not roe.threat_meets(roe.min_threat_for_protect, threat_level):
                status = "requires_authorization"
                constraints.append("low_threat_for_protection")
                reasons.append(
                    f"Infrastructure protection below {roe.min_threat_for_protect} threat "
                    f"({threat_level}) requires authorization"
                )
            elif confidence < roe.min_confidence_for_intercept * 0.8:
                status = "requires_authorization"
                constraints.append("low_confidence_protection")
                reasons.append(
                    f"Infrastructure protection with low confidence ({confidence:.0%}) requires authorization"
                )
            if status != "rejected" and roe.civilian_proximity_restriction and civilian_proximity:
                status = "requires_authorization"
                constraints.append("civilian_proximity")
                reasons.append("Infrastructure protection near civilian traffic requires authorization")

        # --- combined_assertive: restricted/requires_authorization, not bluntly rejected ---
        elif action == ROEAction.combined_assertive:
            if not roe.threat_meets(roe.min_threat_for_combined, threat_level):
                status = "requires_authorization"
                constraints.append("low_threat_for_combined")
                reasons.append(
                    f"Combined assertive response below {roe.min_threat_for_combined} threat "
                    f"({threat_level}) requires authorization"
                )
            else:
                status = "restricted"
                constraints.append("combined_assertive_action")
                reasons.append("Combined multi-axis response carries elevated operational risk")
            if status != "rejected" and confidence < roe.min_confidence_for_intercept:
                status = "requires_authorization"
                constraints.append("low_confidence_combined")
                reasons.append(
                    f"Combined assertive response with confidence {confidence:.0%} requires authorization"
                )
            if status != "rejected" and roe.civilian_proximity_restriction and civilian_proximity:
                status = "requires_authorization"
                constraints.append("civilian_proximity")
                reasons.append("Combined response near civilian airport or dense neutral traffic requires authorization")

        # --- intercept_or_block: strictest category (reserved for future use) ---
        elif action == ROEAction.intercept_or_block:
            if not roe.threat_meets(roe.min_threat_level_for_intercept, threat_level):
                status = "rejected"
                constraints.append("min_threat_for_intercept")
                reasons.append(
                    f"Intercept/block requires {roe.min_threat_level_for_intercept} threat, current is {threat_level}"
                )
            elif confidence < roe.min_confidence_for_intercept:
                status = "requires_authorization"
                constraints.append("low_confidence_intercept")
                reasons.append(
                    f"Intercept requires confidence ≥{roe.min_confidence_for_intercept:.0%}, "
                    f"current is {confidence:.0%}"
                )
            if status != "rejected" and roe.civilian_proximity_restriction and civilian_proximity:
                status = "requires_authorization"
                constraints.append("civilian_proximity")
                reasons.append("Intercept near civilian airport or dense neutral traffic requires authorization")

        # --- Escalation policy (applies on top of action-specific rules) ---
        if status == "allowed" and coa.escalation_risk > roe.max_allowed_escalation:
            if roe.escalation_policy == "reject":
                status = "rejected"
            elif roe.escalation_policy == "restrict":
                status = "restricted"
            constraints.append("escalation_risk_exceeded")
            reasons.append(
                f"Escalation risk {coa.escalation_risk:.0%} exceeds limit {roe.max_allowed_escalation:.0%}"
            )

        # Apply ROE annotations
        coa.roe_status = status
        coa.roe_reason = "; ".join(reasons) if reasons else "All ROE constraints satisfied"
        coa.roe_constraints_triggered = constraints

    allowed_count = sum(1 for s in scored if s.coa.roe_status == "allowed")
    restricted_count = sum(1 for s in scored if s.coa.roe_status in ("restricted", "requires_authorization", "rejected"))
    logger.info(
        "ROE evaluation: %d COAs — %d allowed, %d restricted/rejected",
        len(scored), allowed_count, restricted_count,
    )
    return scored
