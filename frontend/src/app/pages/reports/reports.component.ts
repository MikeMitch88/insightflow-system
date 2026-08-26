import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.css']
})
export class ReportsComponent implements OnInit {
  reports: any[] = [];
  loading = true;
  searchTerm = '';
  filterType = '';
  filterApprovalStatus = '';
  page = 1;
  pageSize = 10;
  totalReports = 0;

  toastMessage: string | null = null;
  toastType = 'success';

  isAdmin = false;
  isManager = false;

  adminPeriodId = 0;
  periods: any[] = [];
  adminReportType = 'Monthly Donor Report';
  reportTypes = [
    { value: 'Monthly Donor Report', label: 'Monthly Donor Report' },
    { value: 'Quarterly Report', label: 'Quarterly Report' },
    { value: 'Annual Report', label: 'Annual Report' },
    { value: 'M&E Report', label: 'M&E Report' },
  ];

  pendingReviewReports: any[] = [];
  summaryStats = { total: 0, approved: 0, pendingReview: 0, rejected: 0 };

  showAdminReviewModal = false;
  adminPreviewLoading = false;
  adminPreviewData: any = null;
  adminActiveTab = 'summary';
  adminValidationData: any = null;
  adminConfirmReviewed = false;
  adminConfirmKPIs = false;
  adminConfirmWarnings = false;
  adminConfirmReady = false;

  get isGenerationReady(): boolean {
    return this.adminConfirmReviewed && this.adminConfirmKPIs && this.adminConfirmWarnings && this.adminConfirmReady;
  }
  actionLoading = false;

  showManagerViewModal = false;
  managerViewLoading = false;
  selectedReport: any = null;
  managerActiveTab = 'summary';

  showApproveConfirmModal = false;
  approvalComment = '';

  showRejectModal = false;
  rejectReason = '';
  rejectionReasonsList = [
    'Missing financial data',
    'Incomplete beneficiary counts',
    'Inconsistent pillar metrics',
    'KPC log discrepancies',
    'Narrative needs revision',
    'Data quality concerns',
  ];

  showReviseModal = false;
  revisingReport: any = null;
  reviseNotes = '';

  showAdminValidateModal = false;
  validationRunning = false;

  constructor(
    private api: ApiService,
    private auth: AuthService,
    private http: HttpClient,
  ) {}

  ngOnInit(): void {
    this.isAdmin = this.auth.hasMinTier(3);
    this.isManager = this.auth.userTier === 2 || this.auth.hasMinTier(3);
    this.loadPeriods();
    this.loadReports();
  }

  loadPeriods(): void {
    this.api.getPeriods().subscribe({
      next: (data: any) => {
        this.periods = Array.isArray(data) ? data : [];
        if (this.periods.length > 0) {
          this.adminPeriodId = this.periods[0].id;
        }
      },
      error: () => { this.periods = []; }
    });
  }

  loadReports(): void {
    this.loading = true;
    const params: any = { page: this.page, page_size: this.pageSize };
    if (this.searchTerm) params.search = this.searchTerm;
    if (this.filterType) params.report_type = this.filterType;
    if (this.filterApprovalStatus) params.approval_status = this.filterApprovalStatus;
    this.api.getReports(params).subscribe({
      next: (data: any) => {
        const items = data.items || data || [];
        this.reports = items;
        this.totalReports = data.total || items.length;
        this.computeSummaryStats(items);
        this.computePendingReview(items);
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  computeSummaryStats(items: any[]): void {
    let approved = 0, pendingReview = 0, rejected = 0;
    for (const r of items) {
      const st = (r.status || '').toLowerCase();
      if (st === 'approved' || st === 'completed') approved++;
      else if (st.includes('pending') || st.includes('manager_review')) pendingReview++;
      else if (st.includes('revision') || st.includes('rejected')) rejected++;
    }
    this.summaryStats = {
      total: this.totalReports,
      approved,
      pendingReview,
      rejected,
    };
  }

  computePendingReview(items: any[]): void {
    this.pendingReviewReports = items.filter(r => {
      const st = (r.status || '').toLowerCase();
      return st.includes('pending') || st.includes('manager_review');
    });
  }

  onSearch(): void { this.page = 1; this.loadReports(); }
  onFilterChange(): void { this.page = 1; this.loadReports(); }
  nextPage(): void { this.page++; this.loadReports(); }
  prevPage(): void { if (this.page > 1) { this.page--; this.loadReports(); } }
  refreshReports(): void { this.loadReports(); this.showToast('Reports refreshed', 'success'); }

  onAdminPeriodSelect(event: any): void {
    this.adminPeriodId = parseInt(event.target.value, 10);
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'completed': return 'badge-completed';
      case 'generating': return 'badge-generating';
      case 'draft': return 'badge-draft';
      default: return 'badge-draft';
    }
  }

  getStatusBadgeClass(status: string): string {
    const st = (status || '').toLowerCase();
    if (st === 'approved' || st === 'completed') return 'badge-approved';
    if (st.includes('pending') || st.includes('manager_review')) return 'badge-review';
    if (st.includes('revision') || st.includes('rejected')) return 'badge-rejected';
    if (st.includes('admin_review') || st.includes('generating')) return 'badge-review';
    return 'badge-draft';
  }

  getStatusDisplay(status: string): string {
    const st = (status || '').toLowerCase();
    if (st === 'approved' || st === 'completed') return 'Approved';
    if (st.includes('pending_manager_review') || st.includes('pending')) return 'Pending Manager Review';
    if (st.includes('revision_required') || st.includes('rejected')) return 'Revision Required';
    if (st.includes('admin_review')) return 'Admin Review';
    if (st.includes('generating')) return 'Generating';
    return status ? status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : 'Draft';
  }

  getTypeLabel(type: string): string {
    switch (type) {
      case 'executive': return 'Executive Report';
      case 'program_performance': return 'Program Performance';
      case 'donor': return 'Donor Report';
      case 'monday_evidence': return 'M&E Report';
      default: return type || 'Report';
    }
  }

  showToast(message: string, type: string = 'success'): void {
    this.toastMessage = message;
    this.toastType = type;
    setTimeout(() => { this.toastMessage = null; }, 5000);
  }

  // =========================================================================
  // ADMIN VALIDATION
  // =========================================================================

  openValidateOnly(): void {
    this.showAdminValidateModal = true;
    this.validationRunning = true;
    const params = {
      reporting_period_id: this.adminPeriodId,
      reporting_period: this.periods.find(p => p.id === this.adminPeriodId)?.name || '',
    };
    this.http.post(`${environment.apiUrl}/reports/validate`, params).subscribe({
      next: (data: any) => {
        this.adminValidationData = data;
        this.validationRunning = false;
      },
      error: () => {
        this.validationRunning = false;
        this.showToast('Validation failed. Please try again.', 'danger');
      }
    });
  }

  closeAdminValidateModal(): void {
    this.showAdminValidateModal = false;
    this.validationRunning = false;
    this.adminValidationData = null;
  }

  // =========================================================================
  // ADMIN REVIEW & GENERATE
  // =========================================================================

  openReviewReport(): void {
    this.showAdminReviewModal = true;
    this.adminPreviewLoading = true;
    this.adminConfirmReviewed = false;
    this.adminConfirmKPIs = false;
    this.adminConfirmWarnings = false;
    this.adminConfirmReady = false;
    this.adminActiveTab = 'summary';

    const period = this.periods.find(p => p.id === this.adminPeriodId);
    const params = {
      reporting_period_id: this.adminPeriodId,
      reporting_period: period?.name || '',
      report_type: this.adminReportType,
      sections: ['executive_summary', 'program_performance', 'beneficiary_reach', 'outcomes', 'geographic_distribution'],
      use_ai_insights: true,
    };

    this.http.post(`${environment.apiUrl}/reports/preview`, params).subscribe({
      next: (data: any) => {
        this.adminPreviewData = data;
        this.adminValidationData = data.validation_results;
        this.adminPreviewLoading = false;
      },
      error: () => {
        this.adminPreviewLoading = false;
        this.showToast('Failed to load report preview.', 'danger');
      }
    });
  }

  closeAdminReviewModal(): void {
    this.showAdminReviewModal = false;
    this.adminPreviewData = null;
  }

  generateAndSendToManager(): void {
    if (!this.adminConfirmReviewed || !this.adminConfirmKPIs || !this.adminConfirmWarnings || !this.adminConfirmReady) {
      this.showToast('All 4 confirmation checkboxes must be checked.', 'danger');
      return;
    }
    this.actionLoading = true;
    const period = this.periods.find(p => p.id === this.adminPeriodId);
    const body = {
      title: `${period?.name || 'Report'} ${this.adminReportType}`,
      report_type: this.adminReportType.toLowerCase().replace(/ /g, '_'),
      reporting_period: period?.name || '',
      reporting_period_id: this.adminPeriodId,
      sections: ['executive_summary', 'program_performance', 'beneficiary_reach', 'outcomes', 'geographic_distribution'],
      use_ai_insights: true,
      confirmed_reviewed: this.adminConfirmReviewed,
      confirmed_kpis: this.adminConfirmKPIs,
      confirmed_warnings: this.adminConfirmWarnings,
      confirmed_ready: this.adminConfirmReady,
    };

    this.http.post(`${environment.apiUrl}/reports/generate`, body).subscribe({
      next: () => {
        this.showToast('Report generated and sent to Manager for review.', 'success');
        this.closeAdminReviewModal();
        this.loadReports();
        this.actionLoading = false;
      },
      error: (err: any) => {
        this.actionLoading = false;
        this.showToast(err.error?.detail || 'Failed to generate report.', 'danger');
      }
    });
  }

  // =========================================================================
  // MANAGER VIEW
  // =========================================================================

  viewReport(report: any): void {
    this.selectedReport = report;
    this.showManagerViewModal = true;
    this.managerViewLoading = true;
    this.managerActiveTab = 'summary';

    this.api.getReport(report.id).subscribe({
      next: (data: any) => {
        this.selectedReport = data;
        this.managerViewLoading = false;
      },
      error: () => {
        this.managerViewLoading = false;
        this.showToast('Failed to load report details.', 'danger');
      }
    });
  }

  closeManagerViewModal(): void {
    this.showManagerViewModal = false;
    this.selectedReport = null;
  }

  // =========================================================================
  // APPROVE
  // =========================================================================

  openApproveModal(): void {
    this.showApproveConfirmModal = true;
    this.approvalComment = '';
  }

  closeApproveConfirmModal(): void {
    this.showApproveConfirmModal = false;
    this.approvalComment = '';
  }

  confirmApprove(): void {
    this.actionLoading = true;
    const body = { comment: this.approvalComment || 'Verified and authorized for official reporting.' };
    this.http.post(`${environment.apiUrl}/reports/${this.selectedReport.id}/approve`, body).subscribe({
      next: () => {
        this.showToast('Report approved successfully.', 'success');
        this.closeApproveConfirmModal();
        this.closeManagerViewModal();
        this.loadReports();
        this.actionLoading = false;
      },
      error: (err: any) => {
        this.actionLoading = false;
        this.showToast(err.error?.detail || 'Approval failed.', 'danger');
      }
    });
  }

  // =========================================================================
  // REJECT
  // =========================================================================

  openRejectModal(): void {
    this.showRejectModal = true;
    this.rejectReason = '';
  }

  closeRejectModal(): void {
    this.showRejectModal = false;
    this.rejectReason = '';
  }

  selectPresetRejectReason(reason: string): void {
    this.rejectReason = reason;
  }

  confirmReject(): void {
    if (!this.rejectReason || this.rejectReason.trim().length < 3) return;
    this.actionLoading = true;
    const body = { reason: this.rejectReason, feedback: this.rejectReason };
    this.http.post(`${environment.apiUrl}/reports/${this.selectedReport.id}/reject`, body).subscribe({
      next: () => {
        this.showToast('Report returned for revision.', 'success');
        this.closeRejectModal();
        this.closeManagerViewModal();
        this.loadReports();
        this.actionLoading = false;
      },
      error: (err: any) => {
        this.actionLoading = false;
        this.showToast(err.error?.detail || 'Rejection failed.', 'danger');
      }
    });
  }

  // =========================================================================
  // REVISION
  // =========================================================================

  openReviseModal(report: any): void {
    this.revisingReport = report;
    this.showReviseModal = true;
    this.reviseNotes = '';
  }

  closeReviseModal(): void {
    this.showReviseModal = false;
    this.revisingReport = null;
    this.reviseNotes = '';
  }

  submitRevision(): void {
    this.actionLoading = true;
    const body = { notes: this.reviseNotes || 'Updated figures and revised content.' };
    this.http.post(`${environment.apiUrl}/reports/${this.revisingReport.id}/revise`, body).subscribe({
      next: () => {
        this.showToast(`Version ${(this.revisingReport.version || 1) + 1} generated and submitted.`, 'success');
        this.closeReviseModal();
        this.loadReports();
        this.actionLoading = false;
      },
      error: (err: any) => {
        this.actionLoading = false;
        this.showToast(err.error?.detail || 'Revision failed.', 'danger');
      }
    });
  }

  // =========================================================================
  // DOWNLOADS & PRINT
  // =========================================================================

  downloadReport(reportId: number, format: string, title?: string): void {
    const token = localStorage.getItem('insightflow_token');
    let endpoint = `${environment.apiUrl}/reports/${reportId}/download`;
    if (format === 'pdf') {
      endpoint = `${environment.apiUrl}/reports/${reportId}/download/pdf`;
    } else if (format === 'csv') {
      endpoint = `${environment.apiUrl}/reports/${reportId}/download/csv`;
    } else {
      endpoint = `${environment.apiUrl}/reports/${reportId}/download/excel`;
    }

    fetch(endpoint, { headers: { 'Authorization': `Bearer ${token}` } })
      .then(res => {
        if (!res.ok) throw new Error('Download failed');
        return res.blob();
      })
      .then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        const ext = format === 'pdf' ? 'html' : format === 'csv' ? 'csv' : 'xlsx';
        a.download = `${(title || 'report').replace(/ /g, '_').substring(0, 50)}.${ext}`;
        a.click();
        URL.revokeObjectURL(a.href);
        this.showToast(`${format.toUpperCase()} downloaded successfully.`, 'success');
      })
      .catch(() => this.showToast('Download failed. Make sure the report is completed.', 'danger'));
  }

  printReport(): void {
    window.print();
  }
}
