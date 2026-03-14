from io import BytesIO
import logging

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, SimpleDocTemplate

from ..blueprint import get_tier_section_blueprint
from .decorator import PageDecorator
from .fonts import register_fonts
from .layout import *
from .renderer import Renderer

# core sections
from .sections.cover import build_cover
from .sections.executive import build_executive
from .sections.strengths_risks import build_strengths_risks
from .sections.metrics import build_metrics
from .sections.radar import build_radar
from .sections.archetype import build_archetype

# analysis sections
from .sections.career import build_career
from .sections.decision import build_decision
from .sections.emotional import build_emotional
from .sections.financial import build_financial
from .sections.business import build_business

# numerology sections
from .sections.numerology import build_numerology
from .sections.planetary import build_planetary
from .sections.loshu import build_loshu
from .sections.compatibility import build_compatibility
from .sections.personal_year import build_personal_year

# strategy sections
from .sections.strategy import build_strategy
from .sections.growth import build_growth
from .sections.lifestyle import build_lifestyle
from .sections.mobile import build_mobile

# vedic + closing
from .sections.vedic import build_vedic
from .sections.closing import build_closing

logger = logging.getLogger(__name__)


def _build_styles():
    regular_font, bold_font = register_fonts()
    styles = getSampleStyleSheet()

    deep_indigo = colors.HexColor("#0f2f59")
    royal_purple = colors.HexColor("#4a2c5f")
    slate = colors.HexColor("#4a5568")
    gold = colors.HexColor("#c6a15b")

    styles["Normal"].fontName = regular_font
    styles["Normal"].fontSize = 10.5
    styles["Normal"].leading = 15
    styles["Normal"].textColor = slate
    styles["Normal"].alignment = TA_LEFT

    styles["BodyText"].fontName = regular_font
    styles["BodyText"].fontSize = 10.5
    styles["BodyText"].leading = 15.5
    styles["BodyText"].textColor = slate
    styles["BodyText"].alignment = TA_JUSTIFY
    styles["BodyText"].spaceAfter = 6

    styles["Title"].fontName = bold_font
    styles["Title"].fontSize = 30
    styles["Title"].leading = 34
    styles["Title"].textColor = deep_indigo
    styles["Title"].alignment = TA_CENTER

    styles["Heading1"].fontName = bold_font
    styles["Heading1"].fontSize = 24
    styles["Heading1"].leading = 28
    styles["Heading1"].textColor = deep_indigo
    styles["Heading1"].alignment = TA_LEFT

    styles["Heading2"].fontName = bold_font
    styles["Heading2"].fontSize = 17
    styles["Heading2"].leading = 21
    styles["Heading2"].textColor = royal_purple
    styles["Heading2"].alignment = TA_LEFT

    styles["Heading3"].fontName = bold_font
    styles["Heading3"].fontSize = 13
    styles["Heading3"].leading = 17
    styles["Heading3"].textColor = deep_indigo
    styles["Heading3"].alignment = TA_LEFT

    styles["Heading4"].fontName = bold_font
    styles["Heading4"].fontSize = 11
    styles["Heading4"].leading = 14
    styles["Heading4"].textColor = royal_purple
    styles["Heading4"].alignment = TA_LEFT

    for style_name in ("Normal", "BodyText", "Title", "Heading1", "Heading2", "Heading3", "Heading4"):
        styles[style_name].wordWrap = "CJK"
        styles[style_name].encoding = "UTF-8"
        styles[style_name].splitLongWords = 1

    if "SectionBanner" not in styles:
        styles.add(
            ParagraphStyle(
                name="SectionBanner",
                parent=styles["Heading2"],
                fontName=bold_font,
                fontSize=14,
                leading=18,
                textColor=colors.white,
                alignment=TA_LEFT,
                wordWrap="CJK",
                encoding="UTF-8",
                splitLongWords=1,
            )
        )

    if "CoverTitle" not in styles:
        styles.add(
            ParagraphStyle(
                name="CoverTitle",
                parent=styles["Title"],
                fontName=bold_font,
                fontSize=40,
                leading=44,
                textColor=deep_indigo,
                alignment=TA_CENTER,
            )
        )

    if "CoverSubtitle" not in styles:
        styles.add(
            ParagraphStyle(
                name="CoverSubtitle",
                parent=styles["Heading2"],
                fontName=regular_font,
                fontSize=18,
                leading=22,
                textColor=deep_indigo,
                alignment=TA_CENTER,
                wordWrap="CJK",
                encoding="UTF-8",
                splitLongWords=1,
            )
        )

    if "CoverPlan" not in styles:
        styles.add(
            ParagraphStyle(
                name="CoverPlan",
                parent=styles["Heading2"],
                fontName=regular_font,
                fontSize=16,
                leading=20,
                textColor=deep_indigo,
                alignment=TA_CENTER,
                wordWrap="CJK",
                encoding="UTF-8",
                splitLongWords=1,
            )
        )

    if "CoverName" not in styles:
        styles.add(
            ParagraphStyle(
                name="CoverName",
                parent=styles["Heading2"],
                fontName=bold_font,
                fontSize=24,
                leading=28,
                textColor=deep_indigo,
                alignment=TA_CENTER,
                wordWrap="CJK",
                encoding="UTF-8",
                splitLongWords=1,
            )
        )

    # Keep accent available for modules that may rely on this naming.
    if "CoverAccent" not in styles:
        styles.add(
            ParagraphStyle(
                name="CoverAccent",
                parent=styles["Normal"],
                fontName=regular_font,
                fontSize=12,
                textColor=gold,
                alignment=TA_CENTER,
                wordWrap="CJK",
                encoding="UTF-8",
                splitLongWords=1,
            )
        )

    if "TableHeader" not in styles:
        styles.add(
            ParagraphStyle(
                name="TableHeader",
                parent=styles["BodyText"],
                fontName=bold_font,
                fontSize=9.5,
                leading=12.5,
                textColor=colors.white,
                alignment=TA_LEFT,
                wordWrap="CJK",
                encoding="UTF-8",
                splitLongWords=1,
            )
        )

    if "SmallText" not in styles:
        styles.add(
            ParagraphStyle(
                name="SmallText",
                parent=styles["BodyText"],
                fontSize=8.5,
                leading=11,
                wordWrap="CJK",
                encoding="UTF-8",
                splitLongWords=1,
            )
        )

    return styles


def safe_section(func, *args):
    try:
        func(*args)
    except Exception:
        logger.exception("Section failed: %s", func.__name__)


def _normalize_plan_tier(plan_name: str) -> str:
    plan = (plan_name or "").strip().lower()
    if plan == "professional":
        return "pro"
    if plan in {"basic", "pro", "premium", "enterprise"}:
        return plan
    return "basic"


def _resolve_active_blueprint_keys(data: dict, plan_tier: str) -> set[str]:
    blueprint = data.get("report_blueprint")
    if isinstance(blueprint, dict) and isinstance(blueprint.get("sections"), list):
        keys = {
            section.get("key")
            for section in blueprint.get("sections", [])
            if isinstance(section, dict) and section.get("key")
        }
        if keys:
            return keys

    generated = get_tier_section_blueprint(plan_tier)
    return {
        section.get("key")
        for section in generated.get("sections", [])
        if isinstance(section, dict) and section.get("key")
    }


def _is_section_enabled(active_keys: set[str], required_keys: tuple[str, ...]) -> bool:
    if not required_keys:
        return True
    return any(key in active_keys for key in required_keys)


def generate_report_pdf(data, watermark: bool = False):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
    )

    styles = _build_styles()
    renderer = Renderer(styles)

    elements = []

    name = data.get("identity", {}).get("full_name", "User")
    plan = _normalize_plan_tier(data.get("meta", {}).get("plan_tier", "enterprise"))
    active_blueprint_keys = _resolve_active_blueprint_keys(data, plan)

    safe_section(build_cover, elements, styles, name, plan, data)

    section_pipeline = [
        (build_executive, (elements, renderer, styles, data), ("primary_insight",)),
        (build_metrics, (elements, renderer, styles, data), ("intelligence_metrics",)),
        (build_numerology, (elements, renderer, styles, data), ("numerology_architecture",)),
        (build_archetype, (elements, renderer, styles, data), ("archetype_intelligence",)),
        (build_loshu, (elements, renderer, data), ("loshu_diagnostic",)),
        (build_planetary, (elements, renderer, styles, data), ("planetary_mapping",)),
        (build_strategy, (elements, renderer, styles, data), ("structural_deficit_model",)),
        (build_lifestyle, (elements, renderer, styles, data), ("circadian_alignment",)),
        (build_mobile, (elements, renderer, styles, data), ("environment_alignment",)),
        (build_vedic, (elements, renderer, styles, data), ("vedic_remedy_protocol",)),
        (build_growth, (elements, renderer, styles, data), ("execution_plan",)),
    ]

    for func, args, required_keys in section_pipeline:
        if _is_section_enabled(active_blueprint_keys, required_keys):
            safe_section(func, *args)

    if elements and isinstance(elements[-1], PageBreak):
        elements.pop()

    decorator = PageDecorator(force_watermark=watermark)

    doc.build(
        elements,
        onFirstPage=decorator.decorate,
        onLaterPages=decorator.decorate,
    )

    buffer.seek(0)
    return buffer


