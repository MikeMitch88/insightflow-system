from datetime import datetime, date
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ============================================================
# RBAC & AUTH SCHEMAS
# ============================================================

class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class RoleOut(BaseModel):
    id: int
    name: str
    tier: int
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class PermissionOut(BaseModel):
    id: int
    resource: str
    action: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: Optional[RoleOut] = None
    department: Optional[DepartmentOut] = None
    status: str

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=6)
    role_id: int
    department_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


# ============================================================
# EXISTING SCHEMAS
# ============================================================

class DashboardSummary(BaseModel):
    total_beneficiaries: int
    active_beneficiaries: int
    completion_rate: float
    program_count: int
    counties_reached: int
    data_quality_score: float
    attendance_rate: float
    dropout_rate: float
    outcome_rate: float


class ProgramPerformance(BaseModel):
    program_name: str
    total_enrolled: int
    active: int
    completed: int
    dropped_out: int
    completion_rate: float
    avg_attendance_rate: Optional[float] = None
    avg_participation_rate: Optional[float] = None


class BeneficiaryAnalytics(BaseModel):
    age_distribution: Dict[str, int]
    gender_distribution: Dict[str, int]
    county_distribution: Dict[str, int]
    program_distribution: Dict[str, int]
    enrollment_trends: List["TrendPoint"]


class OutcomesSummary(BaseModel):
    total_outcomes: int
    employment_rate: float
    completion_rate: float
    by_program: Dict[str, Dict[str, Any]]
    by_county: Dict[str, Dict[str, Any]]


class DataQualityIssueOut(BaseModel):
    id: int
    source_file: Optional[str] = None
    record_id: Optional[str] = None
    field_name: Optional[str] = None
    issue_type: Optional[str] = None
    original_value: Optional[str] = None
    corrected_value: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    detected_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class DataQualitySummary(BaseModel):
    score: float
    total_issues: int
    missing_values: int
    duplicates: int
    invalid_values: int
    unresolved: int
    issues: List[DataQualityIssueOut]


class ReportCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    report_type: str
    reporting_period: Optional[str] = None
    reporting_period_id: Optional[int] = None
    sections: List[str] = []
    use_ai_insights: bool = True


class ReportPreviewRequest(BaseModel):
    reporting_period: str = "August 2026"
    reporting_period_id: Optional[int] = None
    report_type: str = "Monthly Donor Report"
    sections: List[str] = []
    use_ai_insights: bool = True


class ReportValidateRequest(BaseModel):
    reporting_period: str = "August 2026"
    reporting_period_id: Optional[int] = None
    report_type: str = "Monthly Donor Report"
    sections: List[str] = []


class ReportGenerateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    report_type: str = "Monthly Donor Report"
    reporting_period: str = "August 2026"
    reporting_period_id: Optional[int] = None
    sections: List[str] = []
    use_ai_insights: bool = True
    confirmed_reviewed: bool = True
    confirmed_kpis: bool = True
    confirmed_warnings: bool = True
    confirmed_ready: bool = True


class ReportApproveRequest(BaseModel):
    comment: Optional[str] = "Verified and authorized for official reporting."


class ReportRejectRequest(BaseModel):
    reason: str = Field(min_length=3, description="Mandatory rejection reason")
    feedback: Optional[str] = None


class ReportReviseRequest(BaseModel):
    notes: Optional[str] = None


class NotificationResponse(BaseModel):
    id: int
    recipient_role: str
    recipient_user_id: Optional[int] = None
    type: str
    title: str
    message: str
    report_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1)
    context_page: Optional[str] = None


class AIChatResponse(BaseModel):
    answer: str
    relevant_kpis: List[str]
    supporting_data: Dict[str, Any]
    recommendation: Optional[str] = None


class AIInsight(BaseModel):
    title: str
    severity: str
    evidence: str
    explanation: str
    recommended_action: str
    category: Optional[str] = None


class TrendPoint(BaseModel):
    period: str
    value: float


class PaginationResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================
# CROSS-PILLAR DATA COLLECTION SCHEMAS
# ============================================================

class KPIMetricCreate(BaseModel):
    project_id: int
    reporting_period_id: Optional[int] = None
    department_id: Optional[int] = None
    kpi_name: str = Field(min_length=1, max_length=255)
    kpi_category: Optional[str] = None
    target_value: float = 0
    actual_value: float = 0
    unit: Optional[str] = None
    notes: Optional[str] = None


class KPIMetricOut(BaseModel):
    id: int
    project_id: int
    kpi_name: str
    kpi_category: Optional[str] = None
    target_value: float
    actual_value: float
    unit: Optional[str] = None
    attainment_pct: Optional[float] = None
    notes: Optional[str] = None
    verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FinancialLineItemCreate(BaseModel):
    project_id: int
    reporting_period_id: Optional[int] = None
    department_id: Optional[int] = None
    line_item: str = Field(min_length=1, max_length=255)
    category: Optional[str] = None
    budget_amount: float = 0
    actual_spend: float = 0
    currency: str = "USD"
    notes: Optional[str] = None


class FinancialLineItemOut(BaseModel):
    id: int
    project_id: int
    line_item: str
    category: Optional[str] = None
    budget_amount: float
    actual_spend: float
    burn_rate: Optional[float] = None
    variance: Optional[float] = None
    currency: str
    notes: Optional[str] = None
    verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OperationalRiskCreate(BaseModel):
    project_id: int
    reporting_period_id: Optional[int] = None
    department_id: Optional[int] = None
    risk_title: str = Field(min_length=1, max_length=255)
    risk_category: Optional[str] = None
    severity: str = "medium"
    likelihood: Optional[str] = None
    impact: Optional[str] = None
    mitigation_strategy: Optional[str] = None


class OperationalRiskOut(BaseModel):
    id: int
    project_id: int
    risk_title: str
    risk_category: Optional[str] = None
    severity: str
    likelihood: Optional[str] = None
    impact: Optional[str] = None
    mitigation_strategy: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FieldNoteCreate(BaseModel):
    project_id: int
    reporting_period_id: Optional[int] = None
    department_id: Optional[int] = None
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    note_type: Optional[str] = None
    beneficiary_quote: Optional[str] = None
    location: Optional[str] = None
    date_observed: Optional[date] = None
    tags: Optional[dict] = None


class FieldNoteOut(BaseModel):
    id: int
    project_id: int
    title: str
    content: str
    note_type: Optional[str] = None
    beneficiary_quote: Optional[str] = None
    location: Optional[str] = None
    date_observed: Optional[date] = None
    tags: Optional[dict] = None
    vectorized: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# WORKFLOW & REPORT SCHEMAS
# ============================================================

class DonorReportCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    reporting_period_id: Optional[int] = None
    donor_name: Optional[str] = None
    sections_json: Optional[dict] = None


class DonorReportOut(BaseModel):
    id: int
    title: str
    donor_name: Optional[str] = None
    workflow_status: str
    current_tier: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApprovalAction(BaseModel):
    action: str = Field(pattern="^(save_draft|submit_for_review|approve|reject|request_changes|assemble_report|edit_content|submit_for_final_approval)$")
    comments: Optional[str] = None
    changes_json: Optional[dict] = None


class AuditLogOut(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    changes_json: Optional[dict] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    program_id: Optional[int] = None
    department_id: Optional[int] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    program_id: Optional[int] = None
    department_id: Optional[int] = None
    description: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Rebuild forward references
BeneficiaryAnalytics.model_rebuild()
