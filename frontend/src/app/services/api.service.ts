import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getDashboardSummary(period?: number): Observable<any> {
    let params = new HttpParams();
    if (period) params = params.set('period', period.toString());
    return this.http.get(`${this.baseUrl}/dashboard/summary`, { params });
  }

  getDashboardTrends(program?: string): Observable<any> {
    let params = new HttpParams();
    if (program) params = params.set('program', program);
    return this.http.get(`${this.baseUrl}/dashboard/trends`, { params });
  }

  getProgramPerformance(period?: number): Observable<any> {
    let params = new HttpParams();
    if (period) params = params.set('period', period.toString());
    return this.http.get(`${this.baseUrl}/programs/performance`, { params });
  }

  getBeneficiaries(params: any = {}): Observable<any> {
    let httpParams = new HttpParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        httpParams = httpParams.set(key, params[key].toString());
      }
    });
    return this.http.get(`${this.baseUrl}/beneficiaries`, { params: httpParams });
  }

  getBeneficiaryAnalytics(params: any = {}): Observable<any> {
    let httpParams = new HttpParams();
    Object.keys(params).forEach(key => {
      if (params[key]) httpParams = httpParams.set(key, params[key]);
    });
    return this.http.get(`${this.baseUrl}/beneficiaries/analytics`, { params: httpParams });
  }

  getOutcomes(period?: number): Observable<any> {
    let params = new HttpParams();
    if (period) params = params.set('period', period.toString());
    return this.http.get(`${this.baseUrl}/outcomes`, { params });
  }

  getDataQuality(): Observable<any> {
    return this.http.get(`${this.baseUrl}/data-quality`);
  }

  getDataSources(): Observable<any> {
    return this.http.get(`${this.baseUrl}/data-sources`);
  }

  getPipelineStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/pipeline/status`);
  }

  getReports(params: any = {}): Observable<any> {
    let httpParams = new HttpParams();
    Object.keys(params).forEach(key => {
      if (params[key]) httpParams = httpParams.set(key, params[key].toString());
    });
    return this.http.get(`${this.baseUrl}/reports`, { params: httpParams });
  }

  generateReport(config: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/reports/generate`, config);
  }

  getReport(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/reports/${id}`);
  }

<<<<<<< HEAD
  addInsightToReport(reportId: number, insight: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/reports/${reportId}/add-insight`, insight);
=======
  getReportInsights(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/reports/${id}/insights`);
>>>>>>> 992c6da (ai assistatnce)
  }

  chatWithAI(message: string, context?: string): Observable<any> {
    const body: any = { message };
    if (context) body.context_page = context;
    return this.http.post(`${this.baseUrl}/ai/chat`, body);
  }

  getAIInsights(period?: number): Observable<any> {
    let params = new HttpParams();
    if (period) params = params.set('period', period.toString());
    return this.http.get(`${this.baseUrl}/ai/insights`, { params });
  }

  getPeriods(): Observable<any> {
    return this.http.get(`${this.baseUrl}/periods`);
  }

  healthCheck(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }

  syncDataSources(): Observable<any> {
    return this.http.post(`${this.baseUrl}/pipeline/sync`, {});
  }

  getSettings(): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/settings`);
  }

  updateSettings(settings: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/admin/settings`, settings);
  }
}
