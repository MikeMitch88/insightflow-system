import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';

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

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    ProgramPerformanceComponent,
    BeneficiaryAnalyticsComponent,
    OutcomesComponent,
    ReportsComponent,
    ReportBuilderComponent,
    DataSourcesComponent,
    DataQualityComponent,
    DataPipelineComponent,
    AiAssistantComponent,
    AiInsightsComponent,
    AdminComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}
