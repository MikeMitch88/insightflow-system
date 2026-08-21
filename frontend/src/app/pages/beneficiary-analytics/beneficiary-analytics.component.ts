import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-beneficiary-analytics',
  templateUrl: './beneficiary-analytics.component.html',
  styleUrls: ['./beneficiary-analytics.component.css']
})
export class BeneficiaryAnalyticsComponent implements OnInit {
  analytics: any = {};
  selectedProgram = '';
  selectedCounty = '';
  selectedGender = '';
  loading = true;

  constructor(private api: ApiService) {}

  ngOnInit(): void { this.loadData(); }

  loadData(): void {
    this.loading = true;
    const params: any = {};
    if (this.selectedProgram) params.program = this.selectedProgram;
    if (this.selectedCounty) params.county = this.selectedCounty;
    if (this.selectedGender) params.gender = this.selectedGender;
    this.api.getBeneficiaryAnalytics(params).subscribe({
      next: (data) => { this.analytics = data || {}; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  onFilterChange(): void { this.loadData(); }

  getTotal(distribution: any[]): number {
    return distribution ? distribution.reduce((s, d) => s + (d.count || 0), 0) : 1;
  }

  getMaxCount(distribution: any[]): number {
    return distribution && distribution.length ? Math.max(...distribution.map(d => d.count || 0), 1) : 1;
  }
}
