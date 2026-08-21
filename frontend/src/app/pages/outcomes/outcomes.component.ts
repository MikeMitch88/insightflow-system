import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-outcomes',
  templateUrl: './outcomes.component.html',
  styleUrls: ['./outcomes.component.css']
})
export class OutcomesComponent implements OnInit {
  outcomes: any = {};
  periods: any[] = [];
  selectedPeriod: number | null = null;
  loading = true;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getPeriods().subscribe({
      next: (data) => { this.periods = Array.isArray(data) ? data : []; this.loadData(); },
      error: () => this.loadData()
    });
  }

  loadData(): void {
    this.loading = true;
    this.api.getOutcomes(this.selectedPeriod || undefined).subscribe({
      next: (data) => { this.outcomes = data || {}; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  onPeriodChange(): void { this.loadData(); }
}
