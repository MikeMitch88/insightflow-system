"""Workflow State Machine: Manages sequential approval flow for donor reports."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from src.models.models import (
    DonorReport, ApprovalRecord, AuditLog, User, Role
)
from src.auth.rbac import log_audit_event
from src.services.notification_service import notify_workflow_transition


WORKFLOW_STATES = {
    "drafting": {
        "label": "Drafting",
        "description": "Initial draft creation and data entry",
        "allowed_tiers": [1, 3],
        "allowed_actions": ["save_draft", "submit_for_review"],
        "next_state": "tier_2_verification",
        "next_label": "Tier 2 Verification",
    },
    "tier_2_verification": {
        "label": "Tier 2 Verification",
        "description": "Department heads & M&E review data accuracy",
        "allowed_tiers": [2, 3],
        "allowed_actions": ["approve", "reject", "request_changes"],
        "next_state": "tier_3_assembly",
        "next_label": "Tier 3 Assembly",
    },
    "tier_3_assembly": {
        "label": "Tier 3 Assembly",
        "description": "Grants managers compile AI-generated sections",
        "allowed_tiers": [3],
        "allowed_actions": ["assemble_report", "edit_content", "submit_for_final_approval"],
        "next_state": "tier_4_final_sign_off",
        "next_label": "Tier 4 Final Sign-Off",
    },
    "tier_4_final_sign_off": {
        "label": "Tier 4 Final Sign-Off",
        "description": "Executive leadership final review & PDF sign-off",
        "allowed_tiers": [4],
        "allowed_actions": ["approve", "reject", "request_changes"],
        "next_state": "exported_sent",
        "next_label": "Exported/Sent",
    },
    "exported_sent": {
        "label": "Exported/Sent",
        "description": "Report has been finalized, exported, and sent to donor",
        "allowed_tiers": [],
        "allowed_actions": [],
        "next_state": None,
        "next_label": None,
    },
}


class WorkflowEngine:
    """Manages the sequential state transitions for donor report approvals."""

    def __init__(self, db: Session):
        self.db = db

    def get_workflow_status(self) -> list[dict]:
        """Return all workflow states with their metadata."""
        return [
            {
                "state": state,
                "label": info["label"],
                "description": info["description"],
                "allowed_tiers": info["allowed_tiers"],
                "next_state": info["next_state"],
            }
            for state, info in WORKFLOW_STATES.items()
        ]

    def get_report_workflow(self, report_id: int) -> Optional[dict]:
        """Get the current workflow state and history for a report."""
        report = self.db.query(DonorReport).filter(DonorReport.id == report_id).first()
        if not report:
            return None

        approvals = (
            self.db.query(ApprovalRecord)
            .filter(ApprovalRecord.donor_report_id == report_id)
            .order_by(ApprovalRecord.actioned_at.desc())
            .all()
        )

        state_info = WORKFLOW_STATES.get(report.workflow_status, {})

        return {
            "report_id": report.id,
            "title": report.title,
            "current_state": report.workflow_status,
            "current_label": state_info.get("label", "Unknown"),
            "current_tier": report.current_tier,
            "next_state": state_info.get("next_state"),
            "can_transition": len(state_info.get("allowed_tiers", [])) > 0,
            "approval_history": [
                {
                    "id": a.id,
                    "tier": a.tier,
                    "action": a.action,
                    "reviewer_id": a.reviewer_id,
                    "comments": a.comments,
                    "actioned_at": a.actioned_at.isoformat() if a.actioned_at else None,
                }
                for a in approvals
            ],
        }

    def transition(
        self,
        report_id: int,
        user: User,
        action: str,
        comments: Optional[str] = None,
        changes_json: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> dict:
        """
        Attempt a workflow transition.

        Args:
            report_id: The donor report ID
            user: The user attempting the transition
            action: The action to perform (approve, reject, submit_for_review, etc.)
            comments: Optional comments
            changes_json: Optional changes data
            ip_address: Optional IP for audit logging

        Returns:
            dict with transition result

        Raises:
            ValueError: If transition is not allowed
        """
        report = self.db.query(DonorReport).filter(DonorReport.id == report_id).first()
        if not report:
            raise ValueError("Report not found")

        if not user.role:
            raise ValueError("User has no role assigned")

        current_state = report.workflow_status
        state_info = WORKFLOW_STATES.get(current_state)

        if not state_info:
            raise ValueError(f"Unknown workflow state: {current_state}")

        # Check tier authorization
        user_tier = user.role.tier
        if user_tier not in state_info["allowed_tiers"] and action != "submit_for_review":
            raise ValueError(
                f"Tier {user_tier} not authorized for action '{action}' in state '{current_state}'"
            )

        # Determine new state
        new_state = None
        new_tier = report.current_tier

        if action == "submit_for_review":
            if current_state == "drafting":
                new_state = "tier_2_verification"
                new_tier = 2
            else:
                raise ValueError(f"Cannot submit for review from state '{current_state}'")

        elif action == "approve":
            if current_state == "tier_2_verification":
                new_state = "tier_3_assembly"
                new_tier = 3
            elif current_state == "tier_4_final_sign_off":
                new_state = "exported_sent"
                new_tier = 4
            else:
                raise ValueError(f"Cannot approve in state '{current_state}'")

        elif action == "reject":
            new_state = "drafting"
            new_tier = 1

        elif action == "request_changes":
            if current_state in ["tier_2_verification", "tier_4_final_sign_off"]:
                new_state = "drafting"
                new_tier = 1
            else:
                raise ValueError(f"Cannot request changes in state '{current_state}'")

        elif action in ("assemble_report", "submit_for_final_approval"):
            if current_state == "tier_3_assembly":
                new_state = "tier_4_final_sign_off"
                new_tier = 4
            else:
                raise ValueError(f"Cannot assemble report from state '{current_state}'")

        elif action == "edit_content":
            if current_state == "tier_3_assembly":
                new_state = "tier_3_assembly"
                new_tier = 3
            else:
                raise ValueError(f"Cannot edit content in state '{current_state}'")

        elif action == "save_draft":
            if current_state == "drafting":
                new_state = "drafting"
                new_tier = 1
            else:
                raise ValueError(f"Cannot save draft in state '{current_state}'")

        else:
            raise ValueError(f"Unknown action: {action}")

        # Record approval
        approval = ApprovalRecord(
            donor_report_id=report_id,
            tier=user_tier,
            action=action,
            reviewer_id=user.id,
            comments=comments,
            changes_json=changes_json,
        )
        self.db.add(approval)

        # Update report state
        old_state = report.workflow_status
        report.workflow_status = new_state
        report.current_tier = new_tier
        report.updated_at = datetime.now(timezone.utc)

        self.db.commit()

        # Send email notifications
        try:
            self._send_transition_notifications(
                report, user, action, old_state, new_state, comments
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Notification failed: {e}")

        # Audit log
        log_audit_event(
            self.db,
            user.id,
            f"workflow_{action}",
            "donor_report",
            report_id,
            changes_json={
                "old_state": old_state,
                "new_state": new_state,
                "action": action,
                "comments": comments,
            },
            ip_address=ip_address,
        )

        new_state_info = WORKFLOW_STATES.get(new_state, {})

        return {
            "report_id": report_id,
            "previous_state": old_state,
            "new_state": new_state,
            "new_label": new_state_info.get("label", "Unknown"),
            "current_tier": new_tier,
            "action": action,
            "message": f"Successfully transitioned to '{new_state_info.get('label', new_state)}'",
            "notifications": getattr(self, '_last_notifications', {}),
        }

    def _send_transition_notifications(
        self,
        report: DonorReport,
        actor: User,
        action: str,
        old_state: str,
        new_state: str,
        comments: Optional[str],
    ):
        new_state_info = WORKFLOW_STATES.get(new_state, {})
        target_tiers = new_state_info.get("allowed_tiers", [])
        if not target_tiers and new_state != "exported_sent":
            return

        if new_state == "exported_sent":
            target_tiers = [1, 2, 3, 4]

        recipients = (
            self.db.query(User)
            .join(Role, User.role_id == Role.id)
            .filter(Role.tier.in_(target_tiers), User.status == "active")
            .all()
        )

        emails = [u.email for u in recipients if u.email != actor.email]
        names = [u.name for u in recipients if u.email != actor.email]

        if emails:
            result = notify_workflow_transition(
                report_title=report.title,
                report_id=report.id,
                action=action,
                old_state=old_state,
                new_state=new_state,
                actor_name=actor.name,
                actor_email=actor.email,
                recipient_emails=emails,
                recipient_names=names,
                comments=comments,
            )
            self._last_notifications = result
