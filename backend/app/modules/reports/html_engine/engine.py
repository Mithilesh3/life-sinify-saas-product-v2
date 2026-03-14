from __future__ import annotations

import base64
from datetime import datetime
from io import BytesIO
import json
import logging
import mimetypes
from pathlib import Path
import re
from typing import Any, Dict, List, Sequence

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.modules.reports.blueprint import BASIC_SECTION_KEYS

from .svg_diagrams import (
    build_loshu_grid_svg,
    build_numerology_architecture_svg,
    build_planetary_orbit_svg,
    build_structural_deficit_svg,
)

try:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover - import path depends on runtime env
    PlaywrightError = Exception
    sync_playwright = None

try:
    from pypdf import PdfReader, PdfWriter
except Exception:  # pragma: no cover - optional runtime optimization
    PdfReader = None
    PdfWriter = None


logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
STRATEGIC_TEMPLATE_NAME = "strategic_life_audit.html"
BASIC_TEMPLATE_NAME = "basic_numerology_report.html"
ASSETS_ROOT = Path(__file__).resolve().parents[3] / "assets"

METRIC_CONFIG: Sequence[Dict[str, str]] = (
    {
        "key": "life_stability_index",
        "label": "जीवन स्थिरता | Life Stability",
        "chart_label": "Life Stability",
    },
    {
        "key": "confidence_score",
        "label": "निर्णय स्पष्टता | Decision Clarity",
        "chart_label": "Decision Clarity",
    },
    {
        "key": "dharma_alignment_score",
        "label": "धर्म संरेखण | Dharma Alignment",
        "chart_label": "Dharma Alignment",
    },
    {
        "key": "emotional_regulation_index",
        "label": "भावनात्मक संतुलन | Emotional Regulation",
        "chart_label": "Emotional Regulation",
    },
    {
        "key": "financial_discipline_index",
        "label": "वित्त अनुशासन | Financial Discipline",
        "chart_label": "Financial Discipline",
    },
    {
        "key": "karma_pressure_index",
        "label": "कर्म दबाव | Karma Pressure",
        "chart_label": "Karma Pressure",
    },
)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_text(value: Any, default: str = "") -> str:
    text = " ".join(str(value or "").split())
    return text or default


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return [item for item in value if item not in (None, "", [], {})]
    if value in (None, "", [], {}):
        return []
    return [value]


def _clip_text(value: Any, max_chars: int = 180, default: str = "") -> str:
    text = _safe_text(value, default)
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 1].rstrip()}…"


def _hindi_major_text(value: Any, default: str = "") -> str:
    text = _safe_text(value, default)
    if not text:
        return default

    text = re.sub(r"\{[^{}]+\}", "", text)
    text = re.sub(r"(,\s*){2,}", ", ", text)
    text = re.sub(r"\s{2,}", " ", text).strip(" ,;|")
    if not text:
        return default or "इनपुट उपलब्ध नहीं"

    replacements = (
        ("Deterministic", "निर्धारित"),
        ("deterministic", "निर्धारित"),
        ("Current ", "वर्तमान "),
        ("Primary ", "मुख्य "),
        ("Risk band", "रिस्क बैंड"),
        ("Risk Band", "रिस्क बैंड"),
        ("strategic", "रणनीतिक"),
        ("profile", "प्रोफाइल"),
        ("analysis", "विश्लेषण"),
        ("indicates", "संकेत देता है"),
        ("shows", "दिखाता है"),
        ("supports", "सपोर्ट करता है"),
        ("improves", "बेहतर करता है"),
        ("stabilize", "स्थिर करें"),
        ("discipline", "डिसिप्लिन"),
    )
    for source, target in replacements:
        text = text.replace(source, target)

    latin_letters = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))
    latin_ratio = latin_letters / max(len(text), 1)
    if latin_ratio > 0.6 and not re.search(r"[\u0900-\u097F]", text):
        text = f"रणनीतिक संकेत: {text}. सुधार के लिए disciplined execution protocol लागू करें।"

    return text


def _status_label(status: str) -> str:
    normalized = _safe_text(status).lower()
    if normalized == "strong":
        return "मजबूत | Strong"
    if normalized == "moderate":
        return "मध्यम | Moderate"
    if normalized == "sensitive":
        return "संवेदनशील | Sensitive"
    return _hindi_major_text(status, "मध्यम | Moderate")


def _format_timestamp(value: Any) -> str:
    text = _safe_text(value)
    if not text:
        return datetime.utcnow().strftime("%d %b %Y")

    normalized = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
        return dt.strftime("%d %b %Y")
    except ValueError:
        return datetime.utcnow().strftime("%d %b %Y")


def _risk_band(metrics: Dict[str, Any]) -> str:
    explicit = _safe_text(metrics.get("risk_band"))
    if explicit:
        return explicit

    confidence = _safe_int(metrics.get("confidence_score"), 50)
    stability = _safe_int(metrics.get("life_stability_index"), 50)
    emotional = _safe_int(metrics.get("emotional_regulation_index"), 50)
    finance = _safe_int(metrics.get("financial_discipline_index"), 50)
    karma = _safe_int(metrics.get("karma_pressure_index"), 50)
    weakest = min(confidence, stability, emotional, finance)

    if karma >= 75 or weakest <= 34:
        return "उच्च जोखिम | High Risk - Structural Intervention Required"
    if karma >= 60 or weakest <= 49:
        return "वॉच ज़ोन | Watch Zone - Guided Stabilization Needed"
    if weakest >= 70 and karma <= 45:
        return "स्थिर ग्रोथ | Stable Growth - Strategic Scaling Window"
    return "सुधार योग्य | Correctable - Disciplined Execution Needed"


def _status_from_score(score: int) -> str:
    if score >= 75:
        return "Strong"
    if score >= 55:
        return "Moderate"
    return "Sensitive"


def _join_numbers(values: Sequence[Any], default: str = "-") -> str:
    cleaned = [str(_safe_int(item)) for item in values if _safe_int(item, 0) > 0]
    return ", ".join(cleaned) if cleaned else default


def _as_uri(path: Path) -> str:
    if path.exists():
        return path.resolve().as_uri()
    return ""


def _as_image_src(path: Path, max_dim: int = 220) -> str:
    if not path.exists():
        return ""
    try:
        from PIL import Image

        with Image.open(path) as image:
            image = image.copy()
            image.thumbnail((max_dim, max_dim))
            buffer = BytesIO()
            has_alpha = (
                "A" in image.getbands()
                or image.info.get("transparency") is not None
            )
            if has_alpha:
                if image.mode not in ("RGBA", "LA"):
                    image = image.convert("RGBA")
                image.save(
                    buffer,
                    format="PNG",
                    optimize=True,
                    compress_level=9,
                )
                mime = "image/png"
            else:
                if image.mode != "RGB":
                    image = image.convert("RGB")
                image.save(
                    buffer,
                    format="JPEG",
                    quality=74,
                    optimize=True,
                    progressive=True,
                )
                mime = "image/jpeg"
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    except Exception:
        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "image/png"
        try:
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        except OSError:
            return _as_uri(path)
        return f"data:{mime};base64,{encoded}"

    if not encoded:
        return _as_uri(path)
    return f"data:{mime};base64,{encoded}"


def _as_background_src(path: Path, max_dim: int = 900) -> str:
    if not path.exists():
        return ""
    try:
        from PIL import Image

        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((max_dim, max_dim))
            buffer = BytesIO()
            image.save(
                buffer,
                format="JPEG",
                quality=52,
                optimize=True,
                progressive=True,
            )
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
            return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return _as_uri(path)


def _build_context(data: Dict[str, Any], watermark: bool) -> Dict[str, Any]:
    payload = data or {}
    identity = payload.get("identity") or {}
    birth_details = payload.get("birth_details") or {}
    meta = payload.get("meta") or {}

    metrics = payload.get("core_metrics") or {}
    metric_explanations = payload.get("metric_explanations") or {}
    metrics_spine = payload.get("metrics_spine") or {}
    numerology_core = payload.get("numerology_core") or {}

    primary_insight = payload.get("primary_insight") or {}
    architecture_text = payload.get("numerology_architecture") or {}
    archetype = payload.get("archetype_intelligence") or {}
    loshu = payload.get("loshu_diagnostic") or {}
    planetary = payload.get("planetary_mapping") or {}
    deficit_model = payload.get("structural_deficit_model") or {}
    circadian = payload.get("circadian_alignment") or {}
    environment = payload.get("environment_alignment") or {}
    vedic = payload.get("vedic_remedy_protocol") or {}
    execution = payload.get("execution_plan") or {}
    section_payloads = payload.get("section_payloads") or {}
    report_blueprint = payload.get("report_blueprint") or {}

    pythagorean = numerology_core.get("pythagorean") or {}
    chaldean = numerology_core.get("chaldean") or {}
    loshu_grid = numerology_core.get("loshu_grid") or {}

    plan_tier = _safe_text(
        meta.get("plan_tier")
        or report_blueprint.get("plan_tier"),
        "basic",
    ).lower()

    # BASIC no longer targets a fixed 12-page cap; keep richer per-section content.
    narrative_limit = 780 if plan_tier == "basic" else 580
    card_limit = 180 if plan_tier == "basic" else 140

    foundation = architecture_text.get("foundation") or pythagorean.get("life_path_number")
    left_pillar = architecture_text.get("left_pillar") or pythagorean.get("destiny_number")
    right_pillar = architecture_text.get("right_pillar") or pythagorean.get("expression_number")
    facade = architecture_text.get("facade") or chaldean.get("name_number")

    metric_rows: List[Dict[str, Any]] = []
    radar_labels: List[str] = []
    radar_values: List[int] = []

    for metric in METRIC_CONFIG:
        key = metric["key"]
        value = max(0, min(100, _safe_int(metrics.get(key), 50)))
        details = metric_explanations.get(key) if isinstance(metric_explanations, dict) else {}
        details = details if isinstance(details, dict) else {}

        meaning = _clip_text(
            details.get("meaning"),
            max_chars=card_limit,
            default="यह score numerology और intake data से निकला deterministic signal है।",
        )
        driver = _clip_text(
            details.get("driver"),
            max_chars=card_limit,
            default="Primary driver inference profile और behavior signals पर आधारित है।",
        )
        risk = _clip_text(
            details.get("risk"),
            max_chars=card_limit,
            default="इस area में low score execution quality को कम कर सकता है।",
        )
        improvement = _clip_text(
            details.get("improvement"),
            max_chars=card_limit,
            default="इस metric के लिए measurable 21-day practice install करें।",
        )

        metric_rows.append(
            {
                "label": metric["label"],
                "value": value,
                "status": _status_label(_safe_text(details.get("status"), _status_from_score(value))),
                "meaning": _hindi_major_text(meaning),
                "driver": _hindi_major_text(driver),
                "risk": _hindi_major_text(risk),
                "improvement": _hindi_major_text(improvement),
            }
        )

        radar_labels.append(metric["chart_label"])
        radar_values.append(value)

    present_numbers = _safe_list(loshu.get("present_numbers") or loshu_grid.get("present_numbers"))
    missing_numbers = _safe_list(loshu.get("missing_numbers") or loshu_grid.get("missing_numbers"))

    center_presence = loshu.get("center_presence")
    if isinstance(center_presence, bool):
        center_present = center_presence
    else:
        center_present = 5 in {_safe_int(item, 0) for item in present_numbers}

    architecture_svg = build_numerology_architecture_svg(
        foundation=foundation,
        left_pillar=left_pillar,
        right_pillar=right_pillar,
        facade=facade,
    )
    loshu_svg = build_loshu_grid_svg(
        grid_counts=loshu_grid.get("grid_counts") or {},
        missing_numbers=missing_numbers,
    )
    deficit_svg = build_structural_deficit_svg(deficit_model)
    planetary_svg = build_planetary_orbit_svg(planetary, numerology_core)

    brand_logo_uri = _as_image_src(ASSETS_ROOT / "branding" / "numai_logo.png", max_dim=72)
    if not brand_logo_uri:
        brand_logo_uri = _as_image_src(ASSETS_ROOT / "branding" / "logo.png", max_dim=72)

    deva_font_regular = _as_uri(ASSETS_ROOT / "fonts" / "NotoSansDevanagari-Regular.ttf")
    deva_font_bold = _as_uri(ASSETS_ROOT / "fonts" / "NotoSansDevanagari-Bold.ttf")

    full_name = _safe_text(identity.get("full_name"), "Strategic Client")
    report_date = _format_timestamp(meta.get("generated_at"))
    cover_title = (
        "अंक जीवन मार्गदर्शन रिपोर्ट | NumAI Basic Numerology Report"
        if plan_tier == "basic"
        else "रणनीतिक जीवन इंटेलिजेंस ऑडिट | Strategic Life Intelligence Audit"
    )
    cover_subtitle = (
        "Pure Numerology + Quick Insight + Correction (हिंदी-प्रधान संस्करण)"
        if plan_tier == "basic"
        else "Numerology Intelligence x AI Strategy (हिंदी-प्रधान संस्करण)"
    )

    cover_ganesha_uri = _as_image_src(ASSETS_ROOT / "cover" / "ganesha.png", max_dim=220)
    cover_krishna_uri = _as_image_src(ASSETS_ROOT / "cover" / "krishna.png", max_dim=200)
    cover_ganesh_yantra_uri = (
        _as_image_src(ASSETS_ROOT / "cover" / "ganesh_yantra.png", max_dim=420)
        or _as_image_src(ASSETS_ROOT / "cover" / "ganesh_yantra.png.png", max_dim=420)
    )
    lotus_gold_uri = _as_image_src(ASSETS_ROOT / "lotus" / "lotus_gold.png", max_dim=96)
    lotus_chart_uri = (
        _as_image_src(ASSETS_ROOT / "lotus" / "lotus_numerology_chart.svg", max_dim=360)
        or _as_image_src(ASSETS_ROOT / "lotus" / "lotus_numerology_chart.png", max_dim=360)
        or lotus_gold_uri
    )
    mandala_bg_uri = _as_background_src(ASSETS_ROOT / "sacred" / "mandala_bg.png", max_dim=900)
    om_gold_uri = _as_image_src(ASSETS_ROOT / "sacred" / "om_gold.png", max_dim=96)
    chakra_icon_uri = _as_image_src(ASSETS_ROOT / "icons" / "chakra.png", max_dim=96)

    deity_uris = {
        "surya": _as_image_src(ASSETS_ROOT / "deities" / "surya.png", max_dim=96),
        "chandra": _as_image_src(ASSETS_ROOT / "deities" / "chandra.png", max_dim=96),
        "guru": _as_image_src(ASSETS_ROOT / "deities" / "guru.png", max_dim=96),
        "rahu": _as_image_src(ASSETS_ROOT / "deities" / "rahu.png", max_dim=96),
        "budh": _as_image_src(ASSETS_ROOT / "deities" / "budh.png", max_dim=96),
        "shukra": _as_image_src(ASSETS_ROOT / "deities" / "shukra.png", max_dim=96),
        "ketu": _as_image_src(ASSETS_ROOT / "deities" / "ketu.png", max_dim=96),
        "shani": _as_image_src(ASSETS_ROOT / "deities" / "shani.png", max_dim=96),
        "mangal": _as_image_src(ASSETS_ROOT / "deities" / "mangal.png", max_dim=96),
    }

    blueprint_sections = report_blueprint.get("sections") if isinstance(report_blueprint, dict) else []
    blueprint_sections = blueprint_sections or []
    blueprint_title_by_key = {
        _safe_text(item.get("key")): _safe_text(item.get("title"))
        for item in blueprint_sections
        if isinstance(item, dict) and _safe_text(item.get("key"))
    }
    ordered_basic_keys = [
        _safe_text(item.get("key"))
        for item in blueprint_sections
        if isinstance(item, dict) and _safe_text(item.get("key")) in BASIC_SECTION_KEYS
    ]
    if not ordered_basic_keys:
        ordered_basic_keys = [key for key in BASIC_SECTION_KEYS if key in section_payloads]

    icon_by_section = {
        "executive_numerology_summary": cover_ganesha_uri,
        "core_numbers_analysis": cover_krishna_uri,
        "mulank_description": deity_uris["surya"],
        "bhagyank_description": deity_uris["guru"],
        "name_number_analysis": deity_uris["budh"],
        "number_interaction_analysis": chakra_icon_uri,
        "loshu_grid_interpretation": deity_uris["rahu"],
        "missing_numbers_analysis": deity_uris["ketu"],
        "repeating_numbers_impact": deity_uris["shani"],
        "mobile_number_numerology": deity_uris["budh"],
        "mobile_life_number_compatibility": deity_uris["chandra"],
        "email_numerology": deity_uris["budh"],
        "numerology_personality_profile": deity_uris["mangal"],
        "current_life_phase_insight": deity_uris["guru"],
        "career_financial_tendencies": deity_uris["shukra"],
        "relationship_compatibility_patterns": deity_uris["chandra"],
        "health_tendencies_from_numbers": deity_uris["surya"],
        "personal_year_forecast": deity_uris["guru"],
        "lucky_numbers_favorable_dates": lotus_gold_uri,
        "color_alignment": chakra_icon_uri,
        "remedies_lifestyle_adjustments": om_gold_uri,
        "closing_numerology_guidance": lotus_gold_uri,
    }
    diagram_by_section = {
        "core_numbers_analysis": "numerology_architecture",
        "number_interaction_analysis": "numerology_architecture",
        "loshu_grid_interpretation": "loshu_grid",
        "missing_numbers_analysis": "loshu_grid",
        "repeating_numbers_impact": "loshu_grid",
        "personal_year_forecast": "planetary_orbit",
        "lucky_numbers_favorable_dates": "planetary_orbit",
        "remedies_lifestyle_adjustments": "structural_deficit",
        "closing_numerology_guidance": "structural_deficit",
    }
    diagram_svg_by_key = {
        "numerology_architecture": architecture_svg,
        "loshu_grid": loshu_svg,
        "planetary_orbit": planetary_svg,
        "structural_deficit": deficit_svg,
    }

    basic_sections: List[Dict[str, Any]] = []
    for key in ordered_basic_keys:
        section = section_payloads.get(key)
        if not isinstance(section, dict):
            continue

        cards = []
        for card in _safe_list(section.get("cards"))[:6]:
            if not isinstance(card, dict):
                continue
            label = _hindi_major_text(_safe_text(card.get("label"), "-"), "-")
            value = _hindi_major_text(
                _clip_text(card.get("value"), max_chars=card_limit, default="इनपुट उपलब्ध नहीं"),
                "इनपुट उपलब्ध नहीं",
            )
            cards.append({"label": label, "value": value})

        bullets = [
            _hindi_major_text(_clip_text(item, max_chars=card_limit))
            for item in _safe_list(section.get("bullets"))
            if _safe_text(item)
        ][:4]

        diagram_key = diagram_by_section.get(key)
        basic_sections.append(
            {
                "key": key,
                "title": _safe_text(
                    section.get("title"),
                    blueprint_title_by_key.get(key, key.replace("_", " ").title()),
                ),
                "narrative": _hindi_major_text(
                    _clip_text(section.get("narrative"), max_chars=narrative_limit, default="इनपुट उपलब्ध नहीं"),
                    "इनपुट उपलब्ध नहीं",
                ),
                "cards": cards,
                "bullets": bullets,
                "icon_uri": icon_by_section.get(key, chakra_icon_uri),
                "diagram_key": diagram_key or "",
                "diagram_svg": diagram_svg_by_key.get(diagram_key or "", ""),
            }
        )

    basic_section_pages = [
        {
            "page_number": index + 2,
            "section": section,
        }
        for index, section in enumerate(basic_sections)
    ]
    basic_total_pages = 1 + len(basic_sections)

    return {
        "watermark": watermark,
        "report": payload,
        "meta": {
            "plan_tier": plan_tier,
            "report_date": report_date,
            "plan": plan_tier.upper(),
            "version": _safe_text(meta.get("report_version"), "6.0"),
            "engine_version": _safe_text(meta.get("engine_version"), "1.0.0"),
            "section_count": _safe_int(report_blueprint.get("section_count"), len(basic_sections)),
        },
        "cover": {
            "title": cover_title,
            "subtitle": cover_subtitle,
            "name": full_name,
            "dob": _safe_text(
                birth_details.get("date_of_birth") or identity.get("date_of_birth"),
                "इनपुट उपलब्ध नहीं",
            ),
            "risk_band": _risk_band(metrics),
        },
        "primary_insight": {
            "core_archetype": _hindi_major_text(_safe_text(
                primary_insight.get("core_archetype")
                or (payload.get("numerology_archetype") or {}).get("archetype_name"),
                "Strategic Adaptive Profile",
            )),
            "strength": _hindi_major_text(_safe_text(
                primary_insight.get("strength")
                or (payload.get("executive_brief") or {}).get("key_strength"),
                "Pattern recognition and adaptive execution.",
            )),
            "critical_deficit": _hindi_major_text(_safe_text(
                primary_insight.get("critical_deficit")
                or (payload.get("executive_brief") or {}).get("key_risk"),
                "Decision structure under pressure requires calibration.",
            )),
            "stability_risk": _hindi_major_text(_safe_text(
                primary_insight.get("stability_risk"),
                _risk_band(metrics),
            )),
            "phase_1": _hindi_major_text(_safe_text(
                primary_insight.get("phase_1_diagnostic")
                or (payload.get("growth_blueprint") or {}).get("phase_1"),
                "Establish baseline rhythm and signal clarity.",
            )),
            "phase_2": _hindi_major_text(_safe_text(
                primary_insight.get("phase_2_blueprint")
                or (payload.get("growth_blueprint") or {}).get("phase_2"),
                "Build structural blueprint around weakest metric.",
            )),
            "phase_3": _hindi_major_text(_safe_text(
                primary_insight.get("phase_3_intervention_protocol")
                or (payload.get("growth_blueprint") or {}).get("phase_3"),
                "Run 21-day intervention protocol with checkpoints.",
            )),
            "narrative": _hindi_major_text(_clip_text(
                primary_insight.get("narrative")
                or (payload.get("executive_brief") or {}).get("summary"),
                max_chars=narrative_limit,
                default="Deterministic insight indicates that long-term scaling depends on consistency and disciplined execution.",
            )),
        },
        "metrics": {
            "rows": metric_rows,
            "radar_labels_json": json.dumps(radar_labels, ensure_ascii=False),
            "radar_values_json": json.dumps(radar_values, ensure_ascii=False),
            "risk_band": _risk_band(metrics),
            "spine": {
                "primary_strength": _hindi_major_text(_safe_text(
                    metrics_spine.get("primary_strength"),
                    metric_rows[0]["label"] if metric_rows else "Life Stability",
                )),
                "primary_deficit": _hindi_major_text(_safe_text(
                    metrics_spine.get("primary_deficit"),
                    metric_rows[-1]["label"] if metric_rows else "Karma Pressure",
                )),
                "structural_cause": _hindi_major_text(_clip_text(
                    metrics_spine.get("structural_cause"),
                    max_chars=180,
                    default="Current weakest axis is linked to structural pattern gaps and stress-reactivity.",
                )),
                "intervention_focus": _hindi_major_text(_clip_text(
                    metrics_spine.get("intervention_focus"),
                    max_chars=180,
                    default="Install 21-day rhythm and decision protocol before scale actions.",
                )),
            },
        },
        "architecture": {
            "foundation": _safe_text(foundation, "-"),
            "left_pillar": _safe_text(left_pillar, "-"),
            "right_pillar": _safe_text(right_pillar, "-"),
            "facade": _safe_text(facade, "-"),
            "narrative": _hindi_major_text(_clip_text(
                architecture_text.get("narrative"),
                max_chars=narrative_limit,
                default="Foundation numbers interact as a system. Life Path sets the core operating baseline, Destiny and Expression define strategic movement, and Name Number shapes social projection.",
            )),
        },
        "archetype": {
            "signature": _hindi_major_text(_clip_text(
                archetype.get("signature"),
                max_chars=narrative_limit,
                default="This archetype blends analytical depth and adaptive strategy.",
            )),
            "leadership_traits": _hindi_major_text(_clip_text(
                archetype.get("leadership_traits"),
                max_chars=200,
                default="Leads through pattern recognition, timing, and structured execution.",
            )),
            "shadow_traits": _hindi_major_text(_clip_text(
                archetype.get("shadow_traits"),
                max_chars=200,
                default="Under pressure, this profile can over-analyze and delay decisive action.",
            )),
            "growth_path": _hindi_major_text(_clip_text(
                archetype.get("growth_path"),
                max_chars=200,
                default="Install cadence, track behavior weekly, and refine decisions with written filters.",
            )),
        },
        "loshu": {
            "present_numbers": _join_numbers(present_numbers, default="-"),
            "missing_numbers": _join_numbers(missing_numbers, default="-"),
            "center_presence": "उपस्थित | Present" if center_present else "अनुपस्थित | Missing",
            "energy_imbalance": _hindi_major_text(_clip_text(
                loshu.get("energy_imbalance"),
                max_chars=120,
                default="Energy distribution suggests selective strength with patchable blind spots.",
            )),
            "narrative": _hindi_major_text(_clip_text(
                loshu.get("narrative"),
                max_chars=narrative_limit,
                default="Lo Shu geometry highlights where behavior is naturally stable versus where conscious design is required.",
            )),
            "missing_number_meanings": [
                _hindi_major_text(_clip_text(item, max_chars=100))
                for item in _safe_list(loshu.get("missing_number_meanings"))
                if _safe_text(item)
            ][:3],
        },
        "planetary": {
            "background_forces": _hindi_major_text(_clip_text(
                planetary.get("background_forces"),
                max_chars=190,
                default="Planetary map indicates background strategic pressure and momentum channels.",
            )),
            "primary_intervention_planet": _hindi_major_text(_safe_text(
                planetary.get("primary_intervention_planet"),
                "Budh",
            )),
            "calibration_cluster": _hindi_major_text(_clip_text(
                planetary.get("calibration_cluster"),
                max_chars=120,
                default="clarity, discipline, measured response",
            )),
            "narrative": _hindi_major_text(_clip_text(
                planetary.get("narrative"),
                max_chars=narrative_limit,
                default="Planetary mapping is treated as a calibration system for intervention, not a prediction table.",
            )),
        },
        "deficit": {
            "deficit": _hindi_major_text(_clip_text(
                deficit_model.get("deficit") or deficit_model.get("structural_deficit"),
                max_chars=140,
                default="Missing center 5",
            )),
            "symptom": _hindi_major_text(_clip_text(
                deficit_model.get("symptom") or deficit_model.get("behavioral_symptom"),
                max_chars=140,
                default="Decision instability during high-noise phases.",
            )),
            "patch": _hindi_major_text(_clip_text(
                deficit_model.get("patch") or deficit_model.get("engineered_patch"),
                max_chars=140,
                default="Deploy a daily protocol with measurable decision filters.",
            )),
            "summary": _hindi_major_text(_clip_text(
                deficit_model.get("summary"),
                max_chars=220,
                default="Deficit-symptom-patch framework translates numerology into operational behavior.",
            )),
        },
        "circadian": {
            "morning": _hindi_major_text(_clip_text(
                circadian.get("morning_routine"),
                max_chars=170,
                default="Start with light exposure, breath reset, and one strategic intention.",
            )),
            "work": _hindi_major_text(_clip_text(
                circadian.get("work_alignment"),
                max_chars=170,
                default="Anchor the first deep work block to the highest-leverage outcome.",
            )),
            "evening": _hindi_major_text(_clip_text(
                circadian.get("evening_shutdown"),
                max_chars=170,
                default="Close with device slowdown, review, and next-day priority lock.",
            )),
            "narrative": _hindi_major_text(_clip_text(
                circadian.get("narrative"),
                max_chars=220,
                default="Rhythm quality directly affects decision quality and emotional recovery.",
            )),
        },
        "environment": {
            "physical_space": _hindi_major_text(_clip_text(
                environment.get("physical_space"),
                max_chars=170,
                default="Use low-clutter zones for deep work, admin, and decompression.",
            )),
            "color_alignment": _hindi_major_text(_clip_text(
                environment.get("color_alignment"),
                max_chars=170,
                default="Use calming and grounding palettes in workspace and device themes.",
            )),
            "mobile_number_analysis": _hindi_major_text(_clip_text(
                environment.get("mobile_number_analysis"),
                max_chars=170,
                default="Mobile vibration signal should support focus and communication stability.",
            )),
            "digital_behavior": _hindi_major_text(_clip_text(
                environment.get("digital_behavior"),
                max_chars=170,
                default="Reduce notification noise and avoid high-impact decisions late at night.",
            )),
            "narrative": _hindi_major_text(_clip_text(
                environment.get("narrative"),
                max_chars=220,
                default="Environment and digital behavior are treated as strategic levers for stability.",
            )),
        },
        "vedic": {
            "focus": _hindi_major_text(_clip_text(
                vedic.get("focus"),
                max_chars=120,
                default="Primary focus: stabilize weakest intelligence metric.",
            )),
            "code": _safe_text(vedic.get("code"), "Om Budhaya Namah"),
            "parameter": _hindi_major_text(_clip_text(
                vedic.get("parameter"),
                max_chars=120,
                default="21 days x 108 chants with fixed timing.",
            )),
            "output": _hindi_major_text(_clip_text(
                vedic.get("output"),
                max_chars=120,
                default="Donate food or learning support weekly.",
            )),
            "purpose": _hindi_major_text(_clip_text(
                vedic.get("purpose"),
                max_chars=200,
                default="Remedy protocol aligns attention, discipline, and planetary calibration.",
            )),
            "pronunciation": _safe_text(vedic.get("pronunciation"), ""),
            "planetary_alignment": _hindi_major_text(_clip_text(
                vedic.get("planetary_alignment"),
                max_chars=120,
                default="Intervention aligned to dominant planetary pattern.",
            )),
        },
        "execution": {
            "install_rhythm": _hindi_major_text(_clip_text(
                execution.get("install_rhythm"),
                max_chars=140,
                default="Days 1-7: install rhythm, reset sleep, and simplify priorities.",
            )),
            "deploy_anchor": _hindi_major_text(_clip_text(
                execution.get("deploy_anchor"),
                max_chars=140,
                default="Days 8-14: deploy metric anchor and enforce decision rules.",
            )),
            "run_protocol": _hindi_major_text(_clip_text(
                execution.get("run_protocol"),
                max_chars=140,
                default="Days 15-21: run intervention without breaks and track checkpoints.",
            )),
            "summary": _hindi_major_text(_clip_text(
                execution.get("summary"),
                max_chars=220,
                default="Execution consistency converts insight into measurable life stability.",
            )),
            "checkpoints": [
                _hindi_major_text(_clip_text(item, max_chars=120))
                for item in _safe_list(execution.get("checkpoints"))
                if _safe_text(item)
            ][:3],
        },
        "diagrams": {
            "numerology_architecture": architecture_svg,
            "loshu_grid": loshu_svg,
            "structural_deficit": deficit_svg,
            "planetary_orbit": planetary_svg,
        },
        "basic_report": {
            "intro_sections": basic_sections[:2],
            "section_pages": basic_section_pages,
            "all_sections": basic_sections,
            "total_pages": basic_total_pages,
        },
        "assets": {
            "brand_logo_uri": brand_logo_uri,
            "deva_font_regular": deva_font_regular,
            "deva_font_bold": deva_font_bold,
            "cover_ganesha_uri": cover_ganesha_uri,
            "cover_krishna_uri": cover_krishna_uri,
            "cover_ganesh_yantra_uri": cover_ganesh_yantra_uri,
            "lotus_gold_uri": lotus_gold_uri,
            "lotus_chart_uri": lotus_chart_uri,
            "mandala_bg_uri": mandala_bg_uri,
            "om_gold_uri": om_gold_uri,
            "chakra_icon_uri": chakra_icon_uri,
            "deity_uris": deity_uris,
        },
    }


def _render_html(context: Dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    plan_tier = _safe_text((context.get("meta") or {}).get("plan_tier"), "basic").lower()
    template_name = BASIC_TEMPLATE_NAME if plan_tier == "basic" else STRATEGIC_TEMPLATE_NAME
    template = env.get_template(template_name)
    return template.render(context)


def _render_pdf_with_playwright(html_content: str) -> bytes:
    if sync_playwright is None:
        raise RuntimeError(
            "Playwright is not installed. Install dependency with `pip install playwright` and browser runtime with `playwright install chromium`."
        )

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1240, "height": 1754})
            page.set_content(html_content, wait_until="networkidle")
            page.emulate_media(media="print")

            try:
                page.wait_for_function("window.__numaiReady === true", timeout=20000)
            except PlaywrightError:
                logger.warning("Timed out waiting for Chart.js readiness flag; continuing PDF render.")

            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
                prefer_css_page_size=True,
            )
            browser.close()
            return pdf_bytes
    except PlaywrightError as exc:
        message = str(exc)
        if "Executable doesn't exist" in message:
            raise RuntimeError(
                "Playwright Chromium runtime is missing. Rebuild backend image so Dockerfile installs it, "
                "or run `python -m playwright install --with-deps chromium` inside the backend container."
            ) from exc
        raise RuntimeError(f"Playwright PDF generation failed: {exc}") from exc


def _optimize_pdf_bytes(pdf_bytes: bytes) -> bytes:
    if PdfReader is None or PdfWriter is None:
        return pdf_bytes

    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        writer = PdfWriter(clone_from=reader)

        for page in writer.pages:
            try:
                page.compress_content_streams()
            except Exception:
                continue

        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

        output = BytesIO()
        writer.write(output)
        optimized = output.getvalue()
        if optimized and len(optimized) < len(pdf_bytes):
            logger.info(
                "Optimized PDF size from %s bytes to %s bytes",
                len(pdf_bytes),
                len(optimized),
            )
            return optimized
        return pdf_bytes
    except Exception:
        logger.exception("Post-processing PDF optimization failed; using original bytes")
        return pdf_bytes


def generate_report_pdf(data: Dict[str, Any], watermark: bool = False) -> BytesIO:
    context = _build_context(data, watermark=watermark)
    html_content = _render_html(context)
    pdf_bytes = _render_pdf_with_playwright(html_content)
    pdf_bytes = _optimize_pdf_bytes(pdf_bytes)
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return buffer
