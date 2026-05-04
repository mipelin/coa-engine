from __future__ import annotations

import html
import io
import time
from datetime import datetime, timezone

from .aar_generator import GeneratedReport, generate_aar_report
from .briefing_generator import generate_briefing_report
from .reporting_context import ReportingContext, build_reporting_context


def generate_report(mode: str = "combined", language: str = "en", context: ReportingContext | None = None) -> dict:
    started = time.monotonic()
    report_context = context or build_reporting_context()
    normalized_mode = mode if mode in {"aar", "briefing", "combined"} else "combined"

    if normalized_mode == "aar":
        return generate_aar_report(report_context, language).to_dict()
    if normalized_mode == "briefing":
        return generate_briefing_report(report_context, language).to_dict()

    briefing = generate_briefing_report(report_context, language)
    aar = generate_aar_report(report_context, language)
    duration_ms = int((time.monotonic() - started) * 1000)
    fallback_reasons = [item for item in (briefing.fallback_reason, aar.fallback_reason) if item]
    return {
        "text": f"COMMANDER BRIEFING\n\n{briefing.text}\n\nAFTER ACTION REPORT\n\n{aar.text}",
        "briefing": briefing.text,
        "aar": aar.text,
        "llm_used": briefing.llm_used or aar.llm_used,
        "mode": "combined",
        "fallback_reason": ";".join(fallback_reasons) if fallback_reasons else None,
        "duration_ms": duration_ms,
    }


def export_report_pdf(report: dict, context: ReportingContext) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

    scenario = context.scenario
    scenario_name = scenario.get("scenario_name") or scenario.get("scenario_id") or "Operational Scenario"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    mode = report.get("mode", "combined")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("NatoTitle", parent=styles["Title"], fontSize=16, leading=20, textColor=colors.HexColor("#111827"))
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#374151"))
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=11, leading=14, textColor=colors.HexColor("#1f2937"), spaceBefore=8)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, leading=12)

    elements = [
        Paragraph("UNCLASSIFIED / SIMULATION", meta_style),
        Paragraph("NATO-STYLE OPERATIONAL REPORT", title_style),
        Paragraph(f"Scenario: {html.escape(str(scenario_name))}", meta_style),
        Paragraph(f"Generated: {generated_at}", meta_style),
        Paragraph(f"Mode: {html.escape(str(mode)).upper()} | LLM used: {bool(report.get('llm_used'))}", meta_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#6b7280")),
        Spacer(1, 8),
    ]

    if mode == "combined":
        _append_text(elements, section_style, body_style, "Commander Briefing", report.get("briefing") or "")
        _append_text(elements, section_style, body_style, "After Action Report", report.get("aar") or "")
    else:
        _append_text(elements, section_style, body_style, "Commander Briefing" if mode == "briefing" else "After Action Report", report.get("text") or "")

    elements.extend([
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#6b7280")),
        Paragraph("Advisory decision-support output. Synthetic data. Not an execution order.", meta_style),
    ])
    doc.build(elements)
    return buffer.getvalue()


def _append_text(elements: list, section_style, body_style, title: str, text: str) -> None:
    from reportlab.platypus import Paragraph, Spacer

    elements.append(Paragraph(html.escape(title), section_style))
    for block in (text or "").split("\n"):
        clean = block.strip()
        if not clean:
            elements.append(Spacer(1, 4))
            continue
        if clean[:2].isdigit() and "." in clean[:4]:
            elements.append(Paragraph(f"<b>{html.escape(clean)}</b>", body_style))
        else:
            elements.append(Paragraph(html.escape(clean), body_style))
