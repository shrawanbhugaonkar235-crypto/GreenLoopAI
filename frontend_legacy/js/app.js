/**
 * GreenLoopAI — Core Application Bootstrap & UI Utilities
 */

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});

const App = {
  init() {
    this.initPreferences();
    this.initModals();
    this.initGlobalEvents();
    console.info('GreenLoopAI application initialized in frontend-only mode. Ready for backend integration.');
  },

  /**
   * Loads and applies saved UI preferences from localStorage (Theme, Layout, Font Size)
   */
  initPreferences() {
    try {
      const savedTheme = localStorage.getItem('greenloop_theme') || 'light';
      const savedDensity = localStorage.getItem('greenloop_density') || 'comfortable';
      const savedFontSize = localStorage.getItem('greenloop_font_size') || 'medium';
      const savedReducedMotion = localStorage.getItem('greenloop_reduced_motion') === 'true';

      document.documentElement.setAttribute('data-theme', savedTheme);
      document.documentElement.setAttribute('data-density', savedDensity);
      document.documentElement.setAttribute('data-font-size', savedFontSize);
      
      if (savedReducedMotion) {
        document.body.classList.add('reduced-motion');
      }

      // Sync settings form controls if available
      const themeSelect = document.getElementById('setting-theme');
      const densitySelect = document.getElementById('setting-density');
      const fontSelect = document.getElementById('setting-font-size');
      const motionToggle = document.getElementById('setting-reduced-motion');

      if (themeSelect) themeSelect.value = savedTheme;
      if (densitySelect) densitySelect.value = savedDensity;
      if (fontSelect) fontSelect.value = savedFontSize;
      if (motionToggle) motionToggle.checked = savedReducedMotion;
    } catch (e) {
      console.warn('LocalStorage unavailable for preferences:', e);
    }
  },

  /**
   * Initializes modal backdrop interactions
   */
  initModals() {
    document.querySelectorAll('[data-modal-close]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const modal = btn.closest('.modal-backdrop');
        if (modal) {
          App.closeModal(modal.id);
        }
      });
    });

    // Close on backdrop click
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) {
          App.closeModal(backdrop.id);
        }
      });
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal-backdrop.active');
        if (activeModal) {
          App.closeModal(activeModal.id);
        }
      }
    });
  },

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  },

  /**
   * Toast notification display engine
   * @param {string} title - Header of notification
   * @param {string} message - Body text
   * @param {'info'|'success'|'warning'|'danger'} type - Status style
   * @param {number} duration - Milliseconds to show (default 4500)
   */
  showToast(title, message, type = 'info', duration = 4500) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let iconSvg = '';
    if (type === 'success') {
      iconSvg = '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>';
    } else if (type === 'warning') {
      iconSvg = '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>';
    } else if (type === 'danger') {
      iconSvg = '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10" stroke-width="2"/><line x1="15" y1="9" x2="9" y2="15" stroke-width="2"/><line x1="9" y1="9" x2="15" y2="15" stroke-width="2"/></svg>';
    } else {
      iconSvg = '<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10" stroke-width="2"/><line x1="12" y1="16" x2="12" y2="12" stroke-width="2"/><line x1="12" y1="8" x2="12.01" y2="8" stroke-width="2"/></svg>';
    }

    toast.innerHTML = `
      ${iconSvg}
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close-btn" aria-label="Close notification">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"><line x1="18" y1="6" x2="6" y2="18" stroke-width="2"/><line x1="6" y1="6" x2="18" y2="18" stroke-width="2"/></svg>
      </button>
    `;

    const closeBtn = toast.querySelector('.toast-close-btn');
    closeBtn.addEventListener('click', () => {
      this.dismissToast(toast);
    });

    container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => {
        this.dismissToast(toast);
      }, duration);
    }
  },

  dismissToast(toastElement) {
    if (!toastElement || toastElement.classList.contains('toast-hiding')) return;
    toastElement.classList.add('toast-hiding');
    setTimeout(() => {
      if (toastElement.parentNode) {
        toastElement.parentNode.removeChild(toastElement);
      }
    }, 200);
  },

  initGlobalEvents() {
    // Topbar Search Input Feedback
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && searchInput.value.trim().length > 0) {
          App.showToast('Search Query', `Search for "${searchInput.value.trim()}" requires connected database.`, 'info');
        }
      });
    }

    // Topbar Notifications Button
    const notifBtn = document.getElementById('btn-notifications');
    if (notifBtn) {
      notifBtn.addEventListener('click', () => {
        App.openModal('modal-notifications');
      });
    }

    // User Profile Chip
    const userChip = document.getElementById('user-profile-chip');
    if (userChip) {
      userChip.addEventListener('click', () => {
        App.showToast('Authentication Status', 'No user session or auth provider connected.', 'info');
      });
    }
  }
};

window.App = App;
