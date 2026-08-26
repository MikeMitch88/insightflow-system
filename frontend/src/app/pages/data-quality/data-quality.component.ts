import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-data-quality',
  templateUrl: './data-quality.component.html',
  styleUrls: ['./data-quality.component.css']
})
export class DataQualityComponent implements OnInit {
  quality: any = {};
  loading = true;
  resolving = false;
  resolveMessage = '';
  selectedFilter = 'all';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadQualityData();
  }

  loadQualityData(): void {
    this.loading = true;
    this.api.getDataQuality().subscribe({
      next: (data) => { this.quality = data || {}; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  get filteredIssues(): any[] {
    const issues = this.quality.issues || [];
    if (this.selectedFilter === 'all') return issues;
    if (this.selectedFilter === 'critical') return issues.filter((i: any) => i.severity === 'high' || i.severity === 'critical');
    if (this.selectedFilter === 'resolved') return issues.filter((i: any) => i.status === 'resolved');
    if (this.selectedFilter === 'pending') return issues.filter((i: any) => i.status !== 'resolved');
    return issues;
  }

  resolveIssue(issue: any): void {
    issue.status = 'resolved';
    this.api.resolveDataQualityIssue(issue.id, { assigned_to: 'James Otieno' }).subscribe({
      next: () => {
        this.api.createAuditLog({
          user: 'James Otieno (M&E)',
          action: 'Resolved Quality Issue',
          details: `Fixed ${issue.issue_type} in ${issue.source_file} (Record: ${issue.record_id})`,
          category: 'Data Quality'
        }).subscribe();
      }
    });
  }

  batchResolve(): void {
    this.resolving = true;
    this.api.batchResolveDataQualityIssues().subscribe({
      next: (res) => {
        this.resolving = false;
        this.resolveMessage = res.message || 'Auto-standardized top data quality anomalies successfully!';
        (this.quality.issues || []).forEach((i: any) => i.status = 'resolved');
        this.quality.score = Math.min(100, (this.quality.score || 85) + 12);
        setTimeout(() => this.resolveMessage = '', 4000);
      },
      error: () => { this.resolving = false; }
    });
  }

  getSeverityClass(severity: string): string {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high': return 'badge-high';
      case 'medium': return 'badge-medium';
      case 'low': return 'badge-low';
      default: return 'badge-info';
    }
  }

  getScoreClass(): string {
    const score = this.quality.score || 0;
    if (score >= 85) return 'quality-good';
    if (score >= 70) return 'quality-warning';
    return 'quality-bad';
  }
}

