import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AuthGuard } from './guards/auth.guard';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { ProgramPerformanceComponent } from './pages/program-performance/program-performance.component';
import { BeneficiaryAnalyticsComponent } from './pages/beneficiary-analytics/beneficiary-analytics.component';
import { OutcomesComponent } from './pages/outcomes/outcomes.component';
import { ReportsComponent } from './pages/reports/reports.component';
import { ReportBuilderComponent } from './pages/report-builder/report-builder.component';
import { DataSourcesComponent } from './pages/data-sources/data-sources.component';
import { DataQualityComponent } from './pages/data-quality/data-quality.component';
import { DataPipelineComponent } from './pages/data-pipeline/data-pipeline.component';
import { AiAssistantComponent } from './pages/ai-assistant/ai-assistant.component';
import { AiInsightsComponent } from './pages/ai-insights/ai-insights.component';
import { AdminComponent } from './pages/admin/admin.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'program-performance', component: ProgramPerformanceComponent, canActivate: [AuthGuard] },
  { path: 'beneficiary-analytics', component: BeneficiaryAnalyticsComponent, canActivate: [AuthGuard] },
  { path: 'outcomes', component: OutcomesComponent, canActivate: [AuthGuard] },
  { path: 'reports', component: ReportsComponent, canActivate: [AuthGuard] },
  { path: 'report-builder', component: ReportBuilderComponent, canActivate: [AuthGuard] },
  { path: 'data-sources', component: DataSourcesComponent, canActivate: [AuthGuard] },
  { path: 'data-quality', component: DataQualityComponent, canActivate: [AuthGuard] },
  { path: 'data-pipeline', component: DataPipelineComponent, canActivate: [AuthGuard] },
  { path: 'ai-assistant', component: AiAssistantComponent, canActivate: [AuthGuard] },
  { path: 'ai-insights', component: AiInsightsComponent, canActivate: [AuthGuard] },
  { path: 'admin', component: AdminComponent, canActivate: [AuthGuard] },
  { path: '**', redirectTo: 'dashboard' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
