"""Authentication service with JWT tokens and database-backed RBAC."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import bcrypt
from sqlalchemy.orm import Session

from src.config import JWT_SECRET, SHARED_PASSWORD
from src.models.models import User, Role, Department

SHARED_HASHED = bcrypt.hashpw(SHARED_PASSWORD.encode(), bcrypt.gensalt()).decode()

TOKEN_EXPIRY_HOURS = 24


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        return None
    if user.status == "inactive":
        return None
    if bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        return user
    return None


def create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "role_id": user.role_id,
        "role_name": user.role.name if user.role else "",
        "role_tier": user.role.tier if user.role else 0,
        "department_id": user.department_id,
        "status": user.status,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def seed_default_roles(db: Session) -> None:
    """Seed the 4-tier RBAC roles and 5 departments if they don't exist."""
    departments = [
        ("Programs/Field Ops", "PROG", "Programs and Field Operations"),
        ("M&E", "ME", "Monitoring & Evaluation"),
        ("Finance", "FIN", "Finance & Accounting"),
        ("Admin/HR", "AHR", "Administration & Human Resources"),
        ("Executive", "EXEC", "Executive Leadership"),
    ]

    for name, code, desc in departments:
        existing = db.query(Department).filter(Department.code == code).first()
        if not existing:
            db.add(Department(name=name, code=code, description=desc))

    db.flush()

    roles = [
        ("data_contributor", 1, "Field staff & program officers - data input only"),
        ("reviewer", 2, "Department heads & M&E - data audit & section approval"),
        ("report_generator", 3, "Grants managers & admins - trigger AI draft & edit reports"),
        ("final_approver", 4, "Executive leadership - final read-only review & PDF sign-off"),
    ]

    for name, tier, desc in roles:
        existing = db.query(Role).filter(Role.name == name).first()
        if not existing:
            db.add(Role(name=name, tier=tier, description=desc))

    db.flush()

    # Seed default users
    prog_dept = db.query(Department).filter(Department.code == "PROG").first()
    me_dept = db.query(Department).filter(Department.code == "ME").first()
    fin_dept = db.query(Department).filter(Department.code == "FIN").first()
    ahr_dept = db.query(Department).filter(Department.code == "AHR").first()
    exec_dept = db.query(Department).filter(Department.code == "EXEC").first()

    dc_role = db.query(Role).filter(Role.name == "data_contributor").first()
    rv_role = db.query(Role).filter(Role.name == "reviewer").first()
    rg_role = db.query(Role).filter(Role.name == "report_generator").first()
    fa_role = db.query(Role).filter(Role.name == "final_approver").first()

    default_users = [
        ("grace.w@inukafoundation.org", "Grace Wanjiku", dc_role.id, prog_dept.id),
        ("james.o@inukafoundation.org", "James Otieno", rv_role.id, me_dept.id),
        ("amina.h@inukafoundation.org", "Amina Hassan", dc_role.id, fin_dept.id),
        ("david.m@inukafoundation.org", "David Mwangi", rg_role.id, ahr_dept.id),
        ("sarah.n@inukafoundation.org", "Sarah Njeri", rg_role.id, ahr_dept.id),
        ("director@inukafoundation.org", "Dr. James Mwangi", fa_role.id, exec_dept.id),
        ("admin@inukafoundation.org", "System Administrator", rg_role.id, ahr_dept.id),
    ]

    for email, name, role_id, dept_id in default_users:
        existing = db.query(User).filter(User.email == email).first()
        if not existing:
            db.add(User(
                email=email,
                name=name,
                hashed_password=SHARED_HASHED,
                role_id=role_id,
                department_id=dept_id,
                status="active",
            ))

    db.commit()
