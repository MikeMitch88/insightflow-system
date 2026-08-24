import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-ai-insights',
  templateUrl: './ai-insights.component.html',
  styleUrls: ['./ai-insights.component.css']
})
export class AiInsightsComponent implements OnInit {
  insights: any[] = [];
  loading = true;
  filterSeverity = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void { this.loadInsights(); }

  loadInsights(): void {
    this.loading = true;
    this.api.getAIInsights().subscribe({
      next: (data) => { this.insights = data.insights || (Array.isArray(data) ? data : []); this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  get filteredInsights(): any[] {
    if (!this.filterSeverity) return this.insights;
    return this.insights.filter(i => i.severity === this.filterSeverity);
  }

  getSeverityClass(severity: string): string {
    switch (severity) {
      case 'high': return 'badge-high';
      case 'warning': return 'badge-medium';
      case 'info': return 'badge-info';
      default: return 'badge-info';
    }
  }
}
