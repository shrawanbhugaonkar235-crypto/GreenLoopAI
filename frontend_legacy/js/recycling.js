/**
 * ====================================================================
 * GREENLOOPAI — HOW TO RECYCLE MODULE
 * Real, verified step-by-step recycling preparation & segregation guides
 * Integrated with waste verification and AI Assistant.
 * ====================================================================
 */

(function (window) {
  'use strict';

  let categoriesCache = [];
  let currentActiveGuide = null;

  async function initRecycling() {
    initSearchAndFilter();
    initModalEvents();
    await loadCategories();
  }

  function initSearchAndFilter() {
    const searchInput = document.getElementById('recycling-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase().trim();
        filterCategories(query, getActiveFilterTag());
      });
    }

    const filterTags = document.querySelectorAll('.recycling-filter-tag');
    filterTags.forEach(btn => {
      btn.addEventListener('click', () => {
        filterTags.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const tag = btn.getAttribute('data-tag') || 'all';
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        filterCategories(query, tag);
      });
    });
  }

  function getActiveFilterTag() {
    const activeBtn = document.querySelector('.recycling-filter-tag.active');
    return activeBtn ? activeBtn.getAttribute('data-tag') : 'all';
  }

  function initModalEvents() {
    const modal = document.getElementById('modal-recycling-guide');
    const closeBtn = document.getElementById('btn-close-recycling-modal');
    if (closeBtn && modal) {
      closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
      });
    }

    // Ask AI shortcut button inside modal
    const askAiBtn = document.getElementById('btn-recycling-ask-ai');
    if (askAiBtn) {
      askAiBtn.addEventListener('click', () => {
        if (!currentActiveGuide) return;
        if (modal) modal.classList.remove('active');
        if (window.GreenLoopAssistant) {
          window.GreenLoopAssistant.open();
          const chatInput = document.getElementById('ai-chat-input');
          if (chatInput) {
            chatInput.value = `How do I properly prepare and recycle this ${currentActiveGuide.waste_type}?`;
            const sendBtn = document.getElementById('ai-chat-send');
            if (sendBtn) sendBtn.click();
          }
        }
      });
    }
  }

  async function loadCategories() {
    const grid = document.getElementById('recycling-categories-grid');
    if (!grid) return;

    try {
      const res = await window.GreenLoopAPI.getRecyclingCategories();
      categoriesCache = (res && res.categories) ? res.categories : [];
      renderCategoryCards(categoriesCache);
    } catch (err) {
      grid.innerHTML = `
        <div class="empty-state-container" style="grid-column: 1 / -1;">
          <div class="empty-state-icon">♻</div>
          <div class="empty-state-title">Recycling Guide Service Offline</div>
          <div class="empty-state-desc">Connect the GreenLoopAI backend to access verified household recycling instructions.</div>
        </div>
      `;
    }
  }

  function filterCategories(query, tag) {
    let filtered = categoriesCache;

    if (tag && tag !== 'all') {
      filtered = filtered.filter(c => {
        const slug = c.slug.toLowerCase();
        const name = c.name.toLowerCase();
        if (tag === 'plastic') return slug.includes('plastic');
        if (tag === 'paper') return slug.includes('paper') || slug.includes('cardboard');
        if (tag === 'glass') return slug.includes('glass');
        if (tag === 'metal') return slug.includes('metal') || slug.includes('aluminium');
        if (tag === 'e-waste') return slug.includes('e-waste') || slug.includes('batteries');
        if (tag === 'organic') return slug.includes('organic') || slug.includes('wet');
        if (tag === 'textile') return slug.includes('textile');
        if (tag === 'hazardous') return slug.includes('hazardous') || slug.includes('batteries');
        return true;
      });
    }

    if (query) {
      filtered = filtered.filter(c => 
        c.name.toLowerCase().includes(query) ||
        c.description.toLowerCase().includes(query) ||
        c.slug.toLowerCase().includes(query)
      );
    }

    renderCategoryCards(filtered);
  }

  function renderCategoryCards(categories) {
    const grid = document.getElementById('recycling-categories-grid');
    if (!grid) return;

    if (categories.length === 0) {
      grid.innerHTML = `
        <div class="empty-state-container" style="grid-column: 1 / -1;">
          <div class="empty-state-icon">🔍</div>
          <div class="empty-state-title">No Matching Categories</div>
          <div class="empty-state-desc">Try searching for a different household material (e.g. bottle, cardboard, phone, battery).</div>
        </div>
      `;
      return;
    }

    grid.innerHTML = categories.map(cat => {
      const badgeClass = getBadgeClassForStatus(cat.recyclability_status);
      const icon = cat.icon || getIconForSlug(cat.slug);

      return `
        <div class="recycling-category-card" data-slug="${cat.slug}">
          <div class="cat-card-header">
            <span class="cat-card-icon">${icon}</span>
            <span class="badge ${badgeClass}">${formatStatusLabel(cat.recyclability_status)}</span>
          </div>
          <h3 class="cat-card-title">${cat.name}</h3>
          <p class="cat-card-desc">${cat.description}</p>
          <div class="cat-card-footer">
            <button class="btn btn-outline-primary btn-sm btn-view-guide" data-slug="${cat.slug}">View Step-by-Step Guide →</button>
          </div>
        </div>
      `;
    }).join('');

    // Attach card click handlers
    grid.querySelectorAll('.btn-view-guide').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const slug = btn.getAttribute('data-slug');
        openGuideBySlug(slug);
      });
    });

    grid.querySelectorAll('.recycling-category-card').forEach(card => {
      card.addEventListener('click', () => {
        const slug = card.getAttribute('data-slug');
        openGuideBySlug(slug);
      });
    });
  }

  async function openGuideBySlug(slug) {
    try {
      const guide = await window.GreenLoopAPI.getRecyclingGuideBySlug(slug);
      renderGuideDetail(guide);
    } catch (err) {
      if (window.App && window.App.showToast) {
        window.App.showToast('Recycling Guide', 'Failed to load recycling instructions.', 'error');
      }
    }
  }

  async function openGuideForWaste(wasteType, confidence = null) {
    try {
      const guide = await window.GreenLoopAPI.getRecyclingGuideForWasteType(wasteType, confidence);
      renderGuideDetail(guide);
    } catch (err) {
      console.warn('Direct waste guide lookup failed, trying fallback slug...', err);
      try {
        const normalized = String(wasteType || '').toLowerCase();
        let matchedSlug = 'plastic-bottles-containers';
        if (normalized.includes('wood') || normalized.includes('furniture') || normalized.includes('table') || normalized.includes('chair') || normalized.includes('bed') || normalized.includes('bench') || normalized.includes('couch')) {
          matchedSlug = 'wood-bulky-furniture';
        } else if (normalized.includes('paper') || normalized.includes('cardboard') || normalized.includes('box')) {
          matchedSlug = 'paper-cardboard';
        } else if (normalized.includes('glass')) {
          matchedSlug = 'glass-bottles-jars';
        } else if (normalized.includes('metal') || normalized.includes('can') || normalized.includes('aluminum')) {
          matchedSlug = 'metal-cans-packaging';
        } else if (normalized.includes('electronic') || normalized.includes('phone') || normalized.includes('e-waste')) {
          matchedSlug = 'e-waste';
        } else if (normalized.includes('batter')) {
          matchedSlug = 'batteries';
        } else if (normalized.includes('organic') || normalized.includes('food') || normalized.includes('fruit') || normalized.includes('compost')) {
          matchedSlug = 'organic-wet-waste';
        } else if (normalized.includes('textile') || normalized.includes('fabric') || normalized.includes('clothes')) {
          matchedSlug = 'textiles-fabrics';
        } else if (normalized.includes('hazard') || normalized.includes('chemical') || normalized.includes('paint')) {
          matchedSlug = 'hazardous-waste';
        }
        const guide = await window.GreenLoopAPI.getRecyclingGuideBySlug(matchedSlug);
        renderGuideDetail(guide);
      } catch (fallbackErr) {
        if (window.App && window.App.showToast) {
          window.App.showToast('Recycling Guide', 'Failed to load recycling instructions for this item.', 'error');
        }
      }
    }
  }

  function renderGuideDetail(guide) {
    currentActiveGuide = guide;
    const modal = document.getElementById('modal-recycling-guide');
    const container = document.getElementById('recycling-guide-content');
    if (!modal || !container) return;

    const badgeClass = getBadgeClassForStatus(guide.recyclability_status);
    const icon = guide.icon || '♻';

    // 1. Preparation checklist HTML
    const prepHtml = guide.preparation_summary && guide.preparation_summary.length > 0
      ? `
        <div class="recycling-section prep-checklist-section">
          <h4 class="recycling-section-title">Preparation Checklist</h4>
          <ul class="prep-checklist">
            ${guide.preparation_summary.map(item => `<li><span class="prep-check">✓</span> <span>${item}</span></li>`).join('')}
          </ul>
        </div>
      `
      : '';

    // 2. Step-by-step Timeline HTML
    const stepsHtml = guide.steps && guide.steps.length > 0
      ? `
        <div class="recycling-section">
          <h4 class="recycling-section-title">Step-by-Step Recycling Lifecycle</h4>
          <div class="recycling-timeline">
            ${guide.steps.map(step => `
              <div class="timeline-step">
                <div class="step-badge">${step.step_number}</div>
                <div class="step-content">
                  <div class="step-title">${step.title}</div>
                  <div class="step-desc">${step.description}</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `
      : '';

    // 3. Prominent Safety Warnings HTML
    const warningsHtml = guide.warnings && guide.warnings.length > 0
      ? `
        <div class="recycling-section warnings-section">
          <h4 class="recycling-section-title">Safety & Handling Warnings</h4>
          ${guide.warnings.map(warn => {
            const warnClass = getWarningSeverityClass(warn.severity);
            return `
              <div class="warning-callout ${warnClass}">
                <div class="warning-header">
                  <span class="warning-icon">⚠</span>
                  <span class="warning-title">${warn.title}</span>
                  <span class="badge badge-warning-severity">${warn.severity}</span>
                </div>
                <div class="warning-body">${warn.description}</div>
              </div>
            `;
          }).join('')}
        </div>
      `
      : '';

    // 4. Actionable Do / Do Not Rules HTML
    const rulesHtml = guide.rules && guide.rules.length > 0
      ? `
        <div class="recycling-section">
          <h4 class="recycling-section-title">Segregation Rules</h4>
          <div class="rules-grid">
            ${guide.rules.map(r => {
              const isDo = r.rule_type === 'DO';
              const isDanger = r.rule_type === 'DATA_SAFETY' || r.rule_type === 'SPECIAL_HANDLING';
              const ruleClass = isDo ? 'rule-do' : (isDanger ? 'rule-special' : 'rule-dont');
              const ruleIcon = isDo ? '✓' : (isDanger ? '⚡' : '✗');

              return `
                <div class="rule-card ${ruleClass}">
                  <div class="rule-title"><span class="rule-icon">${ruleIcon}</span> ${r.title}</div>
                  <div class="rule-desc">${r.description}</div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `
      : '';

    // 5. Disposal Route & Stream Info HTML
    const disp = guide.disposal_method || {};
    const disposalHtml = `
      <div class="recycling-section disposal-section">
        <h4 class="recycling-section-title">Recommended Disposal Route</h4>
        <div class="disposal-card">
          <div class="disposal-row">
            <span class="disposal-label">Primary Route:</span>
            <strong class="disposal-val">${disp.primary_route || 'Municipal Dry Bin'}</strong>
          </div>
          <div class="disposal-row">
            <span class="disposal-label">Stream:</span>
            <span class="disposal-val">${disp.stream_name || 'Dry Recyclables'}</span>
          </div>
          <div class="disposal-row">
            <span class="disposal-label">Target Container:</span>
            <span class="badge badge-bin">${disp.bin_color || 'Blue Bin'}</span>
          </div>
          ${disp.special_notes ? `<div class="disposal-notes"><small>${disp.special_notes}</small></div>` : ''}
        </div>
      </div>
    `;

    // 6. Local Guidance Note HTML
    const localNoteHtml = `
      <div class="local-guidance-banner">
        <span class="info-icon">ℹ</span>
        <span>${guide.local_guidance_message || 'General recycling standards are shown. Local collection rules may vary.'}</span>
      </div>
    `;

    container.innerHTML = `
      <div class="guide-header">
        <div class="guide-header-icon">${icon}</div>
        <div class="guide-header-text">
          <div class="guide-meta-top">
            <span class="badge ${badgeClass}">${formatStatusLabel(guide.recyclability_status)}</span>
            <span class="guide-category-badge">${guide.category_name}</span>
          </div>
          <h2 class="guide-title">${guide.title}</h2>
          <p class="guide-summary">${guide.summary}</p>
        </div>
      </div>

      ${prepHtml}
      ${stepsHtml}
      ${warningsHtml}
      ${rulesHtml}
      ${disposalHtml}
      ${localNoteHtml}
    `;

    modal.classList.add('active');
  }

  function getBadgeClassForStatus(status) {
    if (!status) return 'badge-secondary';
    const s = status.toUpperCase();
    if (s.includes('RECYCLABLE') && !s.includes('CONDITIONALLY') && !s.includes('NOT')) return 'badge-verified';
    if (s.includes('CONDITIONAL')) return 'badge-gold';
    if (s.includes('SPECIAL')) return 'badge-special-handling';
    if (s.includes('NOT')) return 'badge-rejected';
    return 'badge-secondary';
  }

  function formatStatusLabel(status) {
    if (!status) return 'UNKNOWN';
    return status.replace(/_/g, ' ');
  }

  function getWarningSeverityClass(severity) {
    if (!severity) return 'warn-caution';
    const s = severity.toUpperCase();
    if (s === 'DANGER') return 'warn-danger';
    if (s === 'WARNING') return 'warn-warning';
    if (s === 'CAUTION') return 'warn-caution';
    return 'warn-info';
  }

  function getIconForSlug(slug) {
    if (slug.includes('plastic')) return '🧴';
    if (slug.includes('paper') || slug.includes('cardboard')) return '📦';
    if (slug.includes('glass')) return '🍾';
    if (slug.includes('metal') || slug.includes('aluminium')) return '🥫';
    if (slug.includes('e-waste')) return '💻';
    if (slug.includes('batter')) return '🔋';
    if (slug.includes('organic') || slug.includes('wet')) return '🍎';
    if (slug.includes('textile')) return '👕';
    if (slug.includes('hazardous')) return '☣';
    return '♻';
  }

  // Initialize on DOM Ready
  document.addEventListener('DOMContentLoaded', initRecycling);

  // Export to global scope
  window.GreenLoopRecycling = {
    openGuideBySlug,
    openGuideForWaste,
    loadCategories
  };

})(window);
