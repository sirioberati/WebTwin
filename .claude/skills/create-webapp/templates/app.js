(function() {
  'use strict';

  // ==================== CONFIG ====================
  var CONFIG = {
    appName: 'My App',
    storageKey: 'mdg_myapp',
    api: {
      baseUrl: 'https://api.example.com',
      cacheDuration: 5 * 60 * 1000,
    },
  };

  // ==================== STATE ====================
  var state = {
    currentScreen: 'home',
    screenHistory: [],
    isLoading: false,
    error: null,
    data: {},
    cache: {},
  };

  // ==================== DOM REFS ====================
  var screens = {};

  function collectScreens() {
    document.querySelectorAll('.screen').forEach(function(s) {
      if (s.id) screens[s.id] = s;
    });
  }

  // ==================== NAVIGATION ====================
  function navigateTo(screenId, options) {
    options = options || {};
    var addToHistory = options.addToHistory !== false;

    if (addToHistory && state.currentScreen) {
      state.screenHistory.push(state.currentScreen);
    }

    Object.values(screens).forEach(function(s) { s.classList.add('hidden'); });
    if (screens[screenId]) {
      screens[screenId].classList.remove('hidden');
      state.currentScreen = screenId;
      onScreenEnter(screenId);
      focusFirst(screens[screenId]);
    }
  }

  function navigateBack() {
    if (state.screenHistory.length > 0) {
      navigateTo(state.screenHistory.pop(), { addToHistory: false });
    }
  }

  // ==================== FOCUS MANAGEMENT ====================
  function focusFirst(container) {
    var el = container.querySelector('.focusable:not([disabled]):not(.hidden)');
    if (el) el.focus();
  }

  function moveFocus(direction) {
    var container = screens[state.currentScreen];
    if (!container) return;

    var focusables = Array.from(
      container.querySelectorAll('.focusable:not([disabled]):not(.hidden)')
    );
    if (focusables.length === 0) return;

    var current = document.activeElement;
    var idx = focusables.indexOf(current);

    if (idx === -1) {
      focusFirst(container);
      return;
    }

    var nextIdx;
    if (direction === 'up' || direction === 'left') {
      nextIdx = idx > 0 ? idx - 1 : focusables.length - 1;
    } else {
      nextIdx = idx < focusables.length - 1 ? idx + 1 : 0;
    }
    focusables[nextIdx].focus();

    var scrollParent = focusables[nextIdx].closest('.content, .list-container');
    if (scrollParent) {
      focusables[nextIdx].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }

  // ==================== API LAYER ====================
  function apiGet(url, options) {
    options = options || {};
    var cacheKey = options.cacheKey || url;
    var cacheDuration = options.cacheDuration || CONFIG.api.cacheDuration;

    if (!options.noCache && state.cache[cacheKey]) {
      var cached = state.cache[cacheKey];
      if (Date.now() - cached.timestamp < cacheDuration) {
        return Promise.resolve(cached.data);
      }
    }

    setLoading(true);
    clearError();

    return fetch(url)
      .then(function(res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function(data) {
        state.cache[cacheKey] = { data: data, timestamp: Date.now() };
        setLoading(false);
        return data;
      })
      .catch(function(err) {
        setLoading(false);
        setError(err.message || 'Failed to load data');
        throw err;
      });
  }

  function connectWebSocket(url, handlers) {
    var ws = null;
    var reconnectTimer = null;
    var reconnectDelay = 1000;

    function connect() {
      ws = new WebSocket(url);

      ws.onopen = function() {
        reconnectDelay = 1000;
        if (handlers.onOpen) handlers.onOpen();
      };

      ws.onmessage = function(event) {
        try {
          var data = JSON.parse(event.data);
          if (handlers.onMessage) handlers.onMessage(data);
        } catch (e) {
          if (handlers.onMessage) handlers.onMessage(event.data);
        }
      };

      ws.onclose = function() {
        if (handlers.onClose) handlers.onClose();
        reconnectTimer = setTimeout(function() {
          reconnectDelay = Math.min(reconnectDelay * 2, 30000);
          connect();
        }, reconnectDelay);
      };

      ws.onerror = function() {
        if (handlers.onError) handlers.onError();
      };
    }

    connect();

    return {
      send: function(data) {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(typeof data === 'string' ? data : JSON.stringify(data));
        }
      },
      close: function() {
        clearTimeout(reconnectTimer);
        if (ws) ws.close();
      },
    };
  }

  // ==================== UI HELPERS ====================
  function setLoading(isLoading) {
    state.isLoading = isLoading;
    var spinner = document.getElementById('loading');
    if (spinner) {
      spinner.classList.toggle('hidden', !isLoading);
    }
  }

  function setError(message) {
    state.error = message;
    var errorEl = document.getElementById('error');
    if (errorEl) {
      errorEl.classList.remove('hidden');
      var msgEl = errorEl.querySelector('.error-message');
      if (msgEl) msgEl.textContent = message;
    }
  }

  function clearError() {
    state.error = null;
    var errorEl = document.getElementById('error');
    if (errorEl) errorEl.classList.add('hidden');
  }

  function showToast(message, type) {
    var toast = document.getElementById('toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toast';
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = 'toast' + (type ? ' ' + type : '');
    toast.offsetHeight;
    toast.classList.add('visible');
    setTimeout(function() { toast.classList.remove('visible'); }, 2500);
  }

  function renderList(containerId, items, template) {
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    if (items.length === 0) {
      container.innerHTML = '<div class="error-container"><div class="error-message">No items found</div></div>';
      return;
    }

    items.forEach(function(item, index) {
      var el = template(item, index);
      if (typeof el === 'string') {
        container.insertAdjacentHTML('beforeend', el);
      } else {
        container.appendChild(el);
      }
    });
  }

  // ==================== DATA PERSISTENCE ====================
  function loadData() {
    try {
      var saved = localStorage.getItem(CONFIG.storageKey);
      if (saved) {
        var data = JSON.parse(saved);
        Object.assign(state.data, data);
      }
    } catch (e) {
      console.error('[Storage] Load error:', e);
    }
  }

  function saveData() {
    try {
      localStorage.setItem(CONFIG.storageKey, JSON.stringify(state.data));
    } catch (e) {
      console.error('[Storage] Save error:', e);
    }
  }

  // ==================== ACTION HANDLING ====================
  function handleAction(action, element) {
    switch (action) {
      case 'back':
        navigateBack();
        break;
      case 'refresh':
        onScreenEnter(state.currentScreen);
        break;
      default:
        handleAppAction(action, element);
        break;
    }
  }

  // === CUSTOMIZE: Add app-specific actions here ===
  function handleAppAction(action, element) {
    console.log('[Action]', action);
  }

  // === CUSTOMIZE: Add screen-specific initialization here ===
  function onScreenEnter(screenId) {
    // Load data, refresh API, etc.
  }

  // ==================== EVENT LISTENERS ====================
  function setupEvents() {
    document.addEventListener('click', function(e) {
      var actionEl = e.target.closest('[data-action]');
      if (actionEl) handleAction(actionEl.dataset.action, actionEl);
    });

    document.addEventListener('keydown', function(e) {
      var isInput = document.activeElement &&
        (document.activeElement.tagName === 'INPUT' ||
         document.activeElement.tagName === 'TEXTAREA');
      if (isInput && !['Escape', 'Enter'].includes(e.key)) {
        return;
      }

      switch (e.key) {
        case 'ArrowUp':
          moveFocus('up');
          e.preventDefault();
          break;
        case 'ArrowDown':
          moveFocus('down');
          e.preventDefault();
          break;
        case 'ArrowLeft':
          moveFocus('left');
          e.preventDefault();
          break;
        case 'ArrowRight':
          moveFocus('right');
          e.preventDefault();
          break;
        case 'Enter':
          if (isInput) {
            var submitAction = document.activeElement.dataset.submitAction;
            if (submitAction) handleAction(submitAction, document.activeElement);
          } else if (document.activeElement &&
                     document.activeElement.classList.contains('focusable')) {
            document.activeElement.click();
          }
          e.preventDefault();
          break;
        case 'Escape':
          navigateBack();
          e.preventDefault();
          break;
      }
    });
  }

  // ==================== INITIALIZATION ====================
  function init() {
    collectScreens();
    setupEvents();
    loadData();

    setTimeout(function() {
      navigateTo('home', { addToHistory: false });
    }, 100);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
