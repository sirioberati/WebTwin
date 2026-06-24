---
name: add-device-sensors
description: >-
  Add device sensor data to a Meta Display Glasses webapp — IMU (accelerometer,
  gyroscope, orientation) via DeviceMotionEvent/DeviceOrientationEvent, and GPS
  location via navigator.geolocation. Use when the user wants motion tracking,
  compass, level tool, step counter, shake detection, head tracking, or location.
argument-hint: "[sensor-type: motion|orientation|geolocation]"
---

## Required reading

Before generating or modifying any code, read both:

- `${CLAUDE_PLUGIN_ROOT}/references/display-guidelines.md`
- `${CLAUDE_PLUGIN_ROOT}/references/performance-guidelines.md`

These define the non-negotiable display physics, input model, and performance budgets for Meta Display Glasses webapps. Do not skip — generated UI that ignores these will fail on-device.

# Add Device Sensors to Meta Display Glasses WebApp

Add IMU and GPS sensor integration to an existing webapp using standard Web APIs. No SDK required.

The glasses expose sensor data through two API families:
- **DeviceMotionEvent / DeviceOrientationEvent** — IMU data (accelerometer, gyroscope, compass heading, tilt)
- **navigator.geolocation** — GPS location from the paired companion phone

## Prerequisites

- Existing webapp created via `/create-webapp`

## Available Sensors

### Motion & Orientation (IMU)

The glasses IMU provides high-frequency updates with low latency via two event-based APIs:

**DeviceOrientationEvent** — fires continuously as the glasses rotate:

| Property | Type | Range | Description |
|----------|------|-------|-------------|
| `alpha` | number | 0–360° | Rotation around Z axis (compass heading). 0 = North. |
| `beta` | number | −180° to 180° | Rotation around X axis (front-to-back tilt). |
| `gamma` | number | −90° to 90° | Rotation around Y axis (left-to-right tilt). |
| `absolute` | boolean | — | true if orientation is relative to the Earth's coordinate frame. |

**DeviceMotionEvent** — fires at a regular interval with accelerometer and gyroscope data:

| Property | Unit | Description |
|----------|------|-------------|
| `accelerationIncludingGravity.x/y/z` | m/s² | Linear acceleration including gravitational force. |
| `acceleration.x/y/z` | m/s² | Linear acceleration with gravity removed (may be null). |
| `rotationRate.alpha/beta/gamma` | deg/s | Gyroscope rotation rate around each axis. |
| `interval` | ms | Time interval between events. |

### Geolocation (GPS)

Location is fetched from the paired companion phone — the glasses have no GPS hardware. Permission is granted automatically by the glasses host app.

| Property | Type | Description |
|----------|------|-------------|
| `latitude` | number | Latitude in decimal degrees. |
| `longitude` | number | Longitude in decimal degrees. |
| `accuracy` | number | Accuracy of lat/lon in metres. |
| `altitude` | number \| null | Altitude in metres above sea level. |
| `altitudeAccuracy` | number \| null | Accuracy of altitude in metres. |
| `speed` | number \| null | Speed in m/s. |
| `heading` | number \| null | Direction of travel in degrees from North. |

Accuracy depends on the companion phone's GPS and network fix. Expect 5–50 m typical accuracy. The first call may take several seconds while the phone acquires a fix.

## Steps

### 1. Gather Information

Ask the user:
- **Which sensors?** Motion (accelerometer/gyroscope), orientation (compass/tilt), geolocation (GPS)?
- **What for?** Compass, level tool, step counter, head tracking, spatial AR, location display?
- **Continuous or one-shot?** (for geolocation: `watchPosition` vs `getCurrentPosition`)

### 2. Add Sensor Display UI

Add to the appropriate screen in `index.html`:

```html
<div class="sensor-panel">
  <div class="data-grid">
    <div class="card">
      <div class="card-subtitle">X-Axis</div>
      <div class="card-value" id="sensor-x">0.00</div>
    </div>
    <div class="card">
      <div class="card-subtitle">Y-Axis</div>
      <div class="card-value" id="sensor-y">0.00</div>
    </div>
    <div class="card">
      <div class="card-subtitle">Z-Axis</div>
      <div class="card-value" id="sensor-z">0.00</div>
    </div>
    <div class="card">
      <div class="card-subtitle">Magnitude</div>
      <div class="card-value" id="sensor-mag">0.00</div>
    </div>
  </div>
</div>

<nav class="nav-bar">
  <button class="nav-item focusable primary" data-action="start-sensors">Start</button>
  <button class="nav-item focusable danger" data-action="stop-sensors">Stop</button>
</nav>
```

### 3. Add Motion & Orientation Listeners

In `app.js`, add listener management and action handlers:

```javascript
var motionListening = false;
var orientationListening = false;

function onDeviceMotion(e) {
  // Accelerometer (includes gravity), in m/s²
  var ax = e.accelerationIncludingGravity.x;
  var ay = e.accelerationIncludingGravity.y;
  var az = e.accelerationIncludingGravity.z;

  // Gyroscope rotation rate, in deg/s
  var rotAlpha = e.rotationRate.alpha;
  var rotBeta  = e.rotationRate.beta;
  var rotGamma = e.rotationRate.gamma;

  // Update UI
  document.getElementById('sensor-x').textContent = ax.toFixed(2);
  document.getElementById('sensor-y').textContent = ay.toFixed(2);
  document.getElementById('sensor-z').textContent = az.toFixed(2);
  var mag = Math.sqrt(ax * ax + ay * ay + az * az);
  document.getElementById('sensor-mag').textContent = mag.toFixed(2);
}

function onDeviceOrientation(e) {
  var heading = e.alpha;   // Compass heading 0–360° (0 = North)
  var tilt    = e.beta;    // Front-back tilt −180° to 180°
  var roll    = e.gamma;   // Left-right tilt −90° to 90°

  // Update compass UI
  var headingEl = document.getElementById('compass-heading');
  if (headingEl) headingEl.textContent = Math.round(heading) + '\u00B0';
  var needle = document.getElementById('compass-needle');
  if (needle) needle.style.transform = 'rotate(' + (-heading) + 'deg)';
}

async function startMotionSensors() {
  // Request permission (required on some platforms)
  if (typeof DeviceOrientationEvent.requestPermission === 'function') {
    var state = await DeviceOrientationEvent.requestPermission();
    if (state !== 'granted') {
      showToast('Sensor permission denied', 'error');
      return;
    }
  }

  window.addEventListener('devicemotion', onDeviceMotion);
  motionListening = true;

  window.addEventListener('deviceorientation', onDeviceOrientation);
  orientationListening = true;
}

function stopMotionSensors() {
  if (motionListening) {
    window.removeEventListener('devicemotion', onDeviceMotion);
    motionListening = false;
  }
  if (orientationListening) {
    window.removeEventListener('deviceorientation', onDeviceOrientation);
    orientationListening = false;
  }
}
```

Action handlers in `handleAppAction()`:

```javascript
case 'start-sensors':
  startMotionSensors();
  showToast('Sensors started', 'success');
  break;

case 'stop-sensors':
  stopMotionSensors();
  showToast('Sensors stopped');
  break;
```

### 4. Add Geolocation

**One-shot position** — use a reasonable timeout (10–15 s) to account for phone GPS acquisition:

```javascript
function getLocation(callback) {
  navigator.geolocation.getCurrentPosition(
    function(position) {
      var lat = position.coords.latitude;
      var lon = position.coords.longitude;
      var acc = position.coords.accuracy;
      callback(lat, lon, acc);
    },
    function(error) {
      // error.code: 1 = PERMISSION_DENIED, 2 = POSITION_UNAVAILABLE, 3 = TIMEOUT
      showToast('Location error: ' + error.message, 'error');
    },
    { timeout: 15000 }
  );
}
```

**Continuous updates** — always call `clearWatch` when the app is no longer visible to conserve battery:

```javascript
var watchId = null;

function startLocationWatch(onUpdate) {
  watchId = navigator.geolocation.watchPosition(
    function(position) {
      onUpdate(position.coords.latitude, position.coords.longitude, position.coords.accuracy);
    },
    function(error) {
      showToast('Location error: ' + error.message, 'error');
    }
  );
}

function stopLocationWatch() {
  if (watchId !== null) {
    navigator.geolocation.clearWatch(watchId);
    watchId = null;
  }
}
```

### 5. Clean Up on Screen Exit

Stop all sensors and location watches when leaving the sensor screen. In `navigateTo()`, before switching screens:

```javascript
stopMotionSensors();
stopLocationWatch();
```

## Sensor Patterns

### Compass

Uses `DeviceOrientationEvent.alpha` for heading:

```javascript
window.addEventListener('deviceorientation', function(e) {
  var heading = e.alpha; // 0–360°, 0 = North
  document.getElementById('compass-heading').textContent = Math.round(heading) + '\u00B0';
  document.getElementById('compass-needle').style.transform = 'rotate(' + (-heading) + 'deg)';
});
```

### Level Tool

Uses `DeviceOrientationEvent.beta` and `gamma` for tilt:

```javascript
window.addEventListener('deviceorientation', function(e) {
  var tilt = e.beta;  // front-back
  var roll = e.gamma; // left-right

  // Map tilt to bubble position (max 120px offset)
  var bubbleX = Math.max(-120, Math.min(120, roll * 4));
  var bubbleY = Math.max(-120, Math.min(120, tilt * 4));

  document.getElementById('level-bubble').style.transform =
    'translate(calc(-50% + ' + bubbleX + 'px), calc(-50% + ' + bubbleY + 'px))';

  var angle = Math.sqrt(tilt * tilt + roll * roll);
  document.getElementById('level-reading').textContent = angle.toFixed(1) + '\u00B0';
});
```

### Step Counter

Uses `DeviceMotionEvent.accelerationIncludingGravity` magnitude:

```javascript
var stepCount = 0, lastMagnitude = 0, stepThreshold = 12;

window.addEventListener('devicemotion', function(e) {
  var a = e.accelerationIncludingGravity;
  var mag = Math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z);
  if (lastMagnitude < stepThreshold && mag >= stepThreshold) {
    stepCount++;
    document.getElementById('steps').textContent = stepCount;
  }
  lastMagnitude = mag;
});
```

### Shake Detection

```javascript
var shakeThreshold = 15, lastShakeTime = 0;

window.addEventListener('devicemotion', function(e) {
  var a = e.accelerationIncludingGravity;
  var mag = Math.sqrt(a.x * a.x + a.y * a.y + a.z * a.z);
  if (mag > shakeThreshold && Date.now() - lastShakeTime > 1000) {
    lastShakeTime = Date.now();
    onShake();
  }
});
```

### Tilt Control (for games)

```javascript
window.addEventListener('deviceorientation', function(e) {
  var moveX = Math.max(-1, Math.min(1, e.gamma / 30)); // left-right
  var moveY = Math.max(-1, Math.min(1, e.beta / 30));  // front-back
  updateGamePosition(moveX, moveY);
});
```

### Head Nod / Shake Detection

```javascript
var betaHistory = [], alphaHistory = [];

window.addEventListener('deviceorientation', function(e) {
  betaHistory.push(e.beta);
  alphaHistory.push(e.alpha);
  if (betaHistory.length > 30) betaHistory.shift();
  if (alphaHistory.length > 30) alphaHistory.shift();

  if (betaHistory.length >= 20) {
    var betaRange = Math.max.apply(null, betaHistory) - Math.min.apply(null, betaHistory);
    if (betaRange > 15) onHeadNod();
  }

  if (alphaHistory.length >= 20) {
    var alphaRange = Math.max.apply(null, alphaHistory) - Math.min.apply(null, alphaHistory);
    if (alphaRange > 20) onHeadShake();
  }
});
```

### Spatial App (AR overlay — fuse heading + GPS)

Combine orientation with geolocation to build AR-style spatial overlays:

```javascript
var userLat, userLon;

navigator.geolocation.getCurrentPosition(function(pos) {
  userLat = pos.coords.latitude;
  userLon = pos.coords.longitude;
}, null, { timeout: 15000 });

window.addEventListener('deviceorientation', function(e) {
  var azimuth  = e.alpha; // horizontal direction
  var altitude = e.beta;  // vertical angle (tilt up = positive)
  var roll     = e.gamma;

  var target = findNearestSkyObject(azimuth, altitude, userLat, userLon);
  renderOverlay(target);
});
```

## Specialized UI Templates

### Compass

```html
<div class="compass-container">
  <div class="compass-ring">
    <div class="compass-needle" id="compass-needle"></div>
    <div class="compass-label">N</div>
  </div>
  <div class="compass-heading" id="compass-heading">0&deg;</div>
</div>
```

```css
.compass-container { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 20px; }
.compass-ring { width: 300px; height: 300px; border: 4px solid var(--bg-tertiary); border-radius: 50%; position: relative; display: flex; align-items: center; justify-content: center; }
.compass-needle { width: 4px; height: 120px; background: linear-gradient(to top, var(--danger) 50%, var(--text-primary) 50%); border-radius: 2px; transform-origin: center bottom; position: absolute; bottom: 50%; transition: transform 0.1s ease; }
.compass-label { position: absolute; top: 12px; font-size: 20px; font-weight: 700; color: var(--danger); }
.compass-heading { font-size: 48px; font-weight: 700; color: var(--accent-primary); }
```

### Level Tool

```html
<div class="level-container">
  <div class="level-surface" id="level-surface">
    <div class="level-bubble" id="level-bubble"></div>
    <div class="level-crosshair"></div>
  </div>
  <div class="level-reading" id="level-reading">0.0&deg;</div>
</div>
```

```css
.level-container { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 20px; }
.level-surface { width: 300px; height: 300px; border: 4px solid var(--bg-tertiary); border-radius: 50%; position: relative; overflow: hidden; }
.level-bubble { width: 40px; height: 40px; border-radius: 50%; background: var(--accent-primary); position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); transition: transform 0.1s ease; box-shadow: 0 0 20px var(--focus-glow); }
.level-crosshair { position: absolute; top: 50%; left: 50%; width: 20px; height: 20px; transform: translate(-50%, -50%); border: 2px solid var(--success); border-radius: 50%; }
.level-reading { font-size: 36px; font-weight: 700; color: var(--accent-primary); }
```

## Verify

- [ ] Sensor start/stop buttons work via D-pad + Enter
- [ ] Orientation data updates smoothly (compass heading, tilt)
- [ ] Motion data updates (accelerometer values)
- [ ] Geolocation returns coordinates (may take several seconds on first call)
- [ ] Sensors stop when leaving the screen
- [ ] `clearWatch` is called when location watch is no longer needed

## Related Skills

- `/add-ui` — Add screens, buttons, and other UI components
