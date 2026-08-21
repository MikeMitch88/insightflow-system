from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..analytics import kpi_engine
from ..database import get_db

router = APIRouter(prefix="/api", tags=["outcomes"])


@router.get("/outcomes")
def outcomes_summary(
    period: int = Query(None, description="Reporting period ID"),
    db: Session = Depends(get_db),
):
    """Outcomes and impact summary for the given period."""
    return kpi_engine.get_outcomes_summary(db, period_id=period)
