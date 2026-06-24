# Vanilla JS Patterns

Implementation patterns for vanilla JS webapps created via `/create-webapp`.

## Screens

### Base Screen

```html
<div id="screen-name" class="screen hidden">
  <header class="header">
    <button class="back-btn focusable" data-action="back">&#8592;</button>
    <h1>Screen Title</h1>
  </header>
  <div class="content">
    <!-- Screen content here -->
  </div>
</div>
```

Action handler in `app.js`:

```javascript
case 'go-screen-name':
  navigateTo('screen-name');
  break;
```

The `collectScreens()` function automatically finds all elements with `.screen` class and an `id` — no additional registration needed.

### List Screen

```html
<div id="list-screen" class="screen hidden">
  <header class="header">
    <button class="back-btn focusable" data-action="back">&#8592;</button>
    <h1>Items</h1>
  </header>
  <div class="content">
    <div id="item-list" class="list-container">
      <!-- Items rendered dynamically -->
    </div>
  </div>
</div>
```

### Detail Screen

```html
<div id="detail-screen" class="screen hidden">
  <header class="header">
    <button class="back-btn focusable" data-action="back">&#8592;</button>
    <h1 id="detail-title">Detail</h1>
  </header>
  <div class="content">
    <div id="detail-content"></div>
    <nav class="nav-bar">
      <button class="nav-item focusable" data-action="edit">Edit</button>
      <button class="nav-item focusable danger" data-action="delete">Delete</button>
    </nav>
  </div>
</div>
```

### Form Screen

```html
<div id="form-screen" class="screen hidden">
  <header class="header">
    <button class="back-btn focusable" data-action="back">&#8592;</button>
    <h1>Add Item</h1>
  </header>
  <div class="content">
    <div class="form-field">
      <label>Name</label>
      <input type="text" id="input-name" class="text-input focusable" placeholder="Enter name">
    </div>
    <button class="nav-item focusable primary" data-action="save">Save</button>
  </div>
</div>
```

```css
.form-field { margin-bottom: 16px; }
.form-field label { display: block; margin-bottom: 8px; color: var(--text-secondary); }
```

## Buttons

All buttons use `data-action` attributes and are handled in `handleAppAction()`:

```javascript
case 'action-name':
  // Action behavior here
  break;
```

### Navigation Button

```html
<button class="nav-item focusable" data-action="go-settings">Settings &#8594;</button>
```

```javascript
case 'go-settings':
  navigateTo('settings');
  break;
```

### Primary / Confirm Button

```html
<button class="nav-item focusable primary" data-action="confirm">Confirm</button>
```

### Danger / Delete Button

```html
<button class="nav-item focusable danger" data-action="delete-item">Delete Item</button>
```

```javascript
case 'delete-item':
  var itemId = element.dataset.id;
  state.data.items = state.data.items.filter(function(i) { return i.id !== itemId; });
  saveData();
  navigateBack();
  break;
```

### Toggle Button

```html
<button class="nav-item focusable" data-action="toggle-sound">
  <span class="setting-label">Sound</span>
  <span class="setting-value" id="sound-value">On</span>
</button>
```

```javascript
case 'toggle-sound':
  state.data.soundEnabled = !state.data.soundEnabled;
  document.getElementById('sound-value').textContent = state.data.soundEnabled ? 'On' : 'Off';
  saveData();
  break;
```

### Increment / Decrement (Counter)

```html
<div class="counter-controls">
  <button class="control-btn focusable" data-action="decrement">&#8722;</button>
  <span id="counter-value">0</span>
  <button class="control-btn focusable" data-action="increment">+</button>
</div>
```

```javascript
case 'increment':
  state.data.count++;
  document.getElementById('counter-value').textContent = state.data.count;
  saveData();
  break;

case 'decrement':
  if (state.data.count > 0) {
    state.data.count--;
    document.getElementById('counter-value').textContent = state.data.count;
    saveData();
  }
  break;
```

```css
.counter-controls { display: flex; align-items: center; justify-content: center; gap: 24px; }
.control-btn { width: 60px; height: 60px; border-radius: 50%; background: var(--bg-secondary); color: var(--text-primary); font-size: 32px; display: flex; align-items: center; justify-content: center; }
```

### Button with Data Attributes

When an action needs data from the element:

```html
<button class="list-item focusable" data-action="select-item" data-id="123">Item Name</button>
```

```javascript
case 'select-item':
  var itemId = element.dataset.id;
  state.data.selectedItem = state.data.items.find(function(i) { return i.id === itemId; });
  navigateTo('detail');
  break;
```

## Nav Bar

A row of action buttons at the bottom of a screen:

```html
<nav class="nav-bar">
  <button class="nav-item focusable primary" data-action="save">Save</button>
  <button class="nav-item focusable danger" data-action="cancel">Cancel</button>
</nav>
```

## Screen Cleanup

Stop any active resources (timers, sensors, connections) when leaving a screen. In `navigateTo()`, before switching screens:

```javascript
// Example: stop a timer when leaving
if (myTimer) {
  clearInterval(myTimer);
  myTimer = null;
}
```
