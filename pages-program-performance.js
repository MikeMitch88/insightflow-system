registerPage('program-performance', () => `
<div class="p-xl bg-background max-w-container-max mx-auto space-y-lg">
  <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
    <div>
      <h2 class="font-headline-lg text-headline-lg text-primary tracking-tight">Program Performance</h2>
      <p class="font-body-md text-body-md text-on-surface-variant mt-2">Comprehensive analytics and intelligence across all operational pillars.</p>
    </div>
    <div class="flex flex-wrap gap-3">
      <button class="flex items-center gap-2 px-4 py-2 bg-white border border-[#E2E8F0] rounded-lg text-on-secondary-fixed font-title-md text-title-md hover:bg-surface-variant/10 transition-colors shadow-sm">
        <span class="material-symbols-outlined text-sm">download</span> Export Report
      </button>
      <button class="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-secondary to-tertiary-container text-white rounded-lg font-title-md text-title-md hover:opacity-90 transition-opacity shadow-sm">
        <span class="material-symbols-outlined text-sm">magic_button</span> AI Insights
      </button>
    </div>
  </div>

  <div class="bg-white rounded-[16px] border border-[#E2E8F0] p-md shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)]">
    <div class="grid grid-cols-1 md:grid-cols-5 gap-md">
      <div class="space-y-1"><label class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Program</label>
        <select class="w-full h-[40px] bg-surface border border-[#E2E8F0] rounded-lg px-3 py-2 text-body-md text-on-surface focus:ring-2 focus:ring-secondary focus:border-secondary transition-all"><option>All Programs</option><option>Education Initiative</option><option>Health & Wellness</option><option>Economic Empowerment</option></select></div>
      <div class="space-y-1"><label class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">County</label>
        <select class="w-full h-[40px] bg-surface border border-[#E2E8F0] rounded-lg px-3 py-2 text-body-md text-on-surface focus:ring-2 focus:ring-secondary focus:border-secondary transition-all"><option>All Counties</option><option>Nairobi</option><option>Mombasa</option><option>Kisumu</option></select></div>
      <div class="space-y-1"><label class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Gender</label>
        <select class="w-full h-[40px] bg-surface border border-[#E2E8F0] rounded-lg px-3 py-2 text-body-md text-on-surface focus:ring-2 focus:ring-secondary focus:border-secondary transition-all"><option>All Genders</option><option>Female</option><option>Male</option><option>Other</option></select></div>
      <div class="space-y-1"><label class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Age Group</label>
        <select class="w-full h-[40px] bg-surface border border-[#E2E8F0] rounded-lg px-3 py-2 text-body-md text-on-surface focus:ring-2 focus:ring-secondary focus:border-secondary transition-all"><option>All Ages</option><option>15 - 24</option><option>25 - 34</option><option>35 - 44</option><option>45+</option></select></div>
      <div class="space-y-1"><label class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Reporting Period</label>
        <select class="w-full h-[40px] bg-surface border border-[#E2E8F0] rounded-lg px-3 py-2 text-body-md text-on-surface focus:ring-2 focus:ring-secondary focus:border-secondary transition-all"><option>Q3 2023</option><option>Q2 2023</option><option>Q1 2023</option><option>YTD 2023</option></select></div>
    </div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-4 gap-md">
    <div class="bg-white rounded-[16px] border border-[#E2E8F0] p-md shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] relative overflow-hidden group">
      <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity"><span class="material-symbols-outlined text-6xl text-secondary">group</span></div>
      <p class="font-label-md text-label-md text-on-surface-variant mb-2">Total Enrollment</p>
      <h3 class="font-display-lg text-display-lg text-primary">124.5k</h3>
      <div class="flex items-center gap-2 mt-4 text-sm font-medium text-emerald-600"><span class="material-symbols-outlined text-sm">trending_up</span><span>+12.4% vs last period</span></div>
    </div>
    <div class="bg-white rounded-[16px] border border-[#E2E8F0] p-md shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] relative overflow-hidden group">
      <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity"><span class="material-symbols-outlined text-6xl text-tertiary-container">verified</span></div>
      <p class="font-label-md text-label-md text-on-surface-variant mb-2">Completion Rate</p>
      <h3 class="font-display-lg text-display-lg text-primary">87.2%</h3>
      <div class="flex items-center gap-2 mt-4 text-sm font-medium text-emerald-600"><span class="material-symbols-outlined text-sm">trending_up</span><span>+2.1% vs last period</span></div>
    </div>
    <div class="bg-white rounded-[16px] border border-[#E2E8F0] p-md shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] relative overflow-hidden group">
      <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity"><span class="material-symbols-outlined text-6xl text-error">warning</span></div>
      <p class="font-label-md text-label-md text-on-surface-variant mb-2">Dropout Rate</p>
      <h3 class="font-display-lg text-display-lg text-primary">4.8%</h3>
      <div class="flex items-center gap-2 mt-4 text-sm font-medium text-emerald-600"><span class="material-symbols-outlined text-sm">trending_down</span><span>-1.2% vs last period</span></div>
    </div>
    <div class="bg-white rounded-[16px] border border-[#E2E8F0] p-md shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] relative overflow-hidden group">
      <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity"><span class="material-symbols-outlined text-6xl text-secondary">insights</span></div>
      <p class="font-label-md text-label-md text-on-surface-variant mb-2">Positive Outcomes</p>
      <h3 class="font-display-lg text-display-lg text-primary">92.1%</h3>
      <div class="flex items-center gap-2 mt-4 text-sm font-medium text-emerald-600"><span class="material-symbols-outlined text-sm">trending_up</span><span>+5.4% vs last period</span></div>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-md">
    <div class="lg:col-span-2 bg-white rounded-[16px] border border-[#E2E8F0] shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] flex flex-col">
      <div class="p-md border-b border-[#F1F5F9] flex justify-between items-center">
        <h3 class="font-title-lg text-title-lg text-primary">Beneficiary Trajectory</h3>
        <div class="flex gap-2"><button class="px-3 py-1 text-xs font-medium bg-surface-container rounded-md text-on-surface">Monthly</button><button class="px-3 py-1 text-xs font-medium text-on-surface-variant hover:bg-surface-container rounded-md">Quarterly</button></div>
      </div>
      <div class="p-md flex-1 relative min-h-[300px] chart-grid flex items-end gap-2">
        <div class="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none"><span class="material-symbols-outlined text-9xl">ssid_chart</span></div>
        <div class="w-full h-full flex items-end justify-between px-4 pb-8 pt-4">
          <div class="w-12 bg-secondary/80 rounded-t-sm h-[40%] relative group cursor-pointer hover:bg-secondary transition-colors"><div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-surface text-xs px-2 py-1 rounded shadow hidden group-hover:block whitespace-nowrap">Jan: 40k</div></div>
          <div class="w-12 bg-secondary/80 rounded-t-sm h-[45%] relative group cursor-pointer hover:bg-secondary transition-colors"><div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-surface text-xs px-2 py-1 rounded shadow hidden group-hover:block whitespace-nowrap">Feb: 45k</div></div>
          <div class="w-12 bg-secondary/80 rounded-t-sm h-[60%] relative group cursor-pointer hover:bg-secondary transition-colors"><div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-surface text-xs px-2 py-1 rounded shadow hidden group-hover:block whitespace-nowrap">Mar: 60k</div></div>
          <div class="w-12 bg-secondary/80 rounded-t-sm h-[55%] relative group cursor-pointer hover:bg-secondary transition-colors"><div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-surface text-xs px-2 py-1 rounded shadow hidden group-hover:block whitespace-nowrap">Apr: 55k</div></div>
          <div class="w-12 bg-secondary/80 rounded-t-sm h-[75%] relative group cursor-pointer hover:bg-secondary transition-colors"><div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-surface text-xs px-2 py-1 rounded shadow hidden group-hover:block whitespace-nowrap">May: 75k</div></div>
          <div class="w-12 bg-secondary/80 rounded-t-sm h-[85%] relative group cursor-pointer hover:bg-secondary transition-colors"><div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-surface text-xs px-2 py-1 rounded shadow hidden group-hover:block whitespace-nowrap">Jun: 85k</div></div>
          <div class="w-12 bg-secondary/80 rounded-t-sm h-[100%] relative group cursor-pointer hover:bg-secondary transition-colors"><div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-surface text-xs px-2 py-1 rounded shadow hidden group-hover:block whitespace-nowrap">Jul: 100k</div></div>
        </div>
        <div class="absolute bottom-2 left-0 w-full flex justify-between px-6 text-xs text-on-surface-variant font-medium"><span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span><span>Jul</span></div>
      </div>
    </div>
    <div class="bg-white rounded-[16px] border border-[#E2E8F0] shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] flex flex-col">
      <div class="p-md border-b border-[#F1F5F9]"><h3 class="font-title-lg text-title-lg text-primary">Attendance Distribution</h3></div>
      <div class="p-md flex-1 flex flex-col justify-center items-center gap-6">
        <div class="relative w-40 h-40 rounded-full flex items-center justify-center" style="background: conic-gradient(#0058be 0% 65%, #07006c 65% 85%, #c6c6cd 85% 100%);">
          <div class="w-28 h-28 bg-white rounded-full flex flex-col items-center justify-center"><span class="font-title-lg text-title-lg font-bold">85%</span><span class="text-xs text-on-surface-variant">Avg. Rate</span></div>
        </div>
        <div class="w-full space-y-2">
          <div class="flex items-center justify-between text-sm"><div class="flex items-center gap-2"><span class="w-3 h-3 rounded-full bg-secondary"></span><span class="text-on-surface">Consistent (>80%)</span></div><span class="font-medium">65%</span></div>
          <div class="flex items-center justify-between text-sm"><div class="flex items-center gap-2"><span class="w-3 h-3 rounded-full bg-tertiary-container"></span><span class="text-on-surface">Irregular (50-80%)</span></div><span class="font-medium">20%</span></div>
          <div class="flex items-center justify-between text-sm"><div class="flex items-center gap-2"><span class="w-3 h-3 rounded-full bg-outline-variant"></span><span class="text-on-surface">Poor (<50%)</span></div><span class="font-medium">15%</span></div>
        </div>
      </div>
    </div>
  </div>

  <div class="bg-white rounded-[16px] border border-[#E2E8F0] shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] overflow-hidden">
    <div class="p-md border-b border-[#F1F5F9] flex justify-between items-center bg-white">
      <h3 class="font-title-lg text-title-lg text-primary">Granular Performance by Pillar</h3>
      <button class="text-secondary font-medium text-sm hover:underline flex items-center gap-1">View Full Report <span class="material-symbols-outlined text-sm">arrow_forward</span></button>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead><tr class="bg-[#F8FAFC] border-b border-[#F1F5F9]">
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">Pillar / Program</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Target Enrollment</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Actual Enrollment</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Completion Rate</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">Dropout Rate</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-center">Status</th>
        </tr></thead>
        <tbody class="text-body-md text-on-surface">
          <tr class="border-b border-[#F1F5F9] hover:bg-[#EFF6FF] transition-colors">
            <td class="py-3 px-4"><div class="font-medium text-primary">Digital Literacy Initiative</div><div class="text-xs text-on-surface-variant">Education Pillar</div></td>
            <td class="py-3 px-4 text-right">25,000</td>
            <td class="py-3 px-4 text-right font-medium">28,450</td>
            <td class="py-3 px-4 text-right"><div class="flex items-center justify-end gap-2"><span>92%</span><div class="w-16 h-1.5 bg-surface-container rounded-full overflow-hidden"><div class="bg-secondary h-full" style="width:92%"></div></div></div></td>
            <td class="py-3 px-4 text-right text-emerald-600">3.2%</td>
            <td class="py-3 px-4 text-center"><span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">On Track</span></td>
          </tr>
          <tr class="border-b border-[#F1F5F9] hover:bg-[#EFF6FF] transition-colors">
            <td class="py-3 px-4"><div class="font-medium text-primary">Youth Entrepreneurship</div><div class="text-xs text-on-surface-variant">Economic Pillar</div></td>
            <td class="py-3 px-4 text-right">15,000</td>
            <td class="py-3 px-4 text-right font-medium">12,100</td>
            <td class="py-3 px-4 text-right"><div class="flex items-center justify-end gap-2"><span>78%</span><div class="w-16 h-1.5 bg-surface-container rounded-full overflow-hidden"><div class="bg-tertiary-container h-full" style="width:78%"></div></div></div></td>
            <td class="py-3 px-4 text-right text-amber-600">8.5%</td>
            <td class="py-3 px-4 text-center"><span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">At Risk</span></td>
          </tr>
          <tr class="border-b border-[#F1F5F9] hover:bg-[#EFF6FF] transition-colors">
            <td class="py-3 px-4"><div class="font-medium text-primary">Maternal Health Outreach</div><div class="text-xs text-on-surface-variant">Health Pillar</div></td>
            <td class="py-3 px-4 text-right">40,000</td>
            <td class="py-3 px-4 text-right font-medium">45,200</td>
            <td class="py-3 px-4 text-right"><div class="flex items-center justify-end gap-2"><span>96%</span><div class="w-16 h-1.5 bg-surface-container rounded-full overflow-hidden"><div class="bg-secondary h-full" style="width:96%"></div></div></div></td>
            <td class="py-3 px-4 text-right text-emerald-600">1.8%</td>
            <td class="py-3 px-4 text-center"><span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">On Track</span></td>
          </tr>
          <tr class="hover:bg-[#EFF6FF] transition-colors">
            <td class="py-3 px-4"><div class="font-medium text-primary">Clean Water Access</div><div class="text-xs text-on-surface-variant">Infrastructure Pillar</div></td>
            <td class="py-3 px-4 text-right">10,000</td>
            <td class="py-3 px-4 text-right font-medium">9,800</td>
            <td class="py-3 px-4 text-right"><div class="flex items-center justify-end gap-2"><span>88%</span><div class="w-16 h-1.5 bg-surface-container rounded-full overflow-hidden"><div class="bg-secondary h-full" style="width:88%"></div></div></div></td>
            <td class="py-3 px-4 text-right text-emerald-600">4.1%</td>
            <td class="py-3 px-4 text-center"><span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">On Track</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
`);
