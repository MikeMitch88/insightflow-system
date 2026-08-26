import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { AuthService, User } from '../../services/auth.service';

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
  periods: any[] = [];

  currentUser: User | null = null;
  isAdmin = true;
  isManager = false;

  // Summary Metrics
  summaryStats = {
    total: 0,
    approved: 0,
    pendingReview: 0,
    rejected: 0,
    readinessScore: 96.0
  };

  // =========================================================================
  // ADMIN WORKFLOW STATE
  // =========================================================================
  adminPeriod = 'August 2026';
  adminPeriodId: number | null = 7;
  adminReportType = 'Monthly Donor Report';

  reportTypes = [
    { value: 'Monthly Donor Report', label: 'Monthly Donor Report' },
    { value: 'Executive Summary', label: 'Executive Summary Report' },
    { value: 'Program Performance Report', label: 'Program Performance Report' },
    { value: 'Inuka Cross-Pillar Impact Report', label: 'Inuka Cross-Pillar Impact Report' },
    { value: 'M&E Milestone Report', label: 'M&E Milestone Report' }
  ];

  // Admin Review / Preview Modal
  showAdminReviewModal = false;
  adminPreviewLoading = false;
  adminPreviewData: any = null;
  adminValidationData: any = null;
  adminActiveTab: 'summary' | 'pillars' | 'kpc_log' | 'outcomes' | 'quality' | 'ai_insights' | 'validation' = 'summary';

  // Admin 4 Confirmation Checkboxes
  adminConfirmReviewed = false;
  adminConfirmKPIs = false;
  adminConfirmWarnings = false;
  adminConfirmReady = false;

  // Admin Validation Modal
  showAdminValidateModal = false;
  validationRunning = false;

  // Admin Revision Modal
  showReviseModal = false;
  revisingReport: any = null;
  reviseNotes = '';

  // =========================================================================
  // MANAGER WORKFLOW STATE
  // =========================================================================
  showManagerViewModal = false;
  managerViewLoading = false;
  selectedReport: any = null;
  managerActiveTab: 'summary' | 'pillars' | 'kpc_log' | 'outcomes' | 'quality' | 'ai_insights' | 'validation' | 'timeline' = 'summary';

  // Manager Approval Confirmation Modal
  showApproveConfirmModal = false;
  approvalComment = 'Verified against field registers and approved for official donor submission.';

  // Manager Rejection Modal (Requires Mandatory Reason)
  showRejectModal = false;
  rejectReason = '';
  rejectFeedback = '';
  rejectionReasonsList = [
    'Vocational completion figures require verification with Nakuru training center',
    'Session attendance data inconsistency in Tech Innovation hub',
    'Missing post-program outcome survey records for August cohort',
    'Discrepancy in beneficiary enrollment numbers vs digital registers',
    'Other (specified in feedback)'
  ];

  // Common UI State
  actionLoading = false;
  toastMessage: string | null = null;
  toastType: 'success' | 'danger' | 'info' = 'success';

  constructor(
    private api: ApiService,
    public auth: AuthService
  ) {}

  ngOnInit(): void {
    this.auth.currentUser$.subscribe(user => {
      this.currentUser = user;
      this.checkRolePermissions();
    });
    this.loadPeriods();
    this.loadReports();
    this.loadReadiness();
  }

  checkRolePermissions(): void {
    if (!this.currentUser) {
      this.isAdmin = true;
      this.isManager = false;
      return;
    }
    const role = this.currentUser.role.toLowerCase();
    this.isAdmin = (role === 'admin' || role === 'reporting_officer');
    this.isManager = (role === 'program_manager');
  }

  loadPeriods(): void {
    this.api.getPeriods().subscribe({
      next: (data: any) => {
        this.periods = data.items || (Array.isArray(data) ? data : []);
        if (this.periods.length) {
          const current = this.periods.find((p: any) => p.is_current) || this.periods[this.periods.length - 1];
          this.adminPeriodId = current.id;
          this.adminPeriod = current.display_name ? current.display_name.split(' (')[0] : (current.month_name || current.name);
        }
      }
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
        this.reports = data.items || data || [];
        this.totalReports = data.total || this.reports.length;
        this.calculateSummaryStats();
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  loadReadiness(periodId?: number): void {
    this.api.getReportReadiness(periodId).subscribe({
      next: (data: any) => {
        this.summaryStats.readinessScore = data.overall_completeness || 96.0;
      }
    });
  }

  calculateSummaryStats(): void {
    this.summaryStats.total = this.totalReports;
    let approved = 0;
    let pending = 0;
    let rejected = 0;

    for (const r of this.reports) {
      const st = (r.status || r.approval_status || '').toUpperCase();
      if (st.includes('APPROVED')) {
        approved++;
      } else if (st.includes('REVISION') || st.includes('REJECTED')) {
        rejected++;
      } else {
        pending++;
      }
    }

    this.summaryStats.approved = approved;
    this.summaryStats.pendingReview = pending;
    this.summaryStats.rejected = rejected;
  }

  get pendingReviewReports(): any[] {
    return this.reports.filter(r => {
      const st = (r.status || '').toUpperCase();
      return st === 'PENDING_MANAGER_REVIEW' || st === 'PENDING_REVIEW' || st === 'UNDER_REVIEW';
    });
  }

  onSearch(): void {
    this.page = 1;
    this.loadReports();
  }

  onFilterChange(): void {
    this.page = 1;
    this.loadReports();
  }

  nextPage(): void {
    this.page++;
    this.loadReports();
  }

  prevPage(): void {
    if (this.page > 1) {
      this.page--;
      this.loadReports();
    }
  }

  refreshReports(): void {
    this.loadReports();
    this.loadReadiness(this.adminPeriodId || undefined);
    this.showToast('Reports refreshed successfully', 'info');
  }

  // =========================================================================
  // ADMIN ACTIONS: REVIEW REPORT, VALIDATE, GENERATE
  // =========================================================================

  onAdminPeriodSelect(event: any): void {
    const selectedId = Number(event.target.value);
    this.adminPeriodId = selectedId;
    const p = this.periods.find((x: any) => x.id === selectedId);
    if (p) {
      this.adminPeriod = p.display_name ? p.display_name.split(' (')[0] : (p.month_name || p.name);
    }
  }

  openReviewReport(): void {
    this.showAdminReviewModal = true;
    this.adminPreviewLoading = true;
    this.resetAdminConfirmations();
    this.adminActiveTab = 'summary';

    this.api.previewReport({
      reporting_period: this.adminPeriod,
      reporting_period_id: this.adminPeriodId,
      report_type: this.adminReportType,
      sections: ['executive_summary', 'pillars', 'kpc_log', 'outcomes', 'data_quality', 'ai_insights']
    }).subscribe({
      next: (data: any) => {
        this.adminPreviewData = data;
        this.adminValidationData = data.validation_results;
        this.adminPreviewLoading = false;
      },
      error: () => {
        this.adminPreviewLoading = false;
        this.showToast('Failed to load report preview. Please try again.', 'danger');
      }
    });
  }

  closeAdminReviewModal(): void {
    this.showAdminReviewModal = false;
    this.adminPreviewData = null;
    this.resetAdminConfirmations();
  }

  openValidateOnly(): void {
    this.showAdminValidateModal = true;
    this.validationRunning = true;

    this.api.validateReport({
      reporting_period: this.adminPeriod,
      reporting_period_id: this.adminPeriodId,
      report_type: this.adminReportType
    }).subscribe({
      next: (data: any) => {
        this.adminValidationData = data;
        this.validationRunning = false;
      },
      error: () => {
        this.validationRunning = false;
        this.showToast('Validation service failed.', 'danger');
      }
    });
  }

  closeAdminValidateModal(): void {
    this.showAdminValidateModal = false;
  }

  resetAdminConfirmations(): void {
    this.adminConfirmReviewed = false;
    this.adminConfirmKPIs = false;
    this.adminConfirmWarnings = false;
    this.adminConfirmReady = false;
  }

  get isGenerationReady(): boolean {
    return (
      this.adminConfirmReviewed &&
      this.adminConfirmKPIs &&
      this.adminConfirmWarnings &&
      this.adminConfirmReady &&
      (!this.adminValidationData || this.adminValidationData.can_generate !== false)
    );
  }

  generateAndSendToManager(): void {
    if (!this.isGenerationReady) return;
    this.actionLoading = true;

    const title = `${this.adminPeriod} ${this.adminReportType}`;

    this.api.generateReport({
      title: title,
      report_type: this.adminReportType,
      reporting_period: this.adminPeriod,
      reporting_period_id: this.adminPeriodId,
      sections: ['executive_summary', 'pillars', 'kpc_log', 'outcomes', 'data_quality', 'ai_insights'],
      use_ai_insights: true,
      confirmed_reviewed: this.adminConfirmReviewed,
      confirmed_kpis: this.adminConfirmKPIs,
      confirmed_warnings: this.adminConfirmWarnings,
      confirmed_ready: this.adminConfirmReady
    }).subscribe({
      next: (res: any) => {
        this.actionLoading = false;
        this.closeAdminReviewModal();
        this.showToast(`Report '${title}' generated and sent to Manager for review!`, 'success');
        this.loadReports();
      },
      error: (err: any) => {
        this.actionLoading = false;
        const msg = err?.error?.detail || 'Report generation failed. Please check validation warnings.';
        this.showToast(msg, 'danger');
      }
    });
  }

  // =========================================================================
  // ADMIN REVISION WORKFLOW
  // =========================================================================

  openReviseModal(report: any): void {
    this.revisingReport = report;
    this.reviseNotes = `Addressed feedback: ${report.rejection_reason || ''}`;
    this.showReviseModal = true;
  }

  closeReviseModal(): void {
    this.showReviseModal = false;
    this.revisingReport = null;
    this.reviseNotes = '';
  }

  submitRevision(): void {
    if (!this.revisingReport) return;
    this.actionLoading = true;

    this.api.reviseReport(this.revisingReport.id, { notes: this.reviseNotes }).subscribe({
      next: (res: any) => {
        this.actionLoading = false;
        this.closeReviseModal();
        this.showToast(`Version ${res.version} created and sent to Manager!`, 'success');
        this.loadReports();
      },
      error: () => {
        this.actionLoading = false;
        this.showToast('Revision submission failed.', 'danger');
      }
    });
  }

  // =========================================================================
  // MANAGER ACTIONS: VIEW REPORT, APPROVE, REJECT
  // =========================================================================

  viewReport(report: any): void {
    this.selectedReport = report;
    this.showManagerViewModal = true;
    this.managerViewLoading = true;
    this.managerActiveTab = 'summary';

    this.api.getReportPreview(report.id).subscribe({
      next: (data: any) => {
        this.selectedReport = {
          ...this.selectedReport,
          ...data,
          snapshot: data.snapshot || data.report_snapshot || data
        };
        this.managerViewLoading = false;
      },
      error: () => {
        this.managerViewLoading = false;
        this.showToast('Could not load complete report details.', 'danger');
      }
    });
  }

  closeManagerViewModal(): void {
    this.showManagerViewModal = false;
    this.selectedReport = null;
  }

  openApproveModal(report?: any): void {
    if (report) this.selectedReport = report;
    this.approvalComment = 'Verified against field registers and approved for official donor submission.';
    this.showApproveConfirmModal = true;
  }

  closeApproveConfirmModal(): void {
    this.showApproveConfirmModal = false;
  }

  confirmApprove(): void {
    if (!this.selectedReport) return;
    this.actionLoading = true;

    this.api.approveReport(this.selectedReport.id, { comment: this.approvalComment }).subscribe({
      next: (updated: any) => {
        this.actionLoading = false;
        this.closeApproveConfirmModal();
        this.closeManagerViewModal();
        this.showToast(`Report '${this.selectedReport.title}' has been APPROVED!`, 'success');
        this.loadReports();
      },
      error: (err: any) => {
        this.actionLoading = false;
        const msg = err?.error?.detail || 'Approval failed. Only Manager has authorization.';
        this.showToast(msg, 'danger');
      }
    });
  }

  openRejectModal(report?: any): void {
    if (report) this.selectedReport = report;
    this.rejectReason = '';
    this.rejectFeedback = '';
    this.showRejectModal = true;
  }

  closeRejectModal(): void {
    this.showRejectModal = false;
    this.rejectReason = '';
    this.rejectFeedback = '';
  }

  confirmReject(): void {
    if (!this.selectedReport) return;
    if (!this.rejectReason || this.rejectReason.trim().length < 3) {
      this.showToast('Please provide a mandatory reason for rejection.', 'danger');
      return;
    }

    this.actionLoading = true;
    this.api.rejectReport(this.selectedReport.id, {
      reason: this.rejectReason.trim(),
      feedback: this.rejectFeedback.trim() || this.rejectReason.trim()
    }).subscribe({
      next: (updated: any) => {
        this.actionLoading = false;
        this.closeRejectModal();
        this.closeManagerViewModal();
        this.showToast(`Report returned to Admin with status REVISION_REQUIRED.`, 'info');
        this.loadReports();
      },
      error: (err: any) => {
        this.actionLoading = false;
        const msg = err?.error?.detail || 'Rejection failed.';
        this.showToast(msg, 'danger');
      }
    });
  }

  selectPresetRejectReason(reason: string): void {
    this.rejectReason = reason;
  }

  // =========================================================================
  // DOWNLOADS & HELPERS
  // =========================================================================

  downloadReport(reportId: number, format: string, title?: string): void {
    const token = localStorage.getItem('insightflow_token');
    const headers: any = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const url = `http://localhost:8000/api/reports/${reportId}/download/${format}`;
    const safeTitle = (title || `report_${reportId}`).replace(/[^a-zA-Z0-9_-]/g, '_');

    fetch(url, { headers })
      .then(res => {
        if (!res.ok) throw new Error('Download failed');
        return res.blob();
      })
      .then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        const ext = format === 'pdf' ? 'html' : format;
        a.download = `${safeTitle}.${ext}`;
        a.click();
        URL.revokeObjectURL(a.href);
        this.showToast(`Downloaded ${safeTitle}.${ext}`, 'success');
      })
      .catch(() => {
        this.showToast(`Download failed. Please ensure the backend is running.`, 'danger');
      });
  }

  printReport(): void {
    window.print();
  }

  getStatusBadgeClass(status: string): string {
    const st = (status || '').toUpperCase();
    if (st.includes('APPROVED')) return 'badge-approved';
    if (st.includes('REVISION') || st.includes('REJECTED')) return 'badge-rejected';
    if (st.includes('PENDING') || st.includes('REVIEW')) return 'badge-review';
    return 'badge-draft-chip';
  }

  getStatusDisplay(status: string): string {
    const st = (status || '').toUpperCase();
    if (st === 'PENDING_MANAGER_REVIEW') return 'PENDING MANAGER REVIEW';
    if (st === 'REVISION_REQUIRED') return 'REVISION REQUIRED';
    if (st === 'APPROVED') return 'APPROVED';
    if (st === 'ADMIN_REVIEW') return 'ADMIN REVIEW';
    return st.replace(/_/g, ' ');
  }

  showToast(message: string, type: 'success' | 'danger' | 'info' = 'success'): void {
    this.toastMessage = message;
    this.toastType = type;
    setTimeout(() => {
      if (this.toastMessage === message) {
        this.toastMessage = null;
      }
    }, 4500);
  }
}
