import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes_scenarios import router as scenarios_router
from .api.routes_events import router as events_router
from .api.routes_analysis import router as analysis_router
from .api.routes_coa import router as coa_router
from .api.routes_sse import router as sse_router
from .api.routes_engine import router as engine_router
from .api.routes_dashboard import router as dashboard_router
from .core.config import settings
from .core.logging_config import setup_logging
from .core.rate_limit import get_rate_limiter, is_demo_skip_path, is_local_request
from .core.schemas import HealthResponse

setup_logging()
startup_logger = logging.getLogger("coa_engine.startup")


@asynccontextmanager
async def lifespan(application: FastAPI):
    # --- Startup ---
    startup_logger.info(
        "LLM config: enabled=%s base_url=%s model=%s timeout=%.0fs max_tokens=%d api_key_present=%s",
        settings.llm_enabled,
        settings.llm_base_url,
        settings.llm_model,
        settings.llm_timeout_seconds,
        settings.llm_max_tokens,
        "yes" if settings.llm_api_key else "no",
    )

    from .core.session import get_session
    from .engine.event_ingestion import load_sample_scenario

    if settings.persistence_enabled:
        from .engine.persistence import get_persistent_store
        store = get_persistent_store()
        if not store.restore():
            session = get_session()
            session.load_scenario(load_sample_scenario())
    else:
        session = get_session()
        session.load_scenario(load_sample_scenario())

    yield

    # --- Shutdown ---
    if settings.persistence_enabled:
        from .engine.persistence import get_persistent_store
        try:
            get_persistent_store().close()
        except Exception:
            pass


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins_csv.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scenarios_router, prefix="/v1")
app.include_router(events_router, prefix="/v1")
app.include_router(analysis_router, prefix="/v1")
app.include_router(coa_router, prefix="/v1")
app.include_router(sse_router, prefix="/v1")
app.include_router(engine_router, prefix="/v1")
app.include_router(dashboard_router)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if not settings.rate_limit_enabled:
        return await call_next(request)
    if is_local_request(request):
        return await call_next(request)
    path = request.url.path
    if is_demo_skip_path(path):
        return await call_next(request)
    limiter = get_rate_limiter()
    client_id = request.client.host if request.client else "unknown"
    try:
        limiter.check(client_id, path=path)
    except HTTPException:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    return await call_next(request)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version=settings.app_version)
