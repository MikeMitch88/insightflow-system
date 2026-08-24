# InsightFlow System

### KPC Inuka Foundation — Program Intelligence, Reporting & Decision Platform

**Hackathon 2 — Stage 2 Submission**
**Domain 4, Problem 7: Automating the Reporting Process**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Our Solution](#3-our-solution)
4. [System Architecture](#4-system-architecture)
5. [Data Pipeline & ETL](#5-data-pipeline--etl)
6. [Key Features & Pages](#6-key-features--pages)
7. [AI Integration](#7-ai-integration)
8. [Automated Reporting](#8-automated-reporting)
9. [User Roles & Access Control](#9-user-roles--access-control)
10. [Technical Implementation](#10-technical-implementation)
11. [Database Schema](#11-database-schema)
12. [API Endpoints](#12-api-endpoints)
13. [Data Quality Management](#13-data-quality-management)
14. [Impact & Metrics](#14-impact--metrics)
15. [How to Run](#15-how-to-run)
16. [Project Structure](#16-project-structure)

---

## 1. Executive Summary

KPC Inuka Foundation manages four distinct programs — Scholarship, Plus, Vocational, and Tech — each generating large volumes of operational data. Currently, staff spend significant time manually consolidating, validating, analysing, and formatting this fragmented information to produce monthly and quarterly reports. This process is time-consuming, error-prone, and delays access to management insights.

**InsightFlow System** automates this entire process. It ingests data from all four program pillars, validates and standardises it, calculates key performance indicators, applies AI-powered analysis, and generates ready-to-use reports — transforming fragmented data into trusted insights and better decisions.

**Key Outcomes:**
- Automated data ingestion from 4 program sources into a unified database
- 10,000 synthetic beneficiaries across 7 quarterly reporting periods (Q1 2025 – Q3 2026)
- 7 computed KPI functions covering dashboard, programs, beneficiaries, outcomes, and trends
- 13 interactive frontend pages with role-based access control
- 21 REST API endpoints powering the full platform
- Report generation in Excel and CSV with AI-enhanced analysis
- **Target: ≥50% reduction in manual reporting effort**

---

## 2. Problem Statement

### The Current Reality

KPC Inuka Foundation has four main programs, each producing its own data:

```
Scholarship data ─┐
Plus data ────────┤
Vocational data ──┼──> Manual Excel/Compilation
Tech data ────────┘            │
                               ↓
                     Manual calculations
                               ↓
                     Manual report writing
                               ↓
                   Monthly/Quarterly Report
                               ↓
                     Management decisions
```

### The Problems This Causes

| Problem | Impact |
|---------|--------|
| **Manual data compilation** | Officers spend hours combining data from 4 program pillars into spreadsheets |
| **Slow report preparation** | Monthly and quarterly reports take days to build from scratch |
| **Data inconsistency** | Different programs use different formats, statuses, and naming conventions |
| **Errors in calculations** | Manual formulas are error-prone and hard to audit |
| **Delayed management insights** | Leaders wait days or weeks for a completed report before seeing performance |
| **Difficulty turning data into decisions** | No way to quickly identify why a metric changed or what action to take |

### One-Sentence Summary

> KPC Inuka Foundation spends significant time manually consolidating fragmented data from its four program pillars to produce reports, causing delays, inconsistencies, and limited visibility into program performance.

---

## 3. Our Solution

### The Automated Flow

```
Scholarship ─┐
Plus ────────┤
Vocational ──┼──> Unified Data Platform
Tech ────────┘          │
                        ↓
               Validate & Standardise
                        ↓
                  Calculate KPIs
                        ↓
                  AI Analysis
                        ↓
             Automated Report Generation
                        ↓
              Better, Faster Decisions
```

### What InsightFlow System Solves

1. **Manual data compilation** — Officers no longer manually combine data from four program pillars. The system ingests all sources automatically.

2. **Slow report preparation** — Monthly and quarterly reports are generated from the latest data in seconds, not days.

3. **Data inconsistency and errors** — The system validates incoming data, standardises statuses, and applies consistent calculations before data enters reports.

4. **Delayed management insights** — Dashboards show real-time KPIs, trends, and issues. No waiting for a completed report.

5. **Difficulty turning data into decisions** — The AI layer identifies important changes and helps users understand why a metric changed and what action may be appropriate.

### Pitch Statement

> InsightFlow System automates the reporting process by transforming fragmented program data from KPC Inuka's four pillars into trusted insights and ready-to-use reports, reducing manual reporting effort by at least 50%.

---

## 4. System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (Angular 17)                  │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐  │
│  │Dashboard │ │Programs  │ │Reports  │ │ AI Assistant │  │
│  │  Page    │ │Performance│ │Builder  │ │    Page      │  │
│  └────┬─────┘ └────┬─────┘ └────┬────┘ └──────┬───────┘  │
│       └─────────────┴────────────┴─────────────┘          │
│                         │ HTTP REST API                   │
└─────────────────────────┼────────────────────────────────┘
                          │
┌─────────────────────────┼────────────────────────────────┐
│                    BACKEND (FastAPI)                       │
│  ┌────────────┐ ┌──────────────┐ ┌───────────────────┐   │
│  │ Auth (JWT) │ │ 21 API Routes│ │  7 KPI Functions  │   │
│  │  6 Users   │ │  9 Modules   │ │  7 Engine Methods │   │
│  └─────┬──────┘ └──────┬───────┘ └────────┬──────────┘   │
│        └───────────────┴──────────────────┘               │
│                         │                                 │
│  ┌──────────────────────┴───────────────────────────┐     │
│  │              SQLAlchemy ORM (SQLite)              │     │
│  │     73,533 total records across 9 tables         │     │
│  └──────────────────────────────────────────────────┘     │
│                         │                                 │
│  ┌──────────────────────┴───────────────────────────┐     │
│  │           ETL Pipeline (Python/Pandas)            │     │
│  │  Generate → Validate → Transform → Load           │     │
│  └──────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Angular 17 | Single-page application with 13 pages |
| UI Design | Custom CSS with deep navy theme | Enterprise-grade responsive interface |
| Backend | Python FastAPI | REST API with automatic OpenAPI docs |
| Database | SQLite | Relational database with 9 tables |
| ORM | SQLAlchemy | Database abstraction and query building |
| Data Processing | Python Pandas + NumPy | ETL pipeline, validation, transformation |
| Synthetic Data | Faker | Generates realistic Kenyan NGO data |
| Authentication | JWT + bcrypt | Secure token-based authentication with role-based access |
| AI | Template-based (extensible to OpenAI) | Verified metric responses and natural language insights |

---

## 5. Data Pipeline & ETL

### Pipeline Overview

The system runs a three-stage pipeline that can be triggered with a single command:

```bash
python -m src.run_pipeline --all
```

### Stage 1: Data Generation (`--generate`)

Generates synthetic but realistic data modelling KPC Inuka Foundation's operations:

| Dataset | Records | Description |
|---------|---------|-------------|
| Beneficiaries | 10,000 | Individual program participants across 15 Kenyan counties |
| Program Enrollments | 11,379 | Enrolment records across 4 programs and 7 quarters |
| Attendance | 28,255 | Session attendance tracking per beneficiary |
| Outcomes | 4,167 | Post-program outcomes (employment, education, entrepreneurship) |
| Data Quality Issues | 19,729 | Intentional quality issues for validation demonstration |

**Design choices:**
- Intentional data quality issues embedded (inconsistent county names, gender values, status labels) to demonstrate the validation engine
- Data distributed across 7 quarterly periods (Q1 2025 – Q3 2026) with realistic growth trends
- All beneficiary IDs use Kenyan-style identifiers (e.g., `BEN-XXXXXX`)
- Programs map to 15 real Kenyan counties

### Stage 2: ETL — Validate & Transform (`--etl`)

**Validation** (`validator.py`):
- Detects missing required fields (beneficiary_id, name, program)
- Identifies invalid status values and standardises them
- Flags duplicate beneficiary IDs
- Detects out-of-range numeric values (attendance rates > 100%, negative ages)
- Detects inconsistent county/sub-county name formats
- Produces 19,729 data quality issues for transparency

**Transformation** (`transformer.py`):
- Standardises status values (e.g., "ACTIVE", "Active", "active" → "active")
- Merges four program datasets into a unified enrolment table
- Normalises column names to snake_case
- Coerces date columns to proper datetime format
- Computes missing attendance rates from session counts

### Stage 3: Load (`--load`)

Loads transformed data into the SQLite database with:
- Deduplication of beneficiary records
- Proper foreign key relationships between tables
- Reporting period mapping across 7 quarters

---

## 6. Key Features & Pages

The platform provides 13 interactive pages:

### Core Analytics

| Page | Route | Description |
|------|-------|-------------|
| **Dashboard** | `/` | Executive overview with KPI cards, trend charts, program breakdown, recent activity |
| **Program Performance** | `/program-performance` | Per-program metrics with bar charts and detailed tables; filterable by period and program |
| **Beneficiary Analytics** | `/beneficiary-analytics` | Demographics: age, gender, county, education level distributions |
| **Outcomes** | `/outcomes` | Employment, education, and entrepreneurship outcomes by program and county |

### Data Management

| Page | Route | Description |
|------|-------|-------------|
| **Data Sources** | `/data-sources` | View and manage raw data sources (4 CSV uploads) |
| **Data Quality** | `/data-quality` | Quality issues dashboard with severity breakdowns and filtering |
| **Data Pipeline** | `/data-pipeline` | Pipeline status, ETL controls, data freshness indicators |

### Reporting

| Page | Route | Description |
|------|-------|-------------|
| **Reports** | `/reports` | List all generated reports with status, download as Excel/CSV |
| **Report Builder** | `/report-builder` | 4-step wizard: select period → sections → AI insights → generate |

### AI-Powered

| Page | Route | Description |
|------|-------|-------------|
| **AI Assistant** | `/ai-assistant` | Natural language chat with verified KPI answers; "Add to Report" integration |
| **AI Insights** | `/ai-insights` | Auto-generated AI insights on trends, outliers, and recommendations |

### Administration

| Page | Route | Description |
|------|-------|-------------|
| **Admin** | `/admin` | User management, role permissions grid, system settings, audit logs |
| **Login** | `/login` | Secure authentication with JWT tokens |

---

## 7. AI Integration

### How the AI Works

The AI layer operates in two modes:

**Mode 1: Verified Metrics (Default)**
When no external AI API key is configured, the system uses a template-based engine that:
- Matches user questions against a library of predefined patterns
- Pulls verified, real-time data from the database
- Returns accurate answers with actual numbers

Example:
```
User: "What is the scholarship completion rate?"
AI:   "Scholarship completion rate is 35.2%. This represents 1,260
       completions out of 3,575 enrolled beneficiaries."
```

**Mode 2: OpenAI Enhanced (Optional)**
When an OpenAI API key is provided in the `.env` file, the system can:
- Generate natural language summaries of KPI data
- Provide contextual analysis of metric changes
- Suggest actionable recommendations

### AI Features

1. **AI Chat** — Ask questions in natural language; get verified answers from the database
2. **Quick Questions** — Pre-built prompts for common queries (top programs, dropout trends, etc.)
3. **AI Insights** — Auto-generated analysis covering key trends, performance changes, and recommendations
4. **Add to Report** — Send AI insights directly into the report builder

### AI Response Structure

Every AI response includes:
- **Answer**: The direct response with verified metrics
- **Data used**: The metrics and data points the answer is based on
- **Recommendation**: An actionable suggestion based on the finding

---

## 8. Automated Reporting

### Report Types

| Report Type | Sections Available |
|-------------|-------------------|
| Executive Summary | Overview, key metrics, program highlights |
| Program Performance | Per-program metrics, completion rates, attendance |
| Data Quality | Issues summary, severity breakdown, trends |
| Outcomes | Employment, education, entrepreneurship results |
| Beneficiary Analytics | Demographics, distributions, trends |
| AI Insights Report | AI-generated analysis and recommendations |
| Custom | User-selected sections |

### Report Builder (4-Step Wizard)

1. **Select Period** — Choose a quarterly reporting period
2. **Choose Sections** — Pick which report sections to include
3. **AI Insights** — Optionally include AI-generated analysis
4. **Generate** — Create the report in Excel or CSV format

### Report Features

- Auto-generated reports for all 7 quarters (Q1 2025 – Q3 2026)
- Download as Excel (.xlsx) or CSV
- Section-based generation with optional AI insights
- Report status tracking (completed, pending, failed)
- API-driven with `/api/reports/{id}/download` endpoint

---

## 9. User Roles & Access Control

### Role Definitions

| Role | Access Level | Pages |
|------|-------------|-------|
| **Program Administrator** | Full access | All 13 pages |
| **Program Manager** | Program-focused | Dashboard, Programs, Beneficiaries, Outcomes, Reports, Report Builder, AI Assistant, AI Insights |
| **M&E Officer** | Data-focused | Dashboard, Programs, Beneficiaries, Outcomes, Data Quality, Data Pipeline, AI Assistant, AI Insights |
| **Reporting Officer** | Report-focused | Dashboard, Reports, Report Builder, Data Sources, Data Quality, Data Pipeline, AI Assistant, AI Insights, Outcomes |
| **Leadership** | View-focused | Dashboard, Programs, Beneficiaries, Outcomes, Reports, AI Assistant, AI Insights |

### User Accounts

| User | Email | Role | Status |
|------|-------|------|--------|
| Admin | admin@inukafoundation.org | Program Administrator | Active |
| Grace Wanjiku | grace.w@inukafoundation.org | Program Manager | Active |
| James Otieno | james.o@inukafoundation.org | M&E Officer | Active |
| Amina Hassan | amina.h@inukafoundation.org | Reporting Officer | Active |
| David Mwangi | david.m@inukafoundation.org | Leadership | Active |
| Sarah Njeri | sarah.n@inukafoundation.org | Program Manager | Inactive (blocked) |

### Security Implementation

- **Authentication**: JWT tokens with 24-hour expiry
- **Password Hashing**: bcrypt with salt
- **Route Protection**: Angular AuthGuard on all authenticated routes
- **API Protection**: Bearer token interceptor on all HTTP requests
- **RBAC Enforcement**: Backend validates permissions; frontend filters sidebar navigation by role

---

## 10. Technical Implementation

### Frontend (Angular 17)

- **13 page components** with TypeScript, HTML, and CSS
- **Services**: ApiService (data), AuthService (auth), route guards, HTTP interceptors
- **Responsive design**: CSS Grid layouts with mobile breakpoints
- **Design system**: Deep navy primary (#0f172a), modern blue (#1565c0), purple accent (#6366f1) for AI features only
- **Material icons**: Google Material Icons Outlined for consistent iconography
- **Build size**: ~494KB initial bundle (gzipped ~122KB)

### Backend (FastAPI)

- **21 REST API endpoints** across 9 route modules
- **SQLAlchemy ORM** with 8 database models
- **Automatic API docs** at `/docs` (Swagger UI) and `/redoc`
- **CORS enabled** for frontend development
- **Synchronous report generation** to avoid SQLite session issues

### Data Volume

| Table | Records |
|-------|---------|
| `beneficiaries` | 10,000 |
| `program_enrollments` | 11,379 |
| `attendance` | 28,255 |
| `outcomes` | 4,167 |
| `data_quality_issues` | 19,729 |
| `programs` | 4 |
| `reporting_periods` | 7 |
| `reports` | 4 (auto-generated) |
| **Total** | **73,539** |

---

## 11. Database Schema

### Entity Relationship

```
┌──────────────┐     ┌─────────────────────┐     ┌──────────────┐
│   programs   │     │ program_enrollments  │     │beneficiaries │
│──────────────│     │─────────────────────│     │──────────────│
│ id (PK)      │◄────│ program_id (FK)     │     │ id (PK)      │
│ name         │     │ beneficiary_id (FK) │────►│ beneficiary_ │
│ description  │     │ status              │     │   id         │
│              │     │ reporting_period_id │     │ name         │
└──────────────┘     │ participation_rate  │     │ county       │
                     └─────────────────────┘     │ gender       │
                                                   │ age          │
┌──────────────────┐                              └──────────────┘
│ reporting_periods │
│──────────────────│     ┌──────────────┐     ┌──────────────┐
│ id (PK)          │     │  attendance  │     │   outcomes   │
│ name             │     │──────────────│     │──────────────│
│ year             │     │ beneficiary_ │     │ beneficiary_ │
│ quarter          │     │   id (FK)    │     │   id (FK)    │
│ start_date       │     │ program_id   │     │ program_id   │
│ end_date         │     │ sessions_    │     │ outcome_type │
│ is_current       │     │   attended   │     │ outcome_     │
└──────────────────┘     │ attendance_  │     │   status     │
                         │   rate       │     └──────────────┘
┌──────────────────┐     └──────────────┘
│    reports       │
│──────────────────│     ┌───────────────────┐
│ id (PK)          │     │data_quality_issues │
│ title            │     │───────────────────│
│ report_type      │     │ source_file       │
│ reporting_period │     │ field_name        │
│   _id (FK)       │     │ issue_type        │
│ status           │     │ severity          │
│ ai_insights      │     │ original_value    │
└──────────────────┘     │ corrected_value   │
                         └───────────────────┘
```

---

## 12. API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Authenticate user, return JWT token |
| GET | `/api/auth/me` | Get current user profile |
| GET | `/api/auth/users` | List all users with roles |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/summary` | Executive KPI summary |
| GET | `/api/dashboard/trends` | Quarter-over-quarter trends |

### Programs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/programs` | List all programs |
| GET | `/api/programs/performance` | Program metrics (optional `?period=`) |

### Beneficiaries
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/beneficiaries` | Paginated beneficiary list (optional `?search=`) |
| GET | `/api/beneficiaries/analytics` | Demographic distributions |

### Outcomes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/outcomes` | Outcome records (optional `?program=`) |

### Periods
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/periods` | List reporting periods |
| GET | `/api/periods/current` | Get current period |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports` | List all reports |
| POST | `/api/reports/generate` | Generate a new report |
| GET | `/api/reports/{id}` | Get report details |
| GET | `/api/reports/{id}/download` | Download report (Excel/CSV) |

### Data Quality
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/data-quality` | Data quality issues (optional `?severity=`) |
| GET | `/api/data-sources` | List data sources |
| GET | `/api/pipeline/status` | Pipeline status |
| POST | `/api/pipeline/sync` | Trigger pipeline sync |

### AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chat` | Natural language query |
| GET | `/api/ai/insights` | Auto-generated insights |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/settings` | Get system settings |
| PUT | `/api/admin/settings` | Update system settings |

---

## 13. Data Quality Management

### Validation Engine

The system runs automatic validation on every data import:

| Check Type | Description | Example |
|-----------|-------------|---------|
| Missing required fields | Detects blank beneficiary_id, name, or program | Empty programme column |
| Invalid status values | Flags non-standard status labels | "Dropped", "Left" → standardised to "dropped_out" |
| Duplicate detection | Identifies duplicate beneficiary IDs | Same ID appearing twice |
| Out-of-range values | Flags impossible numeric values | Attendance rate > 100%, negative age |
| Format inconsistencies | Detects variations in county/sub-county names | "Nairobi", "nairobi", "Nairobi County" |

### Quality Metrics

- **19,729 data quality issues** detected across all datasets
- Issues categorised by severity: `critical`, `high`, `medium`, `low`
- Each issue records original value and corrected value for full audit trail
- Dashboard shows quality score and issue trends over time

---

## 14. Impact & Metrics

### Quantified Impact

| Metric | Before (Manual) | After (InsightFlow) | Improvement |
|--------|-----------------|---------------------|-------------|
| Report compilation time | 2-3 days per report | < 1 minute (automated) | **> 90% reduction** |
| Data validation time | Manual spot-checks | Automated validation on import | **100% automated** |
| KPI calculation | Manual Excel formulas | Real-time from database | **Instant** |
| Cross-program analysis | Multiple spreadsheets | Unified dashboard | **Single source of truth** |
| Management insight access | Wait for report delivery | Real-time dashboard | **Immediate** |
| AI-assisted analysis | Not available | Natural language queries | **New capability** |

### Data Coverage

- **10,000** beneficiaries across **15 Kenyan counties**
- **4 programs**: Scholarship, Plus, Vocational, Tech
- **7 quarterly periods**: Q1 2025 through Q3 2026
- **28,255** attendance records tracking session participation
- **4,167** outcome records tracking post-program results

### Reporting Frequency Supported

| Report Type | Frequency | Automation Level |
|-------------|-----------|-----------------|
| Dashboard KPIs | Real-time | Fully automated |
| Weekly summaries | Weekly | One-click generation |
| Monthly program reports | Monthly | Template + AI |
| Quarterly board reports | Quarterly | Full report builder |
| Annual performance review | Annual | Aggregated from quarters |

---

## 15. How to Run

### Prerequisites

- Python 3.14+
- Node.js 24+ and npm 12+
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Step 2: Generate Data & Load Database

```bash
cd backend
python -m src.run_pipeline --all
```

This runs the full pipeline:
1. Generates 10,000 synthetic beneficiaries and related data
2. Validates and transforms all datasets
3. Loads everything into the SQLite database

### Step 3: Start Backend Server

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

API documentation available at: `http://localhost:8000/docs`

### Step 4: Start Frontend Server

```bash
cd frontend
npx ng serve
```

### Step 5: Open Application

Navigate to `http://localhost:4200` and log in.

### Login Credentials

| User | Email | Password |
|------|-------|----------|
| Admin | admin@inukafoundation.org | Admin@123 |
| Grace Wanjiku | grace.w@inukafoundation.org | Admin@123 |
| James Otieno | james.o@inukafoundation.org | Admin@123 |
| Amina Hassan | amina.h@inukafoundation.org | Admin@123 |
| David Mwangi | david.m@inukafoundation.org | Admin@123 |

---

## 16. Project Structure

```
HACKATHON2/
├── backend/
│   ├── requirements.txt
│   └── src/
│       ├── main.py                    # FastAPI application entry point
│       ├── config.py                  # Configuration (SQLite database URL)
│       ├── database.py                # SQLAlchemy engine & session
│       ├── run_pipeline.py            # Full pipeline runner
│       ├── models/
│       │   └── models.py             # SQLAlchemy ORM models (8 models)
│       ├── api/
│       │   ├── dashboard.py           # Dashboard KPI endpoints
│       │   ├── programs.py            # Program performance endpoints
│       │   ├── beneficiaries.py       # Beneficiary analytics endpoints
│       │   ├── outcomes.py            # Outcomes endpoints
│       │   ├── periods.py             # Reporting period endpoints
│       │   ├── reports.py             # Report CRUD & generation
│       │   ├── data_quality.py        # Data quality & pipeline endpoints
│       │   ├── ai_routes.py           # AI chat & insights endpoints
│       │   └── admin.py              # Admin settings endpoints
│       ├── auth/
│       │   ├── service.py            # JWT, bcrypt, 6 users, RBAC
│       │   └── routes.py             # Login, profile, user list
│       ├── analytics/
│       │   └── kpi_engine.py         # 7 KPI computation functions
│       ├── ai/
│       │   └── service.py            # AI service (template + OpenAI)
│       ├── reporting/
│       │   └── generator.py          # Report data & Excel/CSV export
│       ├── data_generation/
│       │   └── generate_all.py       # Synthetic data generation
│       ├── ingestion/
│       │   └── loader.py             # CSV → SQLite loader
│       ├── validation/
│       │   └── validator.py          # Data quality validation engine
│       └── transformation/
│           └── transformer.py        # ETL transform & standardise
├── frontend/
│   ├── package.json
│   ├── angular.json
│   └── src/
│       └── app/
│           ├── app.module.ts
│           ├── app-routing.module.ts  # 13 routes with auth guards
│           ├── services/
│           │   ├── api.service.ts     # HTTP client for all endpoints
│           │   └── auth.service.ts    # Authentication & permissions
│           ├── guards/
│           │   └── auth.guard.ts      # Route protection
│           ├── interceptors/
│           │   └── auth.interceptor.ts # JWT token injection
│           └── pages/
│               ├── login/             # Login page
│               ├── dashboard/         # Executive dashboard
│               ├── program-performance/ # Program metrics
│               ├── beneficiary-analytics/ # Demographics
│               ├── outcomes/          # Post-program outcomes
│               ├── reports/           # Report list & download
│               ├── report-builder/    # 4-step report wizard
│               ├── data-sources/      # Data source management
│               ├── data-quality/      # Quality issues dashboard
│               ├── data-pipeline/     # Pipeline status & controls
│               ├── ai-assistant/      # AI chat interface
│               ├── ai-insights/       # AI-generated insights
│               └── admin/             # User & settings management
├── data/
│   ├── raw/                           # Source CSV files
│   │   ├── scholarship.csv
│   │   ├── plus.csv
│   │   ├── vocational.csv
│   │   ├── tech.csv
│   │   ├── beneficiaries.csv
│   │   ├── attendance.csv
│   │   └── outcomes.csv
│   └── insightflow.db                # SQLite database
├── .env                               # Environment configuration
├── docker-compose.yml                 # Docker orchestration
├── Dockerfile.backend                  # Backend container
├── Dockerfile.frontend                 # Frontend container
└── README.md                          # Project readme
```

---

## Summary

InsightFlow System transforms KPC Inuka Foundation's manual, fragmented reporting process into an automated, AI-enhanced platform. By unifying data from four program pillars, validating it automatically, computing KPIs in real-time, and generating reports at the click of a button, the system eliminates the manual consolidation bottleneck that has historically delayed management insights and increased the risk of errors.

**Fragmented data becomes trusted insight. Manual reporting becomes automated intelligence. Delayed decisions become real-time action.**

---

*InsightFlow System — Hackathon 2, Stage 2 Submission*
*KPC Inuka Foundation*
