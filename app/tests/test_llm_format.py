"""Tests for LLM format flexibility: JSON extraction, prose fallback, event summary."""
from __future__ import annotations

import pytest

from app.engine.event_loop import _extract_json


# ---------------------------------------------------------------------------
# _extract_json helper
# ---------------------------------------------------------------------------


class TestExtractJson:
    def test_plain_json_object(self):
        text = '{"situation": "stable", "assessment": "low threat"}'
        assert _extract_json(text) == text

    def test_json_in_markdown_fence(self):
        text = '```json\n{"situation": "stable"}\n```'
        result = _extract_json(text)
        assert result is not None
        assert '"situation"' in result

    def test_json_in_plain_fence(self):
        text = '```\n{"situation": "stable"}\n```'
        result = _extract_json(text)
        assert result is not None
        assert '"situation"' in result

    def test_json_with_prose_prefix(self):
        text = 'Here is the briefing:\n{"situation": "escalating"}'
        result = _extract_json(text)
        assert result is not None
        assert result.startswith("{")

    def test_json_with_trailing_prose(self):
        text = '{"situation": "stable"}\nEnd of briefing.'
        result = _extract_json(text)
        assert result is not None
        assert result.endswith("}")

    def test_pure_prose_no_json(self):
        text = "The situation is stable. No significant developments."
        assert _extract_json(text) is None

    def test_empty_string(self):
        assert _extract_json("") is None

    def test_no_braces(self):
        assert _extract_json("just text no json here") is None

    def test_nested_json(self):
        text = '{"outer": {"inner": "value"}, "list": [1, 2]}'
        result = _extract_json(text)
        assert result == text


# ---------------------------------------------------------------------------
# Briefing format diagnostics in response
# ---------------------------------------------------------------------------


class TestBriefingFormatDiagnostics:
    def test_briefing_includes_format_diagnostics(self, client):
        from app.engine.state_store import get_state_store
        store = get_state_store()
        store.clear()
        from app.core.schemas import Contact, ContactType
        from datetime import datetime, timezone
        for i in range(3):
            store.ingest_contact(Contact(
                contact_id=f"CF-{i}", timestamp=datetime.now(timezone.utc),
                source="ais", contact_type=ContactType.VESSEL,
                lat=57.5 + i * 0.1, lon=19.0, speed=5.0, heading=45.0,
                confidence=0.8, entity_id=f"EF-{i}", is_hostile=False, attributes={},
            ))
        resp = client.get("/v1/engine/briefing")
        assert resp.status_code == 200
        data = resp.json()
        # raw_format may be None if LLM not enabled, but the key must exist
        assert "raw_format" in data
        assert "duration_ms" in data


# ---------------------------------------------------------------------------
# Event summary keeps text on state mismatch
# ---------------------------------------------------------------------------


class TestEventSummaryMismatchTolerance:
    def test_event_summary_keeps_text_on_mismatch(self):
        from app.engine.llm_orchestrator import LLMOrchestrator, LLMTask, reset_llm_orchestrator
        from app.engine.llm_client import LLMResult

        reset_llm_orchestrator()
        orch = LLMOrchestrator()

        # Simulate a runner that returns text referencing a wrong entity
        def runner():
            return LLMResult(text="VES-SUSP-999 is the main threat. Threat level is CRITICAL.")

        task = LLMTask(
            task_type="event_summary",
            language="en",
            prompt_chars=50,
            runner=runner,
        )
        with orch._lock:
            orch._tasks.append(task)
            orch._wake.set()
        task.done.wait(timeout=5.0)
        # Even with mismatch, the text should be kept (not discarded)
        assert task.result.ok
        assert task.result.text  # text is present
        assert "VES-SUSP-999" in task.result.text
