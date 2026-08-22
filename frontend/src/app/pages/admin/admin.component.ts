import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent implements OnInit {
  activeTab = 'users';
  selectedUser: any = null;

  rolePermissions: Record<string, string[]> = {
    admin: [
      'dashboard', 'program-performance', 'beneficiary-analytics', 'outcomes',
      'reports', 'report-builder', 'data-sources', 'data-quality', 'data-pipeline',
      'ai-assistant', 'ai-insights', 'admin'
    ],
    program_manager: [
      'dashboard', 'program-performance', 'beneficiary-analytics', 'outcomes',
      'reports', 'report-builder', 'ai-assistant', 'ai-insights'
    ],
    me_officer: [
      'dashboard', 'program-performance', 'beneficiary-analytics', 'outcomes',
      'data-quality', 'data-pipeline', 'ai-assistant', 'ai-insights'
    ],
    reporting_officer: [
      'dashboard', 'program-performance', 'beneficiary-analytics', 'outcomes',
      'reports', 'report-builder', 'data-sources', 'data-quality', 'data-pipeline',
      'ai-assistant'
    ],
    leadership: [
      'dashboard', 'program-performance', 'beneficiary-analytics', 'outcomes',
      'reports', 'ai-assistant', 'ai-insights'
    ]
  };

  pageLabels: Record<string, string> = {
    'dashboard': 'Dashboard',
    'program-performance': 'Program Performance',
    'beneficiary-analytics': 'Beneficiary Analytics',
    'outcomes': 'Outcomes & Impact',
    'reports': 'Reports',
    'report-builder': 'Report Builder',
    'data-sources': 'Data Sources',
    'data-quality': 'Data Quality',
    'data-pipeline': 'Data Pipeline',
    'ai-assistant': 'AI Assistant',
    'ai-insights': 'AI Insights',
    'admin': 'Users & Roles'
  };

  users = [
    { id: 1, name: 'Program Administrator', email: 'admin@inukafoundation.org', role: 'Administrator', roleKey: 'admin', status: 'Active', lastActive: '2026-08-20' },
    { id: 2, name: 'Grace Wanjiku', email: 'grace.w@inukafoundation.org', role: 'Program Manager', roleKey: 'program_manager', status: 'Active', lastActive: '2026-08-19' },
    { id: 3, name: 'James Otieno', email: 'james.o@inukafoundation.org', role: 'M&E Officer', roleKey: 'me_officer', status: 'Active', lastActive: '2026-08-20' },
    { id: 4, name: 'Amina Hassan', email: 'amina.h@inukafoundation.org', role: 'Reporting Officer', roleKey: 'reporting_officer', status: 'Active', lastActive: '2026-08-18' },
    { id: 5, name: 'David Mwangi', email: 'david.m@inukafoundation.org', role: 'Leadership', roleKey: 'leadership', status: 'Active', lastActive: '2026-08-15' },
    { id: 6, name: 'Sarah Njeri', email: 'sarah.n@inukafoundation.org', role: 'Program Manager', roleKey: 'program_manager', status: 'Inactive', lastActive: '2026-07-01' }
  ];

  auditLogs = [
    { timestamp: '2026-08-20 14:32', user: 'Program Administrator', action: 'Generated Executive Report', details: 'Q3 2026 Executive Summary' },
    { timestamp: '2026-08-20 10:15', user: 'James Otieno', action: 'Updated Data Quality Rules', details: 'Added validation for phone numbers' },
    { timestamp: '2026-08-19 16:45', user: 'Grace Wanjiku', action: 'Generated Program Report', details: 'Scholarship Performance Q3 2026' },
    { timestamp: '2026-08-19 09:20', user: 'Amina Hassan', action: 'Exported Donor Report', details: 'Quarterly Donor Update Q2 2026' },
    { timestamp: '2026-08-18 11:00', user: 'Program Administrator', action: 'Ran Data Pipeline', details: 'Full ETL run completed successfully' },
    { timestamp: '2026-08-15 14:30', user: 'David Mwangi', action: 'Reviewed Dashboard', details: 'Q3 2026 Executive Overview' }
  ];

  settings = {
    orgName: 'KPC Inuka Foundation',
    reportingFrequency: 'quarterly',
    emailNotifications: true,
    defaultPeriod: 'Q3 2026'
  };

  constructor(private api: ApiService) {}

  ngOnInit(): void {}

  getUserPermissions(user: any): string[] {
    return this.rolePermissions[user.roleKey] || [];
  }

  getPermissionCount(user: any): number {
    return this.getUserPermissions(user).length;
  }

  viewPermissions(user: any): void {
    this.selectedUser = this.selectedUser?.id === user.id ? null : user;
  }

  getPageLabel(page: string): string {
    return this.pageLabels[page] || page;
  }

  getAllPages(): string[] {
    return Object.keys(this.pageLabels);
  }
}
