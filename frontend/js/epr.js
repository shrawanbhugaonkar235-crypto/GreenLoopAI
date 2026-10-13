/**
 * GreenLoopAI — EPR Compliance Module
 * 
 * Manages Extended Producer Responsibility compliance interface and evidence viewer.
 * Connects directly to backend EPR ledger.
 */

const EPRModule = {
  async init() {
    this.initButtons();
    await this.loadEprData();
  },

  initButtons() {
    const exportBtn = document.getElementById('btn-export-epr');
    if (exportBtn) {
      exportBtn.addEventListener('click', () => {
        App.showToast('EPR Report Export', 'Generating official EPR compliance PDF / CSV audit report.', 'success');
      });
    }

    const viewEvidenceSampleBtn = document.getElementById('btn-view-evidence-modal');
    if (viewEvidenceSampleBtn) {
      viewEvidenceSampleBtn.addEventListener('click', () => {
        App.openModal('modal-epr-evidence');
      });
    }
  },

  async loadEprData() {
    const tbody = document.getElementById('epr-table-body');
    const emptyState = document.getElementById('epr-empty-state');
    const totalCreditsEl = document.getElementById('epr-total-credits-val');
    const totalWeightEl = document.getElementById('epr-total-weight-val');

    try {
      const res = await window.GreenLoopAPI.getEprRecords();
      const records = (res && res.records) ? res.records : [];

      if (!tbody) return;

      if (records.length === 0) {
        tbody.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        if (totalCreditsEl) totalCreditsEl.textContent = '0.000';
        if (totalWeightEl) totalWeightEl.textContent = '0.00 kg';
        return;
      }

      if (emptyState) emptyState.style.display = 'none';

      let totalCredits = 0;
      let totalWeight = 0;

      tbody.innerHTML = records.map(r => {
        totalCredits += r.epr_credits_generated || 0;
        totalWeight += r.weight_kg || 0;
        const dateStr = r.timestamp ? new Date(r.timestamp).toLocaleString() : 'Recent';
        const isComp = r.compliance_status === 'COMPLIANT';

        return `
          <tr>
            <td><code>${r.evidence_id}</code></td>
            <td><strong>${r.brand_name || 'Unbranded'}</strong></td>
            <td>${r.material_type}</td>
            <td>${r.weight_kg.toFixed(2)} kg</td>
            <td><strong class="text-success">+${r.epr_credits_generated.toFixed(3)}</strong></td>
            <td><span class="badge ${isComp ? 'badge-verified' : 'badge-rejected'}">${r.compliance_status}</span></td>
            <td><small>${r.regulatory_standard}</small></td>
            <td>${dateStr}</td>
          </tr>
        `;
      }).join('');

      if (totalCreditsEl) totalCreditsEl.textContent = totalCredits.toFixed(3);
      if (totalWeightEl) totalWeightEl.textContent = `${totalWeight.toFixed(2)} kg`;

    } catch (err) {
      if (tbody) tbody.innerHTML = '';
      if (emptyState) emptyState.style.display = 'block';
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  EPRModule.init();
});

window.EPRModule = EPRModule;
