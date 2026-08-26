import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-audit-trail',
  templateUrl: './audit-trail.component.html',
  styleUrls: ['./audit-trail.component.css']
})
export class AuditTrailComponent implements OnInit {
  auditLogs: any[] = [];
  loading = true;
  filterEntityType = '';
  filterAction = '';

  entityTypes = ['user', 'donor_report', 'kpi_metric', 'financial_line_item', 'operational_risk', 'field_note', 'project'];

  constructor(
    private api: ApiService,
    public auth: AuthService
  ) {}

  ngOnInit(): void {
    this.loadAuditLogs();
  }

  loadAuditLogs(): void {
    this.loading = true;
    const filters: any = {};
    if (this.filterEntityType) filters.entity_type = this.filterEntityType;
    if (this.filterAction) filters.action = this.filterAction;

    this.api.getAuditLogs(filters).subscribe({
      next: (data) => { this.auditLogs = data; this.loading = false; },
      error: () => this.loading = false
    });
  }

  formatAction(action: string): string {
    return action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  formatChanges(changes: any): string {
    if (!changes) return '-';
    if (typeof changes === 'string') return changes;
    return Object.entries(changes).map(([k, v]) => `${k}: ${v}`).join(', ');
  }
}
