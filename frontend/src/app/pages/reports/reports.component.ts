import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.css']
})
export class ReportsComponent implements OnInit {
  reports: any[] = [];
  loading = true;
  searchTerm = '';
  filterType = '';
  page = 1;
  pageSize = 10;
  totalReports = 0;

  constructor(private api: ApiService) {}

  ngOnInit(): void { this.loadReports(); }

  loadReports(): void {
    this.loading = true;
    const params: any = { page: this.page, page_size: this.pageSize };
    if (this.searchTerm) params.search = this.searchTerm;
    if (this.filterType) params.report_type = this.filterType;
    this.api.getReports(params).subscribe({
      next: (data: any) => {
        this.reports = data.items || data || [];
        this.totalReports = data.total || this.reports.length;
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  onSearch(): void { this.page = 1; this.loadReports(); }
  onFilterChange(): void { this.page = 1; this.loadReports(); }
  nextPage(): void { this.page++; this.loadReports(); }
  prevPage(): void { if (this.page > 1) { this.page--; this.loadReports(); } }

  getStatusClass(status: string): string {
    switch (status) {
      case 'completed': return 'badge-completed';
      case 'generating': return 'badge-generating';
      case 'draft': return 'badge-draft';
      default: return 'badge-draft';
    }
  }

  getTypeLabel(type: string): string {
    switch (type) {
      case 'executive': return 'Executive Report';
      case 'program_performance': return 'Program Performance';
      case 'donor': return 'Donor Report';
      case 'monday_evidence': return 'M&E Report';
      default: return type;
    }
  }

  downloadReport(reportId: number, format: string): void {
    const token = localStorage.getItem('insightflow_token');
    const url = `http://localhost:8000/api/reports/${reportId}/download?format=${format}`;
    fetch(url, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => {
        if (!res.ok) throw new Error('Download failed');
        return res.blob();
      })
      .then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `report.${format}`;
        a.click();
        URL.revokeObjectURL(a.href);
      })
      .catch(() => alert('Download failed. Make sure the report is completed.'));
  }

  refreshReports(): void { this.loadReports(); }
}
