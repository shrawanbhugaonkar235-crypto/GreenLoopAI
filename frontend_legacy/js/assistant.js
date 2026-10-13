/**
 * ====================================================================
 * GREENLOOPAI — REAL AI ASSISTANT CLIENT
 * Real-time conversation with OpenAI Responses API through Spring Security & FastAPI
 * No fake chatbot, no hardcoded answers, no fake typing animations.
 * ====================================================================
 */

(function (window) {
  'use strict';

  // In-memory conversation state for current browser session (NEVER persisted to localStorage or DB)
  let conversationHistory = [];
  let isThinking = false;
  let isOpen = false;
  let isMinimized = false;

  // DOM Elements
  let triggerBtn = null;
  let chatWindow = null;
  let messagesContainer = null;
  let inputField = null;
  let sendBtn = null;
  let minimizeBtn = null;
  let closeBtn = null;
  let clearBtn = null;

  function initAssistant() {
    triggerBtn = document.getElementById('ai-assistant-trigger');
    chatWindow = document.getElementById('ai-assistant-window');
    messagesContainer = document.getElementById('ai-chat-messages');
    inputField = document.getElementById('ai-chat-input');
    sendBtn = document.getElementById('ai-chat-send');
    minimizeBtn = document.getElementById('ai-btn-minimize');
    closeBtn = document.getElementById('ai-btn-close');
    clearBtn = document.getElementById('ai-btn-clear');

    if (!triggerBtn || !chatWindow) {
      return;
    }

    // Event Listeners
    triggerBtn.addEventListener('click', toggleAssistant);
    if (closeBtn) closeBtn.addEventListener('click', closeAssistant);
    if (minimizeBtn) minimizeBtn.addEventListener('click', toggleMinimize);
    if (clearBtn) clearBtn.addEventListener('click', clearConversation);

    if (sendBtn) {
      sendBtn.addEventListener('click', handleUserSendMessage);
    }

    if (inputField) {
      inputField.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          handleUserSendMessage();
        }
      });
    }

    // Quick prompt buttons delegation
    if (messagesContainer) {
      messagesContainer.addEventListener('click', (e) => {
        const promptBtn = e.target.closest('.ai-quick-prompt-btn');
        if (promptBtn && !isThinking) {
          const promptText = promptBtn.getAttribute('data-prompt') || promptBtn.textContent.trim();
          if (inputField) inputField.value = promptText;
          handleUserSendMessage();
        }
      });
    }
  }

  function toggleAssistant() {
    if (isOpen) {
      closeAssistant();
    } else {
      openAssistant();
    }
  }

  function openAssistant() {
    isOpen = true;
    chatWindow.classList.add('active');
    chatWindow.classList.remove('minimized');
    isMinimized = false;
    if (inputField) {
      setTimeout(() => inputField.focus(), 150);
    }
  }

  function closeAssistant() {
    isOpen = false;
    chatWindow.classList.remove('active');
  }

  function toggleMinimize() {
    isMinimized = !isMinimized;
    chatWindow.classList.toggle('minimized', isMinimized);
  }

  function clearConversation() {
    conversationHistory = [];
    renderMessages();
  }

  /**
   * Render in-memory messages into UI
   */
  function renderMessages() {
    if (!messagesContainer) return;

    if (conversationHistory.length === 0) {
      messagesContainer.innerHTML = `
        <div class="ai-empty-state">
          <div class="ai-empty-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a10 10 0 0 1 10 10c0 5.5-4.5 10-10 10S2 17.5 2 12A10 10 0 0 1 12 2z"/>
              <path d="M12 16v-4M12 8h.01"/>
            </svg>
          </div>
          <div class="ai-empty-title">How can I help you?</div>
          <div class="ai-empty-desc">Ask questions about GreenLoopAI, waste verification, EPR compliance, or technical details.</div>
          <div class="ai-quick-prompts">
            <button class="ai-quick-prompt-btn" data-prompt="What is the GreenLoopAI Detect → Verify → Reward workflow?">What is the Detect → Verify → Reward workflow?</button>
            <button class="ai-quick-prompt-btn" data-prompt="How is the verification score calculated?">How is the verification score calculated?</button>
            <button class="ai-quick-prompt-btn" data-prompt="How does EPR compliance work in GreenLoopAI?">How does EPR compliance work?</button>
          </div>
        </div>
      `;
      return;
    }

    let html = '';
    conversationHistory.forEach((msg) => {
      const isUser = msg.role === 'user';
      const isError = msg.isError;
      const roleClass = isUser ? 'user' : 'assistant' + (isError ? ' error' : '');

      // Sanitize output for HTML safety
      const safeContent = escapeHtml(msg.content).replace(/\n/g, '<br>');

      html += `
        <div class="ai-message ${roleClass}">
          <div class="ai-message-bubble">
            ${safeContent}
          </div>
        </div>
      `;
    });

    if (isThinking) {
      html += `
        <div class="ai-thinking">
          <div class="ai-thinking-dots">
            <div class="ai-thinking-dot"></div>
            <div class="ai-thinking-dot"></div>
            <div class="ai-thinking-dot"></div>
          </div>
          <span>GreenLoopAI is thinking...</span>
        </div>
      `;
    }

    messagesContainer.innerHTML = html;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  async function handleUserSendMessage() {
    if (!inputField || isThinking) return;

    const messageText = inputField.value.trim();
    if (!messageText) return;

    // Append user message to in-memory history
    conversationHistory.push({
      role: 'user',
      content: messageText
    });

    inputField.value = '';
    isThinking = true;
    if (sendBtn) sendBtn.disabled = true;
    renderMessages();

    // Gather minimal UI context if available (strictly real, never fabricated)
    const context = {
      page: window.location.hash ? window.location.hash.replace('#', '') : 'dashboard'
    };

    // If active verification result exists in memory
    if (window.GreenLoopActiveResult) {
      context.current_result = {
        verification_id: window.GreenLoopActiveResult.verification_id,
        score: window.GreenLoopActiveResult.verification_score,
        brand: window.GreenLoopActiveResult.brand_detection?.brand,
        status: window.GreenLoopActiveResult.status
      };
    }

    try {
      // Call Spring Boot / FastAPI backend
      const response = await window.GreenLoopAPI.sendAssistantMessage(conversationHistory, context);

      if (response && response.answer) {
        conversationHistory.push({
          role: 'assistant',
          content: response.answer
        });
      } else {
        conversationHistory.push({
          role: 'assistant',
          content: 'AI service temporarily unavailable.',
          isError: true
        });
      }
    } catch (err) {
      let errorMessage = 'AI Assistant is temporarily unavailable.';

      if (err.data && err.data.message) {
        if (err.data.message.includes('AI_SERVICE_NOT_CONFIGURED')) {
          errorMessage = 'AI Assistant is not configured.';
        } else if (err.status === 429) {
          errorMessage = 'The assistant is temporarily busy. Please try again.';
        } else if (err.status === 401) {
          errorMessage = 'Authentication required.';
        } else if (err.status === 403) {
          errorMessage = "You don't have permission to use this feature.";
        } else {
          errorMessage = err.data.message;
        }
      } else if (err.status === 503) {
        errorMessage = 'AI Assistant is temporarily unavailable.';
      } else if (err.status === 429) {
        errorMessage = 'The assistant is temporarily busy. Please try again.';
      }

      conversationHistory.push({
        role: 'assistant',
        content: errorMessage,
        isError: true
      });
    } finally {
      isThinking = false;
      if (sendBtn) sendBtn.disabled = false;
      renderMessages();
      if (inputField) inputField.focus();
    }
  }

  function escapeHtml(text) {
    if (!text) return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Initialize on DOM load
  document.addEventListener('DOMContentLoaded', initAssistant);

  window.GreenLoopAssistant = {
    open: openAssistant,
    close: closeAssistant,
    clear: clearConversation
  };

})(window);
