/* ==========================================================================
   GREENLOOPAI — Application state
   Session tokens and verified citizen data are managed here and persisted
   securely in MongoDB Atlas.
   ========================================================================== */

var GL = window.GL || {};
window.GL = GL;

GL.state = {
  // Signed-in user profile ({id, name, email})
  user: null,

  // JWT Access token string
  token: null,

  // Currently selected file plus its object URL for the preview.
  selectedFile: null,
  previewUrl: null,

  // Most recent verification attempt (mapped backend Verification), or null.
  lastResult: null,

  // Verification history for the signed-in citizen, newest first.
  history: [],

  // Authoritative GreenCoins summary from the backend, or null before load.
  coinsSummary: null,

  // GreenCoins transaction list
  transactions: [],

  // Verification engine availability, from GET /health.
  health: null,
  healthChecked: false,

  // True while history/greencoins are being fetched.
  loadingHistory: false,
  historyError: null,
};

/* --------------------------------------------------------------------------
   API Base URL and Authentication Helpers
   -------------------------------------------------------------------------- */

GL.getApiUrl = function (path) {
  var base = window.GL_API_BASE;
  if (base === undefined || base === null) {
    // If served from standalone file or dev port other than 8000, target http://localhost:8000
    if (window.location.protocol === 'file:' || (window.location.port && window.location.port !== '8000')) {
      base = 'http://localhost:8000';
    } else {
      base = '';
    }
  }
  return base + path;
};

var TOKEN_KEY = 'greenloopai_jwt_token';

GL.getToken = function () {
  return GL.state.token || sessionStorage.getItem(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY);
};

GL.setToken = function (token) {
  GL.state.token = token;
  if (token) {
    sessionStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    sessionStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(TOKEN_KEY);
  }
};

GL.authHeaders = function (extra) {
  var headers = Object.assign({}, extra || {});
  var token = GL.getToken();
  if (token) {
    headers['Authorization'] = 'Bearer ' + token;
  }
  return headers;
};

/* --------------------------------------------------------------------------
   Identity used to scope server-side records
   -------------------------------------------------------------------------- */

GL.citizenId = function () {
  return GL.state.user && GL.state.user.id
    ? GL.state.user.id
    : (GL.state.user && GL.state.user.email ? GL.state.user.email : 'demo@greenloop.ai');
};

/* --------------------------------------------------------------------------
   Derived values — the backend summary is authoritative when present
   -------------------------------------------------------------------------- */

GL.totalCoins = function () {
  if (GL.state.coinsSummary && typeof GL.state.coinsSummary.balance === 'number') {
    return GL.state.coinsSummary.balance;
  }
  return GL.state.history.reduce(function (sum, entry) {
    return sum + (typeof entry.coins === 'number' ? entry.coins : 0);
  }, 0);
};

// True once we know a real balance figure (even if it is zero).
GL.hasCoinData = function () {
  if (GL.state.coinsSummary) {
    return true;
  }
  return GL.coinTransactions().length > 0;
};

GL.scoredEntries = function () {
  return GL.state.history.filter(function (entry) {
    return typeof entry.score === 'number';
  });
};

GL.coinTransactions = function () {
  if (GL.state.transactions && GL.state.transactions.length) {
    return GL.state.transactions;
  }
  return GL.state.history.filter(function (entry) {
    return typeof entry.coins === 'number' && entry.coins > 0;
  });
};

GL.latestScore = function () {
  if (GL.state.coinsSummary && typeof GL.state.coinsSummary.latest_score === 'number') {
    return GL.state.coinsSummary.latest_score;
  }
  var scored = GL.scoredEntries();
  return scored.length ? scored[0].score : null;
};

/* --------------------------------------------------------------------------
   Interface preferences (non-sensitive) — localStorage
   -------------------------------------------------------------------------- */

var PREFS_KEY = 'greenloopai.prefs';

GL.loadPrefs = function () {
  try {
    var raw = window.localStorage.getItem(PREFS_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (err) {
    return {};
  }
};

GL.savePrefs = function (prefs) {
  try {
    window.localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
  } catch (err) {
    // Ignore quota or private-browsing errors
  }
};
