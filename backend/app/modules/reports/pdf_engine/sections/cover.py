from datetime import datetime

from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Image, PageBreak, Paragraph, Spacer, Table, TableStyle

from ..assets import GANESHA, KRISHNA, OM_SYMBOL


def _fmt_date(raw):
    if not raw:
        return "Not Provided"
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).strftime("%d %b %Y")
    except Exception:
        return str(raw)


def _cover_deity_image():
    if KRISHNA.exists():
        return KRISHNA
    if GANESHA.exists():
        return GANESHA
    return None


def build_cover(elements, styles, name, plan, data):
    identity = data.get("identity", {}) if isinstance(data, dict) else {}
    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    metrics = data.get("core_metrics", {}) if isinstance(data, dict) else {}

    full_name = name or identity.get("full_name") or "User"
    birth_details = data.get("birth_details", {}) if isinstance(data, dict) else {}
    dob = identity.get("date_of_birth") or birth_details.get("date_of_birth") or "Not Provided"
    generated_at = _fmt_date(meta.get("generated_at"))
    risk_band = metrics.get("risk_band", "Not Classified")

    elements.append(Spacer(1, 18))

    if OM_SYMBOL.exists():
        om_img = Image(str(OM_SYMBOL), width=42, height=42)
        om_img.hAlign = "CENTER"
        elements.append(om_img)
        elements.append(Spacer(1, 4))

    deity_path = _cover_deity_image()
    if deity_path is not None:
        deity_img = Image(str(deity_path), width=62, height=62)
        deity_img.hAlign = "CENTER"
        elements.append(deity_img)

    elements.append(Spacer(1, 6))

    top_hr = HRFlowable(width="68%", thickness=1.7, color=HexColor("#c6a15b"), spaceBefore=0, spaceAfter=0)
    top_hr.hAlign = "CENTER"
    elements.append(top_hr)

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("NumAI Strategic Life Audit", styles["CoverTitle"]))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("जीवन बुद्धि ऑडिट | Strategic Life Intelligence Report", styles["CoverSubtitle"]))
    elements.append(Spacer(1, 2))
    elements.append(Paragraph(f"{plan.upper()} Audit Edition", styles["CoverPlan"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("12-Page Deterministic + AI Intelligence Audit", styles["SmallText"]))

    elements.append(Spacer(1, 10))

    bottom_hr = HRFlowable(width="68%", thickness=1.2, color=HexColor("#c6a15b"), spaceBefore=0, spaceAfter=0)
    bottom_hr.hAlign = "CENTER"
    elements.append(bottom_hr)

    elements.append(Spacer(1, 8))

    identity_table = Table(
        [
            [Paragraph("<b>रिपोर्ट पहचान | Report Identity</b>", styles["Heading3"])],
            [Paragraph(f"<para align='left'><b>नाम | User Name:</b> {full_name}</para>", styles["BodyText"])],
            [Paragraph(f"<para align='left'><b>जन्म तिथि | Date of Birth:</b> {dob}</para>", styles["BodyText"])],
            [Paragraph(f"<para align='left'><b>Risk Band:</b> {risk_band}</para>", styles["BodyText"])],
            [Paragraph(f"<para align='left'><b>Generated On:</b> {generated_at}</para>", styles["BodyText"])],
        ],
        colWidths=[162 * mm],
    )
    identity_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), HexColor("#f5f7fa")),
                ("BOX", (0, 0), (-1, -1), 1, HexColor("#d9e0e8")),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    elements.append(identity_table)

    elements.append(PageBreak())
