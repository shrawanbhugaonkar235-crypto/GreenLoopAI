/* ==========================================================================
   GREENLOOPAI — Shared UI helpers
   Toasts, formatting, icons, small DOM utilities.
   ========================================================================== */

var GL = window.GL || {};
window.GL = GL;

GL.ui = {};

/* --------------------------------------------------------------------------
   DOM shortcuts
   -------------------------------------------------------------------------- */

GL.ui.byId = function (id) {
  return document.getElementById(id);
};

GL.ui.setText = function (id, text) {
  var el = GL.ui.byId(id);
  if (el) {
    el.textContent = text;
  }
};

// Builds an <svg><use/></svg> markup string for a sprite icon.
GL.ui.icon = function (name, className) {
  return (
    '<svg class="' + (className || '') + '"><use href="#icon-' + name + '" /></svg>'
  );
};

// Escapes text before it is placed into an HTML string.
GL.ui.escape = function (value) {
  var div = document.createElement('div');
  div.textContent = value == null ? '' : String(value);
  return div.innerHTML;
};

/* --------------------------------------------------------------------------
   Formatting
   -------------------------------------------------------------------------- */

GL.ui.formatBytes = function (bytes) {
  if (typeof bytes !== 'number' || bytes < 0) {
    return '—';
  }
  if (bytes < 1024) {
    return bytes + ' B';
  }
  if (bytes < 1024 * 1024) {
    return (bytes / 1024).toFixed(1) + ' KB';
  }
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
};

GL.ui.formatDateTime = function (isoString) {
  var date = new Date(isoString);
  if (isNaN(date.getTime())) {
    return '—';
  }
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

GL.ui.initials = function (name) {
  if (!name) {
    return 'GL';
  }
  var parts = String(name).trim().split(/\s+/).slice(0, 2);
  return parts
    .map(function (part) {
      return part.charAt(0).toUpperCase();
    })
    .join('');
};

/* --------------------------------------------------------------------------
   Status badge for a history entry / result
   -------------------------------------------------------------------------- */

GL.ui.statusBadge = function (status) {
  var map = {
    verified: { cls: 'badge-success', label: 'Verified' },
    rejected: { cls: 'badge-danger', label: 'Rejected' },
    unavailable: { cls: 'badge-warning', label: 'Service unavailable' },
  };
  var meta = map[status] || { cls: 'badge-neutral', label: 'Unknown' };
  return (
    '<span class="badge ' + meta.cls + '"><span class="badge-dot"></span>' + meta.label + '</span>'
  );
};

/* --------------------------------------------------------------------------
   Empty state block
   -------------------------------------------------------------------------- */

GL.ui.emptyState = function (options) {
  var actions = '';
  if (options.actionLabel && options.actionView) {
    actions =
      '<div class="empty-state-actions">' +
      '<button class="btn btn-primary" data-nav="' +
      options.actionView +
      '" data-testid="' +
      (options.actionTestId || 'empty-state-action') +
      '">' +
      GL.ui.icon(options.actionIcon || 'scan', 'btn-icon') +
      GL.ui.escape(options.actionLabel) +
      '</button>' +
      '</div>';
  }

  return (
    '<div class="empty-state" data-testid="' +
    (options.testId || 'empty-state') +
    '">' +
    '<div class="empty-state-icon">' +
    GL.ui.icon(options.icon || 'info') +
    '</div>' +
    '<div class="empty-state-title">' +
    GL.ui.escape(options.title) +
    '</div>' +
    '<p class="empty-state-desc">' +
    GL.ui.escape(options.description) +
    '</p>' +
    actions +
    '</div>'
  );
};

/* --------------------------------------------------------------------------
   Toast notifications
   -------------------------------------------------------------------------- */

GL.ui.toast = function (type, title, message) {
  var container = GL.ui.byId('toast-container');
  if (!container) {
    return;
  }

  var iconByType = {
    success: 'check',
    danger: 'alert',
    warning: 'alert',
    info: 'info',
  };

  var toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.setAttribute('role', 'status');
  toast.setAttribute('data-testid', 'toast-' + type);
  toast.innerHTML =
    '<svg class="toast-icon"><use href="#icon-' +
    (iconByType[type] || 'info') +
    '" /></svg>' +
    '<div class="toast-content">' +
    '<div class="toast-title">' +
    GL.ui.escape(title) +
    '</div>' +
    (message ? '<div class="toast-message">' + GL.ui.escape(message) + '</div>' : '') +
    '</div>' +
    '<button class="toast-close-btn" aria-label="Dismiss notification">' +
    '<svg width="16" height="16"><use href="#icon-x" /></svg>' +
    '</button>';

  function dismiss() {
    toast.classList.add('toast-hiding');
    window.setTimeout(function () {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 200);
  }

  toast.querySelector('.toast-close-btn').addEventListener('click', dismiss);
  container.appendChild(toast);

  // Keep at most two toasts so the stack never grows over page content.
  var live = container.querySelectorAll('.toast:not(.toast-hiding)');
  if (live.length > 2) {
    for (var i = 0; i < live.length - 2; i++) {
      live[i].classList.add('toast-hiding');
      (function (old) {
        window.setTimeout(function () {
          if (old.parentNode) {
            old.parentNode.removeChild(old);
          }
        }, 200);
      })(live[i]);
    }
  }

  window.setTimeout(dismiss, 3500);
};

/* --------------------------------------------------------------------------
   Button busy state
   -------------------------------------------------------------------------- */

GL.ui.setBusy = function (button, isBusy) {
  if (!button) {
    return;
  }
  if (isBusy) {
    button.classList.add('is-loading');
    button.setAttribute('aria-busy', 'true');
    button.disabled = true;
  } else {
    button.classList.remove('is-loading');
    button.removeAttribute('aria-busy');
    button.disabled = false;
  }
};
