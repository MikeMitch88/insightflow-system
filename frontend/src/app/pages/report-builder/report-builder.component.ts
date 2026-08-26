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
    { value: 'donor', label: 'Inuka Donor Impact Report' },
    { value: 'monday_evidence', label: 'M&E Indicator Report' }
  ];

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getPeriods().subscribe({
      next: (data: any) => {
        this.periods = data.items || (Array.isArray(data) ? data : []);
        if (this.periods.length && !this.config.reporting_period_id) {
          this.config.reporting_period_id = this.periods[this.periods.length - 1].id;
          this.applyDonorPreset();
        }
      }
    });
  }

  applyDonorPreset(): void {
    const activePeriodName = this.getPeriodName(this.config.reporting_period_id || 7) || 'Q3 2026';
    this.config.title = `${activePeriodName} Inuka Cross-Pillar Donor Impact Report`;
    this.config.report_type = 'donor';
    this.config.use_ai_insights = true;
    this.config.sections = [
      'executive_summary',
      'program_performance',
      'beneficiary_reach',
      'outcomes',
      'geographic_distribution',
      'recommendations'
    ];
  }

  onTypeChange(): void {
    if (this.config.report_type === 'donor') {
      this.applyDonorPreset();
    }
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
    this.currentStep = 4;
    this.api.generateReport(this.config).subscribe({
      next: (data) => {
        this.generatedReport = data;
        this.generating = false;
        this.api.createAuditLog({
          user: 'Amina Hassan (Reporting)',
          action: 'Generated Report',
          details: `Generated ${data.title} (${data.report_type})`,
          category: 'Report'
        }).subscribe();
      },
      error: () => { this.generating = false; this.currentStep = 3; }
    });
  }

  downloadGenerated(format: string): void {
    if (!this.generatedReport?.id) return;
    const token = localStorage.getItem('insightflow_token');
    const url = `http://localhost:8000/api/reports/${this.generatedReport.id}/download?format=${format}`;
    fetch(url, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => {
        if (!res.ok) throw new Error('Download failed');
        return res.blob();
      })
      .then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `${this.generatedReport.title || 'report'}.${format}`;
        a.click();
        URL.revokeObjectURL(a.href);
      })
      .catch(() => alert('Download error'));
  }

  getPeriodName(id: number): string {
    const p = this.periods.find((p: any) => p.id === id);
    return p ? p.name : '';
  }

  getReportTypeLabel(value: string): string {
    const type = this.reportTypes.find(t => t.value === value);
    return type ? type.label : value;
  }
}

