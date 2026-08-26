"""Auth API routes: login, me, permissions, user management."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session, joinedload

from src.database import get_db
from src.models.models import User, Role, Department
from src.auth.service import authenticate, create_token, decode_token, hash_password
from src.auth.rbac import get_current_user, require_tier, log_audit_event

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: Optional[dict] = None
    department: Optional[dict] = None
    status: str


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user.status == "inactive":
        raise HTTPException(status_code=403, detail=f"Account for {user.name} is inactive.")

    token = create_token(user)
    log_audit_event(db, user.id, "login", "user", user.id)

    return LoginResponse(
        token=token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": {
                "id": user.role.id,
                "name": user.role.name,
                "tier": user.role.tier,
                "description": user.role.description,
            } if user.role else None,
            "department": {
                "id": user.department.id,
                "name": user.department.name,
                "code": user.department.code,
            } if user.department else None,
            "permissions": _get_user_permissions(user),
        },
    )


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": {
            "id": user.role.id,
            "name": user.role.name,
            "tier": user.role.tier,
            "description": user.role.description,
        } if user.role else None,
        "department": {
            "id": user.department.id,
            "name": user.department.name,
            "code": user.department.code,
        } if user.department else None,
        "permissions": _get_user_permissions(user),
    }


@router.get("/users")
def list_users(
    user: User = Depends(require_tier(2)),
    db: Session = Depends(get_db),
):
    users = db.query(User).options(
        joinedload(User.role),
        joinedload(User.department),
    ).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "role": {"id": u.role.id, "name": u.role.name, "tier": u.role.tier} if u.role else None,
            "department": {"id": u.department.id, "name": u.department.name, "code": u.department.code} if u.department else None,
            "status": u.status,
        }
        for u in users
    ]


@router.get("/roles")
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


@router.get("/departments")
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()


@router.post("/users")
def create_user(
    email: str,
    name: str,
    password: str,
    role_id: int,
    department_id: Optional[int] = None,
    user: User = Depends(require_tier(3)),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        email=email.lower(),
        name=name,
        hashed_password=hash_password(password),
        role_id=role_id,
        department_id=department_id,
        status="active",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit_event(db, user.id, "create_user", "user", new_user.id, {"email": email})

    return {"id": new_user.id, "email": new_user.email, "name": new_user.name, "status": new_user.status}


def _get_user_permissions(user: User) -> list[str]:
    """Get list of permission strings for a user based on their role tier."""
    if not user.role:
        return []

    tier = user.role.tier
    permissions = []

    if tier >= 1:
        permissions.extend([
            "create_kpi_metrics", "create_financial_items", "create_risks", "create_field_notes",
            "read_own_data", "update_own_data",
        ])
    if tier >= 2:
        permissions.extend([
            "read_department_data", "verify_data", "approve_section", "read_audit_logs",
        ])
    if tier >= 3:
        permissions.extend([
            "read_all_data", "update_all_data", "generate_report", "edit_report",
            "manage_users", "manage_departments",
        ])
    if tier >= 4:
        permissions.extend([
            "final_approve", "export_reports", "sign_off",
        ])

    return permissions


def get_current_user_optional(authorization: Optional[str] = None) -> Optional[dict]:
    """Extract user from optional Authorization header. Returns None if no header or invalid."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "", 1)
    try:
        payload = decode_token(token)
        return {
            "id": payload.get("sub"),
            "name": payload.get("name", "Staff"),
            "email": payload.get("email", ""),
            "role": payload.get("role", "staff"),
            "tier": payload.get("tier", 1),
        }
    except Exception:
        return None


def require_manager_role(authorization: Optional[str] = None) -> dict:
    """Dependency that requires tier >= 2 (Reviewer/Manager or higher)."""
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    tier = user.get("tier", 0)
    if tier < 2:
        raise HTTPException(status_code=403, detail="Program Manager role or higher required")
    return user


def require_admin_or_reporter_role(authorization: Optional[str] = None) -> dict:
    """Dependency that requires tier >= 3 (Report Generator/Admin or higher)."""
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    tier = user.get("tier", 0)
    if tier < 3:
        raise HTTPException(status_code=403, detail="Admin or Report Generator role required")
    return user
