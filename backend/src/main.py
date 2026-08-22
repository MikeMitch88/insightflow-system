import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.database import init_db
from src.api.dashboard import router as dashboard_router
from src.api.programs import router as programs_router
from src.api.beneficiaries import router as beneficiaries_router
from src.api.outcomes import router as outcomes_router
from src.api.data_quality import router as data_quality_router
from src.api.reports import router as reports_router
from src.api.ai_routes import router as ai_router
from src.api.periods import router as periods_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="InsightFlow System",
    description="Program Intelligence Platform for KPC Inuka Foundation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(programs_router)
app.include_router(beneficiaries_router)
app.include_router(outcomes_router)
app.include_router(data_quality_router)
app.include_router(reports_router)
app.include_router(ai_router)
app.include_router(periods_router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "InsightFlow System", "version": "1.0.0"}
