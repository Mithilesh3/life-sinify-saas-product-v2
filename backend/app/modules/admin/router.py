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

    return {
        "total_users": total_users or 0,
        "total_reports": total_reports or 0,
        "total_organizations": total_orgs or 0,
        "active_subscriptions": active_subscriptions or 0,
    }

