"""Tests for synthetic data generation."""
import pytest
import pandas as pd
from pathlib import Path
from src.data_generation.generate_all import generate_all, DATA_RAW_DIR


@pytest.fixture(scope="module")
def generated_data():
    generate_all()
    return DATA_RAW_DIR


def test_beneficiaries_csv_exists(generated_data):
    assert (generated_data / "beneficiaries.csv").exists()


def test_beneficiaries_count(generated_data):
    df = pd.read_csv(generated_data / "beneficiaries.csv")
    unique = df["beneficiary_id"].nunique()
    assert unique >= 9000, f"Expected >= 9000 unique beneficiaries, got {unique}"


def test_program_csvs_exist(generated_data):
    for name in ["scholarship", "plus", "vocational", "tech"]:
        assert (generated_data / f"{name}.csv").exists()


def test_attendance_csv_exists(generated_data):
    assert (generated_data / "attendance.csv").exists()
    df = pd.read_csv(generated_data / "attendance.csv")
    assert len(df) > 0


def test_outcomes_csv_exists(generated_data):
    assert (generated_data / "outcomes.csv").exists()
    df = pd.read_csv(generated_data / "outcomes.csv")
    assert len(df) > 0


def test_kenyan_counties_used(generated_data):
    df = pd.read_csv(generated_data / "beneficiaries.csv")
    counties = df["county"].dropna().unique()
    assert len(counties) >= 10, f"Expected >= 10 counties, got {len(counties)}"


def test_gender_distribution(generated_data):
    df = pd.read_csv(generated_data / "beneficiaries.csv")
    female_count = len(df[df["gender"].str.lower().isin(["female", "f"])])
    total = len(df)
    ratio = female_count / total
    assert 0.35 <= ratio <= 0.75, f"Female ratio {ratio:.2f} outside expected range"
