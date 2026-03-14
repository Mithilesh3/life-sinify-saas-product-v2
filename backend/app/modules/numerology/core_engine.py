from typing import Dict, Any

from app.modules.numerology.pythagorean import generate_pythagorean_numbers
from app.modules.numerology.chaldean import generate_chaldean_numbers
from app.modules.numerology.loshu import generate_loshu_grid
from app.modules.numerology.mobile_engine import analyze_mobile_number
from app.modules.numerology.email_engine import analyze_email
from app.modules.numerology.name_correction import suggest_name_corrections
from app.modules.numerology.compatibility import analyze_compatibility


# =========================================================
# MASTER NUMEROLOGY ORCHESTRATOR
# =========================================================


def generate_numerology_profile(
    identity: Dict[str, Any],
    birth_details: Dict[str, Any],
    plan_name: str = "basic",
) -> Dict[str, Any]:

    identity = identity or {}
    birth_details = birth_details or {}

    plan_name = (plan_name or "basic").lower()

    full_name = identity.get("full_name")
    email = identity.get("email")
    partner_name = identity.get("partner_name")

    date_of_birth = birth_details.get("date_of_birth")
    mobile_number = identity.get("mobile_number")

    numerology_core: Dict[str, Any] = {}

    # =====================================================
    # DETERMINISTIC CORE FEATURES (Always Active)
    # =====================================================

    pythagorean = generate_pythagorean_numbers(
        identity,
        birth_details,
    )
    numerology_core["pythagorean"] = pythagorean

    numerology_core["chaldean"] = generate_chaldean_numbers(
        identity
    )

    if date_of_birth:
        numerology_core["loshu_grid"] = generate_loshu_grid(
            date_of_birth
        )

    if mobile_number:
        numerology_core["mobile_analysis"] = analyze_mobile_number(
            mobile_number,
            life_path_number=pythagorean.get("life_path_number"),
        )

    # =====================================================
    # ENHANCED FEATURES
    # =====================================================

    if email:
        numerology_core["email_analysis"] = analyze_email(
            email
        )

    if full_name:
        numerology_core["name_correction"] = suggest_name_corrections(
            full_name
        )

    if full_name and partner_name and date_of_birth:

        primary_profile = generate_pythagorean_numbers(
            {"full_name": full_name},
            {"date_of_birth": date_of_birth}
        )

        partner_profile = generate_pythagorean_numbers(
            {"full_name": partner_name},
            {"date_of_birth": date_of_birth}
        )

        numerology_core["compatibility"] = analyze_compatibility(
            primary_profile,
            partner_profile
        )

    # =====================================================
    # ENTERPRISE FEATURES
    # =====================================================

    if plan_name == "enterprise":

        numerology_core["strategic_forecast"] = {
            "next_3_year_theme": "Expansion cycle with restructuring phase",
            "risk_window": "Mid-cycle volatility possible",
            "growth_window": "Favorable for scaling after stabilization",
        }

    return numerology_core
