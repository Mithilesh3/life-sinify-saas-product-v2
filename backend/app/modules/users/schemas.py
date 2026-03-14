from pydantic import BaseModel, EmailStr, Field
from typing import Literal


# =========================
# REGISTER
# =========================
class UserCreate(BaseModel):
    full_name: str = Field(min_length=2)
    mobile_no: str = Field(min_length=8)
    country: str = Field(min_length=2)
    state: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=6)
    organization_name: str = Field(min_length=2)
    payment_method: Literal["UPI", "Credit/Debit Card", "Net Banking"]


# =========================
# USER RESPONSE
# =========================
class UserResponse(BaseModel):
    id: int
    full_name: str | None = None
    mobile_no: str | None = None
    country: str | None = None
    state: str | None = None
    email: EmailStr
    tenant_id: int
    role: str
    plan: str
    payment_method: str | None = None
    kyc_verified: bool = False

    model_config = {
        "from_attributes": True
    }


# =========================
# TOKEN RESPONSE
# =========================
class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# =========================
# PLAN UPDATE (Admin Only)
# =========================
class PlanUpdate(BaseModel):
    plan: Literal["free", "pro", "enterprise"]
