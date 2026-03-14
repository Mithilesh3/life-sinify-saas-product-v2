from typing import Dict, Any, Optional
from app.core.llm_config import azure_client, DEPLOYMENT_NAME
import json
import logging

logger = logging.getLogger(__name__)

# =====================================================
# TOKEN LIMIT PER PLAN
# =====================================================

PLAN_TOKEN_BASE = {
    "basic": 1600,
    "pro": 2200,
    "premium": 3000,
    "enterprise": 3800,
}


# =====================================================
# SAFE JSON PARSER
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

    plan_name = (plan_name or "basic").lower()
    intake_context = intake_context or {}
    interpretation_draft = interpretation_draft or {}
    preferences = intake_context.get("preferences") or {}
    language_preference = str(preferences.get("language_preference") or "hindi").lower()

    is_basic = plan_name == "basic"
    base_tokens = PLAN_TOKEN_BASE.get(plan_name, 1600)
    max_tokens = int(base_tokens * token_multiplier)
    business_signals = numerology_core.get("business_analysis", {})
    numerology_json = json.dumps(numerology_core, ensure_ascii=False)
    scores_json = json.dumps(scores, ensure_ascii=False)
    intake_json = json.dumps(intake_context, ensure_ascii=False)
    draft_json = json.dumps(interpretation_draft, ensure_ascii=False)
    basic_plan_guardrails = ""
    if is_basic:
        basic_plan_guardrails = """
BASIC PLAN CONTENT MODE (STRICT):
- Keep narration numerology-first: Mulank, Bhagyank, Name Number, Lo Shu, Personal Year, Mobile, Email.
- Avoid enterprise consulting language, business intelligence jargon, strategic blueprint framing, and intervention-heavy wording.
- Keep copy simple, premium, and correction-led.
- Use short paragraphs and deterministic interpretation only.
- Do not use words like "enterprise", "consulting framework", "operating system", "strategic execution", or "blueprint" in BASIC output.
"""

    assistant_role = (
        "You are a senior numerology report editor focused on deterministic, correction-led narration."
        if is_basic
        else "You are an elite numerology strategist and behavioral intelligence advisor."
    )
    report_task = (
        "Your task is to refine an already-generated deterministic interpretation into a polished BASIC numerology report."
        if is_basic
        else "Your task is to refine an already-generated deterministic interpretation into a natural strategic life intelligence report."
    )
    english_terms = (
        "career, business, growth, leadership"
        if is_basic
        else "career, business, strategy, growth, leadership, execution"
    )
    tier_tone_line = (
        "The wording should read like a premium North Indian numerology report with quick insight and practical correction."
        if is_basic
        else "The wording should read like a premium North Indian life-intelligence report."
    )

    prompt = f"""
{assistant_role}

Do NOT calculate numerology numbers.
All numerology calculations are already provided.
{report_task}

Writing style requirements:
- The report must be written in Hindi-major language using Devanagari script.
- Keep the language ratio around 80-90% Hindi and 10-20% English.
- English words may be used for modern terms such as {english_terms}.
- Never use Roman Hindi.
- Sound psychologically insightful, practical, and premium.
- Avoid generic astrology statements and avoid mystical exaggeration.
- Make the report feel clearly different for each user by grounding every section in the user's name, numerology values, strongest or weakest scores, and stated life focus.
- Avoid sentence-level repetition across users; vary phrasing using the actual number combinations and profile signals.
- If data is missing, acknowledge the gap instead of inventing facts.
- If confidence_score is low or behavioral inputs are sparse, explicitly say that some intelligence metrics are based on limited inputs.
- Never leave blanks, placeholders, token fragments, empty commas, or partially stitched grammar.
- Do not output templated filler. Every paragraph must mention concrete deterministic signals such as life path, missing numbers, metric behavior, mobile vibration, or dominant planet.

--------------------------------------------------

USER CURRENT PROBLEM
{current_problem}

--------------------------------------------------

USER PROFILE INPUT
{intake_json}

--------------------------------------------------

NUMEROLOGY CORE DATA
{numerology_json}

--------------------------------------------------

BUSINESS NUMEROLOGY SIGNALS
{json.dumps(business_signals, ensure_ascii=False)}

--------------------------------------------------

BEHAVIORAL INTELLIGENCE SCORES
{scores_json}

--------------------------------------------------

DETERMINISTIC INTERPRETATION DRAFT
{draft_json}

--------------------------------------------------

PLAN TIER
{plan_name.upper()}

LEGACY LANGUAGE PREFERENCE
{language_preference}

Depth of analysis should increase with plan tier.
{tier_tone_line}
Even if a legacy preference says "hinglish", the final narration must still be Hindi-major in Devanagari script.
{basic_plan_guardrails}

--------------------------------------------------

STRICT OUTPUT RULES

Return VALID JSON ONLY.
Do NOT include markdown.
Do NOT include explanations outside JSON.
Keep responses structured and professional.
- Rewrite only the provided narrative fields. Preserve the deterministic meaning.
- Use natural Hindi sentences. Avoid list fragments like ", , और" or broken token sequences.
- Keep each field specific and content-rich.

--------------------------------------------------

REQUIRED JSON STRUCTURE

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
                    "content": f"""
You are {'a senior numerology report editor' if is_basic else 'an elite numerology strategist and behavioral intelligence advisor'}.
Do NOT calculate numerology numbers.
All numerology calculations are already provided.
Refine the deterministic interpretation into a premium {'numerology report' if is_basic else 'life intelligence report'}.
Write the report in Hindi-major language using Devanagari script.
Target a mix of roughly 80-90% Hindi and 10-20% English.
English words may be used for modern concepts such as {english_terms}.
Never write Roman Hindi.
Avoid generic astrology statements.
Make the output meaningfully different when user profile inputs differ.
If inputs are sparse, acknowledge that some intelligence scores are based on limited data.
Never output empty placeholders, blank grammar fragments, or corrupted Hindi.
Avoid repetitive template phrasing; write section text that clearly reflects this exact profile.
{'Avoid consulting or enterprise wording in BASIC output.' if is_basic else ''}
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        try:
            response = azure_client.chat.completions.create(**request_payload)
        except TypeError:
            # Backward compatibility for SDK versions without response_format support.
            request_payload.pop("response_format", None)
            response = azure_client.chat.completions.create(**request_payload)

        raw_text = response.choices[0].message.content.strip()
        structured_output = _safe_json_parse(raw_text)

        summary = (
            structured_output.get("executive_brief", {}).get("summary")
            if isinstance(structured_output, dict)
            else ""
        )
        if not structured_output or not str(summary).strip():
            raise ValueError("Invalid JSON from AI")

        return structured_output

    except Exception as e:

        logger.error(f"AI generation failed: {str(e)}")

        return {}

