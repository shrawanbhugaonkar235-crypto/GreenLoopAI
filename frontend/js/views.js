/* ==========================================================================
   GREENLOOPAI — View rendering
   Every renderer reads GL.state, which is populated from the real backend.
   A value the pipeline did not produce renders as an explicit empty marker.
   ========================================================================== */

var GL = window.GL || {};
window.GL = GL;

GL.views = {};

/* --------------------------------------------------------------------------
   Dashboard
   -------------------------------------------------------------------------- */

GL.views.renderDashboard = function () {
  var user = GL.state.user;
  GL.ui.setText('dashboard-user-name', user ? user.name : 'Citizen');

  var summary = GL.state.coinsSummary;
  var latest = GL.latestScore();

  GL.ui.setText('dashboard-coin-balance', GL.hasCoinData() ? String(GL.totalCoins()) : '—');
  GL.ui.setText(
    'dashboard-verification-count',
    summary ? String(summary.total_count) : String(GL.state.history.length)
  );
  GL.ui.setText('dashboard-latest-score', latest !== null ? String(latest) : '—');

  var coinFooter = GL.ui.byId('dashboard-coin-footer');
  if (coinFooter) {
    var verified = summary ? summary.verified_count : GL.coinTransactions().length;
    coinFooter.innerHTML =
      '<span class="status-indicator"></span><span>' +
      (verified
        ? 'From ' + verified + ' verified submission' + (verified === 1 ? '' : 's')
        : 'Awaiting verified rewards') +
      '</span>';
  }

  var container = GL.ui.byId('dashboard-recent-container');
  if (!container) {
    return;
  }

  if (GL.state.loadingHistory && !GL.state.history.length) {
    container.innerHTML =
      '<p class="text-muted-sm" data-testid="dashboard-recent-loading">Loading your verification history…</p>';
    return;
  }

  var recent = GL.state.history.slice(0, 5);

  if (!recent.length) {
    container.innerHTML = GL.ui.emptyState({
      testId: 'dashboard-recent-empty',
      icon: 'history',
      title: 'No verifications yet',
      description:
        'Upload a waste image and run the verification pipeline. Your submissions will be listed here.',
      actionLabel: 'Verify waste',
      actionView: 'verify',
      actionIcon: 'scan',
      actionTestId: 'dashboard-recent-empty-action',
    });
    return;
  }

  container.innerHTML = GL.views.historyTable(recent, 'dashboard-recent');
};

/* --------------------------------------------------------------------------
   Shared history table markup
   -------------------------------------------------------------------------- */

GL.views.historyTable = function (entries, testIdPrefix) {
  var rows = entries
    .map(function (entry, index) {
      return (
        '<tr data-testid="' + testIdPrefix + '-row-' + index + '">' +
        '<td data-testid="' + testIdPrefix + '-timestamp-' + index + '">' +
        GL.ui.escape(GL.ui.formatDateTime(entry.timestamp)) +
        '</td>' +
        '<td data-testid="' + testIdPrefix + '-filename-' + index + '">' +
        GL.ui.escape(entry.fileName) +
        '</td>' +
        '<td data-testid="' + testIdPrefix + '-category-' + index + '">' +
        (entry.category
          ? GL.ui.escape(entry.category)
          : '<span class="kv-value is-empty">Not available</span>') +
        '</td>' +
        '<td data-testid="' + testIdPrefix + '-score-' + index + '">' +
        (typeof entry.score === 'number'
          ? '<strong>' + entry.score + '</strong>'
          : '<span class="kv-value is-empty">—</span>') +
        '</td>' +
        '<td data-testid="' + testIdPrefix + '-status-' + index + '">' +
        GL.ui.statusBadge(entry.status) +
        '</td>' +
        '<td data-testid="' + testIdPrefix + '-coins-' + index + '">' +
        (typeof entry.coins === 'number' && entry.coins > 0
          ? '+' + entry.coins
          : '<span class="kv-value is-empty">—</span>') +
        '</td>' +
        '</tr>'
      );
    })
    .join('');

  return (
    '<div class="table-wrapper">' +
    '<table class="data-table" data-testid="' + testIdPrefix + '-table">' +
    '<thead><tr>' +
    '<th>Timestamp</th><th>File</th><th>Category</th><th>Score V</th><th>Status</th><th>Coins</th>' +
    '</tr></thead>' +
    '<tbody>' +
    rows +
    '</tbody></table></div>'
  );
};

/* --------------------------------------------------------------------------
   Verification result
   -------------------------------------------------------------------------- */

GL.views.renderResult = function () {
  var container = GL.ui.byId('result-content');
  if (!container) {
    return;
  }

  var result = GL.state.lastResult;

  if (!result) {
    container.innerHTML = GL.ui.emptyState({
      testId: 'result-empty',
      icon: 'clipboard',
      title: 'No verification result yet',
      description:
        'Run a verification from the Verify Waste screen. YOLOv8 detection, OCR text, EXIF authenticity, score V and GreenCoins will appear here.',
      actionLabel: 'Verify waste',
      actionView: 'verify',
      actionIcon: 'scan',
      actionTestId: 'result-empty-action',
    });
    return;
  }

  // The request could not be completed (engine down, network, bad file).
  if (result.status === 'unavailable') {
    container.innerHTML =
      '<div class="service-status-box" data-testid="result-unavailable-notice">' +
      GL.ui.icon('alert') +
      '<span><strong>Verification service unavailable.</strong> ' +
      GL.ui.escape(result.message || 'The verification backend did not respond.') +
      ' No score or reward can be shown until the service is available.</span>' +
      '</div>' +
      '<div class="card" style="margin-top: 1.5rem">' +
      '<div class="card-header"><div><div class="card-title">Submission</div>' +
      '<div class="card-subtitle">The image you attempted to verify</div></div>' +
      GL.ui.statusBadge('unavailable') +
      '</div>' +
      '<div class="card-body"><div class="kv-list">' +
      GL.views.kvRow('File name', result.fileName, 'result-filename') +
      GL.views.kvRow('Submitted at', GL.ui.formatDateTime(result.timestamp), 'result-timestamp') +
      GL.views.kvRow('Detected waste category', null, 'result-category') +
      GL.views.kvRow('OCR extracted text', null, 'result-ocr') +
      GL.views.kvRow('Image authenticity (EXIF)', null, 'result-authenticity') +
      GL.views.kvRow('Verification score V', null, 'result-score') +
      GL.views.kvRow('GreenCoins earned', null, 'result-coins') +
      '</div></div></div>';
    return;
  }

  var score = typeof result.score === 'number' ? result.score : null;
  var circumference = 440;
  var offset = score === null ? circumference : circumference - (score / 100) * circumference;
  var isVerified = result.status === 'verified';

  // Rejection reason banner, straight from the backend message.
  var rejectionNotice = '';
  if (!isVerified && result.message) {
    rejectionNotice =
      '<div class="service-status-box" data-testid="result-rejected-notice" style="margin-bottom: 1.5rem">' +
      GL.ui.icon('alert') +
      '<span><strong>Not verified.</strong> ' +
      GL.ui.escape(result.message) +
      '</span></div>';
  }

  // Detected object list (real YOLO output).
  var objectsMarkup;
  if (result.detectedObjects.length) {
    objectsMarkup =
      '<div class="kv-list" data-testid="result-detected-objects">' +
      result.detectedObjects
        .map(function (obj, index) {
          return (
            '<div class="kv-row"><span class="kv-label">' +
            GL.ui.escape(obj.label) +
            ' <span class="badge badge-primary" style="margin-left:.35rem">' +
            GL.ui.escape(obj.category) +
            '</span></span>' +
            '<span class="kv-value mono" data-testid="result-object-conf-' + index + '">' +
            (obj.confidence * 100).toFixed(1) +
            '%</span></div>'
          );
        })
        .join('') +
      '</div>';
  } else {
    objectsMarkup =
      '<p class="text-muted-sm" data-testid="result-no-objects">' +
      'YOLOv8 found no recognisable waste object in this image.</p>';
  }

  // Score breakdown (the three weighted components).
  var breakdownMarkup = '';
  if (result.breakdown) {
    breakdownMarkup =
      '<div class="card"><div class="card-header"><div>' +
      '<div class="card-title">Score breakdown</div>' +
      '<div class="card-subtitle">V = 0.45 detection + 0.30 brand + 0.25 authenticity</div>' +
      '</div></div><div class="card-body"><div class="kv-list">' +
      GL.views.kvRow(
        'Detection (x0.45)',
        result.breakdown.detection_score + ' %',
        'result-breakdown-detection'
      ) +
      GL.views.kvRow(
        'Brand / packaging (x0.30)',
        result.breakdown.brand_score + ' %',
        'result-breakdown-brand'
      ) +
      GL.views.kvRow(
        'Authenticity (x0.25)',
        result.breakdown.authenticity_score + ' %',
        'result-breakdown-authenticity'
      ) +
      '</div></div></div>';
  }

  var exif = result.authenticityDetail || {};
  var flagsMarkup = '';
  if (exif.flags && exif.flags.length) {
    flagsMarkup =
      '<ul class="text-muted-sm" data-testid="result-exif-flags" style="margin:.5rem 0 0 1.1rem">' +
      exif.flags
        .map(function (flag) {
          return '<li>' + GL.ui.escape(flag) + '</li>';
        })
        .join('') +
      '</ul>';
  }

  container.innerHTML =
    rejectionNotice +
    '<div class="verification-layout" data-testid="result-detail">' +
    // ---------- Left column: gauge + reward ----------
    '<div class="verification-results-panel">' +
    '<div class="card"><div class="card-header">' +
    '<div><div class="card-title">Verification score V</div>' +
    '<div class="card-subtitle">Weighted detection, brand and authenticity</div></div>' +
    GL.ui.statusBadge(result.status) +
    '</div><div class="card-body">' +
    '<div class="score-gauge-container">' +
    '<div class="score-gauge-wrapper">' +
    '<svg class="score-gauge-svg" viewBox="0 0 170 170">' +
    '<circle class="score-gauge-bg" cx="85" cy="85" r="70"></circle>' +
    '<circle class="score-gauge-fill" cx="85" cy="85" r="70" style="stroke-dashoffset:' +
    offset +
    (isVerified ? '' : ';stroke:var(--danger)') +
    '"></circle>' +
    '</svg>' +
    '<div class="score-gauge-center">' +
    '<div class="score-gauge-value" data-testid="result-score-value">' +
    (score === null ? '—' : score) +
    '</div>' +
    '<div class="score-gauge-max">out of 100</div>' +
    '</div></div>' +
    '<div class="score-gauge-caption">' +
    (isVerified
      ? 'Passed — threshold is V ≥ 60'
      : 'Did not pass — threshold is V ≥ 60') +
    '</div></div></div></div>' +
    // Reward card
    '<div class="rewards-result-card" data-testid="result-reward-card">' +
    '<div class="rewards-result-left">' +
    '<span class="rewards-coin-icon">' + GL.ui.icon('coin') + '</span>' +
    '<div><div class="rewards-title">GreenCoins earned</div>' +
    '<div class="rewards-sub" data-testid="result-reward-tier">' +
    (result.rewardTier ? GL.ui.escape(result.rewardTier) + ' tier' : 'No reward issued') +
    '</div></div></div>' +
    '<div class="rewards-amount" data-testid="result-coins-value">' +
    (typeof result.coins === 'number' ? '+' + result.coins : '—') +
    '</div></div>' +
    breakdownMarkup +
    '</div>' +
    // ---------- Right column: pipeline findings ----------
    '<div class="verification-results-panel">' +
    '<div class="card"><div class="card-header"><div>' +
    '<div class="card-title">Detected objects</div>' +
    '<div class="card-subtitle">YOLOv8n inference output</div>' +
    '</div></div><div class="card-body">' +
    objectsMarkup +
    '</div></div>' +
    '<div class="card"><div class="card-header"><div>' +
    '<div class="card-title">Pipeline findings</div>' +
    '<div class="card-subtitle">OCR text, EXIF authenticity and metadata</div>' +
    '</div></div><div class="card-body"><div class="kv-list">' +
    GL.views.kvRow('File name', result.fileName, 'result-filename') +
    GL.views.kvRow('Verified at', GL.ui.formatDateTime(result.timestamp), 'result-timestamp') +
    GL.views.kvRow('Detected waste category', result.category, 'result-category') +
    GL.views.kvRow(
      'Detection confidence',
      result.confidence !== null ? (result.confidence * 100).toFixed(1) + ' %' : null,
      'result-confidence'
    ) +
    GL.views.kvRow('OCR extracted text', result.ocrText, 'result-ocr') +
    GL.views.kvRow('Matched EPR brand', result.brand, 'result-brand') +
    GL.views.kvRow('Image authenticity (EXIF)', result.authenticity, 'result-authenticity') +
    GL.views.kvRow('Camera make / model',
      exif.camera_make || exif.camera_model
        ? [exif.camera_make, exif.camera_model].filter(Boolean).join(' ')
        : null,
      'result-camera'
    ) +
    GL.views.kvRow('Verification status', result.status, 'result-status') +
    '</div>' +
    flagsMarkup +
    '</div></div></div></div>';
};

// One label/value row. A null or empty value renders an explicit empty marker.
GL.views.kvRow = function (label, value, testId) {
  var hasValue = value !== null && value !== undefined && value !== '';
  return (
    '<div class="kv-row">' +
    '<span class="kv-label">' + GL.ui.escape(label) + '</span>' +
    '<span class="kv-value' + (hasValue ? '' : ' is-empty') + '" data-testid="' + testId + '">' +
    (hasValue ? GL.ui.escape(value) : 'Not available') +
    '</span></div>'
  );
};

/* --------------------------------------------------------------------------
   GreenCoins
   -------------------------------------------------------------------------- */

GL.views.renderGreenCoins = function () {
  var transactions = GL.coinTransactions();
  var summary = GL.state.coinsSummary;
  var hasData = GL.hasCoinData();

  GL.ui.setText('greencoins-balance', hasData ? String(GL.totalCoins()) : '—');

  var verified = summary ? summary.verified_count : transactions.length;
  GL.ui.setText(
    'greencoins-balance-sub',
    verified
      ? 'Earned from ' + verified + ' verified submission' + (verified === 1 ? '' : 's') + '.'
      : 'No verified rewards yet — balance appears once a verification passes.'
  );

  var badge = GL.ui.byId('sidebar-coin-badge');
  if (badge) {
    badge.textContent = hasData ? String(GL.totalCoins()) : '0';
  }

  var container = GL.ui.byId('greencoins-transactions');
  if (!container) {
    return;
  }

  if (!transactions.length) {
    container.innerHTML = GL.ui.emptyState({
      testId: 'greencoins-empty',
      icon: 'coin',
      title: 'No transactions yet',
      description:
        'GreenCoins are credited only when a submission passes verification (V ≥ 60 with a detected waste object).',
      actionLabel: 'Verify waste',
      actionView: 'verify',
      actionIcon: 'scan',
      actionTestId: 'greencoins-empty-action',
    });
    return;
  }

  var rows = transactions
    .map(function (entry, index) {
      var fileName = entry.fileName || entry.file_name || '';
      var tier = entry.rewardTier || entry.reward_tier || '—';
      var coins = entry.coins !== undefined ? entry.coins : (entry.amount !== undefined ? entry.amount : 0);
      var desc = entry.description || ('Verified submission' + (fileName ? ' — ' + fileName : ''));
      return (
        '<tr data-testid="greencoins-row-' + index + '">' +
        '<td>' + GL.ui.escape(GL.ui.formatDateTime(entry.timestamp)) + '</td>' +
        '<td>' + GL.ui.escape(desc) + '</td>' +
        '<td>' + (entry.category ? GL.ui.escape(entry.category) : '—') + '</td>' +
        '<td>' + GL.ui.escape(tier) + '</td>' +
        '<td><strong style="color: var(--primary-dark)">+' + coins + '</strong></td>' +
        '</tr>'
      );
    })
    .join('');

  container.innerHTML =
    '<div class="table-wrapper"><table class="data-table" data-testid="greencoins-table">' +
    '<thead><tr><th>Date</th><th>Description</th><th>Category</th><th>Tier</th><th>Coins</th></tr></thead>' +
    '<tbody>' + rows + '</tbody></table></div>';
};

/* --------------------------------------------------------------------------
   History (with frontend filtering)
   -------------------------------------------------------------------------- */

GL.views.renderHistory = function () {
  var container = GL.ui.byId('history-container');
  if (!container) {
    return;
  }

  var statusEl = GL.ui.byId('history-status-filter');
  var searchEl = GL.ui.byId('history-search');
  var status = statusEl ? statusEl.value : 'all';
  var term = searchEl ? searchEl.value.trim().toLowerCase() : '';

  var all = GL.state.history;

  var filtered = all.filter(function (entry) {
    var statusOk = status === 'all' || entry.status === status;
    var haystack = (entry.fileName + ' ' + (entry.category || '')).toLowerCase();
    var searchOk = !term || haystack.indexOf(term) !== -1;
    return statusOk && searchOk;
  });

  var countEl = GL.ui.byId('history-count');
  if (countEl) {
    countEl.textContent = all.length ? 'Showing ' + filtered.length + ' of ' + all.length : '';
  }

  if (GL.state.loadingHistory && !all.length) {
    container.innerHTML =
      '<p class="text-muted-sm" data-testid="history-loading">Loading your verification history…</p>';
    return;
  }

  if (GL.state.historyError && !all.length) {
    container.innerHTML =
      '<div class="service-status-box" data-testid="history-error">' +
      GL.ui.icon('alert') +
      '<span>' + GL.ui.escape(GL.state.historyError) + '</span></div>';
    return;
  }

  if (!all.length) {
    container.innerHTML = GL.ui.emptyState({
      testId: 'history-empty',
      icon: 'history',
      title: 'No scan history',
      description:
        'Your verifications are saved to your account and appear here with their timestamp, category, score and status.',
      actionLabel: 'Verify waste',
      actionView: 'verify',
      actionIcon: 'scan',
      actionTestId: 'history-empty-action',
    });
    return;
  }

  if (!filtered.length) {
    container.innerHTML = GL.ui.emptyState({
      testId: 'history-no-match',
      icon: 'info',
      title: 'No matching records',
      description: 'No verification matches the current status filter or search term.',
    });
    return;
  }

  container.innerHTML = GL.views.historyTable(filtered, 'history');
};

/* --------------------------------------------------------------------------
   Re-render everything that depends on state
   -------------------------------------------------------------------------- */

GL.views.renderAll = function () {
  GL.views.renderDashboard();
  GL.views.renderResult();
  GL.views.renderGreenCoins();
  GL.views.renderHistory();
};
