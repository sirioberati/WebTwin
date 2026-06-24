---
name: add-local-storage
description: >-
  Add client-side data persistence to a Meta Display Glasses webapp using the
  W3C Web Storage API (localStorage and sessionStorage). Use when the user wants
  to save settings, cache data, persist state, or store user preferences.
argument-hint: "[purpose: settings|cache|state|preferences]"
---

# Add Local Storage to Meta Display Glasses WebApp

Add client-side data persistence using the standard [W3C Web Storage API](https://www.w3.org/TR/webstorage/). Supports `localStorage` (persists across sessions) and `sessionStorage` (cleared when the session ends). No SDK required.

## Prerequisites

- Existing webapp created via `/create-webapp`

## Storage Types

| API | Persistence | Use Cases |
|-----|------------|-----------|
| `localStorage` | Persists until explicitly cleared | User settings, saved data, app state, preferences |
| `sessionStorage` | Cleared when session ends | Temporary state, form drafts, navigation context |

Both APIs share the same interface and store string key-value pairs.

## Steps

### 1. Gather Information

Ask the user:
- **What data?** Settings, preferences, app state, cached API responses?
- **Which storage?** Persistent (`localStorage`) or session-only (`sessionStorage`)?
- **Data shape?** Single values or structured objects?

### 2. Add Storage Helpers

In `app.js`, add helpers for reading and writing structured data:

```javascript
var STORAGE_KEY = 'mdg_myapp';

function saveData(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function loadData() {
  try {
    var saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch (e) {
    return null;
  }
}

function clearData() {
  localStorage.removeItem(STORAGE_KEY);
}
```

### 3. Wire Up to App State

Load saved data on startup and save on changes:

```javascript
// On init
var saved = loadData();
if (saved) {
  state.data = saved;
}

// After any state change
state.data.score = 100;
saveData(state.data);
```

### 4. Add Settings UI (if needed)

For user-facing settings with persistence:

```javascript
case 'toggle-dark-mode':
  state.data.darkMode = !state.data.darkMode;
  document.body.classList.toggle('light-mode', !state.data.darkMode);
  saveData(state.data);
  break;

case 'reset-data':
  clearData();
  state.data = {};
  showToast('Data cleared');
  break;
```

## Patterns

### Save User Preferences

```javascript
function savePreference(key, value) {
  var prefs = loadData() || {};
  prefs[key] = value;
  saveData(prefs);
}

function getPreference(key, defaultValue) {
  var prefs = loadData() || {};
  return prefs[key] !== undefined ? prefs[key] : defaultValue;
}
```

### Cache API Responses

```javascript
function cacheResponse(url, data, ttlMs) {
  var entry = { data: data, timestamp: Date.now(), ttl: ttlMs };
  localStorage.setItem('cache_' + url, JSON.stringify(entry));
}

function getCachedResponse(url) {
  try {
    var entry = JSON.parse(localStorage.getItem('cache_' + url));
    if (entry && Date.now() - entry.timestamp < entry.ttl) {
      return entry.data;
    }
  } catch (e) {}
  return null;
}
```

### Session-Only State

Use `sessionStorage` for data that should not survive a restart:

```javascript
// Save temporary navigation context
sessionStorage.setItem('returnScreen', 'home');

// Restore on load
var returnTo = sessionStorage.getItem('returnScreen') || 'home';
```

## Verify

- [ ] Data persists after page refresh (localStorage)
- [ ] Session data clears when session ends (sessionStorage)
- [ ] App handles missing/corrupt stored data gracefully
- [ ] Reset/clear action works

## Related Skills

- `/add-ui` — Add settings screens and toggle buttons
- `/connect-api` — Fetch data to cache locally
