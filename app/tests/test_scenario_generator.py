"""Tests for scenario_generator and its integration with SimulationScenario."""

import pytest

from app.engine.contact_engine import SimulationScenario
from app.engine.scenario_generator import (
    EntitySpec,
    ScenarioGenerator,
    ScenarioTemplate,
    StimulusEvent,
    _TEMPLATE_BUILDERS,
)


# ---------------------------------------------------------------------------
# Scenario template loading
# ---------------------------------------------------------------------------


class TestScenarioLoading:
    @pytest.mark.parametrize("scenario_id", ["baltic_hybrid_001", "arctic_submarine_001", "mediterranean_001"])
    def test_scenario_loads_correctly(self, scenario_id):
        gen = ScenarioGenerator(seed=42)
        template = gen.generate(scenario_id)
        assert template.scenario_id == scenario_id
        assert len(template.entities) >= 4
        assert len(template.stimuli) >= 3
        assert template.bounds["lat_min"] < template.bounds["lat_max"]
        assert template.bounds["lon_min"] < template.bounds["lon_max"]

    def test_unknown_scenario_raises(self):
        gen = ScenarioGenerator(seed=42)
        with pytest.raises(ValueError, match="Unknown scenario template"):
            gen.generate("nonexistent_scenario")

    def test_mediterranean_swarm_alias(self):
        gen = ScenarioGenerator(seed=42)
        template = gen.generate("mediterranean_swarm_001")
        assert template.scenario_id == "mediterranean_001"


class TestScenarioMetadata:
    def test_metadata_fields(self):
        gen = ScenarioGenerator(seed=42)
        template = gen.generate("baltic_hybrid_001")
        meta = template.metadata
        assert meta["scenario_id"] == "baltic_hybrid_001"
        assert meta["display_name"].startswith("Baltic Cable Protection")
        assert "description" in meta
        assert meta["entity_count"] >= 4
        assert meta["stimuli_count"] >= 3
        assert meta["seed"] == 42
        assert "environment" in meta

    def test_list_templates(self):
        templates = ScenarioGenerator.list_templates()
        ids = {t["scenario_id"] for t in templates}
        assert "baltic_hybrid_001" in ids
        assert "arctic_submarine_001" in ids
        assert "mediterranean_001" in ids


# ---------------------------------------------------------------------------
# Stimuli timeline
# ---------------------------------------------------------------------------


class TestStimuliTimeline:
    def test_stimuli_fire_at_expected_ticks(self):
        gen = ScenarioGenerator(seed=42)
        template = gen.generate("baltic_hybrid_001")
        ticks = [s.tick for s in template.stimuli]
        assert 10 in ticks  # cable_severance
        assert 18 in ticks  # jamming

    def test_upcoming_stimuli_excludes_past(self):
        gen = ScenarioGenerator(seed=42)
        template = gen.generate("baltic_hybrid_001")
        upcoming = template.upcoming_stimuli(current_tick=10)
        assert all(s.tick > 10 for s in upcoming)

    def test_active_stimuli_at_tick(self):
        gen = ScenarioGenerator(seed=42)
        template = gen.generate("baltic_hybrid_001")
        active = template.active_stimuli(current_tick=10)
        assert len(active) >= 1
        assert active[0].action == "cable_severance"

    def test_stimulus_to_trigger_dict(self):
        s = StimulusEvent(tick=10, action="jamming", lat=57.5, lon=18.5, radius_nm=20)
        d = s.to_trigger()
        assert d["tick"] == 10
        assert d["action"] == "jamming"
        assert d["lat"] == 57.5
        assert "entity" not in d

    def test_entity_stimulus_to_trigger(self):
        s = StimulusEvent(tick=5, action="course_change", entity="VES-001", new_heading=180.0)
        d = s.to_trigger()
        assert d["entity"] == "VES-001"
        assert d["new_heading"] == 180.0


# ---------------------------------------------------------------------------
# Deterministic replay
# ---------------------------------------------------------------------------


class TestDeterministicReplay:
    def test_same_seed_same_stimuli(self):
        gen1 = ScenarioGenerator(seed=42)
        gen2 = ScenarioGenerator(seed=42)
        t1 = gen1.generate("baltic_hybrid_001")
        t2 = gen2.generate("baltic_hybrid_001")
        for s1, s2 in zip(t1.stimuli, t2.stimuli):
            assert s1.tick == s2.tick
            assert s1.action == s2.action

    def test_same_seed_no_jitter_no_change(self):
        gen_plain = ScenarioGenerator(seed=42, timing_jitter=0)
        t = gen_plain.generate("baltic_hybrid_001")
        original_ticks = [s.tick for s in t.stimuli]
        # Regenerate — should be identical
        t2 = gen_plain.generate("baltic_hybrid_001")
        assert [s.tick for s in t2.stimuli] == original_ticks

    def test_different_seeds_different_timing_with_jitter(self):
        gen_a = ScenarioGenerator(seed=42, timing_jitter=2)
        gen_b = ScenarioGenerator(seed=99, timing_jitter=2)
        t_a = gen_a.generate("baltic_hybrid_001")
        t_b = gen_b.generate("baltic_hybrid_001")
        # At least one stimulus tick should differ
        ticks_a = [s.tick for s in t_a.stimuli]
        ticks_b = [s.tick for s in t_b.stimuli]
        assert ticks_a != ticks_b

    def test_different_seeds_different_positions_with_jitter(self):
        gen_a = ScenarioGenerator(seed=42, position_jitter=0.1)
        gen_b = ScenarioGenerator(seed=99, position_jitter=0.1)
        t_a = gen_a.generate("baltic_hybrid_001")
        t_b = gen_b.generate("baltic_hybrid_001")
        # At least one entity position should differ
        lats_a = [e.lat for e in t_a.entities]
        lats_b = [e.lat for e in t_b.entities]
        assert lats_a != lats_b

    def test_jitter_produces_valid_scenario(self):
        gen = ScenarioGenerator(seed=42, timing_jitter=2, position_jitter=0.05)
        template = gen.generate("baltic_hybrid_001")
        assert len(template.entities) >= 4
        assert len(template.stimuli) >= 3
        for s in template.stimuli:
            assert s.tick >= 1
        for e in template.entities:
            assert template.bounds["lat_min"] <= e.lat <= template.bounds["lat_max"]
            assert template.bounds["lon_min"] <= e.lon <= template.bounds["lon_max"]


# ---------------------------------------------------------------------------
# Integration with SimulationScenario
# ---------------------------------------------------------------------------


def _make_sim(scenario_id="baltic_hybrid_001", **kwargs):
    template = ScenarioGenerator(seed=42, **kwargs).generate(scenario_id)
    return SimulationScenario(template)


class TestSimulationScenarioIntegration:
    def test_scenario_loads_via_generator(self):
        sim = _make_sim()
        assert len(sim.entities) >= 4
        assert sim._triggers  # stimuli loaded from generator

    def test_metadata_accessible(self):
        sim = _make_sim()
        meta = sim.scenario_metadata
        assert meta["scenario_id"] == "baltic_hybrid_001"
        assert "display_name" in meta

    def test_upcoming_stimuli_accessible(self):
        sim = _make_sim()
        sim.tick = 0
        upcoming = sim.upcoming_stimuli
        assert len(upcoming) >= 3

    def test_stimuli_fire_during_tick_forward(self):
        sim = _make_sim()
        # Tick through to tick 10 (cable_severance)
        for _ in range(10):
            contacts = sim.tick_forward()
        # At tick 10, cable severance should fire
        cable_events = [c for c in contacts if c.contact_type.value == "cable_event"]
        assert cable_events, "Cable severance should fire at tick 10"

    def test_deterministic_replay_via_simulation(self):
        sim1 = _make_sim()
        sim2 = _make_sim()
        for _ in range(15):
            c1 = sim1.tick_forward()
            c2 = sim2.tick_forward()
            for a, b in zip(c1, c2):
                assert a.lat == b.lat
                assert a.lon == b.lon

    def test_arctic_scenario_loads(self):
        sim = _make_sim("arctic_submarine_001")
        assert len(sim.entities) >= 4
        meta = sim.scenario_metadata
        assert meta["scenario_id"] == "arctic_submarine_001"

    def test_mediterranean_scenario_loads(self):
        sim = _make_sim("mediterranean_001")
        assert len(sim.entities) >= 4
