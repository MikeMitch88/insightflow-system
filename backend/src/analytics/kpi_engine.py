from sqlalchemy import case, distinct, func, or_
from sqlalchemy.orm import Session

from ..models.models import (
    Attendance,
    Beneficiary,
    DataQualityIssue,
    Outcome,
    Program,
    ProgramEnrollment,
    Report,
    ReportingPeriod,
)

ACTIVE_STATUS = "active"
COMPLETED_STATUS = "completed"
DROPPED_OUT_STATUS = "dropped_out"
EMPLOYED_STATUS = "employed"

GENERATING_STATUSES = ("generating", "running", "pending")

POSITIVE_OUTCOME_TYPES = (
    "employment",
    "certification",
    "completion",
    "graduation",
    "job_placement",
    "internship",
)

AGE_GROUPS = ["16-20", "21-25", "26-30", "31-35", "35+"]


def _percentage(numerator, denominator) -> float:
    if numerator is None or denominator is None:
        return 0.0
    try:
        return round((float(numerator) / float(denominator)) * 100.0, 1)
    except ZeroDivisionError:
        return 0.0


def _to_float(value) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _count_rows(db: Session, model) -> int:
    return _to_int(db.query(func.count(model.id)).scalar())


def _lower_status_match(column, status: str):
    return func.lower(func.coalesce(column, "")) == status.lower()


def _positive_outcome_condition():
    return or_(
        func.lower(func.coalesce(Outcome.outcome_type, "")).in_(
            [t.lower() for t in POSITIVE_OUTCOME_TYPES]
        ),
        func.lower(func.coalesce(Outcome.employment_status, "")) == EMPLOYED_STATUS,
        func.lower(func.coalesce(Outcome.completion_status, "")) == COMPLETED_STATUS,
    )


def get_dashboard_summary(db: Session, period_id: int = None) -> dict:
    """
    Compute executive dashboard summary from database.

    Returns dict with:
    - total_beneficiaries: count of distinct beneficiaries with enrollments
    - active_beneficiaries: count of distinct with status='active'
    - completion_rate: completed / total * 100 (rounded to 1 decimal)
    - program_count: count of distinct programs with enrollments
    - counties_reached: count of distinct counties
    - data_quality_score: 100 - (detected issues / total records * 100), clamped 0-100
    - attendance_rate: avg attendance_rate from attendance table (rounded to 1 decimal)
    - dropout_rate: dropped_out / total * 100 (rounded to 1 decimal)
    - outcome_rate: positive outcomes / total * 100 (rounded to 1 decimal)
    """
    enrollment_query = db.query(
        func.count(distinct(ProgramEnrollment.beneficiary_id)).label("total_beneficiaries"),
        func.count(
            distinct(
                case(
                    (
                        _lower_status_match(ProgramEnrollment.status, ACTIVE_STATUS),
                        ProgramEnrollment.beneficiary_id,
                    )
                )
            )
        ).label("active_beneficiaries"),
        func.count(ProgramEnrollment.id).label("total_enrollments"),
        func.count(
            case((_lower_status_match(ProgramEnrollment.status, COMPLETED_STATUS), 1))
        ).label("completed_enrollments"),
        func.count(
            case((_lower_status_match(ProgramEnrollment.status, DROPPED_OUT_STATUS), 1))
        ).label("dropped_enrollments"),
        func.count(distinct(ProgramEnrollment.program_id)).label("program_count"),
    )
    if period_id is not None:
        enrollment_query = enrollment_query.filter(
            ProgramEnrollment.reporting_period_id == period_id
        )
    enrollment_stats = enrollment_query.one()

    counties_query = (
        db.query(func.count(distinct(Beneficiary.county)))
        .join(ProgramEnrollment, ProgramEnrollment.beneficiary_id == Beneficiary.beneficiary_id)
        .filter(Beneficiary.county.isnot(None))
    )
    if period_id is not None:
        counties_query = counties_query.filter(
            ProgramEnrollment.reporting_period_id == period_id
        )
    counties_reached = _to_int(counties_query.scalar())

    attendance_query = db.query(func.avg(Attendance.attendance_rate))
    if period_id is not None:
        attendance_query = attendance_query.filter(
            Attendance.reporting_period_id == period_id
        )
    attendance_rate = round(_to_float(attendance_query.scalar()), 1)

    outcome_query = db.query(
        func.count(Outcome.id).label("total_outcomes"),
        func.count(case((_positive_outcome_condition(), 1))).label("positive_outcomes"),
    )
    if period_id is not None:
        outcome_query = outcome_query.filter(Outcome.reporting_period_id == period_id)
    outcome_stats = outcome_query.one()

    total_records = (
        _count_rows(db, Beneficiary)
        + _count_rows(db, ProgramEnrollment)
        + _count_rows(db, Attendance)
        + _count_rows(db, Outcome)
    )
    total_issues = _count_rows(db, DataQualityIssue)
    data_quality_score = round(
        _clamp(100.0 - (total_issues / max(total_records, 1)) * 100.0), 1
    )

    total_enrollments = _to_int(enrollment_stats.total_enrollments)
    completed_enrollments = _to_int(enrollment_stats.completed_enrollments)
    dropped_enrollments = _to_int(enrollment_stats.dropped_enrollments)
    total_outcomes = _to_int(outcome_stats.total_outcomes)
    positive_outcomes = _to_int(outcome_stats.positive_outcomes)

    return {
        "total_beneficiaries": _to_int(enrollment_stats.total_beneficiaries),
        "active_beneficiaries": _to_int(enrollment_stats.active_beneficiaries),
        "completion_rate": _percentage(completed_enrollments, total_enrollments),
        "program_count": _to_int(enrollment_stats.program_count),
        "counties_reached": counties_reached,
        "data_quality_score": data_quality_score,
        "attendance_rate": attendance_rate,
        "dropout_rate": _percentage(dropped_enrollments, total_enrollments),
        "outcome_rate": _percentage(positive_outcomes, total_outcomes),
    }


def get_program_performance(db: Session, period_id: int = None) -> list[dict]:
    """
    Per-program performance metrics.
    Returns list of dicts, each with:
    - program_name, total_enrolled, active, completed, dropped_out
    - completion_rate, avg_attendance_rate, avg_participation_rate
    """
    enrollment_query = (
        db.query(
            Program.name.label("program_name"),
            func.count(ProgramEnrollment.id).label("total_enrolled"),
            func.count(
                case((_lower_status_match(ProgramEnrollment.status, ACTIVE_STATUS), 1))
            ).label("active"),
            func.count(
                case((_lower_status_match(ProgramEnrollment.status, COMPLETED_STATUS), 1))
            ).label("completed"),
            func.count(
                case((_lower_status_match(ProgramEnrollment.status, DROPPED_OUT_STATUS), 1))
            ).label("dropped_out"),
            func.avg(ProgramEnrollment.participation_rate).label("avg_participation_rate"),
        )
        .join(ProgramEnrollment, ProgramEnrollment.program_id == Program.id)
        .group_by(Program.id, Program.name)
        .order_by(Program.name)
    )
    if period_id is not None:
        enrollment_query = enrollment_query.filter(
            ProgramEnrollment.reporting_period_id == period_id
        )
    rows = enrollment_query.all()

    attendance_query = (
        db.query(
            Program.name.label("program_name"),
            func.avg(Attendance.attendance_rate).label("avg_attendance_rate"),
        )
        .join(Attendance, Attendance.program_id == Program.id)
        .group_by(Program.id, Program.name)
    )
    if period_id is not None:
        attendance_query = attendance_query.filter(
            Attendance.reporting_period_id == period_id
        )
    attendance_map = {
        row.program_name: _to_float(row.avg_attendance_rate)
        for row in attendance_query.all()
    }

    results = []
    for row in rows:
        total_enrolled = _to_int(row.total_enrolled)
        completed = _to_int(row.completed)
        results.append(
            {
                "program_name": row.program_name,
                "total_enrolled": total_enrolled,
                "active": _to_int(row.active),
                "completed": completed,
                "dropped_out": _to_int(row.dropped_out),
                "completion_rate": _percentage(completed, total_enrolled),
                "avg_attendance_rate": round(
                    attendance_map.get(row.program_name, 0.0), 1
                ),
                "avg_participation_rate": round(
                    _to_float(row.avg_participation_rate), 1
                ),
            }
        )
    return results


def get_trends(db: Session, program: str = None) -> list[dict]:
    """
    Quarter-over-quarter trends.
    Returns list of dicts with:
    - period (e.g. "Q1 2025"), beneficiary_count, completion_rate, attendance_rate, enrollment_count
    Ordered by year then quarter.
    """
    enrollment_query = (
        db.query(
            ReportingPeriod.year.label("year"),
            ReportingPeriod.quarter.label("quarter"),
            func.count(ProgramEnrollment.id).label("enrollment_count"),
            func.count(distinct(ProgramEnrollment.beneficiary_id)).label(
                "beneficiary_count"
            ),
            func.count(
                case((_lower_status_match(ProgramEnrollment.status, COMPLETED_STATUS), 1))
            ).label("completed_count"),
        )
        .join(ReportingPeriod, ProgramEnrollment.reporting_period_id == ReportingPeriod.id)
        .group_by(ReportingPeriod.year, ReportingPeriod.quarter)
    )
    if program:
        enrollment_query = (
            enrollment_query.join(Program, ProgramEnrollment.program_id == Program.id)
            .filter(func.lower(Program.name) == program.strip().lower())
        )

    attendance_query = (
        db.query(
            ReportingPeriod.year.label("year"),
            ReportingPeriod.quarter.label("quarter"),
            func.avg(Attendance.attendance_rate).label("attendance_rate"),
        )
        .join(ReportingPeriod, Attendance.reporting_period_id == ReportingPeriod.id)
        .group_by(ReportingPeriod.year, ReportingPeriod.quarter)
    )
    if program:
        attendance_query = (
            attendance_query.join(Program, Attendance.program_id == Program.id)
            .filter(func.lower(Program.name) == program.strip().lower())
        )
    attendance_map = {
        (row.year, row.quarter): _to_float(row.attendance_rate)
        for row in attendance_query.all()
    }

    ordered_rows = sorted(
        enrollment_query.all(),
        key=lambda r: (_to_int(r.year), _to_int(r.quarter)),
    )

    trends = []
    for row in ordered_rows:
        enrollment_count = _to_int(row.enrollment_count)
        completed_count = _to_int(row.completed_count)
        trends.append(
            {
                "period": f"Q{row.quarter} {row.year}",
                "beneficiary_count": _to_int(row.beneficiary_count),
                "completion_rate": _percentage(completed_count, enrollment_count),
                "attendance_rate": round(
                    attendance_map.get((row.year, row.quarter), 0.0), 1
                ),
                "enrollment_count": enrollment_count,
            }
        )
    return trends


def _beneficiary_query(
    db: Session, program: str = None, county: str = None, gender: str = None
):
    query = db.query(Beneficiary)
    if county:
        query = query.filter(func.lower(Beneficiary.county) == county.strip().lower())
    if gender:
        query = query.filter(func.lower(Beneficiary.gender) == gender.strip().lower())
    if program:
        query = (
            query.join(ProgramEnrollment, ProgramEnrollment.beneficiary_id == Beneficiary.beneficiary_id)
            .join(Program, ProgramEnrollment.program_id == Program.id)
            .filter(func.lower(Program.name) == program.strip().lower())
        )
    return query


def _build_distribution(rows: list, key_name: str) -> list[dict]:
    entries = [
        {key_name: key, "count": _to_int(count)}
        for key, count in rows
        if key is not None
    ]
    total = sum(entry["count"] for entry in entries)
    for entry in entries:
        entry["percentage"] = _percentage(entry["count"], total)
    return entries


def get_beneficiary_analytics(
    db: Session, program: str = None, county: str = None, gender: str = None
) -> dict:
    """
    Beneficiary demographics and distributions.
    Returns dict with:
    - age_distribution: list of {age_group: "16-20", count: N}
    - gender_distribution: list of {gender: "Female", count: N, percentage: float}
    - county_distribution: list of {county: "Nairobi", count: N, percentage: float}
    - program_distribution: list of {program: "Scholarship", count: N, percentage: float}
    """
    base = _beneficiary_query(db, program=program, county=county, gender=gender)

    age_bucket = case(
        (Beneficiary.age <= 20, "16-20"),
        (Beneficiary.age <= 25, "21-25"),
        (Beneficiary.age <= 30, "26-30"),
        (Beneficiary.age <= 35, "31-35"),
        else_="35+",
    )
    age_rows = (
        base.with_entities(age_bucket.label("age_group"), func.count(distinct(Beneficiary.id)))
        .filter(Beneficiary.age.isnot(None))
        .group_by(age_bucket)
        .all()
    )
    age_counts = {row.age_group: _to_int(row[1]) for row in age_rows}
    age_distribution = [
        {"age_group": group, "count": age_counts.get(group, 0)}
        for group in AGE_GROUPS
        if age_counts.get(group, 0) > 0
    ]

    gender_rows = (
        base.with_entities(Beneficiary.gender, func.count(distinct(Beneficiary.id)))
        .filter(Beneficiary.gender.isnot(None))
        .group_by(Beneficiary.gender)
        .order_by(Beneficiary.gender)
        .all()
    )
    gender_distribution = _build_distribution(gender_rows, "gender")

    county_rows = (
        base.with_entities(Beneficiary.county, func.count(distinct(Beneficiary.id)))
        .filter(Beneficiary.county.isnot(None))
        .group_by(Beneficiary.county)
        .order_by(Beneficiary.county)
        .all()
    )
    county_distribution = _build_distribution(county_rows, "county")

    program_rows_query = (
        db.query(
            Program.name.label("program"),
            func.count(distinct(ProgramEnrollment.beneficiary_id)).label("count"),
        )
        .join(ProgramEnrollment, ProgramEnrollment.program_id == Program.id)
    )
    if county or gender or program:
        program_rows_query = program_rows_query.join(
            Beneficiary, Beneficiary.beneficiary_id == ProgramEnrollment.beneficiary_id
        )
    if county:
        program_rows_query = program_rows_query.filter(
            func.lower(Beneficiary.county) == county.strip().lower()
        )
    if gender:
        program_rows_query = program_rows_query.filter(
            func.lower(Beneficiary.gender) == gender.strip().lower()
        )
    if program:
        program_rows_query = program_rows_query.filter(
            func.lower(Program.name) == program.strip().lower()
        )
    program_rows = (
        program_rows_query.group_by(Program.id, Program.name)
        .order_by(Program.name)
        .all()
    )
    program_distribution = _build_distribution(program_rows, "program")

    return {
        "age_distribution": age_distribution,
        "gender_distribution": gender_distribution,
        "county_distribution": county_distribution,
        "program_distribution": program_distribution,
    }


def get_outcomes_summary(db: Session, period_id: int = None) -> dict:
    """
    Outcomes and impact summary.
    Returns dict with:
    - total_outcomes, employment_rate, completion_rate
    - by_program: list of {program_name, total, employed, completed, employment_rate, completion_rate}
    - by_county: list of {county, total, employed, completed, employment_rate}
    """
    filters = []
    if period_id is not None:
        filters.append(Outcome.reporting_period_id == period_id)

    totals = db.query(
        func.count(Outcome.id).label("total"),
        func.count(
            case((_lower_status_match(Outcome.employment_status, EMPLOYED_STATUS), 1))
        ).label("employed"),
        func.count(
            case((_lower_status_match(Outcome.completion_status, COMPLETED_STATUS), 1))
        ).label("completed"),
    ).filter(*filters).one()

    by_program_rows = (
        db.query(
            Program.name.label("program_name"),
            func.count(Outcome.id).label("total"),
            func.count(
                case((_lower_status_match(Outcome.employment_status, EMPLOYED_STATUS), 1))
            ).label("employed"),
            func.count(
                case((_lower_status_match(Outcome.completion_status, COMPLETED_STATUS), 1))
            ).label("completed"),
        )
        .join(Program, Outcome.program_id == Program.id)
        .filter(*filters)
        .group_by(Program.id, Program.name)
        .order_by(Program.name)
        .all()
    )

    by_county_rows = (
        db.query(
            func.coalesce(Beneficiary.county, "Unknown").label("county"),
            func.count(Outcome.id).label("total"),
            func.count(
                case((_lower_status_match(Outcome.employment_status, EMPLOYED_STATUS), 1))
            ).label("employed"),
            func.count(
                case((_lower_status_match(Outcome.completion_status, COMPLETED_STATUS), 1))
            ).label("completed"),
        )
        .join(Beneficiary, Outcome.beneficiary_id == Beneficiary.beneficiary_id)
        .filter(*filters)
        .group_by(func.coalesce(Beneficiary.county, "Unknown"))
        .order_by(func.coalesce(Beneficiary.county, "Unknown"))
        .all()
    )

    total_outcomes = _to_int(totals.total)
    employed_total = _to_int(totals.employed)
    completed_total = _to_int(totals.completed)

    by_program = []
    for row in by_program_rows:
        row_total = _to_int(row.total)
        by_program.append(
            {
                "program_name": row.program_name,
                "total": row_total,
                "employed": _to_int(row.employed),
                "completed": _to_int(row.completed),
                "employment_rate": _percentage(_to_int(row.employed), row_total),
                "completion_rate": _percentage(_to_int(row.completed), row_total),
            }
        )

    by_county = []
    for row in by_county_rows:
        row_total = _to_int(row.total)
        by_county.append(
            {
                "county": row.county,
                "total": row_total,
                "employed": _to_int(row.employed),
                "completed": _to_int(row.completed),
                "employment_rate": _percentage(_to_int(row.employed), row_total),
            }
        )

    return {
        "total_outcomes": total_outcomes,
        "employment_rate": _percentage(employed_total, total_outcomes),
        "completion_rate": _percentage(completed_total, total_outcomes),
        "by_program": by_program,
        "by_county": by_county,
    }


def get_data_quality_summary(db: Session) -> dict:
    """
    Data quality metrics from actual issues table.
    Returns dict with:
    - score (0-100)
    - total_issues, missing_values, duplicates, invalid_values, inconsistent_formats
    - issues: list of {id, source_file, record_id, field_name, issue_type, original_value, severity, status}
    """
    total_issues = _to_int(db.query(func.count(DataQualityIssue.id)).scalar())

    missing_values = _to_int(
        db.query(func.count(DataQualityIssue.id))
        .filter(func.lower(DataQualityIssue.issue_type).like("%missing%"))
        .scalar()
    )
    duplicates = _to_int(
        db.query(func.count(DataQualityIssue.id))
        .filter(func.lower(DataQualityIssue.issue_type).like("%duplicate%"))
        .scalar()
    )
    invalid_values = _to_int(
        db.query(func.count(DataQualityIssue.id))
        .filter(func.lower(DataQualityIssue.issue_type).like("%invalid%"))
        .scalar()
    )
    inconsistent_formats = _to_int(
        db.query(func.count(DataQualityIssue.id))
        .filter(
            or_(
                func.lower(DataQualityIssue.issue_type).like("%inconsistent%"),
                func.lower(DataQualityIssue.issue_type).like("%format%"),
            )
        )
        .scalar()
    )

    total_records = (
        _count_rows(db, Beneficiary)
        + _count_rows(db, ProgramEnrollment)
        + _count_rows(db, Attendance)
        + _count_rows(db, Outcome)
    )
    score = round(_clamp(100.0 - (total_issues / max(total_records, 1)) * 100.0), 1)

    issue_records = (
        db.query(DataQualityIssue)
        .order_by(DataQualityIssue.detected_at.desc(), DataQualityIssue.id.desc())
        .all()
    )
    issues = [
        {
            "id": issue.id,
            "source_file": issue.source_file,
            "record_id": issue.record_id,
            "field_name": issue.field_name,
            "issue_type": issue.issue_type,
            "original_value": issue.original_value,
            "severity": issue.severity,
            "status": issue.status,
        }
        for issue in issue_records
    ]

    return {
        "score": score,
        "total_issues": total_issues,
        "missing_values": missing_values,
        "duplicates": duplicates,
        "invalid_values": invalid_values,
        "inconsistent_formats": inconsistent_formats,
        "issues": issues,
    }


def get_report_stats(db: Session) -> dict:
    """
    Report generation statistics.
    Returns dict with:
    - total_reports, completed, drafts, generating
    - reports_by_type: list of {report_type, count}
    """
    stats = db.query(
        func.count(Report.id).label("total_reports"),
        func.count(case((_lower_status_match(Report.status, "completed"), 1))).label(
            "completed"
        ),
        func.count(case((_lower_status_match(Report.status, "draft"), 1))).label(
            "drafts"
        ),
        func.count(
            case(
                (
                    func.lower(func.coalesce(Report.status, "")).in_(
                        [s.lower() for s in GENERATING_STATUSES]
                    ),
                    1,
                )
            )
        ).label("generating"),
    ).one()

    by_type_rows = (
        db.query(Report.report_type, func.count(Report.id).label("count"))
        .group_by(Report.report_type)
        .order_by(Report.report_type)
        .all()
    )
    reports_by_type = [
        {"report_type": row.report_type, "count": _to_int(row.count)}
        for row in by_type_rows
    ]

    return {
        "total_reports": _to_int(stats.total_reports),
        "completed": _to_int(stats.completed),
        "drafts": _to_int(stats.drafts),
        "generating": _to_int(stats.generating),
        "reports_by_type": reports_by_type,
    }
