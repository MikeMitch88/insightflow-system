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
<<<<<<< HEAD
      next: (data) => { this.insights = data.insights || (Array.isArray(data) ? data : []); this.loading = false; },
=======
      next: (data: any) => { this.insights = Array.isArray(data) ? data : (data?.insights || []); this.loading = false; },
>>>>>>> 992c6da (ai assistatnce)
      error: () => { this.loading = false; }
    });
  }

  get filteredInsights(): any[] {
    if (!this.filterSeverity) return this.insights;
    return this.insights.filter(insight => insight.severity === this.filterSeverity);
  }

  getInsightType(insight: any): string {
    return insight.type || (insight.category === 'data_quality' ? 'data_quality' : 'warning');
  }

  getTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      warning: 'Warning', trend: 'Trend', kpi: 'KPI Performance',
      data_quality: 'Data Quality', recommendation: 'Recommendation'
    };
    return labels[type] || 'Insight';
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
