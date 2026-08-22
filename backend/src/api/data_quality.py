from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..analytics import kpi_engine
from ..database import get_db

router = APIRouter(prefix="/api", tags=["data-quality"])

from ..models.models import Beneficiary, ProgramEnrollment, Attendance, Outcome

DATA_SOURCES = [
    {"name": "beneficiaries", "file": "beneficiaries.csv", "status": "loaded", "records": None},
    {"name": "scholarship", "file": "scholarship.csv", "status": "loaded", "records": None},
    {"name": "plus", "file": "plus.csv", "status": "loaded", "records": None},
    {"name": "vocational", "file": "vocational.csv", "status": "loaded", "records": None},
    {"name": "tech", "file": "tech.csv", "status": "loaded", "records": None},
    {"name": "attendance", "file": "attendance.csv", "status": "loaded", "records": None},
    {"name": "outcomes", "file": "outcomes.csv", "status": "loaded", "records": None},
]


@router.get("/data-quality")
def data_quality(db: Session = Depends(get_db)):
    """Data quality score and issue breakdown from the issues table."""
    return kpi_engine.get_data_quality_summary(db)


@router.get("/data-sources")
def data_sources(db: Session = Depends(get_db)):
    """List of pipeline data sources with dynamic record counts from database."""
    beneficiary_count = db.query(Beneficiary).count()
    attendance_count = db.query(Attendance).count()
    outcome_count = db.query(Outcome).count()
    
    scholarship_count = db.query(ProgramEnrollment).filter(ProgramEnrollment.program_id == 1).count()
    plus_count = db.query(ProgramEnrollment).filter(ProgramEnrollment.program_id == 2).count()
    vocational_count = db.query(ProgramEnrollment).filter(ProgramEnrollment.program_id == 3).count()
    tech_count = db.query(ProgramEnrollment).filter(ProgramEnrollment.program_id == 4).count()

    sources_list = [
        {"name": "Beneficiaries", "type": "Database", "file": "beneficiaries.csv", "status": "Active", "records": beneficiary_count, "last_sync": "10 mins ago"},
        {"name": "Scholarship Program", "type": "Database", "file": "scholarship.csv", "status": "Active", "records": scholarship_count, "last_sync": "10 mins ago"},
        {"name": "Plus Program", "type": "Database", "file": "plus.csv", "status": "Active", "records": plus_count, "last_sync": "1 hour ago"},
        {"name": "Vocational Program", "type": "Database", "file": "vocational.csv", "status": "Active", "records": vocational_count, "last_sync": "45 mins ago"},
        {"name": "Tech Program", "type": "Database", "file": "tech.csv", "status": "Active", "records": tech_count, "last_sync": "2 mins ago"},
        {"name": "Attendance Tracking", "type": "Database", "file": "attendance.csv", "status": "Active", "records": attendance_count, "last_sync": "10 mins ago"},
        {"name": "Outcomes Database", "type": "Database", "file": "outcomes.csv", "status": "Active", "records": outcome_count, "last_sync": "10 mins ago"},
    ]

    return {
        "items": sources_list,
        "sources": sources_list,
        "total": len(sources_list),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/pipeline/status")
def pipeline_status():
    """ETL pipeline status information."""
    return {
        "pipeline": "insightflow-etl",
        "stages": [
            {"stage": "ingestion", "status": "ready"},
            {"stage": "validation", "status": "ready"},
            {"stage": "transformation", "status": "ready"},
            {"stage": "loading", "status": "ready"},
        ],
        "status": "healthy",
        "last_run_at": None,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


from fastapi import BackgroundTasks
from src.run_pipeline import step_generate, step_etl, step_load

@router.post("/pipeline/sync")
def trigger_sync(background_tasks: BackgroundTasks):
    """Trigger data generation, ETL and loading in the background."""
    def run_sync_task():
        try:
            step_generate()
            cleaned, unified, issues = step_etl()
            step_load(cleaned, unified, issues)
        except Exception as e:
            print("Sync failed:", str(e))
    background_tasks.add_task(run_sync_task)
    return {"status": "syncing", "message": "Pipeline sync started in background."}
