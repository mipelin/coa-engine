from __future__ import annotations

from ..core.schemas import DependencyEdge, PlanPackage, PlanTask, ScoredCOA, ScoredCOAPackage
from ..i18n.static_translations import PLAN_PACKAGE_TRANSLATIONS, SUPPORTED_STATIC_LANGUAGES


TASK_LIBRARY: dict[str, list[dict[str, object]]] = {
    "COA-TPL-SHADOW": [
        {
            "task_type": "shadow",
            "title": "Establish shadow track",
            "description": "Maintain visual/radar contact at safe distance and report pattern changes.",
            "required_capabilities": ["maritime_patrol_asset"],
            "start_offset_min": 0,
            "duration_min": 180,
            "preconditions": ["Maritime asset on station"],
        },
    ],
    "COA-TPL-ISR": [
        {
            "task_type": "deploy_isr",
            "title": "Deploy ISR collection",
            "description": "Launch UAV and request supporting remote sensing over the operating corridor.",
            "required_capabilities": ["isr_uav", "sensor_data_feed"],
            "start_offset_min": 0,
            "duration_min": 120,
            "preconditions": ["Weather permits ISR collection"],
        },
    ],
    "COA-TPL-CABLE-PROTECT": [
        {
            "task_type": "protect_zone",
            "title": "Protect cable corridor",
            "description": "Maintain patrol and integrity monitoring over the remaining cable route.",
            "required_capabilities": ["maritime_patrol_asset", "cable_operator_liaison"],
            "start_offset_min": 0,
            "duration_min": 240,
            "preconditions": ["Patrol asset can hold station near infrastructure"],
        },
    ],
    "COA-TPL-AIRSPACE": [
        {
            "task_type": "coordinate_airspace",
            "title": "Coordinate civil airspace",
            "description": "Set temporary procedures with civil aviation actors and distribute sensor cues.",
            "required_capabilities": ["airspace_coordinator", "atc_liaison", "sensor_data_feed"],
            "start_offset_min": 0,
            "duration_min": 90,
            "preconditions": ["Civil aviation authority reachable"],
        },
    ],
    "COA-TPL-BORDER": [
        {
            "task_type": "border_monitor",
            "title": "Increase border monitoring",
            "description": "Coordinate surveillance and reporting over convoy approaches and crossings.",
            "required_capabilities": ["border_patrol_liaison", "surveillance_asset"],
            "start_offset_min": 0,
            "duration_min": 150,
            "preconditions": ["Border patrol liaison available"],
        },
    ],
}


def _task_specs_for_coa(scored: ScoredCOA) -> list[dict[str, object]]:
    specs = list(TASK_LIBRARY.get(scored.coa.template_id, []))
    if not specs:
        specs = [{
            "task_type": "monitor",
            "title": scored.coa.title,
            "description": scored.coa.description,
            "required_capabilities": list(scored.coa.required_assets),
            "start_offset_min": 0,
            "duration_min": scored.coa.estimated_time_minutes,
            "preconditions": list(scored.coa.assumptions[:2]),
        }]
    return specs


def _localized_task_bundle(scored: ScoredCOA, index: int) -> dict[str, dict[str, object]]:
    bundle: dict[str, dict[str, object]] = {}
    for language in SUPPORTED_STATIC_LANGUAGES:
        lang_catalog = PLAN_PACKAGE_TRANSLATIONS.get(language, PLAN_PACKAGE_TRANSLATIONS["en"])
        task_specs = lang_catalog.get("tasks", {}).get(scored.coa.template_id)
        if task_specs and index < len(task_specs):
            spec = task_specs[index]
            bundle[language] = {
                "title": spec["title"],
                "description": spec["description"],
                "preconditions": list(spec.get("preconditions", [])),
            }
    return bundle


def build_plan_package(package: ScoredCOAPackage) -> PlanPackage:
    tasks: list[PlanTask] = []
    dependencies: list[DependencyEdge] = []
    reserved_assets: list[str] = []
    planning_assumptions: list[str] = []
    previous_terminal_task_id: str | None = None

    for coa_index, scored in enumerate(package.coas, start=1):
        specs = _task_specs_for_coa(scored)
        for task_index, spec in enumerate(specs, start=1):
            task_id = f"{package.package_id}-T{len(tasks) + 1}"
            task = PlanTask(
                task_id=task_id,
                task_type=str(spec["task_type"]),
                title=str(spec["title"]),
                description=str(spec["description"]),
                target_entities=list(scored.coa.target_entities),
                assigned_assets=list(scored.coa.assigned_assets),
                required_capabilities=list(spec.get("required_capabilities", [])),
                start_offset_min=int(spec.get("start_offset_min", 0)),
                duration_min=int(spec.get("duration_min", scored.coa.estimated_time_minutes)),
                preconditions=list(spec.get("preconditions", [])),
                expected_effect=scored.coa.expected_effect,
                localized=_localized_task_bundle(scored, task_index - 1) or None,
            )
            tasks.append(task)
            reserved_assets.extend(scored.coa.assigned_assets)
            planning_assumptions.extend(scored.coa.assumptions[:2])

            if previous_terminal_task_id is not None and task_index == 1:
                dependencies.append(DependencyEdge(
                    predecessor_task_id=previous_terminal_task_id,
                    successor_task_id=task_id,
                    dependency_type="soft_sync",
                    condition="Coordinate package branches and deconflict scarce assets",
                    localized={
                        language: {"condition": PLAN_PACKAGE_TRANSLATIONS.get(language, PLAN_PACKAGE_TRANSLATIONS["en"])["soft_sync_condition"]}
                        for language in SUPPORTED_STATIC_LANGUAGES
                    },
                ))

            if task_index > 1:
                dependencies.append(DependencyEdge(
                    predecessor_task_id=tasks[-2].task_id,
                    successor_task_id=task_id,
                    dependency_type="finish_to_start",
                    condition="Prior task establishes the required observation picture",
                    localized={
                        language: {"condition": PLAN_PACKAGE_TRANSLATIONS.get(language, PLAN_PACKAGE_TRANSLATIONS["en"])["finish_to_start_condition"]}
                        for language in SUPPORTED_STATIC_LANGUAGES
                    },
                ))

        if tasks:
            previous_terminal_task_id = tasks[-1].task_id
        coa_index += 1

    if len(package.coas) >= 2:
        dependencies.append(DependencyEdge(
            predecessor_task_id=tasks[0].task_id,
            successor_task_id=tasks[-1].task_id,
            dependency_type="conditional",
            condition="Escalate later package actions only if monitoring confirms persistence or approach",
            localized={
                language: {"condition": PLAN_PACKAGE_TRANSLATIONS.get(language, PLAN_PACKAGE_TRANSLATIONS["en"])["conditional_condition"]}
                for language in SUPPORTED_STATIC_LANGUAGES
            },
        ))

    titles = ", ".join(scored.coa.title for scored in package.coas)
    localized: dict[str, dict[str, object]] = {}
    for language in SUPPORTED_STATIC_LANGUAGES:
        lang_catalog = PLAN_PACKAGE_TRANSLATIONS.get(language, PLAN_PACKAGE_TRANSLATIONS["en"])
        localized_titles = ", ".join(
            (item.coa.localized or {}).get(language, {}).get("title", item.coa.title)
            for item in package.coas
        )
        localized[language] = {
            "title": str(lang_catalog["package_title"]).format(titles=localized_titles),
            "summary": lang_catalog["package_summary"],
        }
    return PlanPackage(
        package_id=package.package_id,
        title=f"Coordinated package for {titles}",
        summary=(
            "Sequenced advisory package with task dependencies, explicit asset reservation, "
            "and branch coordination across the selected COAs."
        ),
        tasks=tasks,
        dependencies=dependencies,
        reserved_assets=sorted(set(reserved_assets)),
        planning_assumptions=sorted(set(planning_assumptions)),
        localized=localized,
    )
