from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..analytics import kpi_engine
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(
    period: int = Query(None, description="Reporting period ID"),
    db: Session = Depends(get_db),
):
    """Executive KPI summary computed from verified database records."""
    return kpi_engine.get_dashboard_summary(db, period_id=period)


@router.get("/trends")
def dashboard_trends(
    program: str = Query(None, description="Filter trends by program name"),
    db: Session = Depends(get_db),
):
    """Quarter-over-quarter trends for enrollments, completion and attendance."""
    return kpi_engine.get_trends(db, program=program)
