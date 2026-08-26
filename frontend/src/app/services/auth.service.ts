import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

export interface UserRole {
  id: number;
  name: string;
  tier: number;
  description: string;
}

export interface UserDepartment {
  id: number;
  name: string;
  code: string;
}

export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole | null;
  department: UserDepartment | null;
  permissions: string[];
}

export interface LoginResponse {
  token: string;
  user: User;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private baseUrl = `${environment.apiUrl}/auth`;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    const stored = localStorage.getItem('insightflow_user');
    if (stored) {
      try {
        this.currentUserSubject.next(JSON.parse(stored));
      } catch {
        localStorage.removeItem('insightflow_user');
      }
    }
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/login`, { email, password }).pipe(
      tap(res => {
        localStorage.setItem('insightflow_token', res.token);
        localStorage.setItem('insightflow_user', JSON.stringify(res.user));
        this.currentUserSubject.next(res.user);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('insightflow_token');
    localStorage.removeItem('insightflow_user');
    this.currentUserSubject.next(null);
  }

  getToken(): string | null {
    return localStorage.getItem('insightflow_token');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  get currentUser(): User | null {
    return this.currentUserSubject.value;
  }

  get userTier(): number {
    return this.currentUser?.role?.tier || 0;
  }

  get userRoleName(): string {
    return this.currentUser?.role?.name || '';
  }

  get userDepartment(): string {
    return this.currentUser?.department?.code || '';
  }

  hasPermission(permission: string): boolean {
    const user = this.currentUser;
    if (!user) return false;
    if (user.role && user.role.tier >= 3) return true;
    return user.permissions.includes(permission);
  }

  hasMinTier(minTier: number): boolean {
    return this.userTier >= minTier;
  }

  canCreateData(): boolean {
    return this.userTier >= 1;
  }

  canVerifyData(): boolean {
    return this.userTier >= 2;
  }

  canGenerateReports(): boolean {
    return this.userTier >= 3;
  }

  canFinalApprove(): boolean {
    return this.userTier >= 4;
  }

  canAccessWorkflowAction(action: string, currentStatus: string): boolean {
    const tier = this.userTier;
    const workflowPermissions: Record<string, Record<string, number[]>> = {
      drafting: { edit: [1, 3], submit_for_review: [1, 3] },
      tier_2_verification: { approve: [2, 3], reject: [2, 3], request_changes: [2, 3] },
      tier_3_assembly: { assemble_report: [3], edit_content: [3], submit_for_final_approval: [3] },
      tier_4_final_sign_off: { approve: [4], reject: [4], request_changes: [4] },
      exported_sent: {},
    };

    const allowedTiers = workflowPermissions[currentStatus]?.[action] || [];
    return allowedTiers.includes(tier);
  }
}
