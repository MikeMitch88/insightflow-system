import os
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://insightflow:insightflow_secret@localhost:5432/insightflow_db")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR.parent / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR.parent / "data" / "processed"
