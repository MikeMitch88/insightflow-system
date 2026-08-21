import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  currentRoute = '';
  sidebarOpen = true;

  navSections = [
    {
      label: 'Overview',
      items: [
        { route: '/dashboard', icon: 'dashboard', label: 'Dashboard' }
      ]
    },
    {
      label: 'Program Intelligence',
      items: [
        { route: '/program-performance', icon: 'analytics', label: 'Program Performance' },
        { route: '/beneficiary-analytics', icon: 'groups', label: 'Beneficiary Analytics' },
        { route: '/outcomes', icon: 'emoji_events', label: 'Outcomes & Impact' }
      ]
    },
    {
      label: 'Reporting',
      items: [
        { route: '/reports', icon: 'insert_chart', label: 'Reports' },
        { route: '/report-builder', icon: 'build', label: 'Report Builder' }
      ]
    },
    {
      label: 'Data',
      items: [
        { route: '/data-sources', icon: 'database', label: 'Data Sources' },
        { route: '/data-quality', icon: 'verified', label: 'Data Quality' },
        { route: '/data-pipeline', icon: 'alt_route', label: 'Data Pipeline' }
      ]
    },
    {
      label: 'Intelligence',
      items: [
        { route: '/ai-assistant', icon: 'psychology', label: 'AI Assistant' },
        { route: '/ai-insights', icon: 'auto_awesome', label: 'AI Insights' }
      ]
    },
    {
      label: 'Administration',
      items: [
        { route: '/admin', icon: 'settings', label: 'Users & Roles' }
      ]
    }
  ];

  constructor(private router: Router) {}

  ngOnInit(): void {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.currentRoute = event.urlAfterRedirects || event.url;
    });
    this.currentRoute = this.router.url;
  }

  isActive(route: string): boolean {
    return this.currentRoute === route;
  }

  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }
}
