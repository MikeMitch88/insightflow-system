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

  quickQuestions = [
    'What changed this quarter?',
    'Which program needs attention?',
    'Summarize Q3 performance',
    'Which counties are underperforming?',
    'Compare Q2 and Q3',
    'Recommend areas requiring management attention'
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
}
