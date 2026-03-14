from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.dependencies import get_db
from app.modules.users.router import super_admin_required
from app.db.models import User, Report, Organization, Subscription


# Router WITHOUT prefix (prefix applied in main.py)
router = APIRouter(tags=["Admin"])


# =====================================================
# ADMIN ANALYTICS
# =====================================================

@router.get("/analytics")
def get_admin_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(super_admin_required),
):

    total_users = db.query(func.count(User.id)).scalar()
    total_reports = db.query(func.count(Report.id)).scalar()
    total_orgs = db.query(func.count(Organization.id)).scalar()

    active_subscriptions = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.is_active.is_(True))
        .scalar()
    )
    kyc_verified = (
        db.query(func.count(User.id))
        .filter(
            User.role != "super_admin",
            User.is_deleted.is_(False),
            User.kyc_verified.is_(True),
        )
        .scalar()
    )
    kyc_pending = (
        db.query(func.count(User.id))
        .filter(
            User.role != "super_admin",
            User.is_deleted.is_(False),
            User.kyc_verified.is_(False),
        )
        .scalar()
    )
    total_customers = (
        db.query(func.count(User.id))
        .filter(
            User.role != "super_admin",
            User.is_deleted.is_(False),
        )
        .scalar()
    )

    return {
        "total_users": total_users or 0,
        "total_reports": total_reports or 0,
        "total_organizations": total_orgs or 0,
        "active_subscriptions": active_subscriptions or 0,
        "total_customers": total_customers or 0,
        "kyc_verified": kyc_verified or 0,
        "kyc_pending": kyc_pending or 0,
    }


@router.get("/customers")
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(super_admin_required),
):
    users = (
        db.query(User)
        .filter(
            User.role != "super_admin",
            User.is_deleted.is_(False),
        )
        .order_by(User.created_at.desc())
        .all()
    )

    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "mobile_no": u.mobile_no,
            "country": u.country,
            "state": u.state,
            "email": u.email,
            "role": u.role,
            "tenant_id": u.tenant_id,
            "payment_method": u.payment_method,
            "kyc_verified": bool(u.kyc_verified),
            "kyc_verified_at": u.kyc_verified_at,
            "created_at": u.created_at,
        }
        for u in users
    ]

