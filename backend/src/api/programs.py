from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..analytics import kpi_engine
from ..database import get_db
from ..models.models import Program

router = APIRouter(prefix="/api", tags=["programs"])


def _serialize_program(program: Program) -> dict:
    return {
        "id": program.id,
        "name": program.name,
        "description": program.description,
        "created_at": program.created_at.isoformat() if program.created_at else None,
    }


@router.get("/programs")
def list_programs(db: Session = Depends(get_db)):
    """Return all programs."""
    programs = db.query(Program).order_by(Program.name).all()
    return {"items": [_serialize_program(p) for p in programs], "total": len(programs)}


@router.get("/programs/performance")
def program_performance(
    period: int = Query(None, description="Reporting period ID"),
    db: Session = Depends(get_db),
):
    """Per-program performance metrics for the given period."""
    return kpi_engine.get_program_performance(db, period_id=period)
