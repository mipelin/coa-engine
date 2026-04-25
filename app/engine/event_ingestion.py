from __future__ import annotations

import json
from pathlib import Path

from ..core.schemas import OperationalEvent, Scenario

_SCENARIO_PATH = Path(__file__).parent.parent / "data" / "sample_scenario_baltic.json"


def load_sample_scenario() -> Scenario:
    """Load and validate the built-in Baltic Sea sample scenario."""
    if not _SCENARIO_PATH.exists():
        raise FileNotFoundError(f"Sample scenario not found at {_SCENARIO_PATH}")
    with open(_SCENARIO_PATH) as f:
        raw = json.load(f)
    return Scenario.model_validate(raw)


def load_scenario_events() -> list[OperationalEvent]:
    """Load validated events from the sample scenario."""
    scenario = load_sample_scenario()
    if not scenario.events:
        raise ValueError("Sample scenario contains no events")
    return scenario.events
