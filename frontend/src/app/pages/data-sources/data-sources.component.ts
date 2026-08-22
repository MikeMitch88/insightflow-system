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
  syncing = false;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading = true;
    this.api.getDataSources().subscribe({
      next: (data) => {
        this.sources = Array.isArray(data) ? data : (data?.sources || []);
        this.loading = false;
        this.syncing = false;
      },
      error: () => {
        this.loading = false;
        this.syncing = false;
      }
    });
  }

  triggerSync(): void {
    this.syncing = true;
    this.api.syncDataSources().subscribe({
      next: () => {
        // Wait 4 seconds for backend to run ETL, then reload
        setTimeout(() => {
          this.loadData();
        }, 4000);
      },
      error: () => {
        this.syncing = false;
      }
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
