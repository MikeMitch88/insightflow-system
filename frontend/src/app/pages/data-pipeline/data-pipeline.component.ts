import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-data-pipeline',
  templateUrl: './data-pipeline.component.html',
  styleUrls: ['./data-pipeline.component.css']
})
export class DataPipelineComponent implements OnInit {
  pipeline: any = {};
  loading = true;

  stages = [
    { label: 'Data Sources', icon: 'storage', status: 'complete', desc: 'Raw CSV data from programs' },
    { label: 'Ingest', icon: 'input', status: 'complete', desc: 'Load and parse CSV files' },
    { label: 'Validate', icon: 'verified', status: 'complete', desc: 'Check data quality rules' },
    { label: 'Transform', icon: 'transform', status: 'complete', desc: 'Standardize and clean data' },
    { label: 'Unify', icon: 'merge', status: 'complete', desc: 'Combine into unified datasets' },
    { label: 'PostgreSQL', icon: 'database', status: 'active', desc: 'Store in normalized schema' },
    { label: 'Analytics', icon: 'analytics', status: 'active', desc: 'Compute KPIs and metrics' },
    { label: 'Reporting', icon: 'description', status: 'active', desc: 'Generate reports and insights' }
  ];

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getPipelineStatus().subscribe({
      next: (data) => { this.pipeline = data || {}; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }
}
