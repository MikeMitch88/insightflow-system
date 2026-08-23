import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-program-performance',
  templateUrl: './program-performance.component.html',
  styleUrls: ['./program-performance.component.css']
})
export class ProgramPerformanceComponent implements OnInit {
  allPrograms: any[] = [];
  programs: any[] = [];
  periods: any[] = [];
  selectedPeriod: number | null = null;
  selectedProgram = '';
  loading = true;

  totalEnrolled = 0;
  totalActive = 0;
  totalCompleted = 0;
  totalDropped = 0;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getPeriods().subscribe({
      next: (data: any) => {
        this.periods = data.items || (Array.isArray(data) ? data : []);
        this.loadData();
      },
      error: () => this.loadData()
    });
  }

  loadData(): void {
    this.loading = true;
    this.api.getProgramPerformance(this.selectedPeriod || undefined).subscribe({
      next: (data) => {
        this.allPrograms = Array.isArray(data) ? data : [];
        this.applyFilters();
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  applyFilters(): void {
    if (this.selectedProgram) {
      this.programs = this.allPrograms.filter(p => p.program_name === this.selectedProgram);
    } else {
      this.programs = [...this.allPrograms];
    }
    this.computeTotals();
  }

  computeTotals(): void {
    this.totalEnrolled = this.programs.reduce((s, p) => s + (p.total_enrolled || 0), 0);
    this.totalActive = this.programs.reduce((s, p) => s + (p.active || 0), 0);
    this.totalCompleted = this.programs.reduce((s, p) => s + (p.completed || 0), 0);
    this.totalDropped = this.programs.reduce((s, p) => s + (p.dropped_out || 0), 0);
  }

  onFilterChange(): void {
    if (this.selectedPeriod) {
      this.loadData();
    } else {
      this.applyFilters();
    }
  }

  getMax(): number {
    return Math.max(...this.programs.map(p => p.total_enrolled || 0), 1);
  }
}
