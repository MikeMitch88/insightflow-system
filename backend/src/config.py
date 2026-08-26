import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env", override=False)
load_dotenv(BASE_DIR.parent / ".env", override=False)

PROJECT_DIR = BASE_DIR.parent
DATA_RAW_DIR = PROJECT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

DB_DIR = PROJECT_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

# Support PostgreSQL (Supabase) with SQLite fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DB_DIR / 'insightflow.db'}",
)

# AI Configuration
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")

# Groq Configuration (alternative to OpenAI)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
SHARED_PASSWORD = os.getenv("SHARED_PASSWORD", "Admin@123")

# CORS
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:4200,http://127.0.0.1:4200",
    ).split(",")
    if origin.strip()
]

# FAISS Vector Store
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", str(PROJECT_DIR / "data" / "faiss_index"))
FAISS_CHUNK_SIZE = int(os.getenv("FAISS_CHUNK_SIZE", "512"))
FAISS_CHUNK_OVERLAP = int(os.getenv("FAISS_CHUNK_OVERLAP", "50"))

# Report Export
REPORT_EXPORT_DIR = os.getenv("REPORT_EXPORT_DIR", str(PROJECT_DIR / "data" / "reports"))
os.makedirs(REPORT_EXPORT_DIR, exist_ok=True)

# Email / SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "insightful-system@inukafoundation.org")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
