registerPage('admin', () => `
<div class="p-xl bg-background max-w-container-max mx-auto space-y-xl">
  <div>
    <h1 class="font-headline-lg text-headline-lg text-on-surface">Administration & Governance Control</h1>
    <p class="text-on-surface-variant mt-2 font-body-md text-body-md">Manage user permissions, review workflow notifications, configure organization settings, and inspect audit logs.</p>
  </div>

  <!-- Real-time Admin Notification Center Card -->
  <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-sm p-6 space-y-4">
    <div class="flex justify-between items-center pb-3 border-b border-surface-container-highest">
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-secondary text-2xl">notifications_active</span>
        <h2 class="font-title-lg text-title-lg text-on-surface font-bold">Admin Notification Center</h2>
        <span class="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-bold rounded-full">2 Active</span>
      </div>
      <button onclick="alert('All notifications marked as read');" class="text-xs text-on-surface-variant hover:text-secondary font-medium">Mark All Read</button>
    </div>

    <div class="space-y-3">
      <!-- Notification Item 1 -->
      <div class="p-4 rounded-lg border-l-4 border-green-600 bg-surface-container/40 flex justify-between items-start gap-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-green-700 font-bold text-xs">✅ REPORT APPROVED</span>
            <span class="text-[11px] text-on-surface-variant">25 August 2026, 14:30</span>
          </div>
          <p class="text-xs font-medium text-on-surface mt-1">'Q2 2026 Executive Summary' has been approved by Grace Wanjiku (Program Manager).</p>
          <a href="#reports" class="text-xs text-secondary font-bold hover:underline inline-block mt-2">[ VIEW REPORT ]</a>
        </div>
        <button onclick="this.parentElement.remove()" class="text-on-surface-variant hover:text-secondary text-sm">✕</button>
      </div>

      <!-- Notification Item 2 -->
      <div class="p-4 rounded-lg border-l-4 border-red-600 bg-surface-container/40 flex justify-between items-start gap-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-red-700 font-bold text-xs">🔴 REPORT REQUIRES REVISION</span>
            <span class="text-[11px] text-on-surface-variant">25 August 2026, 11:15</span>
          </div>
          <p class="text-xs font-medium text-on-surface mt-1">'July 2026 Vocational Milestone' returned for revision. Reason: Vocational completion figures require verification with Nakuru training center.</p>
          <a href="#reports" class="text-xs text-secondary font-bold hover:underline inline-block mt-2">[ REVISE REPORT ]</a>
        </div>
        <button onclick="this.parentElement.remove()" class="text-on-surface-variant hover:text-secondary text-sm">✕</button>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-12 gap-md">
    <!-- Users & Roles -->
    <div class="col-span-12 lg:col-span-8 bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] p-lg flex flex-col h-[500px]">
      <div class="flex justify-between items-center mb-md pb-md border-b border-surface-container-highest">
        <div>
          <h2 class="font-title-lg text-title-lg text-on-surface flex items-center gap-2">
            <span class="material-symbols-outlined text-secondary">group</span> Users &amp; Role-Based Access Control
          </h2>
        </div>
      </div>
      <div class="flex-1 overflow-auto">
        <table class="w-full text-left">
          <thead class="bg-surface-container-low font-label-sm text-label-sm text-on-surface-variant uppercase sticky top-0">
            <tr><th class="py-2 px-4">User</th><th class="py-2 px-4">Role</th><th class="py-2 px-4">Approval Rights</th><th class="py-2 px-4">Status</th></tr>
          </thead>
          <tbody>
            <tr class="border-b border-surface-container-highest hover:bg-secondary-fixed/30 transition-colors">
              <td class="py-3 px-4 font-bold">Program Administrator</td>
              <td class="py-3 px-4">Administrator</td>
              <td class="py-3 px-4 text-xs text-on-surface-variant">Generates / Submits Only</td>
              <td class="py-3 px-4"><span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-bold">Active</span></td>
            </tr>
            <tr class="border-b border-surface-container-highest hover:bg-secondary-fixed/30 transition-colors">
              <td class="py-3 px-4 font-bold">Grace Wanjiku</td>
              <td class="py-3 px-4">Program Manager</td>
              <td class="py-3 px-4 text-xs font-bold text-secondary">Manager Approver &amp; Rejecter</td>
              <td class="py-3 px-4"><span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-bold">Active</span></td>
            </tr>
            <tr class="border-b border-surface-container-highest hover:bg-secondary-fixed/30 transition-colors">
              <td class="py-3 px-4 font-bold">David Mwangi</td>
              <td class="py-3 px-4">Leadership / Viewer</td>
              <td class="py-3 px-4 text-xs text-on-surface-variant">Read-only Access</td>
              <td class="py-3 px-4"><span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-bold">Active</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- General Settings -->
    <div class="col-span-12 lg:col-span-4 bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] p-lg flex flex-col h-[500px]">
      <div class="mb-md pb-md border-b border-surface-container-highest">
        <h2 class="font-title-lg text-title-lg text-on-surface flex items-center gap-2">
          <span class="material-symbols-outlined text-secondary">tune</span> Governance Policies
        </h2>
      </div>
      <div class="flex-1 overflow-auto space-y-4 text-xs">
        <div>
          <label class="block font-bold text-on-surface mb-1">Organization</label>
          <input class="w-full h-9 px-3 bg-surface border border-outline-variant rounded" type="text" value="KPC Inuka Foundation" readonly/>
        </div>
        <div>
          <label class="block font-bold text-on-surface mb-1">Approval Protocol</label>
          <p class="text-on-surface-variant bg-surface-container p-2.5 rounded border border-outline-variant">
            Strict Two-Tier Governance: Administrator generates verified snapshots. Program Manager reviews and signs off.
          </p>
        </div>
        <div>
          <label class="block font-bold text-on-surface mb-1">Audit Trail Policy</label>
          <p class="text-on-surface-variant bg-surface-container p-2.5 rounded border border-outline-variant">
            Immutable timestamps, user identity logging, and snapshot versioning enabled.
          </p>
        </div>
      </div>
    </div>

    <!-- Audit Logs -->
    <div class="col-span-12 bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-[0px_4px_6px_-1px_rgba(15,23,42,0.05)] p-lg flex flex-col h-[400px]">
      <div class="flex justify-between items-center mb-md pb-md border-b border-surface-container-highest">
        <h2 class="font-title-lg text-title-lg text-on-surface flex items-center gap-2">
          <span class="material-symbols-outlined text-secondary">history</span> System Audit Trail
        </h2>
      </div>
      <div class="flex-1 overflow-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-surface-container-low text-on-surface-variant uppercase sticky top-0">
            <tr><th class="py-2 px-4">Timestamp</th><th class="py-2 px-4">User</th><th class="py-2 px-4">Action</th><th class="py-2 px-4">Details</th></tr>
          </thead>
          <tbody class="divide-y divide-surface-container">
            <tr><td class="py-2 px-4">2026-08-25 15:40</td><td class="py-2 px-4 font-bold">Grace Wanjiku</td><td class="py-2 px-4 font-bold text-green-700">REPORT_APPROVED</td><td class="py-2 px-4">Approved 'Q2 2026 Executive Summary'</td></tr>
            <tr><td class="py-2 px-4">2026-08-25 15:30</td><td class="py-2 px-4 font-bold">Program Administrator</td><td class="py-2 px-4 font-bold text-secondary">REPORT_SENT_TO_MANAGER</td><td class="py-2 px-4">Submitted 'August 2026 Monthly Donor Report' to Manager</td></tr>
            <tr><td class="py-2 px-4">2026-08-25 15:28</td><td class="py-2 px-4 font-bold">Program Administrator</td><td class="py-2 px-4 font-bold text-secondary">REPORT_GENERATED</td><td class="py-2 px-4">Created snapshot v1 with 96% completeness</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
`);
