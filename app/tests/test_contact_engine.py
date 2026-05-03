from datetime import datetime, timezone

from app.engine.contact_engine import SimulationScenario
from app.engine.scenario_generator import ScenarioGenerator


def _make_sim(scenario_id="baltic_hybrid_001", **kwargs):
    template = ScenarioGenerator(seed=42, **kwargs).generate(scenario_id)
    return SimulationScenario(template)


def test_trigger_contact_preserves_existing_speed_and_heading_when_null():
    scenario = _make_sim()
    entity = scenario.entities["VES-SUSP-001"]

    contact = scenario._create_trigger_contact(
        {
            "entity": "VES-SUSP-001",
            "action": "course_change",
            "new_heading": None,
            "new_speed": None,
        },
        datetime.now(timezone.utc),
    )

    assert contact.heading == entity["heading"]
    assert contact.speed == entity["speed"]
    assert entity["heading"] == 30.0
    assert entity["speed"] == 8.0
