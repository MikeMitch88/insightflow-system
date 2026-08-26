"""Cross-Pillar Data Collection API: M&E Metrics, Financial Items, Risks, Field Notes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.database import get_db
from src.models.models import (
    KPIMetric, FinancialLineItem, OperationalRisk, FieldNote, Project
)
from src.models.schemas import (
    KPIMetricCreate, KPIMetricOut,
    FinancialLineItemCreate, FinancialLineItemOut,
    OperationalRiskCreate, OperationalRiskOut,
    FieldNoteCreate, FieldNoteOut,
    ProjectCreate, ProjectOut,
)
from src.auth.rbac import get_current_user, require_tier, log_audit_event
from src.models.models import User

router = APIRouter(prefix="/api/cross-pillar", tags=["cross-pillar"])


# ============================================================
# PROJECTS
# ============================================================

@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
):
    q = db.query(Project)
    if status:
        q = q.filter(Project.status == status)
    return q.order_by(desc(Project.created_at)).all()


@router.post("/projects", response_model=ProjectOut)
def create_project(
    data: ProjectCreate,
    user: User = Depends(require_tier(1)),
    db: Session = Depends(get_db),
):
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    log_audit_event(db, user.id, "create_project", "project", project.id, data.model_dump())
    return project


# ============================================================
# M&E KPI METRICS (Targets vs Actuals)
# ============================================================

@router.get("/kpi-metrics", response_model=list[KPIMetricOut])
def list_kpi_metrics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    project_id: Optional[int] = Query(None),
    reporting_period_id: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    verified: Optional[bool] = Query(None),
):
    q = db.query(KPIMetric)
    if project_id:
        q = q.filter(KPIMetric.project_id == project_id)
    if reporting_period_id:
        q = q.filter(KPIMetric.reporting_period_id == reporting_period_id)
    if department_id:
        q = q.filter(KPIMetric.department_id == department_id)
    if verified is not None:
        q = q.filter(KPIMetric.verified == verified)
    return q.order_by(desc(KPIMetric.created_at)).all()


@router.post("/kpi-metrics", response_model=KPIMetricOut)
def create_kpi_metric(
    data: KPIMetricCreate,
    user: User = Depends(require_tier(1)),
    db: Session = Depends(get_db),
):
    metric = KPIMetric(**data.model_dump(), submitted_by=user.id)
    if metric.target_value > 0:
        metric.attainment_pct = round((metric.actual_value / metric.target_value) * 100, 1)
    db.add(metric)
    db.commit()
    db.refresh(metric)
    log_audit_event(db, user.id, "create_kpi_metric", "kpi_metric", metric.id, data.model_dump())
    return metric


@router.post("/kpi-metrics/{metric_id}/verify")
def verify_kpi_metric(
    metric_id: int,
    user: User = Depends(require_tier(2)),
    db: Session = Depends(get_db),
):
    metric = db.query(KPIMetric).filter(KPIMetric.id == metric_id).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    metric.verified = True
    metric.verified_by = user.id
    db.commit()
    log_audit_event(db, user.id, "verify_kpi_metric", "kpi_metric", metric_id)
    return {"status": "verified", "id": metric_id}


# ============================================================
# FINANCIAL LINE ITEMS (Budget vs Spend)
# ============================================================

@router.get("/financial-items", response_model=list[FinancialLineItemOut])
def list_financial_items(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    project_id: Optional[int] = Query(None),
    reporting_period_id: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    verified: Optional[bool] = Query(None),
):
    q = db.query(FinancialLineItem)
    if project_id:
        q = q.filter(FinancialLineItem.project_id == project_id)
    if reporting_period_id:
        q = q.filter(FinancialLineItem.reporting_period_id == reporting_period_id)
    if department_id:
        q = q.filter(FinancialLineItem.department_id == department_id)
    if verified is not None:
        q = q.filter(FinancialLineItem.verified == verified)
    return q.order_by(desc(FinancialLineItem.created_at)).all()


@router.post("/financial-items", response_model=FinancialLineItemOut)
def create_financial_item(
    data: FinancialLineItemCreate,
    user: User = Depends(require_tier(1)),
    db: Session = Depends(get_db),
):
    item = FinancialLineItem(**data.model_dump(), submitted_by=user.id)
    if item.budget_amount > 0:
        item.burn_rate = round((item.actual_spend / item.budget_amount) * 100, 1)
        item.variance = round(item.budget_amount - item.actual_spend, 2)
    db.add(item)
    db.commit()
    db.refresh(item)
    log_audit_event(db, user.id, "create_financial_item", "financial_line_item", item.id, data.model_dump())
    return item


@router.post("/financial-items/{item_id}/verify")
def verify_financial_item(
    item_id: int,
    user: User = Depends(require_tier(2)),
    db: Session = Depends(get_db),
):
    item = db.query(FinancialLineItem).filter(FinancialLineItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Financial item not found")
    item.verified = True
    item.verified_by = user.id
    db.commit()
    log_audit_event(db, user.id, "verify_financial_item", "financial_line_item", item_id)
    return {"status": "verified", "id": item_id}


# ============================================================
# OPERATIONAL RISKS & MITIGATION
# ============================================================

@router.get("/risks", response_model=list[OperationalRiskOut])
def list_risks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    project_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    q = db.query(OperationalRisk)
    if project_id:
        q = q.filter(OperationalRisk.project_id == project_id)
    if severity:
        q = q.filter(OperationalRisk.severity == severity)
    if status:
        q = q.filter(OperationalRisk.status == status)
    return q.order_by(desc(OperationalRisk.created_at)).all()


@router.post("/risks", response_model=OperationalRiskOut)
def create_risk(
    data: OperationalRiskCreate,
    user: User = Depends(require_tier(1)),
    db: Session = Depends(get_db),
):
    risk = OperationalRisk(**data.model_dump(), submitted_by=user.id)
    db.add(risk)
    db.commit()
    db.refresh(risk)
    log_audit_event(db, user.id, "create_risk", "operational_risk", risk.id, data.model_dump())
    return risk


# ============================================================
# FIELD NOTES & QUALITATIVE DATA
# ============================================================

@router.get("/field-notes", response_model=list[FieldNoteOut])
def list_field_notes(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    project_id: Optional[int] = Query(None),
    note_type: Optional[str] = Query(None),
    vectorized: Optional[bool] = Query(None),
):
    q = db.query(FieldNote)
    if project_id:
        q = q.filter(FieldNote.project_id == project_id)
    if note_type:
        q = q.filter(FieldNote.note_type == note_type)
    if vectorized is not None:
        q = q.filter(FieldNote.vectorized == vectorized)
    return q.order_by(desc(FieldNote.created_at)).all()


@router.post("/field-notes", response_model=FieldNoteOut)
def create_field_note(
    data: FieldNoteCreate,
    user: User = Depends(require_tier(1)),
    db: Session = Depends(get_db),
):
    note = FieldNote(**data.model_dump(), submitted_by=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    log_audit_event(db, user.id, "create_field_note", "field_note", note.id, {"title": data.title})
    return note
