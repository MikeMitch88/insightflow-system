import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { AuthService } from './services/auth.service';

interface NavItem {
  route: string;
  icon: string;
  label: string;
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
  filteredNavSections: NavSection[] = [];

  private allNavSections: NavSection[] = [
    {
      label: 'Overview',
      items: [
        { route: '/dashboard', icon: 'dashboard', label: 'Dashboard' }
      ]
    },
    {
      label: 'Programs',
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
        { route: '/data-sources', icon: 'storage', label: 'Data Sources' },
        { route: '/data-quality', icon: 'verified', label: 'Data Quality' },
        { route: '/data-pipeline', icon: 'alt_route', label: 'Data Pipeline' }
      ]
    },
    {
      label: 'Insights',
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

  constructor(private router: Router, public auth: AuthService) {}

  ngOnInit(): void {
    this.auth.currentUser$.subscribe(user => {
      if (user) {
        this.userName = user.name;
        this.userEmail = user.email;
        this.userRoleLabel = user.role_label;
        this.userInitials = user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        this.filteredNavSections = this.buildFilteredNav(user.permissions, user.role);
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

  private buildFilteredNav(permissions: string[], role: string): NavSection[] {
    if (role === 'admin') return this.allNavSections;
    return this.allNavSections
      .map(section => ({
        ...section,
        items: section.items.filter(item => {
          const page = item.route.replace('/', '');
          return permissions.includes(page);
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
