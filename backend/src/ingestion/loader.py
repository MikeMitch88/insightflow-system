import pandas as pd
from pathlib import Path
from typing import Optional

DATA_RAW_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"

def load_csv(file_path: Path) -> pd.DataFrame:
    """Load a CSV file with encoding fallback."""
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding='latin-1')

def load_all_raw() -> dict[str, pd.DataFrame]:
    """Load all CSVs from data/raw/. Returns dict keyed by filename without extension."""
    result = {}
    if not DATA_RAW_DIR.exists():
        return result
    for csv_file in DATA_RAW_DIR.glob("*.csv"):
        result[csv_file.stem] = load_csv(csv_file)
    return result

def validate_schema(df: pd.DataFrame, expected_columns: list[str]) -> list[str]:
    """Check expected columns exist. Return list of missing column names."""
    return [col for col in expected_columns if col not in df.columns]
