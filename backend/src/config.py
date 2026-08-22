import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env configurations
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")

PROJECT_DIR = BASE_DIR.parent
DATA_RAW_DIR = PROJECT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

DB_DIR = PROJECT_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DB_DIR / 'insightflow.db'}"
)
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
