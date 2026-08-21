registerPage('beneficiary-analytics', () => `
<div class="p-xl flex-1 max-w-[1440px] mx-auto w-full flex flex-col gap-lg">
  <div class="flex justify-between items-end mb-4">
    <div>
      <h2 class="font-display-lg text-display-lg text-primary mb-2">Beneficiary Analytics</h2>
      <p class="font-body-lg text-body-lg text-on-surface-variant">Deep operational intelligence on demographic reach and socio-economic impact across Kenya.</p>
    </div>
    <div class="flex gap-4">
      <button class="flex items-center gap-2 px-4 py-2 bg-white border border-[#E2E8F0] rounded text-secondary font-title-md text-title-md hover:bg-surface-variant/20 transition-colors shadow-sm"><span class="material-symbols-outlined">download</span> Export Data</button>
      <button class="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-secondary to-tertiary-container rounded text-white font-title-md text-title-md hover:opacity-90 transition-opacity shadow-md"><span class="material-symbols-outlined">auto_awesome</span> AI Insights</button>
    </div>
  </div>
  <div class="grid grid-cols-1 md:grid-cols-12 gap-lg">
    <div class="col-span-12 grid grid-cols-1 md:grid-cols-4 gap-md">
      <div class="glass-card p-6 rounded-xl flex flex-col gap-2"><span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wide">Total Reach</span><div class="font-headline-lg text-headline-lg text-primary flex items-baseline gap-2">2.4M <span class="font-body-md text-body-md text-secondary">+12% YoY</span></div></div>
      <div class="glass-card p-6 rounded-xl flex flex-col gap-2"><span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wide">Active Counties</span><div class="font-headline-lg text-headline-lg text-primary flex items-baseline gap-2">42 <span class="font-body-md text-body-md text-outline">/ 47</span></div></div>
      <div class="glass-card p-6 rounded-xl flex flex-col gap-2"><span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wide">Avg Vulnerability Score</span><div class="font-headline-lg text-headline-lg text-primary flex items-baseline gap-2">7.8 <span class="font-body-md text-body-md text-error">High Need</span></div></div>
      <div class="glass-card p-6 rounded-xl flex flex-col gap-2 relative overflow-hidden group cursor-pointer"><div class="absolute inset-0 bg-gradient-to-br from-secondary/5 to-tertiary-container/5 opacity-0 group-hover:opacity-100 transition-opacity"></div><span class="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wide flex items-center gap-1"><span class="material-symbols-outlined text-[14px] text-tertiary-container">psychology</span> AI Prediction</span><div class="font-title-lg text-title-lg text-primary ai-gradient-text mt-1">Q3 Reach expected to grow by 15% in Arid regions.</div></div>
    </div>
    <div class="col-span-12 md:col-span-7 glass-card rounded-xl flex flex-col">
      <div class="p-4 border-b border-[#F1F5F9] flex justify-between items-center"><h3 class="font-title-lg text-title-lg text-primary">Geographic Reach: Kenya</h3><div class="flex gap-2"><button class="p-1.5 rounded hover:bg-surface-variant/20"><span class="material-symbols-outlined text-outline">filter_list</span></button><button class="p-1.5 rounded hover:bg-surface-variant/20"><span class="material-symbols-outlined text-outline">more_vert</span></button></div></div>
      <div class="p-4 flex-1 min-h-[400px] relative rounded-b-xl overflow-hidden bg-[#F8FAFC]">
        <div class="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-80 mix-blend-multiply" style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuBzk_eEK13zSeMLN4MwCWuXgAb2ueq80oE3VXvMg7RzhdNf7dlkSMrlTXMix-sNuQ7ToIXB7WYcZ15sLUHbpFFwJcurdQ_U1DvNeBkosQ0B3JtmMBhtOUd-CS1dTx71nwWTpDr2TBdk1HB7bG63buOjaOP7yZazM6eKgZa2xY3TOPC9WzrFEyhIDlhXtMG_Yke47cunnQlatdEyFZmUia2OIKw4Qlk0mLBulGKRV2KCz6ajAsV2Z1w4Mg')"></div>
        <div class="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm p-3 rounded-lg border border-[#E2E8F0] shadow-sm flex flex-col gap-2"><span class="font-label-sm text-label-sm text-on-surface-variant uppercase">Density</span><div class="flex items-center gap-2"><span class="text-xs text-outline">Low</span><div class="w-32 h-2 rounded-full bg-gradient-to-r from-surface-variant via-secondary-fixed to-secondary"></div><span class="text-xs text-outline">High</span></div></div>
      </div>
    </div>
    <div class="col-span-12 md:col-span-5 flex flex-col gap-lg">
      <div class="glass-card rounded-xl flex flex-col flex-1">
        <div class="p-4 border-b border-[#F1F5F9] flex justify-between items-center"><h3 class="font-title-lg text-title-lg text-primary">Demographics</h3></div>
        <div class="p-4 flex-1 flex flex-col gap-4 justify-center">
          <div class="flex justify-between items-end h-48 px-4 gap-2 relative">
            <div class="absolute inset-0 flex flex-col justify-between pointer-events-none"><div class="border-b border-[#E2E8F0]/50 h-px w-full"></div><div class="border-b border-[#E2E8F0]/50 h-px w-full"></div><div class="border-b border-[#E2E8F0]/50 h-px w-full"></div><div class="border-b border-[#E2E8F0] h-px w-full"></div></div>
            <div class="flex gap-1 z-10 w-full justify-around items-end">
              <div class="flex gap-1 items-end group"><div class="w-8 bg-secondary rounded-t-sm h-[60%] group-hover:opacity-80 transition-opacity"></div><div class="w-8 bg-secondary-fixed-dim rounded-t-sm h-[75%] group-hover:opacity-80 transition-opacity"></div></div>
              <div class="flex gap-1 items-end group"><div class="w-8 bg-secondary rounded-t-sm h-[80%] group-hover:opacity-80 transition-opacity"></div><div class="w-8 bg-secondary-fixed-dim rounded-t-sm h-[90%] group-hover:opacity-80 transition-opacity"></div></div>
              <div class="flex gap-1 items-end group"><div class="w-8 bg-secondary rounded-t-sm h-[100%] group-hover:opacity-80 transition-opacity"></div><div class="w-8 bg-secondary-fixed-dim rounded-t-sm h-[85%] group-hover:opacity-80 transition-opacity"></div></div>
              <div class="flex gap-1 items-end group"><div class="w-8 bg-secondary rounded-t-sm h-[40%] group-hover:opacity-80 transition-opacity"></div><div class="w-8 bg-secondary-fixed-dim rounded-t-sm h-[45%] group-hover:opacity-80 transition-opacity"></div></div>
            </div>
          </div>
          <div class="flex justify-around font-label-md text-label-md text-outline"><span>18-25</span><span>26-35</span><span>36-50</span><span>51+</span></div>
          <div class="flex justify-center gap-4 mt-2"><div class="flex items-center gap-2 font-label-sm text-label-sm"><span class="w-3 h-3 rounded-sm bg-secondary"></span> Female</div><div class="flex items-center gap-2 font-label-sm text-label-sm"><span class="w-3 h-3 rounded-sm bg-secondary-fixed-dim"></span> Male</div></div>
        </div>
      </div>
      <div class="glass-card rounded-xl flex flex-col flex-1">
        <div class="p-4 border-b border-[#F1F5F9] flex justify-between items-center"><h3 class="font-title-lg text-title-lg text-primary">Socio-Economic Cohorts</h3></div>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead><tr class="bg-[#F8FAFC]"><th class="py-2 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold">Cohort</th><th class="py-2 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold">% Total</th><th class="py-2 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase font-semibold">Trend</th></tr></thead>
            <tbody class="font-body-md text-body-md text-primary">
              <tr class="border-b border-[#F1F5F9] hover:bg-[#EFF6FF] transition-colors"><td class="py-2 px-4">Extreme Poverty</td><td class="py-2 px-4 font-medium">34%</td><td class="py-2 px-4 text-secondary flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">trending_down</span> -2%</td></tr>
              <tr class="border-b border-[#F1F5F9] hover:bg-[#EFF6FF] transition-colors"><td class="py-2 px-4">Vulnerable</td><td class="py-2 px-4 font-medium">45%</td><td class="py-2 px-4 text-error flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">trending_up</span> +5%</td></tr>
              <tr class="hover:bg-[#EFF6FF] transition-colors"><td class="py-2 px-4">Stable</td><td class="py-2 px-4 font-medium">21%</td><td class="py-2 px-4 text-outline flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">trending_flat</span> 0%</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>
`);
