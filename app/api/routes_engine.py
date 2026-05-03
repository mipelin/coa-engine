from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect

from ..core.config import settings
from ..core.schemas import (
    AssetState,
    Briefing,
    CombatContactInjectRequest,
    CombatContactToggleRequest,
    ContactBatch,
    ContactUpdateRequest,
    EngineActionRequest,
)
from ..engine.contact_engine import EngineMode, get_contact_engine
from ..engine.ais_feed import get_ais_feed
from ..engine.engine_scheduler import get_engine_scheduler
from ..engine.event_loop import get_event_loop
from ..engine.geo_validation import validate_placement
from ..engine.noaa_replay import get_noaa_replay_feed
from ..engine.query_engine import answer_question
from ..engine.scenario_generator import ScenarioGenerator
from ..engine.state_store import get_state_store
from ..engine.llm_client import get_llm_client
from ..engine.llm_orchestrator import get_llm_orchestrator

router = APIRouter(prefix="/engine", tags=["engine"])


@router.get("/llm/health")
async def llm_health():
    """Test LLM connectivity with a tiny prompt. Never exposes the API key."""
    return get_llm_orchestrator().run_health_check()


@router.get("/llm/status")
async def llm_status():
    orchestrator = get_llm_orchestrator()
    store = get_state_store()
    status = orchestrator.status()
    return {
        "busy": status["busy"],
        "queue_length": status["queue_length"],
        "current_task_type": status["current_task_type"],
        "last_summary": (
            store.get_latest_event_summary().model_dump(mode="json")
            if store.get_latest_event_summary() else None
        ),
        "last_error": status["last_error"],
    }


@router.post("/ui-language")
async def set_ui_language(payload: dict):
    language = payload.get("language", "en")
    store = get_state_store()
    store.set_ui_language(language)
    return {"status": "ok", "language": store.get_ui_language()}


@router.get("/event-summary/latest")
async def latest_event_summary():
    store = get_state_store()
    summary = store.get_latest_event_summary()
    return {
        "summary": summary.model_dump(mode="json") if summary else None,
    }


def _roe_summary(scored: list) -> dict:
    """Build ROE status counts and recommended COA ROE details."""
    counts = {"allowed": 0, "restricted": 0, "requires_authorization": 0, "rejected": 0}
    for s in scored:
        status = s.coa.roe_status
        if status in counts:
            counts[status] += 1
    rec_coa = next((s for s in scored if s.rank == 1), None)
    recommended_roe = None
    if rec_coa:
        recommended_roe = {
            "coa_id": rec_coa.coa.coa_id,
            "title": rec_coa.coa.title,
            "roe_status": rec_coa.coa.roe_status,
            "roe_reason": rec_coa.coa.roe_reason,
            "roe_constraints_triggered": rec_coa.coa.roe_constraints_triggered,
        }
    return {"counts": counts, "recommended": recommended_roe}


# ---- State queries ----


@router.get("/state")
async def engine_state():
    store = get_state_store()
    payload = store.state.model_dump(mode="json")
    payload["latest_event_summary"] = (
        store.get_latest_event_summary().model_dump(mode="json")
        if store.get_latest_event_summary() else None
    )
    return payload


@router.get("/assets")
async def list_assets():
    store = get_state_store()
    assets = store.get_asset_states()
    return {"count": len(assets), "assets": [asset.model_dump(mode="json") for asset in assets]}


@router.get("/contacts")
async def list_contacts(source: str | None = None):
    store = get_state_store()
    contacts = store.get_contacts()
    if source:
        contacts = [contact for contact in contacts if contact.source == source]
    return {"count": len(contacts), "contacts": [c.model_dump(mode="json") for c in contacts]}


@router.get("/contacts/history")
async def contact_history(limit: int = 100):
    store = get_state_store()
    contacts = store.get_history(limit)
    return {"count": len(contacts), "contacts": [c.model_dump(mode="json") for c in contacts]}


@router.get("/contacts/{entity_id}")
async def get_contact(entity_id: str):
    store = get_state_store()
    contact = next((c for c in store.get_contacts() if c.entity_id == entity_id), None)
    if contact is None:
        return {"status": "not_found", "entity_id": entity_id}
    return {"status": "ok", "contact": contact.model_dump(mode="json")}


@router.get("/tracks")
async def list_tracks():
    store = get_state_store()
    tracks = store.get_tracks()
    return {"count": len(tracks), "tracks": {k: v.model_dump(mode="json") for k, v in tracks.items()}}


@router.get("/threats")
async def list_threats():
    store = get_state_store()
    threats = store.get_threats()
    return {"count": len(threats), "threats": [t.model_dump(mode="json") for t in threats]}


@router.get("/coas")
async def list_coas():
    store = get_state_store()
    scored = store.get_scored_coas()
    return {
        "count": len(scored),
        "scored_coas": [s.model_dump(mode="json") for s in scored],
        "roe_summary": _roe_summary(scored),
    }


@router.get("/recommendation")
async def get_recommendation():
    store = get_state_store()
    rec = store.get_recommendation()
    if rec is None:
        return {"recommendation": None}
    return {"recommendation": rec.model_dump(mode="json")}


@router.get("/analysis")
async def full_analysis():
    """Return the complete current analysis snapshot."""
    store = get_state_store()
    state = store.state
    contacts = store.get_contacts()
    threats = store.get_threats()
    anomalies = store.get_anomalies() if hasattr(store, "get_anomalies") else []
    scored = store.get_scored_coas()
    rec = store.get_recommendation()
    tracks = store.get_tracks()
    assets = store.get_asset_states()
    return {
        "state": state.model_dump(mode="json"),
        "contacts": [c.model_dump(mode="json") for c in contacts],
        "threats": [t.model_dump(mode="json") for t in threats],
        "anomalies": [a.model_dump(mode="json") for a in anomalies],
        "scored_coas": [s.model_dump(mode="json") for s in scored],
        "roe_summary": _roe_summary(scored),
        "recommendation": rec.model_dump(mode="json") if rec else None,
        "tracks": {k: v.model_dump(mode="json") for k, v in tracks.items()},
        "assets": [asset.model_dump(mode="json") for asset in assets],
        "llm_status": await llm_status(),
        "latest_event_summary": (
            store.get_latest_event_summary().model_dump(mode="json")
            if store.get_latest_event_summary() else None
        ),
    }


@router.post("/combat_contacts/toggle")
async def toggle_combat_contacts(payload: CombatContactToggleRequest):
    store = get_state_store()
    store.set_combat_contact_state(
        enabled=payload.enabled,
        density=payload.density,
        scenario_type=payload.scenario_type,
    )
    return {"status": "ok", "combat_contacts": store.get_combat_contact_state()}


@router.post("/combat_contacts/inject")
async def inject_combat_contact(payload: CombatContactInjectRequest):
    engine = get_contact_engine()
    store = get_state_store()
    bounds = None
    if engine._sim is not None:
        bounds = engine._sim._bounds
    if bounds is None:
        bounds = {"lat_min": 0.0, "lat_max": 0.0, "lon_min": 0.0, "lon_max": 0.0}

    # Domain-aware placement validation when lat/lon are provided
    placement_warning = None
    lat = payload.lat
    lon = payload.lon
    if lat is not None and lon is not None:
        validation = validate_placement(lat, lon, payload.kind)
        if not validation.valid:
            placement_warning = validation.warning
            if validation.snapped_lat is not None and validation.snapped_lon is not None:
                lat = validation.snapped_lat
                lon = validation.snapped_lon
        elif validation.warning:
            placement_warning = validation.warning

    contact = engine._combat.inject_contact(
        kind=payload.kind,
        scenario_bounds=bounds,
        infrastructure=store.get_infrastructure(),
        subtype=payload.subtype,
        suspicious=payload.suspicious,
        allegiance=payload.allegiance,
        lat=lat,
        lon=lon,
        heading=payload.heading,
        speed=payload.speed,
        altitude_ft=payload.altitude_ft,
        depth_m=payload.depth_m,
        sensor_source=payload.sensor_source,
        track_quality=payload.track_quality,
        timestamp=payload.timestamp,
    )
    engine.inject_contact(contact)
    analysis = get_event_loop().run_analysis_now(trigger="combat_contact_injection")
    result = {"status": "ok", "contact": contact.model_dump(mode="json"), "analysis": analysis, "combat_contacts": store.get_combat_contact_state()}
    if placement_warning:
        result["placement_warning"] = placement_warning
    return result


@router.get("/ais/visible")
async def visible_ais_contacts(
    latmin: float,
    latmax: float,
    lonmin: float,
    lonmax: float,
    include_in_analysis: bool = True,
):
    store = get_state_store()
    engine = get_contact_engine()
    loop = get_event_loop()
    if settings.ais_provider == "noaa_replay":
        result = get_noaa_replay_feed().visible_contacts(
            scenario_id=store.state.scenario.scenario_id or "baltic_hybrid_001",
            infrastructure=store.get_infrastructure(),
            latmin=latmin,
            latmax=latmax,
            lonmin=lonmin,
            lonmax=lonmax,
        )
    else:
        dataclass_result = get_ais_feed().fetch_visible_contacts(
            latmin=latmin,
            latmax=latmax,
            lonmin=lonmin,
            lonmax=lonmax,
            infrastructure=store.get_infrastructure(),
        )
        result = {
            "contacts": dataclass_result.contacts,
            "suspicious_contacts": dataclass_result.suspicious_contacts,
            "source_summary": dataclass_result.source_summary,
            "cache_hit": dataclass_result.cache_hit,
            "provider_enabled": dataclass_result.provider_enabled,
        }

    analysis = None
    analysis_changed = False
    suspicious_contacts = result.get("suspicious_contacts", [])
    provider_enabled = bool(result.get("provider_enabled", False))
    if include_in_analysis and provider_enabled:
        suspicious_ids = {contact.entity_id for contact in suspicious_contacts}
        existing_ais_ids = {
            contact.entity_id
            for contact in store.get_contacts()
            if contact.source in ("aishub", "noaa_replay")
        }
        for contact in suspicious_contacts:
            engine.inject_contact(contact)
        for stale_id in existing_ais_ids - suspicious_ids:
            engine.remove_contact(stale_id)
        analysis_changed = bool(suspicious_contacts or existing_ais_ids - suspicious_ids)
        if analysis_changed:
            analysis = loop.run_analysis_now(trigger="ais_visible_feed")

    return {
        "status": "ok",
        "provider": settings.ais_provider,
        "enabled": provider_enabled,
        "cache_hit": bool(result.get("cache_hit", False)),
        "source_summary": result.get("source_summary", ""),
        "contacts": result.get("contacts", []),
        "suspicious_count": len(suspicious_contacts),
        "analysis": analysis,
        "analysis_changed": analysis_changed,
    }


# ---- Control ----


@router.post("/mode/{mode}")
async def set_engine_mode(mode: str):
    engine = get_contact_engine()
    try:
        engine.set_mode(EngineMode(mode))
    except ValueError:
        return {"status": "error", "message": f"Invalid mode: {mode}. Use: simulation, hybrid, live"}
    return {"status": "ok", "mode": mode}


@router.post("/scenario/load")
async def load_scenario_with_options(payload: dict):
    scenario_id = payload.get("scenario_id", "baltic_hybrid_001")
    seed = payload.get("seed", 42)
    timing_jitter = payload.get("timing_jitter", 0)
    position_jitter = payload.get("position_jitter", 0.0)
    mode = payload.get("mode", "simulation")

    settings.simulation_seed = int(seed)

    generator = ScenarioGenerator(
        seed=int(seed),
        timing_jitter=int(timing_jitter),
        position_jitter=float(position_jitter),
    )
    try:
        template = generator.generate(scenario_id)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    scheduler = get_engine_scheduler()
    if scheduler.running:
        await scheduler.stop()

    engine = get_contact_engine()
    engine.reset()
    engine.set_mode(EngineMode(mode))
    engine.load_scenario(scenario_id, template=template)

    return {
        "status": "ok",
        "scenario_id": scenario_id,
        "seed": int(seed),
        "timing_jitter": int(timing_jitter),
        "position_jitter": float(position_jitter),
        "mode": mode,
        "metadata": template.metadata,
    }


@router.post("/scenario/{scenario_id}")
async def load_scenario(scenario_id: str):
    engine = get_contact_engine()
    engine.load_scenario(scenario_id)
    return {"status": "ok", "scenario_id": scenario_id}


@router.post("/assets")
async def set_assets(assets: list[AssetState]):
    store = get_state_store()
    store.set_asset_states(asset_states=assets)
    return {"status": "ok", "assets": [asset.model_dump(mode="json") for asset in store.get_asset_states()]}


@router.post("/tick")
async def run_tick():
    engine = get_contact_engine()
    contacts = engine.tick()
    loop = get_event_loop()
    result = loop.run_tick()
    return {"status": "ok", "new_contacts": len(contacts), **result}


@router.post("/inject")
async def inject_contact(batch: ContactBatch):
    engine = get_contact_engine()
    loop = get_event_loop()
    results = []
    warnings = []
    for contact in batch.contacts:
        validation = validate_placement(contact.lat, contact.lon, contact.contact_type.value)
        if not validation.valid:
            msg = validation.warning or "Invalid placement"
            warnings.append({"entity_id": contact.entity_id, "warning": msg})
            if validation.snapped_lat is not None and validation.snapped_lon is not None:
                contact.lat = validation.snapped_lat
                contact.lon = validation.snapped_lon
        elif validation.warning:
            warnings.append({"entity_id": contact.entity_id, "warning": validation.warning})
        sig = engine.inject_contact(contact)
        results.append({"contact_id": contact.contact_id, "significant": sig})
    analysis = loop.run_analysis_now(trigger="manual_injection")
    resp = {"status": "ok", "contacts_injected": len(results), "results": results, "analysis": analysis}
    if warnings:
        resp["placement_warnings"] = warnings
    return resp


@router.delete("/inject/{entity_id}")
async def remove_injected(entity_id: str):
    engine = get_contact_engine()
    loop = get_event_loop()
    removed = engine.remove_contact(entity_id)
    analysis = loop.run_analysis_now(trigger="manual_delete") if removed else None
    return {"status": "ok" if removed else "not_found", "removed": entity_id, "analysis": analysis}


@router.patch("/contacts/{entity_id}")
async def update_contact(entity_id: str, update: ContactUpdateRequest):
    engine = get_contact_engine()
    loop = get_event_loop()
    try:
        significant = engine.update_contact(entity_id, update)
    except KeyError:
        return {"status": "not_found", "entity_id": entity_id}
    analysis = loop.run_analysis_now(trigger="manual_update")
    return {"status": "ok", "entity_id": entity_id, "significant": significant, "analysis": analysis}


@router.post("/actions")
async def schedule_action(action: EngineActionRequest):
    engine = get_contact_engine()
    try:
        trigger = engine.schedule_action(action)
    except RuntimeError as exc:
        return {"status": "error", "message": str(exc)}
    return {"status": "ok", "scheduled": trigger}


@router.post("/reset")
async def reset_engine():
    scheduler = get_engine_scheduler()
    if scheduler.running:
        await scheduler.stop()
    engine = get_contact_engine()
    engine.reset()
    return {"status": "ok"}


@router.post("/start")
async def start_engine(
    scenario_id: str = "baltic_hybrid_001",
    mode: str = "simulation",
    interval: float = 2.0,
    seed: int | None = None,
    timing_jitter: int = 0,
    position_jitter: float = 0.0,
):
    effective_seed = seed if seed is not None else settings.simulation_seed
    if seed is not None:
        settings.simulation_seed = seed

    generator = ScenarioGenerator(
        seed=effective_seed,
        timing_jitter=timing_jitter,
        position_jitter=position_jitter,
    )
    try:
        template = generator.generate(scenario_id)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    scheduler = get_engine_scheduler()
    await scheduler.start(scenario_id, mode, interval, template=template)
    return {
        "status": "ok",
        "scenario_id": scenario_id,
        "mode": mode,
        "interval": interval,
        "seed": effective_seed,
        "timing_jitter": timing_jitter,
        "position_jitter": position_jitter,
    }


@router.post("/stop")
async def stop_engine():
    scheduler = get_engine_scheduler()
    await scheduler.stop()
    return {"status": "ok"}


@router.get("/briefing")
async def generate_briefing(lang: str = "en"):
    loop = get_event_loop()
    result = loop.run_full_briefing(language=lang)
    return result


@router.post("/briefing/export/pdf")
async def export_cached_briefing_pdf(briefing: Briefing):
    """Export an already-generated briefing as PDF without re-running the pipeline."""
    from ..engine.export import export_briefing_pdf
    content = export_briefing_pdf(briefing)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=briefing.pdf"},
    )


@router.post("/translate-ui")
async def translate_ui(payload: dict):
    """Translate UI strings to the target language using the LLM."""
    from ..engine.llm_narrative import translate_ui_strings
    language = payload.get("language", "en")
    strings = payload.get("strings", {})
    if language == "en" or not strings:
        return {"translations": {}}
    translated = translate_ui_strings(strings, language)
    return {"translations": translated or {}}


# ---- Natural Language Query ----


@router.post("/query")
async def query_operational_state(payload: dict):
    """Answer a natural-language question about current operational state."""
    question = payload.get("question", "").strip()
    ui_language_hint = payload.get("ui_language_hint") or None
    force_language = payload.get("force_language") or None
    if not question:
        return {"answer": "No question provided.", "sources_used": [], "llm_used": False}
    result = answer_question(question, ui_language_hint=ui_language_hint, force_language=force_language)
    return result

# ---- Scenario Generator ----


@router.get("/scenario/templates")
async def list_scenario_templates():
    return {"templates": ScenarioGenerator.list_templates()}


@router.get("/scenario/info")
async def scenario_info():
    engine = get_contact_engine()
    store = get_state_store()
    if engine._sim is None:
        return {"status": "no_scenario_loaded"}
    sim = engine._sim
    meta = sim.scenario_metadata
    scenario_state = store.state.scenario
    return {
        "status": "ok",
        "tick": sim.tick,
        "metadata": meta,
        "upcoming_stimuli": sim.upcoming_stimuli,
        "active_stimuli": sim.active_stimuli_list,
        "fired_stimuli": sim.fired_stimuli_list,
        "mode": engine.mode.value,
        "seed": scenario_state.seed if scenario_state.seed is not None else settings.simulation_seed,
        "environment": scenario_state.environment,
        "timing_jitter": scenario_state.timing_jitter,
        "position_jitter": scenario_state.position_jitter,
        "active_incidents": scenario_state.active_incidents,
        "infrastructure_status": scenario_state.infrastructure_status,
    }


@router.get("/scenario/stimuli")
async def scenario_stimuli():
    engine = get_contact_engine()
    if engine._sim is None:
        return {"status": "no_scenario_loaded"}
    sim = engine._sim
    return {
        "status": "ok",
        "tick": sim.tick,
        "upcoming": sim.upcoming_stimuli,
        "active": sim.active_stimuli_list,
        "fired": sim.fired_stimuli_list,
    }



# ---- Streaming ----


@router.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """WebSocket: subscribe to engine tick updates."""
    await websocket.accept()
    scheduler = get_engine_scheduler()

    try:
        # Read optional config
        try:
            init_msg = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            config = json.loads(init_msg)
            scenario_id = config.get("scenario_id", "baltic_hybrid_001")
            mode = config.get("mode", "simulation")
            interval = float(config.get("tick_interval", 2.0))
        except (asyncio.TimeoutError, json.JSONDecodeError):
            scenario_id = "baltic_hybrid_001"
            mode = "simulation"
            interval = 2.0

        # Start the scheduler if not running
        if not scheduler.running:
            await scheduler.start(scenario_id, mode, interval)

        # Subscribe to updates
        queue = scheduler.subscribe()

        try:
            while True:
                tick_data = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_json(tick_data)
        except asyncio.TimeoutError:
            await websocket.send_json({"type": "heartbeat"})
        except WebSocketDisconnect:
            pass
        finally:
            scheduler.unsubscribe(queue)

    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
