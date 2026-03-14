from typing import Any, Dict, Optional
import json
import logging

from app.core.config import settings
from app.core.llm_config import DEPLOYMENT_NAME, azure_client

logger = logging.getLogger(__name__)


def _is_placeholder(value: str | None) -> bool:
    normalized = (value or "").strip().lower()
    if not normalized:
        return True
    return "your-" in normalized or "xxxxxxxx" in normalized


# =====================================================
# TOKEN LIMITS
# =====================================================

PLAN_TOKEN_BASE = {
    "basic": 420,
    "pro": 560,
    "premium": 720,
    "enterprise": 860,
}

REQUEST_TIMEOUT_SECONDS = 24.0


# =====================================================
# HELPERS
# =====================================================

def _safe_json_parse(raw_text: str) -> Dict[str, Any]:
    if not raw_text:
        return {}

    try:
        return json.loads(raw_text)
    except Exception:
        cleaned = str(raw_text or "").strip()
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        try:
            start = cleaned.index("{")
            end = cleaned.rindex("}") + 1
            return json.loads(cleaned[start:end])
        except Exception:
            logger.error("AI JSON parsing failed")
            return {}


def _clip_text(value: Any, max_chars: int = 220) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 3]}..."


def _compact_payload_for_llm(
    intake_context: Dict[str, Any],
    numerology_core: Dict[str, Any],
    scores: Dict[str, Any],
    interpretation_draft: Dict[str, Any],
) -> Dict[str, Any]:
    identity = intake_context.get("identity") or {}
    birth_details = intake_context.get("birth_details") or {}
    focus = intake_context.get("focus") or {}
    financial = intake_context.get("financial") or {}
    emotional = intake_context.get("emotional") or {}
    health = intake_context.get("health") or {}
    business_history = intake_context.get("business_history") or {}

    pythagorean = numerology_core.get("pythagorean") or {}
    loshu = numerology_core.get("loshu_grid") or {}
    mobile = numerology_core.get("mobile_analysis") or {}
    email = numerology_core.get("email_analysis") or {}

    draft_exec = interpretation_draft.get("executive_brief") or {}
    draft_analysis = interpretation_draft.get("analysis_sections") or {}
    draft_primary = interpretation_draft.get("primary_insight") or {}

    return {
        "user_snapshot": {
            "full_name": identity.get("full_name"),
            "date_of_birth": birth_details.get("date_of_birth"),
            "life_focus": focus.get("life_focus"),
            "current_problem": _clip_text(intake_context.get("current_problem"), 180),
            "financial_hint": {
                "monthly_income": financial.get("monthly_income"),
                "risk_tolerance": financial.get("risk_tolerance"),
            },
            "emotional_hint": {
                "anxiety_level": emotional.get("anxiety_level"),
                "decision_confusion": emotional.get("decision_confusion"),
            },
            "health_hint": {
                "sleep_hours": health.get("sleep_hours"),
                "exercise_frequency_per_week": health.get("exercise_frequency_per_week"),
            },
            "business_hint": {
                "major_investments": business_history.get("major_investments"),
                "major_losses": business_history.get("major_losses"),
                "risk_mistakes_count": business_history.get("risk_mistakes_count"),
            },
        },
        "numerology_summary": {
            "life_path_number": pythagorean.get("life_path_number"),
            "destiny_number": pythagorean.get("destiny_number"),
            "expression_number": pythagorean.get("expression_number"),
            "name_number": (numerology_core.get("chaldean") or {}).get("name_number"),
            "mobile_vibration": mobile.get("mobile_vibration") or mobile.get("mobile_number_vibration"),
            "email_number": email.get("email_number"),
            "loshu_missing_numbers": loshu.get("missing_numbers"),
        },
        "score_summary": {
            "confidence_score": scores.get("confidence_score"),
            "data_completeness_score": scores.get("data_completeness_score"),
            "life_stability_index": scores.get("life_stability_index"),
            "emotional_regulation_index": scores.get("emotional_regulation_index"),
            "financial_discipline_index": scores.get("financial_discipline_index"),
            "dharma_alignment_score": scores.get("dharma_alignment_score"),
            "risk_band": scores.get("risk_band"),
        },
        "deterministic_draft": {
            "executive_brief": {
                "summary": _clip_text(draft_exec.get("summary"), 280),
                "key_strength": _clip_text(draft_exec.get("key_strength"), 200),
                "key_risk": _clip_text(draft_exec.get("key_risk"), 200),
                "strategic_focus": _clip_text(draft_exec.get("strategic_focus"), 200),
            },
            "analysis_sections": {
                "career_analysis": _clip_text(draft_analysis.get("career_analysis"), 220),
                "decision_profile": _clip_text(draft_analysis.get("decision_profile"), 220),
                "emotional_analysis": _clip_text(draft_analysis.get("emotional_analysis"), 220),
                "financial_analysis": _clip_text(draft_analysis.get("financial_analysis"), 220),
            },
            "primary_insight": {
                "narrative": _clip_text(draft_primary.get("narrative"), 220),
            },
            "section_payload_keys": sorted(
                list((interpretation_draft.get("section_payloads") or {}).keys())
            )[:28],
        },
    }


# =====================================================
# MAIN AI REPORT GENERATOR
# =====================================================

def generate_ai_narrative(
    numerology_core: Dict[str, Any],
    scores: Dict[str, Any],
    current_problem: str,
    plan_name: str,
    token_multiplier: float = 1.0,
    intake_context: Optional[Dict[str, Any]] = None,
    interpretation_draft: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if _is_placeholder(settings.AZURE_OPENAI_API_KEY) or _is_placeholder(settings.AZURE_OPENAI_ENDPOINT):
        logger.warning("Azure OpenAI is not configured. Using deterministic fallback narrative.")
        return {}

    plan_name = (plan_name or "basic").lower()
    intake_context = intake_context or {}
    interpretation_draft = interpretation_draft or {}
    preferences = intake_context.get("preferences") or {}
    language_preference = str(preferences.get("language_preference") or "hindi").lower()

    is_basic = plan_name == "basic"
    base_tokens = PLAN_TOKEN_BASE.get(plan_name, 700)
    max_tokens = max(260, min(900, int(base_tokens * token_multiplier)))

    compact_payload = _compact_payload_for_llm(
        intake_context=intake_context,
        numerology_core=numerology_core,
        scores=scores,
        interpretation_draft=interpretation_draft,
    )

    basic_plan_guardrails = ""
    if is_basic:
        basic_plan_guardrails = """
BASIC PLAN CONTENT MODE (STRICT):
- Keep narration numerology-first: Mulank, Bhagyank, Name Number, Lo Shu, Personal Year, Mobile, Email.
- Avoid enterprise consulting language, business intelligence jargon, and strategic blueprint wording.
- Keep copy simple, correction-led, and practical.
"""

    assistant_role = (
        "You are a senior numerology report editor focused on deterministic, correction-led narration."
        if is_basic
        else "You are an elite numerology strategist and behavioral intelligence advisor."
    )
    report_task = (
        "Refine deterministic interpretation into a polished BASIC numerology report."
        if is_basic
        else "Refine deterministic interpretation into a premium life intelligence report."
    )
    english_terms = (
        "career, business, growth, leadership"
        if is_basic
        else "career, business, strategy, growth, leadership, execution"
    )

    prompt = f"""
{assistant_role}
Do NOT calculate numerology numbers. All numbers are already deterministic.
{report_task}

Writing style:
- Hindi-major in Devanagari (80-90% Hindi, 10-20% English).
- Never use Roman Hindi.
- Ground each section in deterministic values; do not invent data.
- If data is limited, mention that directly.
- Avoid repetitive template wording and mystical exaggeration.

PLAN: {plan_name.upper()}
LEGACY LANGUAGE PREFERENCE: {language_preference}
USER CURRENT PROBLEM: {_clip_text(current_problem, 220)}
{basic_plan_guardrails}

DETERMINISTIC INPUT SUMMARY (JSON):
{json.dumps(compact_payload, ensure_ascii=False)}

STRICT OUTPUT RULES:
- Return VALID JSON only (no markdown).
- Rewrite only narrative fields and preserve deterministic meaning.
- Keep wording compact and specific.

REQUIRED JSON STRUCTURE:
{{
  "executive_brief": {{
    "summary": "",
    "key_strength": "",
    "key_risk": "",
    "strategic_focus": ""
  }},
  "analysis_sections": {{
    "career_analysis": "",
    "decision_profile": "",
    "emotional_analysis": "",
    "financial_analysis": ""
  }},
  "primary_insight": {{
    "narrative": ""
  }},
  "archetype_intelligence": {{
    "signature": "",
    "shadow_traits": "",
    "growth_path": ""
  }},
  "loshu_diagnostic": {{
    "narrative": ""
  }},
  "planetary_mapping": {{
    "narrative": ""
  }},
  "execution_plan": {{
    "summary": ""
  }}
}}
"""

    try:
        request_payload = {
            "model": DEPLOYMENT_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a deterministic-first numerology report editor. "
                        "Never invent profile facts. Keep response concise, high-signal, and personalized."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        client = azure_client.with_options(
            timeout=REQUEST_TIMEOUT_SECONDS,
            max_retries=0,
        )

        try:
            response = client.chat.completions.create(**request_payload)
        except TypeError:
            request_payload.pop("response_format", None)
            response = client.chat.completions.create(**request_payload)

        raw_text = (response.choices[0].message.content or "").strip()
        structured_output = _safe_json_parse(raw_text)

        summary = (
            structured_output.get("executive_brief", {}).get("summary")
            if isinstance(structured_output, dict)
            else ""
        )
        if not structured_output or not str(summary).strip():
            raise ValueError("Invalid JSON from AI")

        return structured_output
    except Exception as exc:
        logger.error("AI generation failed: %s", str(exc))
        return {}
