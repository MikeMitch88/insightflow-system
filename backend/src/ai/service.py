import os
import json
from sqlalchemy.orm import Session
from ..analytics import kpi_engine
from ..config import AI_API_KEY, AI_MODEL, AI_BASE_URL


async def chat_with_ai(message: str, context_page: str | None, db: Session) -> dict:
    """Chat with AI using verified backend metrics."""
    verified_data = _gather_verified_metrics(context_page, db)
    prompt = _build_prompt(message, verified_data)

    if AI_API_KEY:
        response = await _call_llm(prompt)
    else:
        response = _generate_template_response(message, verified_data)

    return response


async def generate_insights(db: Session, period_id: int | None = None) -> list[dict]:
    """Generate automated insights by comparing verified data across periods."""
    summary = kpi_engine.get_dashboard_summary(db, period_id)
    trends = kpi_engine.get_trends(db)
    programs = kpi_engine.get_program_performance(db, period_id)
    outcomes = kpi_engine.get_outcomes_summary(db, period_id)
    quality = kpi_engine.get_data_quality_summary(db)

    insights = []

    if programs:
        comp_rates = {p["program_name"]: p.get("completion_rate", 0) for p in programs}
        if comp_rates:
            lowest = min(comp_rates, key=comp_rates.get)
            highest = max(comp_rates, key=comp_rates.get)
            diff = comp_rates[highest] - comp_rates[lowest]
            if diff > 10:
                insights.append({
                    "title": f"{lowest} has the lowest completion rate at {comp_rates[lowest]:.1f}%",
                    "severity": "high",
                    "evidence": f"{lowest}: {comp_rates[lowest]:.1f}%, {highest}: {comp_rates[highest]:.1f}%",
                    "explanation": f"{lowest} is {diff:.0f} percentage points behind {highest}, indicating a significant performance gap.",
                    "recommended_action": f"Review attendance and dropout patterns in {lowest}. Investigate barriers to completion.",
                    "category": "program_performance"
                })

    if trends and len(trends) >= 2:
        latest = trends[-1]
        previous = trends[-2]
        if previous.get("beneficiary_count", 0) > 0:
            growth = ((latest.get("beneficiary_count", 0) - previous.get("beneficiary_count", 0))
                      / previous.get("beneficiary_count", 1)) * 100
            if growth > 15:
                insights.append({
                    "title": f"Strong enrollment growth of {growth:.1f}% quarter-over-quarter",
                    "severity": "info",
                    "evidence": f"Previous: {previous.get('beneficiary_count', 0)}, Current: {latest.get('beneficiary_count', 0)}",
                    "explanation": "Enrollment is growing significantly, indicating effective outreach.",
                    "recommended_action": "Ensure capacity and resources scale with growth. Monitor quality metrics.",
                    "category": "growth"
                })
            elif growth < -10:
                insights.append({
                    "title": f"Enrollment declined by {abs(growth):.1f}% quarter-over-quarter",
                    "severity": "warning",
                    "evidence": f"Previous: {previous.get('beneficiary_count', 0)}, Current: {latest.get('beneficiary_count', 0)}",
                    "explanation": "Declining enrollment may indicate outreach or retention challenges.",
                    "recommended_action": "Investigate root causes. Review recruitment strategies and community engagement.",
                    "category": "growth"
                })

        prev_att = previous.get("attendance_rate", 0)
        curr_att = latest.get("attendance_rate", 0)
        if prev_att > 0:
            att_change = curr_att - prev_att
            if att_change < -5:
                insights.append({
                    "title": f"Attendance rate dropped by {abs(att_change):.1f} percentage points",
                    "severity": "warning",
                    "evidence": f"Previous: {prev_att:.1f}%, Current: {curr_att:.1f}%",
                    "explanation": "Declining attendance may signal engagement issues or scheduling conflicts.",
                    "recommended_action": "Survey participants for feedback. Review session scheduling and accessibility.",
                    "category": "attendance"
                })

    if quality:
        score = quality.get("score", 100)
        if score < 80:
            insights.append({
                "title": f"Data quality score is below threshold at {score:.0f}/100",
                "severity": "high",
                "evidence": f"Total issues: {quality.get('total_issues', 0)}, Missing: {quality.get('missing_values', 0)}, Duplicates: {quality.get('duplicates', 0)}",
                "explanation": "Low data quality undermines reporting accuracy and decision-making.",
                "recommended_action": "Run data cleansing pipeline. Assign data stewards per program.",
                "category": "data_quality"
            })

    if programs:
        for p in programs:
            att = p.get("avg_attendance_rate", 0)
            if att > 0 and att < 60:
                insights.append({
                    "title": f"{p['program_name']} average attendance is critically low at {att:.1f}%",
                    "severity": "high",
                    "evidence": f"Attendance rate: {att:.1f}% across {p['total_enrolled']} enrolled beneficiaries",
                    "explanation": "Consistently low attendance strongly predicts dropouts and poor outcomes.",
                    "recommended_action": f"Investigate barriers in {p['program_name']}. Consider schedule changes, transportation support, or engagement initiatives.",
                    "category": "attendance"
                })

    if outcomes:
        er = outcomes.get("employment_rate", 0)
        if er < 40:
            insights.append({
                "title": f"Employment/outcome rate is only {er:.1f}%",
                "severity": "warning",
                "evidence": f"Employment rate: {er:.1f}% across all programs",
                "explanation": "Low employment outcomes suggest potential gaps in training relevance or market alignment.",
                "recommended_action": "Review curriculum alignment with market needs. Strengthen employer partnerships and internship programs.",
                "category": "outcomes"
            })

    if not insights:
        insights.append({
            "title": "All metrics within expected ranges",
            "severity": "info",
            "evidence": f"Completion: {summary.get('completion_rate', 0):.1f}%, Attendance: {summary.get('attendance_rate', 0):.1f}%",
            "explanation": "No significant anomalies detected in current period metrics.",
            "recommended_action": "Continue monitoring. Review weekly for emerging trends.",
            "category": "general"
        })

    return insights


def _gather_verified_metrics(context_page: str | None, db: Session) -> dict:
    """Gather verified metrics from the database based on context."""
    data = {}
    summary = kpi_engine.get_dashboard_summary(db)
    data["dashboard_summary"] = summary

    programs = kpi_engine.get_program_performance(db)
    data["program_performance"] = programs

    trends = kpi_engine.get_trends(db)
    data["trends"] = trends

    outcomes = kpi_engine.get_outcomes_summary(db)
    data["outcomes"] = outcomes

    quality = kpi_engine.get_data_quality_summary(db)
    data["data_quality"] = quality

    if context_page:
        data["context_page"] = context_page

    return data


def _build_prompt(message: str, verified_data: dict) -> str:
    """Build a prompt with verified data context."""
    summary = verified_data.get("dashboard_summary", {})
    programs = verified_data.get("program_performance", [])

    programs_text = "\n".join(
        f"- {p.get('program_name', 'Unknown')}: "
        f"Enrolled={p.get('total_enrolled', 0)}, "
        f"Completed={p.get('completed', 0)}, "
        f"Completion Rate={p.get('completion_rate', 0):.1f}%, "
        f"Attendance={p.get('avg_attendance_rate', 0):.1f}%"
        for p in programs
    )

    return f"""You are InsightFlow System, the intelligence layer for KPC Inuka Foundation's program management platform.

VERIFIED ORGANIZATIONAL METRICS (from database):
- Total Beneficiaries: {summary.get('total_beneficiaries', 0)}
- Active Beneficiaries: {summary.get('active_beneficiaries', 0)}
- Overall Completion Rate: {summary.get('completion_rate', 0):.1f}%
- Attendance Rate: {summary.get('attendance_rate', 0):.1f}%
- Dropout Rate: {summary.get('dropout_rate', 0):.1f}%
- Outcome Rate: {summary.get('outcome_rate', 0):.1f}%
- Counties Reached: {summary.get('counties_reached', 0)}
- Data Quality Score: {summary.get('data_quality_score', 0):.0f}/100

PROGRAM PERFORMANCE:
{programs_text}

QUESTION: {message}

Respond using ONLY the verified data above. Do not invent statistics.
Structure your response as:
1. Direct Answer
2. Relevant KPI
3. Supporting Data
4. Recommendation"""


def _generate_template_response(message: str, verified_data: dict) -> dict:
    """Generate a structured response using verified data when no LLM is available."""
    summary = verified_data.get("dashboard_summary", {})
    programs = verified_data.get("program_performance", [])

    message_lower = message.lower()

    if "attention" in message_lower or "lowest" in message_lower or "worst" in message_lower:
        if programs:
            lowest = min(programs, key=lambda p: p.get("completion_rate", 100))
            answer = (f"{lowest['program_name']} currently has the lowest completion rate at "
                      f"{lowest.get('completion_rate', 0):.1f}%. "
                      f"It has {lowest.get('total_enrolled', 0)} enrolled beneficiaries with "
                      f"{lowest.get('dropped_out', 0)} dropouts.")
            kpis = {"completion_rate": lowest.get("completion_rate", 0),
                    "program_name": lowest["program_name"]}
            recommendation = (f"Review attendance and dropout patterns in {lowest['program_name']}. "
                              "Investigate barriers to completion and consider targeted interventions.")
        else:
            answer = "No program data available."
            kpis = {}
            recommendation = "Ensure program data is loaded."

    elif "summary" in message_lower or "summarize" in message_lower or "overview" in message_lower:
        answer = (f"The KPC Inuka Foundation currently serves {summary.get('total_beneficiaries', 0)} "
                  f"beneficiaries across {summary.get('program_count', 0)} programs in "
                  f"{summary.get('counties_reached', 0)} counties. "
                  f"The overall completion rate is {summary.get('completion_rate', 0):.1f}% "
                  f"with an attendance rate of {summary.get('attendance_rate', 0):.1f}%.")
        kpis = {k: summary.get(k, 0) for k in ["total_beneficiaries", "completion_rate", "attendance_rate"]}
        recommendation = "Focus on maintaining strong attendance rates and addressing dropout patterns."

    elif "compare" in message_lower or "vs" in message_lower or "versus" in message_lower:
        if len(programs) >= 2:
            sorted_p = sorted(programs, key=lambda p: p.get("completion_rate", 0), reverse=True)
            best = sorted_p[0]
            worst = sorted_p[-1]
            answer = (f"Comparing programs: {best['program_name']} leads with a {best.get('completion_rate', 0):.1f}% "
                      f"completion rate, while {worst['program_name']} trails at {worst.get('completion_rate', 0):.1f}%. "
                      f"The gap is {best.get('completion_rate', 0) - worst.get('completion_rate', 0):.1f} percentage points.")
            kpis = {best["program_name"]: best.get("completion_rate", 0),
                    worst["program_name"]: worst.get("completion_rate", 0)}
            recommendation = f"Investigate what drives {best['program_name']}'s success and apply lessons to {worst['program_name']}."
        else:
            answer = "Insufficient program data for comparison."
            kpis = {}
            recommendation = "Ensure at least two programs have data."

    elif "growth" in message_lower or "trend" in message_lower:
        trends = verified_data.get("trends", [])
        if len(trends) >= 2:
            first = trends[0]
            last = trends[-1]
            growth = ((last.get("beneficiary_count", 0) - first.get("beneficiary_count", 0))
                      / max(first.get("beneficiary_count", 1), 1)) * 100
            answer = (f"Beneficiary count has changed by {growth:.1f}% from {first.get('period', 'N/A')} "
                      f"({first.get('beneficiary_count', 0)}) to {last.get('period', 'N/A')} "
                      f"({last.get('beneficiary_count', 0)}).")
            kpis = {"growth_pct": growth}
            recommendation = "Continue monitoring enrollment trends and adjust outreach strategies."
        else:
            answer = "Insufficient trend data. Need at least two reporting periods."
            kpis = {}
            recommendation = "Collect data for multiple periods."

    elif "county" in message_lower or "region" in message_lower or "geographic" in message_lower:
        analytics = kpi_engine.get_beneficiary_analytics(verified_data.get("_db"))
        counties = analytics.get("county_distribution", []) if analytics else []
        if counties:
            top_counties = counties[:5]
            counties_text = ", ".join(f"{c['county']} ({c['count']})" for c in top_counties)
            answer = f"Top counties by beneficiary count: {counties_text}."
            kpis = {c["county"]: c["count"] for c in top_counties}
            recommendation = "Ensure equitable coverage across all target counties."
        else:
            answer = "Geographic distribution data is being computed."
            kpis = {}
            recommendation = "Run beneficiary analytics."

    elif "recommend" in message_lower or "action" in message_lower:
        if programs:
            low_attendance = [p for p in programs if p.get("avg_attendance_rate", 100) < 70]
            low_completion = [p for p in programs if p.get("completion_rate", 100) < 75]
            actions = []
            if low_completion:
                names = ", ".join(p["program_name"] for p in low_completion)
                actions.append(f"Address completion rates in {names}")
            if low_attendance:
                names = ", ".join(p["program_name"] for p in low_attendance)
                actions.append(f"Improve attendance engagement in {names}")
            if not actions:
                actions.append("Maintain current performance across all programs")
            answer = "Recommended priorities: " + "; ".join(actions) + "."
            kpis = {}
            recommendation = "Prioritize interventions based on severity and impact potential."
        else:
            answer = "No program data available for recommendations."
            kpis = {}
            recommendation = "Load program data first."

    else:
        answer = (f"Based on verified data: {summary.get('total_beneficiaries', 0)} beneficiaries "
                  f"across {summary.get('program_count', 0)} programs with a "
                  f"{summary.get('completion_rate', 0):.1f}% completion rate. "
                  f"Ask me about specific programs, counties, trends, or comparisons.")
        kpis = {k: summary.get(k, 0) for k in ["total_beneficiaries", "completion_rate", "attendance_rate"]}
        recommendation = "Ask specific questions about programs, trends, or performance."

    return {
        "answer": answer,
        "relevant_kpis": kpis,
        "supporting_data": {k: v for k, v in summary.items() if isinstance(v, (int, float, str))},
        "recommendation": recommendation
    }


async def _call_llm(prompt: str) -> dict:
    """Call an OpenAI-compatible LLM API."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{AI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {AI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are InsightFlow System, an expert program intelligence assistant for KPC Inuka Foundation. Use only verified data provided in the context."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {
                    "answer": content,
                    "relevant_kpis": {},
                    "supporting_data": {},
                    "recommendation": "AI-generated insight based on verified organizational data."
                }
    except Exception:
        pass

    return {
        "answer": "AI service temporarily unavailable. Showing template-based analysis.",
        "relevant_kpis": {},
        "supporting_data": {},
        "recommendation": "Configure AI_API_KEY environment variable for AI-powered insights."
    }


import httpx
