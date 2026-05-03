from __future__ import annotations

from typing import Any

import httpx


class COAApiClient:
    """Synchronous HTTP client wrapping the COA Engine REST API."""

    def __init__(self, base_url: str = "http://localhost:8002") -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=30.0)

    # ---- Health ----

    def health(self) -> dict:
        return self._client.get("/health").json()

    # ---- Scenarios ----

    def list_scenarios(self) -> list[dict]:
        resp = self._client.get("/v1/scenario/list")
        return resp.json().get("scenarios", [])

    def load_scenario(self, scenario_id: str) -> dict:
        resp = self._client.post(f"/v1/scenario/load/{scenario_id}")
        resp.raise_for_status()
        return resp.json()

    def get_sample_scenario(self) -> dict:
        return self._client.get("/v1/scenario/sample").json()

    def session_status(self) -> dict:
        return self._client.get("/v1/scenario/session/status").json()

    # ---- Events ----

    def list_events(self) -> dict:
        return self._client.get("/v1/events/list").json()

    def ingest_events(self, events: list[dict]) -> dict:
        resp = self._client.post("/v1/events/ingest", json={"events": events})
        resp.raise_for_status()
        return resp.json()

    # ---- Analysis pipeline (legacy per-step) ----

    def run_analysis(self, payload: dict | None = None) -> dict:
        resp = self._client.post("/v1/analysis/run", json=payload or {})
        resp.raise_for_status()
        return resp.json()

    def generate_coas(self, payload: dict | None = None) -> dict:
        resp = self._client.post("/v1/coa/generate", json=payload or {})
        resp.raise_for_status()
        return resp.json()

    def run_simulation(self, payload: dict | None = None) -> dict:
        resp = self._client.post("/v1/coa/simulation/run", json=payload or {})
        resp.raise_for_status()
        return resp.json()

    def run_recommendation(self, payload: dict | None = None) -> dict:
        resp = self._client.post("/v1/coa/recommendation/run", json=payload or {})
        resp.raise_for_status()
        return resp.json()

    def generate_briefing(self, payload: dict | None = None) -> dict:
        resp = self._client.post("/v1/coa/briefing/generate", json=payload or {})
        resp.raise_for_status()
        return resp.json()

    def export_briefing_json(self, payload: dict | None = None) -> bytes:
        resp = self._client.post("/v1/coa/briefing/export/json", json=payload or {})
        resp.raise_for_status()
        return resp.content

    def export_briefing_pdf(self, payload: dict | None = None) -> bytes:
        resp = self._client.post("/v1/coa/briefing/export/pdf", json=payload or {})
        resp.raise_for_status()
        return resp.content

    # ---- Engine state queries ----

    def get_engine_state(self) -> dict:
        return self._client.get("/v1/engine/state").json()

    def list_engine_assets(self) -> dict:
        return self._client.get("/v1/engine/assets").json()

    def list_engine_contacts(self) -> dict:
        return self._client.get("/v1/engine/contacts").json()

    def get_contact_history(self, limit: int = 100) -> dict:
        return self._client.get(f"/v1/engine/contacts/history?limit={limit}").json()

    def list_tracks(self) -> dict:
        return self._client.get("/v1/engine/tracks").json()

    def list_engine_threats(self) -> dict:
        return self._client.get("/v1/engine/threats").json()

    def list_engine_coas(self) -> dict:
        return self._client.get("/v1/engine/coas").json()

    def get_engine_recommendation(self) -> dict:
        return self._client.get("/v1/engine/recommendation").json()

    def get_full_analysis(self) -> dict:
        return self._client.get("/v1/engine/analysis").json()

    def get_engine_briefing(self) -> dict:
        return self._client.get("/v1/engine/briefing").json()

    def get_visible_ais(
        self,
        latmin: float,
        latmax: float,
        lonmin: float,
        lonmax: float,
        include_in_analysis: bool = True,
    ) -> dict:
        params = (
            f"latmin={latmin}&latmax={latmax}"
            f"&lonmin={lonmin}&lonmax={lonmax}"
            f"&include_in_analysis={include_in_analysis}"
        )
        return self._client.get(f"/v1/engine/ais/visible?{params}").json()

    # ---- Engine control ----

    def set_engine_mode(self, mode: str) -> dict:
        resp = self._client.post(f"/v1/engine/mode/{mode}")
        resp.raise_for_status()
        return resp.json()

    def load_engine_scenario(self, scenario_id: str) -> dict:
        resp = self._client.post(f"/v1/engine/scenario/{scenario_id}")
        resp.raise_for_status()
        return resp.json()

    def set_assets(self, assets: list[dict[str, Any]]) -> dict:
        resp = self._client.post("/v1/engine/assets", json=assets)
        resp.raise_for_status()
        return resp.json()

    def set_asset_inventory(self, inventory: dict[str, int]) -> dict:
        resp = self._client.post("/v1/coa/generate", json={"asset_inventory": inventory})
        resp.raise_for_status()
        return resp.json()

    def run_tick(self) -> dict:
        resp = self._client.post("/v1/engine/tick")
        resp.raise_for_status()
        return resp.json()

    def inject_contacts(self, contacts: list[dict]) -> dict:
        resp = self._client.post("/v1/engine/inject", json={"contacts": contacts})
        resp.raise_for_status()
        return resp.json()

    def delete_contact(self, entity_id: str) -> dict:
        resp = self._client.delete(f"/v1/engine/inject/{entity_id}")
        resp.raise_for_status()
        return resp.json()

    def update_contact(self, entity_id: str, updates: dict) -> dict:
        resp = self._client.patch(f"/v1/engine/contacts/{entity_id}", json=updates)
        resp.raise_for_status()
        return resp.json()

    def schedule_action(self, action: dict) -> dict:
        resp = self._client.post("/v1/engine/actions", json=action)
        resp.raise_for_status()
        return resp.json()

    def reset_engine(self) -> dict:
        resp = self._client.post("/v1/engine/reset")
        resp.raise_for_status()
        return resp.json()

    def start_engine(
        self,
        scenario_id: str = "baltic_hybrid_001",
        mode: str = "simulation",
        interval: float = 2.0,
    ) -> dict:
        resp = self._client.post(
            "/v1/engine/start",
            params={"scenario_id": scenario_id, "mode": mode, "interval": interval},
        )
        resp.raise_for_status()
        return resp.json()

    def stop_engine(self) -> dict:
        resp = self._client.post("/v1/engine/stop")
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        self._client.close()
