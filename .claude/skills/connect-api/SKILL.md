---
name: connect-api
description: >-
  Connect a Meta Display Glasses webapp to REST APIs or WebSockets. Use when
  the user wants to fetch data from an API, add real-time updates, show
  loading/error states, or cache API responses.
argument-hint: "[api-name-or-url]"
---

## Required reading

Before generating or modifying any code, read both:

- `${CLAUDE_PLUGIN_ROOT}/references/display-guidelines.md`
- `${CLAUDE_PLUGIN_ROOT}/references/performance-guidelines.md`

These define the non-negotiable display physics, input model, and performance budgets for Meta Display Glasses webapps. Do not skip — generated UI that ignores these will fail on-device.

# Connect API to Meta Display Glasses WebApp

Add real API connections to an existing webapp. The base `app.js` template already includes `apiGet()`, `setLoading()`, `setError()`, `showToast()`, and `connectWebSocket()` helpers — this skill shows how to wire them up.

## Prerequisites

- Existing webapp created via `/create-webapp` (which includes the API/UI helpers in `app.js`)

## Steps

### 1. Gather Information

Ask the user:
- **What data?** What information should the app display?
- **Which API?** Specific API, or should we pick one?
- **Refresh behavior?** Manual, auto-refresh interval, or real-time WebSocket?
- **Offline fallback?** Should cached data be served when offline?

### 2. Choose an API

If not specified, recommend from these **free, no-key-required** APIs:

| Category | API | Base URL |
|----------|-----|----------|
| Weather | Open-Meteo | `api.open-meteo.com/v1/forecast` |
| Trivia | Open Trivia DB | `opentdb.com/api.php` |
| Crypto | CoinGecko | `api.coingecko.com/api/v3` |
| Earthquakes | USGS | `earthquake.usgs.gov/earthquakes/feed/v1.0` |
| Wikipedia | Wikipedia REST | `en.wikipedia.org/api/rest_v1` |
| Recipes | TheMealDB | `themealdb.com/api/json/v1/1` |
| Countries | REST Countries | `restcountries.com/v3.1` |
| Jokes | Official Joke API | `official-joke-api.appspot.com` |
| Pokemon | PokeAPI | `pokeapi.co/api/v2` |
| IP Location | ipapi | `ipapi.co/json/` |

### 3. Add Loading and Error UI

Add these elements inside the relevant screen in `index.html` (the CSS is already in `styles.css` from `/create-webapp`):

```html
<div id="loading" class="loading-container hidden">
  <div class="loading-spinner"></div>
  <div class="loading-text">Loading...</div>
</div>

<div id="error" class="error-container hidden">
  <div class="error-icon">&#9888;</div>
  <div class="error-message">Something went wrong</div>
  <button class="nav-item focusable" data-action="refresh">Try Again</button>
</div>
```

Add a refresh button to the nav bar:

```html
<button class="nav-item focusable" data-action="refresh">&#8635; Refresh</button>
```

### 4. Update API Configuration

In `app.js`, update the `CONFIG` object:

```javascript
api: {
  baseUrl: 'https://api.example.com',
  cacheDuration: 5 * 60 * 1000,
},
```

### 5. Add Data Fetching

Use the existing `apiGet()` helper in `onScreenEnter()`:

```javascript
function onScreenEnter(screenId) {
  switch (screenId) {
    case 'home':
      loadData();
      break;
  }
}

function loadData() {
  apiGet(CONFIG.api.baseUrl + '/endpoint', { cacheKey: 'my-data' })
    .then(function(data) {
      renderData(data);
    })
    .catch(function() {
      // Error already shown by apiGet
    });
}
```

### 6. Add Refresh Action

In `handleAppAction()`:

```javascript
case 'refresh':
  state.cache = {};
  onScreenEnter(state.currentScreen);
  break;
```

### 7. For WebSocket Connections

Use the existing `connectWebSocket()` helper:

```javascript
var ws = connectWebSocket('wss://stream.example.com/data', {
  onOpen: function() { showToast('Connected', 'success'); },
  onMessage: function(data) { updateDisplay(data); },
  onClose: function() { showToast('Reconnecting...', 'warning'); },
  onError: function() { showToast('Connection error', 'error'); },
});
```

### 8. Add Auto-Refresh (Optional)

For periodic updates:

```javascript
var refreshInterval = null;

function startAutoRefresh(intervalMs) {
  stopAutoRefresh();
  refreshInterval = setInterval(function() {
    onScreenEnter(state.currentScreen);
  }, intervalMs || 60000);
}

function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
}
```

Start in `init()`: `startAutoRefresh(60000);`

## Complete Examples

### Weather API

```javascript
function loadWeather() {
  var url = 'https://api.open-meteo.com/v1/forecast' +
    '?latitude=40.71&longitude=-74.01' +
    '&current_weather=true' +
    '&daily=temperature_2m_max,temperature_2m_min,weathercode' +
    '&timezone=auto&forecast_days=5';

  apiGet(url, { cacheKey: 'weather' })
    .then(function(data) {
      var w = data.current_weather;
      document.getElementById('temp').textContent = Math.round(w.temperature) + '\u00B0';
      document.getElementById('condition').textContent = getWeatherLabel(w.weathercode);
      document.getElementById('wind').textContent = w.windspeed + ' km/h';
      renderForecast(data.daily);
    });
}
```

### Crypto Price Tracker

```javascript
function loadPrices() {
  var url = 'https://api.coingecko.com/api/v3/simple/price' +
    '?ids=bitcoin,ethereum,solana' +
    '&vs_currencies=usd&include_24hr_change=true';

  apiGet(url, { cacheKey: 'crypto', cacheDuration: 30000 })
    .then(function(data) {
      Object.keys(data).forEach(function(coin) {
        var price = data[coin].usd;
        var change = data[coin].usd_24h_change;
        document.getElementById(coin + '-price').textContent = '$' + price.toLocaleString();
        var changeEl = document.getElementById(coin + '-change');
        changeEl.textContent = (change >= 0 ? '+' : '') + change.toFixed(2) + '%';
        changeEl.className = 'badge ' + (change >= 0 ? 'badge-success' : 'badge-danger');
      });
    });
}
```

## Verify

- [ ] Loading spinner appears during API calls
- [ ] Error state appears on network failure
- [ ] Cached data is served on repeated loads
- [ ] Refresh button clears cache and fetches fresh data
- [ ] All API-rendered elements have `.focusable` class for D-pad navigation

## Related Skills

- `/add-ui` — Add screens, buttons, and components for API data
