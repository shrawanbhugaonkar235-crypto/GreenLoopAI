/* ==========================================================================
   GREENLOOPAI — Upload & verification
   Talks to the real backend pipeline: YOLOv8 detection, Tesseract OCR,
   PIL EXIF authenticity, then score V and GreenCoins.
   ========================================================================== */

var GL = window.GL || {};
window.GL = GL;

GL.api = {};
GL.upload = {};

var MAX_FILE_BYTES = 10 * 1024 * 1024; // 10 MB
var ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

/* --------------------------------------------------------------------------
   API calls (relative /api paths)

   Response shapes mirror the Pydantic models in backend/models/verification.py:

   ServiceHealth      { status, detection_available, ocr_available,
                        exif_available, detection_error, ocr_error, model }
   Verification       { id, citizen_id, file_name, file_size, timestamp,
                        category, confidence, ocr_text, brand, authenticity,
                        score, coins, reward_tier, status, message,
                        detected_objects[], ocr{}, authenticity_detail{},
                        breakdown{}, calculation_basis }
   GreenCoinsSummary  { citizen_id, balance, verified_count, total_count,
                        latest_score }
   -------------------------------------------------------------------------- */

// Reads the error detail FastAPI returns, falling back to the status line.
function readError(response) {
  return response
    .json()
    .then(function (body) {
      var detail = body && body.detail;
      if (typeof detail === 'string') {
        return detail;
      }
      if (Array.isArray(detail) && detail.length && detail[0].msg) {
        return detail[0].msg;
      }
      return 'The verification service responded with HTTP ' + response.status + '.';
    })
    .catch(function () {
      return 'The verification service responded with HTTP ' + response.status + '.';
    });
}

GL.api.checkHealth = function () {
  return fetch(GL.getApiUrl('/health'), { headers: { Accept: 'application/json' } })
    .then(function (response) {
      if (!response.ok) {
        return null;
      }
      return response.json();
    })
    .catch(function () {
      return null;
    });
};

GL.api.register = function (name, email, password) {
  return fetch(GL.getApiUrl('/api/v1/auth/register'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ name: name, email: email, password: password })
  }).then(function (response) {
    if (!response.ok) {
      return readError(response).then(function (msg) {
        var err = new Error(msg);
        err.status = response.status;
        throw err;
      });
    }
    return response.json();
  });
};

GL.api.login = function (email, password) {
  return fetch(GL.getApiUrl('/api/v1/auth/login'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ email: email, password: password })
  }).then(function (response) {
    if (!response.ok) {
      return readError(response).then(function (msg) {
        var err = new Error(msg);
        err.status = response.status;
        throw err;
      });
    }
    return response.json();
  });
};

GL.api.me = function () {
  return fetch(GL.getApiUrl('/api/v1/auth/me'), {
    headers: GL.authHeaders({ Accept: 'application/json' })
  }).then(function (response) {
    if (!response.ok) {
      throw new Error('Session invalid');
    }
    return response.json();
  });
};

GL.api.verify = function (file) {
  var form = new FormData();
  form.append('image', file, file.name);

  return fetch(GL.getApiUrl('/api/v1/verify'), {
    method: 'POST',
    headers: GL.authHeaders(),
    body: form
  }).then(function (response) {
    if (!response.ok) {
      return readError(response).then(function (message) {
        var err = new Error(message);
        err.status = response.status;
        throw err;
      });
    }
    return response.json();
  });
};

GL.api.fetchHistory = function () {
  return fetch(GL.getApiUrl('/api/v1/history'), {
    headers: GL.authHeaders({ Accept: 'application/json' }),
  }).then(function (response) {
    if (!response.ok) {
      throw new Error('Could not load history (HTTP ' + response.status + ').');
    }
    return response.json();
  });
};

GL.api.fetchGreenCoins = function () {
  return fetch(GL.getApiUrl('/api/v1/greencoins/balance'), {
    headers: GL.authHeaders({ Accept: 'application/json' }),
  }).then(function (response) {
    if (!response.ok) {
      throw new Error('Could not load GreenCoins (HTTP ' + response.status + ').');
    }
    return response.json();
  });
};

GL.api.fetchTransactions = function () {
  return fetch(GL.getApiUrl('/api/v1/greencoins/transactions'), {
    headers: GL.authHeaders({ Accept: 'application/json' }),
  }).then(function (response) {
    if (!response.ok) {
      return [];
    }
    return response.json();
  }).catch(function () {
    return [];
  });
};

/* --------------------------------------------------------------------------
   Map a backend Verification into the shape the views render
   -------------------------------------------------------------------------- */

GL.api.toEntry = function (data) {
  return {
    id: data.id,
    timestamp: data.timestamp,
    fileName: data.file_name,
    fileSize: data.file_size,
    category: data.category != null ? data.category : null,
    confidence: typeof data.confidence === 'number' ? data.confidence : null,
    ocrText: data.ocr_text != null ? data.ocr_text : null,
    brand: data.brand != null ? data.brand : null,
    authenticity: data.authenticity != null ? data.authenticity : null,
    score: typeof data.score === 'number' ? data.score : null,
    coins: typeof data.coins === 'number' ? data.coins : null,
    rewardTier: data.reward_tier != null ? data.reward_tier : null,
    status: data.status === 'verified' ? 'verified' : 'rejected',
    message: data.message != null ? data.message : null,
    detectedObjects: Array.isArray(data.detected_objects) ? data.detected_objects : [],
    breakdown: data.breakdown || null,
    calculationBasis: data.calculation_basis != null ? data.calculation_basis : null,
    authenticityDetail: data.authenticity_detail || null,
    ocrDetail: data.ocr || null,
  };
};

/* --------------------------------------------------------------------------
   Processing stage UI
   -------------------------------------------------------------------------- */

var STAGES = ['detection', 'ocr', 'exif', 'score', 'reward'];

GL.upload.setStage = function (stage, state, label) {
  var row = document.querySelector('.stage-row[data-stage="' + stage + '"]');
  if (!row) {
    return;
  }
  row.setAttribute('data-state', state);

  var holder = row.querySelector('.stage-state');
  if (!holder) {
    return;
  }

  if (state === 'running') {
    holder.innerHTML = '<span class="stage-spinner"></span>';
    return;
  }

  var badgeClass = 'badge-neutral';
  if (state === 'done') {
    badgeClass = 'badge-success';
  } else if (state === 'failed') {
    badgeClass = 'badge-danger';
  } else if (state === 'warn') {
    badgeClass = 'badge-warning';
  }

  holder.innerHTML = '<span class="badge ' + badgeClass + '">' + GL.ui.escape(label) + '</span>';
};

GL.upload.setAllStages = function (state, label) {
  STAGES.forEach(function (stage) {
    GL.upload.setStage(stage, state, label);
  });
};

GL.upload.setOverallBadge = function (cls, label) {
  var badge = GL.ui.byId('processing-overall-badge');
  if (badge) {
    badge.className = 'badge ' + cls;
    badge.innerHTML = '<span class="badge-dot"></span> ' + GL.ui.escape(label);
  }
};

GL.upload.resetStages = function () {
  GL.upload.setAllStages('idle', 'Pending');
  GL.upload.setOverallBadge('badge-neutral', 'Idle');
};

// Fills the stage rows from a real backend result.
GL.upload.applyResultToStages = function (entry) {
  var objectCount = entry.detectedObjects.length;
  GL.upload.setStage(
    'detection',
    objectCount ? 'done' : 'warn',
    objectCount
      ? objectCount + ' object' + (objectCount === 1 ? '' : 's')
      : 'Nothing detected'
  );

  var ocrDetail = entry.ocrDetail || {};
  GL.upload.setStage(
    'ocr',
    ocrDetail.status === 'DETECTED' ? 'done' : 'warn',
    ocrDetail.status === 'DETECTED'
      ? (ocrDetail.word_count || 0) + ' words'
      : 'No text found'
  );

  var exifDetail = entry.authenticityDetail || {};
  GL.upload.setStage(
    'exif',
    exifDetail.exif_present ? 'done' : 'warn',
    exifDetail.exif_present ? 'Metadata present' : 'No EXIF data'
  );

  GL.upload.setStage(
    'score',
    entry.status === 'verified' ? 'done' : 'failed',
    entry.score !== null ? 'V = ' + entry.score : 'Not scored'
  );

  GL.upload.setStage(
    'reward',
    entry.coins ? 'done' : 'failed',
    entry.coins ? '+' + entry.coins + ' coins' : 'No reward'
  );

  GL.upload.setOverallBadge(
    entry.status === 'verified' ? 'badge-success' : 'badge-danger',
    entry.status === 'verified' ? 'Verified' : 'Rejected'
  );
};

/* --------------------------------------------------------------------------
   File selection, preview, remove / replace
   -------------------------------------------------------------------------- */

GL.upload.validateFile = function (file) {
  var nameLower = file.name.toLowerCase();
  var extensionOk = /\.(jpe?g|png|webp)$/.test(nameLower);
  var typeOk = ALLOWED_TYPES.indexOf(file.type) !== -1;

  if (!typeOk && !extensionOk) {
    return 'Unsupported format. Please choose a JPG, JPEG, PNG or WEBP image.';
  }
  if (file.size > MAX_FILE_BYTES) {
    return 'That image is ' + GL.ui.formatBytes(file.size) + '. The maximum size is 10 MB.';
  }
  if (file.size === 0) {
    return 'That file appears to be empty. Please choose another image.';
  }
  return null;
};

GL.upload.selectFile = function (file) {
  var error = GL.upload.validateFile(file);
  if (error) {
    GL.ui.toast('danger', 'Image rejected', error);
    return;
  }

  if (GL.state.previewUrl) {
    URL.revokeObjectURL(GL.state.previewUrl);
  }

  GL.state.selectedFile = file;
  GL.state.previewUrl = URL.createObjectURL(file);

  var img = GL.ui.byId('preview-image');
  if (img) {
    img.src = GL.state.previewUrl;
  }

  GL.ui.setText('preview-filename', file.name);
  GL.ui.setText('preview-filesize', GL.ui.formatBytes(file.size));
  GL.ui.setText(
    'preview-filetype',
    (file.type || 'image').replace('image/', '').toUpperCase()
  );

  var card = GL.ui.byId('preview-card');
  if (card) {
    card.classList.add('active');
  }

  var dropzone = GL.ui.byId('upload-dropzone');
  if (dropzone) {
    dropzone.classList.remove('drag-active');
  }

  GL.upload.resetStages();
  GL.ui.setText('processing-hint', 'Ready to verify "' + file.name + '".');

  // No toast here on purpose: the preview card is the confirmation, and a toast
  // in the bottom-right corner would sit over the "Verify Waste" button.
};

GL.upload.clearFile = function (announce) {
  if (GL.state.previewUrl) {
    URL.revokeObjectURL(GL.state.previewUrl);
  }
  GL.state.selectedFile = null;
  GL.state.previewUrl = null;

  var card = GL.ui.byId('preview-card');
  if (card) {
    card.classList.remove('active');
  }

  var img = GL.ui.byId('preview-image');
  if (img) {
    img.removeAttribute('src');
  }

  var input = GL.ui.byId('file-input');
  if (input) {
    input.value = '';
  }

  GL.upload.resetStages();
  GL.ui.setText('processing-hint', 'Select an image to enable verification.');

  if (announce) {
    GL.ui.toast('info', 'Image removed', 'Select another image to verify.');
  }
};

/* --------------------------------------------------------------------------
   Run verification against the real pipeline
   -------------------------------------------------------------------------- */

GL.upload.runVerification = function () {
  var file = GL.state.selectedFile;
  if (!file) {
    GL.ui.toast('warning', 'No image selected', 'Choose a waste image before verifying.');
    return;
  }

  var button = GL.ui.byId('verify-waste-btn');
  GL.ui.setBusy(button, true);

  GL.upload.setOverallBadge('badge-info', 'Processing');
  GL.upload.setStage('detection', 'running');
  GL.upload.setStage('ocr', 'idle', 'Queued');
  GL.upload.setStage('exif', 'idle', 'Queued');
  GL.upload.setStage('score', 'idle', 'Queued');
  GL.upload.setStage('reward', 'idle', 'Queued');
  GL.ui.setText(
    'processing-hint',
    'Running YOLOv8 detection, Tesseract OCR and EXIF checks…'
  );

  var citizenId = GL.citizenId();

  GL.api
    .verify(file, citizenId)
    .then(function (data) {
      var entry = GL.api.toEntry(data);

      GL.state.lastResult = entry;
      GL.state.history.unshift(entry);

      GL.upload.applyResultToStages(entry);
      GL.ui.setText('processing-hint', entry.calculationBasis || 'Verification complete.');

      // Refresh the authoritative balance from the backend.
      return GL.app.refreshGreenCoins().then(function () {
        GL.views.renderAll();
        GL.ui.toast(
          entry.status === 'verified' ? 'success' : 'warning',
          entry.status === 'verified'
            ? 'Verified — V ' + entry.score + ', +' + entry.coins + ' GreenCoins'
            : 'Rejected — V ' + entry.score,
          entry.status === 'verified'
            ? entry.category + ' detected.'
            : entry.message || 'This submission did not pass verification.'
        );
        GL.app.navigate('result');
      });
    })
    .catch(function (err) {
      var isUnavailable = err && err.status === 503;
      var message =
        err && err.message
          ? err.message
          : 'The verification service could not be reached.';

      var entry = {
        timestamp: new Date().toISOString(),
        fileName: file.name,
        fileSize: file.size,
        category: null,
        confidence: null,
        ocrText: null,
        brand: null,
        authenticity: null,
        score: null,
        coins: null,
        rewardTier: null,
        status: 'unavailable',
        message: message,
        detectedObjects: [],
        breakdown: null,
        calculationBasis: null,
        authenticityDetail: null,
        ocrDetail: null,
      };

      GL.state.lastResult = entry;
      GL.state.history.unshift(entry);

      GL.upload.setAllStages('failed', 'Unavailable');
      GL.upload.setOverallBadge('badge-warning', 'Service unavailable');
      GL.ui.setText('processing-hint', message);

      GL.views.renderAll();
      GL.ui.toast(
        'warning',
        isUnavailable ? 'Verification engine unavailable' : 'Verification failed',
        message
      );
      GL.app.navigate('result');
    })
    .then(function () {
      GL.ui.setBusy(button, false);
    });
};

/* --------------------------------------------------------------------------
   Wiring
   -------------------------------------------------------------------------- */

GL.upload.init = function () {
  var dropzone = GL.ui.byId('upload-dropzone');
  var input = GL.ui.byId('file-input');
  var browseBtn = GL.ui.byId('browse-files-btn');

  function openPicker() {
    if (input) {
      input.click();
    }
  }

  if (browseBtn) {
    browseBtn.addEventListener('click', function (event) {
      event.stopPropagation();
      openPicker();
    });
  }

  if (dropzone) {
    dropzone.addEventListener('click', openPicker);

    ['dragenter', 'dragover'].forEach(function (name) {
      dropzone.addEventListener(name, function (event) {
        event.preventDefault();
        dropzone.classList.add('drag-active');
      });
    });

    ['dragleave', 'drop'].forEach(function (name) {
      dropzone.addEventListener(name, function (event) {
        event.preventDefault();
        if (name === 'dragleave' && dropzone.contains(event.relatedTarget)) {
          return;
        }
        dropzone.classList.remove('drag-active');
      });
    });

    dropzone.addEventListener('drop', function (event) {
      event.preventDefault();
      var files = event.dataTransfer && event.dataTransfer.files;
      if (files && files.length) {
        GL.upload.selectFile(files[0]);
      }
    });
  }

  if (input) {
    input.addEventListener('change', function () {
      if (input.files && input.files.length) {
        GL.upload.selectFile(input.files[0]);
      }
    });
  }

  var removeBtn = GL.ui.byId('remove-image-btn');
  if (removeBtn) {
    removeBtn.addEventListener('click', function () {
      GL.upload.clearFile(true);
    });
  }

  var replaceBtn = GL.ui.byId('replace-image-btn');
  if (replaceBtn) {
    replaceBtn.addEventListener('click', openPicker);
  }

  var verifyBtn = GL.ui.byId('verify-waste-btn');
  if (verifyBtn) {
    verifyBtn.addEventListener('click', GL.upload.runVerification);
  }

  // Prevent the browser from opening a file dropped outside the dropzone.
  ['dragover', 'drop'].forEach(function (name) {
    window.addEventListener(name, function (event) {
      if (!dropzone || !dropzone.contains(event.target)) {
        event.preventDefault();
      }
    });
  });
};
