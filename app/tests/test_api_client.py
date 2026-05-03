"""Tests for COAApiClient — verify all methods hit the correct endpoints."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.core.api_client import COAApiClient


def _make_client() -> tuple[COAApiClient, MagicMock]:
    client = COAApiClient("http://testhost:9999")
    mock_http = MagicMock()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "ok"}
    mock_resp.content = b'{"status":"ok"}'
    mock_resp.raise_for_status.return_value = None
    mock_http.get.return_value = mock_resp
    mock_http.post.return_value = mock_resp
    mock_http.delete.return_value = mock_resp
    mock_http.patch.return_value = mock_resp
    client._client = mock_http
    return client, mock_http


class TestEngineStateQueries:
    def test_get_engine_state(self):
        c, m = _make_client()
        c.get_engine_state()
        m.get.assert_called_once_with("/v1/engine/state")

    def test_list_engine_assets(self):
        c, m = _make_client()
        c.list_engine_assets()
        m.get.assert_called_once_with("/v1/engine/assets")

    def test_list_engine_contacts(self):
        c, m = _make_client()
        c.list_engine_contacts()
        m.get.assert_called_once_with("/v1/engine/contacts")

    def test_get_contact_history(self):
        c, m = _make_client()
        c.get_contact_history(limit=50)
        m.get.assert_called_once_with("/v1/engine/contacts/history?limit=50")

    def test_list_tracks(self):
        c, m = _make_client()
        c.list_tracks()
        m.get.assert_called_once_with("/v1/engine/tracks")

    def test_list_engine_threats(self):
        c, m = _make_client()
        c.list_engine_threats()
        m.get.assert_called_once_with("/v1/engine/threats")

    def test_list_engine_coas(self):
        c, m = _make_client()
        c.list_engine_coas()
        m.get.assert_called_once_with("/v1/engine/coas")

    def test_get_engine_recommendation(self):
        c, m = _make_client()
        c.get_engine_recommendation()
        m.get.assert_called_once_with("/v1/engine/recommendation")

    def test_get_full_analysis(self):
        c, m = _make_client()
        c.get_full_analysis()
        m.get.assert_called_once_with("/v1/engine/analysis")

    def test_get_engine_briefing(self):
        c, m = _make_client()
        c.get_engine_briefing()
        m.get.assert_called_once_with("/v1/engine/briefing")

    def test_get_visible_ais(self):
        c, m = _make_client()
        c.get_visible_ais(55.0, 60.0, 18.0, 22.0)
        called_url = m.get.call_args[0][0]
        assert "/v1/engine/ais/visible?" in called_url
        assert "latmin=55.0" in called_url
        assert "lonmax=22.0" in called_url


class TestEngineControl:
    def test_set_engine_mode(self):
        c, m = _make_client()
        c.set_engine_mode("simulation")
        m.post.assert_called_once_with("/v1/engine/mode/simulation")

    def test_load_engine_scenario(self):
        c, m = _make_client()
        c.load_engine_scenario("arctic_submarine_001")
        m.post.assert_called_once_with("/v1/engine/scenario/arctic_submarine_001")

    def test_set_assets_posts_to_engine_assets(self):
        c, m = _make_client()
        c.set_assets([{"asset_id": "uav_1", "asset_type": "uav", "quantity_total": 2, "quantity_available": 1}])
        m.post.assert_called_once()
        call_args = m.post.call_args
        assert call_args[0][0] == "/v1/engine/assets"

    def test_set_asset_inventory_posts_to_coa_generate(self):
        c, m = _make_client()
        c.set_asset_inventory({"isr_uav": 2})
        m.post.assert_called_once()
        call_args = m.post.call_args
        assert call_args[0][0] == "/v1/coa/generate"
        assert call_args[1]["json"]["asset_inventory"] == {"isr_uav": 2}

    def test_run_tick(self):
        c, m = _make_client()
        c.run_tick()
        m.post.assert_called_once_with("/v1/engine/tick")

    def test_inject_contacts(self):
        c, m = _make_client()
        c.inject_contacts([{"entity_id": "E1", "contact_type": "vessel"}])
        m.post.assert_called_once()
        call_args = m.post.call_args
        assert call_args[0][0] == "/v1/engine/inject"
        assert "contacts" in call_args[1]["json"]

    def test_delete_contact(self):
        c, m = _make_client()
        c.delete_contact("E1")
        m.delete.assert_called_once_with("/v1/engine/inject/E1")

    def test_update_contact(self):
        c, m = _make_client()
        c.update_contact("E1", {"speed": 10.0})
        m.patch.assert_called_once()
        call_args = m.patch.call_args
        assert call_args[0][0] == "/v1/engine/contacts/E1"
        assert call_args[1]["json"]["speed"] == 10.0

    def test_schedule_action(self):
        c, m = _make_client()
        c.schedule_action({"action": "change_heading", "entity_id": "E1", "new_heading": 180})
        m.post.assert_called_once()
        call_args = m.post.call_args
        assert call_args[0][0] == "/v1/engine/actions"

    def test_reset_engine(self):
        c, m = _make_client()
        c.reset_engine()
        m.post.assert_called_once_with("/v1/engine/reset")

    def test_start_engine(self):
        c, m = _make_client()
        c.start_engine("arctic_submarine_001", "simulation", 3.0)
        m.post.assert_called_once()
        call_args = m.post.call_args
        assert call_args[0][0] == "/v1/engine/start"
        assert call_args[1]["params"]["scenario_id"] == "arctic_submarine_001"

    def test_stop_engine(self):
        c, m = _make_client()
        c.stop_engine()
        m.post.assert_called_once_with("/v1/engine/stop")


class TestLegacyPipelineMethods:
    def test_health(self):
        c, m = _make_client()
        c.health()
        m.get.assert_called_once_with("/health")

    def test_list_scenarios(self):
        c, m = _make_client()
        c.list_scenarios()
        m.get.assert_called_once_with("/v1/scenario/list")

    def test_load_scenario(self):
        c, m = _make_client()
        c.load_scenario("baltic_hybrid_001")
        m.post.assert_called_once_with("/v1/scenario/load/baltic_hybrid_001")

    def test_run_analysis(self):
        c, m = _make_client()
        c.run_analysis()
        m.post.assert_called_once_with("/v1/analysis/run", json={})

    def test_generate_coas(self):
        c, m = _make_client()
        c.generate_coas()
        m.post.assert_called_once_with("/v1/coa/generate", json={})

    def test_run_simulation(self):
        c, m = _make_client()
        c.run_simulation()
        m.post.assert_called_once_with("/v1/coa/simulation/run", json={})

    def test_run_recommendation(self):
        c, m = _make_client()
        c.run_recommendation()
        m.post.assert_called_once_with("/v1/coa/recommendation/run", json={})

    def test_generate_briefing(self):
        c, m = _make_client()
        c.generate_briefing()
        m.post.assert_called_once_with("/v1/coa/briefing/generate", json={})

    def test_export_briefing_json(self):
        c, m = _make_client()
        c.export_briefing_json()
        m.post.assert_called_once_with("/v1/coa/briefing/export/json", json={})

    def test_export_briefing_pdf(self):
        c, m = _make_client()
        c.export_briefing_pdf()
        m.post.assert_called_once_with("/v1/coa/briefing/export/pdf", json={})
