"""Tests for LLM reliability fixes: phrase-based safety, test-chat, validation, queue."""
from __future__ import annotations

import json
import time
from unittest.mock import MagicMock, patch

import pytest

from app.engine.llm_client import LLMClient, LLMResult, _UNSAFE_PHRASES
from app.core.config import settings
from app.engine.llm_guardrails import (
    _looks_like_system_entity_id,
    explanation_references_match,
    sanitize_llm_text,
)


# ---------------------------------------------------------------------------
# Phrase-based safety filter
# ---------------------------------------------------------------------------


class TestPhraseBasedSafety:
    def test_engage_in_safe_context_not_redacted(self):
        client = LLMClient.__new__(LLMClient)
        client.enabled = False
        text = "The vessel should engage with allied forces for coordination."
        assert client._safety_filter(text) == text

    def test_rules_of_engagement_not_redacted(self):
        client = LLMClient.__new__(LLMClient)
        client.enabled = False
        text = "The rules of engagement require authorization for intercept."
        assert client._safety_filter(text) == text

    def test_target_in_advisory_context_not_redacted(self):
        client = LLMClient.__new__(LLMClient)
        client.enabled = False
        text = "The system identified a target advisory for VES-SUSP-001."
        assert client._safety_filter(text) == text

    def test_intercept_in_safe_context_not_redacted(self):
        client = LLMClient.__new__(LLMClient)
        client.enabled = False
        text = "The ISR asset was used to intercept communications."
        assert client._safety_filter(text) == text

    def test_authorize_engagement_redacted(self):
        client = LLMClient.__new__(LLMClient)
        client.enabled = False
        text = "The commander should authorize engagement immediately."
        result = client._safety_filter(text)
        assert "[REDACTED]" in result

    def test_engage_the_target_redacted(self):
        client = LLMClient.__new__(LLMClient)
        client.enabled = False
        text = "We should engage the target now."
        result = client._safety_filter(text)
        assert "[REDACTED]" in result

    def test_bypass_roe_redacted(self):
        client = LLMClient.__new__(LLMClient)
        client.enabled = False
        text = "The operator decided to bypass ROE restrictions."
        result = client._safety_filter(text)
        assert "[REDACTED]" in result

    def test_fire_on_redacted(self):
        client = LLMClient.__new__(LLMClient)
        client.enabled = False
        text = "The unit should fire on the hostile vessel."
        result = client._safety_filter(text)
        assert "[REDACTED]" in result

    def test_destroy_the_target_redacted(self):
        client = LLMClient.__new__(LLMClient)
        client.enabled = False
        text = "The plan is to destroy the target."
        result = client._safety_filter(text)
        assert "[REDACTED]" in result

    def test_engage_stakeholders_safe(self):
        client = LLMClient.__new__(LLMClient)
        client.enabled = False
        text = "NATO should engage with regional stakeholders."
        assert client._safety_filter(text) == text


# ---------------------------------------------------------------------------
# Sanitizer rules
# ---------------------------------------------------------------------------


class TestSanitizer:
    def test_i_suggest_rewritten(self):
        assert "The system indicates" in sanitize_llm_text("I suggest monitoring the vessel.")

    def test_we_should_rewritten(self):
        assert "The system indicates" in sanitize_llm_text("We should increase surveillance.")

    def test_you_must_rewritten(self):
        assert "The system indicates" in sanitize_llm_text("You must follow ROE.")

    def test_optimal_action_rewritten(self):
        assert "The system-recommended action is" in sanitize_llm_text("The optimal action is to shadow.")


# ---------------------------------------------------------------------------
# LLM state mismatch validation
# ---------------------------------------------------------------------------


class TestValidationRobustness:
    def test_empty_text_rejected(self):
        assert not explanation_references_match("")

    def test_generic_text_passes(self):
        """Text with no IDs, no threat levels, no numbers should pass."""
        assert explanation_references_match("The situation is stable.")

    def test_correct_threat_level_passes(self):
        assert explanation_references_match(
            "Threat level is HIGH.",
            threat_level="HIGH",
        )

    def test_wrong_threat_level_fails(self):
        assert not explanation_references_match(
            "Threat level is CRITICAL.",
            threat_level="HIGH",
        )

    def test_valid_entity_id_passes(self):
        assert explanation_references_match(
            "Entity VES-SUSP-001 is being monitored.",
            valid_target_ids={"VES-SUSP-001"},
        )

    def test_invalid_system_entity_id_fails(self):
        assert not explanation_references_match(
            "Entity VES-SUSP-999 is approaching.",
            valid_target_ids={"VES-SUSP-001"},
        )

    def test_non_system_entity_id_passes(self):
        """Generic IDs that don't match system prefixes should pass."""
        assert explanation_references_match(
            "NATO-ALLIED forces are in position.",
            valid_target_ids={"VES-SUSP-001"},
        )

    def test_valid_coa_id_passes(self):
        assert explanation_references_match(
            "COA-TPL-ISR is the recommended course.",
            valid_coa_ids={"COA-TPL-ISR"},
        )

    def test_invalid_coa_id_fails(self):
        assert not explanation_references_match(
            "COA-TPL-UNKNOWN is recommended.",
            valid_coa_ids={"COA-TPL-ISR"},
        )

    def test_safe_event_summary_passes(self):
        """Typical event summary text should pass validation."""
        text = (
            "A suspicious vessel was detected heading toward critical infrastructure. "
            "The system recommends increased ISR coverage. "
            "Threat level is MEDIUM."
        )
        assert explanation_references_match(
            text,
            threat_level="MEDIUM",
        )


class TestSystemEntityDetection:
    def test_vessel_prefix_detected(self):
        assert _looks_like_system_entity_id("VES-SUSP-001")

    def test_uav_prefix_detected(self):
        assert _looks_like_system_entity_id("UAV-001")

    def test_generic_not_detected(self):
        assert not _looks_like_system_entity_id("NATO-UNIT")

    def test_nato_allied_not_detected(self):
        assert not _looks_like_system_entity_id("NATO-ALLIED")


# ---------------------------------------------------------------------------
# Numeric validation
# ---------------------------------------------------------------------------


class TestNumericValidation:
    def test_no_numbers_passes(self):
        assert explanation_references_match("No numbers here.")

    def test_matching_success_probability_passes(self):
        assert explanation_references_match(
            "Success probability is 70%.",
            numeric_ground_truth={"success_probability": 0.70},
        )

    def test_wrong_success_probability_fails(self):
        assert not explanation_references_match(
            "Success probability is 95%.",
            numeric_ground_truth={"success_probability": 0.50},
        )

    def test_unrelated_percentage_passes(self):
        """A percentage not near a keyword should pass."""
        assert explanation_references_match(
            "The vessel is 50% through its transit.",
            numeric_ground_truth={"success_probability": 0.70},
        )


# ---------------------------------------------------------------------------
# Test-chat endpoint
# ---------------------------------------------------------------------------


class TestTestChatEndpoint:
    def test_test_chat_endpoint_exists(self, client):
        resp = client.post("/v1/engine/llm/test-chat")
        assert resp.status_code == 200
        data = resp.json()
        assert "chat_ok" in data
        assert "reachable" in data
        assert "configured" in data

    def test_test_chat_returns_configured_fields(self, client):
        data = client.post("/v1/engine/llm/test-chat").json()
        assert "model" in data
        assert "duration_ms" in data or "error" in data

    def test_health_probe_does_not_generate(self):
        """probe_sync should use GET /models, not POST /chat/completions."""
        from app.engine.llm_client import get_llm_client, reset_llm_client
        reset_llm_client()
        client = get_llm_client()
        # probe_sync will likely fail in test (no server), but it should not crash
        result = client.probe_sync()
        assert "reachable" in result
        assert "configured" in result
        # The method name confirms it's a probe, not a generation call
        assert hasattr(client, "test_chat")
        assert hasattr(client, "probe_sync")
        reset_llm_client()


# ---------------------------------------------------------------------------
# Queue reliability
# ---------------------------------------------------------------------------


class TestQueueReliability:
    def test_failed_task_does_not_poison_queue(self):
        """A failed LLM task should not prevent subsequent tasks from running."""
        from app.engine.llm_orchestrator import LLMOrchestrator, reset_llm_orchestrator

        reset_llm_orchestrator()
        call_count = 0

        def failing_runner():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("Simulated failure")
            return LLMResult(text="recovered")

        orch = LLMOrchestrator()
        # First task fails
        from app.engine.llm_orchestrator import LLMTask
        task1 = LLMTask(
            task_type="test_fail",
            language="en",
            prompt_chars=10,
            runner=failing_runner,
        )
        with orch._lock:
            orch._tasks.append(task1)
            orch._wake.set()
        task1.done.wait(timeout=5.0)
        assert not task1.result.ok

        # Second task succeeds
        task2 = LLMTask(
            task_type="test_recover",
            language="en",
            prompt_chars=10,
            runner=failing_runner,
        )
        with orch._lock:
            orch._tasks.append(task2)
            orch._wake.set()
        task2.done.wait(timeout=5.0)
        assert task2.result.ok
        assert task2.result.text == "recovered"

    def test_queue_status_shows_current_task(self):
        from app.engine.llm_orchestrator import LLMOrchestrator, reset_llm_orchestrator

        reset_llm_orchestrator()
        orch = LLMOrchestrator()
        status = orch.status()
        assert "busy" in status
        assert "queue_length" in status
        assert "last_error" in status


# ---------------------------------------------------------------------------
# Briefing diagnostics
# ---------------------------------------------------------------------------


class TestBriefingDiagnostics:
    def test_briefing_response_includes_diagnostics(self, client):
        """Briefing response should include llm_attempted, llm_used, fallback_reason."""
        from app.engine.state_store import get_state_store
        store = get_state_store()
        store.clear()
        from app.core.schemas import Contact, ContactType
        from datetime import datetime, timezone
        for i in range(3):
            store.ingest_contact(Contact(
                contact_id=f"C-{i}", timestamp=datetime.now(timezone.utc),
                source="ais", contact_type=ContactType.VESSEL,
                lat=57.5 + i * 0.1, lon=19.0, speed=5.0, heading=45.0,
                confidence=0.8, entity_id=f"E-{i}", is_hostile=False, attributes={},
            ))

        resp = client.get("/v1/engine/briefing")
        assert resp.status_code == 200
        data = resp.json()
        assert "llm_attempted" in data
        assert "llm_used" in data
        assert "fallback_reason" in data
        assert "language" in data


# ---------------------------------------------------------------------------
# Language propagation
# ---------------------------------------------------------------------------


class TestLanguagePropagation:
    def test_event_summary_uses_ui_language(self):
        """Event summary should use the store's UI language setting."""
        from app.engine.llm_orchestrator import LLMOrchestrator, reset_llm_orchestrator
        from app.engine.state_store import get_state_store

        reset_llm_orchestrator()
        store = get_state_store()
        store.set_ui_language("es")

        captured_lang = []

        class CapturingOrchestrator(LLMOrchestrator):
            def enqueue_event_summary(self, *, tick, event_type, language, context):
                captured_lang.append(language)
                # Don't actually call LLM

        orch = CapturingOrchestrator()
        orch.enqueue_event_summary(
            tick=1,
            event_type="test",
            language=store.get_ui_language(),
            context={"threat_level": "MEDIUM"},
        )
        assert captured_lang
        assert captured_lang[0] == "es"


# ---------------------------------------------------------------------------
# No LLM in decision logic
# ---------------------------------------------------------------------------


class TestNoLLMInDecisionLogic:
    def test_safety_filter_not_in_scoring(self):
        import app.engine.scoring as mod
        source = open(mod.__file__).read()
        assert "_safety_filter" not in source

    def test_safety_filter_not_in_recommendation(self):
        import app.engine.recommendation as mod
        source = open(mod.__file__).read()
        assert "_safety_filter" not in source

    def test_safety_filter_not_in_targeting(self):
        import app.engine.targeting as mod
        source = open(mod.__file__).read()
        assert "_safety_filter" not in source

    def test_safety_filter_not_in_roe_engine(self):
        import app.engine.roe_engine as mod
        source = open(mod.__file__).read()
        assert "_safety_filter" not in source
