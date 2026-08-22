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
