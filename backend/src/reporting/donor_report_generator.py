"""Automated Donor Report Generator: Compiles 6-section reports using RAG + LLM."""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.models import (
    DonorReport, Report, KPIMetric, FinancialLineItem,
    OperationalRisk, FieldNote, Project, ReportingPeriod, Program
)
from src.auth.rbac import log_audit_event
from src.config import GROQ_API_KEY, GROQ_MODEL, AI_API_KEY, AI_MODEL, AI_BASE_URL

logger = logging.getLogger(__name__)


REPORT_SECTIONS = [
    {
        "id": "executive_summary",
        "title": "Executive Summary",
        "description": "AI narrative synthesis of all sections",
        "order": 1,
    },
    {
        "id": "programmatic_progress",
        "title": "Programmatic Progress",
        "description": "Auto-generated KPI metrics & comparison charts",
        "order": 2,
    },
    {
        "id": "financial_utilization",
        "title": "Financial Utilization",
        "description": "Aggregated ledger tables with burn rates",
        "order": 3,
    },
    {
        "id": "operational_challenges",
        "title": "Operational Challenges",
        "description": "Flagged issues & AI-refined mitigation steps",
        "order": 4,
    },
    {
        "id": "impact_narratives",
        "title": "Impact Narratives",
        "description": "RAG-assisted generation translating raw field notes into polished stories",
        "order": 5,
    },
    {
        "id": "next_quarter_outlook",
        "title": "Next Quarter Outlook",
        "description": "Timeline & upcoming milestone mapping",
        "order": 6,
    },
]


class DonorReportGenerator:
    """Generates structured 6-section donor reports using RAG pipeline."""

    def __init__(self, db: Session):
        self.db = db
        self._llm_provider = None
        self._llm_api_key = None
        self._llm_model = None
        self._llm_base_url = None
        self._init_llm()

    def _init_llm(self):
        if GROQ_API_KEY:
            self._llm_provider = "groq"
            self._llm_api_key = GROQ_API_KEY
            self._llm_model = GROQ_MODEL
            self._llm_base_url = "https://api.groq.com/openai/v1"
            logger.info(f"LLM initialized with Groq: {GROQ_MODEL}")
        elif AI_API_KEY:
            self._llm_provider = "openai"
            self._llm_api_key = AI_API_KEY
            self._llm_model = AI_MODEL
            self._llm_base_url = AI_BASE_URL
            logger.info(f"LLM initialized with OpenAI: {AI_MODEL}")
        else:
            self._llm_provider = "template"
            self._llm_api_key = ""
            self._llm_model = ""
            self._llm_base_url = ""
            logger.info("LLM initialized with template fallback (no API key)")

    def _call_llm(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        """Call LLM and return (content, provider)."""
        if self._llm_provider == "template":
            return self._template_fallback(system_prompt, user_prompt), "template"

        headers = {
            "Authorization": f"Bearer {self._llm_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        try:
            response = httpx.post(
                f"{self._llm_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return content, self._llm_provider
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            fallback = self._template_fallback(system_prompt, user_prompt)
            return f"[LLM Error: {str(e)}] Using template fallback.\n\n{fallback}", "template"

    def get_sections(self) -> list[dict]:
        return REPORT_SECTIONS

    def gather_section_data(self, section_id: str, reporting_period_id: Optional[int] = None) -> dict:
        period_filter = True
        if reporting_period_id:
            period_filter = KPIMetric.reporting_period_id == reporting_period_id

        if section_id == "executive_summary":
            return self._gather_executive_data(reporting_period_id)
        elif section_id == "programmatic_progress":
            return self._gather_programmatic_data(reporting_period_id)
        elif section_id == "financial_utilization":
            return self._gather_financial_data(reporting_period_id)
        elif section_id == "operational_challenges":
            return self._gather_risk_data(reporting_period_id)
        elif section_id == "impact_narratives":
            return self._gather_impact_data(reporting_period_id)
        elif section_id == "next_quarter_outlook":
            return self._gather_outlook_data(reporting_period_id)
        return {}

    def _gather_executive_data(self, period_id: Optional[int] = None) -> dict:
        total_kpis = self.db.query(func.count(KPIMetric.id)).scalar() or 0
        avg_attainment = self.db.query(func.avg(KPIMetric.attainment_pct)).scalar() or 0
        total_budget = self.db.query(func.sum(FinancialLineItem.budget_amount)).scalar() or 0
        total_spend = self.db.query(func.sum(FinancialLineItem.actual_spend)).scalar() or 0
        open_risks = self.db.query(func.count(OperationalRisk.id)).filter(OperationalRisk.status == "open").scalar() or 0
        total_notes = self.db.query(func.count(FieldNote.id)).scalar() or 0
        programs = self.db.query(Program).all()

        return {
            "total_kpis": total_kpis,
            "avg_attainment": round(float(avg_attainment), 1),
            "total_budget": float(total_budget),
            "total_spend": float(total_spend),
            "burn_rate": round((float(total_spend) / float(total_budget) * 100), 1) if total_budget > 0 else 0,
            "open_risks": open_risks,
            "total_notes": total_notes,
            "programs": [{"name": p.name, "description": p.description} for p in programs],
        }

    def _gather_programmatic_data(self, period_id: Optional[int] = None) -> dict:
        q = self.db.query(KPIMetric)
        if period_id:
            q = q.filter(KPIMetric.reporting_period_id == period_id)
        metrics = q.all()

        by_category = {}
        for m in metrics:
            cat = m.kpi_category or "Uncategorized"
            if cat not in by_category:
                by_category[cat] = {"targets": 0, "actuals": 0, "count": 0, "avg_attainment": 0}
            by_category[cat]["targets"] += m.target_value
            by_category[cat]["actuals"] += m.actual_value
            by_category[cat]["count"] += 1

        for cat in by_category:
            if by_category[cat]["targets"] > 0:
                by_category[cat]["avg_attainment"] = round(
                    (by_category[cat]["actuals"] / by_category[cat]["targets"]) * 100, 1
                )

        return {
            "total_metrics": len(metrics),
            "by_category": by_category,
            "metrics": [
                {
                    "name": m.kpi_name, "category": m.kpi_category,
                    "target": m.target_value, "actual": m.actual_value,
                    "attainment": m.attainment_pct,
                }
                for m in metrics[:20]
            ],
        }

    def _gather_financial_data(self, period_id: Optional[int] = None) -> dict:
        q = self.db.query(FinancialLineItem)
        if period_id:
            q = q.filter(FinancialLineItem.reporting_period_id == period_id)
        items = q.all()

        by_category = {}
        for item in items:
            cat = item.category or "Uncategorized"
            if cat not in by_category:
                by_category[cat] = {"budget": 0, "spend": 0, "items": 0}
            by_category[cat]["budget"] += item.budget_amount
            by_category[cat]["spend"] += item.actual_spend
            by_category[cat]["items"] += 1

        for cat in by_category:
            budget = by_category[cat]["budget"]
            by_category[cat]["burn_rate"] = round(
                (by_category[cat]["spend"] / budget * 100), 1
            ) if budget > 0 else 0
            by_category[cat]["variance"] = round(budget - by_category[cat]["spend"], 2)

        total_budget = sum(i.budget_amount for i in items)
        total_spend = sum(i.actual_spend for i in items)

        return {
            "total_items": len(items),
            "total_budget": float(total_budget),
            "total_spend": float(total_spend),
            "overall_burn_rate": round((float(total_spend) / float(total_budget) * 100), 1) if total_budget > 0 else 0,
            "by_category": by_category,
            "items": [
                {
                    "line_item": i.line_item, "category": i.category,
                    "budget": i.budget_amount, "spend": i.actual_spend,
                    "burn_rate": i.burn_rate, "variance": i.variance,
                }
                for i in items[:20]
            ],
        }

    def _gather_risk_data(self, period_id: Optional[int] = None) -> dict:
        q = self.db.query(OperationalRisk)
        if period_id:
            q = q.filter(OperationalRisk.reporting_period_id == period_id)
        risks = q.all()

        by_severity = {}
        for r in risks:
            sev = r.severity or "unknown"
            by_severity[sev] = by_severity.get(sev, 0) + 1

        return {
            "total_risks": len(risks),
            "open_risks": len([r for r in risks if r.status == "open"]),
            "mitigated_risks": len([r for r in risks if r.status == "mitigated"]),
            "by_severity": by_severity,
            "risks": [
                {
                    "title": r.risk_title, "category": r.risk_category,
                    "severity": r.severity, "status": r.status,
                    "mitigation": r.mitigation_strategy,
                }
                for r in risks[:15]
            ],
        }

    def _gather_impact_data(self, period_id: Optional[int] = None) -> dict:
        q = self.db.query(FieldNote)
        if period_id:
            q = q.filter(FieldNote.reporting_period_id == period_id)
        notes = q.all()

        quotes = [n.beneficiary_quote for n in notes if n.beneficiary_quote]

        return {
            "total_notes": len(notes),
            "beneficiary_quotes": quotes[:10],
            "notes": [
                {
                    "title": n.title, "content": n.content[:500],
                    "quote": n.beneficiary_quote, "location": n.location,
                    "type": n.note_type,
                }
                for n in notes[:10]
            ],
        }

    def _gather_outlook_data(self, period_id: Optional[int] = None) -> dict:
        upcoming = self.db.query(ReportingPeriod).filter(
            ReportingPeriod.is_current == False
        ).order_by(ReportingPeriod.start_date.desc()).limit(2).all()

        current = self.db.query(ReportingPeriod).filter(ReportingPeriod.is_current == True).first()

        return {
            "current_period": {"name": current.name, "year": current.year, "quarter": current.quarter} if current else None,
            "upcoming_periods": [{"name": p.name, "year": p.year, "quarter": p.quarter} for p in upcoming],
            "programs": [p.name for p in self.db.query(Program).all()],
        }

    def generate_section(
        self,
        report_id: int,
        section_id: str,
        user_id: int,
    ) -> dict:
        report = self.db.query(DonorReport).filter(DonorReport.id == report_id).first()
        if not report:
            raise ValueError("Report not found")

        section_data = self.gather_section_data(section_id, report.reporting_period_id)

        section_prompts = {
            "executive_summary": {
                "system": "You are a professional NGO report writer. Generate an Executive Summary for a donor report. Write in a formal, professional tone. Use the provided data to synthesize a comprehensive overview of organizational performance.",
                "user": f"Based on the following organizational data, write an Executive Summary:\n\n{json.dumps(section_data, indent=2, default=str)}",
            },
            "programmatic_progress": {
                "system": "You are a professional NGO report writer. Generate the Programmatic Progress section with KPI metrics analysis, targets vs actuals, and performance insights.",
                "user": f"Based on the following program data and KPIs, write the Programmatic Progress section:\n\n{json.dumps(section_data, indent=2, default=str)}",
            },
            "financial_utilization": {
                "system": "You are a professional NGO report writer. Generate the Financial Utilization section with budget analysis, burn rates, and spending patterns.",
                "user": f"Based on the following financial data, write the Financial Utilization section:\n\n{json.dumps(section_data, indent=2, default=str)}",
            },
            "operational_challenges": {
                "system": "You are a professional NGO report writer. Generate the Operational Challenges section identifying risks, issues, and mitigation strategies.",
                "user": f"Based on the following risk and challenge data, write the Operational Challenges section:\n\n{json.dumps(section_data, indent=2, default=str)}",
            },
            "impact_narratives": {
                "system": "You are a professional NGO report writer. Generate Impact Narratives by transforming raw field notes and beneficiary quotes into polished, compelling stories that demonstrate program impact.",
                "user": f"Based on the following field notes, beneficiary quotes, and impact data, write compelling Impact Narratives:\n\n{json.dumps(section_data, indent=2, default=str)}",
            },
            "next_quarter_outlook": {
                "system": "You are a professional NGO report writer. Generate the Next Quarter Outlook section with upcoming milestones, timelines, and strategic priorities.",
                "user": f"Based on the following plans and forward-looking data, write the Next Quarter Outlook:\n\n{json.dumps(section_data, indent=2, default=str)}",
            },
        }

        prompt_config = section_prompts.get(section_id, {
            "system": "You are a professional NGO report writer. Generate the requested report section.",
            "user": f"Write the {section_id.replace('_', ' ').title()} section based on:\n\n{json.dumps(section_data, indent=2, default=str)}",
        })

        content, provider = self._call_llm(prompt_config["system"], prompt_config["user"])

        if not report.ai_generated_content:
            report.ai_generated_content = {}
        report.ai_generated_content[section_id] = {
            "content": content,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data_summary": section_data,
            "provider": provider,
        }
        self.db.commit()

        log_audit_event(
            self.db, user_id, f"generate_section_{section_id}",
            "donor_report", report_id,
            {"section": section_id, "data_keys": list(section_data.keys()), "provider": provider},
        )

        return {"section": section_id, "content": content, "provider": provider, "data_used": section_data}

    def generate_all_sections(self, report_id: int, user_id: int) -> dict:
        results = {}
        for section in REPORT_SECTIONS:
            result = self.generate_section(report_id, section["id"], user_id)
            results[section["id"]] = result
        return {
            "report_id": report_id,
            "sections_generated": len(results),
            "sections": results,
        }

    def _template_fallback(self, section_id: str, data: dict) -> str:
        if section_id == "executive_summary":
            return (
                f"Executive Summary\n\n"
                f"This reporting period, the organization managed {data.get('total_kpis', 0)} KPI indicators "
                f"with an average attainment of {data.get('avg_attainment', 0)}%. "
                f"Total budget utilization stood at {data.get('burn_rate', 0)}% with "
                f"${data.get('total_spend', 0):,.2f} spent against a ${data.get('total_budget', 0):,.2f} budget. "
                f"{data.get('open_risks', 0)} operational risks remain open and under active management."
            )
        elif section_id == "programmatic_progress":
            by_cat = data.get("by_category", {})
            lines = "\n".join(
                f"- {cat}: {info.get('count', 0)} indicators, avg attainment {info.get('avg_attainment', 0)}%"
                for cat, info in by_cat.items()
            )
            return (
                f"Programmatic Progress\n\n"
                f"A total of {data.get('total_metrics', 0)} KPI metrics were tracked this period.\n{lines}"
            )
        elif section_id == "financial_utilization":
            return (
                f"Financial Utilization\n\n"
                f"Total budget: ${data.get('total_budget', 0):,.2f}\n"
                f"Total spend: ${data.get('total_spend', 0):,.2f}\n"
                f"Overall burn rate: {data.get('overall_burn_rate', 0)}%"
            )
        elif section_id == "operational_challenges":
            return (
                f"Operational Challenges\n\n"
                f"Total risks identified: {data.get('total_risks', 0)}\n"
                f"Open: {data.get('open_risks', 0)} | Mitigated: {data.get('mitigated_risks', 0)}"
            )
        elif section_id == "impact_narratives":
            quotes = "\n".join(f'"{q}"' for q in data.get("beneficiary_quotes", [])[:5])
            return (
                f"Impact Narratives\n\n"
                f"{data.get('total_notes', 0)} field notes collected this period.\n{quotes}"
            )
        elif section_id == "next_quarter_outlook":
            current = data.get("current_period") or {}
            return (
                f"Next Quarter Outlook\n\n"
                f"Current period: {current.get('name', 'N/A')}\n"
                f"Active programs: {', '.join(data.get('programs', []))}"
            )
        return f"Report section: {section_id}"
