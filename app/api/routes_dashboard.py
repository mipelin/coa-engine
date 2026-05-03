from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

from ..ui.dashboard_build import build_dashboard_html

router = APIRouter(tags=["dashboard"])

DASHBOARD_HTML = build_dashboard_html()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> HTMLResponse:
    return HTMLResponse(DASHBOARD_HTML)


@router.get("/", include_in_schema=False)
async def dashboard_root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard")
