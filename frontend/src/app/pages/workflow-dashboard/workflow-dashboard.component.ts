import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-workflow-dashboard',
  templateUrl: './workflow-dashboard.component.html',
  styleUrls: ['./workflow-dashboard.component.css']
})
export class WorkflowDashboardComponent implements OnInit {
  reports: any[] = [];
  workflowStates: any[] = [];
  selectedReport: any = null;
  loading = true;
  activeFilter = 'all';

  constructor(
    private api: ApiService,
    public auth: AuthService
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading = true;
    this.api.getWorkflowStates().subscribe(states => this.workflowStates = states);
    this.api.getDonorReports().subscribe({
      next: (reports) => {
        this.reports = reports;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  get filteredReports(): any[] {
    if (this.activeFilter === 'all') return this.reports;
    return this.reports.filter(r => r.workflow_status === this.activeFilter);
  }

  getStatusCounts(): Record<string, number> {
    const counts: Record<string, number> = { all: this.reports.length };
    this.reports.forEach(r => {
      counts[r.workflow_status] = (counts[r.workflow_status] || 0) + 1;
    });
    return counts;
  }

  selectReport(report: any): void {
    this.api.getDonorReport(report.id).subscribe(data => {
      this.selectedReport = data;
    });
  }

  transitionReport(action: string): void {
    if (!this.selectedReport) return;
    const comments = prompt(`Comments for ${action}:`);
    this.api.transitionReport(this.selectedReport.report_id, action, comments || undefined).subscribe({
      next: () => {
        this.selectedReport = null;
        this.loadData();
      },
      error: (err) => alert(err.error?.detail || 'Transition failed')
    });
  }

  canPerformAction(action: string): boolean {
    if (!this.selectedReport) return false;
    return this.auth.canAccessWorkflowAction(action, this.selectedReport.current_state);
  }

  getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      drafting: 'Drafting',
      tier_2_verification: 'Tier 2 Review',
      tier_3_assembly: 'Tier 3 Assembly',
      tier_4_final_sign_off: 'Final Sign-Off',
      exported_sent: 'Exported/Sent'
    };
    return labels[status] || status;
  }

  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      drafting: '#6366f1',
      tier_2_verification: '#f59e0b',
      tier_3_assembly: '#3b82f6',
      tier_4_final_sign_off: '#10b981',
      exported_sent: '#6b7280'
    };
    return colors[status] || '#6b7280';
  }
}
