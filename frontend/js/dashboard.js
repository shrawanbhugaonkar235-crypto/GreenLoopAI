/**
 * GreenLoopAI — Dashboard View Logic
 * 
 * Fetches real platform analytics and renders dynamic stat cards or genuine empty states.
 */

const Dashboard = {
  async init() {
    this.initBannerActions();
    await this.refreshDashboardStats();
  },

  initBannerActions() {
    const connectBtn = document.getElementById('btn-dashboard-connect');
    if (connectBtn) {
      connectBtn.addEventListener('click', () => {
        App.openModal('modal-backend-notice');
      });
    }

    const verifyShortcutBtn = document.getElementById('btn-dashboard-verify');
    if (verifyShortcutBtn) {
      verifyShortcutBtn.addEventListener('click', () => {
        Navigation.switchView('verify');
      });
    }
  },

  async refreshDashboardStats() {
    try {
      const summary = await window.GreenLoopAPI.getAnalyticsSummary();
      if (!summary) return;

      // Update stat card numbers if available in DOM
      const cardVerifications = document.getElementById('dash-stat-verifications');
      const cardGreenCoins = document.getElementById('dash-stat-greencoins');
      const cardEprCredits = document.getElementById('dash-stat-epr');
      const cardSuccessRate = document.getElementById('dash-stat-rate');

      if (summary.has_data) {
        if (cardVerifications) cardVerifications.textContent = summary.total_verifications.toLocaleString();
        if (cardGreenCoins) cardGreenCoins.textContent = summary.total_greencoins_issued.toLocaleString();
        if (cardEprCredits) cardEprCredits.textContent = summary.total_epr_credits.toFixed(3);
        if (cardSuccessRate) cardSuccessRate.textContent = `${summary.verification_success_rate.toFixed(1)}%`;
      } else {
        if (cardVerifications) cardVerifications.textContent = '0';
        if (cardGreenCoins) cardGreenCoins.textContent = '0';
        if (cardEprCredits) cardEprCredits.textContent = '0.000';
        if (cardSuccessRate) cardSuccessRate.textContent = '0.0%';
      }
    } catch (err) {
      // Offline / not reachable
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  Dashboard.init();
});

window.Dashboard = Dashboard;
