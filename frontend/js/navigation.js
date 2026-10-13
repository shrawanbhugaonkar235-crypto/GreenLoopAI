/**
 * GreenLoopAI — Navigation & View Routing Engine
 */

const Navigation = {
  activeView: 'dashboard',

  viewTitles: {
    dashboard: 'Dashboard',
    verify: 'Verify Waste',
    result: 'Verification Result',
    recycling: 'How to Recycle',
    history: 'Scan History',
    rewards: 'GreenCoins',
    epr: 'EPR Compliance',
    analytics: 'Analytics',
    settings: 'Settings'
  },

  init() {
    this.initNavLinks();
    this.initMobileSidebar();
    this.initQuickTriggers();
  },

  initNavLinks() {
    document.querySelectorAll('[data-view-target]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetView = link.getAttribute('data-view-target');
        if (targetView) {
          this.switchView(targetView);
          this.closeMobileSidebar();
        }
      });
    });
  },

  initMobileSidebar() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const overlay = document.getElementById('sidebar-overlay');
    const sidebar = document.getElementById('app-sidebar');

    if (toggleBtn && sidebar) {
      toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('mobile-open');
        if (overlay) overlay.classList.toggle('active');
      });
    }

    if (overlay && sidebar) {
      overlay.addEventListener('click', () => {
        this.closeMobileSidebar();
      });
    }
  },

  closeMobileSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (sidebar) sidebar.classList.remove('mobile-open');
    if (overlay) overlay.classList.remove('active');
  },

  switchView(viewId) {
    const targetSection = document.getElementById(`view-${viewId}`);
    if (!targetSection) return;

    // Update active nav link
    document.querySelectorAll('.app-sidebar .nav-item').forEach(item => {
      if (item.getAttribute('data-view-target') === viewId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Hide all view sections and show target
    document.querySelectorAll('.view-section').forEach(section => {
      section.classList.remove('active');
    });
    targetSection.classList.add('active');

    // Update breadcrumb
    const currentCrumb = document.getElementById('breadcrumb-current');
    if (currentCrumb) {
      currentCrumb.textContent = this.viewTitles[viewId] || 'Workspace';
    }

    this.activeView = viewId;

    // Scroll workspace back to top
    const workspace = document.querySelector('.app-workspace');
    if (workspace) workspace.scrollTop = 0;
  },

  navigateTo(viewId) {
    this.switchView(viewId);
  },

  initQuickTriggers() {
    document.querySelectorAll('[data-navigate]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const target = btn.getAttribute('data-navigate');
        if (target) {
          this.switchView(target);
        }
      });
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  Navigation.init();
});

window.Navigation = Navigation;
