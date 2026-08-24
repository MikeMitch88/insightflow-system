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


def generate_insights(db: Session, period_id: int | None = None) -> list[dict]:
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
                    "type": "warning",
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
                    "type": "trend",
                    "title": f"Strong enrollment growth of {growth:.1f}% quarter-over-quarter",
                    "severity": "info",
                    "evidence": f"Previous: {previous.get('beneficiary_count', 0)}, Current: {latest.get('beneficiary_count', 0)}",
                    "explanation": "Enrollment is growing significantly, indicating effective outreach.",
                    "recommended_action": "Ensure capacity and resources scale with growth. Monitor quality metrics.",
                    "category": "growth"
                })
            elif growth < -10:
                insights.append({
                    "type": "warning",
                    "title": f"Enrollment declined by {abs(growth):.1f}% quarter-over-quarter",
                    "severity": "warning",
                    "evidence": f"Previous: {previous.get('beneficiary_count', 0)}, Current: {latest.get('beneficiary_count', 0)}",
                    "explanation": "Declining enrollment may indicate outreach or retention challenges.",
                    "recommended_action": "Investigate root causes. Review recruitment strategies and community engagement.",
                    "category": "growth"
                })

        if len(trends) >= 2 and not any(i.get("type") == "trend" for i in insights):
            first = trends[0]
            latest = trends[-1]
            insights.append({
                "type": "trend",
                "title": "Enrollment trend is being monitored",
                "severity": "info",
                "evidence": f"{first.get('period', 'Earlier period')}: {first.get('beneficiary_count', 0)} beneficiaries; {latest.get('period', 'Latest period')}: {latest.get('beneficiary_count', 0)}.",
                "explanation": "The system compares reporting periods to identify meaningful changes in reach and engagement.",
                "recommended_action": "Review this trend alongside attendance and completion before changing outreach plans.",
                "category": "trend",
                "impact": "Monitor",
            })

        prev_att = previous.get("attendance_rate", 0)
        curr_att = latest.get("attendance_rate", 0)
        if prev_att > 0:
            att_change = curr_att - prev_att
            if att_change < -5:
                insights.append({
                    "type": "warning",
                    "title": f"Attendance rate dropped by {abs(att_change):.1f} percentage points",
                    "severity": "warning",
                    "evidence": f"Previous: {prev_att:.1f}%, Current: {curr_att:.1f}%",
                    "explanation": "Declining attendance may signal engagement issues or scheduling conflicts.",
                    "recommended_action": "Survey participants for feedback. Review session scheduling and accessibility.",
                    "category": "attendance"
                })

    if quality:
        score = quality.get("score", 100)
        if score < 85 or quality.get("total_issues", 0) > 0:
            insights.append({
                "type": "data_quality",
                "title": f"Data quality score is below threshold at {score:.0f}/100",
                "severity": "high",
                "evidence": f"Total issues: {quality.get('total_issues', 0)}, Missing: {quality.get('missing_values', 0)}, Duplicates: {quality.get('duplicates', 0)}",
                "explanation": "Low data quality undermines reporting accuracy and decision-making.",
                "recommended_action": "Run data cleansing pipeline. Assign data stewards per program.",
                "category": "data_quality"
            })

    if programs:
        lowest = min(programs, key=lambda p: p.get("completion_rate", 100))
        actual = lowest.get("completion_rate", 0)
        target = 75
        gap = actual - target
        insights.append({
            "type": "kpi",
            "title": f"{lowest['program_name']} completion is below the monitoring target",
            "severity": "high" if gap < -10 else "warning" if gap < 0 else "info",
            "evidence": f"Actual: {actual:.1f}%; monitoring target: {target:.1f}%; gap: {gap:+.1f} percentage points.",
            "explanation": "The target is the platform's management monitoring threshold, not an externally supplied programme target.",
            "recommended_action": f"Review attendance, dropout records, and support coverage in {lowest['program_name']}.",
            "category": "kpi_performance",
            "program": lowest["program_name"],
            "impact": "Requires attention" if gap < 0 else "On track",
        })

    if programs:
        for p in programs:
            att = p.get("avg_attendance_rate", 0)
            if att > 0 and att < 60:
                insights.append({
                    "type": "warning",
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
            "type": "warning",
                "title": f"Employment/outcome rate is only {er:.1f}%",
                "severity": "warning",
                "evidence": f"Employment rate: {er:.1f}% across all programs",
                "explanation": "Low employment outcomes suggest potential gaps in training relevance or market alignment.",
                "recommended_action": "Review curriculum alignment with market needs. Strengthen employer partnerships and internship programs.",
                "category": "outcomes"
            })

    if summary.get("dropout_rate", 0) > 0 or programs:
        highest_dropout = max(programs, key=lambda p: p.get("dropped_out", 0)) if programs else None
        focus = f" in {highest_dropout['program_name']}" if highest_dropout else ""
        insights.append({
            "type": "recommendation",
            "title": "Prioritize retention follow-up",
            "severity": "warning" if summary.get("dropout_rate", 0) >= 10 else "info",
            "evidence": f"Current dropout rate: {summary.get('dropout_rate', 0):.1f}%; attendance rate: {summary.get('attendance_rate', 0):.1f}%.",
            "explanation": "Attendance and dropout records identify where follow-up should start, but they do not prove why a participant leaves.",
            "recommended_action": f"Create a weekly early-warning list and assign follow-up owners{focus}. Record the reason and outcome of each intervention.",
            "category": "recommendation",
            "impact": "Reduce avoidable dropout and improve the evidence available for future decisions.",
        })

    if not insights:
        insights.append({
            "type": "trend",
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
    data["_db"] = db

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

    return f"""You are InsightFlow, the intelligence layer for KPC Inuka Foundation's program management platform.

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
    quality = verified_data.get("data_quality", {})

    message_lower = message.lower()

    if any(word in message_lower for word in ["data quality", "missing", "duplicate", "invalid", "clean"]):
        score = quality.get("score", summary.get("data_quality_score", 0))
        issue_count = quality.get("total_issues", 0)
        answer = (
            f"The current data quality score is {score:.1f}/100 with {issue_count} recorded issues. "
            "Before using the data for official reporting, review missing IDs, duplicate records, "
            "invalid values, and inconsistent locations. Uncertain matches should be flagged for "
            "human review rather than changed automatically."
        )
        kpis = {
            "data_quality_score": score,
            "total_issues": issue_count,
            "missing_values": quality.get("missing_values", 0),
            "duplicates": quality.get("duplicates", 0),
        }
        recommendation = (
            "Assign a data steward to resolve high-severity issues, rerun validation after each "
            "correction, and approve the cleaned dataset before report generation."
        )

    elif any(word in message_lower for word in ["predict", "at risk", "risk of", "likely to"]):
        risk_programs = [
            p for p in programs
            if p.get("avg_attendance_rate", 100) < 70 or p.get("completion_rate", 100) < 75
        ]
        if risk_programs:
            names = ", ".join(p["program_name"] for p in risk_programs)
            answer = (
                f"A predictive model is not configured, but the current rule-based screen flags "
                f"{names} for closer review because attendance or completion is below the monitoring "
                "threshold. This is an early-warning signal, not a prediction of an individual outcome."
            )
            kpis = {p["program_name"]: {
                "attendance_rate": p.get("avg_attendance_rate", 0),
                "completion_rate": p.get("completion_rate", 0),
            } for p in risk_programs}
        else:
            answer = "No program currently crosses the early-warning thresholds for attendance or completion."
            kpis = {}
        recommendation = (
            "Build a historical risk model only after collecting consistent attendance, enrollment, "
            "and outcome records. Until then, review low-attendance participants with staff and do not "
            "label individuals as certain dropouts."
        )

    elif any(word in message_lower for word in ["why", "cause", "driver", "reason"]):
        lowest = min(programs, key=lambda p: p.get("completion_rate", 100)) if programs else None
        if lowest:
            answer = (
                f"The data shows {lowest['program_name']} has the lowest completion rate at "
                f"{lowest.get('completion_rate', 0):.1f}% and an average attendance rate of "
                f"{lowest.get('avg_attendance_rate', 0):.1f}%. These are associated indicators, "
                "not proof of the underlying cause. The available dataset does not establish why "
                "participants leave; interviews and follow-up records are needed."
            )
            kpis = {"program_name": lowest["program_name"], "completion_rate": lowest.get("completion_rate", 0), "attendance_rate": lowest.get("avg_attendance_rate", 0)}
        else:
            answer = "The available data is insufficient to identify a likely driver."
            kpis = {}
        recommendation = "Collect structured dropout reasons, participant feedback, and follow-up outcomes by program and county."

    elif "dropout" in message_lower or "drop out" in message_lower:
        priority_programs = sorted(
            programs,
            key=lambda p: p.get("dropped_out", 0),
            reverse=True,
        )
        program_focus = ""
        if priority_programs:
            focus = priority_programs[0]
            program_focus = (
                f" Prioritize {focus['program_name']}, which has "
                f"{focus.get('dropped_out', 0)} recorded dropouts and an "
                f"average attendance rate of {focus.get('avg_attendance_rate', 0):.1f}%."
            )
        answer = (
            f"The current dropout rate is {summary.get('dropout_rate', 0):.1f}%. "
            "To reduce dropout, identify participants with falling attendance early, "
            "contact them quickly to understand barriers, and provide targeted support "
            "such as schedule changes, transport assistance, mentoring, or catch-up sessions."
            + program_focus
        )
        kpis = {
            "dropout_rate": summary.get("dropout_rate", 0),
            "attendance_rate": summary.get("attendance_rate", 0),
            "completion_rate": summary.get("completion_rate", 0),
        }
        recommendation = (
            "Create a weekly early-warning list from attendance records, assign a staff "
            "owner to follow up with each at-risk participant, and review dropout reasons "
            "by program and county every reporting period."
        )

    elif "attention" in message_lower or "lowest" in message_lower or "worst" in message_lower:
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

    elif "dropout" in message_lower or "drop out" in message_lower:
        answer = (f"The overall dropout rate across all programs is {summary.get('dropout_rate', 0):.1f}%. "
                  f"Out of the total {summary.get('total_beneficiaries', 0)} beneficiaries, "
                  f"about {int(summary.get('total_beneficiaries', 0) * summary.get('dropout_rate', 0) / 100)} did not complete their programs.")
        kpis = {"dropout_rate": summary.get("dropout_rate", 0)}
        recommendation = ("Establish an early warning system to identify beneficiaries with declining attendance "
                          "(below 75%) and implement targeted support protocols.")

    elif "quality" in message_lower or "score" in message_lower:
        answer = (f"The current Data Quality Score is {summary.get('data_quality_score', 0):.0f}/100. "
                  f"This score reflects the integrity, completeness, and consistency of the tracked beneficiary and program data.")
        kpis = {"data_quality_score": summary.get("data_quality_score", 0)}
        recommendation = ("Run the automated data cleansing pipeline to resolve missing records and duplicates. "
                          "Assign a dedicated data steward to monitor program logs.")

    elif any(kw in message_lower for kw in ["recommend", "reommend", "action", "recom"]):
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
                        {"role": "system", "content": "You are InsightFlow, an expert program intelligence assistant for KPC Inuka Foundation. Use only verified data provided in the context."},
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
