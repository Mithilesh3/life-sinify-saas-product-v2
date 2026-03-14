from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Dict, List, Sequence, Tuple

from app.modules.reports.blueprint import SECTION_TITLES, get_tier_section_blueprint

PLANET_BY_NUMBER: Dict[int, str] = {
    1: "Surya",
    2: "Chandra",
    3: "Guru",
    4: "Rahu",
    5: "Budh",
    6: "Shukra",
    7: "Ketu",
    8: "Shani",
    9: "Mangal",
    11: "Moon-Jupiter",
    22: "Rahu-Saturn",
}

NUMBER_TRAITS: Dict[int, Dict[str, str]] = {
    1: {"strength": "initiative and leadership", "risk": "over-control", "protocol": "lead with review loops"},
    2: {"strength": "diplomacy and empathy", "risk": "indecision", "protocol": "enforce decision windows"},
    3: {"strength": "communication and creativity", "risk": "scattered execution", "protocol": "convert ideas into weekly outputs"},
    4: {"strength": "discipline and structure", "risk": "rigidity", "protocol": "blend process with flexibility"},
    5: {"strength": "adaptability and speed", "risk": "restless switching", "protocol": "protect freedom inside routine"},
    6: {"strength": "responsibility and trust", "risk": "over-burdening", "protocol": "set role boundaries"},
    7: {"strength": "analysis and insight", "risk": "overthinking", "protocol": "convert insight to checkpoints"},
    8: {"strength": "authority and material strategy", "risk": "pressure intensity", "protocol": "scale with governance"},
    9: {"strength": "vision and influence", "risk": "energy leakage", "protocol": "prioritize and close loops"},
}

COMPOUND_MEANINGS: Dict[int, str] = {
    13: "karmic discipline debt",
    14: "karmic freedom debt",
    16: "karmic ego correction",
    19: "karmic independence debt",
    22: "master builder field",
    33: "master service field",
}

SECTION_META: Dict[str, Dict[str, Any]] = {
    "default": {
        "purpose": "यह सेक्शन निर्धारक diagnosis और correction protocol देता है।",
        "key_inputs": ["numerology_core", "core_metrics", "intake_context"],
        "output_fields": ["cards", "bullets", "narrative"],
        "interpretation_logic": "Structural signals को behavior impact और protocol में map किया जाता है।",
        "tone_guidance": "Executive, premium, और consultation-grade tone बनाए रखें।",
    },
    "intelligence_metrics": {
        "purpose": "Strength, deficit, और intervention focus को measurable format में quantify करें।",
        "key_inputs": ["core_metrics", "loshu_grid", "behavioral_intake"],
        "output_fields": ["primary_strength", "primary_deficit", "structural_cause", "intervention_focus", "risk_band"],
        "interpretation_logic": "Metric stack rank करके उसे structural signals से जोड़ा जाता है।",
        "tone_guidance": "Diagnostic, concise, और high-authority guidance दें।",
    },
}


def _safe_text(value: Any, default: str = "") -> str:
    text = " ".join(str(value or "").split())
    return text or default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return [item for item in value if item not in (None, "", [], {})]
    if value in (None, "", [], {}):
        return []
    return [value]


def _reduce_number(value: int) -> int:
    while value > 9 and value not in {11, 22, 33}:
        value = sum(int(char) for char in str(value))
    return value


def _alpha_sum(value: str) -> int:
    cleaned = "".join(char for char in value.lower() if char.isalpha())
    return sum(ord(char) - 96 for char in cleaned)


def _vibration_from_text(value: str) -> int:
    total = _alpha_sum(value)
    return _reduce_number(total) if total > 0 else 0


def _vibration_from_digits(value: str) -> int:
    digits = [int(char) for char in str(value or "") if char.isdigit()]
    return _reduce_number(sum(digits)) if digits else 0


def _metric_labels() -> Dict[str, str]:
    return {
        "life_stability_index": "Life Stability",
        "confidence_score": "Decision Clarity",
        "dharma_alignment_score": "Dharma Alignment",
        "emotional_regulation_index": "Emotional Regulation",
        "financial_discipline_index": "Financial Discipline",
        "karma_pressure_index": "Karma Pressure",
    }


def _metric_order(scores: Dict[str, Any]) -> List[Tuple[str, int]]:
    keys = [
        "life_stability_index",
        "confidence_score",
        "dharma_alignment_score",
        "emotional_regulation_index",
        "financial_discipline_index",
        "karma_pressure_index",
    ]
    return [(key, _safe_int(scores.get(key), 50)) for key in keys]


def _metric_status(score: int) -> str:
    if score >= 75:
        return "Strong"
    if score >= 55:
        return "Moderate"
    return "Sensitive"


def _risk_band(scores: Dict[str, Any]) -> str:
    confidence = _safe_int(scores.get("confidence_score"), 50)
    stability = _safe_int(scores.get("life_stability_index"), 50)
    emotional = _safe_int(scores.get("emotional_regulation_index"), 50)
    finance = _safe_int(scores.get("financial_discipline_index"), 50)
    karma = _safe_int(scores.get("karma_pressure_index"), 50)
    weakest = min(confidence, stability, emotional, finance)
    if karma >= 75 or weakest <= 35:
        return "High Risk | Structural Intervention Required"
    if karma >= 60 or weakest <= 49:
        return "Watch Zone | Guided Stabilization Required"
    if weakest >= 70 and karma <= 45:
        return "Strategic Growth Zone | Scale with Governance"
    return "Correctable Zone | Protocol-Driven Improvement"


def _dominant_planet(life_path: int, destiny: int, name_number: int) -> str:
    primary = life_path or destiny or name_number or 5
    return PLANET_BY_NUMBER.get(primary, "Budh")


def _parse_date(value: str) -> Tuple[int, int, int]:
    text = _safe_text(value)
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(text, fmt)
            return (dt.day, dt.month, dt.year)
        except ValueError:
            continue
    return (1, 1, 2000)


def _personal_year(day: int, month: int) -> int:
    total = sum(int(char) for char in f"{day:02d}{month:02d}{datetime.utcnow().year}")
    return _reduce_number(total)


def _lucky_dates(day: int, month: int, life_path: int, destiny: int) -> List[int]:
    anchors = {life_path, destiny, _reduce_number(day), _reduce_number(month)}
    anchors.discard(0)
    dates = sorted(value for value in anchors if value <= 31)
    return dates[:5] or [3, 5, 9]


def _karmic_numbers(day: int, name_compound: int, business_compound: int) -> List[int]:
    values = [day, name_compound, business_compound]
    return sorted(set(value for value in values if value in {13, 14, 16, 19}))


def _hidden_passion(loshu_grid: Dict[str, Any], full_name: str) -> Tuple[int, str]:
    counts = loshu_grid.get("grid_counts") if isinstance(loshu_grid, dict) else {}
    if isinstance(counts, dict) and counts:
        best_number = max(range(1, 10), key=lambda number: _safe_int(counts.get(str(number), counts.get(number, 0)), 0))
        return best_number, NUMBER_TRAITS.get(best_number, NUMBER_TRAITS[5])["strength"]
    vibration = _vibration_from_text(full_name) or 5
    return vibration, NUMBER_TRAITS.get(vibration, NUMBER_TRAITS[5])["strength"]


def _pinnacle_challenge(day: int, month: int, year: int) -> Dict[str, List[int]]:
    year_sum = _reduce_number(sum(int(char) for char in str(year)))
    day_root = _reduce_number(day)
    month_root = _reduce_number(month)
    p1 = _reduce_number(day_root + month_root)
    p2 = _reduce_number(day_root + year_sum)
    p3 = _reduce_number(p1 + p2)
    c1 = abs(day_root - month_root)
    c2 = abs(day_root - year_sum)
    c3 = abs(c1 - c2)
    return {"pinnacles": [p1, p2, p3], "challenges": [c1, c2, c3]}

def _name_options(full_name: str, target_numbers: Sequence[int]) -> List[Dict[str, Any]]:
    base = _safe_text(full_name)
    if not base:
        return []
    variants = [base, f"{base}a", f"{base}h", f"{base}aa", f"{base}y", f"{base}i"]
    options: List[Dict[str, Any]] = []
    seen = set()
    for variant in variants:
        key = variant.lower()
        if key in seen:
            continue
        seen.add(key)
        number = _vibration_from_text(variant)
        if number <= 0:
            continue
        if target_numbers and number not in target_numbers:
            continue
        options.append({"option": variant, "number": number, "logic": "aligns with target vibration"})
    return options[:3]


def _handle_patterns(base: str, target_numbers: Sequence[int]) -> List[str]:
    cleaned = "".join(char for char in base.lower() if char.isalnum()) or "strategicprofile"
    patterns: List[str] = []
    for number in target_numbers[:3] or [1, 3, 5]:
        patterns.append(f"{cleaned}.{number}")
        patterns.append(f"{cleaned}_{number}x")
    deduped: List[str] = []
    for item in patterns:
        if item not in deduped:
            deduped.append(item)
    return deduped[:4]


def _compound_meaning(value: int) -> str:
    return COMPOUND_MEANINGS.get(value, "composite growth-pressure cycle")


BASIC_NUMBER_MEANINGS: Dict[int, Dict[str, str]] = {
    1: {"signal": "leadership और आरंभ", "risk": "जल्दबाज़ नियंत्रण"},
    2: {"signal": "सहयोग और संवेदनशीलता", "risk": "निर्णय में देरी"},
    3: {"signal": "अभिव्यक्ति और रचनात्मकता", "risk": "बिखरा फोकस"},
    4: {"signal": "संरचना और अनुशासन", "risk": "कठोरता"},
    5: {"signal": "अनुकूलन और गति", "risk": "अस्थिर स्विचिंग"},
    6: {"signal": "जिम्मेदारी और भरोसा", "risk": "अति-भार लेना"},
    7: {"signal": "विश्लेषण और गहराई", "risk": "अधिक सोच"},
    8: {"signal": "प्राधिकरण और परिणाम", "risk": "दबाव की तीव्रता"},
    9: {"signal": "दृष्टि और प्रभाव", "risk": "ऊर्जा बिखरना"},
}

BASIC_MISSING_EFFECTS: Dict[int, Dict[str, str]] = {
    1: {"gap": "self-initiative में झिझक", "fix": "daily first-action rule"},
    2: {"gap": "भावनात्मक समन्वय में friction", "fix": "response से पहले 10-second pause"},
    3: {"gap": "communication clarity drop", "fix": "हर दिन concise message drill"},
    4: {"gap": "routine inconsistency", "fix": "fixed-time habit anchor"},
    5: {"gap": "adaptability imbalance", "fix": "weekly change-review"},
    6: {"gap": "responsibility boundaries blur", "fix": "clear role limits"},
    7: {"gap": "over-analysis loop", "fix": "decision deadline rule"},
    8: {"gap": "material discipline fluctuation", "fix": "money checkpoint cadence"},
    9: {"gap": "closure energy weak", "fix": "open-loop closure ritual"},
}

BASIC_REPEAT_EFFECTS: Dict[int, str] = {
    1: "assertive streak बढ़ता है",
    2: "emotional sensitivity amplify होती है",
    3: "expressive ऊर्जा तेज़ होती है",
    4: "discipline demand सख्त होती है",
    5: "change-seeking impulse बढ़ता है",
    6: "duty और caretaking pressure बढ़ता है",
    7: "inner analysis लंबा चलता है",
    8: "control और performance drive बढ़ती है",
    9: "idealism और emotional intensity बढ़ती है",
}


def _stable_seed(*parts: Any) -> int:
    joined = "|".join(_safe_text(part) for part in parts if _safe_text(part))
    if not joined:
        return 7
    return sum((index + 1) * ord(char) for index, char in enumerate(joined))


def _pick_variant(seed: int, section_key: str, slot: str, options: Sequence[str]) -> str:
    clean_options = [_safe_text(option) for option in options if _safe_text(option)]
    if not clean_options:
        return ""
    index = _stable_seed(seed, section_key, slot) % len(clean_options)
    return clean_options[index]


def _fit_box_text(value: Any, max_chars: int = 280) -> str:
    text = _safe_text(value)
    if len(text) <= max_chars:
        return text
    trimmed = text[:max_chars].rsplit(" ", 1)[0]
    return f"{trimmed}…"


PERSONAL_YEAR_THEMES: Dict[int, Dict[str, str]] = {
    1: {"theme": "नया आरंभ और पहल", "strength_hook": "यह वर्ष self-start decisions को तेज़ समर्थन देता है", "pressure": "जल्दबाज़ विस्तार", "protocol": "single-priority launch sprint"},
    2: {"theme": "सहयोग और धैर्य", "strength_hook": "partnership-led progress इस cycle में बेहतर compound होती है", "pressure": "decision hesitation", "protocol": "response-pause + coordination review"},
    3: {"theme": "अभिव्यक्ति और visibility", "strength_hook": "communication clarity को public outcomes में बदलना आसान रहता है", "pressure": "scattered focus", "protocol": "message discipline + weekly publishing cadence"},
    4: {"theme": "संरचना और प्रणाली", "strength_hook": "process rigor के साथ execution quality जल्दी स्थिर होती है", "pressure": "rigidity loops", "protocol": "fixed routine + flexible review windows"},
    5: {"theme": "परिवर्तन और adaptation", "strength_hook": "adaptive actions सही boundaries में बड़ा leverage देते हैं", "pressure": "context switching overload", "protocol": "bounded experimentation + closure checklist"},
    6: {"theme": "जिम्मेदारी और stability", "strength_hook": "trust-based commitments इस समय tangible growth में बदलते हैं", "pressure": "over-responsibility fatigue", "protocol": "role-boundary guardrails + recovery rhythm"},
    7: {"theme": "गहराई और introspection", "strength_hook": "analysis को framework में बदलने पर high-quality decisions निकलते हैं", "pressure": "analysis paralysis", "protocol": "insight-to-action checkpoint loop"},
    8: {"theme": "परिणाम और governance", "strength_hook": "authority और disciplined scaling को मजबूत बैकिंग मिलती है", "pressure": "control-heavy execution", "protocol": "governance board + pressure audit"},
    9: {"theme": "closure और synthesis", "strength_hook": "unfinished loops बंद करके बड़ी clarity मिलती है", "pressure": "energy leakage", "protocol": "open-loop closure + selective commitments"},
    11: {"theme": "उच्च अंतर्दृष्टि और intuition", "strength_hook": "vision-led direction को sharp execution में बदलना संभव है", "pressure": "sensitivity overload", "protocol": "grounding rituals + decision filters"},
    22: {"theme": "निर्माण और scale architecture", "strength_hook": "big systems build करने की क्षमता peak पर रहती है", "pressure": "execution burden", "protocol": "macro blueprint + micro accountability"},
}

METRIC_STRENGTH_CONTEXT: Dict[str, str] = {
    "Life Stability": "आप routine से outcome निकालने की क्षमता रखते हैं और chaos में भी base structure बना सकते हैं।",
    "Decision Clarity": "आप ambiguous inputs को practical choices में बदलने का skill-set रखते हैं।",
    "Dharma Alignment": "आपके goals और effort की दिशा में alignment होने पर output quality तेज़ी से improve होती है।",
    "Emotional Regulation": "pressure windows में composure बनाए रखने से आपकी performance advantage बनती है।",
    "Financial Discipline": "money decisions में structured thinking आपकी long-term stability को support करती है।",
    "Karma Pressure": "pressure signals को पहचानकर आप corrective action जल्दी activate कर सकते हैं।",
}

METRIC_RISK_CONTEXT: Dict[str, str] = {
    "Life Stability": "routine breaks होने पर follow-through टूटता है और repeated restarts बढ़ते हैं।",
    "Decision Clarity": "high-noise phases में options अधिक और commitment कम होने का risk बढ़ जाता है।",
    "Dharma Alignment": "effort सही दिशा में न लगने पर busy रहने के बावजूद progress धीमी लगती है।",
    "Emotional Regulation": "stress spike phases में reaction quality गिरने से relationship और decisions दोनों प्रभावित होते हैं।",
    "Financial Discipline": "untracked spending और delayed checkpoints future flexibility को कम कर सकते हैं।",
    "Karma Pressure": "old behavior loops activate होकर correction momentum को पीछे खींच सकते हैं।",
}


def _alignment_signal(vibration: int, anchors: Sequence[int], label: str) -> Tuple[str, str]:
    clean_anchors = [value for value in anchors if isinstance(value, int) and value > 0]
    if _safe_int(vibration, 0) <= 0:
        return "data_limited", f"{label} signal उपलब्ध नहीं होने से alignment reading सीमित है।"
    if not clean_anchors:
        return "neutral", f"{label} vibration {vibration} का baseline प्रभाव neutral माना जाएगा।"

    min_gap = min(abs(vibration - anchor) for anchor in clean_anchors)
    if min_gap == 0:
        return "supportive", f"{label} vibration {vibration} core stack के साथ directly aligned है।"
    if min_gap == 1:
        return "near_supportive", f"{label} vibration {vibration} core stack के काफी करीब है और partial support देता है।"
    if min_gap >= 4:
        return "friction", f"{label} vibration {vibration} core stack से दूर है, इसलिए communication rhythm में friction बन सकता है।"
    return "neutral", f"{label} vibration {vibration} mixed signal देता है; disciplined usage के साथ यह workable है।"


def _harmony_signal(mulank: int, bhagyank: int, name_number: int) -> Tuple[str, str]:
    name_anchor = name_number or bhagyank or mulank or 5
    gaps = [abs(mulank - bhagyank), abs(mulank - name_anchor), abs(bhagyank - name_anchor)]
    max_gap = max(gaps) if gaps else 0
    if max_gap <= 2:
        return "high_harmony", "core numbers में alignment अच्छा है, इसलिए intent और execution का पुल अपेक्षाकृत मजबूत रहता है।"
    if max_gap <= 4:
        return "mixed_harmony", "core numbers में mixed harmony है, यानी कुछ contexts में flow और कुछ में friction उभरता है।"
    return "friction_heavy", "core numbers में gap अधिक है, इसलिए internal push-pull और response drift का जोखिम बढ़ता है।"


def _missing_severity_signal(loshu_missing: Sequence[int]) -> Tuple[str, str]:
    count = len(list(loshu_missing))
    if count >= 6:
        return "high_gap", f"Lo Shu में missing digits ({', '.join(str(v) for v in loshu_missing)}) काफी अधिक हैं; behavioral support systems conscious रूप से बनानी होंगी।"
    if count >= 4:
        return "medium_gap", f"Lo Shu missing set ({', '.join(str(v) for v in loshu_missing)}) moderate gap दिखाता है, जिसे routine correction से भरा जा सकता है।"
    if count >= 2:
        return "light_gap", f"Lo Shu missing digits ({', '.join(str(v) for v in loshu_missing)}) सीमित हैं; targeted habits काफी प्रभावी रहेंगी।"
    return "balanced", "Lo Shu distribution अपेक्षाकृत balanced है, इसलिए correction effort अधिक focused रखा जा सकता है।"


def _build_profile_driven_executive_brief(
    *,
    full_name: str,
    first_name: str,
    city_hint: str,
    focus_text: str,
    current_problem: str,
    mulank: int,
    bhagyank: int,
    life_path: int,
    destiny: int,
    expression: int,
    name_number: int,
    personal_year: int,
    loshu_missing: Sequence[int],
    repeating_numbers: Sequence[int],
    strongest_metric: str,
    strongest_score: int,
    weakest_metric: str,
    weakest_score: int,
    risk_band: str,
    mobile_vibration: int,
    mobile_classification: str,
    email_vibration: int,
    compatibility_level: str,
) -> Dict[str, str]:
    focus_hint = _safe_text(focus_text, "जीवन संतुलन").replace("_", " ")
    concern_hint = _safe_text(current_problem, "वर्तमान जीवन चुनौती")
    city_display = _safe_text(city_hint, "वर्तमान शहर")
    name_number_text = str(name_number) if name_number else "-"
    risk_parts = [part.strip() for part in _safe_text(risk_band).split("|") if part.strip()]
    risk_primary = risk_parts[0] if risk_parts else _safe_text(risk_band, "Correctable Zone")
    risk_protocol = risk_parts[1] if len(risk_parts) > 1 else "protocol-led stabilization"
    repeating_text = ", ".join(str(value) for value in repeating_numbers[:3]) if repeating_numbers else "none"
    anchors = sorted(
        {
            value
            for value in [mulank, bhagyank, life_path, destiny, expression, name_number, personal_year]
            if isinstance(value, int) and value > 0
        }
    )

    harmony_state, harmony_note = _harmony_signal(mulank, bhagyank, name_number)
    harmony_brief = {
        "high_harmony": "core numbers में alignment मजबूत है",
        "mixed_harmony": "core numbers में mixed harmony चल रही है",
        "friction_heavy": "core numbers में friction-heavy gap सक्रिय है",
    }.get(harmony_state, "core numbers में mixed rhythm सक्रिय है")
    missing_state, missing_note = _missing_severity_signal(loshu_missing)
    mobile_state, mobile_note = _alignment_signal(mobile_vibration, anchors, "Mobile")
    email_state, email_note = _alignment_signal(email_vibration, anchors, "Email")
    mobile_classification_hint = _safe_text(mobile_classification, mobile_state.replace("_", " "))

    year_key = personal_year if personal_year in PERSONAL_YEAR_THEMES else _reduce_number(personal_year or 0)
    year_theme = PERSONAL_YEAR_THEMES.get(year_key, PERSONAL_YEAR_THEMES[5])
    strength_core = METRIC_STRENGTH_CONTEXT.get(
        strongest_metric,
        "आपके profile में stable execution leverage मौजूद है।",
    )
    risk_core = METRIC_RISK_CONTEXT.get(
        weakest_metric,
        "यह axis अभी correction demand कर रहा है।",
    )
    compatibility_hint = _safe_text(compatibility_level, "moderate")
    seed = _stable_seed(
        full_name,
        concern_hint,
        focus_hint,
        mulank,
        bhagyank,
        name_number_text,
        personal_year,
        strongest_metric,
        weakest_metric,
        risk_primary,
    )

    summary_templates = [
        f"{first_name} की executive profile में {year_theme['theme']} phase के साथ {harmony_brief}। इसलिए focus '{focus_hint}' पर disciplined sequencing इस समय high-impact रहेगा।",
        f"Core stack {mulank}/{bhagyank}/{name_number_text} और personal year {personal_year} मिलकर यह संकेत देते हैं कि growth संभव है, लेकिन {weakest_metric.lower()} को stabilize किए बिना scale uneven रहेगा।",
        f"For {first_name}, risk context '{risk_primary}' means {strongest_metric.lower()} is the leverage point while {weakest_metric.lower()} is where drift accelerates first. In {city_display}, concern '{concern_hint}' should be converted into measurable weekly actions.",
        f"{city_display} जैसे real-world context में profile की सफलता इस बात पर निर्भर करेगी कि आप {year_theme['pressure']} को कितनी जल्दी control कर पाते हैं।",
    ]
    summary_tail = [
        f"{missing_note}",
        f"{mobile_note} {email_note} Mobile classification '{mobile_classification_hint}' इस combined signal का practical context देता है।",
        f"Repeating pattern ({repeating_text}) और compatibility level '{compatibility_hint}' को साथ पढ़ने पर correction order और स्पष्ट होता है।",
        f"Concern '{concern_hint}' को measurable milestones में बदलना इस report का immediate execution pivot होना चाहिए।",
    ]
    summary = _fit_box_text(
        f"{_pick_variant(seed, 'executive_brief', 'summary', summary_templates)} "
        f"{_pick_variant(seed, 'executive_brief', 'summary_tail', summary_tail)}",
        max_chars=560,
    )

    strength_options = [
        f"{strongest_metric} ({strongest_score}/100) इस profile का strongest operational axis है। {strength_core} {year_theme['strength_hook']}",
        f"मुख्य strength signal {strongest_metric} है और इसकी वजह से high-noise phase में भी आप direction lock करने की क्षमता दिखाते हैं। {harmony_note}",
        f"{strongest_metric} score {strongest_score} बताता है कि सही system मिलने पर आपकी execution quality जल्दी compound हो सकती है, खासकर जब focus '{focus_hint}' पर clear boundaries हों।",
    ]
    if mobile_state in {"supportive", "near_supportive"}:
        strength_options.append(f"{mobile_note} यह signal {strongest_metric.lower()} को day-to-day communication और follow-through में practical support देता है।")
    key_strength = _fit_box_text(
        _pick_variant(seed, "executive_brief", "key_strength", strength_options),
        max_chars=420,
    )

    risk_options = [
        f"{weakest_metric} ({weakest_score}/100) profile का current pressure-point है। {risk_core} {missing_note}",
        f"Risk axis {weakest_metric.lower()} में drift इसलिए दिखता है क्योंकि {harmony_state.replace('_', ' ')} pattern और {year_theme['pressure']} एक साथ load बढ़ाते हैं।",
        f"यदि इस axis पर correction delay हुआ तो {risk_primary} state की intensity बढ़ सकती है, खासकर concern '{concern_hint}' और {missing_state.replace('_', ' ')} Lo Shu profile के संदर्भ में।",
    ]
    if mobile_state == "friction":
        risk_options.append(mobile_note)
    if email_state == "friction":
        risk_options.append(email_note)
    key_risk = _fit_box_text(
        _pick_variant(seed, "executive_brief", "key_risk", risk_options),
        max_chars=420,
    )

    correction_options = [
        f"Correction focus: पहले {year_theme['protocol']} लागू करें, फिर {weakest_metric.lower()} के लिए weekly scorecard चलाएं, और concern '{concern_hint}' को 3 measurable weekly outcomes में तोड़ें।",
        f"Execution order रखें: (1) routine lock, (2) {weakest_metric.lower()} stabilization, (3) mobile/email identity alignment, (4) {strongest_metric.lower()} leverage scale-up।",
        f"{risk_protocol} को daily action में बदलें: morning anchor, mid-week review, और week-end proof log के साथ correction progress visible रखें।",
    ]
    strategic_focus = _fit_box_text(
        _pick_variant(seed, "executive_brief", "strategic_focus", correction_options),
        max_chars=560,
    )

    structural_cause = _fit_box_text(
        f"Root cause stack: {mulank}/{bhagyank}/{name_number_text} में {harmony_state.replace('_', ' ')} signal, Lo Shu gap profile ({missing_state}), और personal year {personal_year} का {year_theme['pressure']} pressure मिलकर {weakest_metric.lower()} axis पर drift बनाते हैं।",
        max_chars=240,
    )
    intervention_focus = _fit_box_text(
        f"{risk_protocol}: {year_theme['protocol']} -> {weakest_metric.lower()} baseline stabilization -> concern '{concern_hint}' पर weekly measurable correction proof।",
        max_chars=240,
    )

    return {
        "summary": summary,
        "key_strength": key_strength,
        "key_risk": key_risk,
        "strategic_focus": strategic_focus,
        "primary_strength": _fit_box_text(f"{strongest_metric} ({strongest_score}/100): {strength_core}", max_chars=200),
        "primary_deficit": _fit_box_text(f"{weakest_metric} ({weakest_score}/100): {risk_core}", max_chars=200),
        "structural_cause": structural_cause,
        "intervention_focus": intervention_focus,
        "short_term": _fit_box_text(f"Short term: {year_theme['protocol']} के साथ {weakest_metric.lower()} volatility को stabilize करें।", max_chars=180),
        "mid_term": _fit_box_text(f"Mid term: Lo Shu missing और repeating pattern ({repeating_text}) पर behavior patches deploy करें।", max_chars=180),
        "long_term": _fit_box_text(f"Long term: {strongest_metric.lower()} leverage को strategic decisions और timing-fit execution में convert करें।", max_chars=180),
    }


CARD_LABELS_HI: Dict[str, str] = {
    "What is happening": "क्या हो रहा है",
    "Why it is happening": "यह क्यों हो रहा है",
    "What it affects": "इसका प्रभाव",
    "What to do about it": "क्या करना चाहिए",
    "Current Number": "वर्तमान संख्या",
    "Current Name Number": "वर्तमान नाम संख्या",
    "Target Numbers": "लक्ष्य संख्याएं",
    "Strength": "मुख्य ताकत",
    "Risk": "मुख्य जोखिम",
    "Current Mobile": "वर्तमान मोबाइल",
    "Target Vibrations": "लक्ष्य वाइब्रेशन",
    "Ending Logic": "अंतिम अंक लॉजिक",
    "Current Email": "वर्तमान ईमेल",
    "Email Vibration": "ईमेल वाइब्रेशन",
    "Authority Signal": "ऑथोरिटी सिग्नल",
    "Starting Stroke": "शुरुआती स्ट्रोक",
    "Ending Stroke": "अंतिम स्ट्रोक",
    "Authority Alignment": "ऑथोरिटी एलाइनमेंट",
    "Business Name": "बिज़नेस नाम",
    "Industry Fit": "इंडस्ट्री फिट",
    "Social Handle": "सोशल हैंडल",
    "Domain Handle": "डोमेन हैंडल",
    "Current Residence Number": "वर्तमान रेजिडेंस नंबर",
    "Residence Vibration": "रेजिडेंस वाइब्रेशन",
    "Current Vehicle Number": "वर्तमान वाहन नंबर",
    "Vehicle Vibration": "वाहन वाइब्रेशन",
    "Focus": "फोकस",
    "Code": "कोड",
    "Parameter": "पैरामीटर",
    "Output": "आउटपुट",
    "Top Priority": "टॉप प्रायोरिटी",
    "High-Impact Quick Fixes": "हाई-इम्पैक्ट क्विक फिक्स",
    "Medium-Term Adjustments": "मिड-टर्म एडजस्टमेंट",
    "Premium Advisory": "प्रीमियम एडवाइजरी",
    "Current Personal Year": "वर्तमान पर्सनल ईयर",
    "Favorable Dates": "अनुकूल तिथियां",
    "Lucky Numbers": "सपोर्टिव नंबर",
    "Risk Band": "रिस्क बैंड",
    "Dominant Planet": "डॉमिनेंट ग्रह",
}

DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")
PLACEHOLDER_PATTERN = re.compile(r"\{[^{}]+\}")

PHRASE_REPLACEMENTS: Sequence[Tuple[str, str]] = [
    ("Deterministic structure", "निर्धारित संरचना"),
    ("deterministic structure", "निर्धारित संरचना"),
    ("Deterministic signal", "निर्धारित संकेत"),
    ("deterministic signal", "निर्धारित संकेत"),
    ("generated from deterministic profile synthesis", "निर्धारित प्रोफाइल synthesis से तैयार"),
    ("Not provided", "इनपुट उपलब्ध नहीं"),
    ("Current cycle", "वर्तमान चक्र"),
    ("Current personal year", "वर्तमान पर्सनल ईयर"),
    ("Personal year", "पर्सनल ईयर"),
    ("Risk band", "रिस्क बैंड"),
    ("Primary deficit", "मुख्य कमी"),
    ("Primary strength", "मुख्य ताकत"),
    ("Current ", "वर्तमान "),
    ("Target ", "लक्ष्य "),
    ("Option ", "विकल्प "),
]

WORD_REPLACEMENTS: Sequence[Tuple[str, str]] = [
    (r"\bprofile\b", "प्रोफाइल"),
    (r"\bstrategic\b", "रणनीतिक"),
    (r"\banalysis\b", "विश्लेषण"),
    (r"\bstructure\b", "संरचना"),
    (r"\bindicates\b", "संकेत देता है"),
    (r"\bshows\b", "दिखाता है"),
    (r"\bsupports\b", "सपोर्ट करता है"),
    (r"\bimproves\b", "बेहतर करता है"),
    (r"\bstabilize\b", "स्थिर करें"),
    (r"\bconsistency\b", "कंसिस्टेंसी"),
    (r"\bdiscipline\b", "डिसिप्लिन"),
    (r"\bstrategy\b", "स्ट्रैटेजी"),
    (r"\brisk\b", "जोखिम"),
    (r"\bstrength\b", "ताकत"),
    (r"\bdeficit\b", "कमी"),
    (r"\balignment\b", "एलाइनमेंट"),
    (r"\bgrowth\b", "ग्रोथ"),
]


def _hindi_mix_text(value: Any) -> str:
    text = _safe_text(value)
    if not text:
        return text

    text = PLACEHOLDER_PATTERN.sub("", text)
    text = re.sub(r"(,\s*){2,}", ", ", text)
    text = re.sub(r"\s+[|]\s+", " | ", text)
    text = re.sub(r"\s{2,}", " ", text).strip(" ,;|")

    if not text:
        return "इनपुट उपलब्ध नहीं"

    for source, target in PHRASE_REPLACEMENTS:
        text = text.replace(source, target)

    for pattern, replacement in WORD_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"\s{2,}", " ", text).strip()
    text = re.sub(r"([|,:;])\1+", r"\1", text)
    text = text.replace("रणनीतिक संकेत: रणनीतिक संकेत:", "रणनीतिक संकेत:")
    text = text.replace("..", ".")

    latin_letters = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))
    latin_ratio = latin_letters / max(len(text), 1)
    has_devanagari = bool(DEVANAGARI_PATTERN.search(text))

    if latin_ratio > 0.55 and not has_devanagari:
        text = f"रणनीतिक संकेत: {text}. इसे सुधार प्रोटोकॉल और disciplined execution के साथ लागू करें।"

    return text


def _localize_payloads(payloads: Dict[str, Any]) -> Dict[str, Any]:
    localized: Dict[str, Any] = {}
    for key, payload in (payloads or {}).items():
        if not isinstance(payload, dict):
            localized[key] = payload
            continue

        entry = dict(payload)

        entry["purpose"] = _hindi_mix_text(
            entry.get("purpose") or "यह सेक्शन deterministic diagnosis और correction protocol देता है।"
        ) or "यह सेक्शन deterministic diagnosis और correction protocol देता है।"
        entry["interpretation_logic"] = _hindi_mix_text(entry.get("interpretation_logic")) or "Structural signal से actionable insight निकाली जाती है।"
        entry["tone_guidance"] = _hindi_mix_text(entry.get("tone_guidance")) or "Executive और premium tone रखें।"
        entry["narrative"] = _hindi_mix_text(entry.get("narrative")) or "इनपुट उपलब्ध नहीं"

        cards = []
        for card in entry.get("cards") or []:
            if not isinstance(card, dict):
                continue
            label = _safe_text(card.get("label"))
            cards.append(
                {
                    "label": CARD_LABELS_HI.get(label, _hindi_mix_text(label)),
                    "value": _hindi_mix_text(card.get("value")) or "इनपुट उपलब्ध नहीं",
                }
            )
        entry["cards"] = cards

        entry["bullets"] = [_hindi_mix_text(item) for item in (entry.get("bullets") or []) if _safe_text(item)]

        localized[key] = entry

    return localized


def _section_payload(
    section_key: str,
    narrative: str,
    what_happening: str,
    why_happening: str,
    impact: str,
    action: str,
    extra_cards: Sequence[Dict[str, str]] | None = None,
    bullets: Sequence[str] | None = None,
) -> Dict[str, Any]:
    meta = SECTION_META.get(section_key, SECTION_META["default"])
    cards = [
        {"label": "क्या हो रहा है", "value": what_happening},
        {"label": "यह क्यों हो रहा है", "value": why_happening},
        {"label": "इसका प्रभाव", "value": impact},
        {"label": "क्या करना चाहिए", "value": action},
    ]
    if extra_cards:
        cards.extend(extra_cards)
    clean_bullets = [_safe_text(item) for item in (bullets or []) if _safe_text(item)]
    return {
        "section_key": section_key,
        "title": SECTION_TITLES.get(section_key, section_key.replace("_", " ").title()),
        "purpose": meta["purpose"],
        "key_inputs": meta["key_inputs"],
        "output_fields": meta["output_fields"],
        "interpretation_logic": meta["interpretation_logic"],
        "tone_guidance": meta["tone_guidance"],
        "cards": cards,
        "bullets": clean_bullets,
        "narrative": _safe_text(narrative),
    }


def _ensure_all_payloads(plan_name: str, payloads: Dict[str, Any]) -> Dict[str, Any]:
    for section in get_tier_section_blueprint(plan_name).get("sections", []):
        key = section.get("key")
        if key and key not in payloads:
            payloads[key] = _section_payload(
                key,
                narrative=f"{SECTION_TITLES.get(key, key)} निर्धारित प्रोफाइल synthesis से तैयार किया गया है।",
                what_happening="इस intelligence layer में स्पष्ट निर्धारित संकेत दिख रहा है।",
                why_happening="यह layer numerology core और intake patterns के रिश्ते से निकला है।",
                impact="यह correction-aware निर्णय lens उपलब्ध कराता है।",
                action="इस protocol को integrated execution system में लागू करें।",
            )
    return payloads


def _personalize_basic_payloads(
    basic_payloads: Dict[str, Any],
    *,
    full_name: str,
    first_name: str,
    date_of_birth: str,
    current_problem: str,
    city_hint: str,
    focus_text: str,
    mulank: int,
    bhagyank: int,
    life_path: int,
    destiny: int,
    expression: int,
    name_number: int,
    name_compound: int,
    personal_year: int,
    strongest_metric: str,
    weakest_metric: str,
    risk_band: str,
    loshu_present: Sequence[int],
    loshu_missing: Sequence[int],
    repeating_numbers: Sequence[int],
    mobile_vibration: int,
    mobile_classification: str,
    mobile_value: str,
    email_value: str,
    email_vibration: int,
    compatibility_summary: str,
    compatibility_level: str,
    career_industry: str,
    lucky_dates: Sequence[int],
    name_targets: Sequence[int],
    favorable_colors: str,
    caution_colors: str,
    dominant_planet: str,
    vedic_code: str,
    vedic_parameter: str,
    lifestyle_protocol: str,
    name_options: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    mulank_signal = BASIC_NUMBER_MEANINGS.get(mulank, BASIC_NUMBER_MEANINGS[5])["signal"]
    bhagyank_signal = BASIC_NUMBER_MEANINGS.get(bhagyank, BASIC_NUMBER_MEANINGS[5])["signal"]
    name_signal = BASIC_NUMBER_MEANINGS.get(name_number or bhagyank or mulank or 5, BASIC_NUMBER_MEANINGS[5])["signal"]
    name_number_text = str(name_number) if name_number else "-"
    present_text = ", ".join(str(value) for value in loshu_present) or "none"
    missing_text = ", ".join(str(value) for value in loshu_missing) or "none"
    repeating_text = ", ".join(str(value) for value in repeating_numbers) if repeating_numbers else "कोई प्रमुख पुनरावृत्ति नहीं"
    lucky_text = ", ".join(str(value) for value in lucky_dates) or "3, 5, 9"
    target_text = ", ".join(str(value) for value in name_targets[:4]) or "3, 5, 9"

    missing_insights: List[str] = []
    for number in list(loshu_missing)[:4]:
        meta = BASIC_MISSING_EFFECTS.get(number, {"gap": "behavior gap", "fix": "daily correction"})
        missing_insights.append(f"{number}→{meta['gap']}")
    missing_insight_text = " | ".join(missing_insights) if missing_insights else "missing gaps limited हैं"

    repeat_insights: List[str] = []
    for number in list(repeating_numbers)[:3]:
        repeat_insights.append(f"{number}→{BASIC_REPEAT_EFFECTS.get(number, 'trait intensity बढ़ती है')}")
    repeat_insight_text = " | ".join(repeat_insights) if repeat_insights else "repeat pressure कम है"

    seed = _stable_seed(
        full_name,
        date_of_birth,
        current_problem,
        focus_text,
        mulank,
        bhagyank,
        name_number,
        personal_year,
        mobile_vibration,
        email_vibration,
        missing_text,
    )

    def _style_line(section_key: str, slot: str, statement: str) -> str:
        clean_statement = _safe_text(statement).rstrip("।.")
        lead = _pick_variant(
            seed,
            section_key,
            f"{slot}:lead",
            ["", "अंक अवलोकन:", "प्रोफ़ाइल विश्लेषण:", "संरचना संकेत:"],
        )
        tail = ""
        if slot == "why":
            tail = _pick_variant(
                seed,
                section_key,
                f"{slot}:tail",
                [
                    f"कारण में Mulank {mulank}, Bhagyank {bhagyank}, Name {name_number_text} और Personal Year {personal_year} एक साथ सक्रिय हैं।",
                    f"Lo Shu missing {missing_text} और repeating pattern इस कारण को व्यवहार में बार-बार trigger करते हैं।",
                    f"Life Path {life_path} और Destiny {destiny} की direction इस कारण की intensity को context के हिसाब से बढ़ाती या घटाती है।",
                ],
            )
        elif slot == "impact":
            tail = _pick_variant(
                seed,
                section_key,
                f"{slot}:tail",
                [
                    f"इसका असर सीधे {weakest_metric} और response consistency की quality पर आता है।",
                    f"अगर यह unchecked रहा तो {risk_band} की दिशा में risk pressure बढ़ सकता है।",
                    f"सही handling होने पर {strongest_metric} का लाभ measurable output में जल्दी दिखता है।",
                ],
            )
        elif slot == "action":
            tail = _pick_variant(
                seed,
                section_key,
                f"{slot}:tail",
                [
                    f"इसे focus '{focus_text}' और concern '{current_problem}' से जोड़कर weekly measurable actions में चलाएं।",
                    f"{city_hint} जैसे context में fixed routine, review slots और low-noise decision windows बेहतर परिणाम देंगे।",
                    f"21-day cycle, weekly proof-log और monthly correction reset साथ रखें।",
                ],
            )

        text = clean_statement
        if lead:
            text = f"{lead} {text}"
        if tail:
            text = f"{text} {tail}"
        if not text.endswith(("।", ".")):
            text = f"{text}।"
        return _fit_box_text(text)

    section_facts: Dict[str, Dict[str, str]] = {
        "executive_numerology_summary": {
            "narrative": f"{full_name} के लिए Mulank {mulank}, Bhagyank {bhagyank}, Name {name_number_text}, Personal Year {personal_year} और focus '{focus_text}' मिलकर मुख्य numerology profile बनाते हैं। Concern: {current_problem}.",
            "what": f"Mulank {mulank} response style में {mulank_signal} को सक्रिय करता है।",
            "why": f"Bhagyank {bhagyank} की direction और Name {name_number_text} की identity resonance इसका कारण है।",
            "impact": f"{strongest_metric} leverage होता है, लेकिन {weakest_metric} में fluctuation friction ला सकती है।",
            "action": "21-day correction routine और weekly review से core instability को stabilize करें।",
        },
        "core_numbers_analysis": {
            "narrative": f"Core stack: Mulank {mulank}, Bhagyank {bhagyank}, Destiny {destiny}, Expression {expression}, Name {name_number_text}.",
            "what": "यह core numbers आपकी decision architecture और response rhythm दिखाती हैं।",
            "why": "DOB digit sum और name vibration deterministic रूप से यह stack बनाते हैं।",
            "impact": "Role-fit, communication tone और discipline quality पर सीधा असर पड़ता है।",
            "action": "हर सप्ताह core numbers के आधार पर 3 priority actions लॉक करें।",
        },
        "mulank_description": {
            "narrative": f"Mulank {mulank} आपकी instinctive personality में {mulank_signal} को प्रमुख बनाता है।",
            "what": "First reaction pattern में Mulank energy तेजी से दिखाई देती है।",
            "why": "जन्मदिन का root vibration reflex behavior को directly shape करता है।",
            "impact": "Pressure phase में impulsive या rigid response pattern उभर सकता है।",
            "action": "Pause rule और routine anchors से Mulank intensity को balance करें।",
        },
        "bhagyank_description": {
            "narrative": f"Bhagyank {bhagyank} long-term path में {bhagyank_signal} theme को drive करता है।",
            "what": "Bhagyank growth direction और recurring lesson-cycle बताता है।",
            "why": "Life-path reduction से यह destiny flow लगातार activate होता है।",
            "impact": "Timing mismatch होने पर progress धीमी और effort heavy महसूस हो सकती है।",
            "action": "Personal Year theme के साथ annual goals align करें।",
        },
        "name_number_analysis": {
            "narrative": f"Name Number {name_number_text} और compound {name_compound} आपकी social projection में {name_signal} signal बनाते हैं।",
            "what": "नाम vibration trust, recall और communication tone को प्रभावित करती है।",
            "why": "अक्षर-वाइब्रेशन का योग identity frequency को encode करता है।",
            "impact": "नाम mismatch होने पर clarity और confidence दोनों dilute हो सकते हैं।",
            "action": "Consistent spelling use करें और practical होने पर target-aligned variant चुनें।",
        },
        "number_interaction_analysis": {
            "narrative": f"Mulank {mulank}, Bhagyank {bhagyank}, Name {name_number_text} interaction profile में harmony-gap signal दिख रहा है।",
            "what": "इन numbers का interaction execution style और emotional pace तय करता है।",
            "why": "Root-number distance बढ़ने पर internal push-pull बढ़ता है।",
            "impact": "Focus और consistency पर cycle-wise friction बन सकती है।",
            "action": "One-habit-one-correction मॉडल से interaction gap कम करें।",
        },
        "loshu_grid_interpretation": {
            "narrative": f"Lo Shu present: {present_text} | missing: {missing_text}.",
            "what": "Grid present बनाम missing energies का practical map देती है।",
            "why": "जन्मतिथि digit distribution से Lo Shu behavior matrix निकलती है।",
            "impact": f"Current grid में {missing_insight_text} जैसे gaps दिखाई देते हैं।",
            "action": "Weekly tracker से missing themes का progress validate करें।",
        },
        "missing_numbers_analysis": {
            "narrative": f"Missing numbers: {missing_text}.",
            "what": "Missing digits behavioral blind zones का संकेत देती हैं।",
            "why": "Absent digits के कारण कुछ traits conscious effort से build करनी पड़ती हैं।",
            "impact": "Untreated gaps से repeated friction और response fatigue बनती है।",
            "action": "हर missing digit के लिए micro-habit correction लागू करें।",
        },
        "repeating_numbers_impact": {
            "narrative": f"Repeating numbers pattern: {repeating_text}. {repeat_insight_text}.",
            "what": "Repeated digits traits को amplify करती हैं।",
            "why": "एक ही number की frequency बढ़ने पर वही behavior loop बार-बार trigger होता है।",
            "impact": "Over-amplification से rigidity, overthinking या impulsive response बढ़ सकती है।",
            "action": "Amplified trait के opposite balancing habit जोड़ें।",
        },
        "mobile_number_numerology": {
            "narrative": f"Mobile vibration {mobile_vibration} का classification {mobile_classification} है।",
            "what": "Phone-number vibration daily communication tone को shape करती है।",
            "why": f"Digit sum {mobile_vibration} core life numbers के साथ resonance बनाता या घटाता है।",
            "impact": "Mismatch होने पर distraction और decision clarity drop हो सकती है।",
            "action": "Supportive ending logic और disciplined mobile usage रखें।",
        },
        "mobile_life_number_compatibility": {
            "narrative": f"Mobile vibration {mobile_vibration} बनाम life numbers {mulank}/{bhagyank}: {mobile_classification}.",
            "what": "यह pairing communication smoothness और response pace का quick indicator है।",
            "why": "Mobile frequency और life-number resonance day-to-day behavior tune करती है।",
            "impact": "Compatibility low होने पर response delay और fatigue बढ़ सकती है।",
            "action": "Next number update में supportive digit logic prefer करें।",
        },
        "email_numerology": {
            "narrative": (
                f"Email vibration {email_vibration or 0} digital identity signal को प्रभावित कर रही है।"
                if email_value
                else "ईमेल इनपुट उपलब्ध नहीं है; detailed email numerology ईमेल मिलने पर auto-generate होगी।"
            ),
            "what": "Email local-part authority और trust perception पर असर डालता है।",
            "why": "Letter-frequency pattern डिजिटल first impression coding बनाती है।",
            "impact": "Weak email signal response quality और perceived credibility घटा सकती है।",
            "action": "Short, clear और number-aligned email naming pattern अपनाएँ।",
        },
        "numerology_personality_profile": {
            "narrative": f"Personality profile में Mulank {mulank} की instinct, Bhagyank {bhagyank} की direction और Name {name_number_text} की projection संयुक्त रूप से active हैं।",
            "what": "यह profile social style, internal nature और pressure response define करती है।",
            "why": "Core-number interaction से thought-action loop की default quality बनती है।",
            "impact": "Blind spots unmanaged रहने पर relationships और confidence दोनों प्रभावित होते हैं।",
            "action": "Strength-led tasks बढ़ाएँ और blind-spot triggers पर pause रखें।",
        },
        "current_life_phase_insight": {
            "narrative": f"Current life phase में Personal Year {personal_year} और risk band '{risk_band}' correction-priority define कर रहे हैं।",
            "what": "यह चरण stabilization और consistency build करने का संकेत देता है।",
            "why": "Year vibration और weakest metric की pairing phase intensity तय करती है।",
            "impact": "गलत priorities रखने पर effort high और output low रह सकता है।",
            "action": "Limited priorities + weekly review cadence तुरंत लागू करें।",
        },
        "career_financial_tendencies": {
            "narrative": f"Career orientation '{career_industry}' और financial behavior pattern में structure-led growth की जरूरत दिखती है।",
            "what": "Work style depth, accountability और process-fit में बेहतर चलती है।",
            "why": "Core numbers और discipline signals earning-response loop को shape करते हैं।",
            "impact": "Reactive choices income consistency और savings momentum को प्रभावित कर सकती हैं।",
            "action": "Monthly finance checkpoints और role-fit review routine बनाएं।",
        },
        "relationship_compatibility_patterns": {
            "narrative": f"{compatibility_summary} Current compatibility level: {compatibility_level}.",
            "what": "Relationship pattern communication pace और emotional style से बनती है।",
            "why": "Core-number resonance expectation matching या mismatch पैदा करती है।",
            "impact": "Mismatch phase में misunderstanding cycle और trust fatigue बढ़ सकती है।",
            "action": "Clear boundaries और calm communication protocol बनाए रखें।",
        },
        "health_tendencies_from_numbers": {
            "narrative": f"Health tendency numerology view: stress rhythm और recovery quality सबसे अधिक {weakest_metric} axis से प्रभावित है।",
            "what": "यह wellness tendency layer है, medical diagnosis नहीं।",
            "why": "Number imbalance sleep, stress pace और recovery discipline पर असर डालती है।",
            "impact": "Fatigue build-up होने पर clarity और emotional steadiness कमजोर हो सकती है।",
            "action": "Breath reset, fixed sleep window और low-noise shutdown routine रखें।",
        },
        "personal_year_forecast": {
            "narrative": f"वर्तमान Personal Year {personal_year} year-theme और action timing को निर्धारित कर रहा है।",
            "what": "यह वर्ष correction-led consistency और focused progress को support करता है।",
            "why": "Birth day/month और current year के योग से yearly vibration बनती है।",
            "impact": "सही timing पर effort का output बेहतर और तेज़ मिलता है।",
            "action": f"महत्वपूर्ण launches और decisions को favorable dates ({lucky_text}) में रखें।",
        },
        "lucky_numbers_favorable_dates": {
            "narrative": f"Supportive numbers: {target_text} | favorable dates: {lucky_text}.",
            "what": "यह timing utility है, blind superstition नहीं।",
            "why": "Core-number resonance specific dates पर action efficiency बढ़ाती है।",
            "impact": "Aligned windows में response quality और confidence बेहतर रहती है।",
            "action": "Key meetings, outreach और agreements date-fit check के बाद करें।",
        },
        "color_alignment": {
            "narrative": f"Favorable colors: {favorable_colors}. Caution colors: {caution_colors}.",
            "what": "Color vibration focus और mood-stability पर subtle प्रभाव डालती है।",
            "why": "Dominant number resonance कुछ tones के साथ बेहतर sync बनाती है।",
            "impact": "Mismatched palette का overuse energy dull या reactive बना सकता है।",
            "action": "Workspace और wardrobe में favorable colors का controlled उपयोग करें।",
        },
        "remedies_lifestyle_adjustments": {
            "narrative": f"Correction layer: mantra + routine + lifestyle discipline. Dominant support planet: {dominant_planet}.",
            "what": "Practical remedies को daily behavior system से जोड़ना सबसे effective रहता है।",
            "why": "Consistency के बिना corrective signal लंबे समय तक टिकता नहीं है।",
            "impact": "Regular practice से stability, clarity और confidence steadily improve होते हैं।",
            "action": "Daily short mantra, fixed routine और weekly correction review रखें।",
        },
        "closing_numerology_guidance": {
            "narrative": f"Closing synthesis: {full_name} की profile correction-ready है; primary focus {weakest_metric} stabilization और {strongest_metric} leverage पर रहना चाहिए।",
            "what": "Profile fundamentally blocked नहीं है; pattern workable और improvable है।",
            "why": "Core numbers, Lo Shu gaps और habits का संयुक्त प्रभाव final outcomes बनाता है।",
            "impact": "Correction ignore होने पर repeat cycle और confidence drift लौट सकते हैं।",
            "action": f"Next step: 21-day correction routine, monthly review, और {city_hint} context में practical consistency।",
        },
    }

    for key, facts in section_facts.items():
        section = basic_payloads.get(key)
        if not isinstance(section, dict):
            continue

        section["narrative"] = _style_line(key, "narrative", facts["narrative"])
        cards = section.get("cards") or []
        if len(cards) >= 4:
            cards[0]["value"] = _style_line(key, "what", facts["what"])
            cards[1]["value"] = _style_line(key, "why", facts["why"])
            cards[2]["value"] = _style_line(key, "impact", facts["impact"])
            cards[3]["value"] = _style_line(key, "action", facts["action"])

    if isinstance(basic_payloads.get("name_number_analysis"), dict):
        basic_payloads["name_number_analysis"]["bullets"] = [
            f"विकल्प {index + 1}: {item.get('option', full_name)} -> {item.get('number', '-')}"
            for index, item in enumerate(name_options[:3])
        ] or [f"विकल्प 1: {full_name} -> {target_text.split(',')[0].strip()}"]

    if isinstance(basic_payloads.get("missing_numbers_analysis"), dict):
        basic_payloads["missing_numbers_analysis"]["bullets"] = [
            f"Missing {number}: {BASIC_MISSING_EFFECTS.get(number, {'fix': 'daily correction'})['fix']}"
            for number in list(loshu_missing)[:5]
        ]

    if isinstance(basic_payloads.get("mobile_number_numerology"), dict):
        cards = basic_payloads["mobile_number_numerology"].get("cards") or []
        if len(cards) >= 5:
            cards[4]["value"] = mobile_value or "इनपुट उपलब्ध नहीं"

    if isinstance(basic_payloads.get("email_numerology"), dict):
        cards = basic_payloads["email_numerology"].get("cards") or []
        if len(cards) >= 5:
            cards[4]["value"] = email_value or "इनपुट उपलब्ध नहीं"

    if isinstance(basic_payloads.get("personal_year_forecast"), dict):
        cards = basic_payloads["personal_year_forecast"].get("cards") or []
        if len(cards) >= 6:
            cards[4]["value"] = str(personal_year)
            cards[5]["value"] = lucky_text

    if isinstance(basic_payloads.get("lucky_numbers_favorable_dates"), dict):
        cards = basic_payloads["lucky_numbers_favorable_dates"].get("cards") or []
        if len(cards) >= 6:
            cards[4]["value"] = target_text
            cards[5]["value"] = lucky_text

    if isinstance(basic_payloads.get("remedies_lifestyle_adjustments"), dict):
        basic_payloads["remedies_lifestyle_adjustments"]["bullets"] = [
            f"Mantra: {vedic_code}",
            f"Practice: {vedic_parameter}",
            f"Lifestyle: {lifestyle_protocol}",
        ]

    return basic_payloads


def _enrich_basic_payloads(
    basic_payloads: Dict[str, Any],
    *,
    full_name: str,
    first_name: str,
    city_hint: str,
    focus_text: str,
    current_problem: str,
    mulank: int,
    bhagyank: int,
    life_path: int,
    destiny: int,
    expression: int,
    name_number: int,
    name_compound: int,
    loshu_present: Sequence[int],
    loshu_missing: Sequence[int],
    repeating_numbers: Sequence[int],
    mobile_vibration: int,
    mobile_classification: str,
    mobile_value: str,
    email_value: str,
    email_vibration: int,
    compatibility_summary: str,
    compatibility_level: str,
    personal_year: int,
    strongest_metric: str,
    weakest_metric: str,
    risk_band: str,
    lucky_dates: Sequence[int],
    target_numbers: Sequence[int],
    favorable_colors: str,
    caution_colors: str,
    dominant_planet: str,
    vedic_code: str,
    vedic_parameter: str,
    lifestyle_protocol: str,
) -> Dict[str, Any]:
    seed = _stable_seed(
        full_name,
        focus_text,
        current_problem,
        mulank,
        bhagyank,
        life_path,
        destiny,
        expression,
        name_number,
        personal_year,
        ",".join(str(v) for v in loshu_missing),
    )

    mulank_signal = BASIC_NUMBER_MEANINGS.get(mulank or 5, BASIC_NUMBER_MEANINGS[5])["signal"]
    bhagyank_signal = BASIC_NUMBER_MEANINGS.get(bhagyank or 5, BASIC_NUMBER_MEANINGS[5])["signal"]
    name_signal = BASIC_NUMBER_MEANINGS.get(name_number or bhagyank or mulank or 5, BASIC_NUMBER_MEANINGS[5])["signal"]
    risk_primary = _safe_text(risk_band).split("|")[0].strip()
    risk_protocol = _safe_text(risk_band).split("|")[1].strip() if "|" in _safe_text(risk_band) else "नियमित सुधार प्रक्रिया जारी रखें"

    present_text = ", ".join(str(v) for v in loshu_present) if loshu_present else "none"
    missing_text = ", ".join(str(v) for v in loshu_missing) if loshu_missing else "none"
    repeating_text = ", ".join(str(v) for v in repeating_numbers) if repeating_numbers else "none"
    lucky_text = ", ".join(str(v) for v in lucky_dates) if lucky_dates else "3, 5, 9"
    target_text = ", ".join(str(v) for v in target_numbers[:4]) if target_numbers else "3, 5, 9"
    focus_hint = _safe_text(focus_text, "जीवन संतुलन")
    concern_hint = _safe_text(current_problem, "वर्तमान जीवन चुनौती")
    city_display = _safe_text(city_hint, "वर्तमान शहर")
    mobile_state = _safe_text(mobile_classification, "neutral")
    name_number_text = str(name_number) if name_number else "0"

    missing_descriptions = []
    for number in list(loshu_missing)[:4]:
        meta = BASIC_MISSING_EFFECTS.get(number, {"gap": "व्यवहारिक रिक्ति", "fix": "दैनिक सुधार आदत"})
        missing_descriptions.append(f"{number} में {meta['gap']}")
    missing_line = " | ".join(missing_descriptions) if missing_descriptions else "मुख्य missing digits सीमित हैं"

    repeat_descriptions = []
    for number in list(repeating_numbers)[:3]:
        repeat_descriptions.append(f"{number} के दोहराव से {BASIC_REPEAT_EFFECTS.get(number, 'एक trait का volume बढ़ता है')}")
    repeating_line = " | ".join(repeat_descriptions) if repeat_descriptions else "कोई बड़ा दोहराव नहीं है"

    def _sent(text: str) -> str:
        clean = _safe_text(text)
        if not clean:
            return ""
        if clean.endswith(("।", ".")):
            return clean
        return f"{clean}।"

    def _fit_rich(value: str, max_chars: int = 700) -> str:
        text = _safe_text(value)
        if len(text) <= max_chars:
            return text
        window = text[:max_chars]
        end = max(window.rfind("।"), window.rfind("."))
        if end >= int(max_chars * 0.65):
            return window[: end + 1].strip()
        trimmed = window.rsplit(" ", 1)[0].strip()
        return trimmed if trimmed.endswith(("।", ".", "…")) else f"{trimmed}…"

    global_fillers: Dict[str, List[str]] = {
        "what": [
            f"यह संकेत {first_name} के रोज़मर्रा के व्यवहार, communication tone और execution pace में स्पष्ट तौर पर दिखता है",
            f"फोकस '{focus_hint}' और concern '{concern_hint}' के संदर्भ में यह pattern अभी सक्रिय है",
            f"{city_display} जैसे वर्तमान वातावरण में भी यही tendency बार-बार उभरती है",
        ],
        "why": [
            f"कारण एकल नहीं है; Mulank {mulank}, Bhagyank {bhagyank}, Name {name_number_text}, Personal Year {personal_year} और Lo Shu pattern का संयुक्त प्रभाव बन रहा है",
            f"core stack और missing digits की interaction intensity से behavior friction का root स्पष्ट होता है",
            f"इसी वजह से pattern situational नहीं बल्कि repeatable numerology architecture जैसा दिखता है",
        ],
        "impact": [
            f"इसका असर {weakest_metric}, confidence rhythm और decision consistency पर compound तरीके से आता है",
            f"अगर corrective action न हो तो {risk_primary} band के संकेत और गहरे हो सकते हैं",
            f"सही handling होने पर {strongest_metric} leverage होकर overall stability बढ़ती है",
        ],
        "action": [
            "उपायों को 21-day discipline cycle, weekly review और measurable tracking के साथ लागू करना जरूरी है",
            f"weekly execution map बनाकर correction को concern '{concern_hint}' के measurable outcomes से जोड़ें",
            f"छोटे लेकिन लगातार कदम रखें ताकि {weakest_metric} axis में durable सुधार बनता जाए",
        ],
    }

    dynamic_fillers: Dict[str, List[str]] = {
        "what": [
            f"Core stack {mulank}/{bhagyank}/{name_number_text} और personal year {personal_year} का संयुक्त पैटर्न अभी मुख्य संचालन संकेत दे रहा है",
            f"फोकस '{focus_hint}' और concern '{concern_hint}' के कारण यह संकेत इस समय और अधिक visible है",
            f"{city_display} जैसे वातावरण में भी यही प्रवृत्ति दोहरकर सामने आती है, इसलिए इसे स्थायी behavior signal माना जा सकता है",
        ],
        "why": [
            f"current root कारण में missing cluster ({missing_line}) और repeating cluster ({repeating_line}) दोनों का परस्पर दबाव शामिल है",
            f"risk context '{risk_primary}' होने से वही कारण सामान्य दिनों की तुलना में अधिक स्पष्ट दिखाई दे रहे हैं",
            f"stack {mulank}/{bhagyank}/{name_number_text} और personal year {personal_year} साथ आने पर कारण केवल surface-level नहीं रहता",
        ],
        "impact": [
            f"असर की रेंज decision clarity से लेकर relationship pacing और money discipline तक जाती है, इसलिए इसे एक single-issue न समझें",
            f"यदि unchecked रहा तो weekly output quality घट सकती है और long-term confidence curve flatter हो सकती है",
            f"positive correction की स्थिति में {strongest_metric} की ऊर्जा recovery accelerator का काम कर सकती है",
        ],
        "action": [
            f"{city_display} जैसे context में भी routine discipline लागू किया जा सकता है यदि steps measurable हों और review calendar-locked हो",
            f"daily correction को identity consistency, communication drill और timing alignment के साथ जोड़ें ताकि परिणाम टिकाऊ बनें",
            f"हर सप्ताह एक improvement proof लिखें, ताकि progress visible रहे और motivation volatile न बने",
        ],
    }

    def _style_sentence(section_key: str, slot: str, sentence: str, idx: int) -> str:
        styled = _safe_text(sentence)
        style_modes: Sequence[Dict[str, str]] = (
            {},
            {
                "बताता है": "स्पष्ट करता है",
                "दिखता है": "नज़र आता है",
                "प्रभावित करता है": "असर डालता है",
                "प्रभावित हो सकता है": "असर में आ सकता है",
                "जरूरी": "अनिवार्य",
                "सुधार": "बेहतर बदलाव",
            },
            {
                "बताता है": "संकेत देता है",
                "दिखता है": "उभरता है",
                "प्रभावित करता है": "गहरा असर डालता है",
                "प्रभावित हो सकता है": "काफी प्रभावित हो सकता है",
                "जरूरी": "अत्यावश्यक",
                "सुधार": "करेक्टिव बदलाव",
            },
        )
        style_mode = (_stable_seed(seed, section_key, slot) + idx) % len(style_modes)
        for source, target in style_modes[style_mode].items():
            styled = styled.replace(source, target)
        prefix_options = [
            "",
            "",
            "",
            "संख्यात्मक दृष्टि से,",
            "स्पष्ट संकेत यह है कि,",
            "अवलोकन से स्पष्ट है कि,",
        ]
        prefix_index = (_stable_seed(seed, section_key, slot) + idx) % len(prefix_options)
        prefix = _safe_text(prefix_options[prefix_index])
        if prefix:
            return _safe_text(f"{prefix} {styled}")
        return styled

    section_lines: Dict[str, Dict[str, List[str]]] = {
        "executive_numerology_summary": {
            "what": [
                f"आपकी प्रोफ़ाइल में Mulank {mulank}, Bhagyank {bhagyank}, Name Number {name_number_text} और Personal Year {personal_year} एक साथ सक्रिय हैं",
                f"इस संयोजन से {mulank_signal} और {bhagyank_signal} की dual rhythm बनती है, जिसमें गति और गहराई दोनों साथ चलते हैं",
            ],
            "why": [
                f"जब identity signal ({name_signal}) और life direction ({bhagyank_signal}) अलग गति से काम करते हैं, तो अंदर-बाहर के अनुभव में अंतर बनता है",
                f"Lo Shu missing pattern ({missing_text}) इस अंतर को और स्पष्ट करता है क्योंकि कुछ behavioral supports प्राकृतिक रूप से उपलब्ध नहीं रहते",
            ],
            "impact": [
                f"प्रभाव रूप में कभी high clarity और कभी hesitation दिख सकती है, जिससे {weakest_metric} में fluctuation आता है",
                f"यह उतार-चढ़ाव long-term confidence और trust consistency दोनों को प्रभावित कर सकता है",
            ],
            "action": [
                "पहला कदम profile simplification है: एक समय में कम goals लेकर उन्हें rigorously पूरा करें",
                f"दूसरा कदम weekly reflection है जिसमें आप देखें कि कौन-सा व्यवहार आपके मुख्य focus '{focus_hint}' को support कर रहा है",
            ],
        },
        "core_numbers_analysis": {
            "what": [
                f"Core stack में Mulank {mulank} instinct, Bhagyank {bhagyank} direction, Destiny {destiny} execution frame और Expression {expression} communication style को define करता है",
                f"Name Number {name_number_text} इस architecture में public perception layer जोड़ता है, जिससे capability की social readability तय होती है",
            ],
            "why": [
                "ये सभी numbers अलग-अलग behavior layers को नियंत्रित करते हैं, इसलिए इन्हें अलग-अलग पढ़ने के बजाय integrated रूप में देखना जरूरी होता है",
                f"जब इन layers में alignment होता है तो flow smooth रहता है, और mismatch होने पर start और finish के बीच gap बनता है",
            ],
            "impact": [
                "इस संरचना का असर निर्णय की गति, संचार की स्पष्टता, accountability और परिणाम की स्थिरता पर सीधे दिखता है",
                "व्यक्ति सक्षम होने के बावजूद inconsistent दिख सकता है यदि core layers एक ही दिशा में synchronized न हों",
            ],
            "action": [
                "हर सप्ताह top-3 priorities को core numbers के हिसाब से map करें: कौन-सा काम instinct fit है और कौन-सा direction fit",
                "decision के बाद review loop रखें ताकि architecture-driven सुधार व्यवहार में उतर सके",
            ],
        },
        "mulank_description": {
            "what": [
                f"Mulank {mulank} आपके reflex behavior का मुख्य ट्रिगर है और पहली प्रतिक्रिया के टोन में स्पष्ट दिखता है",
                f"इस अंक की वजह से आपकी natural style में {mulank_signal} प्रमुख रहती है, खासकर जब स्थिति नई या urgent हो",
            ],
            "why": [
                "Mulank जन्मदिन की मूल आवृत्ति से निकलता है, इसलिए यह subconscious response pattern पर सीधा प्रभाव डालता है",
                f"यदि Mulank ऊर्जा और Name Number {name_number_text} की अभिव्यक्ति में अंतर हो तो व्यक्ति की intent और expression अलग दिखाई देते हैं",
            ],
            "impact": [
                "इससे impulsive jumps, delayed closure या mixed social signals जैसे पैटर्न बन सकते हैं",
                "stress phase में यही प्रवृत्ति confidence drift और communication inconsistency को बढ़ा सकती है",
            ],
            "action": [
                "response-pause drill अपनाएं: तुरंत निर्णय वाले क्षणों में छोटा विराम, फिर लिखित निर्णय",
                "daily routine में एक non-negotiable execution block रखें ताकि instinctive energy productive दिशा में जाए",
            ],
        },
        "bhagyank_description": {
            "what": [
                f"Bhagyank {bhagyank} आपकी long-term दिशा, maturity pattern और recurring life lessons का आधार बनाता है",
                f"इस अंक की वजह से {bhagyank_signal} theme बार-बार जीवन के अलग चरणों में उभरती है",
            ],
            "why": [
                "Bhagyank date-reduction से निकलकर life-cycle pressure को दर्शाता है, इसलिए यह growth की प्राकृतिक लय बताता है",
                f"Life Path {life_path} और Destiny {destiny} के साथ इसका मेल तय करता है कि progress steady होगी या fragmented",
            ],
            "impact": [
                "alignment होने पर दिशा स्पष्ट रहती है, लेकिन mismatch में मेहनत बढ़कर भी output तुलनात्मक रूप से कम दिख सकता है",
                "गलत समय पर बड़े commitments लेने से frustration और reset cycles बढ़ सकते हैं",
            ],
            "action": [
                "annual goals को quarterly milestones में तोड़ें और हर milestone को personal-year theme से validate करें",
                "long-term decisions में readiness checklist रखें ताकि direction drift न हो",
            ],
        },
        "name_number_analysis": {
            "what": [
                f"Name Number {name_number_text} और compound {name_compound} आपकी public memory, trust signal और communication impression को shape करते हैं",
                f"यह layer बताती है कि लोग आपकी presence को structured, warm, assertive या reserved कैसे पढ़ते हैं",
            ],
            "why": [
                "नाम की अक्षर-आवृत्ति identity frequency बनाती है; spelling consistency और usage frequency इसके प्रभाव को बढ़ाती है",
                f"core stack से इसका alignment कमजोर होने पर perception gap बनता है, जहां क्षमता अधिक पर projection कम दिखती है",
            ],
            "impact": [
                "impact के रूप में clarity loss, social hesitation, delayed trust formation और authority dilution हो सकता है",
                "यह gap professional और personal दोनों interactions में conversion quality को कम कर सकता है",
            ],
            "action": [
                "एक standard spelling निर्धारित करें और सभी public surfaces पर वही रखें",
                f"जहां practical हो, target numbers ({target_text}) की दिशा में identity consistency test करें",
            ],
        },
        "number_interaction_analysis": {
            "what": [
                f"Mulank {mulank}, Bhagyank {bhagyank} और Name Number {name_number_text} के बीच interaction आपकी inner drive और outer expression का समन्वय दिखाता है",
                "यही combination तय करता है कि आप tension में integrated दिखेंगे या fragmented",
            ],
            "why": [
                "जब reflex layer, direction layer और identity layer की गति अलग हो जाती है तो internal push-pull बढ़ता है",
                f"Lo Shu missing cluster ({missing_text}) इस tension को amplify कर सकता है क्योंकि stabilizing supports कम हो जाते हैं",
            ],
            "impact": [
                "यह स्थिति decision reversals, communication mismatch और execution fatigue के रूप में दिखाई दे सकती है",
                "व्यक्ति intent से committed होता है, पर behavior rhythm inconsistent होने पर outcome quality गिरती है",
            ],
            "action": [
                "interaction correction chart बनाएं: trigger, old response, corrected response, measurable result",
                "weekly दो घटनाएं चुनकर देखें कि आपने impulse और direction को कितना sync किया",
            ],
        },
        "loshu_grid_interpretation": {
            "what": [
                f"Lo Shu layout में present digits ({present_text}) आपकी available strengths दिखाते हैं और missing digits ({missing_text}) conscious correction zones बताते हैं",
                "यह grid केवल सूची नहीं बल्कि behavior wiring का practical map है",
            ],
            "why": [
                "grid जन्मतिथि के digit distribution से बनता है, इसलिए यह मानसिक rhythm, routine discipline और emotional handling का आधार बताता है",
                f"आपके pattern में {missing_line} जैसे संकेत combined व्यवहारिक gaps की ओर इशारा करते हैं",
            ],
            "impact": [
                "असर यह होता है कि कुछ क्षेत्रों में तेज़ प्रगति और कुछ में repeated friction साथ-साथ चलते हैं",
                "असंतुलित grid होने पर व्यक्ति planning तो करता है पर sustained follow-through टूट सकता है",
            ],
            "action": [
                "Lo Shu behavior tracker बनाएं: communication, routine, money, recovery, closure पांच axes पर weekly score रखें",
                "missing digits के लिए micro-habit correction रखें और 21-day cycles में परिणाम देखें",
            ],
        },
        "missing_numbers_analysis": {
            "what": [
                f"Missing digits ({missing_text}) का मतलब है कि कुछ behavioral muscles naturally strong नहीं हैं और उन्हें consciously train करना होगा",
                "ये gaps isolated नहीं बल्कि combined pattern बनाकर daily behavior को प्रभावित करते हैं",
            ],
            "why": [
                "जब संबंधित digits जन्म pattern में नहीं होते तो उनके गुण स्वतः नहीं आते और व्यक्ति pressure में reactive mode चुनता है",
                f"इस वजह से कुछ क्षेत्रों में repeated strain बनता है, भले core intent स्पष्ट और सकारात्मक हो",
            ],
            "impact": [
                "impact में communication breaks, delayed closure, habit inconsistency और decision fatigue शामिल हो सकते हैं",
                "दीर्घकाल में यही gaps confidence को धीमे-धीमे कमजोर कर सकते हैं",
            ],
            "action": [
                "हर missing digit के लिए एक targeted corrective habit तय करें और उसे measurable outcome से जोड़ें",
                "monthly review में देखें कौन-से gaps सुधर रहे हैं और किन्हें stronger intervention की जरूरत है",
            ],
        },
        "repeating_numbers_impact": {
            "what": [
                f"Repeating pattern ({repeating_text}) बताता है कि आपकी कुछ traits amplified mode में चलती हैं और behavior volume सामान्य से अधिक हो जाता है",
                f"आपके case में {repeating_line} जैसी tendencies visible हैं, जिन्हें सही channel मिले तो यह advantage बनती हैं",
            ],
            "why": [
                "एक digit का बार-बार आना mind को familiar response loop में रखता है, इसलिए वही pattern अलग contexts में भी repeat होता है",
                f"जब amplification और missing pattern साथ आते हैं, तो overuse और underdevelopment का मिश्रित imbalance बनता है",
            ],
            "impact": [
                "इसका असर या तो high performance spikes के रूप में दिखता है या overthinking/rigidity के रूप में",
                "यदि modulation न हो तो संबंधों और काम दोनों में response quality uneven हो सकती है",
            ],
            "action": [
                "हर amplified trait के साथ opposite balancing habit जोड़ें ताकि behavior range नियंत्रित रहे",
                "daily quick log रखें: आज amplification ने सहायता की या friction बनाया",
            ],
        },
        "mobile_number_numerology": {
            "what": [
                f"Mobile vibration {mobile_vibration} ({mobile_state}) आपकी daily communication energy, response style और interaction clarity को प्रभावित करता है",
                f"current number signal से message timing और conversational tone में subtle pattern बनता है",
            ],
            "why": [
                f"digit-sum resonance core life numbers के साथ sync या mismatch बनाता है, जिससे communication fatigue का स्तर बदलता है",
                f"जब mobile signal और name identity अलग दिशा में हों तो expression noise बढ़ सकता है",
            ],
            "impact": [
                "परिणाम के रूप में delayed responses, unclear follow-ups और mental distraction बढ़ सकती है",
                f"यह pattern {weakest_metric} और confidence consistency को भी प्रभावित कर सकता है",
            ],
            "action": [
                "phone hygiene protocol अपनाएं: response windows, callback slots और notification boundaries तय करें",
                "यदि future में number change हो तो target-compatible ending logic पर विचार करें",
            ],
        },
        "mobile_life_number_compatibility": {
            "what": [
                f"mobile vibration {mobile_vibration} और life stack {mulank}/{bhagyank} का compatibility signal बताता है कि रोज़मर्रा का response flow कितना smooth रहेगा",
                f"अभी का classification ({mobile_state}) communication discipline की आवश्यकता का स्तर तय करता है",
            ],
            "why": [
                "mobile frequency micro-decisions पर प्रभाव डालती है; life numbers से mismatch होने पर cognitive switching load बढ़ता है",
                "यही कारण है कि कुछ दिनों में responsiveness अच्छा रहता है और कुछ दिनों में unplanned delays आते हैं",
            ],
            "impact": [
                "प्रभाव में inconsistent replies, conversation fatigue और priority confusion शामिल हो सकते हैं",
                "long-term में यह भरोसा और relationship pacing दोनों पर असर डाल सकता है",
            ],
            "action": [
                "communication rules लिखित करें: urgent, important और routine responses के लिए अलग windows रखें",
                "सप्ताह में एक बार interaction audit करें और friction patterns को कम करने के लिए behavior tweaks लागू करें",
            ],
        },
    }

    section_lines.update(
        {
            "email_numerology": {
                "what": [
                    f"Email vibration {email_vibration or 0} आपकी digital identity readability, professionalism signal और trust perception को प्रभावित करता है",
                    "email handle का tone अक्सर first response की quality और seriousness तय करता है, इसलिए यह identity का functional हिस्सा है",
                ],
                "why": [
                    "email numerology अक्षर-पैटर्न, naming clarity और consistency से बनती है; यह केवल number नहीं बल्कि signal architecture है",
                    f"Name Number {name_number_text} और email vibration में तालमेल रहने पर public identity coherent दिखती है",
                ],
                "impact": [
                    "mismatch होने पर व्यक्ति सक्षम होने के बावजूद online communication में clarity loss और delayed trust का सामना कर सकता है",
                    "career, outreach और formal संबंधों में यह gap conversion quality और credibility perception को कमजोर कर सकता है",
                ],
                "action": [
                    "email naming को short, clear और identity-consistent रखें; random digits और अनावश्यक separators कम करें",
                    "display name, signature और profile naming को एकरूप रखें ताकि trust signal stable बने",
                ],
            },
            "numerology_personality_profile": {
                "what": [
                    f"आपकी personality profile में Mulank {mulank} की instinct, Bhagyank {bhagyank} की direction और Name {name_number_text} की projection एक साथ काम करती है",
                    "इस संयोजन से आप context-sensitive व्यक्ति दिखते हैं, जो कभी बहुत decisive और कभी बहुत reflective हो सकता है",
                ],
                "why": [
                    "core numbers अलग-अलग behavioral layers को सक्रिय करते हैं; इन्हीं layers का तालमेल आपकी social style और internal processing तय करता है",
                    f"Lo Shu pattern ({present_text}/{missing_text}) इन layers को stabilize या disturb कर सकता है",
                ],
                "impact": [
                    "इसका प्रभाव social readability, self-confidence rhythm और emotional boundary setting पर दिखता है",
                    "जब blind spots active रहते हैं तो व्यक्ति की strengths दिखने के बावजूद consistency perception कम हो सकती है",
                ],
                "action": [
                    "trigger-based self-awareness sheet बनाएं और देखें किस स्थिति में आपका कौन-सा mode activate होता है",
                    "strength-led scheduling करें: high-focus tasks clarity windows में और high-emotion interactions regulated windows में रखें",
                ],
            },
            "current_life_phase_insight": {
                "what": [
                    f"वर्तमान चरण Personal Year {personal_year} से संचालित है और यह phase correction-led progress, structured reset और priority refinement मांगता है",
                    f"अभी की स्थिति में {strongest_metric} support दे रहा है जबकि {weakest_metric} को stabilizing attention चाहिए",
                ],
                "why": [
                    "personal year time-pressure map देता है, जिससे पता चलता है कि किस प्रकार के निर्णय अभी परिणामकारी होंगे",
                    f"core stack और concern '{concern_hint}' का intersection इस phase की urgency और intervention depth तय कर रहा है",
                ],
                "impact": [
                    "phase-aligned actions से progress compounding हो सकती है, जबकि scattered actions से effort leakage बढ़ सकता है",
                    f"यदि correction delay हुआ तो {risk_primary} संकेत decision fatigue और confidence drift में बदल सकते हैं",
                ],
                "action": [
                    "90-day phase board बनाएं: 3 focus outcomes, 3 weekly metrics और 1 non-negotiable routine block",
                    "हर सप्ताह phase-fit review करें और low-value commitments हटाकर execution bandwidth बचाएं",
                ],
            },
            "career_financial_tendencies": {
                "what": [
                    "career layer में आपकी tendency depth, accountability और structured execution की तरफ है, जहां role clarity होने पर output मजबूत रहता है",
                    "financial layer में discipline और timing दोनों महत्वपूर्ण हैं; केवल income potential पर्याप्त नहीं होता",
                ],
                "why": [
                    f"Mulank {mulank} action impulse देता है, Bhagyank {bhagyank} direction देता है और Name {name_number_text} opportunity conversion signal देता है",
                    f"missing digits ({missing_text}) होने पर money routine में inconsistency और delayed follow-through का जोखिम बढ़ता है",
                ],
                "impact": [
                    "career side पर role mismatch होने से motivation drop और decision confusion बढ़ती है",
                    "finance side पर reactive choices savings continuity और long-term stability को कमजोर कर सकती हैं",
                ],
                "action": [
                    "monthly career review रखें: role-fit, output quality, communication value और growth direction का लेखा बनाएं",
                    "money checkpoint protocol लागू करें: essentials, reserves, growth allocation और impulse guardrails चारों तय करें",
                ],
            },
            "relationship_compatibility_patterns": {
                "what": [
                    "रिश्तों में आपका pattern अक्सर emotional pace और communication pace के तालमेल पर निर्भर करता है, न कि केवल intent पर",
                    "जब response timing सही रहती है तो संबंध जल्दी स्थिर होते हैं; timing टूटे तो misunderstanding का loop बनता है",
                ],
                "why": [
                    f"Mulank {mulank} त्वरित प्रतिक्रिया देता है जबकि Bhagyank {bhagyank} गहराई से समझ चाहता है; यही अंतर relational friction का स्रोत बन सकता है",
                    f"compatibility level ({_safe_text(compatibility_level, 'medium')}) और summary ({_safe_text(compatibility_summary, 'balanced signal')}) इस प्रवृत्ति का वर्तमान संदर्भ देते हैं",
                ],
                "impact": [
                    "प्रभाव के रूप में over-explaining, silence blocks, delayed repair या expectation mismatch दिख सकता है",
                    "यदि clarity protocols न हों तो trust building की गति धीमी होती है और emotional fatigue बढ़ती है",
                ],
                "action": [
                    "conflict protocol तय करें: pause, clear statement, listening window, repair action और closure check",
                    "साप्ताहिक relationship review रखें जिसमें unresolved points और appreciation दोनों संतुलित रूप से दर्ज हों",
                ],
            },
            "health_tendencies_from_numbers": {
                "what": [
                    "यह health section non-medical wellness trend बताता है: stress rhythm, sleep discipline, recovery quality और emotional overload risk",
                    f"current profile में {weakest_metric} axis संवेदनशील दिख रहा है, इसलिए recovery planning की जरूरत बढ़ती है",
                ],
                "why": [
                    f"Lo Shu gaps ({missing_text}) और repeating traits ({repeating_text}) stress-processing को uneven बना सकते हैं",
                    "जब decision pressure और emotional load साथ बढ़ते हैं तो nervous system में reset time लंबा हो सकता है",
                ],
                "impact": [
                    "इसका असर fatigue build-up, attention drift, irritability spikes और motivation inconsistency के रूप में दिख सकता है",
                    "routine टूटने पर performance और emotional steadiness दोनों प्रभावित होते हैं",
                ],
                "action": [
                    "daily recovery protocol रखें: breathing reset, movement block, digital shutdown और fixed sleep window",
                    "peak-stress दिनों के लिए backup plan बनाएं ताकि overload को तुरंत stabilize किया जा सके",
                ],
            },
            "personal_year_forecast": {
                "what": [
                    f"Personal Year {personal_year} इस वर्ष की growth theme, decision timing और correction priority को स्पष्ट कर रहा है",
                    "यह वर्ष random expansion की जगह disciplined progress और structure-led gains के लिए उपयुक्त है",
                ],
                "why": [
                    "year vibration जन्मतिथि और वर्तमान वर्ष के गणित से बनती है, इसलिए यह समय-आधारित behavioral pressure को विश्वसनीय रूप से दर्शाती है",
                    "जब actions year-theme aligned होते हैं तो effort-to-result ratio बेहतर रहता है",
                ],
                "impact": [
                    "aligned timing में launches और commitments smoother रहते हैं, misaligned timing में same effort भारी लग सकता है",
                    "year awareness होने से uncertainty कम होती है और decision confidence स्थिर रहता है",
                ],
                "action": [
                    f"महत्वपूर्ण निर्णयों को favorable dates ({lucky_text}) पर schedule करें और पहले readiness checklist पूरी करें",
                    "हर महीने phase review करके non-aligned tasks हटाएं और aligned tasks की intensity बढ़ाएं",
                ],
            },
            "lucky_numbers_favorable_dates": {
                "what": [
                    f"Supportive numbers ({target_text}) और favorable dates ({lucky_text}) आपकी profile के लिए timing accelerators की तरह काम करते हैं",
                    "इनका उपयोग blind belief नहीं बल्कि structured planning utility के रूप में करना चाहिए",
                ],
                "why": [
                    "timing windows core stack और year vibration के resonance से निकाले जाते हैं, इसलिए ये contextual support देते हैं",
                    "aligned dates पर cognitive friction कम होने से focus और completion rate बेहतर होती है",
                ],
                "impact": [
                    "प्रभाव के रूप में key actions में momentum, clarity और stakeholder response quality बढ़ सकती है",
                    "गलत timing में वही कार्य अधिक rework और delay पैदा कर सकता है",
                ],
                "action": [
                    "हर महीने top supportive dates पहले मार्क करें और high-impact tasks उन्हीं windows में रखें",
                    "date alignment के साथ preparation discipline जोड़ें ताकि timing का लाभ वास्तविक परिणाम में बदले",
                ],
            },
            "color_alignment": {
                "what": [
                    "रंग केवल aesthetics नहीं बल्कि mood regulation, focus stability और public projection को प्रभावित करने वाला subtle behavioral lever हैं",
                    f"favorable palette ({_safe_text(favorable_colors, 'neutral supportive tones')}) आपकी profile के लिए balanced signal दे सकती है",
                ],
                "why": [
                    f"core number resonance और dominant planet ({dominant_planet}) color sensitivity पर असर डालते हैं",
                    f"caution palette ({_safe_text(caution_colors, 'high-intensity tones')}) का overuse emotional tone को reactive बना सकता है",
                ],
                "impact": [
                    "सही रंग choices से communication presence और confidence projection सुधरती है",
                    "गलत color environment में fatigue, irritability या distracted mood के संकेत बढ़ सकते हैं",
                ],
                "action": [
                    "workspace, wardrobe और digital profile में consistent color strategy रखें ताकि identity tone coherent रहे",
                    "high-pressure दिनों में calming-supportive palette को प्राथमिकता दें और extreme contrasts सीमित रखें",
                ],
            },
            "remedies_lifestyle_adjustments": {
                "what": [
                    "यह section practical correction protocol देता है जिसमें mantra, habit discipline और lifestyle calibration को एक integrated system की तरह लागू किया जाता है",
                    f"मुख्य उद्देश्य {weakest_metric} stabilization और behavior consistency बनाना है, ताकि long-term drift रुके",
                ],
                "why": [
                    "Remedies तभी प्रभावी होती हैं जब repetition, timing और routine integration के साथ की जाएं",
                    f"आपके pattern में missing cluster और concern '{concern_hint}' दोनों sustained correction मांगते हैं",
                ],
                "impact": [
                    "consistent practice होने पर clarity, emotional regulation और decision steadiness धीरे-धीरे स्थिर होती है",
                    "अनियमित अभ्यास में शुरुआती लाभ टिकते नहीं और पुराना behavior loop लौट सकता है",
                ],
                "action": [
                    f"Mantra routine: {vedic_code}; इसे fixed time पर short but daily discipline के साथ करें",
                    f"Practice stack: {vedic_parameter}; lifestyle anchor: {lifestyle_protocol}; weekly compliance review अनिवार्य रखें",
                ],
            },
            "closing_numerology_guidance": {
                "what": [
                    f"{full_name} की profile correction-ready है; core potential मौजूद है और growth path usable है",
                    f"मुख्य balance point {weakest_metric} stabilization और {strongest_metric} leverage के बीच disciplined coordination है",
                ],
                "why": [
                    "समग्र पैटर्न बताता है कि issue क्षमता की कमी नहीं बल्कि rhythm, timing और consistency misalignment का है",
                    f"core stack, Lo Shu gaps और yearly pressure मिलकर repeat cycles बनाते हैं, जिन्हें process-driven correction से तोड़ा जा सकता है",
                ],
                "impact": [
                    "सही implementation होने पर decision quality, communication trust और execution continuity तीनों में compound सुधार आता है",
                    "यदि correction postpone किया जाए तो वही patterns बार-बार लौटते हैं और effort efficiency गिरती है",
                ],
                "action": [
                    "अगले 30 दिनों के लिए compact execution plan लागू करें: daily anchors, weekly review और monthly consolidation",
                    f"final focus: concern '{concern_hint}' को measurable goals में तोड़ें और हर सप्ताह evidence-based progress validate करें",
                ],
            },
        }
    )

    def _compose_box(section_key: str, slot: str, seeds: Sequence[str]) -> str:
        seed_pool: List[str] = []
        for item in seeds:
            clean = _safe_text(item)
            if clean and clean not in seed_pool:
                seed_pool.append(clean)
        dynamic_pool: List[str] = []
        for item in global_fillers.get(slot, []) + dynamic_fillers.get(slot, []):
            clean = _safe_text(item)
            if clean and clean not in dynamic_pool:
                dynamic_pool.append(clean)
        sentences: List[str] = []
        used = set()

        ordered_seeds = sorted(seed_pool, key=lambda text: _stable_seed(seed, section_key, slot, "seed", text))
        for idx, base in enumerate(ordered_seeds):
            if len(sentences) >= 3:
                break
            pick = _sent(_style_sentence(section_key, slot, base, idx))
            if pick and pick not in used:
                sentences.append(pick)
                used.add(pick)

        ordered_fillers = sorted(dynamic_pool, key=lambda text: _stable_seed(seed, section_key, slot, "fill", text))
        for idx, filler in enumerate(ordered_fillers):
            if not ((len(sentences) < 5 or len(" ".join(sentences)) < 450) and len(sentences) < 7):
                break
            pick = _sent(_style_sentence(section_key, slot, filler, idx + 10))
            if pick and pick not in used:
                sentences.append(pick)
                used.add(pick)

        emergency_pool = ordered_fillers + ordered_seeds
        for idx, filler in enumerate(emergency_pool):
            if not ((len(sentences) < 4 or len(" ".join(sentences)) < 350) and len(sentences) < 7):
                break
            pick = _sent(_style_sentence(section_key, slot, filler, idx + 40))
            if pick and pick not in used:
                sentences.append(pick)
                used.add(pick)

        text = " ".join(sentences)
        return _fit_rich(text, max_chars=700)

    narrative_hooks: Dict[str, List[str]] = {
        "executive_numerology_summary": [
            f"Strength-risk ranking में {strongest_metric} leverage और {weakest_metric} correction दोनों साथ चलाना इस profile के लिए अनिवार्य रहेगा।",
            f"Risk band '{risk_primary}' के भीतर concern '{concern_hint}' को measurable protocol में बदलना executive priority है।",
        ],
        "core_numbers_analysis": [
            f"Core architecture {mulank}/{bhagyank}/{name_number_text} तभी productive बनती है जब decision rhythm और closure rhythm एक ही sequence में चलें।",
            f"यह stack यदि aligned रखा जाए तो {strongest_metric.lower()} को consistent growth asset में बदला जा सकता है।",
        ],
        "name_number_analysis": [
            f"Identity projection layer में Name {name_number_text} और compound {name_compound} की tuning social trust और clarity दोनों पर असर डालती है।",
            f"नाम signal की consistency से public perception और internal confidence के बीच gap कम होता है।",
        ],
        "number_interaction_analysis": [
            f"Interaction layer में harmony-gap profile बताता है कि intent बनाम execution mismatch कहाँ से पैदा हो रहा है।",
            f"यह section व्यवहारिक friction के root node की पहचान देता है, जिससे corrective sequencing आसान होती है।",
        ],
        "remedies_lifestyle_adjustments": [
            f"Correction engine तभी effective होगा जब routine, mantra और behavior audit तीनों calendar-bound cadence में चलें।",
            f"यह section केवल सलाह नहीं बल्कि daily/weekly execution protocol का practical blueprint देता है।",
        ],
        "closing_numerology_guidance": [
            f"Final synthesis दिखाता है कि profile में क्षमता मौजूद है, bottleneck consistency architecture में है।",
            f"Next-step discipline जितनी measurable होगी, उतनी जल्दी {risk_primary} pressure zone से बाहर निकला जा सकेगा।",
        ],
    }

    def _compose_narrative(section_key: str, slots: Dict[str, List[str]]) -> str:
        base_leads = [
            f"{first_name} की {section_key.replace('_', ' ')} reading में profile-specific संकेत स्पष्ट हैं।",
            f"{section_key.replace('_', ' ').title()} layer में core numbers, Lo Shu और current cycle का संयुक्त प्रभाव दिख रहा है।",
            f"यह section {focus_hint} और concern '{concern_hint}' के संदर्भ में actionable clarity देता है।",
        ]
        selected_sentences: List[str] = []
        lead = _pick_variant(seed, section_key, "narrative:lead", base_leads)
        selected_sentences.append(_sent(_style_sentence(section_key, "what", lead, 70)))

        for slot_name in ("what", "why"):
            candidates = [item for item in slots.get(slot_name, []) if _safe_text(item)]
            if not candidates:
                continue
            idx = _stable_seed(seed, section_key, slot_name, "narrative") % len(candidates)
            selected_sentences.append(_sent(_style_sentence(section_key, slot_name, candidates[idx], idx + 80)))

        hooks = narrative_hooks.get(
            section_key,
            [
                f"Risk context '{risk_primary}' और year theme {personal_year} इस section की correction priority को directly influence करते हैं।",
                f"Focused implementation होने पर {strongest_metric.lower()} leverage और {weakest_metric.lower()} stabilization साथ में संभव है।",
            ],
        )
        selected_sentences.append(_sent(_pick_variant(seed, section_key, "narrative:hook", hooks)))
        return _fit_rich(" ".join(item for item in selected_sentences if _safe_text(item)), max_chars=420)

    for section_key, slots in section_lines.items():
        section = basic_payloads.get(section_key)
        if not isinstance(section, dict):
            continue
        section["narrative"] = _compose_narrative(section_key, slots)
        cards = section.get("cards") or []
        if len(cards) < 4:
            continue
        cards[0]["value"] = _compose_box(section_key, "what", slots.get("what", []))
        cards[1]["value"] = _compose_box(section_key, "why", slots.get("why", []))
        cards[2]["value"] = _compose_box(section_key, "impact", slots.get("impact", []))
        cards[3]["value"] = _compose_box(section_key, "action", slots.get("action", []))

    if isinstance(basic_payloads.get("missing_numbers_analysis"), dict):
        basic_payloads["missing_numbers_analysis"]["bullets"] = [
            f"{number}: {BASIC_MISSING_EFFECTS.get(number, {'fix': 'दैनिक correction discipline'})['fix']}"
            for number in list(loshu_missing)[:5]
        ]

    if isinstance(basic_payloads.get("mobile_number_numerology"), dict):
        cards = basic_payloads["mobile_number_numerology"].get("cards") or []
        if len(cards) >= 5:
            cards[4]["value"] = mobile_value or "इनपुट उपलब्ध नहीं"

    if isinstance(basic_payloads.get("email_numerology"), dict):
        cards = basic_payloads["email_numerology"].get("cards") or []
        if len(cards) >= 5:
            cards[4]["value"] = email_value or "इनपुट उपलब्ध नहीं"

    if isinstance(basic_payloads.get("personal_year_forecast"), dict):
        cards = basic_payloads["personal_year_forecast"].get("cards") or []
        if len(cards) >= 6:
            cards[4]["value"] = str(personal_year)
            cards[5]["value"] = lucky_text

    if isinstance(basic_payloads.get("lucky_numbers_favorable_dates"), dict):
        cards = basic_payloads["lucky_numbers_favorable_dates"].get("cards") or []
        if len(cards) >= 6:
            cards[4]["value"] = target_text
            cards[5]["value"] = lucky_text

    if isinstance(basic_payloads.get("remedies_lifestyle_adjustments"), dict):
        basic_payloads["remedies_lifestyle_adjustments"]["bullets"] = [
            f"Mantra: {vedic_code}",
            f"Practice: {vedic_parameter}",
            f"Lifestyle: {lifestyle_protocol}",
        ]

    if isinstance(basic_payloads.get("name_number_analysis"), dict):
        cards = basic_payloads["name_number_analysis"].get("cards") or []
        if len(cards) >= 6:
            cards[4]["value"] = name_number_text
            cards[5]["value"] = target_text

    return basic_payloads


def build_interpretation_report(
    intake_context: Dict[str, Any],
    numerology_core: Dict[str, Any],
    scores: Dict[str, Any],
    archetype: Dict[str, Any],
    remedies: Dict[str, Any],
    plan_name: str = "basic",
) -> Dict[str, Any]:
    intake_context = intake_context or {}
    numerology_core = numerology_core or {}
    scores = scores or {}
    archetype = archetype or {}
    remedies = remedies or {}

    identity = intake_context.get("identity") or {}
    birth_details = intake_context.get("birth_details") or {}
    focus = intake_context.get("focus") or {}
    career = intake_context.get("career") or {}
    contact = intake_context.get("contact") or {}
    preferences = intake_context.get("preferences") or {}

    full_name = _safe_text(identity.get("full_name"), "Strategic Client")
    first_name = full_name.split()[0]
    date_of_birth = _safe_text(birth_details.get("date_of_birth") or identity.get("date_of_birth"))
    day, month, year = _parse_date(date_of_birth)
    current_problem = _safe_text(intake_context.get("current_problem"), "strategic consistency and calibrated growth")

    city = _safe_text(birth_details.get("birthplace_city") or identity.get("city"), "current city")
    career_industry = _safe_text(career.get("industry") or preferences.get("profession"), "strategy and operations")

    pyth = numerology_core.get("pythagorean") or {}
    chaldean = numerology_core.get("chaldean") or {}
    loshu_grid = numerology_core.get("loshu_grid") or {}
    mobile_analysis = numerology_core.get("mobile_analysis") or {}
    email_analysis = numerology_core.get("email_analysis") or {}
    name_correction = numerology_core.get("name_correction") or {}
    business_analysis = numerology_core.get("business_analysis") or {}
    compatibility = numerology_core.get("compatibility") or {}

    life_path = _safe_int(pyth.get("life_path_number"), 0)
    destiny = _safe_int(pyth.get("destiny_number"), 0)
    expression = _safe_int(pyth.get("expression_number"), 0)
    soul_urge = _safe_int(pyth.get("soul_urge_number"), _reduce_number(_alpha_sum(full_name)))
    personality = _safe_int(pyth.get("personality_number"), expression)
    name_number = _safe_int(chaldean.get("name_number"), _safe_int(name_correction.get("current_number"), 0))

    name_compound = _alpha_sum(full_name)
    name_trait = NUMBER_TRAITS.get(name_number or life_path or 5, NUMBER_TRAITS[5])
    name_strength = name_trait["strength"]
    name_risk = name_trait["risk"]

    dominant_planet = _dominant_planet(life_path, destiny, name_number)

    metric_labels = _metric_labels()
    metric_pairs = _metric_order(scores)
    strongest_key, strongest_score = max(metric_pairs, key=lambda item: item[1])
    weakest_key, weakest_score = min(metric_pairs, key=lambda item: item[1])
    strongest_metric = metric_labels[strongest_key]
    weakest_metric = metric_labels[weakest_key]
    risk_band = _risk_band(scores)

    grid_counts = loshu_grid.get("grid_counts") if isinstance(loshu_grid, dict) else {}
    if not isinstance(grid_counts, dict):
        grid_counts = {}
    loshu_present: List[int] = []
    loshu_missing: List[int] = []
    if isinstance(grid_counts, dict) and grid_counts:
        for number in range(1, 10):
            count = _safe_int(grid_counts.get(str(number), grid_counts.get(number, 0)), 0)
            if count > 0:
                loshu_present.append(number)
            else:
                loshu_missing.append(number)
    else:
        loshu_missing = [3, 5, 6]

    override_missing = [_safe_int(value, 0) for value in _safe_list(loshu_grid.get("missing_numbers")) if _safe_int(value, 0)]
    if override_missing:
        loshu_missing = sorted(set(override_missing))
        loshu_present = [number for number in range(1, 10) if number not in loshu_missing]

    primary_missing = loshu_missing[0] if loshu_missing else 0
    structural_cause = (
        f"सबसे कमजोर अक्ष {weakest_metric} पर Lo Shu में digit {primary_missing or 'none'} की कमी और current stress load का संयुक्त प्रभाव है।"
    )
    intervention_focus = (
        f"{weakest_metric.lower()} को rhythm protocol से स्थिर करें, फिर identity corrections को architecture के साथ align करें।"
    )

    metric_cards: List[Dict[str, Any]] = []
    for key, score in metric_pairs:
        label = metric_labels[key]
        metric_cards.append(
            {
                "key": key,
                "label": label,
                "score": score,
                "status": _metric_status(score),
                "meaning": f"{label} का score {score} आपकी deterministic behavior-risk quality को दिखाता है।",
                "risk": "Low score पर pressure के समय execution unstable हो सकता है।",
                "improvement": "Measurable protocol बनाकर weekly review checkpoint जोड़ें।",
            }
        )

    metric_explanations = {
        card["key"]: {
            "label": card["label"],
            "score": card["score"],
            "status": card["status"],
            "meaning": card["meaning"],
            "driver": structural_cause,
            "risk": card["risk"],
            "improvement": card["improvement"],
        }
        for card in metric_cards
    }

    mobile_value = _safe_text(contact.get("mobile_number") or identity.get("mobile_number"))
    mobile_vibration = _safe_int(mobile_analysis.get("mobile_vibration") or mobile_analysis.get("mobile_number_vibration"), _vibration_from_digits(mobile_value))
    mobile_supportive = [_safe_int(value, 0) for value in _safe_list(mobile_analysis.get("supportive_number_energies")) if _safe_int(value, 0)]
    if not mobile_supportive:
        mobile_supportive = [life_path or 1, destiny or 3, 5]
    mobile_compatibility = _safe_text(
        mobile_analysis.get("compatibility_status"),
        "supportive" if mobile_vibration in mobile_supportive else "neutral",
    )
    mobile_summary = _safe_text(
        mobile_analysis.get("compatibility_summary"),
        f"Mobile vibration {mobile_vibration} और profile compatibility {mobile_compatibility} का संयुक्त असर communication tone पर पड़ता है।",
    )

    email_value = _safe_text(identity.get("email"))
    email_vibration = _safe_int(email_analysis.get("email_number"), _vibration_from_text(email_value.split("@")[0] if email_value else ""))

    social_handle = _safe_text(contact.get("social_handle"))
    domain_handle = _safe_text(contact.get("domain_handle"))
    residence_number = _safe_text(contact.get("residence_number"))
    vehicle_number = _safe_text(contact.get("vehicle_number"))
    residence_vibration = _vibration_from_digits(residence_number)
    vehicle_vibration = _vibration_from_digits(vehicle_number)

    business_name = _safe_text(identity.get("business_name"))
    business_number = _safe_int(business_analysis.get("business_number"), _vibration_from_text(business_name))
    business_compound = _safe_int(business_analysis.get("compound_number"), _alpha_sum(business_name))
    business_strength = _safe_text(
        business_analysis.get("business_strength"),
        "Business signal disciplined execution के साथ strategic positioning को support करता है।",
    )
    business_risk = _safe_text(
        business_analysis.get("risk_factor"),
        "Commercial outcome pressure के समय discipline और clarity पर निर्भर करता है।",
    )
    business_industries = [_safe_text(item) for item in _safe_list(business_analysis.get("compatible_industries")) if _safe_text(item)]
    if not business_industries:
        business_industries = [career_industry, "consulting", "digital services"]

    personal_year = _personal_year(day, month)
    lucky_dates = _lucky_dates(day, month, life_path, destiny)
    karmic_numbers = _karmic_numbers(day, name_compound, business_compound)
    hidden_passion_number, hidden_talent_trait = _hidden_passion(loshu_grid, full_name)
    pinnacle = _pinnacle_challenge(day, month, year)

    name_targets = sorted({value for value in [life_path, destiny, expression, 3, 5, 6] if value and value not in {4, 8}})[:4]
    if not name_targets:
        name_targets = [1, 3, 5]
    name_options = _name_options(full_name, name_targets)

    compatibility_summary = _safe_text(
        compatibility.get("relationship_guidance"),
        f"Compatibility उन profiles के साथ strongest होती है जो {strongest_metric.lower()} को reinforce करें और {weakest_metric.lower()} पर pressure कम करें।",
    )

    lifestyle_protocol = "Daily same-time morning anchor, deep-work first block, और evening shutdown checklist follow करें।"
    digital_protocol = "Notification tiering रखें, late-night high-stake decisions avoid करें, और weekly digital detox window रखें।"
    decision_protocol = "High-impact decisions में 24-hour delay rule, written criteria, और weekly assumption audit लागू करें।"
    emotional_protocol = "Key calls से पहले breath reset, fixed sleep window, और post-stress review cadence बनाए रखें।"

    vedic = remedies.get("vedic_remedies") if isinstance(remedies, dict) else {}
    vedic = vedic if isinstance(vedic, dict) else {}
    vedic_code = _safe_text(vedic.get("mantra_pronunciation") or vedic.get("mantra_sanskrit"), "Om Budhaya Namah")
    vedic_parameter = _safe_text(vedic.get("practice_guideline"), "21 days x 108 repetitions fixed time पर")
    vedic_output = _safe_text(vedic.get("recommended_donation"), "Weekly practical donation with clear intention")

    correction_priority_lines = [
        f"{weakest_metric.lower()} को rhythm protocol से स्थिर करें।",
        "Name और mobile vibration alignment optimize करें।",
        "Email और signature authority signal upgrade करें।",
        "अगर high-pressure pattern बना रहे तो residence और vehicle vibration align करें।",
    ]

    payloads: Dict[str, Any] = {}
    payloads["executive_summary"] = _section_payload("executive_summary", f"{full_name} की प्रोफाइल रणनीतिक है, पर correction-sensitive भी है। Risk band {risk_band} दिखाता है कि primary strength {strongest_metric} और primary deficit {weakest_metric} के बीच संतुलन बनाना ज़रूरी है। Core concern: {current_problem}.", f"Strategic potential स्पष्ट है, लेकिन {weakest_metric.lower()} execution में friction ला रहा है।", structural_cause, f"इसका असर {career_industry} में career momentum, financial discipline, और decision quality पर पड़ता है।", intervention_focus, [{"label": "Risk Band", "value": risk_band}, {"label": "Dominant Planet", "value": dominant_planet}])
    payloads["intelligence_metrics"] = {**_section_payload("intelligence_metrics", "Metrics को structural diagnostics की तरह पढ़ना चाहिए।", f"Primary Strength: {strongest_metric}. Primary Deficit: {weakest_metric}.", structural_cause, "Deficit metric volatility बढ़ाता है, जबकि strength metric growth leverage देता है।", intervention_focus, [{"label": "Primary Strength", "value": strongest_metric}, {"label": "Primary Deficit", "value": weakest_metric}, {"label": "Structural Cause", "value": structural_cause}, {"label": "Intervention Focus", "value": intervention_focus}, {"label": "Risk Band", "value": risk_band}]), "metric_cards": metric_cards, "show_chart": True}
    payloads["core_numerology_numbers"] = _section_payload("core_numerology_numbers", f"मूल अंक संरचना: Life Path {life_path}, Destiny {destiny}, Expression {expression}, Soul Urge {soul_urge}, Personality {personality}.", "Core numbers strategic-growth potential दिखाते हैं, लेकिन protocol dependency भी दर्शाते हैं।", "Direction, execution, expression, और projection इस stack से नियंत्रित होते हैं।", "Role-fit, leadership style, और stress response इसी architecture को follow करते हैं।", "Strongest axis leverage करें और weakest behavior loop को patch करें।")
    payloads["name_number_analysis"] = _section_payload("name_number_analysis", f"Current name vibration {name_number}, compound {name_compound} ({_compound_meaning(name_compound)}).", "Name signal is active but partially optimized.", "Name frequency impacts authority and trust perception.", "Mismatch can suppress social clarity and strategic momentum.", "Move toward target-aligned spelling where practical.", [{"label": "Current Name Number", "value": str(name_number)}, {"label": "Strength", "value": name_trait['strength']}, {"label": "Risk", "value": name_trait['risk']}, {"label": "Target Numbers", "value": ', '.join(str(value) for value in name_targets)}], [f"Option {index + 1}: {item['option']} -> {item['number']}" for index, item in enumerate(name_options)])
    payloads["birth_date_numerology"] = _section_payload("birth_date_numerology", f"Birth pattern and personal year {personal_year} define timing quality.", "Birth-date rhythm indicates cycle-based opportunities and caution windows.", "Day, month, and year roots shape recurring behavior cadence.", "Cycle alignment improves clarity and reduces decision friction.", "Schedule major actions in favorable date windows.", [{"label": "Favorable Dates", "value": ', '.join(str(v) for v in lucky_dates)}])
    payloads["loshu_grid_intelligence"] = _section_payload("loshu_grid_intelligence", f"Lo Shu present: {', '.join(str(v) for v in loshu_present) or 'none'} | missing: {', '.join(str(v) for v in loshu_missing) or 'none'}.", "Lo Shu reveals naturally available energies and missing capacities.", "Digit distribution maps communication, discipline, and adaptability.", "Missing center/communication digits can amplify instability.", "Target missing number themes with habit-based correction protocol.")
    payloads["karmic_pattern_intelligence"] = _section_payload("karmic_pattern_intelligence", f"Karmic indicators: {', '.join(str(v) for v in karmic_numbers) if karmic_numbers else 'none explicit'}.", "Karmic numbers indicate recurring lesson loops.", "Date and compound patterns repeat during stress cycles.", "Unresolved loops delay consistency and compounding progress.", "Attach one behavior protocol to each active karmic pattern.")
    payloads["hidden_talent_intelligence"] = _section_payload("hidden_talent_intelligence", f"Hidden Passion number {hidden_passion_number} indicates edge in {hidden_talent_trait}.", "Latent skill axis is visible in number-dominance patterns.", "Core and grid signals create compounding potential.", "When activated, this axis boosts speed and confidence.", "Convert hidden talent into weekly measurable outputs.")
    payloads["personal_year_forecast"] = _section_payload("personal_year_forecast", f"Personal year {personal_year} indicates correction-led growth and consolidation.", f"Current cycle number {personal_year} defines the year theme.", "Personal year derives from birth day/month and current year.", "Cycle awareness improves effort-to-result ratio.", "Use favorable dates for launches and directional decisions.")
    payloads["lucky_numbers_favorable_dates"] = _section_payload("lucky_numbers_favorable_dates", "Lucky logic is scheduling calibration, not superstition.", "Selected numbers and dates show higher profile resonance.", "They align with life-path and destiny rhythm.", "Timing alignment can improve confidence and outcomes.", "Use these windows for high-impact actions.", [{"label": "Lucky Numbers", "value": ', '.join(str(v) for v in name_targets[:4])}, {"label": "Favorable Dates", "value": ', '.join(str(v) for v in lucky_dates)}])
    payloads["basic_remedies"] = _section_payload("basic_remedies", "Basic remedies are behavior anchors designed for consistency.", f"Weakest metric {weakest_metric.lower()} requires stabilization.", "Profile sensitivity increases when routine breaks under stress.", "Instability affects strategic clarity and follow-through.", f"{lifestyle_protocol} | {digital_protocol}", bullets=[f"Mantra code: {vedic_code}", f"Practice: {vedic_parameter}", f"Output: {vedic_output}"])
    payloads["archetype_intelligence"] = _section_payload("archetype_intelligence", f"{first_name} archetype blends {name_strength} with risk of {name_risk}.", "Archetype signature shows strategic upside with discipline dependency.", "Core numbers combine analytical depth and adaptive drive.", "Leadership impact depends on rhythm and message clarity.", name_trait["protocol"])
    payloads["career_intelligence"] = _section_payload("career_intelligence", f"Career alignment {career_industry} में ownership-driven roles के साथ strongest दिखता है।", "Growth curve strategic responsibility और measurable outcomes को favor करता है।", "Life-path और expression alignment depth-based execution को reward करता है।", "Role mismatch होने पर effort तो लगता है, पर compounding नहीं बनती।", "ऐसे roles चुनें जिनमें authority, visibility, और accountability स्पष्ट हो।")
    payloads["financial_intelligence"] = _section_payload("financial_intelligence", f"Financial signal: discipline score {_safe_int(scores.get('financial_discipline_index'), 50)} और protocol-first improvement path।", "Financial behavior correction-ready है, पर structure dependency अधिक है।", "Metric stack stress phase में discipline variance दिखाता है।", "Protocol के बिना growth reactive decisions में leak हो सकती है।", "Budget checkpoints और monthly capital review तुरंत install करें।")
    payloads["numerology_architecture"] = _section_payload("numerology_architecture", f"Architecture: Foundation {life_path}, Left Pillar {destiny}, Right Pillar {expression}, Facade {name_number}.", "Core numbers form a unified structural blueprint.", "Each pillar controls direction, execution, and projection.", "Misalignment appears as confidence drift and inconsistency.", "Align corrections (name/mobile/email) to this architecture.")
    payloads["planetary_influence"] = _section_payload("planetary_influence", f"Primary intervention planet: {dominant_planet}.", "Planetary mapping is calibration lens, not fate prediction.", "Core numbers amplify one intervention channel in current cycle.", "Ignoring it increases friction in decision and emotional domains.", "Anchor routines and remedies to intervention-planet discipline.")
    payloads["compatibility_intelligence"] = _section_payload("compatibility_intelligence", _safe_text(compatibility.get("relationship_guidance"), f"Compatibility strongest with profiles reinforcing {strongest_metric.lower()} and reducing pressure on {weakest_metric.lower()}"), "Compatibility signal highlights support and friction patterns.", "Number resonance influences communication pace and expectation alignment.", "Mismatch can drain energy in personal and business collaborations.", "Prioritize partnerships that reinforce strengths and de-risk deficits.")
    payloads["life_cycle_timeline"] = _section_payload("life_cycle_timeline", "Life cycle timeline maps foundation, expansion, and integration phases.", "Current phase requires correction-led consolidation before aggressive scaling.", "Pinnacle progression and personal-year rhythm indicate sequencing needs.", "Right sequencing improves long-term optionality and stability.", "Plan in three phases: stabilize, optimize, scale.")
    payloads["pinnacle_challenge_cycle_intelligence"] = _section_payload("pinnacle_challenge_cycle_intelligence", f"Pinnacles {pinnacle['pinnacles']} | Challenges {pinnacle['challenges']}.", "Pinnacle cycles define opportunities; challenge cycles define resistance.", "Date-derived reductions map developmental sequence.", "Ignoring challenge signatures repeats avoidable errors.", "Match strategy to active pinnacle and neutralize challenge traits.")
    payloads["strategic_guidance"] = _section_payload("strategic_guidance", "Strategic guidance converts numerology into operating decisions.", "System requires correction-first execution before scale expansion.", f"Risk band {risk_band} and weakest axis {weakest_metric.lower()} require stabilization.", "Correct sequence improves clarity and timing quality.", "Run correction stack: behavior -> identity -> timing -> scale.")
    payloads["name_vibration_optimization"] = _section_payload("name_vibration_optimization", f"Current name number {name_number}, compound {name_compound} ({_compound_meaning(name_compound)}).", "Name vibration is active but partially optimized for strategic goals.", "Name frequency encodes authority and trust signal.", "Suboptimal signal can reduce conversion quality and momentum.", "Adopt target-aligned variants where commercial context justifies.", [{"label": "Current Number", "value": str(name_number)}, {"label": "Target Numbers", "value": ', '.join(str(v) for v in name_targets)}, {"label": "Strength", "value": name_trait['strength']}, {"label": "Risk", "value": name_trait['risk']}], [f"Option {index + 1}: {item['option']} -> {item['number']}" for index, item in enumerate(name_options)])
    payloads["mobile_number_intelligence"] = _section_payload("mobile_number_intelligence", mobile_summary, f"Current mobile vibration {mobile_vibration} with {mobile_compatibility} compatibility.", "Mobile frequency influences communication and response cadence.", "Misalignment may increase noise or decision fatigue.", "Shift to supportive ending patterns when feasible.", [{"label": "Current Mobile", "value": mobile_value or 'Not provided'}, {"label": "Target Vibrations", "value": ', '.join(str(v) for v in mobile_supportive[:4])}, {"label": "Ending Logic", "value": "Prefer final digits matching supportive triad"}])
    payloads["email_identity_intelligence"] = _section_payload("email_identity_intelligence", f"Current email vibration {email_vibration} shapes digital authority signal.", "Digital identity is active but can be optimized for trust and visibility.", "Email local-part vibration affects first-impression coding.", "Weak signal can lower credibility and response quality.", "Use cleaner naming pattern aligned with target profile numbers.", [{"label": "Current Email", "value": email_value or 'Not provided'}, {"label": "Email Vibration", "value": str(email_vibration or 0)}, {"label": "Authority Signal", "value": 'High' if email_vibration in {1, 8, 9, 22} else 'Moderate'}], [f"Suggested pattern: {pattern}" for pattern in _handle_patterns(first_name, name_targets)])
    payloads["signature_intelligence"] = _section_payload("signature_intelligence", "Signature energy should communicate authority with controlled flow and completion.", "Current signature behavior can be optimized for growth alignment.", "Stroke structure encodes confidence and decision intent.", "Weak structure can dilute authority signal.", "Use rising start, stable midline, and forward closure stroke.", [{"label": "Starting Stroke", "value": "Begin upward, avoid backward hooks"}, {"label": "Ending Stroke", "value": "Close forward-right with complete finish"}, {"label": "Authority Alignment", "value": 'High' if name_number in {1, 8, 9, 22} else 'Moderate'}])
    payloads["business_name_intelligence"] = _section_payload("business_name_intelligence", f"Business vibration {business_number or 0}, compound {business_compound or 0}, signal: {business_strength}.", "Business name signal affects commercial trust and positioning.", "Brand vibration influences category fit and conversion texture.", "Misalignment can reduce pricing power and authority velocity.", "Adjust naming pattern toward target commercial numbers when required.", [{"label": "Business Name", "value": business_name or 'Not provided'}, {"label": "Industry Fit", "value": ', '.join(business_industries[:3])}, {"label": "Risk", "value": business_risk}])

    handle_source = domain_handle or social_handle or first_name
    handle_vibration = _vibration_from_text(handle_source)
    payloads["brand_handle_optimization"] = _section_payload("brand_handle_optimization", f"Current handle/domain vibration {handle_vibration or 0} should align with visibility strategy.", "Public handle signal can be optimized for trust and discoverability.", "Handle vibration influences memorability and social proof perception.", "Weak naming logic lowers visibility consistency.", "Unify handle/domain root with target vibration endings.", [{"label": "Social Handle", "value": social_handle or 'Not provided'}, {"label": "Domain Handle", "value": domain_handle or 'Not provided'}, {"label": "Authority Signal", "value": 'High' if handle_vibration in {1, 8, 9, 22} else 'Moderate'}], [f"Improved pattern: {pattern}" for pattern in _handle_patterns(handle_source, name_targets)])
    payloads["residence_energy_intelligence"] = _section_payload("residence_energy_intelligence", f"Residence vibration {residence_vibration or 0} affects baseline stability signal.", "Home number creates recurring environmental energy tone.", "Repeated daily exposure amplifies behavior feedback.", "Misfit vibration can reduce recovery quality and clarity.", "Apply symbolic balancing with plate letters and entrance corrections.", [{"label": "Current Residence Number", "value": residence_number or 'Not provided'}, {"label": "Residence Vibration", "value": str(residence_vibration or 0)}])
    payloads["vehicle_number_intelligence"] = _section_payload("vehicle_number_intelligence", f"Vehicle vibration {vehicle_vibration or 0} influences movement tone and confidence expression.", "Vehicle number creates recurring movement-state signal.", "Travel frequency amplifies vibration feedback into transitions.", "Misalignment may increase urgency bias and reactive behavior.", "Prefer compatible number logic during selection or correction.", [{"label": "Current Vehicle Number", "value": vehicle_number or 'Not provided'}, {"label": "Vehicle Vibration", "value": str(vehicle_vibration or 0)}])
    payloads["lifestyle_alignment"] = _section_payload("lifestyle_alignment", "Lifestyle alignment strategic infrastructure है, सिर्फ wellness filler नहीं।", f"Weakest metric {weakest_metric.lower()} को rhythm-led stabilization चाहिए।", "Routine disruption cognitive noise और volatility बढ़ाता है।", "यह instability clarity, discipline, और execution quality को प्रभावित करती है।", lifestyle_protocol)
    payloads["digital_discipline"] = _section_payload("digital_discipline", "Digital behavior सीधे decision quality और recovery को shape करता है।", "Notification overload एक hidden performance drain है।", "High-frequency context switching deficit metrics को amplify करता है।", "इसके बाद reactive decisions और deep-work quality में गिरावट दिखती है।", digital_protocol)
    payloads["vedic_remedy"] = _section_payload("vedic_remedy", "Vedic protocol is focus-conditioning and discipline anchor.", "Current profile benefits from ritualized consistency loops.", "Weakest metric and dominant planet point to intervention need.", "Improves composure and timing discipline.", f"Code: {vedic_code} | Parameter: {vedic_parameter}", [{"label": "Focus", "value": weakest_metric}, {"label": "Code", "value": vedic_code}, {"label": "Parameter", "value": vedic_parameter}, {"label": "Output", "value": vedic_output}])
    payloads["correction_protocol_summary"] = _section_payload("correction_protocol_summary", "Correction protocol ranks interventions by impact on stability and monetizable outcomes.", "Multiple correction levers exist and must be sequenced.", "Weakest metric and identity-signal gaps define order.", "Correct sequencing improves measurable improvement speed.", "Execute 21-day and 90-day checkpoints with priority order.", [{"label": "Top Priority", "value": correction_priority_lines[0]}, {"label": "High-Impact Quick Fixes", "value": ' | '.join(correction_priority_lines[:2])}, {"label": "Medium-Term Adjustments", "value": "Email identity, signature protocol, environment alignment"}, {"label": "Premium Advisory", "value": "Run full correction audit quarterly"}], correction_priority_lines)
    payloads["business_intelligence"] = _section_payload("business_intelligence", f"Business signal: {business_strength}. Risk gate: {business_risk}.", "Commercial upside exists with correction-led governance discipline.", "Business vibration and metric stack indicate potential with pressure constraints.", "Without structure, growth can convert into volatility.", "Align offer, pricing, and positioning to cycle window.")
    payloads["wealth_energy_blueprint"] = _section_payload("wealth_energy_blueprint", f"Wealth blueprint: financial discipline {_safe_int(scores.get('financial_discipline_index'), 50)} with business vibration {business_number or 'N/A'}.", "Wealth path depends on behavior architecture.", "Financial metric and identity signals define compounding quality.", "Protocol failure causes leak in high-income phases.", "Use monthly capital governance and staged risk model.")
    payloads["decision_intelligence"] = _section_payload("decision_intelligence", "Decision intelligence को filters, delay rules, और review loops से engineer किया जाता है।", "Current profile में capability है, पर stress phase inconsistency भी है।", f"Weakest metric {weakest_metric.lower()} high load में decision noise बढ़ाता है।", "Fast और unfiltered calls opportunity cost बढ़ाती हैं।", decision_protocol)
    payloads["emotional_intelligence"] = _section_payload("emotional_intelligence", "Emotional regulation strategic performance infrastructure का core हिस्सा है।", "Recovery speed एक variable risk factor की तरह काम करती है।", "Metric pattern बताता है कि rhythm टूटने पर reactive windows बढ़ती हैं।", "इसका प्रभाव clarity, relationships, और financial discipline पर पड़ता है।", emotional_protocol)
    payloads["leadership_intelligence"] = _section_payload("leadership_intelligence", "Leadership signal should combine authority with stable execution cadence.", "Leadership potential is high but governance rhythm is mandatory.", "Core numbers indicate strategic strength with overextension risk.", "Inconsistent cadence reduces trust and execution velocity.", "Weekly leadership protocol: priorities, delegation, review, recovery.")
    payloads["strategic_timing_intelligence"] = _section_payload("strategic_timing_intelligence", "Timing intelligence calibrates when to push, pause, and consolidate.", "Decision quality varies by cycle windows and date resonance.", "Personal-year and pinnacle sequences define timing intensity.", "Poor timing increases effort with lower conversion.", "Use favorable dates for launches and negotiations.", [{"label": "Current Personal Year", "value": str(personal_year)}, {"label": "Favorable Dates", "value": ', '.join(str(v) for v in lucky_dates)}])
    payloads["growth_blueprint"] = _section_payload("growth_blueprint", "Growth blueprint sequences stabilize -> optimize -> scale.", "Current phase is correction-led stabilization before aggressive expansion.", f"Risk band {risk_band} requires structural readiness before scale.", "Premature expansion can lock volatility into operations.", "Run staged roadmap with gate checks across 90 days.")
    payloads["strategic_execution_roadmap"] = _section_payload("strategic_execution_roadmap", "Execution roadmap converts intelligence into a 90-day operating system.", "Multiple interventions need coordinated sequencing.", "Correction outcomes compound only in operational order.", "Unsequenced action wastes effort and obscures ROI.", "Days 1-30 stabilize, 31-60 optimize, 61-90 scale tests.", bullets=["Days 1-30: metric deficit stabilization and behavior lock.", "Days 31-60: identity corrections (name/mobile/email/signature).", "Days 61-90: timing alignment and controlled scale tests."])
    payloads["closing_synthesis"] = _section_payload("closing_synthesis", f"Final synthesis: {full_name} में clear leverage potential है, यदि correction priorities को disciplined execution के साथ चलाया जाए।", "Profile calibration-sensitive है, fundamentally blocked नहीं।", "Strength-deficit architecture स्पष्ट है और सही sequence से correct की जा सकती है।", "Protocol-led execution constraints को strategic advantage में बदल सकता है।", "Correction stack, timing control, और quarterly recalibration पर committed रहें।")

    if plan_name == "basic":
        mulank = _reduce_number(day)
        bhagyank = life_path or _reduce_number(day + month + _reduce_number(year))
        interaction_gap = abs((mulank or 0) - (bhagyank or 0))
        interaction_state = "संतुलित" if interaction_gap <= 2 else "विरोधी संकेत"
        repeating_numbers = [
            number
            for number in range(1, 10)
            if _safe_int(grid_counts.get(str(number), grid_counts.get(number, 0)), 0) > 1
        ]
        repeating_text = ", ".join(str(number) for number in repeating_numbers) if repeating_numbers else "कोई प्रमुख पुनरावृत्ति नहीं"
        mobile_classification = "supportive" if mobile_vibration in {mulank, bhagyank, destiny} else "neutral"
        email_available = bool(email_value)
        color_base = (name_number or bhagyank or mulank or 5)
        color_map = {
            1: ("gold, saffron", "dark grey"),
            2: ("white, silver", "muddy brown"),
            3: ("yellow, honey", "dull black"),
            4: ("smoky blue, graphite", "neon red"),
            5: ("green, mint", "overly dark maroon"),
            6: ("cream, rose", "charcoal black"),
            7: ("sea green, turquoise", "rust orange"),
            8: ("navy, steel blue", "faded yellow"),
            9: ("maroon, crimson", "pale grey"),
        }
        favorable_colors, caution_colors = color_map.get(color_base, ("green, blue", "muddy grey"))
        mulank_trait = NUMBER_TRAITS.get(mulank, NUMBER_TRAITS[5])
        bhagyank_trait = NUMBER_TRAITS.get(bhagyank, NUMBER_TRAITS[5])
        focus_key = _safe_text((intake_context.get("focus") or {}).get("life_focus"), "general_alignment")
        focus_text = focus_key.replace("_", " ")
        city_hint = _safe_text(birth_details.get("birthplace_city") or identity.get("city"), "local environment")
        compatibility_level = _safe_text((numerology_core.get("compatibility") or {}).get("compatibility_level"), "Moderate")

        basic_payloads: Dict[str, Any] = {}
        basic_payloads["executive_numerology_summary"] = _section_payload(
            "executive_numerology_summary",
            f"{full_name} की numerology profile का मूल स्वर {mulank}-{bhagyank}-{name_number or '-'} संयोजन पर आधारित है। मुख्य ताकत {strongest_metric} और चुनौती {weakest_metric} है। वर्तमान focus: {focus_text}.",
            "Core number stack से quick nature signal स्पष्ट है।",
            "मूलांक, भाग्यांक और नामांक का संयुक्त प्रभाव baseline behavior तय करता है।",
            f"इसका असर निर्णय, संबंध, दिनचर्या और execution consistency पर पड़ता है, खासकर {city_hint} जैसे environment में।",
            f"पहली correction priority: {weakest_metric.lower()} stabilization और missing number discipline।",
        )
        basic_payloads["core_numbers_analysis"] = _section_payload(
            "core_numbers_analysis",
            f"Mulank {mulank}, Bhagyank {bhagyank}, Destiny {destiny}, Expression {expression}.",
            "ये चार संख्या आपकी आधार संरचना दिखाती हैं।",
            "जन्मतिथि और नाम vibration से ये numbers deterministic तरीके से निकलते हैं।",
            "व्यक्तित्व, अवसर और चुनौतियों का मुख्य pattern यही तय करता है।",
            "हर weekly review में इन numbers के basis पर self-observation करें।",
        )
        basic_payloads["name_number_analysis"] = _section_payload(
            "name_number_analysis",
            f"नामांक {name_number} और compound {name_compound} आपके पहचान संकेत को प्रभावित करते हैं।",
            "नाम संख्या आपके social impression और communication tone को दर्शाती है।",
            "अक्षर-वाइब्रेशन से बना total आपकी पहचान की स्थिरता और trust signal तय करता है।",
            "नाम और मूलांक/भाग्यांक में mismatch होने पर clarity और confidence प्रभावित हो सकते हैं।",
            "नाम उपयोग में consistency रखें और practical होने पर target-friendly spelling अपनाएं।",
            [
                {"label": "Current Name Number", "value": str(name_number)},
                {"label": "Strength", "value": name_trait["strength"]},
                {"label": "Risk", "value": name_trait["risk"]},
            ],
            [f"विकल्प {index + 1}: {item['option']} -> {item['number']}" for index, item in enumerate(name_options)],
        )
        basic_payloads["mulank_description"] = _section_payload(
            "mulank_description",
            f"Mulank {mulank} आपकी instinctive response style और daily behavior tone को दर्शाता है। यह {mulank_trait['strength']} को बढ़ाता है और {mulank_trait['risk']} tendency दिखा सकता है।",
            "मूलांक आपकी natural प्रतिक्रिया और प्राथमिकता pattern दिखाता है।",
            "दिनांक जन्म का root number सीधे personality reflexes से जुड़ता है।",
            "Strengths और blind spots दैनिक फैसलों में बार-बार दिखते हैं।",
            "मूलांक strength को routine में उपयोग करें और weakness पर habit correction लगाएं।",
        )
        basic_payloads["bhagyank_description"] = _section_payload(
            "bhagyank_description",
            f"Bhagyank {bhagyank} life path theme, growth direction और recurring lesson cycle को define करता है। इसका core strength {bhagyank_trait['strength']} है।",
            "भाग्यांक long-term direction और opportunity flow का संकेत देता है।",
            "पूरा जन्मांक योग (life path) से destiny pattern निकलता है।",
            f"गलत timing या discipline gap होने पर growth धीमी हो सकती है और {bhagyank_trait['risk']} बढ़ सकता है।",
            f"व्यक्तिगत वर्ष {personal_year} और भाग्यांक को जोड़कर yearly focus तय करें।",
        )
        basic_payloads["number_interaction_analysis"] = _section_payload(
            "number_interaction_analysis",
            f"Mulank {mulank}, Bhagyank {bhagyank}, Name Number {name_number or '-'} के बीच {interaction_state} pattern दिखाई देता है (gap {interaction_gap}).",
            "Numbers में harmony या conflict execution style बदलता है।",
            "जब root numbers दूर होते हैं तो behavior में friction बढ़ता है।",
            "फोकस, confidence और consistency पर सीधा प्रभाव पड़ता है।",
            "अगर conflict है तो routine, mantra और number-aligned habit से correction करें।",
        )
        basic_payloads["loshu_grid_interpretation"] = _section_payload(
            "loshu_grid_interpretation",
            f"Lo Shu present: {', '.join(str(v) for v in loshu_present) or 'none'} | missing: {', '.join(str(v) for v in loshu_missing) or 'none'}.",
            "Lo Shu grid ऊर्जा layout को practical रूप से दिखाता है।",
            "जन्मांक digit distribution से present और missing energies निकलती हैं।",
            "Present numbers natural strengths और missing numbers correction areas बताते हैं।",
            "Grid reading को weekly behavior tracking से validate करें।",
        )
        basic_payloads["missing_numbers_analysis"] = _section_payload(
            "missing_numbers_analysis",
            f"Missing numbers: {', '.join(str(v) for v in loshu_missing) if loshu_missing else 'none'}.",
            "Missing numbers संभावित behavior gaps को दिखाते हैं।",
            "इन digits की कमी communication, flexibility या discipline gaps में दिख सकती है।",
            "गैप untreated रहे तो repeat friction बनता है।",
            "हर missing digit के लिए एक micro-habit correction निर्धारित करें।",
            [f"Missing {number}: structured correction routine आवश्यक." for number in loshu_missing[:5]],
        )
        basic_payloads["repeating_numbers_impact"] = _section_payload(
            "repeating_numbers_impact",
            f"Repeating numbers pattern: {repeating_text}.",
            "Repeated digits amplified traits दिखाते हैं।",
            "एक ही digit का बार-बार आना excess tendency को मजबूत करता है।",
            "Overuse होने पर rigidity, impulsivity या overthinking उभर सकता है।",
            "Amplified trait को balance करने के लिए opposite habit anchor जोड़ें।",
        )
        basic_payloads["mobile_number_numerology"] = _section_payload(
            "mobile_number_numerology",
            f"Mobile vibration {mobile_vibration} का classification: {mobile_classification}.",
            "मोबाइल vibration daily communication tone को प्रभावित करता है।",
            "Digit sum vibration profile numbers के साथ resonance बनाता या घटाता है।",
            "Conflicting vibration होने पर distraction और clarity drop हो सकती है।",
            "Supportive ending pattern चुनें और usage discipline maintain रखें।",
            [{"label": "Current Mobile", "value": mobile_value or "इनपुट उपलब्ध नहीं"}],
        )
        basic_payloads["mobile_life_number_compatibility"] = _section_payload(
            "mobile_life_number_compatibility",
            f"Mobile vibration {mobile_vibration} बनाम life numbers {mulank}/{bhagyank}: {mobile_classification}.",
            "यह सेक्शन mobile और life-number relationship को simple तरीके से पढ़ता है।",
            "Compatibility resonance जितनी बेहतर होगी, communication clarity उतनी smooth रहती है।",
            "Mismatch होने पर response fatigue या decision delay बढ़ सकता है।",
            "यदि mismatch है तो अगली SIM update में supportive digit logic चुनें।",
        )
        basic_payloads["email_numerology"] = _section_payload(
            "email_numerology",
            f"Email vibration {email_vibration or 0} trust, clarity और digital identity signal को प्रभावित करता है।" if email_available else "ईमेल इनपुट उपलब्ध नहीं है, इसलिए अभी detailed email numerology analysis सीमित है।",
            "Email local-part भी एक numerology identity layer मानी जाती है।",
            "Vibration authority perception और response quality पर प्रभाव डालती है।",
            "Weak pattern होने पर digital signal dilute हो सकता है।",
            "Email उपलब्ध होने पर clean pattern के साथ optimized सुझाव generate करें।",
            [{"label": "Current Email", "value": email_value or "इनपुट उपलब्ध नहीं"}],
        )
        basic_payloads["numerology_personality_profile"] = _section_payload(
            "numerology_personality_profile",
            f"Personality profile में {name_strength} प्रमुख है, जबकि {name_risk} internal blind spot की तरह दिखता है।",
            "Numbers social style, inner nature और reaction pattern को summarize करते हैं।",
            "Mulank + Name Number का मिश्रण interpersonal tone तय करता है।",
            "Blind spots unmanaged रहें तो relationship और confidence दोनों प्रभावित होते हैं।",
            "Strength-driven behavior रखें और blind spot पर conscious pause rule लगाएं।",
        )
        basic_payloads["current_life_phase_insight"] = _section_payload(
            "current_life_phase_insight",
            f"Current life phase theme: personal year {personal_year} और risk band {risk_band}.",
            "यह phase correction-led stabilization और clarity building का संकेत देता है।",
            "Personal year और number interaction इस समय की priority तय करते हैं।",
            "Wrong focus चुनने पर effort high और output low रह सकता है।",
            "इस phase में consistency, timing और disciplined decisions पर फोकस रखें।",
        )
        basic_payloads["career_financial_tendencies"] = _section_payload(
            "career_financial_tendencies",
            f"Career tendency {career_industry} orientation के साथ और financial discipline score {_safe_int(scores.get('financial_discipline_index'), 50)} के आसपास है। यह {focus_text} लक्ष्य के लिए उपयोगी संकेत देता है।",
            "यह section केवल numerology-based tendencies बताता है, consulting strategy नहीं।",
            "Work style, routine discipline और number resonance earning pattern को shape करते हैं।",
            "Reactive style होने पर income consistency प्रभावित हो सकती है।",
            "Skill depth, role-fit और money routine पर steady focus रखें।",
        )
        basic_payloads["relationship_compatibility_patterns"] = _section_payload(
            "relationship_compatibility_patterns",
            f"{compatibility_summary} Current compatibility level: {compatibility_level}.",
            "Relationship pattern में emotional style और number resonance दोनों काम करते हैं।",
            "Compatibility tendency communication pace और expectation alignment से बनती है।",
            "Mismatch होने पर repeated misunderstanding cycle बन सकता है।",
            "Clear boundaries, calm communication और timing awareness रखें।",
        )
        basic_payloads["health_tendencies_from_numbers"] = _section_payload(
            "health_tendencies_from_numbers",
            f"Emotional regulation score {_safe_int(scores.get('emotional_regulation_index'), 50)} और karma pressure {_safe_int(scores.get('karma_pressure_index'), 50)} stress tendency की दिशा दिखाते हैं। सबसे संवेदनशील axis: {weakest_metric}.",
            "यह numerology-based wellness tendency है, medical diagnosis नहीं।",
            "Number imbalance sleep rhythm, stress response और recovery pattern प्रभावित कर सकता है।",
            "अवहेलना करने पर fatigue और decision quality दोनों गिर सकते हैं।",
            "Breath reset, sleep discipline और low-noise routine अपनाएं।",
        )
        basic_payloads["personal_year_forecast"] = _section_payload(
            "personal_year_forecast",
            f"वर्तमान personal year {personal_year} इस वर्ष की गति और प्राथमिकता तय करता है।",
            f"Year {personal_year} में focus theme correction + consistency है।",
            "Personal year जन्म दिन, माह और वर्तमान वर्ष के योग से बनता है।",
            "सही timing चुनने पर effort का परिणाम बेहतर मिलता है।",
            "महत्वपूर्ण decisions और launches को favorable date windows में रखें।",
            [
                {"label": "Current Personal Year", "value": str(personal_year)},
                {"label": "Favorable Dates", "value": ", ".join(str(v) for v in lucky_dates)},
            ],
        )
        basic_payloads["lucky_numbers_favorable_dates"] = _section_payload(
            "lucky_numbers_favorable_dates",
            f"Supportive numbers: {', '.join(str(v) for v in name_targets[:4]) or '3, 5, 9'} | favorable dates: {', '.join(str(v) for v in lucky_dates)}.",
            "यह superstition नहीं, बल्कि numerology timing utility है।",
            "मूलांक, भाग्यांक और नामांक resonance से कुछ तिथियां अधिक supportive रहती हैं।",
            "गलत timing में वही प्रयास धीमा या थकाऊ लग सकता है।",
            "महत्वपूर्ण meeting, outreach और नई शुरुआत supportive dates पर करें।",
            [
                {"label": "Lucky Numbers", "value": ", ".join(str(v) for v in name_targets[:4]) or "3, 5, 9"},
                {"label": "Favorable Dates", "value": ", ".join(str(v) for v in lucky_dates)},
            ],
        )
        basic_payloads["color_alignment"] = _section_payload(
            "color_alignment",
            f"Favorable colors: {favorable_colors}. Caution colors: {caution_colors}.",
            "Color alignment numerology support layer की तरह काम करती है।",
            "Dominant number vibration से aligned tones focus और steadiness बढ़ा सकते हैं।",
            "Mismatched color overuse से energy tone dull हो सकती है।",
            "Primary wardrobe/workspace में favorable tones का controlled use करें।",
        )
        basic_payloads["remedies_lifestyle_adjustments"] = _section_payload(
            "remedies_lifestyle_adjustments",
            f"Basic correction layer = simple mantra + disciplined habit + lifestyle alignment. Dominant planet support: {dominant_planet}.",
            "Remedies को practical routine के साथ जोड़ना सबसे प्रभावी रहता है।",
            "Consistency के बिना remedy signal कमजोर हो जाता है।",
            "Irregular practice से correction outcome धीमा पड़ता है।",
            "Daily short mantra, fixed routine, और weekly review रखें।",
            [
                f"Mantra: {vedic_code}",
                f"Practice: {vedic_parameter}",
                f"Lifestyle: {lifestyle_protocol}",
            ],
        )
        basic_payloads["closing_numerology_guidance"] = _section_payload(
            "closing_numerology_guidance",
            f"Main life theme: {bhagyank} path refinement with {mulank} day-expression and name signal {name_number}. Primary correction: {weakest_metric}.",
            "आपकी numerology profile workable और correctable है।",
            "Core numbers, Lo Shu gaps और daily habits का जोड़ final outcome तय करता है।",
            "Correction priority ignore करने पर repeat cycle बन सकता है।",
            "Next best step: 21-day correction routine + monthly numerology review.",
        )

        basic_payloads = _personalize_basic_payloads(
            basic_payloads,
            full_name=full_name,
            first_name=first_name,
            date_of_birth=date_of_birth,
            current_problem=current_problem,
            city_hint=city_hint,
            focus_text=focus_text,
            mulank=mulank,
            bhagyank=bhagyank,
            life_path=life_path,
            destiny=destiny,
            expression=expression,
            name_number=name_number,
            name_compound=name_compound,
            personal_year=personal_year,
            strongest_metric=strongest_metric,
            weakest_metric=weakest_metric,
            risk_band=risk_band,
            loshu_present=loshu_present,
            loshu_missing=loshu_missing,
            repeating_numbers=repeating_numbers,
            mobile_vibration=mobile_vibration,
            mobile_classification=mobile_classification,
            mobile_value=mobile_value,
            email_value=email_value,
            email_vibration=email_vibration,
            compatibility_summary=compatibility_summary,
            compatibility_level=compatibility_level,
            career_industry=career_industry,
            lucky_dates=lucky_dates,
            name_targets=name_targets,
            favorable_colors=favorable_colors,
            caution_colors=caution_colors,
            dominant_planet=dominant_planet,
            vedic_code=vedic_code,
            vedic_parameter=vedic_parameter,
            lifestyle_protocol=lifestyle_protocol,
            name_options=name_options,
        )

        basic_payloads = _enrich_basic_payloads(
            basic_payloads,
            full_name=full_name,
            first_name=first_name,
            city_hint=city_hint,
            focus_text=focus_text,
            current_problem=current_problem,
            mulank=mulank,
            bhagyank=bhagyank,
            life_path=life_path,
            destiny=destiny,
            expression=expression,
            name_number=name_number,
            name_compound=name_compound,
            loshu_present=loshu_present,
            loshu_missing=loshu_missing,
            repeating_numbers=repeating_numbers,
            mobile_vibration=mobile_vibration,
            mobile_classification=mobile_classification,
            mobile_value=mobile_value,
            email_value=email_value,
            email_vibration=email_vibration,
            compatibility_summary=compatibility_summary,
            compatibility_level=compatibility_level,
            personal_year=personal_year,
            strongest_metric=strongest_metric,
            weakest_metric=weakest_metric,
            risk_band=risk_band,
            lucky_dates=lucky_dates,
            target_numbers=name_targets,
            favorable_colors=favorable_colors,
            caution_colors=caution_colors,
            dominant_planet=dominant_planet,
            vedic_code=vedic_code,
            vedic_parameter=vedic_parameter,
            lifestyle_protocol=lifestyle_protocol,
        )

        payloads.update(basic_payloads)

        # Backward-compatible aliases consumed by current template/context layers.
        payloads["executive_summary"] = basic_payloads["executive_numerology_summary"]
        payloads["core_numerology_numbers"] = basic_payloads["core_numbers_analysis"]
        payloads["birth_date_numerology"] = basic_payloads["current_life_phase_insight"]
        payloads["loshu_grid_intelligence"] = basic_payloads["loshu_grid_interpretation"]
        payloads["mobile_number_intelligence"] = basic_payloads["mobile_number_numerology"]
        payloads["email_identity_intelligence"] = basic_payloads["email_numerology"]
        payloads["archetype_intelligence"] = basic_payloads["numerology_personality_profile"]
        payloads["career_intelligence"] = basic_payloads["career_financial_tendencies"]
        payloads["financial_intelligence"] = basic_payloads["career_financial_tendencies"]
        payloads["decision_intelligence"] = basic_payloads["number_interaction_analysis"]
        payloads["emotional_intelligence"] = basic_payloads["health_tendencies_from_numbers"]
        payloads["compatibility_intelligence"] = basic_payloads["relationship_compatibility_patterns"]
        payloads["lifestyle_alignment"] = basic_payloads["remedies_lifestyle_adjustments"]
        payloads["basic_remedies"] = basic_payloads["remedies_lifestyle_adjustments"]
        payloads["closing_synthesis"] = basic_payloads["closing_numerology_guidance"]

    payloads = _ensure_all_payloads(plan_name, payloads)
    payloads = _localize_payloads(payloads)

    profile_executive = _build_profile_driven_executive_brief(
        full_name=full_name,
        first_name=first_name,
        city_hint=city,
        focus_text=_safe_text(focus.get("life_focus"), "general_alignment"),
        current_problem=current_problem,
        mulank=mulank,
        bhagyank=bhagyank,
        life_path=life_path,
        destiny=destiny,
        expression=expression,
        name_number=name_number,
        personal_year=personal_year,
        loshu_missing=loshu_missing,
        repeating_numbers=repeating_numbers,
        strongest_metric=strongest_metric,
        strongest_score=strongest_score,
        weakest_metric=weakest_metric,
        weakest_score=weakest_score,
        risk_band=risk_band,
        mobile_vibration=mobile_vibration,
        mobile_classification=mobile_classification,
        email_vibration=email_vibration,
        compatibility_level=compatibility_level,
    )
    structural_cause = profile_executive.get("structural_cause") or structural_cause
    intervention_focus = profile_executive.get("intervention_focus") or intervention_focus

    primary_insight = {
        "core_archetype": _safe_text(archetype.get("archetype_name"), "रणनीतिक अनुकूल archetype"),
        "strength": profile_executive.get("primary_strength") or f"Primary strength axis: {strongest_metric}",
        "critical_deficit": profile_executive.get("primary_deficit") or f"Primary deficit axis: {weakest_metric}",
        "stability_risk": risk_band,
        "phase_1_diagnostic": "Phase 1: deficit triggers diagnose करके baseline behaviors lock करें।",
        "phase_2_blueprint": "Phase 2: architecture-aligned identity corrections deploy करें।",
        "phase_3_intervention_protocol": "Phase 3: 90-day timing-calibrated execution protocol चलाएं।",
        "narrative": profile_executive.get("summary") or payloads["executive_summary"]["narrative"],
    }

    executive_brief = {
        "summary": profile_executive.get("summary") or payloads["executive_summary"]["narrative"],
        "key_strength": profile_executive.get("key_strength") or primary_insight["strength"],
        "key_risk": profile_executive.get("key_risk") or primary_insight["critical_deficit"],
        "strategic_focus": profile_executive.get("strategic_focus") or intervention_focus,
    }

    analysis_sections = {
        "career_analysis": payloads["career_intelligence"]["narrative"],
        "decision_profile": payloads["decision_intelligence"]["narrative"],
        "emotional_analysis": payloads["emotional_intelligence"]["narrative"],
        "financial_analysis": payloads["financial_intelligence"]["narrative"],
    }

    strategic_guidance = {
        "short_term": profile_executive.get("short_term") or "Short term में weakest metric को low-noise behavior protocol से stabilize करें।",
        "mid_term": profile_executive.get("mid_term") or "Mid term में identity corrections deploy करके behavior delta measure करें।",
        "long_term": profile_executive.get("long_term") or "Long term scale के लिए strategic timing और quarterly recalibration रखें।",
    }

    growth_blueprint = {
        "phase_1": f"Days 1-30: {strongest_metric} leverage बनाए रखते हुए {weakest_metric.lower()} baseline stabilize करें।",
        "phase_2": f"Days 31-60: concern '{_safe_text(current_problem, 'current challenge')}' को measurable weekly protocols में deploy करें।",
        "phase_3": f"Days 61-90: personal year {personal_year} theme के साथ timing-fit growth experiments चलाएं।",
    }

    if plan_name == "basic":
        primary_insight = {
            "core_archetype": _safe_text(archetype.get("archetype_name"), "मूल अंक व्यक्तित्व"),
            "strength": profile_executive.get("primary_strength") or f"{strongest_metric} profile strength",
            "critical_deficit": profile_executive.get("primary_deficit") or f"{weakest_metric} profile challenge",
            "stability_risk": risk_band,
            "phase_1_diagnostic": "चरण 1: मूलांक और भाग्यांक pattern समझें।",
            "phase_2_blueprint": "चरण 2: missing numbers और routine correction लागू करें।",
            "phase_3_intervention_protocol": "चरण 3: 21-day numerology correction discipline चलाएं।",
            "narrative": profile_executive.get("summary") or payloads["executive_numerology_summary"]["narrative"],
        }
        executive_brief = {
            "summary": profile_executive.get("summary") or payloads["executive_numerology_summary"]["narrative"],
            "key_strength": profile_executive.get("key_strength") or primary_insight["strength"],
            "key_risk": profile_executive.get("key_risk") or primary_insight["critical_deficit"],
            "strategic_focus": profile_executive.get("strategic_focus")
            or (
                payloads["remedies_lifestyle_adjustments"]["cards"][3]["value"]
                if payloads["remedies_lifestyle_adjustments"]["cards"]
                else intervention_focus
            ),
        }
        strategic_guidance = {
            "short_term": profile_executive.get("short_term") or "Mulank-Bhagyank understanding के साथ daily correction शुरू करें।",
            "mid_term": profile_executive.get("mid_term") or "Missing numbers और repeating traits पर structured balancing करें।",
            "long_term": profile_executive.get("long_term") or "Personal year timing के साथ numerology-aligned decisions लें।",
        }
        growth_blueprint = {
            "phase_1": f"Week 1: core numbers observation + {weakest_metric.lower()} tracker + daily log।",
            "phase_2": f"Week 2: missing number correction + concern '{_safe_text(current_problem, 'current challenge')}' action loop।",
            "phase_3": f"Week 3: mobile/email alignment + personal year {personal_year} timing review + follow-through proof।",
        }

    business_block = {"business_strength": business_strength, "risk_factor": business_risk, "compatible_industries": business_industries}
    compatibility_block = {"compatible_numbers": [value for value in [life_path, destiny, expression] if value], "challenging_numbers": loshu_missing[:3], "relationship_guidance": compatibility_summary}

    return {
        "primary_insight": primary_insight,
        "metric_explanations": metric_explanations,
        "metrics_spine": {"primary_strength": strongest_metric, "primary_deficit": weakest_metric, "structural_cause": structural_cause, "intervention_focus": intervention_focus, "risk_band": risk_band},
        "numerology_architecture": {"foundation": life_path, "left_pillar": destiny, "right_pillar": expression, "facade": name_number, "narrative": payloads["numerology_architecture"]["narrative"]},
        "archetype_intelligence": {"signature": payloads["archetype_intelligence"]["narrative"], "leadership_traits": name_trait["strength"], "shadow_traits": name_trait["risk"], "growth_path": name_trait["protocol"]},
        "loshu_diagnostic": {"present_numbers": loshu_present, "missing_numbers": loshu_missing, "center_presence": 5 in loshu_present, "energy_imbalance": f"Present {len(loshu_present)} बनाम missing {len(loshu_missing)}.", "missing_number_meanings": [f"Missing {number}: conscious correction protocol बनाएं।" for number in loshu_missing], "narrative": payloads["loshu_grid_intelligence"]["narrative"]},
        "planetary_mapping": {"background_forces": f"Life Path {life_path}, Destiny {destiny}, और Name {name_number} मिलकर {dominant_planet} influence channel बनाते हैं।", "primary_intervention_planet": dominant_planet, "calibration_cluster": "discipline, timing, authority", "narrative": payloads["planetary_influence"]["narrative"]},
        "structural_deficit_model": {"deficit": f"Primary deficit: {weakest_metric}", "symptom": "Stress phase में execution inconsistency और identity mismatch दिखता है।", "patch": intervention_focus, "summary": "Deficit -> behavior risk -> protocol patch sequence को strict order में चलाएं।"},
        "circadian_alignment": {"morning_routine": "10-minute sunlight, breath reset, और strategic priority lock करें।", "work_alignment": "Communication noise से पहले first deep-work block पूरा करें।", "evening_shutdown": "Decision freeze window, digital wind-down, और short review रखें।", "narrative": "Rhythm quality सीधे decision quality को drive करती है।"},
        "environment_alignment": {"physical_space": "Focus और recovery के लिए low-clutter workspace zones बनाएं।", "color_alignment": "Workspace और digital surfaces पर grounded color palette रखें।", "mobile_number_analysis": payloads["mobile_number_intelligence"]["narrative"], "digital_behavior": digital_protocol, "narrative": "Environment का काम friction कम करना और clarity protect करना है।"},
        "vedic_remedy_protocol": {"focus": weakest_metric, "code": vedic_code, "parameter": vedic_parameter, "output": vedic_output, "purpose": "Disciplined intention से deficit metric को stabilize करना।", "planetary_alignment": dominant_planet, "pronunciation": vedic_code},
        "execution_plan": {"install_rhythm": growth_blueprint["phase_1"], "deploy_anchor": growth_blueprint["phase_2"], "run_protocol": growth_blueprint["phase_3"], "checkpoints": ["Week 1: rhythm और metric baseline lock करें।", "Week 2: identity corrections deploy करके behavior delta compare करें।", "Week 3: timing windows validate करके decision quality scale करें।"], "summary": "21-day execution पहले stability बनाता है, फिर strategic expansion को support करता है।"},
        "executive_brief": executive_brief,
        "analysis_sections": analysis_sections,
        "strategic_guidance": strategic_guidance,
        "growth_blueprint": growth_blueprint,
        "business_block": business_block,
        "compatibility_block": compatibility_block,
        "personal_year_forecast": {"current_personal_year": personal_year, "theme": "वर्तमान वर्ष में structure consolidation और correction adoption पर फोकस रखें।", "opportunities": "Aligned launches, cleaner partnerships, और stronger authority signal.", "caution_areas": "High-noise windows में reactive decisions से बचें।", "favorable_dates": lucky_dates},
        "executive_numerology_summary": payloads.get("executive_numerology_summary"),
        "core_numbers_analysis": payloads.get("core_numbers_analysis"),
        "mulank_description": payloads.get("mulank_description"),
        "bhagyank_description": payloads.get("bhagyank_description"),
        "number_interaction_analysis": payloads.get("number_interaction_analysis"),
        "loshu_grid_interpretation": payloads.get("loshu_grid_interpretation"),
        "missing_numbers_analysis": payloads.get("missing_numbers_analysis"),
        "repeating_numbers_impact": payloads.get("repeating_numbers_impact"),
        "mobile_number_numerology": payloads.get("mobile_number_numerology"),
        "mobile_life_number_compatibility": payloads.get("mobile_life_number_compatibility"),
        "email_numerology": payloads.get("email_numerology"),
        "numerology_personality_profile": payloads.get("numerology_personality_profile"),
        "current_life_phase_insight": payloads.get("current_life_phase_insight"),
        "career_financial_tendencies": payloads.get("career_financial_tendencies"),
        "relationship_compatibility_patterns": payloads.get("relationship_compatibility_patterns"),
        "health_tendencies_from_numbers": payloads.get("health_tendencies_from_numbers"),
        "color_alignment": payloads.get("color_alignment"),
        "remedies_lifestyle_adjustments": payloads.get("remedies_lifestyle_adjustments"),
        "closing_numerology_guidance": payloads.get("closing_numerology_guidance"),
        "name_vibration_optimization": payloads["name_vibration_optimization"],
        "mobile_number_intelligence": payloads["mobile_number_intelligence"],
        "email_identity_intelligence": payloads["email_identity_intelligence"],
        "signature_intelligence": payloads.get("signature_intelligence"),
        "business_name_intelligence": payloads.get("business_name_intelligence"),
        "brand_handle_optimization": payloads.get("brand_handle_optimization"),
        "residence_energy_intelligence": payloads.get("residence_energy_intelligence"),
        "vehicle_number_intelligence": payloads.get("vehicle_number_intelligence"),
        "correction_protocol_summary": payloads["correction_protocol_summary"],
        "karmic_pattern_intelligence": payloads["karmic_pattern_intelligence"],
        "hidden_talent_intelligence": payloads["hidden_talent_intelligence"],
        "pinnacle_challenge_cycle_intelligence": payloads["pinnacle_challenge_cycle_intelligence"],
        "life_cycle_timeline": payloads["life_cycle_timeline"],
        "strategic_timing_intelligence": payloads.get("strategic_timing_intelligence"),
        "wealth_energy_blueprint": payloads.get("wealth_energy_blueprint"),
        "leadership_intelligence": payloads.get("leadership_intelligence"),
        "decision_intelligence": payloads.get("decision_intelligence"),
        "emotional_intelligence": payloads.get("emotional_intelligence"),
        "digital_discipline": payloads.get("digital_discipline"),
        "lifestyle_alignment": payloads.get("lifestyle_alignment"),
        "vedic_remedy": payloads.get("vedic_remedy"),
        "closing_synthesis": payloads["closing_synthesis"],
        "section_payloads": payloads,
        "meta_notes": {"dominant_planet": dominant_planet, "strongest_metric": strongest_metric, "strongest_metric_score": strongest_score, "weakest_metric": weakest_metric, "weakest_metric_score": weakest_score, "focus": _safe_text(focus.get("life_focus"), "general_alignment"), "city": city, "career_industry": career_industry, "risk_band": risk_band, "social_handle": social_handle, "domain_handle": domain_handle, "residence_number": residence_number, "vehicle_number": vehicle_number},
    }
