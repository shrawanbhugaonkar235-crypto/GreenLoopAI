/**
 * GreenLoopAI — Scan History View Logic
 * 
 * Fetches real verification records from database and renders table or clean empty state.
 * Never displays fake demo records.
 */

const HistoryModule = {
  async init() {
    this.initSearchAndFilters();
    await this.loadHistory();
  },

  initSearchAndFilters() {
    const searchInput = document.getElementById('history-search-input');
    const filterStatus = document.getElementById('history-filter-status');
    const filterMaterial = document.getElementById('history-filter-material');

    if (searchInput) {
      searchInput.addEventListener('input', () => this.loadHistory());
    }

    if (filterStatus) {
      filterStatus.addEventListener('change', () => this.loadHistory());
    }

    if (filterMaterial) {
      filterMaterial.addEventListener('change', () => this.loadHistory());
    }
  },

  async loadHistory() {
    const tbody = document.getElementById('history-table-body');
    const emptyState = document.getElementById('history-empty-state');
    const searchInput = document.getElementById('history-search-input');
    const filterStatus = document.getElementById('history-filter-status');
    const filterMaterial = document.getElementById('history-filter-material');

    if (!tbody) return;

    try {
      const filters = {};
      if (filterStatus && filterStatus.value && filterStatus.value !== 'all') {
        filters.status = filterStatus.value.toUpperCase();
      }
      if (filterMaterial && filterMaterial.value && filterMaterial.value !== 'all') {
        filters.category = filterMaterial.value;
      }

      const res = await window.GreenLoopAPI.getVerificationHistory(filters);
      let items = (res && res.items) ? res.items : [];

      if (searchInput && searchInput.value.trim()) {
        const q = searchInput.value.toLowerCase().trim();
        items = items.filter(it => 
          (it.waste_category && it.waste_category.toLowerCase().includes(q)) ||
          (it.detected_label && it.detected_label.toLowerCase().includes(q)) ||
          (it.brand_name && it.brand_name.toLowerCase().includes(q)) ||
          (it.id && it.id.toLowerCase().includes(q))
        );
      }

      if (items.length === 0) {
        tbody.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        return;
      }

      if (emptyState) emptyState.style.display = 'none';

      tbody.innerHTML = items.map(item => {
        const dateStr = item.created_at ? new Date(item.created_at).toLocaleString() : 'Recent';
        const isVerified = item.status === 'VERIFIED';
        const badgeClass = isVerified ? 'badge-verified' : 'badge-rejected';

        return `
          <tr>
            <td><code>${item.id}</code></td>
            <td>${dateStr}</td>
            <td><strong>${item.detected_label || item.waste_category}</strong> <span class="text-muted">(${item.waste_category})</span></td>
            <td>${item.brand_name || '<span class="text-muted">Unbranded</span>'}</td>
            <td><strong>${item.composite_score.toFixed(1)}%</strong></td>
            <td><span class="badge ${badgeClass}">${item.status}</span></td>
            <td><span class="greencoin-pill">+${item.greencoins_awarded} 🪙</span></td>
            <td>${item.epr_evidence_id ? `<code>${item.epr_evidence_id}</code>` : '<span class="text-muted">—</span>'}</td>
          </tr>
        `;
      }).join('');

    } catch (err) {
      if (tbody) tbody.innerHTML = '';
      if (emptyState) emptyState.style.display = 'block';
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  HistoryModule.init();
});

window.HistoryModule = HistoryModule;
