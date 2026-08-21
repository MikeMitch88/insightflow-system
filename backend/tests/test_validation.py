"""Tests for data validation."""
import pytest
from src.validation.validator import (
    standardize_county, standardize_gender, standardize_status,
    standardize_program_name
)


def test_standardize_county_uppercase():
    assert standardize_county("NAIROBI") == "Nairobi"


def test_standardize_county_with_suffix():
    assert standardize_county("Nairobi County") == "Nairobi"


def test_standardize_county_lowercase():
    assert standardize_county("mombasa") == "Mombasa"


def test_standardize_county_nan():
    assert standardize_county(None) == "Unknown"
    import pandas as pd
    assert standardize_county(pd.NA) == "Unknown"


def test_standardize_gender_male():
    assert standardize_gender("M") == "Male"
    assert standardize_gender("male") == "Male"
    assert standardize_gender("MALE") == "Male"


def test_standardize_gender_female():
    assert standardize_gender("F") == "Female"
    assert standardize_gender("female") == "Female"
    assert standardize_gender("FEMALE") == "Female"


def test_standardize_status_completed():
    assert standardize_status("complete") == "completed"
    assert standardize_status("COMPLETED") == "completed"
    assert standardize_status("Completed") == "completed"


def test_standardize_status_dropped():
    assert standardize_status("Dropped") == "dropped_out"
    assert standardize_status("dropped out") == "dropped_out"


def test_standardize_program():
    assert standardize_program_name("SCHOLARSHIP") == "Scholarship"
    assert standardize_program_name("scholarship program") == "Scholarship"
    assert standardize_program_name("Tech") == "Tech"
