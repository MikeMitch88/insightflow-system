"""
InsightFlow System - Main Pipeline Orchestrator

Usage:
    python src/main.py --generate     # Generate synthetic data
    python src/main.py --etl          # Run ETL pipeline
    python src/main.py --load         # Load data into PostgreSQL
    python src/main.py --all          # Run full pipeline
    python src/main.py                # Default: run full pipeline
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def step_generate():
    print("=" * 60)
    print("STEP 1: GENERATING SYNTHETIC DATA")
    print("=" * 60)
    from src.data_generation.generate_all import generate_all
    generate_all()
    print("Data generation complete.\n")


def step_etl():
    print("=" * 60)
    print("STEP 2: RUNNING ETL PIPELINE")
    print("=" * 60)
    from src.ingestion.loader import load_all_raw
    from src.validation.validator import run_full_validation
    from src.transformation.transformer import unify_all

    print("Loading raw data...")
    raw_data = load_all_raw()
    print(f"  Loaded {len(raw_data)} CSV files: {list(raw_data.keys())}")

    print("\nValidating and cleaning data...")
    cleaned_data, issues = run_full_validation(raw_data)
    print(f"  Found {len(issues)} data quality issues")
    print(f"  Cleaned {len(cleaned_data)} datasets")

    print("\nTransforming and unifying data...")
    unified = unify_all(cleaned_data)
    print(f"  Unified datasets: {list(unified.keys())}")

    processed_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    import pandas as pd
    for name, df in unified.items():
        out_path = processed_dir / f"{name}.csv"
        df.to_csv(out_path, index=False)
        print(f"  Saved {out_path.name} ({len(df)} rows)")

    for name, df in cleaned_data.items():
        if name not in unified:
            out_path = processed_dir / f"{name}_cleaned.csv"
            df.to_csv(out_path, index=False)
            print(f"  Saved {out_path.name} ({len(df)} rows)")

    return cleaned_data, unified, issues


def step_load(cleaned_data=None, unified=None, issues=None):
    print("=" * 60)
    print("STEP 3: LOADING INTO DATABASE")
    print("=" * 60)

    from src.config import DATABASE_URL
    from sqlalchemy import create_engine, text
    from src.models.models import Base
    from src.database import SessionLocal, init_db

    engine = create_engine(DATABASE_URL)

    print("Creating database tables...")
    init_db()
    print("  Tables created.")

    from src.models.models import (
        ReportingPeriod, Beneficiary, Program,
        ProgramEnrollment, Attendance, Outcome, DataQualityIssue
    )
    from datetime import date
    import pandas as pd

    session = SessionLocal()
    try:
        periods = []
        quarter_dates = {
            "Q1 2025": (date(2025, 1, 1), date(2025, 3, 31)),
            "Q2 2025": (date(2025, 4, 1), date(2025, 6, 30)),
            "Q3 2025": (date(2025, 7, 1), date(2025, 9, 30)),
            "Q4 2025": (date(2025, 10, 1), date(2025, 12, 31)),
            "Q1 2026": (date(2026, 1, 1), date(2026, 3, 31)),
            "Q2 2026": (date(2026, 4, 1), date(2026, 6, 30)),
            "Q3 2026": (date(2026, 7, 1), date(2026, 9, 30)),
        }
        for i, (name, (start, end)) in enumerate(quarter_dates.items(), 1):
            p = ReportingPeriod(
                id=i, name=name, year=int(name.split()[1]),
                quarter=int(name[1]), start_date=start, end_date=end,
                is_current=(name == "Q3 2026")
            )
            session.merge(p)
            periods.append(p)
        session.commit()
        print(f"  Inserted {len(periods)} reporting periods.")

        programs_data = [
            ("Scholarship", "Educational scholarship program"),
            ("Plus", "Life skills and personal development"),
            ("Vocational", "Vocational training and skills"),
            ("Tech", "Technology and digital skills"),
        ]
        for name, desc in programs_data:
            p = Program(name=name, description=desc)
            session.merge(p)
        session.commit()
        print("  Inserted 4 programs.")

        if unified and "beneficiaries" in unified:
            ben_df = unified["beneficiaries"]
            count = 0
            for _, row in ben_df.iterrows():
                b = Beneficiary(
                    beneficiary_id=str(row.get("beneficiary_id", "")),
                    first_name=str(row.get("first_name", "")),
                    last_name=str(row.get("last_name", "")),
                    gender=str(row.get("gender", "Unknown")),
                    date_of_birth=row.get("date_of_birth"),
                    age=int(row.get("age", 0)) if pd.notna(row.get("age")) else None,
                    phone=str(row.get("phone", "")) if pd.notna(row.get("phone")) else None,
                    email=str(row.get("email", "")) if pd.notna(row.get("email")) else None,
                    county=str(row.get("county", "")),
                    sub_county=str(row.get("sub_county", "")) if pd.notna(row.get("sub_county")) else None,
                )
                session.merge(b)
                count += 1
                if count % 1000 == 0:
                    session.commit()
            session.commit()
            print(f"  Inserted {count} beneficiaries.")

        if unified and "program_enrollments" in unified:
            enroll_df = unified["program_enrollments"]
            program_map = {"Scholarship": 1, "Plus": 2, "Vocational": 3, "Tech": 4}
            period_map = {name: i for i, name in enumerate(quarter_dates.keys(), 1)}
            count = 0
            for _, row in enroll_df.iterrows():
                prog_name = str(row.get("program", ""))
                period_name = str(row.get("reporting_period", ""))
                e = ProgramEnrollment(
                    beneficiary_id=str(row.get("beneficiary_id", "")),
                    program_id=program_map.get(prog_name, 1),
                    enrollment_date=row.get("enrollment_date"),
                    status=str(row.get("status", "active")),
                    reporting_period_id=period_map.get(period_name, 1),
                    education_level=str(row.get("education_level", "")) if pd.notna(row.get("education_level")) else None,
                    academic_year=str(row.get("academic_year", "")) if pd.notna(row.get("academic_year")) else None,
                    institution=str(row.get("institution", "")) if pd.notna(row.get("institution")) else None,
                    activity=str(row.get("activity", "")) if pd.notna(row.get("activity")) else None,
                    sessions_attended=int(row.get("sessions_attended", 0)) if pd.notna(row.get("sessions_attended")) else None,
                    sessions_expected=int(row.get("sessions_expected", 0)) if pd.notna(row.get("sessions_expected")) else None,
                    participation_rate=float(row.get("participation_rate", 0)) if pd.notna(row.get("participation_rate")) else None,
                    course=str(row.get("course", "")) if pd.notna(row.get("course")) else None,
                    training_center=str(row.get("training_center", "")) if pd.notna(row.get("training_center")) else None,
                    training_provider=str(row.get("training_provider", "")) if pd.notna(row.get("training_provider")) else None,
                    certification_status=str(row.get("certification_status", "")) if pd.notna(row.get("certification_status")) else None,
                    employment_status=str(row.get("employment_status", "")) if pd.notna(row.get("employment_status")) else None,
                    skills_acquired=str(row.get("skills_acquired", "")) if pd.notna(row.get("skills_acquired")) else None,
                )
                session.add(e)
                count += 1
                if count % 1000 == 0:
                    session.commit()
            session.commit()
            print(f"  Inserted {count} program enrollments.")

        if unified and "attendance" in unified:
            att_df = unified["attendance"]
            program_map = {"Scholarship": 1, "Plus": 2, "Vocational": 3, "Tech": 4}
            period_map = {name: i for i, name in enumerate(quarter_dates.keys(), 1)}
            count = 0
            for _, row in att_df.iterrows():
                a = Attendance(
                    beneficiary_id=str(row.get("beneficiary_id", "")),
                    program_id=program_map.get(str(row.get("program", "")), 1),
                    reporting_period_id=period_map.get(str(row.get("reporting_period", "")), 1),
                    sessions_expected=int(row.get("sessions_expected", 0)) if pd.notna(row.get("sessions_expected")) else 0,
                    sessions_attended=int(row.get("sessions_attended", 0)) if pd.notna(row.get("sessions_attended")) else 0,
                    attendance_rate=float(row.get("attendance_rate", 0)) if pd.notna(row.get("attendance_rate")) else 0,
                )
                session.add(a)
                count += 1
                if count % 1000 == 0:
                    session.commit()
            session.commit()
            print(f"  Inserted {count} attendance records.")

        if unified and "outcomes" in unified:
            out_df = unified["outcomes"]
            program_map = {"Scholarship": 1, "Plus": 2, "Vocational": 3, "Tech": 4}
            period_map = {name: i for i, name in enumerate(quarter_dates.keys(), 1)}
            count = 0
            for _, row in out_df.iterrows():
                o = Outcome(
                    beneficiary_id=str(row.get("beneficiary_id", "")),
                    program_id=program_map.get(str(row.get("program", "")), 1),
                    reporting_period_id=period_map.get(str(row.get("reporting_period", "")), 1),
                    outcome_type=str(row.get("outcome_type", "")),
                    outcome_status=str(row.get("outcome_status", "")),
                    employment_status=str(row.get("employment_status", "")) if pd.notna(row.get("employment_status")) else None,
                    completion_status=str(row.get("completion_status", "")) if pd.notna(row.get("completion_status")) else None,
                )
                session.add(o)
                count += 1
                if count % 1000 == 0:
                    session.commit()
            session.commit()
            print(f"  Inserted {count} outcome records.")

        if issues:
            count = 0
            for issue in issues:
                dq = DataQualityIssue(
                    source_file=issue.get("source_file", ""),
                    record_id=str(issue.get("record_id", "")),
                    field_name=issue.get("field_name", ""),
                    issue_type=issue.get("issue_type", ""),
                    original_value=str(issue.get("original_value", ""))[:500] if issue.get("original_value") else None,
                    corrected_value=str(issue.get("corrected_value", ""))[:500] if issue.get("corrected_value") else None,
                    severity=issue.get("severity", "medium"),
                    status=issue.get("status", "detected"),
                )
                session.add(dq)
                count += 1
                if count % 1000 == 0:
                    session.commit()
            session.commit()
            print(f"  Inserted {count} data quality issues.")

    finally:
        session.close()

    print("Database loading complete.\n")


def main():
    parser = argparse.ArgumentParser(description="InsightFlow System Pipeline")
    parser.add_argument("--generate", action="store_true", help="Generate synthetic data")
    parser.add_argument("--etl", action="store_true", help="Run ETL pipeline")
    parser.add_argument("--load", action="store_true", help="Load into database")
    parser.add_argument("--all", action="store_true", help="Run full pipeline")
    args = parser.parse_args()

    if args.all or not any([args.generate, args.etl, args.load]):
        step_generate()
        cleaned, unified, issues = step_etl()
        step_load(cleaned, unified, issues)
        print("=" * 60)
        print("FULL PIPELINE COMPLETE")
        print("=" * 60)
    else:
        if args.generate:
            step_generate()
        if args.etl:
            step_etl()
        if args.load:
            step_load()


if __name__ == "__main__":
    main()
