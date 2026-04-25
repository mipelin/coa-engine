from __future__ import annotations

import json
import logging
from pathlib import Path

from ..core.schemas import OperationalEvent, Scenario

logger = logging.getLogger("coa_engine.engine.event_ingestion")

_SCENARIOS_DIR = Path(__file__).parent.parent / "data"

_registry_cache: dict[str, str] | None = None


def _build_registry() -> dict[str, str]:
    """Build scenario_id -> filename registry by reading each JSON file."""
    global _registry_cache
    if _registry_cache is not None:
        return _registry_cache

    result: dict[str, str] = {}
    if _SCENARIOS_DIR.exists():
        for f in _SCENARIOS_DIR.glob("sample_scenario_*.json"):
            try:
                with open(f) as fp:
                    raw = json.load(fp)
                sid = raw.get("scenario_id", f.stem.replace("sample_scenario_", ""))
                result[sid] = f.name
            except Exception as e:
                logger.warning("Failed to read scenario file %s: %s", f.name, e)

    _registry_cache = result
    return result


def list_scenarios() -> list[dict]:
    """Return metadata for all available scenarios."""
    registry = _build_registry()
    results = []
    for sid, fname in registry.items():
        path = _SCENARIOS_DIR / fname
        if path.exists():
            try:
                with open(path) as f:
                    raw = json.load(f)
                results.append({
                    "scenario_id": raw.get("scenario_id", sid),
                    "name": raw.get("name", sid),
                    "description": raw.get("description", "")[:120],
                    "event_count": len(raw.get("events", [])),
                    "file": fname,
                })
            except Exception as e:
                logger.warning("Failed to read scenario %s: %s", fname, e)
    return results


def load_sample_scenario() -> Scenario:
    """Load and validate the built-in Baltic Sea sample scenario."""
    path = _SCENARIOS_DIR / "sample_scenario_baltic.json"
    if not path.exists():
        raise FileNotFoundError(f"Sample scenario not found at {path}")
    with open(path) as f:
        raw = json.load(f)
    return Scenario.model_validate(raw)


def load_scenario(scenario_id: str) -> Scenario:
    """Load a specific scenario by ID."""
    registry = _build_registry()
    fname = registry.get(scenario_id)
    if not fname:
        raise ValueError(f"Unknown scenario: {scenario_id}. Available: {list(registry.keys())}")
    path = _SCENARIOS_DIR / fname
    if not path.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")
    with open(path) as f:
        raw = json.load(f)
    logger.info("Loaded scenario: %s (%s)", scenario_id, fname)
    return Scenario.model_validate(raw)


def load_scenario_events() -> list[OperationalEvent]:
    """Load validated events from the sample scenario."""
    scenario = load_sample_scenario()
    if not scenario.events:
        raise ValueError("Sample scenario contains no events")
    return scenario.events
