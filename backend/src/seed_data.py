"""Seed data script: Populates 5 departments, 4 tiers, cross-pillar data, and sample workflows."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date, datetime, timezone, timedelta
import random

from src.database import SessionLocal, init_db
from src.auth.service import seed_default_roles, SHARED_HASHED
from src.models.models import (
    Department, Role, User, Project, Program, ReportingPeriod,
    KPIMetric, FinancialLineItem, OperationalRisk, FieldNote,
    DonorReport, ApprovalRecord, AuditLog,
)


def seed_cross_pillar_data(db):
    """Seed projects, KPI metrics, financial items, risks, and field notes across all 5 departments."""

    departments = {d.code: d for d in db.query(Department).all()}
    programs = {p.name: p for p in db.query(Program).all()}
    periods = db.query(ReportingPeriod).all()
    current_period = db.query(ReportingPeriod).filter(ReportingPeriod.is_current == True).first()

    # Create Projects per department
    projects_data = [
        ("Youth Empowerment Scholarship Program", "PROG", "Scholarship"),
        ("Digital Skills Training Initiative", "PROG", "Tech"),
        ("M&E Data Quality Enhancement", "ME", None),
        ("Financial Accountability Framework", "FIN", None),
        ("Staff Capacity Building", "AHR", None),
        ("Strategic Growth & Expansion", "EXEC", None),
        ("Vocational Skills Development", "PROG", "Vocational"),
        ("Community Health Outreach", "PROG", None),
    ]

    projects = {}
    for name, dept_code, prog_name in projects_data:
        dept = departments.get(dept_code)
        prog = programs.get(prog_name) if prog_name else None
        project = Project(
            name=name,
            program_id=prog.id if prog else None,
            department_id=dept.id if dept else None,
            description=f"Strategic initiative under {dept.name if dept else 'Organization'} oversight",
            start_date=date(2025, 1, 1),
            end_date=date(2026, 12, 31),
            status="active",
        )
        db.add(project)
        db.flush()
        projects[name] = project

    # KPI Metrics across all departments
    kpi_data = [
        ("Youth Empowerment Scholarship Program", "Beneficiaries Enrolled", "Enrollment", 500, 478, "youth"),
        ("Youth Empowerment Scholarship Program", "Scholarship Completion Rate", "Completion", 85.0, 82.3, "%"),
        ("Youth Empowerment Scholarship Program", "Employment Placement Rate", "Outcome", 70.0, 65.5, "%"),
        ("Digital Skills Training Initiative", "Training Sessions Conducted", "Delivery", 48, 45, "sessions"),
        ("Digital Skills Training Initiative", "Certification Pass Rate", "Quality", 90.0, 87.2, "%"),
        ("Digital Skills Training Initiative", "Digital Literacy Score", "Quality", 75.0, 71.8, "score"),
        ("M&E Data Quality Enhancement", "Data Quality Score", "Quality", 95.0, 91.5, "%"),
        ("M&E Data Quality Enhancement", "Reporting Timeliness", "Timeliness", 100.0, 94.0, "%"),
        ("M&E Data Quality Enhancement", "Indicator Coverage", "Coverage", 100.0, 98.0, "%"),
        ("Financial Accountability Framework", "Budget Utilization Rate", "Financial", 85.0, 82.7, "%"),
        ("Financial Accountability Framework", "Audit Compliance Score", "Compliance", 100.0, 97.5, "%"),
        ("Financial Accountability Framework", "Donor Fund Utilization", "Financial", 90.0, 88.3, "%"),
        ("Staff Capacity Building", "Training Hours per Staff", "Capacity", 40.0, 37.5, "hours"),
        ("Staff Capacity Building", "Staff Retention Rate", "Retention", 90.0, 92.0, "%"),
        ("Staff Capacity Building", "Performance Appraisal Completion", "HR", 100.0, 95.0, "%"),
        ("Strategic Growth & Expansion", "New Partnership Agreements", "Partnership", 5, 4, "agreements"),
        ("Strategic Growth & Expansion", "Community Reach", "Reach", 10000, 9450, "people"),
        ("Strategic Growth & Expansion", "Sustainability Index", "Strategy", 80.0, 76.5, "%"),
        ("Vocational Skills Development", "Vocational Graduates", "Outcome", 200, 192, "graduates"),
        ("Vocational Skills Development", "Enterprise Launches", "Outcome", 30, 24, "enterprises"),
        ("Community Health Outreach", "Health Screenings", "Health", 800, 765, "screenings"),
        ("Community Health Outreach", "Community Health Workers Trained", "Capacity", 50, 48, "workers"),
    ]

    for proj_name, kpi_name, category, target, actual, unit in kpi_data:
        project = projects.get(proj_name)
        if not project:
            continue
        attainment = round((actual / target * 100), 1) if target > 0 else 0
        metric = KPIMetric(
            project_id=project.id,
            reporting_period_id=current_period.id if current_period else None,
            department_id=project.department_id,
            kpi_name=kpi_name,
            kpi_category=category,
            target_value=float(target),
            actual_value=float(actual),
            unit=unit,
            attainment_pct=attainment,
            verified=random.choice([True, True, False]),
        )
        db.add(metric)

    # Financial Line Items
    financial_data = [
        ("Youth Empowerment Scholarship Program", "Scholarship Tuition Fees", "Program Costs", 75000, 72500, "USD"),
        ("Youth Empowerment Scholarship Program", "Learning Materials", "Program Costs", 15000, 14200, "USD"),
        ("Youth Empowerment Scholarship Program", "Student Stipends", "Program Costs", 30000, 28900, "USD"),
        ("Digital Skills Training Initiative", "Computer Lab Equipment", "Capital", 45000, 43200, "USD"),
        ("Digital Skills Training Initiative", "Instructor Fees", "Program Costs", 25000, 24800, "USD"),
        ("Digital Skills Training Initiative", "Internet & Software", "Operations", 8000, 7650, "USD"),
        ("M&E Data Quality Enhancement", "Data Collection Tools", "Operations", 12000, 11500, "USD"),
        ("M&E Data Quality Enhancement", "Database Maintenance", "IT", 10000, 9800, "USD"),
        ("Financial Accountability Framework", "Audit Services", "Professional", 20000, 19500, "USD"),
        ("Financial Accountability Framework", "Accounting Software", "IT", 5000, 4800, "USD"),
        ("Staff Capacity Building", "Training Workshops", "Capacity", 18000, 17200, "USD"),
        ("Staff Capacity Building", "Conference Attendance", "Professional", 12000, 11500, "USD"),
        ("Strategic Growth & Expansion", "Partnership Development", "Strategy", 25000, 23800, "USD"),
        ("Strategic Growth & Expansion", "Community Mobilization", "Operations", 15000, 14200, "USD"),
        ("Vocational Skills Development", "Workshop Equipment", "Capital", 35000, 33500, "USD"),
        ("Vocational Skills Development", "Raw Materials", "Program Costs", 20000, 19200, "USD"),
        ("Community Health Outreach", "Medical Supplies", "Health", 22000, 21300, "USD"),
        ("Community Health Outreach", "Transport & Logistics", "Operations", 8000, 7800, "USD"),
    ]

    for proj_name, line_item, category, budget, spend, currency in financial_data:
        project = projects.get(proj_name)
        if not project:
            continue
        burn_rate = round((spend / budget * 100), 1) if budget > 0 else 0
        item = FinancialLineItem(
            project_id=project.id,
            reporting_period_id=current_period.id if current_period else None,
            department_id=project.department_id,
            line_item=line_item,
            category=category,
            budget_amount=float(budget),
            actual_spend=float(spend),
            burn_rate=burn_rate,
            variance=float(budget - spend),
            currency=currency,
            verified=random.choice([True, True, False]),
        )
        db.add(item)

    # Operational Risks
    risks_data = [
        ("Youth Empowerment Scholarship Program", "Funding Gap Risk", "Financial", "high", "medium", "high",
         "Diversify funding sources and maintain reserve fund", "open"),
        ("Digital Skills Training Initiative", "Equipment Obsolescence", "Technical", "medium", "low", "medium",
         "Implement technology refresh cycle every 3 years", "mitigated"),
        ("M&E Data Quality Enhancement", "Data Privacy Breach", "Compliance", "critical", "low", "high",
         "Strengthen data encryption and access controls", "open"),
        ("Financial Accountability Framework", "Regulatory Changes", "Compliance", "medium", "medium", "medium",
         "Monitor regulatory environment and update policies quarterly", "open"),
        ("Staff Capacity Building", "Key Staff Turnover", "Human Resources", "high", "medium", "high",
         "Implement retention programs and succession planning", "open"),
        ("Strategic Growth & Expansion", "Market Saturation", "Strategic", "medium", "high", "medium",
         "Explore new geographic areas and program diversification", "open"),
        ("Vocational Skills Development", "Industry Demand Shift", "Market", "medium", "medium", "medium",
         "Regular industry consultation and curriculum updates", "mitigated"),
        ("Community Health Outreach", "Supply Chain Disruption", "Operations", "high", "medium", "high",
         "Establish multiple supplier relationships and buffer stocks", "open"),
        ("Youth Empowerment Scholarship Program", "Seasonal Accessibility", "Logistics", "low", "high", "low",
         "Schedule activities around rainy season and provide transport", "mitigated"),
        ("Digital Skills Training Initiative", "Low Digital Literacy Baseline", "Programmatic", "medium", "high", "medium",
         "Provide pre-training bootcamps and personalized learning paths", "open"),
    ]

    for proj_name, title, category, severity, likelihood, impact, mitigation, status in risks_data:
        project = projects.get(proj_name)
        if not project:
            continue
        risk = OperationalRisk(
            project_id=project.id,
            reporting_period_id=current_period.id if current_period else None,
            department_id=project.department_id,
            risk_title=title,
            risk_category=category,
            severity=severity,
            likelihood=likelihood,
            impact=impact,
            mitigation_strategy=mitigation,
            status=status,
        )
        db.add(risk)

    # Field Notes
    field_notes_data = [
        ("Youth Empowerment Scholarship Program", "Scholarship Impact: Mary's Story",
         "Mary Wanjiku, a 19-year-old from Kibera, was selected for the scholarship program in Q1. "
         "She had dropped out of school due to fees but has since returned and is excelling in her studies. "
         "Her mother reports that Mary's confidence has transformed completely.",
         "Education transforms lives - when barriers are removed, potential flourishes",
         "Kibera, Nairobi", "beneficiary_story", "PROG"),
        ("Digital Skills Training Initiative", "Digital Literacy Breakthrough Session",
         "The cohort of 45 participants completed their final practical assessment. "
         "38 of 45 passed with distinction. The remaining 7 are scheduled for re-examination. "
         "Participants showed remarkable improvement in web development and data analysis skills.",
         "The digital skills I learned have opened doors I never knew existed",
         "Nairobi Tech Hub", "program_update", "PROG"),
        ("M&E Data Quality Enhancement", "Data Quality Audit Findings",
         "The quarterly data quality audit revealed a 15% improvement in data completeness "
         "across all program databases. Key areas of improvement include beneficiary contact "
         "information capture and outcome tracking consistency.",
         None, "Organization-wide", "audit_finding", "ME"),
        ("Vocational Skills Development", "Vocational Graduate Enterprise Launch",
         "Five graduates from the carpentry program have jointly established a workshop in Nakuru. "
         "They have secured contracts worth $15,000 for school furniture. This demonstrates the "
         "program's success in creating sustainable livelihoods.",
         "We learned skills that clients actually need - that's why our business is growing",
         "Nakuru Town", "success_story", "PROG"),
        ("Community Health Outreach", "Health Screening Campaign Results",
         "The quarterly health screening campaign reached 765 community members across 3 counties. "
         "120 cases of hypertension were identified and referred for treatment. "
         "50 community health workers were trained to conduct follow-up visits.",
         None, "Kiambu, Muranga, Nyeri", "program_update", "PROG"),
        ("Financial Accountability Framework", "Quarterly Financial Review",
         "The internal financial review identified minor variances in administrative overhead "
         "due to unplanned travel costs. Corrective measures include implementing a pre-approval "
         "system for travel budgets. Overall compliance score remains above 95%.",
         None, "Head Office", "audit_finding", "FIN"),
        ("Staff Capacity Building", "Team Building Workshop Impact",
         "The annual team building workshop brought together 85 staff from all 5 departments. "
         "Post-workshop surveys indicate a 23% improvement in cross-departmental collaboration scores. "
         "Staff reported feeling more connected to organizational mission.",
         "Working with colleagues from other departments showed me how our efforts interconnect",
         "Naivasha Resort", "program_update", "AHR"),
        ("Strategic Growth & Expansion", "New Partnership with County Government",
         "A memorandum of understanding was signed with Nakuru County Government for youth "
         "employment initiatives. The partnership will leverage county resources and our "
         "program expertise to reach 2,000 additional youth over the next 18 months.",
         None, "Nakuru County", "partnership_update", "EXEC"),
        ("Youth Empowerment Scholarship Program", "Dropout Prevention Intervention",
         "Three scholarship beneficiaries were identified as at-risk of dropping out due to "
         "family financial pressures. Immediate intervention included emergency stipend "
         "disbursement and family counseling sessions. All three students have re-engaged.",
         "When we intervene early, we can change the trajectory of a young person's life",
         "Mombasa", "intervention_log", "PROG"),
        ("Digital Skills Training Initiative", "Industry Mentorship Program Launch",
         "A mentorship program pairing 30 participants with tech industry professionals was launched. "
         "Initial feedback indicates high engagement. Mentors volunteered from 8 different tech companies "
         "including Safaricom and Andela.",
         None, "Nairobi", "program_update", "PROG"),
    ]

    for proj_name, title, content, quote, location, note_type, dept_code in field_notes_data:
        project = projects.get(proj_name)
        dept = departments.get(dept_code)
        if not project:
            continue
        note = FieldNote(
            project_id=project.id,
            reporting_period_id=current_period.id if current_period else None,
            department_id=dept.id if dept else None,
            title=title,
            content=content,
            beneficiary_quote=quote,
            location=location,
            note_type=note_type,
            date_observed=date.today() - timedelta(days=random.randint(1, 60)),
            tags={"department": dept_code, "type": note_type},
        )
        db.add(note)

    db.commit()
    print("Cross-pillar seed data created successfully.")


def seed_workflow_data(db):
    """Seed sample donor reports and approval workflows."""
    periods = db.query(ReportingPeriod).all()
    current_period = db.query(ReportingPeriod).filter(ReportingPeriod.is_current == True).first()
    users = db.query(User).all()

    user_by_tier = {}
    for u in users:
        if u.role:
            tier = u.role.tier
            if tier not in user_by_tier:
                user_by_tier[tier] = u

    # Create sample donor reports at various workflow stages
    reports_data = [
        ("Q3 2026 USAID Progress Report", "USAID", "drafting", 1),
        ("Q3 2026 EU Impact Assessment", "European Union", "tier_2_verification", 2),
        ("Q3 2026 DFID Quarterly Report", "DFID/FCDO", "tier_3_assembly", 3),
        ("Q3 2026 Annual Foundation Report", "MasterCard Foundation", "tier_4_final_sign_off", 4),
    ]

    for title, donor, status, tier in reports_data:
        creator = user_by_tier.get(1, user_by_tier.get(3, users[0]))
        report = DonorReport(
            title=title,
            donor_name=donor,
            reporting_period_id=current_period.id if current_period else None,
            created_by=creator.id,
            workflow_status=status,
            current_tier=tier,
            ai_generated_content={
                "executive_summary": {
                    "content": f"Executive summary for {donor} reporting period. "
                    "This period showed strong progress across all programmatic indicators.",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
                "programmatic_progress": {
                    "content": f"Program performance data for {donor} reporting. "
                    "KPI attainment averaged 89% across all tracked indicators.",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
            },
        )
        db.add(report)
        db.flush()

        # Add approval records for reports that have progressed
        if tier >= 2:
            rv_user = user_by_tier.get(2, users[1])
            db.add(ApprovalRecord(
                donor_report_id=report.id,
                tier=2,
                action="submit_for_review",
                reviewer_id=creator.id,
                comments="Submitted for Tier 2 review",
            ))
            db.add(ApprovalRecord(
                donor_report_id=report.id,
                tier=2,
                action="approve",
                reviewer_id=rv_user.id,
                comments="Data verified and approved for assembly",
            ))

        if tier >= 3:
            rg_user = user_by_tier.get(3, users[3])
            db.add(ApprovalRecord(
                donor_report_id=report.id,
                tier=3,
                action="assemble_report",
                reviewer_id=rg_user.id,
                comments="Report assembled with AI-generated sections",
            ))

    db.commit()
    print("Workflow seed data created successfully.")


def main():
    print("Initializing database...")
    init_db()

    db = SessionLocal()
    try:
        print("Seeding roles, departments, and users...")
        seed_default_roles(db)

        print("Seeding cross-pillar data...")
        seed_cross_pillar_data(db)

        print("Seeding workflow data...")
        seed_workflow_data(db)

        print("\nSeed data complete!")
        print("=" * 60)
        print("DEPARTMENTS:")
        for d in db.query(Department).all():
            print(f"  - {d.name} ({d.code})")
        print("\nROLES (4 Tiers):")
        for r in db.query(Role).all():
            print(f"  Tier {r.tier}: {r.name} - {r.description}")
        print("\nUSERS:")
        for u in db.query(User).all():
            print(f"  - {u.name} ({u.email}) - {u.role.name if u.role else 'N/A'} [{u.department.name if u.department else 'N/A'}]")
        print(f"\nPROJECTS: {db.query(Project).count()}")
        print(f"KPI METRICS: {db.query(KPIMetric).count()}")
        print(f"FINANCIAL ITEMS: {db.query(FinancialLineItem).count()}")
        print(f"RISKS: {db.query(OperationalRisk).count()}")
        print(f"FIELD NOTES: {db.query(FieldNote).count()}")
        print(f"DONOR REPORTS: {db.query(DonorReport).count()}")
        print(f"APPROVAL RECORDS: {db.query(ApprovalRecord).count()}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
