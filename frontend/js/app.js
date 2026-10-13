/* ==========================================================================
   GREENLOOPAI — Application bootstrap
   Navigation, login/registration, preferences and the service health probe.
   ========================================================================== */

var GL = window.GL || {};
window.GL = GL;

GL.app = {};

var VIEW_TITLES = {
  dashboard: 'Dashboard',
  verify: 'Verify Waste',
  result: 'Verification Result',
  greencoins: 'GreenCoins',
  history: 'History',
  settings: 'Settings',
};

/* --------------------------------------------------------------------------
   Navigation
   -------------------------------------------------------------------------- */

GL.app.navigate = function (view) {
  if (!VIEW_TITLES[view]) {
    view = 'dashboard';
  }

  // Sections
  var sections = document.querySelectorAll('.view-section');
  Array.prototype.forEach.call(sections, function (section) {
    section.classList.toggle('active', section.id === 'view-' + view);
  });

  // Sidebar items
  var items = document.querySelectorAll('.nav-item[data-view]');
  Array.prototype.forEach.call(items, function (item) {
    item.classList.toggle('active', item.getAttribute('data-view') === view);
  });

  GL.ui.setText('breadcrumb-current', VIEW_TITLES[view]);

  // Re-render the view being entered so it always reflects current state.
  if (view === 'dashboard') {
    GL.views.renderDashboard();
  } else if (view === 'result') {
    GL.views.renderResult();
  } else if (view === 'greencoins') {
    GL.views.renderGreenCoins();
  } else if (view === 'history') {
    GL.views.renderHistory();
  }

  GL.app.closeMobileSidebar();

  var workspace = GL.ui.byId('app-workspace');
  if (workspace) {
    workspace.scrollTop = 0;
  }
};

GL.app.closeMobileSidebar = function () {
  var sidebar = GL.ui.byId('app-sidebar');
  var overlay = GL.ui.byId('sidebar-overlay');
  if (sidebar) {
    sidebar.classList.remove('mobile-open');
  }
  if (overlay) {
    overlay.classList.remove('active');
  }
};

GL.app.toggleMobileSidebar = function () {
  var sidebar = GL.ui.byId('app-sidebar');
  var overlay = GL.ui.byId('sidebar-overlay');
  if (!sidebar || !overlay) {
    return;
  }
  var isOpen = sidebar.classList.toggle('mobile-open');
  overlay.classList.toggle('active', isOpen);
};

/* --------------------------------------------------------------------------
   Authentication (frontend-only, in-memory)
   -------------------------------------------------------------------------- */

var authMode = 'login';

GL.app.setAuthMode = function (mode) {
  authMode = mode;
  var isRegister = mode === 'register';

  GL.ui.setText('auth-title', isRegister ? 'Create your account' : 'Sign in to your account');
  GL.ui.setText(
    'auth-subtitle',
    isRegister
      ? 'Register as a citizen to verify your waste disposal and collect GreenCoins.'
      : 'Verify your waste disposal with AI and earn GreenCoins for every validated contribution.'
  );
  GL.ui.setText('auth-submit-label', isRegister ? 'Create account' : 'Sign in');
  GL.ui.setText('auth-switch-text', isRegister ? 'Already registered?' : 'New to GreenLoopAI?');

  var switchBtn = GL.ui.byId('auth-switch-btn');
  if (switchBtn) {
    switchBtn.textContent = isRegister ? 'Sign in instead' : 'Create an account';
  }

  var nameGroup = GL.ui.byId('name-field-group');
  if (nameGroup) {
    nameGroup.classList.toggle('is-hidden', !isRegister);
  }

  var password = GL.ui.byId('auth-password');
  if (password) {
    password.setAttribute('autocomplete', isRegister ? 'new-password' : 'current-password');
  }

  GL.app.clearFieldError('name');
  GL.app.clearFieldError('email');
  GL.app.clearFieldError('password');
};

GL.app.showFieldError = function (field, message) {
  var errorEl = GL.ui.byId(field + '-error');
  var inputEl = GL.ui.byId('auth-' + field);
  if (errorEl) {
    errorEl.textContent = message;
    errorEl.classList.add('active');
  }
  if (inputEl) {
    inputEl.classList.add('has-error');
    inputEl.setAttribute('aria-invalid', 'true');
  }
};

GL.app.clearFieldError = function (field) {
  var errorEl = GL.ui.byId(field + '-error');
  var inputEl = GL.ui.byId('auth-' + field);
  if (errorEl) {
    errorEl.textContent = '';
    errorEl.classList.remove('active');
  }
  if (inputEl) {
    inputEl.classList.remove('has-error');
    inputEl.removeAttribute('aria-invalid');
  }
};

GL.app.handleAuthSubmit = function (event) {
  event.preventDefault();

  var nameEl = GL.ui.byId('auth-name');
  var emailEl = GL.ui.byId('auth-email');
  var passwordEl = GL.ui.byId('auth-password');

  var name = nameEl ? nameEl.value.trim() : '';
  var email = emailEl ? emailEl.value.trim() : '';
  var password = passwordEl ? passwordEl.value : '';

  GL.app.clearFieldError('name');
  GL.app.clearFieldError('email');
  GL.app.clearFieldError('password');

  var valid = true;

  if (authMode === 'register' && name.length < 2) {
    GL.app.showFieldError('name', 'Please enter your full name.');
    valid = false;
  }

  if (!email) {
    GL.app.showFieldError('email', 'Email address is required.');
    valid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    GL.app.showFieldError('email', 'Enter a valid email address, e.g. you@example.com.');
    valid = false;
  }

  if (!password) {
    GL.app.showFieldError('password', 'Password is required.');
    valid = false;
  } else if (password.length < 6) {
    GL.app.showFieldError('password', 'Password must be at least 6 characters.');
    valid = false;
  }

  if (!valid) {
    GL.ui.toast('danger', 'Check your details', 'Please correct the highlighted fields.');
    return;
  }

  var submitBtn = GL.ui.byId('auth-submit-btn');
  GL.ui.setBusy(submitBtn, true);

  var authAction = authMode === 'register'
    ? GL.api.register(name, email, password)
    : GL.api.login(email, password);

  authAction
    .then(function (res) {
      GL.setToken(res.access_token);
      GL.state.user = res.user;

      if (passwordEl) {
        passwordEl.value = '';
      }

      GL.app.enterApp();
      GL.ui.toast(
        'success',
        authMode === 'register' ? 'Account created' : 'Signed in',
        'Welcome to GreenLoopAI, ' + res.user.name + '.'
      );
    })
    .catch(function (err) {
      var message = (err && err.message) || 'Authentication failed.';
      GL.ui.toast('danger', 'Authentication error', message);
      if (message.toLowerCase().indexOf('email') !== -1) {
        GL.app.showFieldError('email', message);
      } else if (message.toLowerCase().indexOf('password') !== -1) {
        GL.app.showFieldError('password', message);
      }
    })
    .then(function () {
      GL.ui.setBusy(submitBtn, false);
    });
};

GL.app.enterApp = function () {
  var auth = GL.ui.byId('auth-screen');
  var app = GL.ui.byId('app-root');
  if (auth) {
    auth.classList.remove('active');
  }
  if (app) {
    app.classList.remove('is-hidden');
  }

  var user = GL.state.user || { name: 'Citizen', email: '' };
  GL.ui.setText('topbar-user-name', user.name);
  GL.ui.setText('topbar-user-initials', GL.ui.initials(user.name));

  var settingsName = GL.ui.byId('settings-name');
  var settingsEmail = GL.ui.byId('settings-email');
  if (settingsName) {
    settingsName.value = user.name;
  }
  if (settingsEmail) {
    settingsEmail.value = user.email;
  }

  GL.views.renderAll();
  GL.app.navigate('dashboard');
  GL.app.probeService();
  GL.app.loadCitizenData();
};

/* --------------------------------------------------------------------------
   Server-persisted data for the signed-in citizen
   -------------------------------------------------------------------------- */

GL.app.refreshGreenCoins = function () {
  return GL.api
    .fetchGreenCoins()
    .then(function (summary) {
      GL.state.coinsSummary = summary;
    })
    .catch(function () {
      // Leave the previous summary in place
    });
};

GL.app.loadCitizenData = function () {
  GL.state.loadingHistory = true;
  GL.state.historyError = null;
  GL.views.renderAll();

  return Promise.all([
    GL.api.fetchHistory().then(function (rows) {
      GL.state.history = rows.map(GL.api.toEntry);
    }),
    GL.api.fetchTransactions().then(function (txs) {
      GL.state.transactions = txs;
    }),
    GL.app.refreshGreenCoins(),
  ])
    .catch(function (err) {
      GL.state.historyError =
        (err && err.message) || 'Could not load your saved verifications.';
    })
    .then(function () {
      GL.state.loadingHistory = false;
      GL.views.renderAll();
    });
};

GL.app.logout = function () {
  GL.setToken(null);
  GL.state.user = null;
  GL.state.lastResult = null;
  GL.state.history = [];
  GL.state.transactions = [];
  GL.state.coinsSummary = null;
  GL.state.historyError = null;
  GL.upload.clearFile(false);

  var app = GL.ui.byId('app-root');
  var auth = GL.ui.byId('auth-screen');
  if (app) {
    app.classList.add('is-hidden');
  }
  if (auth) {
    auth.classList.add('active');
  }

  GL.app.setAuthMode('login');
  var form = GL.ui.byId('auth-form');
  if (form) {
    form.reset();
  }

  GL.ui.toast('info', 'Signed out', 'Your session data was cleared.');
};

/* --------------------------------------------------------------------------
   Verification service availability
   -------------------------------------------------------------------------- */

GL.app.applyServiceStatus = function (health) {
  GL.state.health = health;
  GL.state.healthChecked = true;

  var available = !!(health && health.detection_available && health.ocr_available);
  var partial = !!(health && (health.detection_available || health.ocr_available));

  var dot = GL.ui.byId('service-status-dot');
  if (dot) {
    dot.className = 'status-dot ' + (available ? 'active' : partial ? '' : 'disconnected');
  }

  GL.ui.setText(
    'service-status-text',
    available ? 'Service online' : partial ? 'Partially available' : 'Backend not connected'
  );
  GL.ui.setText(
    'service-status-sub',
    available && health.model ? health.model.toUpperCase() + ' + OCR + EXIF' : 'Verification API'
  );

  var message;
  if (available) {
    message =
      'Verification service online — YOLOv8 object detection, Tesseract OCR and EXIF metadata ' +
      'checks run on every upload to compute your score V and GreenCoins.';
  } else if (partial) {
    var downParts = [];
    if (!health.detection_available) {
      downParts.push('YOLO detection (' + (health.detection_error || 'unavailable') + ')');
    }
    if (!health.ocr_available) {
      downParts.push('OCR (' + (health.ocr_error || 'unavailable') + ')');
    }
    message =
      'Verification is partially available — ' +
      downParts.join(' and ') +
      ' is down, so submissions cannot be scored until it is restored.';
  } else {
    message =
      'Backend not connected — the verification service is unavailable, so no score or ' +
      'GreenCoins can be issued. You can still upload and preview an image.';
  }

  GL.ui.setText('dashboard-service-message', message);
  GL.ui.setText('verify-service-message', message);

  ['dashboard-service-box', 'verify-service-box'].forEach(function (id) {
    var box = GL.ui.byId(id);
    if (box) {
      box.classList.toggle('status-box-connected', available);
    }
  });
};

GL.app.probeService = function () {
  GL.api.checkHealth().then(GL.app.applyServiceStatus);
};

/* --------------------------------------------------------------------------
   Interface preferences
   -------------------------------------------------------------------------- */

GL.app.applyPrefs = function (prefs) {
  document.documentElement.setAttribute('data-theme', prefs.darkTheme ? 'dark' : 'light');
  document.documentElement.setAttribute('data-density', prefs.compact ? 'compact' : 'default');
  document.body.classList.toggle('reduced-motion', !!prefs.reducedMotion);
};

GL.app.initPrefs = function () {
  var prefs = GL.loadPrefs();

  var controls = {
    darkTheme: GL.ui.byId('pref-dark-theme'),
    compact: GL.ui.byId('pref-compact'),
    reducedMotion: GL.ui.byId('pref-reduced-motion'),
  };

  Object.keys(controls).forEach(function (key) {
    var input = controls[key];
    if (!input) {
      return;
    }
    input.checked = !!prefs[key];
    input.addEventListener('change', function () {
      prefs[key] = input.checked;
      GL.savePrefs(prefs);
      GL.app.applyPrefs(prefs);
    });
  });

  GL.app.applyPrefs(prefs);
};

/* --------------------------------------------------------------------------
   Init
   -------------------------------------------------------------------------- */

GL.app.init = function () {
  // --- Auth screen ---
  var authForm = GL.ui.byId('auth-form');
  if (authForm) {
    authForm.addEventListener('submit', GL.app.handleAuthSubmit);
  }

  var switchBtn = GL.ui.byId('auth-switch-btn');
  if (switchBtn) {
    switchBtn.addEventListener('click', function () {
      GL.app.setAuthMode(authMode === 'login' ? 'register' : 'login');
    });
  }

  var toggle = GL.ui.byId('password-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var input = GL.ui.byId('auth-password');
      var icon = GL.ui.byId('password-toggle-icon');
      if (!input) {
        return;
      }
      var show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      toggle.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
      if (icon) {
        icon.innerHTML = '<use href="#icon-' + (show ? 'eye-off' : 'eye') + '" />';
      }
    });
  }

  // Clear a field's error as soon as the user edits it.
  ['name', 'email', 'password'].forEach(function (field) {
    var input = GL.ui.byId('auth-' + field);
    if (input) {
      input.addEventListener('input', function () {
        GL.app.clearFieldError(field);
      });
    }
  });

  // --- Sidebar navigation ---
  var navItems = document.querySelectorAll('.nav-item[data-view]');
  Array.prototype.forEach.call(navItems, function (item) {
    item.addEventListener('click', function () {
      GL.app.navigate(item.getAttribute('data-view'));
    });
  });

  // Any element with data-nav navigates (delegated, so it also covers
  // buttons rendered later inside empty states).
  document.addEventListener('click', function (event) {
    var target = event.target.closest ? event.target.closest('[data-nav]') : null;
    if (target) {
      event.preventDefault();
      GL.app.navigate(target.getAttribute('data-nav'));
    }
  });

  var sidebarToggle = GL.ui.byId('sidebar-toggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', GL.app.toggleMobileSidebar);
  }

  var overlay = GL.ui.byId('sidebar-overlay');
  if (overlay) {
    overlay.addEventListener('click', GL.app.closeMobileSidebar);
  }

  var logoutBtn = GL.ui.byId('sidebar-logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', GL.app.logout);
  }

  // --- History filters ---
  var statusFilter = GL.ui.byId('history-status-filter');
  if (statusFilter) {
    statusFilter.addEventListener('change', GL.views.renderHistory);
  }

  var search = GL.ui.byId('history-search');
  if (search) {
    search.addEventListener('input', GL.views.renderHistory);
  }

  // --- Settings account form ---
  var accountForm = GL.ui.byId('account-form');
  if (accountForm) {
    accountForm.addEventListener('submit', function (event) {
      event.preventDefault();
      var nameEl = GL.ui.byId('settings-name');
      var emailEl = GL.ui.byId('settings-email');
      var name = nameEl ? nameEl.value.trim() : '';
      var email = emailEl ? emailEl.value.trim() : '';

      if (!name || !email) {
        GL.ui.toast('danger', 'Incomplete details', 'Name and email are both required.');
        return;
      }

      GL.state.user = { name: name, email: email };
      GL.ui.setText('topbar-user-name', name);
      GL.ui.setText('topbar-user-initials', GL.ui.initials(name));
      GL.views.renderDashboard();
      GL.ui.toast('success', 'Details saved', 'Your profile was updated for this session.');
    });
  }

  // --- Upload module ---
  GL.upload.init();

  // --- Preferences ---
  GL.app.initPrefs();

  // --- Initial screen or restored session ---
  var existingToken = GL.getToken();
  if (existingToken) {
    GL.api.me()
      .then(function (user) {
        GL.state.user = user;
        GL.app.enterApp();
      })
      .catch(function () {
        GL.setToken(null);
        GL.app.setAuthMode('login');
        GL.views.renderAll();
      });
  } else {
    GL.app.setAuthMode('login');
    GL.views.renderAll();
  }
};

document.addEventListener('DOMContentLoaded', GL.app.init);
