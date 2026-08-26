import {
  Component,
  OnDestroy,
  OnInit
} from '@angular/core';

import { Subject, forkJoin, of } from 'rxjs';
import {
  catchError,
  finalize,
  takeUntil
} from 'rxjs/operators';

import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

interface Period {
  id: number;
  name?: string;
  label?: string;
  is_current?: boolean;
}

interface DashboardSummary {
  total_beneficiaries: number;
  active_beneficiaries: number;
  completion_rate: number;
  program_count: number;
  counties_reached: number;
  data_quality_score: number;
  total_enrolled: number;
  [key: string]: any;
}

interface Trend {
  period: string;
  beneficiary_count: number;
  enrollment_count: number;
  [key: string]: any;
}

interface Program {
  program_name: string;
  total_enrolled: number;
  completion_rate: number;
  avg_attendance_rate: number;
  [key: string]: any;
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent
  implements OnInit, OnDestroy {

  summary: DashboardSummary = {
    total_beneficiaries: 0,
    active_beneficiaries: 0,
    completion_rate: 0,
    program_count: 0,
    counties_reached: 0,
    data_quality_score: 0,
    total_enrolled: 0
  };

  trends: Trend[] = [];
  programs: Program[] = [];
  periods: Period[] = [];

  selectedPeriod: number | null = null;

  loading = true;
  errorMessage = '';

  pendingReviewsCount = 0;

  programColors: Record<string, string> = {
    Scholarship: '#e92134',
    Plus: '#1f1f1f',
    Vocational: '#7d7d7d',
    Tech: '#bd1020'
  };

  private destroy$ = new Subject<void>();

  constructor(
    private api: ApiService,
    public auth: AuthService
  ) { }

  ngOnInit(): void {
    this.loadPeriods();
    this.checkManagerPendingQueue();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadPeriods(): void {
    this.loading = true;

    this.api
      .getPeriods()
      .pipe(
        takeUntil(this.destroy$),
        catchError(() => {
          this.periods = [];
          return of([]);
        })
      )
      .subscribe({
        next: (data: any) => {
          this.periods =
            this.normalizeArray<Period>(data);

          const currentPeriod =
            this.periods.find(
              period => period.is_current === true
            );

          if (currentPeriod) {
            this.selectedPeriod =
              currentPeriod.id;
          } else if (this.periods.length > 0) {
            this.selectedPeriod =
              this.periods[0].id;
          }

          this.loadData();
        }
      });
  }

  loadData(): void {
    this.loading = true;
    this.errorMessage = '';

    const period =
      this.selectedPeriod ?? undefined;

    forkJoin({
      summary: this.api
        .getDashboardSummary(period)
        .pipe(
          catchError(() =>
            of({
              total_beneficiaries: 0,
              active_beneficiaries: 0,
              completion_rate: 0,
              program_count: 0,
              counties_reached: 0,
              data_quality_score: 0,
              total_enrolled: 0
            })
          )
        ),

      trends: this.api
        .getDashboardTrends()
        .pipe(
          catchError(() => of([]))
        ),

      programs: this.api
        .getProgramPerformance(period)
        .pipe(
          catchError(() => of([]))
        )
    })
      .pipe(
        takeUntil(this.destroy$),
        finalize(() => {
          this.loading = false;
        })
      )
      .subscribe({
        next: (result: any) => {
          this.summary = {
            total_beneficiaries:
              Number(
                result.summary
                  ?.total_beneficiaries
              ) || 0,

            active_beneficiaries:
              Number(
                result.summary
                  ?.active_beneficiaries
              ) || 0,

            completion_rate:
              Number(
                result.summary
                  ?.completion_rate
              ) || 0,

            program_count:
              Number(
                result.summary
                  ?.program_count
              ) || 0,

            counties_reached:
              Number(
                result.summary
                  ?.counties_reached
              ) || 0,

            data_quality_score:
              Number(
                result.summary
                  ?.data_quality_score
              ) || 0,

            total_enrolled:
              Number(
                result.summary
                  ?.total_enrolled
              ) || 0,

            ...result.summary
          };

          this.trends =
            this.normalizeArray<Trend>(
              result.trends
            ).map((trend: any) => ({
              ...trend,
              period:
                trend.period ??
                trend.period_name ??
                '',
              beneficiary_count:
                Number(
                  trend.beneficiary_count
                ) || 0,
              enrollment_count:
                Number(
                  trend.enrollment_count
                ) || 0
            }));

          this.programs =
            this.normalizeArray<Program>(
              result.programs
            ).map((program: any) => ({
              ...program,
              program_name:
                program.program_name ??
                program.name ??
                '',
              total_enrolled:
                Number(
                  program.total_enrolled
                ) || 0,
              completion_rate:
                Number(
                  program.completion_rate
                ) || 0,
              avg_attendance_rate:
                Number(
                  program.avg_attendance_rate
                ) || 0
            }));
        },

        error: () => {
          this.errorMessage =
            'Unable to load dashboard data. Please try again.';
        }
      });
  }

  onPeriodChange(): void {
    this.loadData();
  }

  private checkManagerPendingQueue(): void {
    const user =
      this.auth.currentUser;

    if (
      !user ||
      user.role !== 'program_manager'
    ) {
      this.pendingReviewsCount = 0;
      return;
    }

    this.api
      .getReports({
        approval_status:
          'pending_manager_review'
      })
      .pipe(
        takeUntil(this.destroy$),
        catchError(() =>
          of({
            total: 0,
            items: []
          })
        )
      )
      .subscribe({
        next: (response: any) => {
          this.pendingReviewsCount =
            Number(response?.total) ||
            (Array.isArray(response?.items)
              ? response.items.length
              : 0);
        }
      });
  }

  getMaxTrend(): number {
    if (this.trends.length === 0) {
      return 1;
    }

    const values =
      this.trends.map(trend =>
        Math.max(
          Number(
            trend.beneficiary_count
          ) || 0,
          Number(
            trend.enrollment_count
          ) || 0
        )
      );

    return Math.max(...values, 1);
  }

  getMaxProgram(): number {
    if (this.programs.length === 0) {
      return 1;
    }

    const values =
      this.programs.map(program =>
        Number(
          program.total_enrolled
        ) || 0
      );

    return Math.max(...values, 1);
  }

  getTrendPercentage(
    value: number
  ): number {
    const max =
      this.getMaxTrend();

    if (max <= 0) {
      return 0;
    }

    return Math.min(
      100,
      Math.max(
        0,
        (value / max) * 100
      )
    );
  }

  getProgramPercentage(
    value: number
  ): number {
    const max =
      this.getMaxProgram();

    if (max <= 0) {
      return 0;
    }

    return Math.min(
      100,
      Math.max(
        0,
        (value / max) * 100
      )
    );
  }

  getProgramColor(
    programName: string
  ): string {
    return (
      this.programColors[programName] ||
      '#666666'
    );
  }

  formatNumber(
    value: number
  ): string {
    return new Intl.NumberFormat().format(
      Number(value) || 0
    );
  }

  isProgramManager(): boolean {
    return (
      this.auth.currentUser?.role ===
      'program_manager'
    );
  }

  refresh(): void {
    this.checkManagerPendingQueue();
    this.loadData();
  }

  private normalizeArray<T>(
    data: any
  ): T[] {
    if (Array.isArray(data)) {
      return data as T[];
    }

    if (Array.isArray(data?.items)) {
      return data.items as T[];
    }

    if (Array.isArray(data?.results)) {
      return data.results as T[];
    }

    return [];
  }
}