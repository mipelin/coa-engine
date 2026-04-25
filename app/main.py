from fastapi import FastAPI

from .api.routes_scenarios import router as scenarios_router
from .api.routes_events import router as events_router
from .api.routes_analysis import router as analysis_router
from .api.routes_coa import router as coa_router
from .core.config import settings
from .core.schemas import HealthResponse

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(scenarios_router)
app.include_router(events_router)
app.include_router(analysis_router)
app.include_router(coa_router)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version=settings.app_version)
