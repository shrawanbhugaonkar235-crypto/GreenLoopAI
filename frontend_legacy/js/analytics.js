/**
 * GreenLoopAI — Analytics & Settings Management Module
 */

const AnalyticsModule = {
  init() {
    this.initTimeIntervalFilters();
    this.initSettingsControls();
  },

  initTimeIntervalFilters() {
    document.querySelectorAll('.analytics-interval-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.analytics-interval-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const interval = btn.getAttribute('data-interval');
        App.showToast('Time Filter', `Range set to: ${interval} (No backend records available)`, 'info', 2000);
      });
    });
  },

  initSettingsControls() {
    // Theme Switcher
    const themeSelect = document.getElementById('setting-theme');
    if (themeSelect) {
      themeSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        document.documentElement.setAttribute('data-theme', val);
        try {
          localStorage.setItem('greenloop_theme', val);
          App.showToast('Appearance Updated', `Switched to ${val} mode.`, 'success', 2000);
        } catch (err) {}
      });
    }

    // UI Density Switcher
    const densitySelect = document.getElementById('setting-density');
    if (densitySelect) {
      densitySelect.addEventListener('change', (e) => {
        const val = e.target.value;
        document.documentElement.setAttribute('data-density', val);
        try {
          localStorage.setItem('greenloop_density', val);
          App.showToast('Layout Updated', `Density set to ${val}.`, 'success', 2000);
        } catch (err) {}
      });
    }

    // Font Size Switcher
    const fontSizeSelect = document.getElementById('setting-font-size');
    if (fontSizeSelect) {
      fontSizeSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        document.documentElement.setAttribute('data-font-size', val);
        try {
          localStorage.setItem('greenloop_font_size', val);
          App.showToast('Font Size Updated', `Scale set to ${val}.`, 'success', 2000);
        } catch (err) {}
      });
    }

    // Reduced Motion Toggle
    const motionToggle = document.getElementById('setting-reduced-motion');
    if (motionToggle) {
      motionToggle.addEventListener('change', (e) => {
        const checked = e.target.checked;
        if (checked) {
          document.body.classList.add('reduced-motion');
        } else {
          document.body.classList.remove('reduced-motion');
        }
        try {
          localStorage.setItem('greenloop_reduced_motion', checked ? 'true' : 'false');
          App.showToast('Accessibility Updated', `Reduced motion: ${checked ? 'Enabled' : 'Disabled'}.`, 'info', 2000);
        } catch (err) {}
      });
    }

    // Notifications toggle
    const notifToggle = document.getElementById('setting-notifications');
    if (notifToggle) {
      notifToggle.addEventListener('change', (e) => {
        App.showToast('Notifications Preference', `In-app notifications ${e.target.checked ? 'enabled' : 'disabled'}.`, 'info', 2000);
      });
    }

    // Reset settings button
    const resetBtn = document.getElementById('btn-reset-settings');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        try {
          localStorage.removeItem('greenloop_theme');
          localStorage.removeItem('greenloop_density');
          localStorage.removeItem('greenloop_font_size');
          localStorage.removeItem('greenloop_reduced_motion');
        } catch (e) {}
        document.documentElement.setAttribute('data-theme', 'light');
        document.documentElement.setAttribute('data-density', 'comfortable');
        document.documentElement.setAttribute('data-font-size', 'medium');
        document.body.classList.remove('reduced-motion');

        if (themeSelect) themeSelect.value = 'light';
        if (densitySelect) densitySelect.value = 'comfortable';
        if (fontSizeSelect) fontSizeSelect.value = 'medium';
        if (motionToggle) motionToggle.checked = false;

        App.showToast('Settings Reset', 'Preferences restored to defaults.', 'success');
      });
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  AnalyticsModule.init();
});

window.AnalyticsModule = AnalyticsModule;
