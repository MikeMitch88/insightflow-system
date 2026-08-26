import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-ai-assistant',
  templateUrl: './ai-assistant.component.html',
  styleUrls: ['./ai-assistant.component.css']
})
export class AiAssistantComponent implements OnInit {
  messages: { role: string; content: any }[] = [];
  userInput = '';
  loading = false;
  contextPage = 'dashboard';
  addedToReport: number | null = null;

  quickQuestions = [
    'Summarize Q3 cross-pillar outcomes for donor brief',
    'What are the completion rates across all 4 pillars?',
    'Which counties show highest tech employment rate?',
    'What are the primary data quality bottlenecks?',
    'Compare Q2 and Q3 performance trends',
    'Recommend key areas requiring administrative action'
  ];


  contextMetrics: any = {};

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.messages.push({
      role: 'assistant',
      content: {
        answer: "I'm InsightFlow, your program intelligence assistant. I can answer questions about KPC Inuka Foundation's programs using verified organizational data. Ask me anything about performance, trends, or outcomes.",
        recommendation: 'Try one of the quick questions below to get started.'
      }
    });
    this.api.getDashboardSummary().subscribe({
      next: (data) => { this.contextMetrics = data || {}; }
    });
  }

  sendMessage(): void {
    if (!this.userInput.trim() || this.loading) return;
    const msg = this.userInput.trim();
    this.messages.push({ role: 'user', content: msg });
    this.userInput = '';
    this.loading = true;

    this.api.chatWithAI(msg, this.contextPage).subscribe({
      next: (response) => {
        this.messages.push({ role: 'assistant', content: response });
        this.loading = false;
      },
      error: () => {
        this.messages.push({
          role: 'assistant',
          content: { answer: 'Unable to process your request. Please try again.', recommendation: '' }
        });
        this.loading = false;
      }
    });
  }

  askQuickQuestion(question: string): void {
    this.userInput = question;
    this.sendMessage();
  }

  addToReport(msg: any, index: number): void {
    if (!msg.content?.answer) return;
    this.api.generateReport({
      title: 'AI Insight: ' + msg.content.answer.substring(0, 60),
      report_type: 'executive',
      reporting_period_id: 7,
      sections: ['executive_summary', 'recommendations'],
      use_ai_insights: true
    }).subscribe({
      next: () => {
        this.addedToReport = index;
        setTimeout(() => this.addedToReport = null, 3000);
      },
      error: () => {}
    });
  }

  exportChat(format: 'csv' | 'xlsx'): void {
    if (!this.messages.length) return;
    const rows: any[] = [];
    this.messages.forEach((msg, i) => {
      if (msg.role === 'user') {
        rows.push({ '#': i + 1, Role: 'You', Question: msg.content, Answer: '', KPIs: '', Recommendation: '' });
      } else if (msg.content?.answer) {
        const kpis = (msg.content.kpis || []).map((k: any) => k.label + ': ' + k.value).join('; ');
        rows.push({ '#': i + 1, Role: 'AI', Question: '', Answer: msg.content.answer, KPIs: kpis, Recommendation: msg.content.recommendation || '' });
      }
    });
    const blob = new Blob([this.toCSV(rows)], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'insightflow-ai-chat.' + format;
    a.click();
    URL.revokeObjectURL(url);
  }

  private toCSV(data: any[]): string {
    if (!data.length) return '';
    const headers = Object.keys(data[0]);
    const lines = [headers.join(',')];
    data.forEach(row => {
      lines.push(headers.map(h => '"' + String(row[h] || '').replace(/"/g, '""') + '"').join(','));
    });
    return lines.join('\n');
  }
}
