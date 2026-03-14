from __future__ import annotations

import logging

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.models import Organization, Subscription, User

logger = logging.getLogger(__name__)


# =====================================================
# REGISTER (ALWAYS CREATE NEW ORG + BASIC SUBSCRIPTION)
# =====================================================
def create_user(
    db: Session,
    email: str,
    password: str,
    organization_name: str,
):
    normalized_email = (email or "").strip().lower()
    normalized_org_name = " ".join(str(organization_name or "").split())

    if not normalized_email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not normalized_org_name:
        raise HTTPException(status_code=400, detail="Organization name is required")

    try:
        # Prevent duplicate email (case-insensitive).
        if db.query(User).filter(func.lower(User.email) == normalized_email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Prevent duplicate organization name (case-insensitive).
        if db.query(Organization).filter(func.lower(Organization.name) == normalized_org_name.lower()).first():
            raise HTTPException(
                status_code=400,
                detail="Organization name already exists. Please choose a different name.",
            )

        organization = Organization(name=normalized_org_name, plan="basic")
        db.add(organization)
        db.flush()

        user = User(
            email=normalized_email,
            password=hash_password(password),
            tenant_id=organization.id,
            role="admin",
        )
        db.add(user)
        db.flush()

        subscription = Subscription(
            tenant_id=organization.id,
            plan_name="basic",
            is_active=True,
        )
        db.add(subscription)

        db.commit()
        db.refresh(user)

        # Audit logging should not fail registration response.
        try:
            log_action(
                db=db,
                user_id=user.id,
                tenant_id=user.tenant_id,
                action="USER_REGISTERED",
                details={"email": user.email, "role": user.role},
            )
        except Exception:
            db.rollback()
            logger.exception("Registration succeeded, but audit logging failed")

        return user

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError as exc:
        db.rollback()
        details = str(getattr(exc, "orig", exc)).lower()
        if "users_email_key" in details or ("unique constraint" in details and "email" in details):
            raise HTTPException(status_code=400, detail="Email already registered") from exc
        if "organizations_name_key" in details or ("unique constraint" in details and "organization" in details):
            raise HTTPException(
                status_code=400,
                detail="Organization name already exists. Please choose a different name.",
            ) from exc
        raise HTTPException(
            status_code=400,
            detail="Registration could not be completed due to duplicate data.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error during registration")
        raise HTTPException(status_code=500, detail="Database error during registration") from exc


# =====================================================
# AUTHENTICATE USER
# =====================================================
def authenticate_user(db: Session, email: str, password: str):
    normalized_email = (email or "").strip().lower()

    user = (
        db.query(User)
        .filter(
            func.lower(User.email) == normalized_email,
            User.is_deleted.is_(False),
        )
        .first()
    )

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user


# =====================================================
# LOGIN (JWT = user + tenant + role)
# =====================================================
def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)

    if not user:
        return None

    organization = db.query(Organization).filter(Organization.id == user.tenant_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    token = create_access_token(
        {
            "sub": str(user.id),
            "tenant_id": user.tenant_id,
            "role": user.role,
        }
    )

    try:
        log_action(
            db=db,
            user_id=user.id,
            tenant_id=user.tenant_id,
            action="USER_LOGIN",
            details={"email": user.email},
        )
    except Exception:
        db.rollback()
        logger.exception("Login succeeded, but audit logging failed")

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# =====================================================
# UPDATE ORGANIZATION PLAN (ADMIN)
# =====================================================
def update_organization_plan(
    db: Session,
    current_user: User,
    new_plan: str,
):
    organization = db.query(Organization).filter(Organization.id == current_user.tenant_id).first()

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    organization.plan = new_plan
    db.commit()
    db.refresh(organization)

    try:
        log_action(
            db=db,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            action="PLAN_UPDATED",
            details={"new_plan": new_plan},
        )
    except Exception:
        db.rollback()
        logger.exception("Plan update succeeded, but audit logging failed")

    return organization
