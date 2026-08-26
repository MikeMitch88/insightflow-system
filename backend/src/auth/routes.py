"""Auth API routes: login, me, permissions, user list."""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from .service import authenticate, create_token, decode_token, get_permissions, USERS, ROLE_LABELS

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
    role: str
    role_label: str
    permissions: list[str]


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    user = authenticate(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user.get("_inactive"):
        raise HTTPException(status_code=403, detail=f"Account for {user['name']} is inactive. Contact an administrator.")
    token = create_token(user)
    return LoginResponse(
        token=token,
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "role_label": ROLE_LABELS.get(user["role"], user["role"]),
            "permissions": get_permissions(user["role"]),
        },
    )


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    payload["permissions"] = get_permissions(payload.get("role", ""))
    payload["role_label"] = ROLE_LABELS.get(payload.get("role", ""), payload.get("role", ""))
    return payload


def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        return None
    payload["permissions"] = get_permissions(payload.get("role", ""))
    payload["role_label"] = ROLE_LABELS.get(payload.get("role", ""), payload.get("role", ""))
    return payload


def require_manager_role(authorization: Optional[str] = Header(None)) -> dict:
    """Enforce that ONLY Program Manager can approve or reject reports. Admin and others get 403."""
    user = get_current_user_optional(authorization)
    if user:
        role = user.get("role", "").lower()
        if role not in ["program_manager"]:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: User role '{user.get('role_label', role)}' is not authorized to approve or reject reports. Only Program Manager has approval authority."
            )
        return user
    
    # If no token passed, require authorization
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    user = get_current_user(authorization)
    role = user.get("role", "").lower()
    if role not in ["program_manager"]:
        raise HTTPException(
            status_code=403,
            detail=f"Forbidden: User role '{user.get('role_label', role)}' is not authorized to approve or reject reports. Only Program Manager has approval authority."
        )
    return user


def require_admin_or_reporter_role(authorization: Optional[str] = Header(None)) -> dict:
    """Enforce that reports can only be generated/revised by Admin or authorized reporter."""
    user = get_current_user_optional(authorization)
    if user:
        role = user.get("role", "").lower()
        if role not in ["admin", "reporting_officer"]:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: User role '{user.get('role_label', role)}' cannot generate official reports."
            )
        return user
    return {"id": 1, "name": "Program Administrator", "role": "admin", "role_label": "Administrator"}


@router.get("/me")
def me(authorization: Optional[str] = Header(None)):
    user = get_current_user(authorization)
    return {
        "id": int(user["sub"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "role_label": user["role_label"],
        "permissions": user["permissions"],
    }


@router.get("/users")
def list_users():
    return [
        {
            "id": u["id"],
            "email": u["email"],
            "name": u["name"],
            "role": u["role"],
            "role_label": ROLE_LABELS.get(u["role"], u["role"]),
            "status": u["status"],
        }
        for u in USERS
    ]

