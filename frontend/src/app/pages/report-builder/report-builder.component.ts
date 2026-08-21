import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-report-builder',
  templateUrl: './report-builder.component.html',
  styleUrls: ['./report-builder.component.css']
})
export class ReportBuilderComponent implements OnInit {
  currentStep = 1;
  totalSteps = 4;
  periods: any[] = [];
  generating = false;
  generatedReport: any = null;

  config = {
    title: '',
    report_type: 'executive',
    reporting_period_id: null as number | null,
    program: '',
    use_ai_insights: false,
    sections: ['executive_summary', 'program_performance', 'beneficiary_reach', 'outcomes']
  };

  availableSections = [
    { id: 'executive_summary', label: 'Executive Summary' },
    { id: 'program_performance', label: 'Program Performance' },
    { id: 'beneficiary_reach', label: 'Beneficiary Reach' },
    { id: 'outcomes', label: 'Outcomes & Impact' },
    { id: 'geographic_distribution', label: 'Geographic Distribution' },
    { id: 'key_challenges', label: 'Key Challenges' },
    { id: 'recommendations', label: 'Recommendations' }
  ];

  reportTypes = [
    { value: 'executive', label: 'Executive Report' },
    { value: 'program_performance', label: 'Program Performance Report' },
    { value: 'donor', label: 'Donor Report' },
    { value: 'monday_evidence', label: 'M&E Report' }
  ];

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getPeriods().subscribe({
      next: (data) => { this.periods = Array.isArray(data) ? data : []; }
    });
  }

  nextStep(): void { if (this.currentStep < this.totalSteps) this.currentStep++; }
  prevStep(): void { if (this.currentStep > 1) this.currentStep--; }

  toggleSection(sectionId: string): void {
    const idx = this.config.sections.indexOf(sectionId);
    if (idx > -1) this.config.sections.splice(idx, 1);
    else this.config.sections.push(sectionId);
  }

  isSectionSelected(sectionId: string): boolean {
    return this.config.sections.includes(sectionId);
  }

  generateReport(): void {
    if (!this.config.reporting_period_id || !this.config.title) return;
    this.generating = true;
    this.api.generateReport(this.config).subscribe({
      next: (data) => { this.generatedReport = data; this.generating = false; this.currentStep = 4; },
      error: () => { this.generating = false; }
    });
  }

  getPeriodName(id: number): string {
    const p = this.periods.find((p: any) => p.id === id);
    return p ? p.name : '';
  }
}
