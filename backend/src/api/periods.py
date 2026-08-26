from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import ReportingPeriod

router = APIRouter(prefix="/api", tags=["periods"])


def _serialize_period(period: ReportingPeriod) -> dict:
    month_map = {1: "February", 2: "May", 3: "August", 4: "November"}
    month_name = month_map.get(period.quarter, "Quarter")
    display_name = f"{month_name} {period.year} ({period.name})"
    return {
        "id": period.id,
        "name": period.name,
        "display_name": display_name,
        "month_name": f"{month_name} {period.year}",
        "year": period.year,
        "quarter": period.quarter,
        "start_date": period.start_date.isoformat() if period.start_date else None,
        "end_date": period.end_date.isoformat() if period.end_date else None,
        "is_current": period.is_current,
    }


@router.get("/periods")
def list_periods(db: Session = Depends(get_db)):
    """Return all reporting periods ordered by year and quarter."""
    periods = (
        db.query(ReportingPeriod)
        .order_by(ReportingPeriod.year, ReportingPeriod.quarter)
        .all()
    )
    return {"items": [_serialize_period(p) for p in periods], "total": len(periods)}


@router.get("/periods/current")
def current_period(db: Session = Depends(get_db)):
    """Return the current reporting period (falls back to the latest)."""
    period = (
        db.query(ReportingPeriod)
        .filter(ReportingPeriod.is_current.is_(True))
        .first()
    )
    if period is None:
        period = (
            db.query(ReportingPeriod)
            .order_by(ReportingPeriod.year.desc(), ReportingPeriod.quarter.desc())
            .first()
        )
    if period is None:
        raise HTTPException(status_code=404, detail="No reporting periods found")
    return _serialize_period(period)
