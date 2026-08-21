import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

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
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'program-performance', component: ProgramPerformanceComponent },
  { path: 'beneficiary-analytics', component: BeneficiaryAnalyticsComponent },
  { path: 'outcomes', component: OutcomesComponent },
  { path: 'reports', component: ReportsComponent },
  { path: 'report-builder', component: ReportBuilderComponent },
  { path: 'data-sources', component: DataSourcesComponent },
  { path: 'data-quality', component: DataQualityComponent },
  { path: 'data-pipeline', component: DataPipelineComponent },
  { path: 'ai-assistant', component: AiAssistantComponent },
  { path: 'ai-insights', component: AiInsightsComponent },
  { path: 'admin', component: AdminComponent },
  { path: '**', redirectTo: 'dashboard' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
