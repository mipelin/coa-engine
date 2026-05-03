from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.schemas import CourseOfAction
from ..i18n.static_translations import COA_TEMPLATE_TRANSLATIONS, SUPPORTED_STATIC_LANGUAGES


@dataclass
class COATemplate:
    """A parameterized COA template that gets bound to scenario entities."""

    template_id: str
    title_template: str
    description_template: str
    required_assets: list[str]
    assumptions: list[str]
    estimated_time_minutes: int
    expected_effect_template: str
    objective_template: str
    rationale_template: str
    risk_categories: list[str]
    escalation_risk: float
    civilian_risk: float
    logistics_burden: float
    trigger_conditions: list[str] = field(default_factory=list)

    def _localized_bundle(
        self,
        entities: str,
        infra: str,
        scenario_context: str,
    ) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for language in SUPPORTED_STATIC_LANGUAGES:
            text = COA_TEMPLATE_TRANSLATIONS.get(self.template_id, {}).get(language) or COA_TEMPLATE_TRANSLATIONS.get(self.template_id, {}).get("en", {})
            if not text:
                continue
            result[language] = {
                "title": str(text["title_template"]).format(entities=entities, infra=infra, context=scenario_context),
                "description": str(text["description_template"]).format(entities=entities, infra=infra, context=scenario_context),
                "assumptions": list(text["assumptions"]),
                "expected_effect": str(text["expected_effect_template"]).format(entities=entities, infra=infra),
                "objective": str(text["objective_template"]).format(entities=entities, infra=infra, context=scenario_context),
                "rationale": str(text["rationale_template"]).format(entities=entities, infra=infra, context=scenario_context),
            }
        return result

    def bind(
        self,
        entities: list[dict[str, Any]] | None = None,
        assets: dict[str, int] | None = None,
        infra: str = "critical infrastructure",
        scenario_context: str = "",
    ) -> CourseOfAction:
        """Bind template parameters to produce a concrete COA."""
        entity_names = ", ".join(e.get("name", e.get("entity_id", "unknown")) for e in (entities or []))
        entity_label = entity_names or "identified contacts"
        localized = self._localized_bundle(entity_label, infra, scenario_context)

        title = self.title_template.format(
            entities=entity_label,
            infra=infra,
            context=scenario_context,
        )
        description = self.description_template.format(
            entities=entity_label,
            infra=infra,
            context=scenario_context,
        )
        expected_effect = self.expected_effect_template.format(
            entities=entity_label,
            infra=infra,
        )
        objective = self.objective_template.format(
            entities=entity_label,
            infra=infra,
            context=scenario_context,
        )
        rationale = self.rationale_template.format(
            entities=entity_label,
            infra=infra,
            context=scenario_context,
        )
        target_entities = [e.get("entity_id", "") for e in (entities or []) if e.get("entity_id")]

        return CourseOfAction(
            coa_id=self.template_id,
            template_id=self.template_id,
            title=title,
            description=description,
            target_entities=target_entities,
            required_assets=list(self.required_assets),
            assigned_assets=[],
            assumptions=list(self.assumptions),
            estimated_time_minutes=self.estimated_time_minutes,
            expected_effect=expected_effect,
            objective=objective,
            rationale=rationale,
            risk_categories=list(self.risk_categories),
            escalation_risk=self.escalation_risk,
            civilian_risk=self.civilian_risk,
            logistics_burden=self.logistics_burden,
            feasibility_status="unknown",
            validation_warnings=[],
            source="template_engine",
            localized=localized or None,
        )


TEMPLATES: list[COATemplate] = [
    COATemplate(
        template_id="COA-TPL-ISR",
        title_template="Increase ISR Coverage and Observation",
        description_template=(
            "Recommend increasing ISR coverage to maintain persistent observation "
            "of {entities}. Coordinate with available tactical UAV assets "
            "and satellite observation requests to improve coverage of the {infra} corridor."
        ),
        required_assets=["isr_uav", "satellite_observation_request", "sigint_team"],
        assumptions=[
            "ISR assets can be redirected within 30 minutes",
            "Weather permits UAV operations in the area",
            "Satellite revisit time is acceptable for tracking",
        ],
        estimated_time_minutes=30,
        expected_effect_template="Persistent observation of suspicious entities and {infra} corridor",
        objective_template="Maintain persistent awareness over {entities} and the {infra} corridor.",
        rationale_template="Selected because the situation requires better observation before higher-friction measures are considered.",
        risk_categories=["sensor_gap", "weather"],
        escalation_risk=0.05,
        civilian_risk=0.0,
        logistics_burden=0.2,
        trigger_conditions=["always"],
    ),
    COATemplate(
        template_id="COA-TPL-SHADOW",
        title_template="Shadow Suspicious Vessels with Allied Maritime Assets",
        description_template=(
            "Recommend allied maritime patrol assets maintain visual and radar contact "
            "with {entities}. Maintain safe distance. Document activity "
            "and report observations through established channels."
        ),
        required_assets=["maritime_patrol_asset", "coast_guard_liaison"],
        assumptions=[
            "Allied naval assets are available within 60 minutes",
            "Rules of observation are clearly communicated",
            "Vessels will not attempt evasion at high speed",
        ],
        estimated_time_minutes=60,
        expected_effect_template="Direct observation and deterrence through presence near {entities}",
        objective_template="Maintain close observation of {entities} using allied maritime presence.",
        rationale_template="Selected because the threat picture suggests continued contact management and pattern collection are required.",
        risk_categories=["proximity_incident", "navigation_safety"],
        escalation_risk=0.15,
        civilian_risk=0.05,
        logistics_burden=0.4,
        trigger_conditions=["high_threat"],
    ),
    COATemplate(
        template_id="COA-TPL-CABLE-PROTECT",
        title_template="Prioritize Protection of {infra}",
        description_template=(
            "Given confirmed cable compromise, recommend prioritizing "
            "monitoring and protection of remaining {infra}. Consider assigning the nearest "
            "available allied maritime asset to observe the cable corridor. "
            "Coordinate with cable operator for continuous integrity monitoring."
        ),
        required_assets=["maritime_patrol_asset", "cable_operator_liaison", "isr_uav"],
        assumptions=[
            "Secondary infrastructure has not yet been compromised",
            "Nearest allied asset can reach the area within 90 minutes",
            "Cable operator can provide continuous integrity status",
        ],
        estimated_time_minutes=90,
        expected_effect_template="Reduced risk of further compromise to {infra}",
        objective_template="Protect remaining {infra} from follow-on disruption.",
        rationale_template="Selected because confirmed infrastructure compromise shifts priority toward protecting the remaining network.",
        risk_categories=["asset_availability", "response_time"],
        escalation_risk=0.10,
        civilian_risk=0.0,
        logistics_burden=0.5,
        trigger_conditions=["cable_severance"],
    ),
    COATemplate(
        template_id="COA-TPL-AIRSPACE",
        title_template="Coordinate Civilian Airspace Safety Response",
        description_template=(
            "Recommend coordination with civil aviation authority to manage "
            "airspace around affected area. Support establishment of temporary "
            "flight restrictions. Share available sensor data with air traffic control."
        ),
        required_assets=["airspace_coordinator", "atc_liaison", "sensor_data_feed"],
        assumptions=[
            "Civil aviation authority is responsive",
            "UAV does not escalate to controlled airspace breach",
            "Commercial diversions can be managed without major disruption",
        ],
        estimated_time_minutes=20,
        expected_effect_template="Safe civilian airspace management during UAV incident near {infra}",
        objective_template="Reduce civilian airspace disruption and improve safety around the affected area.",
        rationale_template="Selected because UAV activity near civilian airspace requires coordinated civil-safety management.",
        risk_categories=["airspace_safety", "public_disruption"],
        escalation_risk=0.05,
        civilian_risk=0.1,
        logistics_burden=0.2,
        trigger_conditions=["uav_detected"],
    ),
    COATemplate(
        template_id="COA-TPL-BORDER",
        title_template="Increase Border Monitoring and Information Sharing",
        description_template=(
            "Recommend increased monitoring of border areas where convoy activity "
            "has been reported. Coordinate information sharing with border security "
            "and allied intelligence. Maintain an awareness-focused posture."
        ),
        required_assets=["border_patrol_liaison", "intelligence_team", "surveillance_asset"],
        assumptions=[
            "Convoy activity is observable through existing ISR",
            "Border security forces can increase patrol frequency",
            "Convoy movements remain indicators requiring corroboration",
        ],
        estimated_time_minutes=45,
        expected_effect_template="Enhanced situational awareness of ground movements near {infra}",
        objective_template="Increase awareness of convoy activity and related movements near {infra}.",
        rationale_template="Selected because convoy indicators require cross-agency monitoring rather than isolated reporting.",
        risk_categories=["intelligence_gap", "response_latency"],
        escalation_risk=0.08,
        civilian_risk=0.02,
        logistics_burden=0.3,
        trigger_conditions=["convoy_activity"],
    ),
    COATemplate(
        template_id="COA-TPL-COMBINED",
        title_template="Combined Observation, Cable Protection, and Border Monitoring",
        description_template=(
            "Recommend a combined approach: shadow {entities} while "
            "simultaneously increasing observation of {infra} and expanding "
            "border monitoring. Most resource-intensive but addresses all threat vectors."
        ),
        required_assets=[
            "maritime_patrol_asset", "isr_uav", "cable_operator_liaison",
            "border_patrol_liaison", "intelligence_team", "coast_guard_liaison",
        ],
        assumptions=[
            "Sufficient assets available for multi-axis response",
            "Coordination staff can manage concurrent advisory workflows",
            "Logistics support is available for extended operations",
        ],
        estimated_time_minutes=90,
        expected_effect_template="Comprehensive coverage across all threat domains near {infra}",
        objective_template="Coordinate observation, protection, and contingency posture around {infra} and {entities}.",
        rationale_template="Selected because multiple concurrent threat indicators justify a combined, resource-intensive response posture.",
        risk_categories=["resource_strain", "coordination_complexity"],
        escalation_risk=0.20,
        civilian_risk=0.05,
        logistics_burden=0.8,
        trigger_conditions=["high_threat", "friendly_support_high", "multi_contact_pressure"],
    ),
    COATemplate(
        template_id="COA-TPL-REINFORCE",
        title_template="Request Additional Allied Support and Sustain Monitoring",
        description_template=(
            "Current contact pressure exceeds the immediately available friendly support posture. "
            "Recommend requesting additional allied maritime and ISR coverage while sustaining "
            "monitoring of {entities} and the {infra} area."
        ),
        required_assets=["intelligence_team", "sensor_data_feed", "coast_guard_liaison"],
        assumptions=[
            "Higher headquarters or partners can allocate additional support",
            "Existing local forces can maintain observation until relief arrives",
            "The operating picture remains fluid and requires coordinated reinforcement",
        ],
        estimated_time_minutes=40,
        expected_effect_template="Improved friendly force balance and monitoring resilience around {infra}",
        objective_template="Stabilize the surveillance posture and request reinforcements for {entities} near {infra}.",
        rationale_template="Selected because contact pressure currently exceeds the friendly support available in theater.",
        risk_categories=["response_gap", "reinforcement_delay"],
        escalation_risk=0.08,
        civilian_risk=0.02,
        logistics_burden=0.35,
        trigger_conditions=["high_threat", "support_gap"],
    ),
    COATemplate(
        template_id="COA-TPL-BASELINE",
        title_template="Maintain Baseline Monitoring",
        description_template="No elevated threat indicators detected. Recommend continuing routine monitoring.",
        required_assets=["standard_watch_team"],
        assumptions=["No change in current threat picture"],
        estimated_time_minutes=0,
        expected_effect_template="Continued situational awareness at baseline level near {infra}",
        objective_template="Maintain baseline awareness of {infra} and the operating area.",
        rationale_template="Selected because no stronger threat-matched advisory action currently dominates baseline monitoring.",
        risk_categories=["detection_lag"],
        escalation_risk=0.0,
        civilian_risk=0.0,
        logistics_burden=0.0,
        trigger_conditions=["fallback"],
    ),
]


def select_templates(
    cable_severed: bool = False,
    uav_threat: bool = False,
    convoy_active: bool = False,
    high_threat: bool = False,
    critical_threat: bool = False,
    friendly_support_available: bool = False,
    friendly_support_high: bool = False,
    support_gap: bool = False,
    multi_contact_pressure: bool = False,
) -> list[COATemplate]:
    """Select relevant templates based on scenario conditions."""
    flags = {
        "cable_severance": cable_severed,
        "uav_detected": uav_threat,
        "convoy_activity": convoy_active,
        "high_threat": high_threat,
        "critical_threat": critical_threat,
        "friendly_support_available": friendly_support_available,
        "friendly_support_high": friendly_support_high,
        "support_gap": support_gap,
        "multi_contact_pressure": multi_contact_pressure,
    }

    matched: list[COATemplate] = []

    for tpl in TEMPLATES:
        if tpl.template_id == "COA-TPL-BASELINE":
            continue
        conditions = tpl.trigger_conditions

        if "always" in conditions:
            matched.append(tpl)
            continue

        # Multi-condition: ALL non-meta conditions must be met
        if "fallback" in conditions:
            continue

        if all(flags.get(c, False) for c in conditions):
            matched.append(tpl)

    if not matched:
        for tpl in TEMPLATES:
            if tpl.template_id == "COA-TPL-BASELINE":
                matched.append(tpl)

    return matched
