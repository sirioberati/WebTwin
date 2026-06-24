# Display Guidelines — Meta Display Glasses

Guidelines for building web apps on the Meta Display Glasses 600x600dp additive waveguide display.

## Rendering APIs

The glasses WebView supports three rendering approaches:

| API | Use case |
|-----|----------|
| DOM (HTML/CSS) | Standard UI — text, layouts, lists, buttons |
| Canvas 2D | Custom drawing — charts, gauges, visualizations |
| WebGL | GPU-accelerated rendering |

## Display Properties

| Property | Value |
|----------|-------|
| Viewport | 600 x 600dp |
| Display type | Additive waveguide — light adds to the real world |
| Black (#000000) | Fully transparent — invisible on display |
| White (#FFFFFF) | Maximum brightness — most visible |
| Refresh rate | 60fps |

## Background Canvas vs. UI Surfaces

On an additive display, `#000000` emits no light and is fully transparent — the real world shows through. This is the **correct** choice for the page background (`body`, `html`), giving the app a see-through canvas.

However, `#000000` must **never** be used on UI surfaces that need to be visible — cards, headers, nav bars, buttons, modals. These require a dark gray (e.g. `#0a0a0f` or `#1C1E21`) so they emit enough light to read as opaque elements on top of the transparent canvas.

| Surface | Color | Why |
|---------|-------|-----|
| Page background (`body`) | `#000000` | Transparent — real world shows through |
| UI surfaces (cards, headers, nav) | `#0a0a0f` – `#1C1E21` | Faintly visible, reads as opaque on the see-through canvas |

```html
<meta name="viewport" content="width=600, height=600, initial-scale=1.0">
<!-- Brief, app-specific description of what the app does -->
<meta name="description" content="...">
<!-- Identifies the page as a Meta Display Glasses (MRBD) compatible webapp -->
<meta name="mrbd-web-app-capable" content="yes">
```

```css
html, body {
  width: 600px;
  height: 600px;
  overflow: hidden;
  background: #000000; /* transparent on additive display — real world shows through */
}
```

## Color & Contrast

- `#FFFFFF` — primary text, icons, UI elements
- `#E4E6EB` — secondary text, subtle labels
- `#B0B3B8` — muted text, disabled states
- `#000000` — page background (transparent on display — real world shows through)
- `#0a0a0f` – `#1C1E21` — UI surface backgrounds (cards, headers, nav — must remain visible)

Minimum contrast ratios: 4.5:1 for body text, 3:1 for large text (WCAG AA). Never use color as the sole indicator of meaning — always pair with an icon, shape, or text label.

Use `mix-blend-mode: plus-lighter` on containers (not content) to create elevation effects.

## Layout & Safe Zone

| Property | Value |
|----------|-------|
| Display canvas | 600 x 600dp |
| Safe margin | 8dp all sides (24dp for full-screen experiences) |
| Safe content area | 584 x 584dp (standard) |
| Header | 24dp from top, 64dp tall |
| Button height | 88dp fixed |

Always apply the 8dp safe margin. Interactive elements at the screen edge get clipped by rubberbanding animations.

```css
.app-root {
  width: 600px;
  height: 600px;
  padding: 8px;
  box-sizing: border-box;
}
```

## Typography

| Element | Size | Weight |
|---------|------|--------|
| Heading 1 | 28dp | Bold |
| Heading 2 | 22dp | Bold |
| Body 1 | 16dp | Regular/Bold |
| Body 2 | 14dp | Regular/Bold |
| Meta 1 | 12dp | Regular |
| Meta 2 | 10dp | Regular |

All text must scale to 200% without breaking layouts. Do not use font sizes below 14dp for interactive elements. Minimum tap target: 88dp height.

## Input Model

The display has no touchscreen, mouse, or keyboard. All input comes through:

- **Captouch (D-pad):** Swipe forward/back on temple. Moves focus between elements.
- **Neural Band (EMG):** Thumb pinch gestures via wrist band. Discrete select/back and continuous movement.
- **No cursor:** Focus jumps between elements — no free-roaming pointer.

Keep navigation shallow — ideally 3 steps or fewer to reach any action.

## Interaction States

Every interactive element must implement three states:

| State | Container | Content Opacity |
|-------|-----------|-----------------|
| Idle | Scale 1x | 80% |
| Targeted (focused) | Scale -8dp | 100% |
| Pressed | Press animation | 100% |

Only the container scales on focus — content stays at 1x to preserve legibility.

```css
.interactive {
  transition:
    transform 475ms cubic-bezier(0.6, 0, 0.4, 1),
    opacity 300ms cubic-bezier(0.4, 0.04, 0.5, 1);
}
.interactive .content { opacity: 0.8; }
.interactive:focus-within { transform: scale(calc(1 - 8/88)); }
.interactive:focus-within .content { opacity: 1.0; }
```

## Animation Curves

| Transition | Duration | Curve |
|------------|----------|-------|
| Focus on | 475ms | `cubic-bezier(0.6, 0, 0.4, 1)` |
| Focus off | 625ms | `cubic-bezier(0.24, 0.24, 0.6, 1)` |
| Color on | 300ms | `cubic-bezier(0.4, 0.04, 0.5, 1)` |
| Color off | 400ms | `cubic-bezier(0.2, 0.24, 0.9, 1)` |
| Press | 100ms | `cubic-bezier(0.68, 0, 0.29, 1)` |

## Scrims

Required on any scrolling container. Gradient overlays at edges signal more content exists.

| Size | Height | Use |
|------|--------|-----|
| SM | 32dp | Short lists |
| MD | 64dp | Standard scrolling |
| LG | 88dp | Long lists |

Scrims span the full display dimension (not just the container).

```css
.scroll-container::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 64px;
  background: linear-gradient(to top, #0a0a0f 0%, transparent 100%);
  pointer-events: none;
  z-index: 10;
}
```

## Navigation Patterns

| Pattern | Use | Key Rules |
|---------|-----|-----------|
| Rail | Primary actions | Horizontal row, 24dp gap |
| List View | Content browsing | Vertical, scrims top/bottom |
| Carousel | Media browsing | Max item width 488dp, 24dp gap, cascading scale |
| Tiles | App grids | Idle 104dp, Targeted 120dp, Pressed 112dp |

Add a progress indicator (dots or numbers) for carousels with more than 3 items.

## Toasts

| Property | Value |
|----------|-------|
| Position | 24dp from top, horizontally centered |
| Max width | 536dp |
| Auto-dismiss | 3.5s + 300ms per word over 2, max 8s |
| Border radius | 24px |

Toasts are for feedback only — not for navigation or persistent content. Use a modal if you need more than 2 lines.

## Containers

| Type | Purpose | Interactive |
|------|---------|-------------|
| Primary | Buttons, list items, tiles | Yes — all 3 states |
| Static | Chips, headers, tooltips, panels | No |
| Card | Media in carousels | Yes — cascading scale |
| Panel | Background overlays | No |

## Icons

Use Unicode symbols or simple inline PNGs. Do not use external icon fonts or SVG icon libraries that require network downloads.

## Accessibility

- Sequential focus order for screen readers
- 4.5:1 contrast for body text, 3:1 for large text
- All text scales to 200% without layout breakage
- Color never used as sole meaning indicator
- Support 1.5x–3x magnification
- Screen reader announces dynamic updates in real time
