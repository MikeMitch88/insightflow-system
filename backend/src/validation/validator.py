"""Data quality validation for raw CSV datasets.

Detects missing values, duplicates, inconsistent categorical values,
and invalid dates/rates, then returns cleaned DataFrames plus a full
list of issue records for reporting.
"""

import re
from typing import Callable, Optional

import pandas as pd


PROGRAM_FILE_KEYS = ("scholarship", "plus", "vocational", "tech")

CANONICAL_PROGRAM_BY_FILE = {
    "scholarship": "Scholarship",
    "plus": "Plus",
    "vocational": "Vocational",
    "tech": "Tech",
}

HIGH_SEVERITY_MISSING_COLUMNS = {"beneficiary_id", "id", "name", "full_name"}

BENEFICIARY_CRITICAL_COLUMNS = (
    "beneficiary_id",
    "name",
    "full_name",
    "phone",
    "email",
    "county",
    "gender",
)

BENEFICIARY_DATE_COLUMNS = (
    "date_of_birth",
    "enrollment_date",
    "registration_date",
    "start_date",
    "completion_date",
)

PROGRAM_CRITICAL_COLUMNS = ("beneficiary_id", "enrollment_date", "status", "program")

ATTENDANCE_CRITICAL_COLUMNS = (
    "beneficiary_id",
    "session_date",
    "date",
    "sessions_attended",
    "sessions_expected",
    "participation_rate",
)

OUTCOME_CRITICAL_COLUMNS = ("beneficiary_id", "outcome_type", "outcome_date", "status")

RATE_COLUMNS = ("participation_rate", "attendance_rate", "rate")

GENDER_MAP = {
    "m": "Male",
    "male": "Male",
    "f": "Female",
    "female": "Female",
}

STATUS_MAP = {
    "active": "active",
    "currently_enrolled": "active",
    "enrolled": "active",
    "in_progress": "active",
    "ongoing": "active",
    "current": "active",
    "in_school": "active",
    "complete": "completed",
    "completed": "completed",
    "graduated": "completed",
    "finished": "completed",
    "done": "completed",
    "passed": "completed",
    "dropped": "dropped_out",
    "drop_out": "dropped_out",
    "dropout": "dropped_out",
    "dropped_out": "dropped_out",
    "withdrawn": "dropped_out",
    "withdrew": "dropped_out",
    "discontinued": "dropped_out",
    "terminated": "dropped_out",
    "left": "dropped_out",
}

PROGRAM_NAME_MAP = {
    "scholarship": "Scholarship",
    "scholarships": "Scholarship",
    "scholarship_program": "Scholarship",
    "the_scholarship_program": "Scholarship",
    "plus": "Plus",
    "plus_program": "Plus",
    "girls_plus": "Plus",
    "g_plus": "Plus",
    "vocational": "Vocational",
    "vocational_training": "Vocational",
    "voc": "Vocational",
    "tech": "Tech",
    "technology": "Tech",
    "tech_program": "Tech",
    "tech_skills": "Tech",
}


# ---------------------------------------------------------------------------
# Standardizers
# ---------------------------------------------------------------------------

def standardize_county(name) -> str:
    """Normalize county names to title case with the 'County' suffix stripped."""
    if pd.isna(name):
        return "Unknown"
    text = re.sub(r"\s+", " ", str(name)).strip()
    if not text:
        return "Unknown"
    text = re.sub(r"\s+county$", "", text, flags=re.IGNORECASE).strip()
    return text.title()



def standardize_gender(gender) -> str:
    """Normalize gender values to 'Male', 'Female', 'Other' or 'Unknown'."""
    if pd.isna(gender) or not str(gender).strip():
        return "Unknown"
    key = str(gender).strip().lower()
    if key in GENDER_MAP:
        return GENDER_MAP[key]
    titled = str(gender).strip().title()
    if titled in {"Male", "Female"}:
        return titled
    return "Other"


def standardize_status(status) -> str:
    """Normalize enrollment/status values to active/completed/dropped_out."""
    if pd.isna(status) or not str(status).strip():
        return "unknown"
    key = _normalize_snake_case(status)
    return STATUS_MAP.get(key, key)


def standardize_program_name(name) -> Optional[str]:
    """Map free-text program names onto the four canonical programs."""
    if pd.isna(name):
        return None
    text = str(name).strip()
    if not text:
        return None
    key = _normalize_snake_case(text)
    if key in PROGRAM_NAME_MAP:
        return PROGRAM_NAME_MAP[key]
    return text.title()


def _normalize_snake_case(value) -> str:
    return re.sub(r"[\s\-]+", "_", str(value).strip().lower()).strip("_")


# ---------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------

def detect_missing_values(df: pd.DataFrame, critical_columns: list[str]) -> list[dict]:
    """Return one issue per missing/null value in the given columns."""
    issues: list[dict] = []
    if df is None or df.empty:
        return issues
    for column in critical_columns:
        if column not in df.columns:
            continue
        series = df[column]
        mask = series.isna() | (series.astype(str).str.strip() == "")
        for row_index in df.index[mask]:
            issues.append(
                {
                    "row_index": int(row_index),
                    "column": column,
                    "issue_type": "missing_value",
                    "severity": "high" if column in HIGH_SEVERITY_MISSING_COLUMNS else "medium",
                    "original_value": None,
                }
            )
    return issues


def detect_duplicates(df: pd.DataFrame, key_columns: list[str]) -> list[dict]:
    """Return one issue per row that duplicates an earlier record on key_columns."""
    issues: list[dict] = []
    if df is None or df.empty:
        return issues
    existing_keys = [column for column in key_columns if column in df.columns]
    if not existing_keys:
        return issues
    duplicate_mask = df.duplicated(subset=existing_keys, keep="first")
    for row_index in df.index[duplicate_mask]:
        issues.append(
            {
                "row_index": int(row_index),
                "issue_type": "duplicate",
                "severity": "high",
                "original_value": "duplicate record",
            }
        )
    return issues


def detect_inconsistent_values(
    df: pd.DataFrame, column: str, standardizer: Callable
) -> list[dict]:
    """Return one issue per value whose standardized form differs from the original."""
    issues: list[dict] = []
    if df is None or df.empty or column not in df.columns:
        return issues
    for row_index, original in df[column].items():
        if pd.isna(original):
            continue
        standardized = standardizer(original)
        if standardized == original:
            continue
        issues.append(
            {
                "row_index": int(row_index),
                "column": column,
                "issue_type": "inconsistent_value",
                "severity": "low",
                "original_value": str(original),
                "standardized_value": standardized,
            }
        )
    return issues


# ---------------------------------------------------------------------------
# Issue assembly helpers
# ---------------------------------------------------------------------------

def _build_issue(
    source_file: str,
    record_id,
    field_name: str,
    issue_type: str,
    original_value,
    severity: str,
    status: str = "pending",
) -> dict:
    return {
        "source_file": source_file,
        "record_id": str(record_id),
        "field_name": field_name,
        "issue_type": issue_type,
        "original_value": original_value,
        "severity": severity,
        "status": status,
    }


def _make_record_id_fn(df: pd.DataFrame):
    id_column = next(
        (c for c in ("beneficiary_id", "id") if c in df.columns), None
    )

    def record_id(row_index) -> str:
        if id_column is not None:
            value = df.at[row_index, id_column]
            if not pd.isna(value):
                return str(value)
        return str(row_index)

    return record_id


def _collect_missing_issues(df, source_file, critical_columns, record_id) -> list[dict]:
    issues = []
    for found in detect_missing_values(df, critical_columns):
        issues.append(
            _build_issue(
                source_file=source_file,
                record_id=record_id(found["row_index"]),
                field_name=found["column"],
                issue_type="missing_value",
                original_value=None,
                severity=found["severity"],
            )
        )
    return issues


def _collect_duplicate_issues(df, source_file, key_columns, record_id, field_name) -> list[dict]:
    issues = []
    for found in detect_duplicates(df, key_columns):
        issues.append(
            _build_issue(
                source_file=source_file,
                record_id=record_id(found["row_index"]),
                field_name=field_name,
                issue_type="duplicate",
                original_value="duplicate record",
                severity="high",
            )
        )
    return issues


def _standardize_column_with_issues(df, source_file, column, standardizer, severity, record_id) -> list[dict]:
    issues = []
    for found in detect_inconsistent_values(df, column, standardizer):
        issues.append(
            _build_issue(
                source_file=source_file,
                record_id=record_id(found["row_index"]),
                field_name=column,
                issue_type="inconsistent_value",
                original_value=found["original_value"],
                severity=severity,
            )
        )
    df[column] = df[column].apply(standardizer)
    return issues


# ---------------------------------------------------------------------------
# Per-file validators
# ---------------------------------------------------------------------------

def _validate_beneficiaries(df: pd.DataFrame, source_file: str) -> tuple[list[dict], pd.DataFrame]:
    issues: list[dict] = []
    record_id = _make_record_id_fn(df)

    critical = [c for c in BENEFICIARY_CRITICAL_COLUMNS if c in df.columns]
    issues.extend(_collect_missing_issues(df, source_file, critical, record_id))

    key_columns = [c for c in ("beneficiary_id", "id") if c in df.columns] or list(df.columns)
    issues.extend(
        _collect_duplicate_issues(df, source_file, key_columns, record_id, ", ".join(key_columns))
    )

    for column, standardizer in (("county", standardize_county), ("gender", standardize_gender)):
        if column in df.columns:
            issues.extend(
                _standardize_column_with_issues(
                    df, source_file, column, standardizer, "low", record_id
                )
            )

    for column in BENEFICIARY_DATE_COLUMNS:
        if column not in df.columns:
            continue
        parsed = pd.to_datetime(df[column], errors="coerce")
        invalid_mask = df[column].notna() & parsed.isna()
        for row_index in df.index[invalid_mask]:
            issues.append(
                _build_issue(
                    source_file=source_file,
                    record_id=record_id(row_index),
                    field_name=column,
                    issue_type="invalid_date",
                    original_value=str(df.at[row_index, column]),
                    severity="high",
                )
            )
        df[column] = parsed

    return issues, df


def _validate_program(df: pd.DataFrame, source_file: str) -> tuple[list[dict], pd.DataFrame]:
    issues: list[dict] = []
    record_id = _make_record_id_fn(df)

    critical = [c for c in PROGRAM_CRITICAL_COLUMNS if c in df.columns]
    issues.extend(_collect_missing_issues(df, source_file, critical, record_id))

    if "beneficiary_id" in df.columns:
        issues.extend(
            _collect_duplicate_issues(
                df, source_file, ["beneficiary_id"], record_id, "beneficiary_id"
            )
        )

    if "status" in df.columns:
        issues.extend(
            _standardize_column_with_issues(
                df, source_file, "status", standardize_status, "low", record_id
            )
        )

    if "program" in df.columns:
        issues.extend(
            _standardize_column_with_issues(
                df, source_file, "program", standardize_program_name, "medium", record_id
            )
        )
        fallback = CANONICAL_PROGRAM_BY_FILE.get(source_file, source_file.title())
        df["program"] = df["program"].fillna(fallback)

    return issues, df


def _validate_attendance(df: pd.DataFrame, source_file: str) -> tuple[list[dict], pd.DataFrame]:
    issues: list[dict] = []
    record_id = _make_record_id_fn(df)

    critical = [c for c in ATTENDANCE_CRITICAL_COLUMNS if c in df.columns]
    issues.extend(_collect_missing_issues(df, source_file, critical, record_id))

    for column in RATE_COLUMNS:
        if column not in df.columns:
            continue
        numeric = pd.to_numeric(df[column], errors="coerce")
        invalid_mask = numeric.notna() & ((numeric < 0) | (numeric > 100))
        for row_index in df.index[invalid_mask]:
            issues.append(
                _build_issue(
                    source_file=source_file,
                    record_id=record_id(row_index),
                    field_name=column,
                    issue_type="invalid_rate",
                    original_value=str(df.at[row_index, column]),
                    severity="medium",
                )
            )
        df[column] = numeric.clip(lower=0, upper=100)

    return issues, df


def _validate_outcomes(df: pd.DataFrame, source_file: str) -> tuple[list[dict], pd.DataFrame]:
    issues: list[dict] = []
    record_id = _make_record_id_fn(df)

    critical = [c for c in OUTCOME_CRITICAL_COLUMNS if c in df.columns]
    issues.extend(_collect_missing_issues(df, source_file, critical, record_id))

    for status_column in ("status", "outcome_status"):
        if status_column in df.columns:
            issues.extend(
                _standardize_column_with_issues(
                    df, source_file, status_column, standardize_status, "low", record_id
                )
            )

    return issues, df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_full_validation(
    raw_data: dict[str, pd.DataFrame],
) -> tuple[dict[str, pd.DataFrame], list[dict]]:
    """Validate every DataFrame and return (cleaned_data, all_issues)."""
    cleaned_data: dict[str, pd.DataFrame] = {}
    all_issues: list[dict] = []

    for source_file, df in (raw_data or {}).items():
        working = df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()

        if source_file == "beneficiaries":
            issues, working = _validate_beneficiaries(working, source_file)
        elif source_file == "attendance":
            issues, working = _validate_attendance(working, source_file)
        elif source_file == "outcomes":
            issues, working = _validate_outcomes(working, source_file)
        elif source_file in PROGRAM_FILE_KEYS:
            issues, working = _validate_program(working, source_file)
        else:
            issues = []

        cleaned_data[source_file] = working
        all_issues.extend(issues)

    return cleaned_data, all_issues
