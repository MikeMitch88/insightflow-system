from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..analytics import kpi_engine
from ..database import get_db

router = APIRouter(prefix="/api", tags=["data-quality"])

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
def data_sources():
    """Static list of pipeline data sources with load status."""
    return {
        "items": DATA_SOURCES,
        "total": len(DATA_SOURCES),
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
