"""Workflow API: Donor report approval workflow with state machine."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.database import get_db
from src.models.models import DonorReport, ApprovalRecord, AuditLog, User
from src.models.schemas import DonorReportCreate, DonorReportOut, ApprovalAction, AuditLogOut
from src.auth.rbac import get_current_user, require_tier, log_audit_event
from src.workflow.engine import WorkflowEngine

router = APIRouter(prefix="/api/workflow", tags=["workflow"])


@router.get("/states")
def get_workflow_states(user: User = Depends(get_current_user)):
    engine = WorkflowEngine(None)
    return engine.get_workflow_status()


@router.get("/reports", response_model=list[DonorReportOut])
def list_donor_reports(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    tier: Optional[int] = Query(None),
):
    q = db.query(DonorReport)
    if status:
        q = q.filter(DonorReport.workflow_status == status)
    if tier:
        q = q.filter(DonorReport.current_tier == tier)
    return q.order_by(desc(DonorReport.updated_at)).all()


@router.post("/reports", response_model=DonorReportOut)
def create_donor_report(
    data: DonorReportCreate,
    user: User = Depends(require_tier(1)),
    db: Session = Depends(get_db),
):
    report = DonorReport(
        title=data.title,
        reporting_period_id=data.reporting_period_id,
        donor_name=data.donor_name,
        sections_json=data.sections_json,
        created_by=user.id,
        workflow_status="drafting",
        current_tier=1,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    log_audit_event(db, user.id, "create_donor_report", "donor_report", report.id, data.model_dump())
    return report


@router.get("/reports/{report_id}")
def get_donor_report(
    report_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = WorkflowEngine(db)
    result = engine.get_report_workflow(report_id)
    if not result:
        raise HTTPException(status_code=404, detail="Report not found")
    return result


@router.post("/reports/{report_id}/transition")
def transition_report(
    report_id: int,
    action_data: ApprovalAction,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = WorkflowEngine(db)
    try:
        result = engine.transition(
            report_id=report_id,
            user=user,
            action=action_data.action,
            comments=action_data.comments,
            changes_json=action_data.changes_json,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reports/{report_id}/approve")
def approve_report(
    report_id: int,
    comments: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = WorkflowEngine(db)
    try:
        result = engine.transition(
            report_id=report_id,
            user=user,
            action="approve",
            comments=comments,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reports/{report_id}/reject")
def reject_report(
    report_id: int,
    comments: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    engine = WorkflowEngine(db)
    try:
        result = engine.transition(
            report_id=report_id,
            user=user,
            action="reject",
            comments=comments,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reports/{report_id}/submit")
def submit_for_review(
    report_id: int,
    user: User = Depends(require_tier(1)),
    db: Session = Depends(get_db),
):
    engine = WorkflowEngine(db)
    try:
        result = engine.transition(
            report_id=report_id,
            user=user,
            action="submit_for_review",
            comments="Submitted for Tier 2 review",
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# AUDIT TRAIL
# ============================================================

@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    user: User = Depends(require_tier(2)),
    db: Session = Depends(get_db),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    q = db.query(AuditLog)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    if action:
        q = q.filter(AuditLog.action == action)
    return q.order_by(desc(AuditLog.timestamp)).limit(limit).all()
