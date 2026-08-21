import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-data-sources',
  templateUrl: './data-sources.component.html',
  styleUrls: ['./data-sources.component.css']
})
export class DataSourcesComponent implements OnInit {
  sources: any[] = [];
  loading = true;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getDataSources().subscribe({
      next: (data) => {
        this.sources = Array.isArray(data) ? data : (data?.sources || []);
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  getStatusClass(status: string): string {
    switch (status?.toLowerCase()) {
      case 'active': return 'badge-active';
      case 'syncing': return 'badge-generating';
      case 'inactive': return 'badge-draft';
      default: return 'badge-info';
    }
  }
}
