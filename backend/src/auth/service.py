"""Authentication service with RBAC, JWT tokens, and hardcoded users."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import bcrypt

from src.config import JWT_SECRET

SHARED_PASSWORD = "Admin@123"
SHARED_HASHED = bcrypt.hashpw(SHARED_PASSWORD.encode(), bcrypt.gensalt()).decode()

ALL_PAGES = [
    "dashboard",
    "program-performance",
    "beneficiary-analytics",
    "outcomes",
    "reports",
    "report-builder",
    "data-sources",
    "data-quality",
    "data-pipeline",
    "ai-assistant",
    "ai-insights",
    "admin",
]

ROLE_PERMISSIONS = {
    "admin": ALL_PAGES,
    "program_manager": [
        "dashboard", "program-performance", "beneficiary-analytics", "outcomes",
        "reports", "report-builder", "ai-assistant", "ai-insights",
    ],
    "me_officer": [
        "dashboard", "program-performance", "beneficiary-analytics", "outcomes",
        "data-quality", "data-pipeline", "ai-assistant", "ai-insights",
    ],
    "reporting_officer": [
        "dashboard", "program-performance", "beneficiary-analytics", "outcomes",
        "reports", "report-builder", "data-sources", "data-quality", "data-pipeline",
        "ai-assistant",
    ],
    "leadership": [
        "dashboard", "program-performance", "beneficiary-analytics", "outcomes",
        "reports", "ai-assistant", "ai-insights",
    ],
}

USERS = [
    {"id": 1, "email": "admin@inukafoundation.org", "name": "Program Administrator", "role": "admin", "status": "active"},
    {"id": 2, "email": "grace.w@inukafoundation.org", "name": "Grace Wanjiku", "role": "program_manager", "status": "active"},
    {"id": 3, "email": "james.o@inukafoundation.org", "name": "James Otieno", "role": "me_officer", "status": "active"},
    {"id": 4, "email": "amina.h@inukafoundation.org", "name": "Amina Hassan", "role": "reporting_officer", "status": "active"},
    {"id": 5, "email": "david.m@inukafoundation.org", "name": "David Mwangi", "role": "leadership", "status": "active"},
    {"id": 6, "email": "sarah.n@inukafoundation.org", "name": "Sarah Njeri", "role": "program_manager", "status": "inactive"},
]

_USERS_BY_EMAIL: dict[str, dict] = {u["email"].lower(): {**u, "hashed_password": SHARED_HASHED} for u in USERS}

ROLE_LABELS = {
    "admin": "Administrator",
    "program_manager": "Program Manager",
    "me_officer": "M&E Officer",
    "reporting_officer": "Reporting Officer",
    "leadership": "Leadership",
}

TOKEN_EXPIRY_HOURS = 24


def authenticate(email: str, password: str) -> Optional[dict]:
    user = _USERS_BY_EMAIL.get(email.lower())
    if not user:
        return None
    if user["status"] == "inactive":
        return {"_inactive": True, "name": user["name"]}
    if bcrypt.checkpw(password.encode(), user["hashed_password"].encode()):
        return user
    return None


def create_token(user: dict) -> str:
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "status": user["status"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_permissions(role: str) -> list[str]:
    return ROLE_PERMISSIONS.get(role, [])
