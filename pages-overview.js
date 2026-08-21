registerPage('overview', () => `
<div class="p-4 md:p-xl space-y-lg">
  <div class="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-4">
    <div>
      <h2 class="font-display-lg text-headline-lg font-bold text-primary tracking-tight">Program Overview</h2>
      <p class="font-body-lg text-body-lg text-on-surface-variant mt-1">Real-time visibility across Inuka Foundation programs</p>
    </div>
    <div class="flex flex-wrap items-center gap-3">
      <div class="relative">
        <select class="appearance-none bg-surface-container border border-outline-variant text-on-surface font-title-md text-body-md rounded-lg pl-4 pr-10 py-2 h-10 focus:ring-2 focus:ring-secondary focus:border-secondary outline-none cursor-pointer">
          <option>Q3 2026</option><option>Q2 2026</option><option>Q1 2026</option>
        </select>
        <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-outline">expand_more</span>
      </div>
      <button class="flex items-center gap-2 bg-surface border border-outline-variant text-primary font-title-md text-title-md h-10 px-4 rounded-lg hover:bg-surface-container transition-colors">
        <span class="material-symbols-outlined text-sm">download</span> Export
      </button>
      <button class="flex items-center gap-2 bg-secondary text-on-secondary font-title-md text-title-md h-10 px-4 rounded-lg hover:bg-secondary/90 transition-colors shadow-sm">
        <span class="material-symbols-outlined text-sm">magic_button</span> Generate
      </button>
    </div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-md">
    <div class="glass-card rounded-xl p-md">
      <div class="flex justify-between items-start">
        <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wide">Total Beneficiaries</p>
        <span class="material-symbols-outlined text-outline">groups</span>
      </div>
      <div class="mt-4 flex items-baseline gap-2">
        <h3 class="font-headline-lg text-headline-lg text-primary">12,450</h3>
        <span class="flex items-center text-sm font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
          <span class="material-symbols-outlined text-[14px]">trending_up</span> +14.2%
        </span>
      </div>
    </div>
    <div class="glass-card rounded-xl p-md">
      <div class="flex justify-between items-start">
        <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wide">Active Beneficiaries</p>
        <span class="material-symbols-outlined text-outline">how_to_reg</span>
      </div>
      <div class="mt-4 flex items-baseline gap-2">
        <h3 class="font-headline-lg text-headline-lg text-primary">9,820</h3>
        <span class="text-sm font-medium text-on-surface-variant">(78.9%)</span>
      </div>
    </div>
    <div class="glass-card rounded-xl p-md">
      <div class="flex justify-between items-start">
        <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wide">Program Completion Rate</p>
        <span class="material-symbols-outlined text-outline">school</span>
      </div>
      <div class="mt-4 flex items-baseline gap-2">
        <h3 class="font-headline-lg text-headline-lg text-primary">82.4%</h3>
        <span class="flex items-center text-sm font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
          <span class="material-symbols-outlined text-[14px]">trending_up</span> +6.8%
        </span>
      </div>
    </div>
    <div class="glass-card rounded-xl p-md">
      <div class="flex justify-between items-start">
        <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wide">Programs</p>
        <span class="material-symbols-outlined text-outline">view_cozy</span>
      </div>
      <div class="mt-4 flex items-baseline gap-2">
        <h3 class="font-headline-lg text-headline-lg text-primary">4</h3>
        <span class="text-sm font-medium text-on-surface-variant">(All active)</span>
      </div>
    </div>
    <div class="glass-card rounded-xl p-md">
      <div class="flex justify-between items-start">
        <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wide">Counties Reached</p>
        <span class="material-symbols-outlined text-outline">map</span>
      </div>
      <div class="mt-4 flex items-baseline gap-2">
        <h3 class="font-headline-lg text-headline-lg text-primary">32</h3>
        <span class="flex items-center text-sm font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
          <span class="material-symbols-outlined text-[14px]">add</span> +3
        </span>
      </div>
    </div>
    <div class="glass-card rounded-xl p-md">
      <div class="flex justify-between items-start">
        <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wide">Data Quality Score</p>
        <span class="material-symbols-outlined text-outline">verified</span>
      </div>
      <div class="mt-4 flex items-baseline gap-2">
        <h3 class="font-headline-lg text-headline-lg text-primary">96.8%</h3>
        <span class="flex items-center text-sm font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
          <span class="material-symbols-outlined text-[14px]">trending_up</span> Up 2.4%
        </span>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-md">
    <div class="glass-card rounded-xl lg:col-span-2 flex flex-col h-96">
      <div class="p-md border-b border-surface-container-high">
        <h3 class="font-title-lg text-title-lg text-primary">Beneficiary Reach Over Time</h3>
      </div>
      <div class="flex-1 p-md relative">
        <div class="absolute inset-0 m-md flex items-end">
          <div class="chart-grid-line absolute bottom-[25%] w-full border-b border-[#E2E8F0]/50"></div>
          <div class="chart-grid-line absolute bottom-[50%] w-full border-b border-[#E2E8F0]/50"></div>
          <div class="chart-grid-line absolute bottom-[75%] w-full border-b border-[#E2E8F0]/50"></div>
          <svg class="w-full h-full absolute inset-0 z-10" preserveAspectRatio="none" viewBox="0 0 100 100">
            <path class="opacity-80" d="M0,80 Q10,75 20,60 T40,50 T60,30 T80,20 T100,10" fill="none" stroke="#0058be" stroke-width="2"/>
            <path class="opacity-20" d="M0,80 Q10,75 20,60 T40,50 T60,30 T80,20 T100,10 L100,100 L0,100 Z" fill="url(#blue-gradient)"/>
            <defs><linearGradient id="blue-gradient" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#0058be"/><stop offset="100%" stop-color="#ffffff" stop-opacity="0"/></linearGradient></defs>
          </svg>
        </div>
      </div>
    </div>
    <div class="glass-card rounded-xl lg:col-span-1 flex flex-col h-96">
      <div class="p-md border-b border-surface-container-high">
        <h3 class="font-title-lg text-title-lg text-primary">Program Performance</h3>
      </div>
      <div class="flex-1 p-md flex flex-col justify-center space-y-6">
        <div class="space-y-1"><div class="flex justify-between font-label-md text-label-md text-on-surface"><span>Scholarship</span><span>85%</span></div><div class="w-full bg-surface-container h-2 rounded-full overflow-hidden"><div class="bg-secondary h-full" style="width:85%"></div></div></div>
        <div class="space-y-1"><div class="flex justify-between font-label-md text-label-md text-on-surface"><span>Plus</span><span>72%</span></div><div class="w-full bg-surface-container h-2 rounded-full overflow-hidden"><div class="bg-tertiary-container h-full" style="width:72%"></div></div></div>
        <div class="space-y-1"><div class="flex justify-between font-label-md text-label-md text-on-surface"><span>Vocational</span><span>94%</span></div><div class="w-full bg-surface-container h-2 rounded-full overflow-hidden"><div class="bg-secondary-container h-full" style="width:94%"></div></div></div>
        <div class="space-y-1"><div class="flex justify-between font-label-md text-label-md text-on-surface"><span>Tech</span><span>61%</span></div><div class="w-full bg-surface-container h-2 rounded-full overflow-hidden"><div class="bg-outline h-full" style="width:61%"></div></div></div>
      </div>
    </div>
  </div>

  <div class="bg-gradient-to-r from-tertiary-fixed to-primary-fixed rounded-xl p-1 border border-tertiary-fixed-dim">
    <div class="bg-surface/80 backdrop-blur-md rounded-lg p-md h-full">
      <div class="flex items-center gap-2 mb-4">
        <span class="material-symbols-outlined text-tertiary-container icon-fill">temp_preferences_custom</span>
        <h3 class="font-title-lg text-title-lg ai-gradient-text font-bold">AI Insights</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-surface rounded-lg p-4 border border-outline-variant/30 flex gap-3 items-start shadow-sm">
          <div class="p-2 bg-emerald-50 text-emerald-600 rounded-lg shrink-0"><span class="material-symbols-outlined text-[20px]">trending_up</span></div>
          <div><h4 class="font-title-md text-title-md text-primary">Vocational Surge</h4><p class="font-body-md text-body-md text-on-surface-variant mt-1">Vocational participation is up 18% this quarter.</p></div>
        </div>
        <div class="bg-surface rounded-lg p-4 border border-outline-variant/30 flex gap-3 items-start shadow-sm">
          <div class="p-2 bg-red-50 text-red-600 rounded-lg shrink-0"><span class="material-symbols-outlined text-[20px]">trending_down</span></div>
          <div><h4 class="font-title-md text-title-md text-primary">Tech Completion Alert</h4><p class="font-body-md text-body-md text-on-surface-variant mt-1">Tech program completion rate dropped 6% below target.</p></div>
        </div>
        <div class="bg-surface rounded-lg p-4 border border-outline-variant/30 flex gap-3 items-start shadow-sm">
          <div class="p-2 bg-amber-50 text-amber-600 rounded-lg shrink-0"><span class="material-symbols-outlined text-[20px]">rule</span></div>
          <div><h4 class="font-title-md text-title-md text-primary">Data Anomaly</h4><p class="font-body-md text-body-md text-on-surface-variant mt-1">3.2% of beneficiary records require manual review.</p></div>
        </div>
      </div>
    </div>
  </div>

  <div class="glass-card rounded-xl overflow-hidden mb-xl">
    <div class="p-md border-b border-surface-container-high flex justify-between items-center">
      <h3 class="font-title-lg text-title-lg text-primary">Recent Reports</h3>
      <button class="text-secondary font-title-md text-body-md hover:underline">View All</button>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead><tr class="bg-surface-container-lowest border-b border-surface-container-high">
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Report Name</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Type</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Date Generated</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Status</th>
          <th class="py-3 px-4 text-right"></th>
        </tr></thead>
        <tbody class="font-body-md text-body-md text-on-surface">
          <tr class="border-b border-surface-container-high hover:bg-[#EFF6FF] transition-colors">
            <td class="py-3 px-4 font-medium">Q3 2026 Executive Summary</td>
            <td class="py-3 px-4 text-on-surface-variant">Performance</td>
            <td class="py-3 px-4 text-on-surface-variant">Oct 15, 2026</td>
            <td class="py-3 px-4"><span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">Complete</span></td>
            <td class="py-3 px-4 text-right"><button class="text-secondary hover:text-secondary-fixed-variant"><span class="material-symbols-outlined text-[20px]">download</span></button></td>
          </tr>
          <tr class="border-b border-surface-container-high hover:bg-[#EFF6FF] transition-colors">
            <td class="py-3 px-4 font-medium">Vocational Impact Analysis</td>
            <td class="py-3 px-4 text-on-surface-variant">Impact</td>
            <td class="py-3 px-4 text-on-surface-variant">Oct 12, 2026</td>
            <td class="py-3 px-4"><span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">Complete</span></td>
            <td class="py-3 px-4 text-right"><button class="text-secondary hover:text-secondary-fixed-variant"><span class="material-symbols-outlined text-[20px]">download</span></button></td>
          </tr>
          <tr class="border-b border-surface-container-high hover:bg-[#EFF6FF] transition-colors">
            <td class="py-3 px-4 font-medium">Tech Program Enrollment Deficit</td>
            <td class="py-3 px-4 text-on-surface-variant">Ad-Hoc / AI</td>
            <td class="py-3 px-4 text-on-surface-variant">Oct 10, 2026</td>
            <td class="py-3 px-4"><span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">Review</span></td>
            <td class="py-3 px-4 text-right"><button class="text-secondary hover:text-secondary-fixed-variant"><span class="material-symbols-outlined text-[20px]">download</span></button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
`);
