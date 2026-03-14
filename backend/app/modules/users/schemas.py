from pydantic import BaseModel, EmailStr, Field
from typing import Literal


# =========================
# REGISTER
# =========================
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    organization_name: str = Field(min_length=2)


# =========================
# USER RESPONSE
# =========================
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    tenant_id: int
    role: str
    plan: str

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
