import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { AuthService } from './services/auth.service';

interface NavItem {
  route: string;
  icon: string;
  label: string;
  minTier?: number;
}

interface NavSection {
  label: string;
  items: NavItem[];
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  currentRoute = '';
  sidebarOpen = true;
  userName = '';
  userEmail = '';
  userInitials = '';
  userRoleLabel = '';
  userTierLabel = '';
  filteredNavSections: NavSection[] = [];

  private allNavSections: NavSection[] = [
    {
      label: 'Overview',
      items: [
        { route: '/dashboard', icon: 'dashboard', label: 'Dashboard', minTier: 1 }
      ]
    },
    {
      label: 'Programs',
      items: [
        { route: '/program-performance', icon: 'analytics', label: 'Program Performance', minTier: 1 },
        { route: '/beneficiary-analytics', icon: 'groups', label: 'Beneficiary Analytics', minTier: 1 },
        { route: '/outcomes', icon: 'emoji_events', label: 'Outcomes & Impact', minTier: 1 }
      ]
    },
    {
      label: 'Data Collection',
      items: [
        { route: '/cross-pillar-forms', icon: 'dynamic_form', label: 'Cross-Pillar Forms', minTier: 1 },
        { route: '/data-sources', icon: 'storage', label: 'Data Sources', minTier: 1 },
        { route: '/data-quality', icon: 'verified', label: 'Data Quality', minTier: 2 },
        { route: '/data-pipeline', icon: 'alt_route', label: 'Data Pipeline', minTier: 2 }
      ]
    },
    {
      label: 'Reporting',
      items: [
        { route: '/reports', icon: 'insert_chart', label: 'Reports', minTier: 1 },
        { route: '/report-builder', icon: 'build', label: 'Report Builder', minTier: 2 },
        { route: '/donor-report-builder', icon: 'auto_awesome', label: 'AI Donor Reports', minTier: 3 },
        { route: '/workflow', icon: 'account_tree', label: 'Approval Workflow', minTier: 2 }
      ]
    },
    {
      label: 'Insights',
      items: [
        { route: '/ai-assistant', icon: 'psychology', label: 'AI Assistant', minTier: 2 },
        { route: '/ai-insights', icon: 'auto_awesome', label: 'AI Insights', minTier: 1 }
      ]
    },
    {
      label: 'Administration',
      items: [
        { route: '/admin', icon: 'settings', label: 'Users & Roles', minTier: 3 },
        { route: '/audit-trail', icon: 'history', label: 'Audit Trail', minTier: 2 }
      ]
    }
  ];

  constructor(private router: Router, public auth: AuthService) {}

  ngOnInit(): void {
    this.auth.currentUser$.subscribe(user => {
      if (user) {
        this.userName = user.name;
        this.userEmail = user.email;
        this.userRoleLabel = user.role?.name?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || '';
        this.userTierLabel = user.role ? `Tier ${user.role.tier}` : '';
        this.userInitials = user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        this.filteredNavSections = this.buildFilteredNav(user);
      } else {
        this.filteredNavSections = [];
      }
    });
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.currentRoute = event.urlAfterRedirects || event.url;
    });
    this.currentRoute = this.router.url;
  }

  private buildFilteredNav(user: any): NavSection[] {
    const tier = user.role?.tier || 0;
    return this.allNavSections
      .map(section => ({
        ...section,
        items: section.items.filter(item => {
          const minTier = item.minTier || 1;
          return tier >= minTier;
        })
      }))
      .filter(section => section.items.length > 0);
  }

  isActive(route: string): boolean {
    return this.currentRoute === route;
  }

  isLoggedIn(): boolean {
    return this.auth.isLoggedIn();
  }

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }

  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }
}
