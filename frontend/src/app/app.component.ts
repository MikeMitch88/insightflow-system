import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

import { ApiService } from './services/api.service';
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

  unreadNotifCount = 0;
  pendingReportsCount = 0;

  private readonly allNavSections: NavSection[] = [
    {
      label: 'Overview',
      items: [
        {
          route: '/dashboard',
          icon: 'dashboard',
          label: 'Dashboard'
        }
      ]
    },
    {
      label: 'Programs',
      items: [
        {
          route: '/program-performance',
          icon: 'analytics',
          label: 'Program Performance'
        },
        {
          route: '/beneficiary-analytics',
          icon: 'groups',
          label: 'Beneficiary Analytics'
        },
        {
          route: '/outcomes',
          icon: 'emoji_events',
          label: 'Outcomes & Impact'
        }
      ]
    },
    {
      label: 'Reporting',
      items: [
        {
          route: '/reports',
          icon: 'insert_chart',
          label: 'Reports'
        },
        {
          route: '/report-builder',
          icon: 'build',
          label: 'Report Builder'
        }
      ]
    },
    {
      label: 'Data',
      items: [
        {
          route: '/data-sources',
          icon: 'storage',
          label: 'Data Sources'
        },
        {
          route: '/data-quality',
          icon: 'verified',
          label: 'Data Quality'
        },
        {
          route: '/data-pipeline',
          icon: 'alt_route',
          label: 'Data Pipeline'
        }
      ]
    },
    {
      label: 'Insights',
      items: [
        {
          route: '/ai-assistant',
          icon: 'psychology',
          label: 'AI Assistant'
        },
        {
          route: '/ai-insights',
          icon: 'auto_awesome',
          label: 'AI Insights'
        }
      ]
    },
    {
      label: 'Administration',
      items: [
        {
          route: '/admin',
          icon: 'settings',
          label: 'Users & Roles'
        }
      ]
    }
  ];

  constructor(
    private readonly router: Router,
    public readonly auth: AuthService,
    private readonly api: ApiService
  ) { }

  ngOnInit(): void {
    this.loadCurrentUser();
    this.listenToRouter();
    this.currentRoute = this.router.url;
  }

  private loadCurrentUser(): void {
    this.auth.currentUser$.subscribe(user => {
      if (!user) {
        this.clearUserData();
        return;
      }


      this.userName = user.name || '';
      this.userEmail = user.email || '';
      this.userRoleLabel = user.role_label || '';

      this.userInitials = this.getInitials(user.name);

      this.filteredNavSections = this.buildFilteredNav(
        user.permissions || [],
        user.role
      );

      this.loadUnreadBadges(user.role);
    });

  }

  private listenToRouter(): void {
    this.router.events
      .pipe(
        filter(
          event => event instanceof NavigationEnd
        )
      )
      .subscribe(event => {
        const navigation = event as NavigationEnd;

        this.currentRoute =
          navigation.urlAfterRedirects || navigation.url;

        const user = this.auth.currentUser;

        if (user) {
          this.loadUnreadBadges(user.role);
        }
      });

  }

  private getInitials(name: string | undefined): string {
    if (!name) {
      return '';
    }

    return name
      .trim()
      .split(/\s+/)
      .map(part => part.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);


  }

  private clearUserData(): void {
    this.userName = '';
    this.userEmail = '';
    this.userInitials = '';
    this.userRoleLabel = '';
    this.filteredNavSections = [];
    this.unreadNotifCount = 0;
    this.pendingReportsCount = 0;
  }

  private loadUnreadBadges(role: string): void {
    this.api.getNotifications(role).subscribe({
      next: (response: any) => {
        this.unreadNotifCount =
          Number(response?.unread_count) || 0;
      },
      error: () => {
        this.unreadNotifCount = 0;
      }
    });

    if (role !== 'program_manager') {
      this.pendingReportsCount = 0;
      return;
    }

    this.api
      .getReports({
        approval_status: 'pending_manager_review'
      })
      .subscribe({
        next: (response: any) => {
          this.pendingReportsCount =
            Number(response?.total) ||
            (Array.isArray(response?.items)
              ? response.items.length
              : 0);
        },
        error: () => {
          this.pendingReportsCount = 0;
        }
      });


  }

  switchRole(
    targetRole: 'admin' | 'program_manager'
  ): void {
    const accounts = {
      admin: {
        email: '[admin@inukafoundation.org](mailto:admin@inukafoundation.org)',
        password: 'Admin@123'
      },
      program_manager: {
        email: '[grace.w@inukafoundation.org](mailto:grace.w@inukafoundation.org)',
        password: 'Admin@123'
      }
    };

    const account = accounts[targetRole];

    this.auth
      .login(account.email, account.password)
      .subscribe({
        next: () => {
          this.router.navigate(['/reports']);
        }
      });
  }

  private buildFilteredNav(
    permissions: string[],
    role: string
  ): NavSection[] {
    if (role === 'admin') {
      return this.allNavSections;
    }

    return this.allNavSections
      .map(section => ({
        ...section,
        items: section.items.filter(item => {
          const page = item.route.substring(1);
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
