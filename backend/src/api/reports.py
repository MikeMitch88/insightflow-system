import math

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import SessionLocal, get_db
from ..models.models import Report, ReportingPeriod
from ..reporting.generator import complete_report_generation

router = APIRouter(prefix="/api", tags=["reports"])

DEFAULT_SECTIONS = [
    "executive_summary",
    "program_performance",
    "beneficiary_reach",
    "outcomes",
    "geographic_distribution",
]


class ReportCreate(BaseModel):
    title: str
    report_type: str  # executive, program_performance, donor, monday_evidence
    reporting_period_id: int
    sections: list[str] = DEFAULT_SECTIONS
    use_ai_insights: bool = False


def _serialize_report(report: Report) -> dict:
    period_name = report.reporting_period.name if report.reporting_period else None
    return {
        "id": report.id,
        "title": report.title,
        "report_type": report.report_type,
        "reporting_period_id": report.reporting_period_id,
        "period_name": period_name,
        "config": report.config_json,
        "status": report.status,
        "file_path": report.file_path,
        "created_by": report.created_by,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "completed_at": report.completed_at.isoformat() if report.completed_at else None,
    }


@router.get("/reports")
def list_reports(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page"),
    report_type: str = Query(None, description="Filter by report type"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """Paginated list of generated reports."""
    query = db.query(Report)
    if report_type:
        query = query.filter(Report.report_type == report_type.strip())
    if status:
        query = query.filter(Report.status == status.strip().lower())

    total = int(query.with_entities(func.count(Report.id)).scalar() or 0)
    items = (
        query.order_by(Report.created_at.desc(), Report.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [_serialize_report(r) for r in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, math.ceil(total / page_size)),
    }


@router.post("/reports/generate", status_code=201)
def generate_report(
    report: ReportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Create a report record, mark it as generating and schedule generation."""
    period = (
        db.query(ReportingPeriod)
        .filter(ReportingPeriod.id == report.reporting_period_id)
        .first()
    )
    if period is None:
        raise HTTPException(status_code=404, detail=f"Reporting period {report.reporting_period_id} not found")

    record = Report(
        title=report.title,
        report_type=report.report_type,
        reporting_period_id=report.reporting_period_id,
        config_json={
            "sections": report.sections or DEFAULT_SECTIONS,
            "use_ai_insights": report.use_ai_insights,
        },
        status="generating",
        created_by="api",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    background_tasks.add_task(_run_generation, record.id)
    return _serialize_report(record)


def _run_generation(report_id: int) -> None:
    """Background worker: generate data, export CSV and finalize the report."""
    db = SessionLocal()
    try:
        complete_report_generation(db, report_id)
    finally:
        db.close()


@router.get("/reports/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get a single report by ID."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return _serialize_report(report)
