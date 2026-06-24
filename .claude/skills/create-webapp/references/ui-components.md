# UI Component Patterns

Reusable HTML patterns for Meta Display Glasses webapps. All components use the base CSS from `templates/styles.css`.

## Data Card with Live Value

```html
<div class="card focusable" tabindex="0" data-action="view-detail">
  <div class="card-subtitle">Bitcoin</div>
  <div class="card-value" id="btc-price">$--,---</div>
  <div class="card-subtitle">
    <span class="badge badge-success" id="btc-change">+0.0%</span>
  </div>
</div>
```

## List Item with Icon and Badge

```html
<button class="list-item focusable" data-action="select-item" data-id="123">
  <span class="list-item-icon">&#9729;</span>
  <div class="list-item-content">
    <div class="list-item-title">Partly Cloudy</div>
    <div class="list-item-meta">New York, NY</div>
  </div>
  <span class="badge badge-info">72&deg;F</span>
</button>
```

## Inline Loading Skeleton

```html
<div id="content-skeleton" class="loading-container">
  <div class="skeleton skeleton-line medium"></div>
  <div class="skeleton skeleton-line"></div>
  <div class="skeleton skeleton-line short"></div>
</div>
```

## Tab Navigation

```html
<div class="tab-bar">
  <button class="tab-item focusable active" data-action="tab-all">All</button>
  <button class="tab-item focusable" data-action="tab-favorites">Favorites</button>
  <button class="tab-item focusable" data-action="tab-recent">Recent</button>
</div>
```

## Loading + Error States

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

## Key Rules

- All interactive elements must have `class="focusable"`
- Non-button interactive elements need `tabindex="0"`
- Buttons use `data-action="action-name"` for click handling
- Back buttons use `data-action="back"` with `&#8592;` arrow character
- Content must fit within 600×600 viewport
- Scrollable containers need `overflow-y: auto` and `max-height`
