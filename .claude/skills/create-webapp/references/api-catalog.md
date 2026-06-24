# API Catalog and Integration Patterns

## Free Public APIs (No API Key Required)

| API | URL Pattern | Returns |
|-----|------------|---------|
| Open-Meteo Weather | `api.open-meteo.com/v1/forecast?latitude=X&longitude=Y&current_weather=true` | Temperature, wind, conditions |
| Open Trivia DB | `opentdb.com/api.php?amount=10&category=9` | Trivia questions |
| Wikipedia | `en.wikipedia.org/api/rest_v1/page/summary/TITLE` | Article summaries |
| CoinGecko | `api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd` | Crypto prices |
| USGS Earthquakes | `earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson` | Earthquake data |
| ISS Position | `api.open-notify.org/iss-now.json` | ISS lat/long |
| Random Jokes | `official-joke-api.appspot.com/random_joke` | Setup + punchline |
| Dog Facts | `dogapi.dog/api/v2/facts` | Random dog facts |
| Numbers API | `numbersapi.com/random/trivia?json` | Number facts |
| TheMealDB | `themealdb.com/api/json/v1/1/random.php` | Random recipes |
| PokeAPI | `pokeapi.co/api/v2/pokemon/IDORNAME` | Pokemon data |
| REST Countries | `restcountries.com/v3.1/name/COUNTRY` | Country info |
| IP Geolocation | `ipapi.co/json/` | Location from IP |

## REST API with Loading + Error States

```javascript
function loadWeather(city) {
  var url = 'https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.01&current_weather=true';
  apiGet(url, { cacheKey: 'weather_' + city })
    .then(function(data) {
      renderWeather(data.current_weather);
    })
    .catch(function() {
      showToast('Could not load weather', 'error');
    });
}
```

## WebSocket Real-Time Data

```javascript
var ws = connectWebSocket('wss://stream.example.com/prices', {
  onOpen: function() { showToast('Connected', 'success'); },
  onMessage: function(data) { updatePriceDisplay(data); },
  onClose: function() { showToast('Reconnecting...', 'warning'); },
  onError: function() { showToast('Connection error', 'error'); },
});
```

## Periodic Refresh Pattern

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
