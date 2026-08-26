import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-donor-report-builder',
  templateUrl: './donor-report-builder.component.html',
  styleUrls: ['./donor-report-builder.component.css']
})
export class DonorReportBuilderComponent implements OnInit {
  sections: any[] = [];
  reports: any[] = [];
  selectedReport: any = null;
  reportContent: any = null;
  loading = true;
  generating = false;
  ingesting = false;
  vectorStats: any = null;

  newReportTitle = '';
  newReportDonor = '';
  showNewForm = false;

  constructor(
    private api: ApiService,
    public auth: AuthService
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading = true;
    this.api.getReportSections().subscribe(data => this.sections = data);
    this.api.getDonorReportList().subscribe({
      next: (data) => { this.reports = data; this.loading = false; },
      error: () => this.loading = false
    });
  }

  createReport(): void {
    if (!this.newReportTitle) return;
    this.api.createDonorReportGen({
      title: this.newReportTitle,
      donor_name: this.newReportDonor || undefined,
    }).subscribe({
      next: () => {
        this.showNewForm = false;
        this.newReportTitle = '';
        this.newReportDonor = '';
        this.loadData();
      },
      error: (err) => alert(err.error?.detail || 'Failed to create report')
    });
  }

  selectReport(report: any): void {
    this.selectedReport = report;
    this.api.getReportContent(report.id).subscribe(data => this.reportContent = data);
  }

  ingestData(): void {
    if (!this.selectedReport) return;
    this.ingesting = true;
    this.api.ingestDataToVectorStore(this.selectedReport.id).subscribe({
      next: (data) => {
        this.vectorStats = data.stats;
        this.ingesting = false;
      },
      error: () => this.ingesting = false
    });
  }

  generateSection(sectionId: string): void {
    if (!this.selectedReport) return;
    this.generating = true;
    this.api.generateReportSection(this.selectedReport.id, sectionId).subscribe({
      next: () => {
        this.generating = false;
        this.api.getReportContent(this.selectedReport.id).subscribe(data => this.reportContent = data);
      },
      error: (err) => { this.generating = false; alert(err.error?.detail || 'Generation failed'); }
    });
  }

  generateAllSections(): void {
    if (!this.selectedReport) return;
    this.generating = true;
    this.api.generateAllSections(this.selectedReport.id).subscribe({
      next: () => {
        this.generating = false;
        this.api.getReportContent(this.selectedReport.id).subscribe(data => this.reportContent = data);
      },
      error: (err) => { this.generating = false; alert(err.error?.detail || 'Generation failed'); }
    });
  }

  getSectionContent(sectionId: string): string {
    return this.reportContent?.sections?.[sectionId]?.content || 'Not yet generated. Click Generate to create this section.';
  }

  getSectionGeneratedAt(sectionId: string): string {
    return this.reportContent?.sections?.[sectionId]?.generated_at || '';
  }
}
