registerPage('reports', () => `
<div class="p-xl max-w-container-max mx-auto w-full flex-1">
  <div class="flex flex-col md:flex-row justify-between items-start md:items-end mb-lg gap-4">
    <div><h2 class="font-headline-lg text-headline-lg text-on-background mb-1">Reports</h2><p class="font-body-md text-body-md text-on-surface-variant">Generate, manage and share automated program reports.</p></div>
    <div class="flex flex-wrap items-center gap-md w-full md:w-auto">
      <div class="relative w-full md:w-64 focus-within:ring-2 focus-within:ring-secondary rounded"><span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span><input class="w-full h-[40px] pl-10 pr-4 bg-surface border border-outline-variant rounded font-body-md text-body-md focus:outline-none focus:border-secondary transition-colors text-on-surface" placeholder="Search reports..." type="text"/></div>
      <button class="h-[40px] px-4 bg-surface border border-outline-variant rounded flex items-center gap-2 hover:bg-surface-variant/20 transition-colors text-on-surface font-title-md text-title-md"><span class="material-symbols-outlined text-[18px]">filter_list</span> Filter</button>
      <button class="h-[40px] px-6 bg-secondary text-on-secondary rounded font-title-md text-title-md hover:bg-secondary/90 transition-colors shadow-sm flex items-center gap-2 whitespace-nowrap"><span class="material-symbols-outlined text-[18px]">add</span> Generate New Report</button>
    </div>
  </div>
  <div class="bg-surface-container-lowest rounded-xl border border-outline-variant shadow-sm overflow-hidden flex flex-col">
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead class="bg-surface-container-low border-b border-outline-variant"><tr>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Report Name</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Period</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Programs</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Date Generated</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">Status</th>
          <th class="py-3 px-4 font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider text-right">Actions</th>
        </tr></thead>
        <tbody class="divide-y divide-surface-container font-body-md text-body-md">
          <tr class="hover:bg-secondary-fixed/30 transition-colors group">
            <td class="py-3 px-4"><div class="flex items-center gap-3"><div class="w-8 h-8 rounded bg-primary-fixed flex items-center justify-center text-primary"><span class="material-symbols-outlined text-[16px]">picture_as_pdf</span></div><span class="font-title-md text-title-md text-on-surface">Q3 Executive Summary</span></div></td>
            <td class="py-3 px-4 text-on-surface-variant">Q3 2023</td><td class="py-3 px-4 text-on-surface-variant">Alpha, Beta, Gamma</td><td class="py-3 px-4 text-on-surface-variant">Oct 15, 2023</td>
            <td class="py-3 px-4"><span class="inline-flex items-center px-2 py-1 rounded-full bg-surface-container-highest text-on-surface font-label-sm text-label-sm"><span class="w-2 h-2 rounded-full bg-secondary mr-2"></span>Ready</span></td>
            <td class="py-3 px-4 text-right"><div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity"><button class="p-1 text-on-surface-variant hover:text-secondary transition-colors"><span class="material-symbols-outlined">visibility</span></button><button class="p-1 text-on-surface-variant hover:text-secondary transition-colors"><span class="material-symbols-outlined">download</span></button><button class="p-1 text-on-surface-variant hover:text-secondary transition-colors"><span class="material-symbols-outlined">share</span></button></div></td>
          </tr>
          <tr class="hover:bg-secondary-fixed/30 transition-colors group">
            <td class="py-3 px-4"><div class="flex items-center gap-3"><div class="w-8 h-8 rounded bg-primary-fixed flex items-center justify-center text-primary"><span class="material-symbols-outlined text-[16px]">table_chart</span></div><span class="font-title-md text-title-md text-on-surface">Monthly Performance Metrics</span></div></td>
            <td class="py-3 px-4 text-on-surface-variant">September 2023</td><td class="py-3 px-4 text-on-surface-variant">All Active</td><td class="py-3 px-4 text-on-surface-variant">Oct 01, 2023</td>
            <td class="py-3 px-4"><span class="inline-flex items-center px-2 py-1 rounded-full bg-surface-container-highest text-on-surface font-label-sm text-label-sm"><span class="w-2 h-2 rounded-full bg-secondary mr-2"></span>Ready</span></td>
            <td class="py-3 px-4 text-right"><div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity"><button class="p-1 text-on-surface-variant hover:text-secondary transition-colors"><span class="material-symbols-outlined">visibility</span></button><button class="p-1 text-on-surface-variant hover:text-secondary transition-colors"><span class="material-symbols-outlined">download</span></button><button class="p-1 text-on-surface-variant hover:text-secondary transition-colors"><span class="material-symbols-outlined">share</span></button></div></td>
          </tr>
          <tr class="hover:bg-secondary-fixed/30 transition-colors group bg-surface-container/30">
            <td class="py-3 px-4"><div class="flex items-center gap-3"><div class="w-8 h-8 rounded bg-surface-container-high flex items-center justify-center text-on-surface-variant animate-pulse"><span class="material-symbols-outlined text-[16px]">pending</span></div><span class="font-title-md text-title-md text-on-surface">AI Insights: Delta Project</span></div></td>
            <td class="py-3 px-4 text-on-surface-variant">YTD 2023</td><td class="py-3 px-4 text-on-surface-variant">Delta</td><td class="py-3 px-4 text-on-surface-variant">Pending...</td>
            <td class="py-3 px-4"><span class="inline-flex items-center px-2 py-1 rounded-full bg-tertiary-fixed text-on-tertiary-fixed font-label-sm text-label-sm"><span class="material-symbols-outlined text-[14px] mr-1 animate-spin">sync</span>Generating</span></td>
            <td class="py-3 px-4 text-right"><div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity"><button class="p-1 text-outline hover:text-on-surface-variant transition-colors cursor-not-allowed"><span class="material-symbols-outlined">visibility</span></button></div></td>
          </tr>
          <tr class="hover:bg-secondary-fixed/30 transition-colors group">
            <td class="py-3 px-4"><div class="flex items-center gap-3"><div class="w-8 h-8 rounded bg-primary-fixed flex items-center justify-center text-primary"><span class="material-symbols-outlined text-[16px]">picture_as_pdf</span></div><span class="font-title-md text-title-md text-on-surface">Resource Allocation Overview</span></div></td>
            <td class="py-3 px-4 text-on-surface-variant">H1 2023</td><td class="py-3 px-4 text-on-surface-variant">Global</td><td class="py-3 px-4 text-on-surface-variant">Jul 05, 2023</td>
            <td class="py-3 px-4"><span class="inline-flex items-center px-2 py-1 rounded-full bg-surface-container-highest text-on-surface font-label-sm text-label-sm"><span class="w-2 h-2 rounded-full bg-secondary mr-2"></span>Ready</span></td>
            <td class="py-3 px-4 text-right"><div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity"><button class="p-1 text-on-surface-variant hover:text-secondary transition-colors"><span class="material-symbols-outlined">visibility</span></button><button class="p-1 text-on-surface-variant hover:text-secondary transition-colors"><span class="material-symbols-outlined">download</span></button><button class="p-1 text-on-surface-variant hover:text-secondary transition-colors"><span class="material-symbols-outlined">share</span></button></div></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="bg-surface-container-lowest border-t border-outline-variant p-4 flex items-center justify-between">
      <span class="font-body-md text-body-md text-on-surface-variant">Showing 1 to 4 of 24 entries</span>
      <div class="flex items-center gap-2">
        <button class="p-1 rounded border border-outline-variant text-on-surface-variant hover:bg-surface-variant/20 disabled:opacity-50" disabled><span class="material-symbols-outlined">chevron_left</span></button>
        <button class="w-8 h-8 rounded bg-secondary text-on-secondary font-title-md text-title-md flex items-center justify-center">1</button>
        <button class="w-8 h-8 rounded hover:bg-surface-variant/20 text-on-surface font-title-md text-title-md flex items-center justify-center">2</button>
        <button class="w-8 h-8 rounded hover:bg-surface-variant/20 text-on-surface font-title-md text-title-md flex items-center justify-center">3</button>
        <span class="text-on-surface-variant">...</span>
        <button class="p-1 rounded border border-outline-variant text-on-surface-variant hover:bg-surface-variant/20"><span class="material-symbols-outlined">chevron_right</span></button>
      </div>
    </div>
  </div>
</div>
`);
