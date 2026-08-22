# InsightFlow System

> **Automating Reporting. Turning Data Into Actionable Intelligence.**

Enterprise program intelligence and automated reporting platform for **KPC Inuka Foundation**, reducing manual data compilation time by over 50%.

---

## Overview

InsightFlow System transforms fragmented operational data across four program pillars into unified analytics, AI-powered insights, and automated donor reports.

| Data Flow | |
|---|---|
| Fragmented Data | Trusted Data | Unified Intelligence | Automated Reporting | Better Decisions |

### Programs

- **Scholarship** — Educational scholarships across Kenyan institutions
- **Plus** — Life skills, financial literacy, and personal development
- **Vocational** — Vocational training and certification programs
- **Tech** — Technology and digital skills training

---

## Features

### Executive Dashboard
- Real-time KPIs computed from the database (beneficiaries, completion rates, attendance, outcomes)
- Beneficiary growth trends, program performance, and distribution charts
- Quarter-over-quarter comparisons

### Program Intelligence
- Per-program performance metrics with completion, attendance, and participation rates
- Filterable by period, program, county, and gender

### Beneficiary Analytics
- Demographic breakdowns by age, gender, county, and program
- Geographic distribution across 15 Kenyan counties

### Outcomes & Impact
- Employment rates, completion rates, and program efficacy metrics
- Executive-friendly impact summaries

### Automated Reporting
- Generate Executive, Program Performance, Donor, and M&E reports
- 4-step report builder with reusable templates
- Export to CSV and Excel

### AI Intelligence
- AI Assistant answering questions using verified organizational metrics
- Automated insights detecting significant trends, anomalies, and performance gaps
- Template-based responses (no external API required) or LLM-powered via API key

### Data Pipeline
- Full ETL pipeline: Extract, Transform, Validate, Unify, Load
- Data quality scoring and issue tracking
- Stage 1 (raw data) to Stage 2 (unified intelligence) visualization

---

## Architecture

```
FAKER SYNTHETIC DATA
        ↓
RAW CSV DATA (10,000+ beneficiaries)
        ↓
INGESTION → VALIDATION → TRANSFORMATION → UNIFICATION
        ↓
POSTGRESQL (9 normalized tables)
        ↓
ANALYTICS / KPI ENGINE
        ↓
FASTAPI (15+ REST endpoints)
        ↓
ANGULAR 17 FRONTEND (12 enterprise pages)

AI operates as an intelligence layer over verified data.
REPORTING operates on the same analytics layer.
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Angular 17, TypeScript, CSS |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Database | PostgreSQL 17 |
| Data Engineering | Pandas, NumPy, Faker |
| AI | OpenAI-compatible API (optional) |
| Reporting | CSV/Excel export via Pandas + OpenPyXL |
| DevOps | Docker, Docker Compose |
| Testing | Pytest |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Option 1: Docker (Recommended)

```bash
docker-compose up --build
```

Then load data:

```bash
docker-compose exec backend python src/run_pipeline.py --all
```

- Frontend: http://localhost:4200
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

**1. Create PostgreSQL database:**

```sql
CREATE USER insightflow WITH PASSWORD 'insightflow_secret' SUPERUSER;
CREATE DATABASE insightflow_db OWNER insightflow;
```

**2. Install backend dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

**3. Generate data and load into database:**

```bash
python src/run_pipeline.py --all
```

**4. Start the backend:**

```bash
uvicorn src.main:app --reload --port 8000
```

**5. Install and start the frontend:**

```bash
cd frontend
npm install
ng serve
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/dashboard/summary` | GET | Executive dashboard KPIs |
| `/api/dashboard/trends` | GET | Quarter-over-quarter trends |
| `/api/programs/performance` | GET | Per-program metrics |
| `/api/beneficiaries` | GET | Paginated beneficiary list |
| `/api/beneficiaries/analytics` | GET | Demographic distributions |
| `/api/outcomes` | GET | Outcomes and impact summary |
| `/api/data-quality` | GET | Data quality score and issues |
| `/api/data-sources` | GET | Data source status |
| `/api/pipeline/status` | GET | Pipeline status |
| `/api/reports` | GET | List reports |
| `/api/reports/generate` | POST | Generate a report |
| `/api/reports/{id}` | GET | Get report details |
| `/api/ai/chat` | POST | AI Assistant chat |
| `/api/ai/insights` | GET | Automated AI insights |
| `/api/periods` | GET | Reporting periods |

---

## Project Structure

```
insightflow-ai/
├── backend/
│   ├── src/
│   │   ├── data_generation/    # Faker synthetic data
│   │   ├── ingestion/          # CSV loading
│   │   ├── validation/         # Data quality checks
│   │   ├── transformation/     # Data standardization
│   │   ├── analytics/          # KPI engine
│   │   ├── models/             # SQLAlchemy + Pydantic
│   │   ├── api/                # FastAPI routers
│   │   ├── ai/                 # AI service layer
│   │   ├── reporting/          # Report generation
│   │   ├── main.py             # FastAPI app
│   │   └── run_pipeline.py     # Full pipeline runner
│   ├── tests/                  # Pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── pages/          # 12 page components
│   │   │   ├── services/       # API service
│   │   │   └── app.module.ts
│   │   └── styles.css          # Design system
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── data/
│   ├── raw/                    # Generated CSVs
│   └── processed/              # Unified datasets
├── docker-compose.yml
├── .env
└── .env.example
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://insightflow:insightflow_secret@localhost:5432/insightflow_db` | PostgreSQL connection |
| `AI_API_KEY` | (empty) | OpenAI API key (optional) |
| `AI_MODEL` | `gpt-4` | LLM model name |
| `AI_BASE_URL` | `https://api.openai.com/v1` | LLM API base URL |
| `JWT_SECRET` | `change-this-in-production` | JWT signing secret |

---

## License

Built for KPC Inuka Foundation.
