from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import secrets

from app.db.dependencies import get_db
from app.db.models import User, Organization, Subscription
from app.modules.users.schemas import (
    UserCreate,
    UserResponse,
    TokenResponse,
    PlanUpdate,
)
from app.modules.users.service import (
    create_user,
    login_user,
    update_organization_plan,
)
from app.core.security import decode_access_token, hash_password


router = APIRouter(tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


# =====================================================
# AUTH DEPENDENCY
# =====================================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")

    user = (
        db.query(User)
        .filter(
            User.id == int(user_id),
            User.tenant_id == int(tenant_id),
            User.is_deleted == False
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# =====================================================
# ROLE GUARDS
# =====================================================
def super_admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    return current_user


def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# =====================================================
# REGISTER
# =====================================================
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    new_user = create_user(
        db,
        user.email,
        user.password,
        user.organization_name
    )

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        tenant_id=new_user.tenant_id,
        role=new_user.role,
        plan=new_user.organization.plan
    )


# =====================================================
# LOGIN
# =====================================================
@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    result = login_user(db, form_data.username, form_data.password)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result


# =====================================================
# CURRENT USER DETAILS
# =====================================================
@router.get("/me")
def read_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.tenant_id == current_user.tenant_id,
            Subscription.is_active == True
        )
        .first()
    )

    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "organization": {
            "id": current_user.organization.id,
            "name": current_user.organization.name,
            "plan": current_user.organization.plan,
        },
        "subscription": {
            "plan_name": subscription.plan_name if subscription else "basic",
            "is_active": subscription.is_active if subscription else False,
            "end_date": subscription.end_date if subscription else None,
            "reports_used": subscription.reports_used if subscription else 0,
        }
    }


# =====================================================
# LIST ORG USERS
# =====================================================
@router.get("/org-users")
def list_org_users(
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    users = (
        db.query(User)
        .filter(
            User.tenant_id == current_user.tenant_id,
            User.is_deleted == False
        )
        .all()
    )

    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at
        }
        for u in users
    ]


# =====================================================
# DELETE USER (SAFE)
# =====================================================
@router.delete("/delete-user/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id,
            User.is_deleted == False
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user.is_deleted = True
    db.commit()

    return {"message": "User deleted successfully"}


# =====================================================
# UPDATE ROLE
# =====================================================
@router.put("/update-user-role/{user_id}")
def update_user_role(
    user_id: int,
    new_role: str,
    current_user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    allowed_roles = ["admin", "manager", "user"]

    if new_role not in allowed_roles:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id,
            User.is_deleted == False
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    db.commit()

    return {"message": "Role updated successfully"}


# =====================================================
# INVITE USER
# =====================================================
class InviteUserRequest(BaseModel):
    email: str
    role: str = "user"


@router.post("/invite")
def invite_user(
    payload: InviteUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    temp_password = secrets.token_hex(4)

    new_user = User(
        email=payload.email,
        password=hash_password(temp_password),
        tenant_id=current_user.tenant_id,
        role=payload.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User invited successfully",
        "temporary_password": temp_password
    }   