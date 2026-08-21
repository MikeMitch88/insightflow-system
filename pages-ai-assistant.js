registerPage('ai-assistant', () => `
<div class="flex-1 flex overflow-hidden h-[calc(100vh-64px)]">
  <aside class="w-64 border-r border-outline-variant bg-surface overflow-y-auto hidden lg:flex flex-col shrink-0">
    <div class="p-4 border-b border-outline-variant/50 flex justify-between items-center sticky top-0 bg-surface z-10"><h2 class="font-title-md text-title-md text-on-surface">Recent Chats</h2><button class="p-1 hover:bg-surface-variant rounded-md text-tertiary-container transition-colors"><span class="material-symbols-outlined text-sm">edit_square</span></button></div>
    <div class="p-2 flex flex-col gap-1">
      <div class="px-2 py-2 text-xs font-semibold text-outline uppercase tracking-wider mt-2">Today</div>
      <button class="flex items-center gap-3 px-3 py-2 bg-tertiary-fixed/30 text-tertiary-container rounded-lg text-left transition-colors"><span class="material-symbols-outlined text-sm">chat_bubble</span><span class="font-label-md text-label-md truncate">Q3 Dropout Analysis</span></button>
      <button class="flex items-center gap-3 px-3 py-2 hover:bg-surface-variant/50 text-on-surface-variant rounded-lg text-left transition-colors"><span class="material-symbols-outlined text-sm">chat_bubble</span><span class="font-label-md text-label-md truncate">Revenue Projections '27</span></button>
      <div class="px-2 py-2 text-xs font-semibold text-outline uppercase tracking-wider mt-4">Previous 7 Days</div>
      <button class="flex items-center gap-3 px-3 py-2 hover:bg-surface-variant/50 text-on-surface-variant rounded-lg text-left transition-colors"><span class="material-symbols-outlined text-sm">chat_bubble</span><span class="font-label-md text-label-md truncate">Q2 Executive Summary</span></button>
      <button class="flex items-center gap-3 px-3 py-2 hover:bg-surface-variant/50 text-on-surface-variant rounded-lg text-left transition-colors"><span class="material-symbols-outlined text-sm">chat_bubble</span><span class="font-label-md text-label-md truncate">Client Retention Metrics</span></button>
    </div>
  </aside>
  <div class="flex-1 flex flex-col relative bg-surface-bright">
    <div class="flex-1 overflow-y-auto p-6 md:p-xl space-y-8 pb-32">
      <div class="flex justify-end max-w-4xl mx-auto w-full"><div class="bg-surface-container-high text-on-surface rounded-2xl rounded-tr-sm px-5 py-4 max-w-[80%] shadow-sm"><p class="font-body-md text-body-md">Can you break down the Q3 Dropout Analysis? I need to understand the primary drivers behind the 4.2% increase in the EMEA region.</p></div></div>
      <div class="flex justify-start max-w-4xl mx-auto w-full gap-4">
        <div class="w-8 h-8 rounded-full ai-gradient shrink-0 flex items-center justify-center shadow-sm mt-1"><span class="material-symbols-outlined text-white text-sm icon-fill">psychology</span></div>
        <div class="flex-1 space-y-4">
          <div class="text-on-surface font-body-md text-body-md leading-relaxed"><p>Based on the verified Q3 2026 dataset, the 4.2% increase in EMEA dropouts is primarily correlated with two major factors, rather than a systemic product issue.</p></div>
          <div class="bg-surface rounded-xl border border-outline-variant p-5 shadow-sm">
            <div class="flex items-center justify-between mb-4 pb-4 border-b border-surface-container-high"><h3 class="font-title-md text-title-md text-on-surface flex items-center gap-2"><span class="material-symbols-outlined text-tertiary-container">trending_up</span> EMEA Dropout Drivers (Q3)</h3><span class="px-2 py-1 bg-tertiary-fixed text-on-tertiary-fixed text-xs rounded-md font-medium">Confidence: 94%</span></div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="p-4 bg-surface-container-lowest rounded-lg border border-outline-variant/50"><div class="text-sm font-semibold text-on-surface-variant mb-1">Pricing Tier Restructure</div><div class="flex items-end gap-2 mb-2"><span class="text-2xl font-bold text-error">68%</span><span class="text-xs text-on-surface-variant mb-1">of total variance</span></div><p class="text-xs text-on-surface-variant">The transition from Legacy Basic to Pro plans caused a spike in immediate cancellations among sub-50 user accounts.</p></div>
              <div class="p-4 bg-surface-container-lowest rounded-lg border border-outline-variant/50"><div class="text-sm font-semibold text-on-surface-variant mb-1">Regional Compliance Rollout</div><div class="flex items-end gap-2 mb-2"><span class="text-2xl font-bold text-tertiary-container">22%</span><span class="text-xs text-on-surface-variant mb-1">of total variance</span></div><p class="text-xs text-on-surface-variant">Mandatory re-verification for EU data residency caused temporary suspension classification.</p></div>
            </div>
            <div class="mt-4 pt-4 border-t border-surface-container-high flex justify-end"><button class="flex items-center gap-2 text-sm font-medium text-secondary hover:text-secondary-container transition-colors">View Full Driver Analysis <span class="material-symbols-outlined text-sm">arrow_forward</span></button></div>
          </div>
          <div class="text-on-surface font-body-md text-body-md leading-relaxed"><p>I recommend reviewing the <span class="px-1.5 py-0.5 bg-surface-variant rounded text-xs font-mono text-on-surface-variant cursor-pointer hover:bg-outline-variant transition-colors">Tier Transition Strategy</span> document for mitigation steps. Would you like me to generate a predictive model for Q4 based on these findings?</p></div>
          <div class="flex flex-wrap gap-2 pt-2">
            <button class="px-3 py-1.5 bg-surface border border-outline-variant rounded-full text-xs font-medium text-on-surface hover:bg-surface-variant transition-colors flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">auto_graph</span> Generate Q4 Prediction</button>
            <button class="px-3 py-1.5 bg-surface border border-outline-variant rounded-full text-xs font-medium text-on-surface hover:bg-surface-variant transition-colors flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">summarize</span> Summarize Mitigation</button>
          </div>
        </div>
      </div>
    </div>
    <div class="absolute bottom-0 left-0 right-0 p-4 md:p-6 bg-gradient-to-t from-surface-bright via-surface-bright to-transparent pt-12">
      <div class="max-w-4xl mx-auto">
        <div class="relative bg-surface rounded-2xl border border-outline-variant shadow-[0px_4px_16px_rgba(15,23,42,0.05)] focus-within:border-tertiary-container focus-within:ring-1 focus-within:ring-tertiary-container transition-all">
          <textarea class="w-full bg-transparent border-none focus:ring-0 resize-none py-4 pl-4 pr-16 text-on-surface placeholder-on-surface-variant font-body-md min-h-[56px] max-h-32 rounded-2xl" placeholder="Ask about your data, generate reports, or find insights..." rows="1"></textarea>
          <div class="absolute right-2 bottom-2 flex items-center gap-2">
            <button class="p-2 text-on-surface-variant hover:text-tertiary-container hover:bg-surface-variant rounded-full transition-colors" title="Attach Data"><span class="material-symbols-outlined">attach_file</span></button>
            <button class="p-2 ai-gradient text-white rounded-full hover:opacity-90 transition-opacity shadow-sm flex items-center justify-center h-10 w-10"><span class="material-symbols-outlined">arrow_upward</span></button>
          </div>
        </div>
        <div class="text-center mt-2"><span class="text-[10px] text-outline font-medium">InsightFlow AI can make mistakes. Verify critical data points.</span></div>
      </div>
    </div>
  </div>
  <aside class="w-72 border-l border-outline-variant bg-surface hidden xl:flex flex-col shrink-0">
    <div class="p-4 border-b border-outline-variant/50 bg-surface z-10 flex items-center gap-2"><span class="material-symbols-outlined text-tertiary-container">dataset</span><h2 class="font-title-md text-title-md text-on-surface">Data Context</h2></div>
    <div class="p-4 overflow-y-auto flex-1 space-y-6">
      <div><h3 class="text-xs font-bold text-outline uppercase tracking-wider mb-3">Active Sources</h3><div class="space-y-2">
        <div class="p-3 bg-surface-container-low rounded-lg border border-outline-variant/40 flex items-start gap-3"><span class="material-symbols-outlined text-secondary text-sm mt-0.5">table_view</span><div><div class="text-sm font-medium text-on-surface">EMEA_Q3_Churn_Final.csv</div><div class="text-xs text-on-surface-variant mt-1">12,450 records &bull; Updated 2h ago</div></div></div>
        <div class="p-3 bg-surface-container-low rounded-lg border border-outline-variant/40 flex items-start gap-3"><span class="material-symbols-outlined text-tertiary-container text-sm mt-0.5">description</span><div><div class="text-sm font-medium text-on-surface">Tier Transition Strategy</div><div class="text-xs text-on-surface-variant mt-1">PDF &bull; 14 pages</div></div></div>
      </div><button class="mt-3 text-xs font-medium text-secondary flex items-center gap-1 hover:underline"><span class="material-symbols-outlined text-[14px]">add</span> Add Source</button></div>
      <div><h3 class="text-xs font-bold text-outline uppercase tracking-wider mb-3">Referenced KPIs</h3><div class="bg-surface-container-lowest rounded-lg border border-outline-variant overflow-hidden">
        <div class="p-3 border-b border-outline-variant/50 flex justify-between items-center bg-surface-container-low"><span class="text-xs font-medium text-on-surface">EMEA Dropout Rate</span><span class="text-xs font-bold text-error">+4.2%</span></div>
        <div class="p-3 border-b border-outline-variant/50 flex justify-between items-center bg-surface-container-low"><span class="text-xs font-medium text-on-surface">Avg. Impact per Acct</span><span class="text-xs font-bold text-on-surface-variant">$1,240</span></div>
        <div class="p-3 flex justify-between items-center bg-surface-container-low"><span class="text-xs font-medium text-on-surface">Confidence Score</span><span class="text-xs font-bold text-tertiary-container">High (94%)</span></div>
      </div></div>
      <div class="p-3 bg-secondary-fixed/30 rounded-lg border border-secondary-fixed flex items-start gap-2"><span class="material-symbols-outlined text-secondary text-sm mt-0.5">verified_user</span><div><div class="text-xs font-semibold text-on-secondary-fixed">Enterprise Guardrails Active</div><p class="text-[10px] text-on-surface-variant mt-1">PII redacted. Responses grounded in verified datasets only.</p></div></div>
    </div>
  </aside>
</div>
`);
