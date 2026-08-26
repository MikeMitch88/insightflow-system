import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-cross-pillar-forms',
  templateUrl: './cross-pillar-forms.component.html',
  styleUrls: ['./cross-pillar-forms.component.css']
})
export class CrossPillarFormsComponent implements OnInit {
  projects: any[] = [];
  kpiMetrics: any[] = [];
  financialItems: any[] = [];
  risks: any[] = [];
  fieldNotes: any[] = [];
  activeTab = 'kpi';
  showForm = false;
  loading = true;
  submitting = false;

  kpiForm: FormGroup;
  financialForm: FormGroup;
  riskForm: FormGroup;
  fieldNoteForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    public auth: AuthService
  ) {
    this.kpiForm = this.fb.group({
      project_id: [null, Validators.required],
      kpi_name: ['', Validators.required],
      kpi_category: [''],
      target_value: [0, [Validators.required, Validators.min(0)]],
      actual_value: [0, [Validators.required, Validators.min(0)]],
      unit: [''],
      notes: ['']
    });

    this.financialForm = this.fb.group({
      project_id: [null, Validators.required],
      line_item: ['', Validators.required],
      category: [''],
      budget_amount: [0, [Validators.required, Validators.min(0)]],
      actual_spend: [0, [Validators.required, Validators.min(0)]],
      currency: ['USD'],
      notes: ['']
    });

    this.riskForm = this.fb.group({
      project_id: [null, Validators.required],
      risk_title: ['', Validators.required],
      risk_category: [''],
      severity: ['medium', Validators.required],
      likelihood: ['medium'],
      impact: ['medium'],
      mitigation_strategy: ['']
    });

    this.fieldNoteForm = this.fb.group({
      project_id: [null, Validators.required],
      title: ['', Validators.required],
      content: ['', Validators.required],
      note_type: ['program_update'],
      beneficiary_quote: [''],
      location: [''],
      date_observed: [new Date().toISOString().split('T')[0]]
    });
  }

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading = true;
    this.api.getProjects().subscribe(data => this.projects = data);
    this.api.getKpiMetrics().subscribe(data => { this.kpiMetrics = data; this.loading = false; });
    this.api.getFinancialItems().subscribe(data => this.financialItems = data);
    this.api.getRisks().subscribe(data => this.risks = data);
    this.api.getFieldNotes().subscribe(data => this.fieldNotes = data);
  }

  submitKpi(): void {
    if (this.kpiForm.invalid) return;
    this.submitting = true;
    this.api.createKpiMetric(this.kpiForm.value).subscribe({
      next: () => { this.showForm = false; this.submitting = false; this.loadData(); this.kpiForm.reset(); },
      error: (err) => { this.submitting = false; alert(err.error?.detail || 'Failed'); }
    });
  }

  submitFinancial(): void {
    if (this.financialForm.invalid) return;
    this.submitting = true;
    this.api.createFinancialItem(this.financialForm.value).subscribe({
      next: () => { this.showForm = false; this.submitting = false; this.loadData(); this.financialForm.reset(); },
      error: (err) => { this.submitting = false; alert(err.error?.detail || 'Failed'); }
    });
  }

  submitRisk(): void {
    if (this.riskForm.invalid) return;
    this.submitting = true;
    this.api.createRisk(this.riskForm.value).subscribe({
      next: () => { this.showForm = false; this.submitting = false; this.loadData(); this.riskForm.reset(); },
      error: (err) => { this.submitting = false; alert(err.error?.detail || 'Failed'); }
    });
  }

  submitFieldNote(): void {
    if (this.fieldNoteForm.invalid) return;
    this.submitting = true;
    this.api.createFieldNote(this.fieldNoteForm.value).subscribe({
      next: () => { this.showForm = false; this.submitting = false; this.loadData(); this.fieldNoteForm.reset(); },
      error: (err) => { this.submitting = false; alert(err.error?.detail || 'Failed'); }
    });
  }

  verifyMetric(id: number): void {
    this.api.verifyKpiMetric(id).subscribe(() => this.loadData());
  }

  verifyFinancial(id: number): void {
    this.api.verifyFinancialItem(id).subscribe(() => this.loadData());
  }

  getProjectName(id: number): string {
    return this.projects.find(p => p.id === id)?.name || 'Unknown';
  }
}
