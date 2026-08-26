import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // ============================================================
  // EXISTING ENDPOINTS
  // ============================================================

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

  // ============================================================
  // NEW: RBAC & AUTH ENDPOINTS
  // ============================================================

  getRoles(): Observable<any> {
    return this.http.get(`${this.baseUrl}/auth/roles`);
  }

  getDepartments(): Observable<any> {
    return this.http.get(`${this.baseUrl}/auth/departments`);
  }

  getUsers(): Observable<any> {
    return this.http.get(`${this.baseUrl}/auth/users`);
  }

  // ============================================================
  // NEW: CROSS-PILLAR DATA COLLECTION
  // ============================================================

  getProjects(): Observable<any> {
    return this.http.get(`${this.baseUrl}/cross-pillar/projects`);
  }

  createProject(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/cross-pillar/projects`, data);
  }

  getKpiMetrics(filters: any = {}): Observable<any> {
    let httpParams = new HttpParams();
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined) {
        httpParams = httpParams.set(key, filters[key].toString());
      }
    });
    return this.http.get(`${this.baseUrl}/cross-pillar/kpi-metrics`, { params: httpParams });
  }

  createKpiMetric(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/cross-pillar/kpi-metrics`, data);
  }

  verifyKpiMetric(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/cross-pillar/kpi-metrics/${id}/verify`, {});
  }

  getFinancialItems(filters: any = {}): Observable<any> {
    let httpParams = new HttpParams();
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined) {
        httpParams = httpParams.set(key, filters[key].toString());
      }
    });
    return this.http.get(`${this.baseUrl}/cross-pillar/financial-items`, { params: httpParams });
  }

  createFinancialItem(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/cross-pillar/financial-items`, data);
  }

  verifyFinancialItem(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/cross-pillar/financial-items/${id}/verify`, {});
  }

  getRisks(filters: any = {}): Observable<any> {
    let httpParams = new HttpParams();
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined) {
        httpParams = httpParams.set(key, filters[key].toString());
      }
    });
    return this.http.get(`${this.baseUrl}/cross-pillar/risks`, { params: httpParams });
  }

  createRisk(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/cross-pillar/risks`, data);
  }

  getFieldNotes(filters: any = {}): Observable<any> {
    let httpParams = new HttpParams();
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined) {
        httpParams = httpParams.set(key, filters[key].toString());
      }
    });
    return this.http.get(`${this.baseUrl}/cross-pillar/field-notes`, { params: httpParams });
  }

  createFieldNote(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/cross-pillar/field-notes`, data);
  }

  // ============================================================
  // NEW: WORKFLOW & APPROVAL
  // ============================================================

  getWorkflowStates(): Observable<any> {
    return this.http.get(`${this.baseUrl}/workflow/states`);
  }

  getDonorReports(filters: any = {}): Observable<any> {
    let httpParams = new HttpParams();
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined) {
        httpParams = httpParams.set(key, filters[key].toString());
      }
    });
    return this.http.get(`${this.baseUrl}/workflow/reports`, { params: httpParams });
  }

  createDonorReport(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/workflow/reports`, data);
  }

  getDonorReport(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/workflow/reports/${id}`);
  }

  transitionReport(reportId: number, action: string, comments?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/workflow/reports/${reportId}/transition`, {
      action,
      comments,
    });
  }

  approveReport(reportId: number, comments?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/workflow/reports/${reportId}/approve`, null, {
      params: comments ? { comments } : {},
    });
  }

  rejectReport(reportId: number, comments?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/workflow/reports/${reportId}/reject`, null, {
      params: comments ? { comments } : {},
    });
  }

  submitForReview(reportId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/workflow/reports/${reportId}/submit`, {});
  }

  getAuditLogs(filters: any = {}): Observable<any> {
    let httpParams = new HttpParams();
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined) {
        httpParams = httpParams.set(key, filters[key].toString());
      }
    });
    return this.http.get(`${this.baseUrl}/workflow/audit-logs`, { params: httpParams });
  }

  // ============================================================
  // NEW: AI REPORT GENERATION
  // ============================================================

  getReportSections(): Observable<any> {
    return this.http.get(`${this.baseUrl}/report-gen/sections`);
  }

  getDonorReportList(): Observable<any> {
    return this.http.get(`${this.baseUrl}/report-gen/donor-reports`);
  }

  createDonorReportGen(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/report-gen/donor-reports`, null, {
      params: data,
    });
  }

  generateReportSection(reportId: number, sectionId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/report-gen/donor-reports/${reportId}/generate-section/${sectionId}`, {});
  }

  generateAllSections(reportId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/report-gen/donor-reports/${reportId}/generate-all`, {});
  }

  ingestDataToVectorStore(reportId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/report-gen/donor-reports/${reportId}/ingest-data`, {});
  }

  getReportContent(reportId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/report-gen/donor-reports/${reportId}/content`);
  }

  getVectorStoreStats(reportId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/report-gen/donor-reports/${reportId}/stats`);
  }

  // ============================================================
  // ADMIN NOTIFICATIONS
  // ============================================================

  getNotifications(role: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/notifications`, { params: { role } });
  }

  markNotificationRead(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/admin/notifications/${id}/read`, {});
  }

  clearAllNotifications(role: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/admin/notifications/clear`, { role });
  }

  // ============================================================
  // ADMIN USER MANAGEMENT
  // ============================================================

  getAdminUsers(): Observable<any> {
    return this.http.get(`${this.baseUrl}/admin/users`);
  }

  updateAdminUser(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/admin/users/${id}`, data);
  }

  // ============================================================
  // AUDIT LOGS
  // ============================================================

  createAuditLog(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/workflow/audit-logs`, data);
  }

  // ============================================================
  // DATA QUALITY MANAGEMENT
  // ============================================================

  resolveDataQualityIssue(id: number, data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/data-quality/issues/${id}/resolve`, data);
  }

  batchResolveDataQualityIssues(): Observable<any> {
    return this.http.post(`${this.baseUrl}/data-quality/batch-resolve`, {});
  }
}
