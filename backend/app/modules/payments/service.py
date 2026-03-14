from datetime import datetime, timedelta
import hashlib
import hmac

from fastapi import HTTPException
from sqlalchemy.orm import Session
from razorpay.errors import BadRequestError, ServerError, GatewayError

from app.core.payment_config import razorpay_client
from app.db.models import Organization, Payment, Subscription, User


# Prices are in paise.
PLAN_PRICING = {
    "basic": 251,
    "pro": 1100,
    "premium": 21000,
}
KYC_AMOUNT = 100  # Rs. 1


def _is_placeholder(value: str | None) -> bool:
    normalized = (value or "").strip().lower()
    if not normalized:
        return True
    return (
        "your-" in normalized
        or "xxxxxxxx" in normalized
        or normalized in {"change-me", "replace-me", "test"}
    )


def _ensure_razorpay_configured() -> None:
    key_id = razorpay_client.auth[0] if razorpay_client.auth else None
    key_secret = razorpay_client.auth[1] if razorpay_client.auth else None

    if _is_placeholder(key_id) or _is_placeholder(key_secret):
        raise HTTPException(
            status_code=503,
            detail="Payment service is not configured. Set valid Razorpay credentials.",
        )


def _create_razorpay_order(amount: int) -> dict:
    _ensure_razorpay_configured()
    try:
        return razorpay_client.order.create(
            {"amount": amount, "currency": "INR", "payment_capture": 1}
        )
    except BadRequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Payment gateway rejected order creation: {str(exc)}",
        ) from exc
    except (ServerError, GatewayError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Payment gateway is temporarily unavailable. Please retry.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to initiate payment at the moment.",
        ) from exc


def create_payment_order(db: Session, current_user: User, plan_name: str):
    plan_key = plan_name.lower()
    if plan_key not in PLAN_PRICING:
        raise HTTPException(status_code=400, detail="Invalid plan selected")

    amount = PLAN_PRICING[plan_key]
    order = _create_razorpay_order(amount)

    payment = Payment(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        plan_name=plan_key,
        razorpay_order_id=order["id"],
        amount=amount,
        currency="INR",
        status="created",
        created_at=datetime.utcnow(),
    )
    db.add(payment)
    db.commit()

    return {"id": order["id"], "amount": amount, "currency": "INR"}


def verify_payment_signature(
    db: Session,
    current_user: User,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
):
    razorpay_secret = razorpay_client.auth[1]
    generated_signature = hmac.new(
        razorpay_secret.encode("utf-8"),
        f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if generated_signature != razorpay_signature:
        raise HTTPException(status_code=400, detail="Signature mismatch")

    payment = db.query(Payment).filter(Payment.razorpay_order_id == razorpay_order_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.user_id != current_user.id or payment.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Payment does not belong to this user")

    if payment.status == "paid":
        return {"message": "Already verified"}

    payment.status = "paid"
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature

    subscription = db.query(Subscription).filter(Subscription.tenant_id == payment.tenant_id).first()
    if not subscription:
        subscription = Subscription(tenant_id=payment.tenant_id)
        db.add(subscription)

    subscription.plan_name = payment.plan_name
    subscription.is_active = True
    subscription.start_date = datetime.utcnow()
    subscription.end_date = datetime.utcnow() + timedelta(days=30)
    subscription.reports_used = 0

    organization = db.query(Organization).filter(Organization.id == payment.tenant_id).first()
    if organization:
        organization.plan = payment.plan_name

    db.commit()
    return {"message": "Subscription activated", "plan": organization.plan if organization else payment.plan_name}


def create_kyc_order(db: Session, current_user: User):
    order = _create_razorpay_order(KYC_AMOUNT)

    payment = Payment(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        plan_name="kyc",
        razorpay_order_id=order["id"],
        amount=KYC_AMOUNT,
        currency="INR",
        status="created",
        created_at=datetime.utcnow(),
    )
    db.add(payment)
    db.commit()

    return {"id": order["id"], "amount": KYC_AMOUNT, "currency": "INR"}


def verify_kyc_payment_signature(
    db: Session,
    current_user: User,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
):
    razorpay_secret = razorpay_client.auth[1]
    generated_signature = hmac.new(
        razorpay_secret.encode("utf-8"),
        f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if generated_signature != razorpay_signature:
        raise HTTPException(status_code=400, detail="Signature mismatch")

    payment = (
        db.query(Payment)
        .filter(
            Payment.razorpay_order_id == razorpay_order_id,
            Payment.plan_name == "kyc",
        )
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="KYC payment not found")

    if payment.user_id != current_user.id or payment.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="KYC payment does not belong to this user")

    if payment.status == "paid" and current_user.kyc_verified:
        return {"message": "KYC already verified", "kyc_verified": True}

    payment.status = "paid"
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature

    current_user.kyc_verified = True
    current_user.kyc_payment_id = razorpay_payment_id
    current_user.kyc_verified_at = datetime.utcnow()

    db.commit()
    return {"message": "KYC verified", "kyc_verified": True}
