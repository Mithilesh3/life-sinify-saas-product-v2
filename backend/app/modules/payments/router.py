from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.db.dependencies import get_db
from app.modules.users.router import get_current_user
from app.db.models import User
from app.modules.payments.service import (
    create_payment_order,
    verify_payment_signature
)

router = APIRouter(tags=["Payments"])


# =====================================================
# RESPONSE MODELS
# =====================================================

class Plan(BaseModel):
    name: str
    price: int
    reports_limit: int | str


class CreateOrderRequest(BaseModel):
    plan: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# =====================================================
# GET AVAILABLE PLANS
# =====================================================

@router.get("/plans", response_model=List[Plan])
def get_plans():
    return [
        {
            "name": "Basic",
            "price": 251,
            "reports_limit": 1
        },
        {
            "name": "Pro",
            "price": 1100,
            "reports_limit": 5
        },
        {
            "name": "Premium",
            "price": 21000,
            "reports_limit": 50
        }
    ]

# =====================================================
# GET PAYMENT HISTORY
# =====================================================

@router.get("/history")
def get_payment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return []


# =====================================================
# CREATE PAYMENT ORDER (UPDATED ✅)
# =====================================================

@router.post("/create-order")
def create_order(
    payload: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_payment_order(db, current_user, payload.plan)


# =====================================================
# VERIFY PAYMENT
# =====================================================

@router.post("/verify")
def verify_payment(
    payload: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return verify_payment_signature(
        db=db,
        current_user=current_user,
        razorpay_order_id=payload.razorpay_order_id,
        razorpay_payment_id=payload.razorpay_payment_id,
        razorpay_signature=payload.razorpay_signature,
    )