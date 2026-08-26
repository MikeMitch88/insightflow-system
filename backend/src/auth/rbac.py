"""RBAC Middleware: Enforces 4-tier role-based access control."""

from functools import wraps
from typing import Callable, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.models import User, Role, Permission, RolePermission, AuditLog
from src.auth.service import decode_token

security = HTTPBearer(auto_error=False)


# ============================================================
# RBAC TIER DEFINITIONS
# ============================================================

TIER_DEFINITIONS = {
    1: {
        "name": "Data Contributor",
        "description": "Field staff & program officers - data input only",
        "max_actions": ["create", "read_own", "update_own"],
        "resources": ["kpi_metrics", "financial_items", "risks", "field_notes", "projects"],
    },
    2: {
        "name": "Reviewer",
        "description": "Department heads & M&E - data audit & section approval",
        "max_actions": ["create", "read_department", "update_department", "verify", "approve_section"],
        "resources": [
            "kpi_metrics", "financial_items", "risks", "field_notes", "projects",
            "reports", "audit_logs",
        ],
    },
    3: {
        "name": "Report Generator",
        "description": "Grants managers & admins - trigger AI draft & edit reports",
        "max_actions": [
            "create", "read_all", "update_all", "verify", "generate_report",
            "edit_report", "approve_section",
        ],
        "resources": [
            "kpi_metrics", "financial_items", "risks", "field_notes", "projects",
            "reports", "donor_reports", "audit_logs", "users",
        ],
    },
    4: {
        "name": "Final Approver",
        "description": "Executive leadership - final read-only review & PDF sign-off",
        "max_actions": ["read_all", "final_approve", "export", "sign_off"],
        "resources": [
            "kpi_metrics", "financial_items", "risks", "field_notes", "projects",
            "reports", "donor_reports", "audit_logs", "users", "departments",
        ],
    },
}

WORKFLOW_TRANSITIONS = {
    "drafting": {"allowed_tiers": [1, 3], "next": "tier_2_verification"},
    "tier_2_verification": {"allowed_tiers": [2], "next": "tier_3_assembly"},
    "tier_3_assembly": {"allowed_tiers": [3], "next": "tier_4_final_sign_off"},
    "tier_4_final_sign_off": {"allowed_tiers": [4], "next": "exported_sent"},
    "exported_sent": {"allowed_tiers": [], "next": None},
}


# ============================================================
# CURRENT USER EXTRACTION
# ============================================================

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = int(payload.get("sub", 0))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.status != "active":
        raise HTTPException(status_code=403, detail="Account is inactive")

    return user


def get_current_user_payload(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


# ============================================================
# TIER-BASED ACCESS CHECKS
# ============================================================

def require_tier(minimum_tier: int):
    """Dependency that requires the user to have at least the specified tier."""

    def _check(user: User = Depends(get_current_user)) -> User:
        if not user.role or user.role.tier < minimum_tier:
            raise HTTPException(
                status_code=403,
                detail=f"Requires tier {minimum_tier} ({TIER_DEFINITIONS.get(minimum_tier, {}).get('name', 'Unknown')}) or higher",
            )
        return user

    return _check


def require_role(role_name: str):
    """Dependency that requires a specific role name."""

    def _check(user: User = Depends(get_current_user)) -> User:
        if not user.role or user.role.name != role_name:
            raise HTTPException(
                status_code=403,
                detail=f"Requires role '{role_name}'",
            )
        return user

    return _check


def require_any_role(*role_names: str):
    """Dependency that requires one of the specified role names."""

    def _check(user: User = Depends(get_current_user)) -> User:
        if not user.role or user.role.name not in role_names:
            raise HTTPException(
                status_code=403,
                detail=f"Requires one of roles: {', '.join(role_names)}",
            )
        return user

    return _check


def require_permission(resource: str, action: str):
    """Dependency that checks if user's role has the specified permission."""

    def _check(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        if not user.role:
            raise HTTPException(status_code=403, detail="No role assigned")

        has_perm = (
            db.query(RolePermission)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .filter(
                RolePermission.role_id == user.role_id,
                Permission.resource == resource,
                Permission.action == action,
            )
            .first()
        )

        if not has_perm and user.role.tier < 3:
            raise HTTPException(
                status_code=403,
                detail=f"Missing permission: {resource}:{action}",
            )

        return user

    return _check


# ============================================================
# WORKFLOW ACCESS CHECKS
# ============================================================

def can_access_workflow(user: User, workflow_status: str, action: str) -> bool:
    """Check if a user can perform an action on a workflow in the given status."""
    if not user.role:
        return False

    tier = user.role.tier
    transitions = WORKFLOW_TRANSITIONS.get(workflow_status)
    if not transitions:
        return False

    if action == "transition":
        return tier in transitions["allowed_tiers"]
    elif action == "read":
        return True
    elif action == "edit":
        return workflow_status == "drafting" and tier in [1, 3]
    elif action == "final_approve":
        return workflow_status == "tier_4_final_sign_off" and tier == 4

    return False


# ============================================================
# AUDIT LOGGING
# ============================================================

def log_audit_event(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    changes_json: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Create an immutable audit log entry."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes_json=changes_json,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
