from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


# ============================================================
# RBAC & AUTH MODELS
# ============================================================

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    users: Mapped[list["User"]] = relationship(back_populates="department")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    tier: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    permissions: Mapped[list["RolePermission"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    users: Mapped[list["User"]] = relationship(back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("resource", "action", name="uq_permission_resource_action"),
    )

    roles: Mapped[list["RolePermission"]] = relationship(back_populates="permission")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    role: Mapped["Role"] = relationship(back_populates="permissions")
    permission: Mapped["Permission"] = relationship(back_populates="roles")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, index=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    role: Mapped["Role"] = relationship(back_populates="users")
    department: Mapped[Optional["Department"]] = relationship(back_populates="users")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


# ============================================================
# EXISTING MODELS (kept for backward compatibility)
# ============================================================

class ReportingPeriod(Base):
    __tablename__ = "reporting_periods"
    __table_args__ = (
        UniqueConstraint("year", "quarter", name="uq_reporting_periods_year_quarter"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    enrollments: Mapped[list["ProgramEnrollment"]] = relationship(back_populates="reporting_period")
    attendance_records: Mapped[list["Attendance"]] = relationship(back_populates="reporting_period")
    outcomes: Mapped[list["Outcome"]] = relationship(back_populates="reporting_period")
    reports: Mapped[list["Report"]] = relationship(back_populates="reporting_period")
    project_cycles: Mapped[list["ProjectCycle"]] = relationship(back_populates="reporting_period")


class Beneficiary(Base):
    __tablename__ = "beneficiaries"
    __table_args__ = (
        Index("ix_beneficiaries_county_gender", "county", "gender"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    county: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    sub_county: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    enrollments: Mapped[list["ProgramEnrollment"]] = relationship(back_populates="beneficiary")
    attendance_records: Mapped[list["Attendance"]] = relationship(back_populates="beneficiary")
    outcomes: Mapped[list["Outcome"]] = relationship(back_populates="beneficiary")


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    enrollments: Mapped[list["ProgramEnrollment"]] = relationship(back_populates="program")
    attendance_records: Mapped[list["Attendance"]] = relationship(back_populates="program")
    outcomes: Mapped[list["Outcome"]] = relationship(back_populates="program")
    projects: Mapped[list["Project"]] = relationship(back_populates="program")


class ProgramEnrollment(Base):
    __tablename__ = "program_enrollments"
    __table_args__ = (
        Index("ix_enrollments_beneficiary_program", "beneficiary_id", "program_id"),
        Index("ix_enrollments_period_status", "reporting_period_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("beneficiaries.beneficiary_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id"), nullable=False, index=True
    )
    enrollment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
    reporting_period_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("reporting_periods.id"), nullable=True, index=True
    )
    education_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    academic_year: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    institution: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    activity: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    sessions_attended: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sessions_expected: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    participation_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    course: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    training_center: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    training_provider: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    certification_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    employment_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    skills_acquired: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    beneficiary: Mapped["Beneficiary"] = relationship(back_populates="enrollments")
    program: Mapped["Program"] = relationship(back_populates="enrollments")
    reporting_period: Mapped["ReportingPeriod"] = relationship(back_populates="enrollments")


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        Index("ix_attendance_beneficiary_period", "beneficiary_id", "reporting_period_id"),
        Index("ix_attendance_program_period", "program_id", "reporting_period_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    beneficiary_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("beneficiaries.beneficiary_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), nullable=False, index=True)
    reporting_period_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("reporting_periods.id"), nullable=True, index=True
    )
    sessions_expected: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sessions_attended: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    attendance_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    beneficiary: Mapped["Beneficiary"] = relationship(back_populates="attendance_records")
    program: Mapped["Program"] = relationship(back_populates="attendance_records")
    reporting_period: Mapped["ReportingPeriod"] = relationship(back_populates="attendance_records")


class Outcome(Base):
    __tablename__ = "outcomes"
    __table_args__ = (
        Index("ix_outcomes_beneficiary_period", "beneficiary_id", "reporting_period_id"),
        Index("ix_outcomes_program_type", "program_id", "outcome_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    beneficiary_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("beneficiaries.beneficiary_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), nullable=False, index=True)
    reporting_period_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("reporting_periods.id"), nullable=True, index=True
    )
    outcome_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    outcome_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    employment_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    completion_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    beneficiary: Mapped["Beneficiary"] = relationship(back_populates="outcomes")
    program: Mapped["Program"] = relationship(back_populates="outcomes")
    reporting_period: Mapped["ReportingPeriod"] = relationship(back_populates="outcomes")


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"
    __table_args__ = (
        Index("ix_dqi_type_status", "issue_type", "status"),
        Index("ix_dqi_severity_status", "severity", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_file: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    record_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    field_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    issue_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    original_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrected_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        Index("ix_reports_type_status", "report_type", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    reporting_period_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("reporting_periods.id"), nullable=True, index=True
    )
    config_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    reporting_period_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=1)
    parent_report_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("reports.id"), nullable=True, index=True
    )
    generated_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_to: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejected_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    validation_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default="PASS")
    validation_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    report_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    kpi_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    reporting_period: Mapped["ReportingPeriod"] = relationship(back_populates="reports")
    runs: Mapped[list["ReportRun"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )
    donor_reports: Mapped[list["DonorReport"]] = relationship(back_populates="base_report")


class ReportRun(Base):
    __tablename__ = "report_runs"
    __table_args__ = (
        Index("ix_report_runs_report_started", "report_id", "started_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(
        ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running", index=True)
    records_processed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    report: Mapped["Report"] = relationship(back_populates="runs")


# ============================================================
# CROSS-PILLAR DATA COLLECTION MODELS
# ============================================================

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    program_id: Mapped[Optional[int]] = mapped_column(ForeignKey("programs.id"), nullable=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    program: Mapped[Optional["Program"]] = relationship(back_populates="projects")
    cycles: Mapped[list["ProjectCycle"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    kpi_metrics: Mapped[list["KPIMetric"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    financial_items: Mapped[list["FinancialLineItem"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    risks: Mapped[list["OperationalRisk"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    field_notes: Mapped[list["FieldNote"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectCycle(Base):
    __tablename__ = "project_cycles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_period_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reporting_periods.id"), nullable=True)
    cycle_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="cycles")
    reporting_period: Mapped[Optional["ReportingPeriod"]] = relationship(back_populates="project_cycles")


# ============================================================
# M&E METRICS (Targets vs Actuals)
# ============================================================

class KPIMetric(Base):
    __tablename__ = "kpi_metrics"
    __table_args__ = (
        Index("ix_kpi_project_period", "project_id", "reporting_period_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_period_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reporting_periods.id"), nullable=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    kpi_name: Mapped[str] = mapped_column(String(255), nullable=False)
    kpi_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_value: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    actual_value: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    attainment_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    verified_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="kpi_metrics")


# ============================================================
# FINANCIAL LINE ITEMS (Budget vs Spend)
# ============================================================

class FinancialLineItem(Base):
    __tablename__ = "financial_line_items"
    __table_args__ = (
        Index("ix_financial_project_period", "project_id", "reporting_period_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_period_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reporting_periods.id"), nullable=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    line_item: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    budget_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    actual_spend: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    burn_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    variance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    verified_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="financial_items")


# ============================================================
# OPERATIONAL RISKS & MITIGATION
# ============================================================

class OperationalRisk(Base):
    __tablename__ = "operational_risks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_period_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reporting_periods.id"), nullable=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    risk_title: Mapped[str] = mapped_column(String(255), nullable=False)
    risk_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="medium", index=True)
    likelihood: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    impact: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    mitigation_strategy: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="risks")


# ============================================================
# FIELD NOTES & QUALITATIVE DATA
# ============================================================

class FieldNote(Base):
    __tablename__ = "field_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_period_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reporting_periods.id"), nullable=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    beneficiary_quote: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_observed: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    submitted_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    vectorized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="field_notes")


# ============================================================
# WORKFLOW & APPROVAL MODELS
# ============================================================

class DonorReport(Base):
    __tablename__ = "donor_reports"
    __table_args__ = (
        Index("ix_donor_reports_status", "workflow_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    reporting_period_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reporting_periods.id"), nullable=True)
    base_report_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reports.id"), nullable=True)
    donor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    workflow_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="drafting", index=True
    )
    current_tier: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    sections_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ai_generated_content: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    final_pdf_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    base_report: Mapped[Optional["Report"]] = relationship(back_populates="donor_reports")
    approvals: Mapped[list["ApprovalRecord"]] = relationship(
        back_populates="donor_report", cascade="all, delete-orphan"
    )
    shares: Mapped[list["ReportShare"]] = relationship(
        back_populates="donor_report", cascade="all, delete-orphan"
    )


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    donor_report_id: Mapped[int] = mapped_column(
        ForeignKey("donor_reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tier: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changes_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    actioned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    donor_report: Mapped["DonorReport"] = relationship(back_populates="approvals")


class ReportShare(Base):
    __tablename__ = "report_shares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    donor_report_id: Mapped[int] = mapped_column(
        ForeignKey("donor_reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    shared_with_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    permission_level: Mapped[str] = mapped_column(String(20), nullable=False, default="read")
    shared_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    donor_report: Mapped["DonorReport"] = relationship(back_populates="shares")


# ============================================================
# AUDIT TRAIL (Immutable)
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_user_timestamp", "user_id", "timestamp"),
        Index("ix_audit_action_entity", "action", "entity_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    changes_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    user: Mapped["User"] = relationship(back_populates="audit_logs")

    report_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    report_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


# ============================================================
# COLLABORATIVE EDITING (Edit Locks)
# ============================================================

class EditLock(Base):
    __tablename__ = "edit_locks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    donor_report_id: Mapped[int] = mapped_column(
        ForeignKey("donor_reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_id: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    locked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    donor_report: Mapped["DonorReport"] = relationship()


class EditHistory(Base):
    __tablename__ = "edit_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    donor_report_id: Mapped[int] = mapped_column(
        ForeignKey("donor_reports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_id: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    edited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
