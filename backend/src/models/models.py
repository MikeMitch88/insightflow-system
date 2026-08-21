import uuid
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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


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


class Beneficiary(Base):
    __tablename__ = "beneficiaries"
    __table_args__ = (
        Index("ix_beneficiaries_county_gender", "county", "gender"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
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


class ProgramEnrollment(Base):
    __tablename__ = "program_enrollments"
    __table_args__ = (
        Index("ix_enrollments_beneficiary_program", "beneficiary_id", "program_id"),
        Index("ix_enrollments_period_status", "reporting_period_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    beneficiary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("beneficiaries.id", ondelete="CASCADE"),
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
    beneficiary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("beneficiaries.id", ondelete="CASCADE"),
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
    beneficiary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("beneficiaries.id", ondelete="CASCADE"),
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

    reporting_period: Mapped["ReportingPeriod"] = relationship(back_populates="reports")
    runs: Mapped[list["ReportRun"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )


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
