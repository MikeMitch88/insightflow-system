"""Reports API module for InukaOps.

Implements the complete report lifecycle:
- Admin: Preview, Validate, Confirm, Generate, Revise, Download
- Manager: Review Queue, Approve, Reject (with mandatory reason), Download
- Role-based security (HTTP 403 for unauthorized actions)
- Audit log tracking & dynamic timeline
- Persistent notifications & unread badges
- 12-sheet Excel, CSV, and PDF exports
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import Report, ReportingPeriod, Notification, AuditLog
from ..models.schemas import (
    ReportCreate,
    ReportPreviewRequest,
    ReportValidateRequest,
    ReportGenerateRequest,
    ReportApproveRequest,
    ReportRejectRequest,
    ReportReviseRequest,
)
from ..reporting.generator import (
    generate_report_snapshot,
    generate_report_data,
    export_to_excel,
    export_to_csv,
    export_to_pdf,
    get_kpc_log_records,
)
from ..validation.report_validator import validate_report_data
from ..ai.service import analyze_report_snapshot
from ..auth.routes import (
    get_current_user_optional,
    require_manager_role,
    require_admin_or_reporter_role,
)
from .admin import _load_audit_logs, _save_audit_logs, create_notification

router = APIRouter(prefix="/api", tags=["reports"])


def _log_audit_event(
    db: Session,
    user: str,
    action: str,
    details: str,
    role: Optional[str] = None,
    report_id: Optional[int] = None,
    report_version: Optional[int] = None,
    category: str = "Report",
    comment: Optional[str] = None,
):
    """Record an audit trail event in both DB and JSON storage."""
    now_dt = datetime.now(timezone.utc)
    try:
        audit_entry = AuditLog(
            user=user,
            role=role,
            report_id=report_id,
            report_version=report_version or 1,
            action=action,
            timestamp=now_dt,
            details=details,
            comment=comment,
            category=category,
        )
        db.add(audit_entry)
        db.commit()
    except Exception:
        pass

    try:
        logs = _load_audit_logs()
        logs.insert(0, {
            "id": len(logs) + 1,
            "timestamp": now_dt.strftime("%Y-%m-%d %H:%M"),
            "user": user,
            "action": action.replace("_", " ").title(),
            "details": details,
            "category": category,
            "report_id": report_id,
            "report_version": report_version,
        })
        _save_audit_logs(logs[:100])
    except Exception:
        pass


def _get_report_timeline(db: Session, report_id: int) -> List[dict]:
    """Build the visual timeline of actions performed on this report."""
    db_logs = db.query(AuditLog).filter(AuditLog.report_id == report_id).order_by(AuditLog.timestamp.asc()).all()
    if db_logs:
        return [
            {
                "timestamp": l.timestamp.strftime("%d %b %H:%M") if l.timestamp else "Recently",
                "user": l.user,
                "role": l.role or "System",
                "action": l.action.replace("_", " ").title(),
                "details": l.details or "",
                "comment": l.comment or "",
            }
            for l in db_logs
        ]

    # Fallback to JSON logs
    logs = _load_audit_logs()
    matched = [l for l in logs if l.get("report_id") == report_id]
    if matched:
        return [
            {
                "timestamp": l.get("timestamp", ""),
                "user": l.get("user", "User"),
                "role": "Staff",
                "action": l.get("action", "Action"),
                "details": l.get("details", ""),
                "comment": "",
            }
            for l in reversed(matched)
        ]

    return [
        {
            "timestamp": datetime.now(timezone.utc).strftime("%d %b %H:%M"),
            "user": "Program Administrator",
            "role": "Administrator",
            "action": "Report Initialized",
            "details": "Report registered in system",
            "comment": "",
        }
    ]


def _serialize_report(report: Report, db: Optional[Session] = None) -> dict:
    """Format report into full API response with snapshots, approval info, and timeline."""
    period_name = report.reporting_period_name or (
        report.reporting_period.name if report.reporting_period else "August 2026"
    )
    config = dict(report.config_json or {})

    # Format status
    st = (report.status or "draft").upper()
    if st == "PENDING_MANAGER_REVIEW":
        display_status = "PENDING_MANAGER_REVIEW"
        badge_label = "Pending Manager Review"
    elif st == "APPROVED":
        display_status = "APPROVED"
        badge_label = "Approved"
    elif st == "REVISION_REQUIRED":
        display_status = "REVISION_REQUIRED"
        badge_label = "Revision Required"
    elif st == "ADMIN_REVIEW":
        display_status = "ADMIN_REVIEW"
        badge_label = "Admin Review"
    else:
        display_status = st
        badge_label = st.replace("_", " ").title()

    timeline = _get_report_timeline(db, report.id) if db else []

    return {
        "id": report.id,
        "title": report.title,
        "report_type": report.report_type,
        "reporting_period": period_name,
        "reporting_period_id": report.reporting_period_id,
        "version": report.version or 1,
        "parent_report_id": report.parent_report_id,
        "status": display_status,
        "approval_status": badge_label,
        "generated_by": report.generated_by or report.created_by or "Program Administrator",
        "generated_at": report.generated_at.isoformat() if report.generated_at else (
            report.created_at.isoformat() if report.created_at else None
        ),
        "submitted_to": report.submitted_to or "Program Manager",
        "submitted_at": report.submitted_at.isoformat() if report.submitted_at else None,
        "reviewed_by": report.reviewed_by,
        "reviewed_at": report.reviewed_at.isoformat() if report.reviewed_at else None,
        "approved_by": report.approved_by,
        "approved_at": report.approved_at.isoformat() if report.approved_at else None,
        "approval_comment": report.approval_comment or config.get("approval_notes", ""),
        "rejected_by": report.rejected_by,
        "rejected_at": report.rejected_at.isoformat() if report.rejected_at else None,
        "rejection_reason": report.rejection_reason or config.get("rejection_reason", ""),
        "rejection_feedback": report.rejection_feedback or config.get("rejection_feedback", ""),
        "validation_status": report.validation_status or "PASS",
        "validation_result": report.validation_result or {},
        "data_completeness": (report.report_snapshot or {}).get("data_completeness", 96.0),
        "data_quality_score": (report.report_snapshot or {}).get("data_quality_score", 94.0),
        "report_snapshot": report.report_snapshot or {},
        "kpi_snapshot": report.kpi_snapshot or {},
        "timeline": timeline,
        "file_path": report.file_path,
        "config": config,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "completed_at": report.completed_at.isoformat() if report.completed_at else None,
    }


# =========================================================================
# 1. ADMIN PREVIEW & VALIDATION ENDPOINTS
# =========================================================================

@router.post("/reports/preview")
def preview_report(req: ReportPreviewRequest, db: Session = Depends(get_db)):
    """
    Generate complete report preview before submission.
    Admin inspects actual numbers across all 4 pillars, KPC log, validation, and AI insights.
    Uses the exact same data-generation service as final generation.
    """
    snapshot = generate_report_snapshot(
        db=db,
        period_id=req.reporting_period_id,
        period_name=req.reporting_period,
        title=f"{req.reporting_period} {req.report_type}",
        report_type=req.report_type,
        sections=req.sections,
        use_ai_insights=req.use_ai_insights,
    )

    validation = validate_report_data(db, req.reporting_period_id, req.reporting_period)

    # Log audit
    _log_audit_event(
        db=db,
        user="Program Administrator",
        role="admin",
        action="REPORT_PREVIEWED",
        details=f"Admin previewed report for '{req.reporting_period}' ({req.report_type})",
        category="Report",
    )

    return {
        "status": "ADMIN_REVIEW",
        "reporting_period": req.reporting_period,
        "report_type": req.report_type,
        "data_completeness": validation["summary"]["completeness_score"],
        "data_quality": validation["summary"]["data_quality_score"],
        "validation_results": validation,
        "snapshot": snapshot,
        "executive_summary": snapshot.get("executive_summary", {}),
        "kpi_snapshot": snapshot.get("kpi_snapshot", {}),
        "pillar_performance": snapshot.get("pillar_performance", {}),
        "beneficiaries": snapshot.get("beneficiaries", {}),
        "outcomes": snapshot.get("outcomes", {}),
        "data_quality_data": snapshot.get("data_quality", {}),
        "kpc_log": snapshot.get("kpc_log", {}),
        "ai_insights": snapshot.get("ai_insights", {}),
    }


@router.post("/reports/validate")
def validate_report(req: ReportValidateRequest, db: Session = Depends(get_db)):
    """Run automated validation checks on reporting data."""
    results = validate_report_data(db, req.reporting_period_id, req.reporting_period)

    _log_audit_event(
        db=db,
        user="Program Administrator",
        role="admin",
        action="REPORT_VALIDATED",
        details=f"Automated validation executed: {results['status']} ({results['summary']['passed']} passed, {results['summary']['warnings']} warnings, {results['summary']['errors']} errors)",
        category="Data Quality",
    )

    return results


# =========================================================================
# 2. ADMIN GENERATION & SUBMISSION TO MANAGER
# =========================================================================

@router.post("/reports/generate", status_code=201)
def generate_and_submit_report(
    req: ReportGenerateRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Admin generates the report and sends it to the Manager for review.
    1. Generates final report snapshot.
    2. Validates checkboxes confirmation.
    3. Saves immutable snapshot.
    4. Sets status = PENDING_MANAGER_REVIEW.
    5. Dispatches persistent Manager notification.
    6. Logs audit trail.
    """
    user = get_current_user_optional(authorization) or {
        "name": "Program Administrator", "role": "admin"
    }

    # Verify confirmation checkboxes
    if not (req.confirmed_reviewed and req.confirmed_kpis and req.confirmed_warnings and req.confirmed_ready):
        raise HTTPException(
            status_code=400,
            detail="Admin confirmation required: All 4 review and validation confirmation checkboxes must be verified before generation."
        )

    # 1. Generate immutable report snapshot
    snapshot = generate_report_snapshot(
        db=db,
        period_id=req.reporting_period_id,
        period_name=req.reporting_period,
        title=req.title,
        report_type=req.report_type,
        sections=req.sections,
        use_ai_insights=req.use_ai_insights,
    )

    validation = validate_report_data(db, req.reporting_period_id, req.reporting_period)
    if validation["status"] == "ERROR":
        raise HTTPException(
            status_code=400,
            detail=f"Report cannot be generated due to critical validation errors. Please resolve errors before submission."
        )

    # 2. Save immutable Report record
    now_dt = datetime.now(timezone.utc)
    report = Report(
        title=req.title,
        report_type=req.report_type,
        reporting_period_name=req.reporting_period,
        reporting_period_id=snapshot.get("reporting_period_id"),
        version=1,
        status="pending_manager_review",
        generated_by=user.get("name", "Program Administrator"),
        generated_at=now_dt,
        submitted_to="Grace Wanjiku (Program Manager)",
        submitted_at=now_dt,
        validation_status=validation["status"],
        validation_result=validation,
        report_snapshot=snapshot,
        kpi_snapshot=snapshot.get("kpi_snapshot", {}),
        config_json={
            "sections": req.sections,
            "use_ai_insights": req.use_ai_insights,
            "approval_status": "Pending Manager Review",
        },
        created_by=user.get("name", "Program Administrator"),
        created_at=now_dt,
        completed_at=now_dt,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # 3. Export initial files
    try:
        excel_path = export_to_excel(snapshot)
        report.file_path = str(excel_path)
        db.commit()
    except Exception:
        pass

    # 4. Dispatch persistent notification to Manager
    create_notification(
        recipient_role="program_manager",
        title="🔔 NEW REPORT FOR REVIEW",
        message=f"{req.title} generated by Admin on {now_dt.strftime('%d %B %Y')}. Status: Pending Manager Review.",
        report_id=report.id,
        notif_type="NEW_REPORT_FOR_REVIEW",
    )

    # 5. Log audit trail
    _log_audit_event(
        db=db,
        user=user.get("name", "Program Administrator"),
        role=user.get("role", "admin"),
        report_id=report.id,
        report_version=1,
        action="REPORT_GENERATED",
        details=f"Generated immutable snapshot v1 for '{report.title}' ({req.reporting_period})",
        category="Report",
    )
    _log_audit_event(
        db=db,
        user=user.get("name", "Program Administrator"),
        role=user.get("role", "admin"),
        report_id=report.id,
        report_version=1,
        action="REPORT_SENT_TO_MANAGER",
        details=f"Submitted report '{report.title}' to Program Manager for review.",
        category="Workflow",
    )

    return _serialize_report(report, db)


# =========================================================================
# 3. REPORT LISTING, DETAILS & VERSIONS
# =========================================================================

@router.get("/reports")
def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    report_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    approval_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List all reports with pagination, filtering, and status matching."""
    query = db.query(Report)
    if report_type:
        query = query.filter(Report.report_type == report_type.strip())
    if status:
        query = query.filter(Report.status == status.strip().lower())
    if search:
        query = query.filter(Report.title.ilike(f"%{search.strip()}%"))

    all_items = query.order_by(Report.created_at.desc(), Report.id.desc()).all()
    serialized = [_serialize_report(r, db) for r in all_items]

    if approval_status:
        target = approval_status.strip().lower()
        serialized = [
            r for r in serialized
            if target in r.get("status", "").lower() or target in r.get("approval_status", "").lower()
        ]

    total = len(serialized)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    items = serialized[start_idx:end_idx]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, math.ceil(total / page_size)),
    }


@router.get("/reports/readiness")
def get_report_readiness(period_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """Pre-generation readiness and data quality score."""
    validation = validate_report_data(db, period_id)
    return {
        "period_id": period_id or 1,
        "period_name": validation.get("reporting_period", "August 2026"),
        "overall_completeness": validation["summary"]["completeness_score"],
        "is_ready": validation["can_generate"],
        "status_label": "High Readiness (Ready to Generate)" if validation["summary"]["completeness_score"] >= 90 else "Satisfactory",
        "data_quality_score": validation["summary"]["data_quality_score"],
        "checklist": validation["checks"],
    }


@router.get("/reports/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Fetch report details and record view in audit log."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    _log_audit_event(
        db=db,
        user="Staff",
        action="REPORT_VIEWED",
        details=f"Viewed report details for '{report.title}'",
        report_id=report.id,
        report_version=report.version,
    )

    return _serialize_report(report, db)


@router.get("/reports/{report_id}/preview")
def get_single_report_preview(report_id: int, db: Session = Depends(get_db)):
    """Fetch structured preview representation of an existing report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    snapshot = report.report_snapshot or generate_report_data(db, report_id)
    serialized = _serialize_report(report, db)
    return {
        "report": serialized,
        "title": report.title,
        "report_type": report.report_type,
        "period_name": serialized["reporting_period"],
        "status": serialized["status"],
        "approval_status": serialized["approval_status"],
        "approved_by": serialized["approved_by"],
        "approved_at": serialized["approved_at"],
        "rejected_by": serialized["rejected_by"],
        "rejected_at": serialized["rejected_at"],
        "rejection_reason": serialized["rejection_reason"],
        "rejection_feedback": serialized["rejection_feedback"],
        "snapshot": snapshot,
        "executive_summary": snapshot.get("executive_summary", {}),
        "kpi_snapshot": snapshot.get("kpi_snapshot", {}),
        "pillar_performance": snapshot.get("pillar_performance", {}),
        "beneficiaries": snapshot.get("beneficiaries", {}),
        "outcomes": snapshot.get("outcomes", {}),
        "data_quality": snapshot.get("data_quality", {}),
        "kpc_log": snapshot.get("kpc_log", {}),
        "ai_insights": snapshot.get("ai_insights", {}),
        "validation_results": report.validation_result or snapshot.get("validation_results", {}),
        "timeline": serialized.get("timeline", []),
    }


@router.get("/reports/{report_id}/versions")
def get_report_versions(report_id: int, db: Session = Depends(get_db)):
    """Get all versions in this report's revision lineage."""
    target = db.query(Report).filter(Report.id == report_id).first()
    if not target:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    # Find root report
    root_id = target.parent_report_id or target.id
    versions = db.query(Report).filter(
        (Report.id == root_id) | (Report.parent_report_id == root_id) | (Report.id == target.id)
    ).order_by(Report.version.asc()).all()

    return {
        "report_id": report_id,
        "title": target.title,
        "total_versions": len(versions),
        "versions": [_serialize_report(v, db) for v in versions],
    }


# =========================================================================
# 4. MANAGER APPROVAL & REJECTION (STRICT RBAC)
# =========================================================================

@router.post("/reports/{report_id}/approve")
def approve_report(
    report_id: int,
    body: ReportApproveRequest = ReportApproveRequest(),
    user: dict = Depends(require_manager_role),
    db: Session = Depends(get_db),
):
    """
    Manager approves a submitted report.
    Enforces RBAC: Admin, Officers, and Viewers will receive HTTP 403.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    now_dt = datetime.now(timezone.utc)
    approver_name = user.get("name", "Grace Wanjiku (Program Manager)")

    report.status = "approved"
    report.approved_by = approver_name
    report.approved_at = now_dt
    report.approval_comment = body.comment or "Verified and authorized for official reporting."
    report.reviewed_by = approver_name
    report.reviewed_at = now_dt

    config = dict(report.config_json or {})
    config["approval_status"] = "Approved"
    config["approved_by"] = approver_name
    config["approved_at"] = now_dt.isoformat()
    config["approval_notes"] = body.comment
    report.config_json = config

    db.commit()
    db.refresh(report)

    # Create persistent notification for Admin
    create_notification(
        recipient_role="admin",
        title="✅ REPORT APPROVED",
        message=f"'{report.title}' has been approved by {approver_name} on {now_dt.strftime('%d %B %Y')}.",
        report_id=report.id,
        notif_type="REPORT_APPROVED",
    )

    # Log audit event
    _log_audit_event(
        db=db,
        user=approver_name,
        role="program_manager",
        report_id=report.id,
        report_version=report.version,
        action="REPORT_APPROVED",
        details=f"Official sign-off granted by {approver_name}. Comment: {body.comment}",
        comment=body.comment,
        category="Governance",
    )

    return _serialize_report(report, db)


@router.post("/reports/{report_id}/reject")
def reject_report(
    report_id: int,
    body: ReportRejectRequest,
    user: dict = Depends(require_manager_role),
    db: Session = Depends(get_db),
):
    """
    Manager rejects a report and requests revision.
    Requires mandatory rejection reason.
    Enforces RBAC: Admin, Officers, and Viewers receive HTTP 403.
    """
    if not body.reason or len(body.reason.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required. Manager must provide specific feedback for revision."
        )

    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    now_dt = datetime.now(timezone.utc)
    reviewer_name = user.get("name", "Grace Wanjiku (Program Manager)")

    report.status = "revision_required"
    report.rejected_by = reviewer_name
    report.rejected_at = now_dt
    report.rejection_reason = body.reason.strip()
    report.rejection_feedback = body.feedback or body.reason.strip()
    report.reviewed_by = reviewer_name
    report.reviewed_at = now_dt

    config = dict(report.config_json or {})
    config["approval_status"] = "Revision Required"
    config["rejected_by"] = reviewer_name
    config["rejected_at"] = now_dt.isoformat()
    config["rejection_reason"] = body.reason.strip()
    config["rejection_feedback"] = body.feedback
    report.config_json = config

    db.commit()
    db.refresh(report)

    # Create persistent notification for Admin
    create_notification(
        recipient_role="admin",
        title="🔴 REPORT REQUIRES REVISION",
        message=f"'{report.title}' has been rejected by {reviewer_name}. Reason: {body.reason}",
        report_id=report.id,
        notif_type="REPORT_REVISION_REQUIRED",
    )

    # Log audit event
    _log_audit_event(
        db=db,
        user=reviewer_name,
        role="program_manager",
        report_id=report.id,
        report_version=report.version,
        action="REPORT_REVISION_REQUIRED",
        details=f"Returned for revision by {reviewer_name}. Reason: {body.reason}",
        comment=body.reason,
        category="Governance",
    )

    return _serialize_report(report, db)


# =========================================================================
# 5. ADMIN REVISION ENDPOINT
# =========================================================================

@router.post("/reports/{report_id}/revise")
def revise_report(
    report_id: int,
    body: ReportReviseRequest = ReportReviseRequest(),
    user: dict = Depends(require_admin_or_reporter_role),
    db: Session = Depends(get_db),
):
    """
    Admin creates a new version of a rejected report (e.g. Version 2).
    Generates fresh snapshot, sets status = PENDING_MANAGER_REVIEW,
    notifies Manager, and maintains version lineage without overwriting history.
    """
    parent = db.query(Report).filter(Report.id == report_id).first()
    if parent is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    next_version = (parent.version or 1) + 1
    new_title = f"{parent.title.split(' - Version')[0]} - Version {next_version}"

    # Generate fresh snapshot with latest data
    snapshot = generate_report_snapshot(
        db=db,
        period_id=parent.reporting_period_id,
        period_name=parent.reporting_period_name,
        title=new_title,
        report_type=parent.report_type,
    )
    validation = validate_report_data(db, parent.reporting_period_id, parent.reporting_period_name)

    now_dt = datetime.now(timezone.utc)
    new_report = Report(
        title=new_title,
        report_type=parent.report_type,
        reporting_period_name=parent.reporting_period_name,
        reporting_period_id=parent.reporting_period_id,
        version=next_version,
        parent_report_id=parent.parent_report_id or parent.id,
        status="pending_manager_review",
        generated_by=user.get("name", "Program Administrator"),
        generated_at=now_dt,
        submitted_to="Grace Wanjiku (Program Manager)",
        submitted_at=now_dt,
        validation_status=validation["status"],
        validation_result=validation,
        report_snapshot=snapshot,
        kpi_snapshot=snapshot.get("kpi_snapshot", {}),
        config_json={
            "sections": (parent.config_json or {}).get("sections", []),
            "use_ai_insights": True,
            "approval_status": "Pending Manager Review",
            "revision_notes": body.notes,
        },
        created_by=user.get("name", "Program Administrator"),
        created_at=now_dt,
        completed_at=now_dt,
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    # Notify Manager of resubmission
    create_notification(
        recipient_role="program_manager",
        title="🔔 NEW REPORT FOR REVIEW",
        message=f"Admin submitted revised report '{new_report.title}' for review.",
        report_id=new_report.id,
        notif_type="REPORT_RESUBMITTED",
    )

    # Audit log
    _log_audit_event(
        db=db,
        user=user.get("name", "Program Administrator"),
        role=user.get("role", "admin"),
        report_id=new_report.id,
        report_version=next_version,
        action="REPORT_RESUBMITTED",
        details=f"Admin created and resubmitted Version {next_version} for review. Notes: {body.notes or 'Updated figures.'}",
        category="Workflow",
    )

    return _serialize_report(new_report, db)


# =========================================================================
# 6. DOWNLOADS & AI INSIGHTS
# =========================================================================

@router.get("/reports/{report_id}/download/excel")
@router.get("/reports/{report_id}/download")
def download_report_excel(
    report_id: int,
    format: str = Query("xlsx"),
    db: Session = Depends(get_db),
):
    """Download 12-sheet Excel or CSV export."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    snapshot = report.report_snapshot or generate_report_data(db, report_id)
    safe_title = report.title.replace(" ", "_").replace("/", "-")[:50]

    _log_audit_event(
        db=db,
        user="Staff",
        action="REPORT_DOWNLOADED",
        details=f"Downloaded {format.upper()} for '{report.title}'",
        report_id=report.id,
        report_version=report.version,
    )

    if format.lower() == "csv":
        filepath = export_to_csv(snapshot)
        return FileResponse(
            path=str(filepath),
            filename=f"{safe_title}.csv",
            media_type="text/csv",
        )

    filepath = export_to_excel(snapshot)
    return FileResponse(
        path=str(filepath),
        filename=f"{safe_title}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/reports/{report_id}/download/csv")
def download_report_csv(report_id: int, db: Session = Depends(get_db)):
    """Download CSV format of the report snapshot."""
    return download_report_excel(report_id=report_id, format="csv", db=db)


@router.get("/reports/{report_id}/download/pdf")
def download_report_pdf(report_id: int, db: Session = Depends(get_db)):
    """Download formatted Printable / PDF version of report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    snapshot = report.report_snapshot or generate_report_data(db, report_id)
    filepath = export_to_pdf(snapshot)
    safe_title = report.title.replace(" ", "_").replace("/", "-")[:50]

    _log_audit_event(
        db=db,
        user="Staff",
        action="REPORT_DOWNLOADED",
        details=f"Downloaded PDF document for '{report.title}'",
        report_id=report.id,
        report_version=report.version,
    )

    return FileResponse(
        path=str(filepath),
        filename=f"{safe_title}.html",
        media_type="text/html",
    )


@router.get("/reports/{report_id}/ai-insights")
def get_report_ai_insights(report_id: int, db: Session = Depends(get_db)):
    """Get AI Insights grounded strictly in this report's frozen snapshot."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    snapshot = report.report_snapshot or generate_report_data(db, report_id)
    return analyze_report_snapshot(snapshot)
