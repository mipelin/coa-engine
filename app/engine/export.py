from __future__ import annotations

import io
import json

from ..core.schemas import Briefing


def export_briefing_json(briefing: Briefing) -> str:
    """Export briefing as formatted JSON string."""
    return json.dumps(briefing.model_dump(mode="json"), indent=2)


def export_briefing_pdf(briefing: Briefing) -> bytes:
    """Export briefing as PDF bytes using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    elements = []

    alert_style = ParagraphStyle(
        "Alert",
        parent=styles["Normal"],
        textColor="red",
        fontSize=9,
        alignment=1,
    )

    elements.append(Paragraph("COA ENGINE", styles["Title"]))
    elements.append(Paragraph("COMMANDER DECISION-SUPPORT BRIEFING", styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "ADVISORY ONLY — SYNTHETIC DATA — NOT AN EXECUTION ORDER", alert_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("Situation", styles["Heading2"]))
    elements.append(Paragraph(briefing.situation, styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("Key Indicators", styles["Heading2"]))
    for ind in briefing.key_indicators:
        elements.append(Paragraph(f"• {ind}", styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("Assessment", styles["Heading2"]))
    elements.append(Paragraph(briefing.assessment, styles["Normal"]))
    if briefing.enriched_assessment:
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(briefing.enriched_assessment, styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("COAs Considered", styles["Heading2"]))
    for coa_name in briefing.coas_considered:
        elements.append(Paragraph(f"• {coa_name}", styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("Recommended COA", styles["Heading2"]))
    elements.append(Paragraph(briefing.recommended_coa, styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("Risks", styles["Heading2"]))
    for risk in briefing.risks:
        elements.append(Paragraph(f"• {risk}", styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(f"Assessment Confidence: {briefing.confidence}", styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("Assumptions", styles["Heading2"]))
    for assumption in briefing.assumptions:
        elements.append(Paragraph(f"• {assumption}", styles["Normal"]))

    if briefing.entity_risk_narratives:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Entity Risk Narratives", styles["Heading2"]))
        for entity_id, narrative in briefing.entity_risk_narratives.items():
            elements.append(Paragraph(f"<b>{entity_id}:</b> {narrative}", styles["Normal"]))

    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=1))
    elements.append(Paragraph(
        "COA Engine — Synthetic decision-support prototype. All outputs are advisory.",
        alert_style,
    ))

    doc.build(elements)
    return buffer.getvalue()
