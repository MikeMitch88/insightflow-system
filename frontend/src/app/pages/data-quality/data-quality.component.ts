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

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getDataQuality().subscribe({
      next: (data) => { this.quality = data || {}; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  getSeverityClass(severity: string): string {
    switch (severity) {
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
