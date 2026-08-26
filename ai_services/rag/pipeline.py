"""RAG Pipeline: Combines FAISS retrieval with LLM generation for report sections."""

import json
from typing import Optional

from ai_services.rag.vector_store import FAISSVectorStore


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for automated report generation."""

    def __init__(self):
        self.vector_store = FAISSVectorStore()
        self.llm_client = None
        self._init_llm()

    def _init_llm(self):
        from src.config import AI_API_KEY, AI_BASE_URL, AI_MODEL, GROQ_API_KEY, GROQ_MODEL

        if GROQ_API_KEY:
            self.llm_provider = "groq"
            self.llm_api_key = GROQ_API_KEY
            self.llm_model = GROQ_MODEL
            self.llm_base_url = "https://api.groq.com/openai/v1"
        elif AI_API_KEY:
            self.llm_provider = "openai"
            self.llm_api_key = AI_API_KEY
            self.llm_model = AI_MODEL
            self.llm_base_url = AI_BASE_URL
        else:
            self.llm_provider = "template"
            self.llm_api_key = ""
            self.llm_model = ""
            self.llm_base_url = ""

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if self.llm_provider == "template":
            return self._template_generation(system_prompt, user_prompt)

        import httpx

        headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        try:
            response = httpx.post(
                f"{self.llm_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[LLM Error: {str(e)}] Falling back to template generation.\n\n" + self._template_generation(system_prompt, user_prompt)

    def _template_generation(self, system_prompt: str, user_prompt: str) -> str:
        if "Executive Summary" in system_prompt or "executive_summary" in user_prompt.lower():
            return (
                "This reporting period demonstrated significant progress across all programmatic pillars. "
                "Key achievements include improved beneficiary enrollment, strengthened M&E data quality, "
                "and enhanced financial discipline with controlled burn rates. "
                "The organization maintained its commitment to accountability and transparency throughout the period."
            )
        elif "Programmatic" in system_prompt or "programmatic" in user_prompt.lower():
            return (
                "Program performance metrics indicate steady progress toward quarterly targets. "
                "Enrollment numbers have grown across all active programs, with completion rates "
                "maintaining above organizational benchmarks. Attendance tracking shows consistent "
                "engagement from beneficiaries, with room for improvement in specific geographic areas."
            )
        elif "Financial" in system_prompt or "financial" in user_prompt.lower():
            return (
                "Financial utilization for the period shows responsible stewardship of donor funds. "
                "The overall burn rate remains within acceptable parameters, with minor variances "
                "in administrative overhead that are being addressed. Budget allocations align with "
                "strategic program priorities."
            )
        elif "Challenge" in system_prompt or "challenge" in user_prompt.lower():
            return (
                "Operational challenges encountered during the period include supply chain delays, "
                "seasonal accessibility issues in remote project areas, and capacity constraints "
                "in rapid reporting cycles. Mitigation strategies have been implemented with "
                "favorable early results."
            )
        elif "Impact" in system_prompt or "impact" in user_prompt.lower():
            return (
                "Beneficiary testimonials reflect meaningful transformation in target communities. "
                "Stories of economic empowerment, educational advancement, and social cohesion "
                "demonstrate the tangible impact of program interventions on individual lives "
                "and community well-being."
            )
        elif "Outlook" in user_prompt.lower():
            return (
                "The next quarter will focus on scaling successful pilot interventions, "
                "strengthening data collection mechanisms, and deepening stakeholder engagement. "
                "Key milestones include mid-term review completion, beneficiary satisfaction surveys, "
                "and preparation for annual reporting requirements."
            )
        return "Report section content will be generated based on retrieved context and program data."

    def generate_report_section(self, section: str, project_id: Optional[int] = None, context_data: Optional[dict] = None) -> dict:
        context = self.vector_store.get_context_for_report(section, project_id=project_id)

        section_prompts = {
            "executive_summary": {
                "system": "You are a professional NGO report writer. Generate an Executive Summary for a donor report. Write in a formal, professional tone. Use the provided context to synthesize a comprehensive overview.",
                "user": f"Based on the following organizational data and context, write an Executive Summary:\n\n{context}\n\nAdditional context: {json.dumps(context_data or {}, indent=2)}",
            },
            "programmatic_progress": {
                "system": "You are a professional NGO report writer. Generate the Programmatic Progress section with KPI metrics, targets vs actuals, and program performance analysis.",
                "user": f"Based on the following program data and KPIs, write the Programmatic Progress section:\n\n{context}\n\nAdditional context: {json.dumps(context_data or {}, indent=2)}",
            },
            "financial_utilization": {
                "system": "You are a professional NGO report writer. Generate the Financial Utilization section with budget analysis, burn rates, and spending patterns.",
                "user": f"Based on the following financial data, write the Financial Utilization section:\n\n{context}\n\nAdditional context: {json.dumps(context_data or {}, indent=2)}",
            },
            "operational_challenges": {
                "system": "You are a professional NGO report writer. Generate the Operational Challenges section identifying risks, issues, and mitigation strategies.",
                "user": f"Based on the following risk and challenge data, write the Operational Challenges section:\n\n{context}\n\nAdditional context: {json.dumps(context_data or {}, indent=2)}",
            },
            "impact_narratives": {
                "system": "You are a professional NGO report writer. Generate Impact Narratives by transforming raw field notes and beneficiary quotes into polished, compelling stories that demonstrate program impact.",
                "user": f"Based on the following field notes, beneficiary quotes, and impact data, write compelling Impact Narratives:\n\n{context}\n\nAdditional context: {json.dumps(context_data or {}, indent=2)}",
            },
            "next_quarter_outlook": {
                "system": "You are a professional NGO report writer. Generate the Next Quarter Outlook section with upcoming milestones, timelines, and strategic priorities.",
                "user": f"Based on the following plans and forward-looking data, write the Next Quarter Outlook section:\n\n{context}\n\nAdditional context: {json.dumps(context_data or {}, indent=2)}",
            },
        }

        prompt_config = section_prompts.get(section, {
            "system": "You are a professional NGO report writer. Generate the requested report section.",
            "user": f"Write the {section} section based on:\n\n{context}",
        })

        generated_content = self._call_llm(prompt_config["system"], prompt_config["user"])

        return {
            "section": section,
            "content": generated_content,
            "sources_used": len(self.vector_store.search(section, k=5)),
            "provider": self.llm_provider,
        }

    def ingest_all_project_data(self, db_session) -> dict:
        from src.models.models import FieldNote, KPIMetric, FinancialLineItem, OperationalRisk

        stats = {"field_notes": 0, "kpi_metrics": 0, "financial_items": 0, "risks": 0}

        notes = db_session.query(FieldNote).all()
        if notes:
            notes_data = [
                {
                    "id": n.id, "title": n.title, "content": n.content,
                    "beneficiary_quote": n.beneficiary_quote, "project_id": n.project_id,
                    "note_type": n.note_type, "location": n.location, "date_observed": n.date_observed,
                }
                for n in notes
            ]
            stats["field_notes"] = self.vector_store.ingest_field_notes(notes_data)

        kpis = db_session.query(KPIMetric).all()
        if kpis:
            kpi_data = [
                {
                    "id": k.id, "kpi_name": k.kpi_name, "kpi_category": k.kpi_category,
                    "target_value": k.target_value, "actual_value": k.actual_value,
                    "attainment_pct": k.attainment_pct, "notes": k.notes, "project_id": k.project_id,
                }
                for k in kpis
            ]
            stats["kpi_metrics"] = self.vector_store.ingest_kpi_metrics(kpi_data)

        financials = db_session.query(FinancialLineItem).all()
        if financials:
            fin_data = [
                {
                    "id": f.id, "line_item": f.line_item, "category": f.category,
                    "budget_amount": f.budget_amount, "actual_spend": f.actual_spend,
                    "burn_rate": f.burn_rate, "variance": f.variance, "currency": f.currency,
                    "notes": f.notes, "project_id": f.project_id,
                }
                for f in financials
            ]
            stats["financial_items"] = self.vector_store.ingest_financial_items(fin_data)

        return stats
