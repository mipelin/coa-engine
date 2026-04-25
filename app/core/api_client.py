from __future__ import annotations

from typing import Any

import httpx


class COAApiClient:
    """Synchronous HTTP client wrapping the COA Engine REST API."""

    def __init__(self, base_url: str = "http://localhost:8002") -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def health(self) -> dict:
        return self._client.get("/health").json()

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

    def list_events(self) -> dict:
        return self._client.get("/v1/events/list").json()

    def ingest_events(self, events: list[dict]) -> dict:
        resp = self._client.post("/v1/events/ingest", json={"events": events})
        resp.raise_for_status()
        return resp.json()

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

    def set_assets(self, inventory: dict[str, int]) -> dict:
        resp = self._client.post("/v1/coa/generate", json={"asset_inventory": inventory})
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

    def close(self) -> None:
        self._client.close()
