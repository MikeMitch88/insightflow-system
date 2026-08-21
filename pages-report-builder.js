registerPage('report-builder', () => `
<div class="p-xl max-w-5xl mx-auto">
  <div class="mb-8"><h2 class="font-headline-lg text-headline-lg text-on-surface mb-2">Report Builder</h2><p class="font-body-md text-body-md text-on-surface-variant">Configure and generate custom intelligence reports.</p></div>
  <div class="mb-10 relative">
    <div class="absolute top-1/2 left-0 w-full h-0.5 bg-outline-variant/30 -z-10 -translate-y-1/2"></div>
    <div class="flex justify-between relative z-0">
      <div class="flex flex-col items-center gap-2"><div class="w-8 h-8 rounded-full bg-secondary text-on-secondary flex items-center justify-center font-label-md text-label-md font-bold shadow-sm"><span class="material-symbols-outlined text-sm">check</span></div><span class="font-label-sm text-label-sm text-on-surface uppercase tracking-wider">1. Select Data</span></div>
      <div class="flex flex-col items-center gap-2"><div class="w-8 h-8 rounded-full bg-secondary text-on-secondary flex items-center justify-center font-label-md text-label-md font-bold shadow-sm ring-4 ring-secondary/20">2</div><span class="font-label-sm text-label-sm text-secondary uppercase tracking-wider font-bold">2. Configure</span></div>
      <div class="flex flex-col items-center gap-2"><div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center font-label-md text-label-md font-bold border border-outline-variant shadow-sm">3</div><span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">3. Review</span></div>
      <div class="flex flex-col items-center gap-2"><div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center font-label-md text-label-md font-bold border border-outline-variant shadow-sm">4</div><span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">4. Generate</span></div>
    </div>
  </div>
  <div class="bg-surface-container-lowest rounded-xl border border-surface-variant shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] overflow-hidden">
    <div class="p-lg border-b border-surface-variant bg-surface-bright"><h3 class="font-title-lg text-title-lg text-on-surface">Report Configuration</h3></div>
    <div class="p-lg grid grid-cols-1 md:grid-cols-12 gap-xl">
      <div class="md:col-span-8 space-y-8">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div class="space-y-2"><label class="font-label-md text-label-md text-on-surface-variant block">Reporting Period</label><div class="relative"><select class="w-full h-10 pl-3 pr-10 rounded-md border border-outline-variant bg-surface-container-lowest text-on-surface font-body-md text-body-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary appearance-none shadow-sm"><option>Q3 2024 (Current)</option><option>Q2 2024</option><option>YTD 2024</option><option>Custom Range...</option></select><span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-outline pointer-events-none">expand_more</span></div></div>
          <div class="space-y-2"><label class="font-label-md text-label-md text-on-surface-variant block">Report Type</label><div class="relative"><select class="w-full h-10 pl-3 pr-10 rounded-md border border-outline-variant bg-surface-container-lowest text-on-surface font-body-md text-body-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary appearance-none shadow-sm"><option>Executive Briefing</option><option>Donor Impact Report</option><option>M&E Detailed Analysis</option></select><span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-outline pointer-events-none">expand_more</span></div></div>
        </div>
        <div class="space-y-3">
          <label class="font-label-md text-label-md text-on-surface-variant block border-b border-surface-variant pb-2">Included Programs</label>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <label class="flex items-start gap-3 p-3 rounded-lg border border-secondary bg-secondary-fixed/30 cursor-pointer hover:bg-secondary-fixed/50 transition-colors"><input checked type="checkbox" class="mt-0.5 rounded text-secondary focus:ring-secondary border-outline-variant"/><div><span class="font-title-md text-title-md text-on-surface block leading-tight">Scholarship</span><span class="font-label-sm text-label-sm text-on-surface-variant">Core</span></div></label>
            <label class="flex items-start gap-3 p-3 rounded-lg border border-outline-variant bg-surface-container-lowest cursor-pointer hover:bg-surface-container-low transition-colors"><input type="checkbox" class="mt-0.5 rounded text-secondary focus:ring-secondary border-outline-variant"/><div><span class="font-title-md text-title-md text-on-surface block leading-tight">Plus</span><span class="font-label-sm text-label-sm text-on-surface-variant">Extension</span></div></label>
            <label class="flex items-start gap-3 p-3 rounded-lg border border-secondary bg-secondary-fixed/30 cursor-pointer hover:bg-secondary-fixed/50 transition-colors"><input checked type="checkbox" class="mt-0.5 rounded text-secondary focus:ring-secondary border-outline-variant"/><div><span class="font-title-md text-title-md text-on-surface block leading-tight">Vocational</span><span class="font-label-sm text-label-sm text-on-surface-variant">Skills</span></div></label>
            <label class="flex items-start gap-3 p-3 rounded-lg border border-outline-variant bg-surface-container-lowest cursor-pointer hover:bg-surface-container-low transition-colors"><input type="checkbox" class="mt-0.5 rounded text-secondary focus:ring-secondary border-outline-variant"/><div><span class="font-title-md text-title-md text-on-surface block leading-tight">Tech</span><span class="font-label-sm text-label-sm text-on-surface-variant">Digital</span></div></label>
          </div>
        </div>
        <div class="space-y-3">
          <label class="font-label-md text-label-md text-on-surface-variant block border-b border-surface-variant pb-2">Report Sections</label>
          <div class="bg-surface-container rounded-lg border border-outline-variant overflow-hidden">
            <div class="flex items-center justify-between p-4 border-b border-outline-variant/50 hover:bg-surface-container-high transition-colors cursor-pointer"><div class="flex items-center gap-3"><span class="material-symbols-outlined text-outline">drag_indicator</span><span class="font-body-md text-body-md text-on-surface font-medium">Executive Summary</span></div><label class="relative inline-flex items-center cursor-pointer"><input checked type="checkbox" class="sr-only peer"/><div class="w-9 h-5 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-secondary"></div></label></div>
            <div class="flex items-center justify-between p-4 border-b border-outline-variant/50 hover:bg-surface-container-high transition-colors cursor-pointer"><div class="flex items-center gap-3"><span class="material-symbols-outlined text-outline">drag_indicator</span><span class="font-body-md text-body-md text-on-surface font-medium">Key Outcomes & Metrics</span></div><label class="relative inline-flex items-center cursor-pointer"><input checked type="checkbox" class="sr-only peer"/><div class="w-9 h-5 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-secondary"></div></label></div>
            <div class="flex items-center justify-between p-4 hover:bg-surface-container-high transition-colors cursor-pointer"><div class="flex items-center gap-3"><span class="material-symbols-outlined text-outline">drag_indicator</span><span class="font-body-md text-body-md text-on-surface font-medium">Financial Overview</span></div><label class="relative inline-flex items-center cursor-pointer"><input type="checkbox" class="sr-only peer"/><div class="w-9 h-5 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-secondary"></div></label></div>
          </div>
        </div>
      </div>
      <div class="md:col-span-4 space-y-6">
        <div class="rounded-lg p-[2px] bg-gradient-to-br from-secondary via-on-tertiary-container to-secondary-container shadow-md">
          <div class="bg-surface-container-lowest rounded-md p-5 h-full flex flex-col">
            <div class="flex items-center gap-2 mb-3"><span class="material-symbols-outlined text-on-tertiary-container">auto_awesome</span><h4 class="font-title-md text-title-md text-on-surface font-bold">InsightFlow Intelligence</h4></div>
            <p class="font-body-md text-body-md text-on-surface-variant mb-4 flex-1">Synthesize raw data points into a cohesive executive narrative.</p>
            <label class="flex items-center justify-between bg-surface-container rounded p-3 cursor-pointer border border-outline-variant/30 hover:border-secondary/50 transition-colors"><span class="font-label-md text-label-md font-semibold text-on-surface pr-4">Use AI to generate executive summary and insights</span><div class="relative inline-flex items-center shrink-0"><input checked type="checkbox" class="sr-only peer"/><div class="w-9 h-5 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-secondary"></div></div></label>
          </div>
        </div>
      </div>
    </div>
    <div class="p-6 border-t border-surface-variant bg-surface-bright flex justify-between items-center">
      <button class="px-5 py-2.5 rounded border border-outline-variant bg-surface-container-lowest text-on-surface font-label-md text-label-md hover:bg-surface-container-low transition-colors shadow-sm">Save Draft</button>
      <div class="flex gap-3">
        <button class="px-5 py-2.5 rounded border border-outline-variant bg-surface-container-lowest text-on-surface font-label-md text-label-md hover:bg-surface-container-low transition-colors shadow-sm">Back</button>
        <button class="px-6 py-2.5 rounded bg-secondary text-on-secondary font-label-md text-label-md font-semibold hover:bg-secondary/90 transition-colors shadow-sm flex items-center gap-2">Review & Generate <span class="material-symbols-outlined text-sm">arrow_forward</span></button>
      </div>
    </div>
  </div>
</div>
`);
