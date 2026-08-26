from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


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


BeneficiaryAnalytics.model_rebuild()
