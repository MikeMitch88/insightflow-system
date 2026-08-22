"""Authentication service with hardcoded admin user and JWT tokens."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import bcrypt

from src.config import JWT_SECRET

ADMIN_EMAIL = "Adm@insight.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_HASHED = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()

ADMIN_USER = {
    "id": 1,
    "email": ADMIN_EMAIL,
    "name": "Administrator",
    "role": "admin",
    "hashed_password": ADMIN_HASHED,
}

_USERS_BY_EMAIL: dict[str, dict] = {ADMIN_USER["email"].lower(): ADMIN_USER}

TOKEN_EXPIRY_HOURS = 24


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def authenticate(email: str, password: str) -> Optional[dict]:
    user = _USERS_BY_EMAIL.get(email.lower())
    if user and verify_password(password, user["hashed_password"]):
        return user
    return None


def create_token(user: dict) -> str:
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
