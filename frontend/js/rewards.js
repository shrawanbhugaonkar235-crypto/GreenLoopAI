/**
 * GreenLoopAI — GreenCoins & Rewards Logic
 * 
 * Fetches real transaction ledger and balance from database.
 * Never generates fake transactions or hardcoded balances.
 */

const RewardsModule = {
  async init() {
    this.initActionButtons();
    await this.loadRewardsData();
  },

  initActionButtons() {
    const redeemBtn = document.getElementById('btn-redeem-coins');
    if (redeemBtn) {
      redeemBtn.addEventListener('click', () => {
        App.showToast('Reward Redemption', 'Select voucher partner to redeem earned GreenCoins.', 'info');
      });
    }

    const transferBtn = document.getElementById('btn-transfer-coins');
    if (transferBtn) {
      transferBtn.addEventListener('click', () => {
        App.showToast('GreenCoins Transfer', 'Enter recipient citizen ID or municipal wallet address.', 'info');
      });
    }
  },

  async loadRewardsData() {
    const balanceEl = document.getElementById('greencoins-balance-value');
    const tbody = document.getElementById('rewards-table-body');
    const emptyState = document.getElementById('rewards-empty-state');

    try {
      // 1. Balance
      const balanceRes = await window.GreenLoopAPI.getGreenCoinsBalance();
      if (balanceEl && balanceRes) {
        balanceEl.textContent = balanceRes.total_balance !== undefined ? balanceRes.total_balance.toLocaleString() : '0';
      }

      // 2. Transactions
      const txRes = await window.GreenLoopAPI.getGreenCoinsTransactions();
      const txs = (txRes && txRes.transactions) ? txRes.transactions : [];

      if (!tbody) return;

      if (txs.length === 0) {
        tbody.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        return;
      }

      if (emptyState) emptyState.style.display = 'none';

      tbody.innerHTML = txs.map(tx => {
        const dateStr = tx.timestamp ? new Date(tx.timestamp).toLocaleString() : 'Recent';
        return `
          <tr>
            <td><code>${tx.id.substring(0, 8)}...</code></td>
            <td>${dateStr}</td>
            <td><span class="badge badge-verified">${tx.transaction_type}</span></td>
            <td><span class="badge tier-badge-${tx.reward_tier.toLowerCase()}">${tx.reward_tier}</span></td>
            <td><strong>+${tx.amount} 🪙</strong></td>
            <td><small class="text-muted">${tx.calculation_basis || 'Verified Waste'}</small></td>
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
  RewardsModule.init();
});

window.RewardsModule = RewardsModule;
