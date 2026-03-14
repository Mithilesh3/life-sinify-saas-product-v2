from datetime import datetime
from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field, model_validator


SUPPORTED_LANGUAGE_PREFERENCE = Literal["hinglish", "hindi", "english"]
SUPPORTED_GENDER = Literal["male", "female", "other"]
SUPPORTED_CAREER_TYPE = Literal["business", "job"]
SUPPORTED_ROLE = Literal["entrepreneur", "employee", "consultant", "student"]


def _derive_life_focus(primary_goal: Optional[str], career_type: Optional[str]) -> str:
    goal = (primary_goal or "").strip().lower()
    career = (career_type or "").strip().lower()

    if career == "business":
        return "business_decision"

    keyword_map = {
        "finance_debt": ["finance", "money", "debt", "loan", "cash", "income", "wealth"],
        "career_growth": ["career", "job", "promotion", "growth", "profession", "role"],
        "relationship": ["relationship", "marriage", "love", "partner", "family"],
        "health_stability": ["health", "fitness", "sleep", "wellness"],
        "emotional_confusion": ["anxiety", "emotion", "confusion", "clarity", "stress"],
        "business_decision": ["business", "startup", "company", "venture", "brand"],
    }

    for focus, keywords in keyword_map.items():
        if any(keyword in goal for keyword in keywords):
            return focus

    return "general_alignment"


def _map_career_role(career_type: Optional[str]) -> Optional[str]:
    career = (career_type or "").strip().lower()
    if career == "business":
        return "entrepreneur"
    if career == "job":
        return "employee"
    return None


def _normalize_date(raw_date: Optional[str]) -> Optional[str]:
    if not raw_date:
        return raw_date

    text = str(raw_date).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text


class BasicIdentity(BaseModel):
    full_name: str = Field(..., min_length=2)
    date_of_birth: str
    gender: Optional[SUPPORTED_GENDER] = None
    country_of_residence: str = Field(..., min_length=2)
    email: Optional[str] = None
    partner_name: Optional[str] = None
    business_name: Optional[str] = None
    signature_style: Optional[str] = None


class BirthDetails(BaseModel):
    date_of_birth: str
    time_of_birth: Optional[str] = None
    birthplace_city: Optional[str] = None
    birthplace_country: Optional[str] = None


class FocusArea(BaseModel):
    life_focus: Literal[
        "finance_debt",
        "career_growth",
        "relationship",
        "health_stability",
        "emotional_confusion",
        "business_decision",
        "general_alignment",
    ]


class ContactLayer(BaseModel):
    mobile_number: Optional[str] = None
    social_handle: Optional[str] = None
    domain_handle: Optional[str] = None
    residence_number: Optional[str] = None
    vehicle_number: Optional[str] = None


class FinancialSnapshot(BaseModel):
    monthly_income: Optional[int] = None
    savings_ratio: Optional[int] = Field(None, ge=0, le=100)
    debt_ratio: Optional[int] = Field(None, ge=0, le=100)
    risk_tolerance: Optional[Literal["low", "moderate", "high"]] = None


class CareerProfile(BaseModel):
    industry: Optional[str] = None
    role: Optional[SUPPORTED_ROLE] = None
    years_experience: Optional[int] = None
    stress_level: Optional[int] = Field(None, ge=1, le=10)


class EmotionalState(BaseModel):
    anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    decision_confusion: Optional[int] = Field(None, ge=1, le=10)
    impulse_control: Optional[int] = Field(None, ge=1, le=10)
    emotional_stability: Optional[int] = Field(None, ge=1, le=10)


class LifeEvents(BaseModel):
    positive_events_years: Optional[List[int]] = None
    setback_events_years: Optional[List[int]] = None


class BusinessHistory(BaseModel):
    major_investments: Optional[int] = None
    major_losses: Optional[int] = None
    risk_mistakes_count: Optional[int] = None


class HealthLifestyle(BaseModel):
    sleep_hours: Optional[int] = None
    alcohol: Optional[bool] = None
    smoking: Optional[bool] = None
    exercise_frequency_per_week: Optional[int] = None
    food_pattern: Optional[Literal["veg", "non_veg", "mixed"]] = None


class CalibrationAnswers(BaseModel):
    stress_response: Optional[Literal["withdraw", "impulsive", "overthink", "take_control"]] = None
    money_decision_style: Optional[Literal["emotional", "calculated", "risky", "avoidant"]] = None
    biggest_weakness: Optional[Literal["discipline", "patience", "confidence", "focus"]] = None
    life_preference: Optional[Literal["stability", "growth", "recognition", "freedom"]] = None
    decision_style: Optional[Literal["fast", "research", "advice", "emotional"]] = None


class ReportPreferences(BaseModel):
    language_preference: SUPPORTED_LANGUAGE_PREFERENCE = "hindi"
    profession: Optional[str] = None
    relationship_status: Optional[str] = None
    career_type: Optional[SUPPORTED_CAREER_TYPE] = None
    primary_goal: Optional[str] = None


class LifeSignifyRequest(BaseModel):
    identity: BasicIdentity
    birth_details: BirthDetails
    focus: FocusArea
    current_problem: Optional[str] = None
    contact: Optional[ContactLayer] = None
    financial: Optional[FinancialSnapshot] = None
    career: Optional[CareerProfile] = None
    emotional: Optional[EmotionalState] = None
    life_events: Optional[LifeEvents] = None
    business_history: Optional[BusinessHistory] = None
    health: Optional[HealthLifestyle] = None
    calibration: Optional[CalibrationAnswers] = None
    preferences: Optional[ReportPreferences] = None
    plan_override: Optional[Literal["basic", "pro", "premium", "enterprise"]] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        data = dict(value)
        has_nested_contract = any(data.get(key) for key in ("identity", "birth_details", "focus"))

        if not has_nested_contract:
            required_flat_fields = [
                "full_name",
                "date_of_birth",
                "mobile_number",
                "gender",
                "city",
                "country",
                "email",
                "language_preference",
            ]
            missing = [field for field in required_flat_fields if not data.get(field)]
            if missing:
                joined = ", ".join(missing)
                raise ValueError(f"Missing required report fields: {joined}")

        identity = dict(data.get("identity") or {})
        birth_details = dict(data.get("birth_details") or {})
        focus = dict(data.get("focus") or {})
        contact = dict(data.get("contact") or {})
        career = dict(data.get("career") or {})
        preferences = dict(data.get("preferences") or {})

        flat_full_name = data.get("full_name")
        flat_dob = data.get("date_of_birth")
        flat_gender = data.get("gender")
        flat_city = data.get("city")
        flat_country = data.get("country")
        flat_email = data.get("email")
        flat_mobile = data.get("mobile_number")
        flat_language = data.get("language_preference")
        flat_profession = data.get("profession")
        flat_relationship_status = data.get("relationship_status")
        flat_career_type = data.get("career_type")
        flat_primary_goal = data.get("primary_goal")

        if flat_full_name and not identity.get("full_name"):
            identity["full_name"] = flat_full_name
        if flat_dob:
            identity.setdefault("date_of_birth", flat_dob)
            birth_details.setdefault("date_of_birth", flat_dob)
        if identity.get("date_of_birth"):
            identity["date_of_birth"] = _normalize_date(identity.get("date_of_birth"))
        if birth_details.get("date_of_birth"):
            birth_details["date_of_birth"] = _normalize_date(birth_details.get("date_of_birth"))
        if flat_gender and not identity.get("gender"):
            identity["gender"] = flat_gender
        if flat_country:
            identity.setdefault("country_of_residence", flat_country)
            birth_details.setdefault("birthplace_country", flat_country)
        if flat_email and not identity.get("email"):
            identity["email"] = flat_email
        if flat_city and not birth_details.get("birthplace_city"):
            birth_details["birthplace_city"] = flat_city
        if flat_mobile and not contact.get("mobile_number"):
            contact["mobile_number"] = flat_mobile

        if flat_profession and not career.get("industry"):
            career["industry"] = flat_profession
        derived_role = _map_career_role(flat_career_type)
        if derived_role and not career.get("role"):
            career["role"] = derived_role

        if flat_language and not preferences.get("language_preference"):
            preferences["language_preference"] = flat_language
        if flat_profession and not preferences.get("profession"):
            preferences["profession"] = flat_profession
        if flat_relationship_status and not preferences.get("relationship_status"):
            preferences["relationship_status"] = flat_relationship_status
        if flat_career_type and not preferences.get("career_type"):
            preferences["career_type"] = flat_career_type
        if flat_primary_goal and not preferences.get("primary_goal"):
            preferences["primary_goal"] = flat_primary_goal

        if not focus.get("life_focus"):
            focus["life_focus"] = _derive_life_focus(
                primary_goal=preferences.get("primary_goal") or data.get("current_problem"),
                career_type=preferences.get("career_type"),
            )

        if preferences.get("primary_goal") and not data.get("current_problem"):
            data["current_problem"] = preferences.get("primary_goal")

        data["identity"] = identity
        data["birth_details"] = birth_details
        data["focus"] = focus
        if contact:
            data["contact"] = contact
        if career:
            data["career"] = career
        if preferences:
            data["preferences"] = preferences

        return data

    model_config = {
        "extra": "ignore",
        "json_schema_extra": {
            "examples": [
                {
                    "full_name": "Aarav Sharma",
                    "date_of_birth": "1992-08-14",
                    "mobile_number": "9876543210",
                    "gender": "male",
                    "city": "Lucknow",
                    "country": "India",
                    "email": "aarav@example.com",
                    "language_preference": "hindi",
                    "profession": "Sales",
                    "relationship_status": "married",
                    "career_type": "job",
                    "primary_goal": "career growth and financial stability",
                }
            ]
        },
    }
