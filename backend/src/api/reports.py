"""Reports API — synchronous generation for reliable hackathon demo."""

import math
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import Report, ReportingPeriod
from ..reporting.generator import generate_report_data, export_to_excel, export_to_csv

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
    report_type: str
    reporting_period_id: int
    sections: list[str] = DEFAULT_SECTIONS
    use_ai_insights: bool = False


class AddInsightToReport(BaseModel):
    insight_text: str
    kpis: list[dict] = []
    recommendation: str = ""


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
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    report_type: str = Query(None),
    status: str = Query(None),
    db: Session = Depends(get_db),
):
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
def generate_report(report: ReportCreate, db: Session = Depends(get_db)):
    period = db.query(ReportingPeriod).filter(ReportingPeriod.id == report.reporting_period_id).first()
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

    try:
        report_data = generate_report_data(db, record.id)
        excel_path = export_to_excel(report_data)
        record.status = "completed"
        record.file_path = str(excel_path)
        record.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(record)
    except Exception as e:
        record.status = "failed"
        record.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

    return _serialize_report(record)


@router.get("/reports/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return _serialize_report(report)


<<<<<<< HEAD
@router.post("/reports/{report_id}/add-insight")
def add_insight_to_report(report_id: int, body: AddInsightToReport, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    config = dict(report.config_json or {})
    insights = config.get("ai_insights", [])
    insights.append({
        "text": body.insight_text,
        "kpis": body.kpis,
        "recommendation": body.recommendation,
        "added_at": datetime.utcnow().isoformat(),
    })
    config["ai_insights"] = insights
    config["use_ai_insights"] = True
    report.config_json = config
    db.commit()
    db.refresh(report)
    return _serialize_report(report)
=======
@router.get("/reports/{report_id}/insights")
def get_report_insights(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    if report.status != "completed":
        raise HTTPException(status_code=400, detail="Report has not completed yet")

    report_data = generate_report_data(db, report_id)
    return {
        "id": report.id,
        "title": report.title,
        "report_type": report.report_type,
        "period_name": report.reporting_period.name if report.reporting_period else None,
        "sections": report_data.get("sections", {}),
    }
>>>>>>> 992c6da (ai assistatnce)


@router.get("/reports/{report_id}/download")
def download_report(report_id: int, format: str = Query("xlsx", regex="^(xlsx|csv)$"), db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    if report.status != "completed":
        raise HTTPException(status_code=400, detail="Report has not completed yet")

    report_data = generate_report_data(db, report_id)
    safe_title = report.title.replace(" ", "_").replace("/", "-")[:50]

    if format == "csv":
        filepath = export_to_csv(report_data)
        media_type = "text/csv"
        ext = "csv"
    else:
        filepath = export_to_excel(report_data)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"

    return FileResponse(
        path=str(filepath),
        filename=f"{safe_title}.{ext}",
        media_type=media_type,
    )


def auto_generate_reports(db: Session) -> None:
    """Generate one report per reporting period on startup / pipeline completion."""
    periods = db.query(ReportingPeriod).order_by(ReportingPeriod.id).all()
    existing = {(r.reporting_period_id, r.report_type) for r in db.query(Report).all()}

    for period in periods:
        if (period.id, "executive") in existing:
            continue

        record = Report(
            title=f"{period.name} Executive Summary",
            report_type="executive",
            reporting_period_id=period.id,
            config_json={"sections": DEFAULT_SECTIONS, "use_ai_insights": False},
            status="generating",
            created_by="system",
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        try:
            report_data = generate_report_data(db, record.id)
            excel_path = export_to_excel(report_data)
            record.status = "completed"
            record.file_path = str(excel_path)
            record.completed_at = datetime.utcnow()
            db.commit()
        except Exception:
            record.status = "failed"
            record.completed_at = datetime.utcnow()
            db.commit()
