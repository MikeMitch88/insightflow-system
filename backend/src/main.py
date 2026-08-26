import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.database import init_db, SessionLocal
from src.config import ALLOWED_ORIGINS
from src.auth.service import seed_default_roles

# Existing routers
from src.api.dashboard import router as dashboard_router
from src.api.programs import router as programs_router
from src.api.beneficiaries import router as beneficiaries_router
from src.api.outcomes import router as outcomes_router
from src.api.data_quality import router as data_quality_router
from src.api.reports import router as reports_router
from src.api.ai_routes import router as ai_router
from src.api.periods import router as periods_router
from src.api.admin import router as admin_router
from src.auth.routes import router as auth_router

# New routers
from src.api.cross_pillar import router as cross_pillar_router
from src.api.workflow_routes import router as workflow_router
from src.api.report_gen_routes import router as report_gen_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_default_roles(db)
    except Exception:
        db.rollback()
    finally:
        db.close()
    yield


app = FastAPI(
    title="Insightful System - Intelligent Automated Reporting",
    description="AI-Powered NGO Reporting & Admin Workflow System with RBAC",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(programs_router)
app.include_router(beneficiaries_router)
app.include_router(outcomes_router)
app.include_router(data_quality_router)
app.include_router(reports_router)
app.include_router(ai_router)
app.include_router(periods_router)
app.include_router(admin_router)

# New routers
app.include_router(cross_pillar_router)
app.include_router(workflow_router)
app.include_router(report_gen_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Insightful System - Intelligent Automated Reporting",
        "version": "2.0.0",
        "features": [
            "rbac_4tier",
            "cross_pillar_data_collection",
            "rag_ai_reporting",
            "workflow_state_machine",
            "audit_trail",
        ],
    }
