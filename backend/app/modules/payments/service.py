from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models import Payment, User, Subscription, Organization
from app.core.payment_config import razorpay_client
from datetime import datetime, timedelta
import hmac
import hashlib


# =====================================================
# UPDATED PLAN PRICING (IN PAISE)
# =====================================================
PLAN_PRICING = {
    "basic": 251,      # ₹251
    "pro": 1100,       # ₹1100
    "premium": 21000   # ₹21000
}


# =====================================================
# CREATE ORDER
# =====================================================
def create_payment_order(db: Session, current_user: User, plan_name: str):

    plan_key = plan_name.lower()

    if plan_key not in PLAN_PRICING:
        raise HTTPException(status_code=400, detail="Invalid plan selected")

    amount = PLAN_PRICING[plan_key]

    order = razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    payment = Payment(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        plan_name=plan_key,
        razorpay_order_id=order["id"],
        amount=amount,
        currency="INR",
        status="created",
        created_at=datetime.utcnow()
    )

    db.add(payment)
    db.commit()

    return {
        "id": order["id"],
        "amount": amount,
        "currency": "INR"
    }


# =====================================================
# VERIFY + ACTIVATE SUBSCRIPTION
# =====================================================
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
        hashlib.sha256
    ).hexdigest()

    if generated_signature != razorpay_signature:
        raise HTTPException(status_code=400, detail="Signature mismatch")

    payment = (
        db.query(Payment)
        .filter(Payment.razorpay_order_id == razorpay_order_id)
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.user_id != current_user.id or payment.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Payment does not belong to this user")

    if payment.status == "paid":
        return {"message": "Already verified"}

    payment.status = "paid"
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature

    # =====================================================
    # ACTIVATE / UPDATE SUBSCRIPTION
    # =====================================================
    subscription = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == payment.tenant_id)
        .first()
    )

    if not subscription:
        subscription = Subscription(
            tenant_id=payment.tenant_id
        )
        db.add(subscription)

    subscription.plan_name = payment.plan_name
    subscription.is_active = True
    subscription.start_date = datetime.utcnow()
    subscription.end_date = datetime.utcnow() + timedelta(days=30)

    # 🔥 Reset usage on new subscription
    subscription.reports_used = 0

    organization = (
        db.query(Organization)
        .filter(Organization.id == payment.tenant_id)
        .first()
    )

    organization.plan = payment.plan_name

    db.commit()

    return {
        "message": "Subscription activated",
        "plan": organization.plan
    }


