import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent implements OnInit {
  activeTab = 'users';

  users = [
    { name: 'Program Administrator', email: 'admin@inukafoundation.org', role: 'Administrator', status: 'Active', lastActive: '2026-08-20' },
    { name: 'Grace Wanjiku', email: 'grace.w@inukafoundation.org', role: 'Program Manager', status: 'Active', lastActive: '2026-08-19' },
    { name: 'James Otieno', email: 'james.o@inukafoundation.org', role: 'M&E Officer', status: 'Active', lastActive: '2026-08-20' },
    { name: 'Amina Hassan', email: 'amina.h@inukafoundation.org', role: 'Reporting Officer', status: 'Active', lastActive: '2026-08-18' },
    { name: 'David Mwangi', email: 'david.m@inukafoundation.org', role: 'Leadership', status: 'Active', lastActive: '2026-08-15' },
    { name: 'Sarah Njeri', email: 'sarah.n@inukafoundation.org', role: 'Program Manager', status: 'Inactive', lastActive: '2026-07-01' }
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

  ngOnInit(): void {}
}
