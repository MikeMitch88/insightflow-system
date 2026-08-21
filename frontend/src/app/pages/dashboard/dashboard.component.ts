import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  summary: any = {};
  trends: any[] = [];
  programs: any[] = [];
  periods: any[] = [];
  selectedPeriod: number | null = null;
  loading = true;

  programColors: Record<string, string> = {
    'Scholarship': '#1565c0',
    'Plus': '#7c3aed',
    'Vocational': '#059669',
    'Tech': '#d97706'
  };

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getPeriods().subscribe({
      next: (data) => {
        this.periods = Array.isArray(data) ? data : [];
        const current = this.periods.find((p: any) => p.is_current);
        if (current) this.selectedPeriod = current.id;
        this.loadData();
      },
      error: () => this.loadData()
    });
  }

  loadData(): void {
    this.loading = true;
    this.api.getDashboardSummary(this.selectedPeriod || undefined).subscribe({
      next: (data) => { this.summary = data; this.loading = false; },
      error: () => { this.loading = false; }
    });
    this.api.getDashboardTrends().subscribe({
      next: (data) => { this.trends = Array.isArray(data) ? data : []; }
    });
    this.api.getProgramPerformance(this.selectedPeriod || undefined).subscribe({
      next: (data) => { this.programs = Array.isArray(data) ? data : []; }
    });
  }

  onPeriodChange(): void {
    this.loadData();
  }

  getMaxTrend(): number {
    if (!this.trends.length) return 1;
    return Math.max(...this.trends.map(t => t.beneficiary_count || t.enrollment_count || 0), 1);
  }

  getMaxProgram(): number {
    if (!this.programs.length) return 1;
    return Math.max(...this.programs.map(p => p.total_enrolled || 0), 1);
  }
}
