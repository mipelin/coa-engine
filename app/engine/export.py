from __future__ import annotations

import io
import json

from ..core.schemas import Briefing

PDF_LABELS = {
    "en": {
        "title": "COMMANDER DECISION-SUPPORT BRIEFING",
        "advisory": "ADVISORY ONLY — SYNTHETIC DATA — NOT AN EXECUTION ORDER",
        "situation": "Situation",
        "key_indicators": "Key Indicators",
        "assessment": "Assessment",
        "coas_considered": "COAs Considered",
        "recommended_coa": "Recommended COA",
        "risks": "Risks",
        "confidence": "Assessment Confidence",
        "assumptions": "Assumptions",
        "entity_risk": "Entity Risk Narratives",
        "footer": "COA Engine — Synthetic decision-support prototype. All outputs are advisory.",
    },
    "es": {
        "title": "BRIEFING DE APOYO A LA DECISIÓN DEL MANDO",
        "advisory": "SOLO ASESORAMIENTO — DATOS SINTÉTICOS — NO ES UNA ORDEN DE EJECUCIÓN",
        "situation": "Situación",
        "key_indicators": "Indicadores clave",
        "assessment": "Evaluación",
        "coas_considered": "COAs consideradas",
        "recommended_coa": "COA recomendada",
        "risks": "Riesgos",
        "confidence": "Confianza de la evaluación",
        "assumptions": "Supuestos",
        "entity_risk": "Narrativas de riesgo por entidad",
        "footer": "COA Engine — Prototipo sintético de apoyo a la decisión. Todas las salidas son consultivas.",
    },
}


def export_briefing_json(briefing: Briefing) -> str:
    """Export briefing as formatted JSON string."""
    return json.dumps(briefing.model_dump(mode="json"), indent=2)


def export_briefing_pdf(briefing: Briefing) -> bytes:
    """Export briefing as PDF bytes using reportlab."""
    from pathlib import Path

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

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
    labels = PDF_LABELS.get(briefing.language or "en", PDF_LABELS["en"])
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font_name = "Helvetica"
    if font_path.exists():
        pdfmetrics.registerFont(TTFont("DejaVuSans", str(font_path)))
        font_name = "DejaVuSans"
        for style_name in ("Title", "Heading2", "Normal"):
            styles[style_name].fontName = font_name
    elements = []

    alert_style = ParagraphStyle(
        "Alert",
        parent=styles["Normal"],
        fontName=font_name,
        textColor="red",
        fontSize=9,
        alignment=1,
    )

    elements.append(Paragraph("COA ENGINE", styles["Title"]))
    elements.append(Paragraph(labels["title"], styles["Heading2"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        labels["advisory"], alert_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(labels["situation"], styles["Heading2"]))
    elements.append(Paragraph(briefing.situation, styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(labels["key_indicators"], styles["Heading2"]))
    for ind in briefing.key_indicators:
        elements.append(Paragraph(f"• {ind}", styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(labels["assessment"], styles["Heading2"]))
    elements.append(Paragraph(briefing.assessment, styles["Normal"]))
    if briefing.enriched_assessment:
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(briefing.enriched_assessment, styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(labels["coas_considered"], styles["Heading2"]))
    for coa_name in briefing.coas_considered:
        elements.append(Paragraph(f"• {coa_name}", styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(labels["recommended_coa"], styles["Heading2"]))
    elements.append(Paragraph(briefing.recommended_coa, styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(labels["risks"], styles["Heading2"]))
    for risk in briefing.risks:
        elements.append(Paragraph(f"• {risk}", styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(f"{labels['confidence']}: {briefing.confidence}", styles["Normal"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(labels["assumptions"], styles["Heading2"]))
    for assumption in briefing.assumptions:
        elements.append(Paragraph(f"• {assumption}", styles["Normal"]))

    if briefing.entity_risk_narratives:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(labels["entity_risk"], styles["Heading2"]))
        for entity_id, narrative in briefing.entity_risk_narratives.items():
            elements.append(Paragraph(f"<b>{entity_id}:</b> {narrative}", styles["Normal"]))

    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=1))
    elements.append(Paragraph(
        labels["footer"],
        alert_style,
    ))

    doc.build(elements)
    return buffer.getvalue()
