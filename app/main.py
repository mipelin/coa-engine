from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api.routes_scenarios import router as scenarios_router
from .api.routes_events import router as events_router
from .api.routes_analysis import router as analysis_router
from .api.routes_coa import router as coa_router
from .api.routes_sse import router as sse_router
from .core.config import settings
from .core.logging_config import setup_logging
from .core.rate_limit import get_rate_limiter
from .core.schemas import HealthResponse

setup_logging()

app = FastAPI(title=settings.app_name, version=settings.app_version)

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


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    limiter = get_rate_limiter()
    client_id = request.client.host if request.client else "unknown"
    if request.url.path not in ("/health", "/docs", "/openapi.json", "/redoc"):
        limiter.check(client_id)
    return await call_next(request)


@app.on_event("startup")
async def startup():
    from .core.session import get_session
    from .engine.event_ingestion import load_sample_scenario

    session = get_session()
    session.load_scenario(load_sample_scenario())


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version=settings.app_version)
