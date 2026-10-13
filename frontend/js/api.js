/**
 * ====================================================================
 * GREENLOOPAI — REAL API CLIENT
 * Real backend communication for Spring Boot Security Gateway & FastAPI
 * ====================================================================
 */

(function (window) {
  'use strict';

  // Configurable base URL: Spring Boot Security Gateway (8080) or direct FastAPI (8000)
  const API_CONFIG = {
    // Check if hosted on same origin or use default local Spring Boot Gateway port
    BASE_URL: window.location.port === '8080' ? '' : 'http://localhost:8080',
    FALLBACK_URL: 'http://localhost:8000',
    ACTIVE_URL: window.location.port === '8080' ? '' : 'http://localhost:8080',
    HEALTH_POLL_INTERVAL_MS: 15000,
    TIMEOUT_MS: 30000
  };

  let isConnected = false;
  let activeJwtToken = null; // Stored in runtime memory only (NEVER in localStorage)

  /**
   * Set runtime JWT authentication token (e.g. from OAuth2/OIDC flow)
   */
  function setAuthToken(token) {
    activeJwtToken = token;
  }

  function getAuthHeaders() {
    const headers = {
      'Accept': 'application/json',
      'X-Service-Token': 'dev-internal-secret-token'
    };
    if (activeJwtToken) {
      headers['Authorization'] = `Bearer ${activeJwtToken}`;
    }
    return headers;
  }

  /**
   * Safe fetch with timeout and error mapping
   */
  async function apiFetch(endpoint, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT_MS);

    const url = `${API_CONFIG.ACTIVE_URL}${endpoint}`;
    const headers = {
      ...getAuthHeaders(),
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      // Handle non-OK HTTP status codes with structured parsing
      if (!response.ok) {
        let errorData = null;
        try {
          errorData = await response.json();
        } catch (_) {
          errorData = { message: response.statusText, status_code: response.status };
        }

        const error = new Error(errorData.message || `Request failed with status ${response.status}`);
        error.status = response.status;
        error.data = errorData;
        throw error;
      }

      return await response.json();
    } catch (err) {
      clearTimeout(timeoutId);
      
      // If primary endpoint failed, attempt direct fallback in local dev if on 8080
      if (err.name === 'TypeError' && API_CONFIG.FALLBACK_URL) {
        try {
          const fallbackUrl = `${API_CONFIG.FALLBACK_URL}${endpoint}`;
          const fallbackRes = await fetch(fallbackUrl, {
            ...options,
            headers: {
              ...getAuthHeaders(),
              ...(options.headers || {})
            }
          });
          if (fallbackRes.ok) {
            API_CONFIG.ACTIVE_URL = API_CONFIG.FALLBACK_URL;
            return await fallbackRes.json();
          }
        } catch (_) {
          // Keep original error
        }
      }

      throw err;
    }
  }

  /**
   * Health Check
   */
  async function checkHealth() {
    // Candidates to auto-discover: Spring Boot Gateway (8080), FastAPI (8000, 8001, 5000)
    const candidates = [
      'http://localhost:8080/api/health',
      'http://127.0.0.1:8000/health',
      'http://localhost:8000/health',
      'http://127.0.0.1:8001/health',
      'http://localhost:8001/health'
    ];

    for (const endpoint of candidates) {
      try {
        const res = await fetch(endpoint, {
          headers: { 'Accept': 'application/json' },
          signal: AbortSignal.timeout(6000)
        });
        if (res.ok) {
          const data = await res.json();
          API_CONFIG.ACTIVE_URL = endpoint.substring(0, endpoint.lastIndexOf('/'));
          if (API_CONFIG.ACTIVE_URL.endsWith('/api')) {
            API_CONFIG.ACTIVE_URL = API_CONFIG.ACTIVE_URL.replace(/\/api$/, '');
          }
          isConnected = true;
          updateStatusIndicator(true, data);
          return data;
        }
      } catch (_) {
        // Try next candidate
      }
    }

    isConnected = false;
    updateStatusIndicator(false, null);
    throw new Error('Verification service offline');
  }

  function updateStatusIndicator(connected, info) {
    const dot = document.getElementById('service-dot');
    const text = document.getElementById('service-sub-text');
    if (dot && text) {
      if (connected) {
        dot.className = 'status-dot connected';
        text.textContent = 'Operational (Live)';
      } else {
        dot.className = 'status-dot disconnected';
        text.textContent = 'Disconnected';
      }
    }

    // Dynamic Dashboard Banner
    const bannerTitle = document.querySelector('.system-banner-title');
    const bannerDesc = document.querySelector('.system-banner-desc');
    const banner = document.querySelector('.system-banner');
    if (bannerTitle && bannerDesc) {
      if (connected) {
        bannerTitle.textContent = 'AI Verification Engine Live & Connected';
        bannerDesc.textContent = 'Real YOLOv8 computer vision, OCR brand matching, and EXIF authenticity verification active.';
        if (banner) banner.classList.add('banner-connected');
      } else {
        bannerTitle.textContent = 'Verification Service Not Connected';
        bannerDesc.textContent = 'Connect the backend API to enable live YOLOv8 detection, brand verification, and EPR record syncing.';
        if (banner) banner.classList.remove('banner-connected');
      }
    }

    // Dynamic Upload Status Box on Verify Screen
    const serviceBoxes = document.querySelectorAll('.service-status-box');
    serviceBoxes.forEach(box => {
      const span = box.querySelector('span');
      if (span) {
        if (connected) {
          span.textContent = 'AI Backend connected. Ready for real YOLOv8 detection, OCR, and verification scoring.';
          box.classList.add('status-box-connected');
        } else {
          span.textContent = 'Verification service is not connected. Connect the verification backend to process this image.';
          box.classList.remove('status-box-connected');
        }
      }
    });
  }

  /**
   * Send Waste Verification Image to Backend
   */
  async function verifyWasteImage(file) {
    const formData = new FormData();
    formData.append('image', file);

    const headers = {
      'X-Service-Token': 'dev-internal-secret-token'
    };
    if (activeJwtToken) {
      headers['Authorization'] = `Bearer ${activeJwtToken}`;
    }

    const baseCandidates = [
      API_CONFIG.ACTIVE_URL,
      'http://localhost:8080',
      'http://127.0.0.1:8000',
      'http://localhost:8000',
      'http://127.0.0.1:8001'
    ];
    const targets = Array.from(new Set(baseCandidates.filter(Boolean))).map(b => `${b}/api/v1/verification/verify`);

    let lastError = null;
    for (const targetUrl of targets) {
      try {
        const response = await fetch(targetUrl, {
          method: 'POST',
          headers,
          body: formData,
          signal: AbortSignal.timeout(60000)
        });

        if (!response.ok) {
          let errorData;
          try {
            errorData = await response.json();
          } catch (_) {
            errorData = { message: response.statusText, status_code: response.status };
          }
          const errorMsg = errorData.message || errorData.detail || 'Verification failed';
          const error = new Error(errorMsg);
          error.status = response.status;
          error.data = errorData;
          throw error;
        }

        if (targetUrl.startsWith(API_CONFIG.FALLBACK_URL) || targetUrl.includes('8000') || targetUrl.includes('8001')) {
          API_CONFIG.ACTIVE_URL = targetUrl.substring(0, targetUrl.indexOf('/api/v1'));
        }

        isConnected = true;
        updateStatusIndicator(true, null);
        return await response.json();
      } catch (err) {
        lastError = err;
        // If it's a 4xx/5xx from the server, don't try fallback
        if (err.status) {
          throw err;
        }
      }
    }

    throw lastError || new Error('Verification service unreachable');
  }

  /**
   * Send Query to Real AI Assistant Service
   */
  async function sendAssistantMessage(messages, context = null) {
    return await apiFetch('/api/v1/assistant/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        messages,
        context
      })
    });
  }

  /**
   * Process Verified Record for EPR Compliance
   */
  async function processEprCompliance(eprPayload) {
    return await apiFetch('/api/v1/epr/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(eprPayload)
    });
  }

  /**
   * Fetch Verification History from Database
   */
  async function getVerificationHistory(filters = {}) {
    const params = new URLSearchParams();
    if (filters.user_id) params.append('user_id', filters.user_id);
    if (filters.category) params.append('category', filters.category);
    if (filters.status) params.append('status', filters.status);
    if (filters.skip !== undefined) params.append('skip', filters.skip);
    if (filters.limit !== undefined) params.append('limit', filters.limit);

    const queryStr = params.toString() ? `?${params.toString()}` : '';
    return await apiFetch(`/api/v1/verification/history${queryStr}`, {
      method: 'GET'
    });
  }

  /**
   * Fetch GreenCoins Balance & Ledger
   */
  async function getGreenCoinsBalance(userId = null) {
    const query = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    return await apiFetch(`/api/v1/green-coins/balance${query}`, { method: 'GET' });
  }

  async function getGreenCoinsTransactions(skip = 0, limit = 50) {
    return await apiFetch(`/api/v1/green-coins/transactions?skip=${skip}&limit=${limit}`, { method: 'GET' });
  }

  /**
   * Fetch EPR Records & Brand Summary
   */
  async function getEprRecords(brand = null, status = null, skip = 0, limit = 50) {
    const params = new URLSearchParams();
    if (brand) params.append('brand', brand);
    if (status) params.append('status', status);
    params.append('skip', skip);
    params.append('limit', limit);
    return await apiFetch(`/api/v1/epr/records?${params.toString()}`, { method: 'GET' });
  }

  async function getEprSummary() {
    return await apiFetch('/api/v1/epr/summary', { method: 'GET' });
  }

  /**
   * Fetch Real Platform Analytics Summary
   */
  async function getAnalyticsSummary() {
    return await apiFetch('/api/v1/analytics/summary', { method: 'GET' });
  }

  /**
   * Fetch How to Recycle Categories and Guides
   */
  async function getRecyclingCategories() {
    return await apiFetch('/api/v1/recycling/categories', { method: 'GET' });
  }

  async function getRecyclingGuideBySlug(slug) {
    return await apiFetch(`/api/v1/recycling/categories/${encodeURIComponent(slug)}`, { method: 'GET' });
  }

  async function getRecyclingGuideForWasteType(wasteType, confidence = null) {
    const query = confidence !== null ? `?confidence=${confidence}` : '';
    return await apiFetch(`/api/v1/recycling/guide/${encodeURIComponent(wasteType)}${query}`, { method: 'GET' });
  }

  async function getRecyclingRecommendation(payload) {
    return await apiFetch('/api/v1/recycling/recommendation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  }

  /**
   * Fetch Audit Logs (Admin)
   */
  async function getAuditLogs(skip = 0, limit = 50) {
    return await apiFetch(`/api/v1/audit/logs?skip=${skip}&limit=${limit}`, { method: 'GET' });
  }

  /**
   * User Registration & Login
   */
  async function login(email, password) {
    const data = await apiFetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (data && data.access_token) {
      setAuthToken(data.access_token);
    }
    return data;
  }

  async function register(email, fullName, password, role = 'CITIZEN') {
    const data = await apiFetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, full_name: fullName, password, role })
    });
    if (data && data.access_token) {
      setAuthToken(data.access_token);
    }
    return data;
  }

  // Initialize background health polling
  function startHealthMonitor() {
    checkHealth().catch(() => {});
    setInterval(() => {
      checkHealth().catch(() => {});
    }, API_CONFIG.HEALTH_POLL_INTERVAL_MS);
  }

  // Export module to global scope
  window.GreenLoopAPI = {
    checkHealth,
    verifyWasteImage,
    sendAssistantMessage,
    processEprCompliance,
    getVerificationHistory,
    getGreenCoinsBalance,
    getGreenCoinsTransactions,
    getEprRecords,
    getEprSummary,
    getAnalyticsSummary,
    getRecyclingCategories,
    getRecyclingGuideBySlug,
    getRecyclingGuideForWasteType,
    getRecyclingRecommendation,
    getAuditLogs,
    login,
    register,
    setAuthToken,
    startHealthMonitor,
    get isConnected() { return isConnected; }
  };

  document.addEventListener('DOMContentLoaded', startHealthMonitor);

})(window);
