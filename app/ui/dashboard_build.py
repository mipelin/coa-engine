"""Assemble the full dashboard HTML from component data files."""
from __future__ import annotations

import json
from pathlib import Path

from ..core.constants import SCENARIO_BOUNDS, SCENARIO_CABLE_ROUTES
from ..i18n.static_translations import STATIC_UI_TRANSLATIONS

_DATA_DIR = Path(__file__).parent


def build_dashboard_html() -> str:
    css = (_DATA_DIR / "dashboard.css.data").read_text()
    body = (_DATA_DIR / "dashboard.html.data").read_text()
    js = (_DATA_DIR / "dashboard.js.data").read_text()

    html = (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>COA Engine</title>\n"
        '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />\n'
        '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>\n'
        f"{css}\n"
        "</head>\n"
        f"{body}\n"
        "<script>\n"
        f"{js}\n"
        "</script>\n"
        "</body>\n"
        "</html>"
    )
    html = html.replace("__SCENARIO_BOUNDS_JSON__", json.dumps(SCENARIO_BOUNDS))
    html = html.replace("__CABLE_ROUTES_JSON__", json.dumps(SCENARIO_CABLE_ROUTES))
    html = html.replace("__STATIC_UI_TRANSLATIONS_JSON__", json.dumps(STATIC_UI_TRANSLATIONS, ensure_ascii=False))
    return html
