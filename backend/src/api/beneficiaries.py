import math
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func, or_
from sqlalchemy.orm import Session

from ..analytics import kpi_engine
from ..database import get_db
from ..models.models import Beneficiary, Program, ProgramEnrollment

router = APIRouter(prefix="/api", tags=["beneficiaries"])


def _serialize_beneficiary(beneficiary: Beneficiary, enrollments: list) -> dict:
    return {
        "id": str(beneficiary.id),
        "beneficiary_id": beneficiary.beneficiary_id,
        "first_name": beneficiary.first_name,
        "last_name": beneficiary.last_name,
        "gender": beneficiary.gender,
        "age": beneficiary.age,
        "county": beneficiary.county,
        "sub_county": beneficiary.sub_county,
        "enrollments": [
            {
                "program_id": e.program_id,
                "program": e.program.name if e.program else None,
                "status": e.status,
                "enrollment_date": e.enrollment_date.isoformat() if e.enrollment_date else None,
                "participation_rate": e.participation_rate,
            }
            for e in enrollments
        ],
    }


@router.get("/beneficiaries")
def list_beneficiaries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page"),
    program: str = Query(None, description="Filter by program name"),
    county: str = Query(None, description="Filter by county"),
    status: str = Query(None, description="Filter by enrollment status"),
    search: str = Query(None, description="Search name, ID, email or phone"),
    db: Session = Depends(get_db),
):
    """Paginated beneficiary list with filters."""
    query = db.query(Beneficiary)
    joined_enrollment = False

    if program:
        query = (
            query.join(ProgramEnrollment, ProgramEnrollment.beneficiary_id == Beneficiary.id)
            .join(Program, ProgramEnrollment.program_id == Program.id)
            .filter(func.lower(Program.name) == program.strip().lower())
        )
        joined_enrollment = True
    if status:
        if not joined_enrollment:
            query = query.join(
                ProgramEnrollment, ProgramEnrollment.beneficiary_id == Beneficiary.id
            )
        query = query.filter(func.lower(func.coalesce(ProgramEnrollment.status, "")) == status.strip().lower())
    if county:
        query = query.filter(func.lower(Beneficiary.county) == county.strip().lower())
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Beneficiary.first_name.ilike(pattern),
                Beneficiary.last_name.ilike(pattern),
                Beneficiary.beneficiary_id.ilike(pattern),
                Beneficiary.email.ilike(pattern),
                Beneficiary.phone.ilike(pattern),
            )
        )

    total = int(query.with_entities(func.count(distinct(Beneficiary.id))).scalar() or 0)
    items = (
        query.order_by(Beneficiary.created_at.desc(), Beneficiary.beneficiary_id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    enrollment_map: dict = {}
    if items:
        rows = (
            db.query(ProgramEnrollment)
            .filter(ProgramEnrollment.beneficiary_id.in_([b.id for b in items]))
            .all()
        )
        for row in rows:
            enrollment_map.setdefault(row.beneficiary_id, []).append(row)

    return {
        "items": [
            _serialize_beneficiary(b, enrollment_map.get(b.id, [])) for b in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, math.ceil(total / page_size)),
    }


@router.get("/beneficiaries/analytics")
def beneficiary_analytics(
    program: str = Query(None, description="Filter by program name"),
    county: str = Query(None, description="Filter by county"),
    gender: str = Query(None, description="Filter by gender"),
    db: Session = Depends(get_db),
):
    """Demographic distributions computed from verified records."""
    return kpi_engine.get_beneficiary_analytics(db, program=program, county=county, gender=gender)
