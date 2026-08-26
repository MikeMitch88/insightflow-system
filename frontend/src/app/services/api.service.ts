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

  previewReport(config: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/reports/preview`, config);
  }

  validateReport(config: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/reports/validate`, config);
  }

  generateReport(config: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/reports/generate`, config);
  }

  getReport(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/reports/${id}`);
  }

  getReportPreview(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/reports/${id}/preview`);
  }

  getReportVersions(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/reports/${id}/versions`);
  }

  getReportReadiness(periodId?: number): Observable<any> {
    let params = new HttpParams();
    if (periodId) params = params.set('period_id', periodId.toString());
    return this.http.get(`${this.baseUrl}/reports/readiness`, { params });
  }

  approveReport(reportId: number, body: { comment?: string } = {}): Observable<any> {
    return this.http.post(`${this.baseUrl}/reports/${reportId}/approve`, body);
  }

  rejectReport(reportId: number, body: { reason: string; feedback?: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/reports/${reportId}/reject`, body);
  }

  reviseReport(reportId: number, body: { notes?: string } = {}): Observable<any> {
    return this.http.post(`${this.baseUrl}/reports/${reportId}/revise`, body);
  }

  getReportAIInsights(reportId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/reports/${reportId}/ai-insights`);
  }

  addInsightToReport(reportId: number, insight: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/reports/${reportId}/add-insight`, insight);
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

  getAdminUsers(): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/users`);
  }

  updateAdminUser(userId: number, data: { status?: string; role?: string }): Observable<any> {
    return this.http.put(`${this.baseUrl}/admin/users/${userId}`, data);
  }

  getAuditLogs(): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/audit-logs`);
  }

  createAuditLog(log: { user: string; action: string; details: string; category?: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/admin/audit-logs`, log);
  }

  updateReportStatus(reportId: number, status: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/reports/${reportId}/status`, { status });
  }

  resolveDataQualityIssue(issueId: number, data: any = {}): Observable<any> {
    return this.http.put(`${this.baseUrl}/data-quality/${issueId}/resolve`, data);
  }

  batchResolveDataQualityIssues(): Observable<any> {
    return this.http.post(`${this.baseUrl}/data-quality/batch-resolve`, {});
  }

  getNotifications(role?: string): Observable<any> {
    let params = new HttpParams();
    if (role) params = params.set('role', role);
    return this.http.get(`${this.baseUrl}/notifications`, { params });
  }

  markNotificationRead(notificationId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/notifications/${notificationId}/read`, {});
  }

  clearAllNotifications(role?: string): Observable<any> {
    let params = new HttpParams();
    if (role) params = params.set('role', role);
    return this.http.post(`${this.baseUrl}/notifications/clear-all`, {}, { params });
  }
}


