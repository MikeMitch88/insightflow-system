import json
import csv
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.models import Report, ReportRun, ReportingPeriod
from ..analytics import kpi_engine
from ..config import DATA_PROCESSED_DIR


def generate_report_data(db: Session, report_id: int) -> dict:
    """Generate complete report data from verified database metrics."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise ValueError(f"Report {report_id} not found")

    config = json.loads(report.config_json) if report.config_json else {}
    sections = config.get("sections", ["executive_summary", "program_performance", "beneficiary_reach", "outcomes", "geographic_distribution"])
    period_id = report.reporting_period_id

    report_data = {
        "title": report.title,
        "report_type": report.report_type,
        "generated_at": datetime.utcnow().isoformat(),
        "sections": {}
    }

    summary = kpi_engine.get_dashboard_summary(db, period_id)
    report_data["dashboard_summary"] = summary

    if "executive_summary" in sections:
        report_data["sections"]["executive_summary"] = {
            "title": "Executive Summary",
            "total_beneficiaries": summary.get("total_beneficiaries", 0),
            "active_beneficiaries": summary.get("active_beneficiaries", 0),
            "completion_rate": summary.get("completion_rate", 0),
            "attendance_rate": summary.get("attendance_rate", 0),
            "dropout_rate": summary.get("dropout_rate", 0),
            "outcome_rate": summary.get("outcome_rate", 0),
            "counties_reached": summary.get("counties_reached", 0),
            "data_quality_score": summary.get("data_quality_score", 0),
        }

    if "program_performance" in sections:
        programs = kpi_engine.get_program_performance(db, period_id)
        report_data["sections"]["program_performance"] = {
            "title": "Program Performance",
            "programs": programs
        }

    if "beneficiary_reach" in sections:
        analytics = kpi_engine.get_beneficiary_analytics(db)
        report_data["sections"]["beneficiary_reach"] = {
            "title": "Beneficiary Reach",
            "age_distribution": analytics.get("age_distribution", []),
            "gender_distribution": analytics.get("gender_distribution", []),
            "county_distribution": analytics.get("county_distribution", [])
        }

    if "outcomes" in sections:
        outcomes = kpi_engine.get_outcomes_summary(db, period_id)
        report_data["sections"]["outcomes"] = {
            "title": "Outcomes & Impact",
            "summary": outcomes
        }

    if "geographic_distribution" in sections:
        analytics = kpi_engine.get_beneficiary_analytics(db)
        report_data["sections"]["geographic_distribution"] = {
            "title": "Geographic Distribution",
            "counties": analytics.get("county_distribution", [])
        }

    if "key_challenges" in sections:
        quality = kpi_engine.get_data_quality_summary(db)
        report_data["sections"]["key_challenges"] = {
            "title": "Key Challenges",
            "data_quality_score": quality.get("score", 100),
            "total_issues": quality.get("total_issues", 0),
            "top_issues": quality.get("issues", [])[:10]
        }

    if "recommendations" in sections:
        report_data["sections"]["recommendations"] = {
            "title": "Recommendations",
            "items": _generate_recommendations(summary, db, period_id)
        }

    return report_data


def export_to_csv(report_data: dict, output_dir: Path = None) -> Path:
    """Export report data to CSV file."""
    if output_dir is None:
        output_dir = DATA_PROCESSED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = output_dir / filename

    rows = []
    for section_key, section_data in report_data.get("sections", {}).items():
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                if key == "title":
                    continue
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            row = {"section": section_data.get("title", section_key), **item}
                            rows.append(row)
                        else:
                            rows.append({"section": section_data.get("title", section_key), "value": item})
                elif isinstance(value, dict):
                    for k, v in value.items():
                        rows.append({"section": section_data.get("title", section_key), "metric": k, "value": v})
                else:
                    rows.append({"section": section_data.get("title", section_key), "metric": key, "value": value})

    if not rows:
        rows.append({"section": "Summary", "metric": "Report Type", "value": report_data.get("report_type", "")})

    df = __import__("pandas").DataFrame(rows)
    df.to_csv(filepath, index=False)
    return filepath


def export_to_excel(report_data: dict, output_dir: Path = None) -> Path:
    """Export report data to Excel file with multiple sheets."""
    if output_dir is None:
        output_dir = DATA_PROCESSED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = output_dir / filename

    import pandas as pd
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        summary = report_data.get("dashboard_summary", {})
        if summary:
            pd.DataFrame([summary]).to_excel(writer, sheet_name="Summary", index=False)

        for section_key, section_data in report_data.get("sections", {}).items():
            if isinstance(section_data, dict):
                sheet_name = section_data.get("title", section_key)[:31]
                data_rows = []
                for key, value in section_data.items():
                    if key == "title":
                        continue
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                data_rows.append(item)
                    elif isinstance(value, dict):
                        data_rows.append(value)
                    else:
                        data_rows.append({"metric": key, "value": value})
                if data_rows:
                    pd.DataFrame(data_rows).to_excel(writer, sheet_name=sheet_name, index=False)

    return filepath


def _generate_recommendations(summary: dict, db: Session, period_id: int) -> list[str]:
    """Generate data-driven recommendations."""
    recommendations = []

    programs = kpi_engine.get_program_performance(db, period_id)
    for p in programs:
        if p.get("completion_rate", 100) < 75:
            recommendations.append(
                f"Review completion barriers in {p['program_name']} "
                f"(completion rate: {p.get('completion_rate', 0):.1f}%). "
                f"Consider targeted support for at-risk beneficiaries."
            )
        if p.get("avg_attendance_rate", 100) < 65:
            recommendations.append(
                f"Increase engagement in {p['program_name']} "
                f"(attendance: {p.get('avg_attendance_rate', 0):.1f}%). "
                f"Review scheduling and session accessibility."
            )

    if summary.get("data_quality_score", 100) < 85:
        recommendations.append(
            f"Improve data quality (score: {summary.get('data_quality_score', 0):.0f}/100). "
            f"Assign data stewards and run automated validation."
        )

    if summary.get("dropout_rate", 0) > 15:
        recommendations.append(
            f"Address high dropout rate ({summary.get('dropout_rate', 0):.1f}%). "
            f"Implement early warning system and intervention protocols."
        )

    if not recommendations:
        recommendations.append("Continue current trajectory. Monitor key metrics weekly.")

    return recommendations
