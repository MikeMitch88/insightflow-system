"""Transform validated datasets into unified, analysis-ready tables."""

import re

import numpy as np
import pandas as pd

try:
    from ..validation.validator import standardize_status
except ImportError:  # pragma: no cover - fallback for direct/script execution
    from src.validation.validator import standardize_status


PROGRAM_SOURCES = {
    "scholarship": "Scholarship",
    "plus": "Plus",
    "vocational": "Vocational",
    "tech": "Tech",
}

UNIFIED_PROGRAM_COLUMNS = [
    "beneficiary_id",
    "program",
    "enrollment_date",
    "reporting_period",
    "status",
    "education_level",
    "academic_year",
    "institution",
    "activity",
    "sessions_attended",
    "sessions_expected",
    "participation_rate",
    "course",
    "training_center",
    "training_provider",
    "certification_status",
    "employment_status",
    "skills_acquired",
]

ENROLLMENT_DATE_ALIASES = (
    "enrollment_date",
    "date_of_enrollment",
    "start_date",
    "date_joined",
)

BENEFICIARY_TEXT_DEFAULTS = {
    "county": "Unknown",
    "sub_county": "Unknown",
    "gender": "Unknown",
    "phone": "",
    "email": "",
    "school": "Unknown",
    "education_level": "Unknown",
}

BENEFICIARY_DATE_COLUMNS = ("date_of_birth", "enrollment_date", "registration_date")

ATTENDANCE_NUMERIC_COLUMNS = ("sessions_attended", "sessions_expected")

ATTENDANCE_RATE_CANDIDATES = ("participation_rate", "attendance_rate", "rate")

OUTCOME_TYPE_CANDIDATES = ("outcome_type", "type")

OUTCOME_STATUS_CANDIDATES = ("status", "outcome_status")

OUTCOME_DATE_CANDIDATES = ("outcome_date", "date", "completion_date")

OUTCOME_TYPE_MAP = {
    "employment": "Employment",
    "employed": "Employment",
    "job_placement": "Employment",
    "internship": "Employment",
    "education": "Education",
    "further_education": "Education",
    "continuing_education": "Education",
    "university": "Education",
    "college": "Education",
    "entrepreneurship": "Entrepreneurship",
    "business": "Entrepreneurship",
    "self_employment": "Entrepreneurship",
    "self_employed": "Entrepreneurship",
    "other": "Other",
}


def _empty_or_copy(df) -> pd.DataFrame:
    return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()


def _pick_column(df: pd.DataFrame, candidates) -> str | None:
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


def _normalize_snake_case(value) -> str:
    return re.sub(r"[\s\-]+", "_", str(value).strip().lower()).strip("_")


# ---------------------------------------------------------------------------
# Beneficiaries
# ---------------------------------------------------------------------------

def transform_beneficiaries(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce beneficiary types and fill missing non-critical fields."""
    out = _empty_or_copy(df)
    if out.empty:
        return out

    if "age" in out.columns:
        out["age"] = pd.to_numeric(out["age"], errors="coerce")

    for column, default in BENEFICIARY_TEXT_DEFAULTS.items():
        if column in out.columns:
            out[column] = out[column].fillna(default)

    for column in BENEFICIARY_DATE_COLUMNS:
        if column in out.columns:
            out[column] = pd.to_datetime(out[column], errors="coerce")

    if "status" in out.columns:
        out["status"] = out["status"].apply(standardize_status)

    return out


# ---------------------------------------------------------------------------
# Program enrollments
# ---------------------------------------------------------------------------

def transform_program_data(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Merge the four program datasets into one unified enrollments table."""
    frames = []
    for source_key, program_label in PROGRAM_SOURCES.items():
        df = (data or {}).get(source_key)
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue
        out = df.copy()

        date_column = _pick_column(out, ENROLLMENT_DATE_ALIASES)
        if date_column is not None and date_column != "enrollment_date":
            out = out.rename(columns={date_column: "enrollment_date"})
        if "enrollment_date" in out.columns:
            out["enrollment_date"] = pd.to_datetime(out["enrollment_date"], errors="coerce")

        if "status" in out.columns:
            out["status"] = out["status"].apply(standardize_status)

        if "program" not in out.columns:
            out["program"] = program_label
        else:
            out["program"] = out["program"].fillna(program_label)

        for numeric_column in ("sessions_attended", "sessions_expected", "participation_rate"):
            if numeric_column in out.columns:
                out[numeric_column] = pd.to_numeric(out[numeric_column], errors="coerce")

        frames.append(out)

    if not frames:
        return pd.DataFrame(columns=UNIFIED_PROGRAM_COLUMNS)

    merged = pd.concat(frames, ignore_index=True, sort=False)
    for column in UNIFIED_PROGRAM_COLUMNS:
        if column not in merged.columns:
            merged[column] = np.nan
    return merged[UNIFIED_PROGRAM_COLUMNS]


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------

def transform_attendance(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure numeric session counts and compute missing rates."""
    out = _empty_or_copy(df)
    if out.empty:
        return out

    for column in ATTENDANCE_NUMERIC_COLUMNS:
        if column in out.columns:
            out[column] = pd.to_numeric(out[column], errors="coerce")

    rate_column = _pick_column(out, ATTENDANCE_RATE_CANDIDATES)
    if rate_column is not None:
        out[rate_column] = pd.to_numeric(out[rate_column], errors="coerce")

        if {"sessions_attended", "sessions_expected"} <= set(out.columns):
            expected = out["sessions_expected"]
            computable = (
                out["sessions_attended"].notna()
                & expected.notna()
                & (expected > 0)
                & out[rate_column].isna()
            )
            out.loc[computable, rate_column] = (
                out.loc[computable, "sessions_attended"] / expected[computable] * 100
            )

        out[rate_column] = out[rate_column].clip(lower=0, upper=100)

    return out


# ---------------------------------------------------------------------------
# Outcomes
# ---------------------------------------------------------------------------

def _standardize_outcome_type(value) -> str:
    if pd.isna(value) or not str(value).strip():
        return "Unknown"
    key = _normalize_snake_case(value)
    if key in OUTCOME_TYPE_MAP:
        return OUTCOME_TYPE_MAP[key]
    return str(value).strip().title()


def transform_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize outcome types and statuses, coercing dates."""
    out = _empty_or_copy(df)
    if out.empty:
        return out

    type_column = _pick_column(out, OUTCOME_TYPE_CANDIDATES)
    if type_column is not None:
        out[type_column] = out[type_column].apply(_standardize_outcome_type)

    for status_column in OUTCOME_STATUS_CANDIDATES:
        if status_column in out.columns:
            out[status_column] = out[status_column].apply(standardize_status)

    for date_column in OUTCOME_DATE_CANDIDATES:
        if date_column in out.columns:
            out[date_column] = pd.to_datetime(out[date_column], errors="coerce")

    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def unify_all(cleaned_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Run every transform and return the unified datasets."""
    cleaned_data = cleaned_data or {}
    return {
        "beneficiaries": transform_beneficiaries(cleaned_data.get("beneficiaries")),
        "program_enrollments": transform_program_data(cleaned_data),
        "attendance": transform_attendance(cleaned_data.get("attendance")),
        "outcomes": transform_outcomes(cleaned_data.get("outcomes")),
    }
