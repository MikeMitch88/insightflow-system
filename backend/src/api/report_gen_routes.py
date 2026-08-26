"""Report Generation API: Triggers AI-powered 6-section donor report generation."""

import os
from typing import Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.models import DonorReport, User, EditLock, EditHistory
from src.auth.rbac import get_current_user, require_tier, log_audit_event
from src.reporting.donor_report_generator import DonorReportGenerator, REPORT_SECTIONS

router = APIRouter(prefix="/api/report-gen", tags=["report-generation"])


@router.get("/sections")
def get_report_sections(user: User = Depends(get_current_user)):
    return REPORT_SECTIONS


@router.get("/donor-reports")
def list_donor_reports(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reports = db.query(DonorReport).order_by(DonorReport.updated_at.desc()).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "donor_name": r.donor_name,
            "workflow_status": r.workflow_status,
            "current_tier": r.current_tier,
            "sections_generated": len(r.ai_generated_content or {}),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]


@router.post("/donor-reports")
def create_donor_report(
    title: str,
    donor_name: Optional[str] = None,
    reporting_period_id: Optional[int] = None,
    user: User = Depends(require_tier(1)),
    db: Session = Depends(get_db),
):
    report = DonorReport(
        title=title,
        donor_name=donor_name,
        reporting_period_id=reporting_period_id,
        created_by=user.id,
        workflow_status="drafting",
        current_tier=1,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    log_audit_event(db, user.id, "create_donor_report", "donor_report", report.id, {"title": title})
    return {"id": report.id, "title": report.title, "workflow_status": report.workflow_status}


@router.post("/donor-reports/{report_id}/generate-section/{section_id}")
def generate_section(
    report_id: int,
    section_id: str,
    user: User = Depends(require_tier(3)),
    db: Session = Depends(get_db),
):
    generator = DonorReportGenerator(db)
    try:
        result = generator.generate_section(report_id, section_id, user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/donor-reports/{report_id}/generate-all")
def generate_all_sections(
    report_id: int,
    user: User = Depends(require_tier(3)),
    db: Session = Depends(get_db),
):
    generator = DonorReportGenerator(db)
    try:
        result = generator.generate_all_sections(report_id, user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/donor-reports/{report_id}/ingest-data")
def ingest_data_to_vector_store(
    report_id: int,
    user: User = Depends(require_tier(3)),
    db: Session = Depends(get_db),
):
    generator = DonorReportGenerator(db)
    if generator.rag_pipeline:
        stats = generator.rag_pipeline.ingest_all_project_data(db)
        log_audit_event(db, user.id, "ingest_vector_data", "donor_report", report_id, stats)
        return {"status": "ingested", "stats": stats}
    return {"status": "skipped", "message": "RAG pipeline not available"}


@router.get("/donor-reports/{report_id}/content")
def get_report_content(
    report_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = db.query(DonorReport).filter(DonorReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "id": report.id,
        "title": report.title,
        "donor_name": report.donor_name,
        "workflow_status": report.workflow_status,
        "sections": report.ai_generated_content or {},
        "sections_json": report.sections_json,
        "llm_provider": report.ai_generated_content.get("executive_summary", {}).get("provider", "unknown") if report.ai_generated_content else "unknown",
    }


@router.get("/donor-reports/{report_id}/stats")
def get_vector_store_stats(
    report_id: int,
    user: User = Depends(get_current_user),
):
    try:
        from ai_services.rag.vector_store import FAISSVectorStore
        store = FAISSVectorStore()
        return store.get_stats()
    except ImportError:
        return {"status": "unavailable", "message": "FAISS not installed"}


# ============================================================
# PDF EXPORT
# ============================================================

@router.get("/donor-reports/{report_id}/export-pdf")
def export_report_pdf(
    report_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from src.services.pdf_export import generate_report_pdf

    report = db.query(DonorReport).filter(DonorReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    filepath = generate_report_pdf(
        report_id=report.id,
        title=report.title,
        donor_name=report.donor_name,
        workflow_status=report.workflow_status,
        ai_content=report.ai_generated_content or {},
        created_at=report.created_at.isoformat() if report.created_at else None,
    )

    report.final_pdf_path = filepath
    db.commit()

    log_audit_event(db, user.id, "export_pdf", "donor_report", report_id, {"filepath": filepath})

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=f"{report.title.replace(' ', '_')}.pdf",
    )


# ============================================================
# COLLABORATIVE EDITING
# ============================================================

LOCK_DURATION_MINUTES = 30


@router.post("/donor-reports/{report_id}/sections/{section_id}/lock")
def lock_section(
    report_id: int,
    section_id: str,
    user: User = Depends(require_tier(3)),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    existing = (
        db.query(EditLock)
        .filter(
            EditLock.donor_report_id == report_id,
            EditLock.section_id == section_id,
            EditLock.active == True,
        )
        .first()
    )

    if existing:
        if existing.expires_at > now and existing.user_id != user.id:
            lock_owner = db.query(User).filter(User.id == existing.user_id).first()
            raise HTTPException(
                status_code=409,
                detail=f"Section is being edited by {lock_owner.name if lock_owner else 'another user'}. Try again in {(existing.expires_at - now).seconds // 60} minutes.",
            )
        if existing.user_id == user.id:
            existing.expires_at = now + timedelta(minutes=LOCK_DURATION_MINUTES)
            db.commit()
            return {"locked": True, "expires_at": existing.expires_at.isoformat(), "section": section_id}

        existing.active = False
        db.commit()

    lock = EditLock(
        donor_report_id=report_id,
        section_id=section_id,
        user_id=user.id,
        expires_at=now + timedelta(minutes=LOCK_DURATION_MINUTES),
        active=True,
    )
    db.add(lock)
    db.commit()

    log_audit_event(db, user.id, "lock_section", "donor_report", report_id, {"section": section_id})

    return {"locked": True, "expires_at": lock.expires_at.isoformat(), "section": section_id}


@router.post("/donor-reports/{report_id}/sections/{section_id}/unlock")
def unlock_section(
    report_id: int,
    section_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lock = (
        db.query(EditLock)
        .filter(
            EditLock.donor_report_id == report_id,
            EditLock.section_id == section_id,
            EditLock.user_id == user.id,
            EditLock.active == True,
        )
        .first()
    )
    if lock:
        lock.active = False
        db.commit()
    return {"unlocked": True, "section": section_id}


@router.get("/donor-reports/{report_id}/sections/{section_id}/editors")
def get_section_editors(
    report_id: int,
    section_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    locks = (
        db.query(EditLock)
        .filter(
            EditLock.donor_report_id == report_id,
            EditLock.section_id == section_id,
            EditLock.active == True,
            EditLock.expires_at > now,
        )
        .all()
    )

    editors = []
    for lock in locks:
        owner = db.query(User).filter(User.id == lock.user_id).first()
        if owner:
            editors.append({
                "user_id": owner.id,
                "name": owner.name,
                "locked_at": lock.locked_at.isoformat() if lock.locked_at else None,
                "expires_at": lock.expires_at.isoformat() if lock.expires_at else None,
                "is_self": owner.id == user.id,
            })

    return {"editors": editors, "section": section_id}


@router.post("/donor-reports/{report_id}/sections/{section_id}/save")
def save_section_content(
    report_id: int,
    section_id: str,
    content: dict,
    user: User = Depends(require_tier(3)),
    db: Session = Depends(get_db),
):
    report = db.query(DonorReport).filter(DonorReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    lock = (
        db.query(EditLock)
        .filter(
            EditLock.donor_report_id == report_id,
            EditLock.section_id == section_id,
            EditLock.user_id == user.id,
            EditLock.active == True,
        )
        .first()
    )
    if not lock:
        raise HTTPException(status_code=409, detail="You must lock this section before editing")

    old_content = {}
    if report.ai_generated_content and section_id in report.ai_generated_content:
        old_content = report.ai_generated_content[section_id]

    history = EditHistory(
        donor_report_id=report_id,
        section_id=section_id,
        user_id=user.id,
        content_snapshot=old_content,
    )
    db.add(history)

    if not report.ai_generated_content:
        report.ai_generated_content = {}
    report.ai_generated_content[section_id] = {
        "content": content.get("content", ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "edited_by": user.name,
        "edited_at": datetime.now(timezone.utc).isoformat(),
    }
    report.updated_at = datetime.now(timezone.utc)
    db.commit()

    log_audit_event(
        db, user.id, "save_section", "donor_report", report_id,
        {"section": section_id},
    )

    return {"saved": True, "section": section_id}


@router.get("/donor-reports/{report_id}/sections/{section_id}/history")
def get_section_history(
    report_id: int,
    section_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history = (
        db.query(EditHistory)
        .filter(
            EditHistory.donor_report_id == report_id,
            EditHistory.section_id == section_id,
        )
        .order_by(EditHistory.edited_at.desc())
        .limit(20)
        .all()
    )

    result = []
    for h in history:
        editor = db.query(User).filter(User.id == h.user_id).first()
        result.append({
            "id": h.id,
            "user": editor.name if editor else "Unknown",
            "edited_at": h.edited_at.isoformat() if h.edited_at else None,
            "has_snapshot": h.content_snapshot is not None,
        })

    return {"history": result, "section": section_id}
