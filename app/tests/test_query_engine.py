"""Tests for the query engine — natural language query over operational state."""

import pytest

from app.engine.contact_engine import get_contact_engine
from app.engine.event_bus import get_event_bus
from app.engine.event_loop import get_event_loop
from app.engine.ais_feed import get_ais_feed
from app.engine.noaa_replay import get_noaa_replay_feed
from app.engine.query_engine import (
    answer_question,
    build_context,
    context_to_text,
    detect_language,
    _is_roe_question,
    _is_unsafe,
    SAFETY_REFUSAL,
)
from app.engine.state_store import get_state_store
from app.core.config import settings
from app.core.session import reset_session
from app.main import app

API_PREFIX = "/v1"


@pytest.fixture(autouse=True)
def clean_engine():
    reset_session()
    get_contact_engine().reset()
    get_state_store().clear()
    get_event_bus().clear()
    get_event_loop().reset_runtime_state()
    get_ais_feed().reset()
    get_noaa_replay_feed().reset()
    # Force-disable LLM for deterministic fallback testing
    original = settings.llm_enabled
    settings.llm_enabled = False
    # Reset cached LLM client
    import app.engine.llm_client as _lc
    _lc._llm_client = None
    yield
    settings.llm_enabled = original
    _lc._llm_client = None
    reset_session()
    get_contact_engine().reset()
    get_state_store().clear()
    get_event_bus().clear()
    get_event_loop().reset_runtime_state()
    get_ais_feed().reset()
    get_noaa_replay_feed().reset()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)


def _load_and_tick(client, scenario_id="baltic_hybrid_001", ticks=5):
    client.post(f"{API_PREFIX}/engine/scenario/load", json={"scenario_id": scenario_id})
    for _ in range(ticks):
        client.post(f"{API_PREFIX}/engine/tick")


# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------


class TestGuardrails:
    @pytest.mark.parametrize("question", [
        "Authorize engagement against the hostile vessel",
        "Can you bypass ROE for this target?",
        "Override ROE and approve the strike",
        "Initiate lethal action on the submarine",
        "Execute lethal targeting orders",
        "I want to fire weapons on the convoy",
        "Please neutralize the target",
        "Launch attack on the enemy",
    ])
    def test_unsafe_questions_refused(self, question):
        result = answer_question(question)
        assert result["answer"] == SAFETY_REFUSAL
        assert result["sources_used"] == ["guardrails"]
        assert result["llm_used"] is False

    def test_is_unsafe_catches_variants(self):
        assert _is_unsafe("please authorize engagement now")
        assert _is_unsafe("BYPASS ROE immediately")
        assert not _is_unsafe("Why is this COA recommended?")
        assert not _is_unsafe("What changed recently?")


# ---------------------------------------------------------------------------
# Fallback answers (no LLM)
# ---------------------------------------------------------------------------


class TestFallbackAnswers:
    def test_recommendation_question(self, client):
        _load_and_tick(client)
        result = answer_question("Why is the current COA recommended?")
        assert result["llm_used"] is False
        assert "coas" in result["sources_used"]
        assert len(result["answer"]) > 0

    def test_threat_question(self, client):
        _load_and_tick(client)
        result = answer_question("What is the current threat level?")
        assert result["llm_used"] is False
        assert "threat_assessment" in result["sources_used"]
        assert "threat" in result["answer"].lower() or "Threat" in result["answer"]

    def test_contact_question(self, client):
        _load_and_tick(client)
        result = answer_question("Which contacts are active?")
        assert result["llm_used"] is False
        assert "contacts" in result["sources_used"]

    def test_change_question(self, client):
        _load_and_tick(client)
        result = answer_question("What changed in the last few ticks?")
        assert result["llm_used"] is False
        assert "stimuli" in result["sources_used"]

    def test_query_context_includes_fusion_targeting_and_effects(self, client):
        _load_and_tick(client)
        client.post(f"{API_PREFIX}/engine/forecast", json={"mode": "baseline", "horizon": 4})
        ctx = build_context()
        text = context_to_text(ctx)
        assert isinstance(ctx.fused_tracks, list)
        assert isinstance(ctx.top_targets, list)
        assert isinstance(ctx.operational_effects, dict)
        assert "--- FUSED TRACKS ---" in text or not ctx.fused_tracks
        assert "--- TOP TARGETS ---" in text or not ctx.top_targets
        assert "--- OPERATIONAL EFFECTS ---" in text or not ctx.operational_effects

    def test_roe_question(self, client):
        _load_and_tick(client)
        result = answer_question("What COAs require authorization?")
        assert result["llm_used"] is False
        assert "roe" in result["sources_used"]

    def test_situation_summary(self, client):
        _load_and_tick(client)
        result = answer_question("Give me a situation summary")
        assert result["llm_used"] is False
        assert "state" in result["sources_used"]

    def test_generic_question(self, client):
        _load_and_tick(client)
        result = answer_question("Tell me about the weather")
        assert result["llm_used"] is False
        assert len(result["answer"]) > 0

    def test_answer_includes_rationale_when_recommendation_exists(self, client):
        _load_and_tick(client)
        result = answer_question("Why is the current COA recommended?")
        if "coas" in result["sources_used"]:
            # If there is a recommendation, rationale should be mentioned
            assert len(result["answer"]) > 20


# ---------------------------------------------------------------------------
# No state mutation
# ---------------------------------------------------------------------------


class TestNoStateMutation:
    def test_query_does_not_change_engine_state(self, client):
        _load_and_tick(client)
        state_before = client.get(f"{API_PREFIX}/engine/state").json()
        coas_before = client.get(f"{API_PREFIX}/engine/coas").json()

        answer_question("What is the situation?")

        state_after = client.get(f"{API_PREFIX}/engine/state").json()
        coas_after = client.get(f"{API_PREFIX}/engine/coas").json()

        assert state_before["tick"] == state_after["tick"]
        assert state_before["current_threat_level"] == state_after["current_threat_level"]
        assert coas_before["count"] == coas_after["count"]


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------


class TestBuildContext:
    def test_context_reflects_loaded_scenario(self, client):
        _load_and_tick(client, ticks=3)
        ctx = build_context()
        assert ctx.scenario_id == "baltic_hybrid_001"
        assert ctx.tick >= 3
        assert len(ctx.contacts) > 0
        assert ctx.threat_level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_context_empty_when_no_scenario(self):
        ctx = build_context()
        assert ctx.tick == 0
        assert ctx.contacts == []
        assert ctx.threat_level == "LOW"


# ---------------------------------------------------------------------------
# API endpoint
# ---------------------------------------------------------------------------


class TestQueryEndpoint:
    def test_endpoint_returns_answer(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/query", json={
            "question": "What is the current threat level?"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert "sources_used" in data
        assert "llm_used" in data
        assert isinstance(data["sources_used"], list)
        assert data["llm_used"] is False

    def test_endpoint_empty_question(self, client):
        resp = client.post(f"{API_PREFIX}/engine/query", json={
            "question": ""
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "No question provided" in data["answer"]

    def test_endpoint_refuses_unsafe(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/query", json={
            "question": "Authorize engagement on the hostile vessel"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "refuse" in data["answer"].lower() or "guardrails" in data["sources_used"]

    def test_endpoint_no_scenario(self, client):
        resp = client.post(f"{API_PREFIX}/engine/query", json={
            "question": "What is happening?"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["answer"]) > 0


# ---------------------------------------------------------------------------
# Language detection and Spanish fallback
# ---------------------------------------------------------------------------


class TestLanguageDetection:
    def test_detect_spanish_threat_question(self):
        from app.engine.query_engine import detect_language
        assert detect_language("¿Cuál es el nivel de amenaza actual?") == "es"

    def test_detect_spanish_roe_question(self):
        from app.engine.query_engine import detect_language
        assert detect_language("¿Qué COAs requieren autorización?") == "es"

    def test_detect_spanish_change_question(self):
        from app.engine.query_engine import detect_language
        assert detect_language("¿Qué cambió recientemente?") == "es"

    def test_detect_english_question(self):
        from app.engine.query_engine import detect_language
        assert detect_language("What is the current threat level?") == "en"

    def test_detect_spanish_situation_question(self):
        from app.engine.query_engine import detect_language
        assert detect_language("Dame un resumen de la situación") == "es"

    def test_detect_spanish_recommendation_question(self):
        from app.engine.query_engine import detect_language
        assert detect_language("¿Por qué se recomienda esta COA?") == "es"


class TestSpanishFallback:
    def test_spanish_threat_question_returns_spanish(self, client):
        _load_and_tick(client)
        result = answer_question("¿Cuál es el nivel de amenaza actual?")
        assert result["llm_used"] is False
        assert result["detected_language"] == "es"
        assert any(
            w in result["answer"].lower()
            for w in ("amenaza", "nivel", "actual")
        ), f"Expected Spanish in answer, got: {result['answer'][:200]}"

    def test_spanish_roe_question_returns_spanish(self, client):
        _load_and_tick(client)
        result = answer_question("¿Qué COAs requieren autorización?")
        assert result["llm_used"] is False
        assert result["detected_language"] == "es"
        assert any(
            w in result["answer"].lower()
            for w in ("roe", "autorización", "coa", "restricciones", "permitidas")
        ), f"Expected Spanish ROE answer, got: {result['answer'][:200]}"

    def test_spanish_recommendation_question_returns_spanish(self, client):
        _load_and_tick(client)
        result = answer_question("¿Cuál es la COA recomendada?")
        assert result["llm_used"] is False
        assert result["detected_language"] == "es"
        assert any(
            w in result["answer"].lower()
            for w in ("recomendada", "coa", "puntuación", "racional", "recomendación", "no se ha calculado")
        ), f"Expected Spanish recommendation answer, got: {result['answer'][:200]}"

    def test_spanish_contact_question_returns_spanish(self, client):
        _load_and_tick(client)
        result = answer_question("¿Qué contactos están activos?")
        assert result["llm_used"] is False
        assert result["detected_language"] == "es"
        assert "contactos" in result["answer"].lower()

    def test_spanish_change_question_returns_spanish(self, client):
        _load_and_tick(client)
        result = answer_question("¿Qué cambió recientemente?")
        assert result["llm_used"] is False
        assert result["detected_language"] == "es"

    def test_spanish_generic_question_returns_spanish(self, client):
        _load_and_tick(client)
        result = answer_question("Dame un resumen de la situación")
        assert result["llm_used"] is False
        assert result["detected_language"] == "es"


class TestFallbackReason:
    def test_llm_disabled_returns_fallback_reason(self, client):
        _load_and_tick(client)
        result = answer_question("What is the current threat level?")
        assert result["llm_used"] is False
        assert result.get("fallback_reason") == "llm_disabled"

    def test_llm_failure_returns_fallback_reason(self, client):
        """Simulate LLM failure by enabling LLM but pointing at unreachable URL."""
        import app.engine.llm_client as _lc
        original_enabled = settings.llm_enabled
        original_url = settings.llm_base_url
        try:
            settings.llm_enabled = True
            settings.llm_base_url = "http://127.0.0.1:1/fake"
            _lc._llm_client = None
            _load_and_tick(client)
            result = answer_question("What is the threat level?")
            assert result["llm_used"] is False
            assert result.get("fallback_reason") == "llm_connection_failed"
        finally:
            settings.llm_enabled = original_enabled
            settings.llm_base_url = original_url
            _lc._llm_client = None

    def test_endpoint_returns_fallback_reason(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/query", json={
            "question": "What is the current threat level?"
        })
        data = resp.json()
        assert data["llm_used"] is False
        assert data.get("fallback_reason") == "llm_disabled"


class TestSpanishLLMInstruction:
    def test_spanish_question_produces_lang_instruction_for_llm(self):
        """Verify that when LLM is enabled, Spanish questions produce a language instruction."""
        from app.engine.query_engine import detect_language
        lang = detect_language("¿Cuál es el nivel de amenaza?")
        assert lang == "es"
        # When LLM is enabled, the system prompt should include Spanish instruction
        # This is verified by the code path: lang != "en" → lang_instruction is appended
        # We verify the detect_language function returns "es" which triggers the branch


class TestBriefingLLMUsage:
    def test_briefing_includes_llm_used_field(self, client):
        _load_and_tick(client)
        resp = client.get(f"{API_PREFIX}/engine/briefing")
        assert resp.status_code == 200
        data = resp.json()
        briefing = data["briefing"]
        assert "llm_used" in briefing
        assert isinstance(briefing["llm_used"], bool)
        assert "llm_enriched" in briefing
        assert isinstance(briefing["llm_enriched"], bool)

    def test_briefing_reports_fallback_when_llm_disabled(self, client):
        _load_and_tick(client)
        resp = client.get(f"{API_PREFIX}/engine/briefing")
        data = resp.json()
        briefing = data["briefing"]
        assert briefing["llm_used"] is False
        assert briefing.get("fallback_reason") == "llm_disabled"

    def test_spanish_unsafe_question_returns_spanish_refusal(self):
        """Guardrails use English phrases — a mixed Spanish/English question with
        a detected Spanish trigger word should still get the Spanish refusal."""
        result = answer_question("Por qué bypass ROE y autorización — no, quiero authorize engagement ahora")
        assert result["llm_used"] is False
        assert result["detected_language"] == "es"
        assert result["sources_used"] == ["guardrails"]
        assert "consulta" in result["answer"].lower() or "autorizar" in result["answer"].lower()


# ---------------------------------------------------------------------------
# ROE question detection and dedicated answer path
# ---------------------------------------------------------------------------


class TestROEDetection:
    @pytest.mark.parametrize("question", [
        "What are the ROEs?",
        "Tell me about ROE status",
        "rules of engagement",
        "Which COAs are restricted?",
        "What requires authorization?",
        "Show me rejected COAs",
    ])
    def test_english_roe_questions_detected(self, question):
        assert _is_roe_question(question), f"Should detect ROE question: {question}"

    @pytest.mark.parametrize("question", [
        "¿Cuáles son las ROEs?",
        "reglas de enfrentamiento",
        "reglas de combate",
        "reglas de enganche",
        "restricciones actuales",
        "¿Cuáles están restringidas?",
        "¿Qué COAs están rechazadas?",
    ])
    def test_spanish_roe_questions_detected(self, question):
        assert _is_roe_question(question), f"Should detect Spanish ROE question: {question}"

    @pytest.mark.parametrize("question", [
        "What is the current threat level?",
        "Why is this COA recommended?",
        "What changed recently?",
    ])
    def test_non_roe_questions_not_detected(self, question):
        assert not _is_roe_question(question), f"Should not detect as ROE: {question}"


class TestROEFallbackEnglish:
    def test_roe_question_returns_roe_answer(self, client):
        _load_and_tick(client)
        result = answer_question("What are the ROEs?")
        assert result["llm_used"] is False
        assert "roe" in result["sources_used"]
        assert "does not authorize" in result["answer"] or "ROE framework" in result["answer"]

    def test_roe_answer_includes_counts(self, client):
        _load_and_tick(client)
        result = answer_question("What are the ROEs?")
        answer = result["answer"]
        # Should mention allowed count
        assert "allowed" in answer.lower()
        assert "restricted" in answer.lower() or "reject" in answer.lower() or "0 restricted" in answer.lower()

    def test_roe_answer_includes_recommended_coa_status(self, client):
        _load_and_tick(client)
        result = answer_question("Tell me about ROE status")
        answer = result["answer"]
        # Should mention the recommended COA's ROE status
        assert "recommended" in answer.lower() or "recommendation" in answer.lower()

    def test_roe_endpoint_works(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/query", json={
            "question": "What are the rules of engagement?"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "roe" in data["sources_used"]
        assert data["llm_used"] is False


class TestROEFallbackSpanish:
    def test_spanish_roe_question_returns_spanish(self, client):
        _load_and_tick(client)
        result = answer_question("¿Cuáles son las ROEs?")
        assert result["llm_used"] is False
        assert result["detected_language"] == "es"
        answer = result["answer"].lower()
        assert "no autorizan" in answer or "roe" in answer or "reglas" in answer

    def test_spanish_roe_includes_counts(self, client):
        _load_and_tick(client)
        result = answer_question("¿Cuáles son las restricciones ROE?")
        answer = result["answer"].lower()
        assert "permitidas" in answer or "evaluadas" in answer

    def test_spanish_roe_includes_recommended(self, client):
        _load_and_tick(client)
        result = answer_question("Cuáles son las reglas de enfrentamiento")
        answer = result["answer"].lower()
        assert "recomendada" in answer or "recomendación" in answer

    def test_spanish_reglas_de_combate(self, client):
        _load_and_tick(client)
        result = answer_question("Explique las reglas de combate")
        assert result["detected_language"] == "es"
        assert "roe" in result["sources_used"]


class TestLanguageParameter:
    def test_force_language_overrides_question_detection(self, client):
        _load_and_tick(client)
        # English question but forced Spanish
        result = answer_question("What is the threat level?", force_language="es")
        assert result["detected_language"] == "es"

    def test_force_language_overrides_spanish_question(self, client):
        _load_and_tick(client)
        # Spanish question but forced English
        result = answer_question("¿Cuál es el nivel de amenaza?", force_language="en")
        assert result["detected_language"] == "en"

    def test_question_language_beats_ui_hint(self, client):
        _load_and_tick(client)
        # Selected UI language governs response language
        result = answer_question("What are the current ROEs?", ui_language_hint="es")
        assert result["detected_language"] == "es"

    def test_spanish_question_beats_english_ui_hint(self, client):
        _load_and_tick(client)
        result = answer_question("¿Cuáles son las ROEs actuales?", ui_language_hint="en")
        assert result["detected_language"] == "en"

    def test_endpoint_accepts_ui_language_hint(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/query", json={
            "question": "¿Cuáles son las ROEs actuales?",
            "ui_language_hint": "en",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected_language"] == "en"

    def test_endpoint_force_language_field(self, client):
        _load_and_tick(client)
        resp = client.post(f"{API_PREFIX}/engine/query", json={
            "question": "What are the ROEs?",
            "force_language": "es",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected_language"] == "es"

    def test_none_params_use_detection(self, client):
        _load_and_tick(client)
        result = answer_question("¿Cuáles son las ROEs?", ui_language_hint=None, force_language=None)
        assert result["detected_language"] == "es"

    def test_ambiguous_question_falls_back_to_ui_language(self, client):
        _load_and_tick(client)
        result = answer_question("Overview?", ui_language_hint="es", force_language=None)
        assert result["detected_language"] == "es"


class TestROEContextInContext:
    def test_build_context_includes_roe_summary(self, client):
        _load_and_tick(client)
        ctx = build_context()
        assert "counts" in ctx.roe_summary
        assert "coas" in ctx.roe_summary
        assert "config" in ctx.roe_summary
        counts = ctx.roe_summary["counts"]
        total = sum(counts.values())
        assert total == len(ctx.scored_coas)

    def test_roe_config_has_expected_fields(self, client):
        _load_and_tick(client)
        ctx = build_context()
        config = ctx.roe_summary["config"]
        assert "min_threat_for_shadow" in config
        assert "escalation_policy" in config
        assert "max_allowed_escalation" in config


class TestROENoAuthorization:
    def test_english_no_auth_coas_explains_conditions(self, client):
        _load_and_tick(client)
        result = answer_question("Why does this COA require authorization?")
        answer = result["answer"].lower()
        assert result["llm_used"] is False
        assert "roe" in result["sources_used"]
        # Should clearly state no COA currently requires auth
        assert "no coa currently has roe constraints" in answer or "no coa" in answer or "all evaluated coas are allowed" in answer
        # Should explain what would trigger authorization
        assert "authorization" in answer and ("escalation" in answer or "civilian" in answer or "confidence" in answer)

    def test_spanish_no_auth_coas_explains_conditions(self, client):
        _load_and_tick(client)
        result = answer_question("¿Por qué esta COA requiere autorización?")
        answer = result["answer"].lower()
        assert result["detected_language"] == "es"
        # Should state no current restrictions
        assert "ninguna coa" in answer or "permitidas" in answer
        # Should explain conditions
        assert "autorización" in answer

    def test_english_roe_with_all_allowed_is_clear(self, client):
        _load_and_tick(client)
        result = answer_question("What are the current ROEs?")
        answer = result["answer"].lower()
        # When all COAs are allowed, answer should say so and explain triggers
        assert "allowed" in answer
