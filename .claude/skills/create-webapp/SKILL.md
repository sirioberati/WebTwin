---
name: create-webapp
description: >-
  Create a new webapp for Meta Display Glasses with D-pad navigation
  and 600x600 dark-theme display. Use when the user wants to build a
  new glasses app, start a project, or scaffold a webapp for smart
  glasses.
argument-hint: "[app-type] [app-name]"
---

## Required reading

Before generating or modifying any code, read both:

- `${CLAUDE_PLUGIN_ROOT}/references/display-guidelines.md`
- `${CLAUDE_PLUGIN_ROOT}/references/performance-guidelines.md`

These define the non-negotiable display physics, input model, and performance budgets for Meta Display Glasses webapps. Do not skip — generated UI that ignores these will fail on-device.

# Create Meta Display Glasses WebApp

Create complete webapps for Meta Display Glasses with EMG wrist-band input, D-pad navigation — including sensor integration and real API connections.

## Input Model

- **D-pad (Up/Down/Left/Right)**: Navigate focusable elements (EMG band or captouch)
- **Enter / Tap**: Select/activate focused element (EMG tap gesture)
- **Back / Escape**: Navigate to previous screen
- **Sensors**: Accelerometer, gyroscope, magnetometer, orientation via W3C Generic Sensor API

No touch input is available. The EMG wrist band translates gestures into D-pad events automatically.

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/add-ui` | Add screens, buttons, UI components | Expanding the app |
| `/connect-api` | Add API connection | Connect to REST/WebSocket APIs |
| `/add-device-sensors` | Add sensor data | Motion/orientation/GPS features |
| `/add-local-storage` | Add data persistence | Save settings, cache, state |

## What Gets Generated

```
<app-name>/
  index.html              # HTML structure with screens
  styles.css              # Dark theme with focus states, loading states, components
  app.js                  # Logic, navigation, D-pad, APIs, SDK integration
  favicon.png             # 128x128 PNG icon themed to the app idea
  manifest.webmanifest    # Web App Manifest referencing the favicon
```

## Workflow

### Step 1: Understand the Request

If the user specified a webapp type, proceed to Step 2.

If not specified, ask what they want to build. Suggest from categories in [references/app-ideas.md](references/app-ideas.md).

### Step 2: Determine Output Location

Ask where to create the webapp, or use defaults:
- `~/meta-display-glasses-webapps/<app-name>/` for new webapps
- Current directory if already in a webapp workspace

```bash
mkdir -p ~/meta-display-glasses-webapps/<app-name>
```

### Step 3: Generate Files

Generate three files using these templates as the foundation:

1. **index.html** — Read [templates/index.html](templates/index.html) for the base HTML structure
2. **styles.css** — Read [templates/styles.css](templates/styles.css) for the complete CSS
3. **app.js** — Read [templates/app.js](templates/app.js) for the complete JS architecture

Key requirements for the HTML:
- Viewport: `width=600, height=600`
- Description: `<meta name="description" content="...">` in the `<head>` with a brief, app-specific summary of what the app does. Replace the template placeholder with real copy.
- MRBD identification: `<meta name="mrbd-web-app-capable" content="yes">` in the `<head>` to positively identify the page as a Meta Display Glasses (MRBD) compatible webapp. Keep `content="yes"` verbatim.
- All interactive elements: `class="focusable"` and `tabindex="0"` if not a button
- Button actions: `data-action="action-name"`
- Back buttons: `data-action="back"` with `&#8592;` arrow character
- Each screen is a `<div class="screen">` with a unique `id`

Customize these sections in `app.js` for each app:
- `CONFIG` — API URLs, storage key, SDK options
- `state.data` — App-specific data shape
- `handleAppAction()` — App-specific action dispatch
- `onScreenEnter()` — Screen-specific data loading/rendering

Add app-specific styles to `styles.css` as needed, building on the template foundations.

### Step 4: Generate the Favicon

Create a `favicon.png` themed to the app idea using the bundled pure-Python script (no dependencies — stdlib only).

**Constraints (do not violate):**
- PNG format. **No SVG** — SVG favicons are not supported.
- Resolution **larger than 52×52**. Default to **128×128**.
- Must be referenced from both `index.html` (`<link rel="icon">`) and the Web App Manifest. The template already wires both.

**How to generate:**

1. Design a small concept that maps to the app idea (e.g. NBA scores → orange basketball with a "B" glyph; weather → sun/cloud; music → note shape). Pick colors that contrast on a dark background.
2. Build a JSON spec using the primitives the script supports: `background` (solid or vertical gradient), optional rounded `plate`, and `layers` of `circle` / `ring` / `rrect` / `polygon` / `points` / `glyph`. See the script header for the full schema.
3. Render the PNG into the app directory:

```bash
python3 <plugin-path>/skills/create-webapp/scripts/favicon_generator.py \
  --spec - --out <app-name>/favicon.png <<'EOF'
{
  "size": 128,
  "background": {"type": "gradient", "from": "#1C1E21", "to": "#0A0B0C"},
  "plate": {"color": "#FF6B35", "radius": 28, "inset": 8},
  "layers": [
    {"type": "ring", "cx": 64, "cy": 64, "r": 38, "width": 4, "color": "#1C1E21"},
    {"type": "glyph", "char": "B", "cx": 64, "cy": 64, "scale": 7, "color": "#1C1E21"}
  ]
}
EOF
```

4. Write `manifest.webmanifest` next to `index.html`:

```json
{
  "name": "<App Name>",
  "short_name": "<App Name>",
  "icons": [
    { "src": "favicon.png", "sizes": "128x128", "type": "image/png" }
  ],
  "background_color": "#000000",
  "theme_color": "#000000",
  "display": "standalone"
}
```

The `<link rel="icon">` and `<link rel="manifest">` references are already present in `templates/index.html` — no HTML edits needed.

### Step 5: For API-Connected Apps

See [references/api-catalog.md](references/api-catalog.md) for free public APIs and integration patterns.

### Step 6: For Sensor Apps

Use `/add-device-sensors` to add motion, orientation, or GPS data to the webapp.

### Step 7: For UI Components

See [references/ui-components.md](references/ui-components.md) for reusable HTML component patterns (cards, lists, tabs, loading states).

### Step 8: Verify

- [ ] All screens have `.screen` class and unique `id`
- [ ] All interactive elements have `.focusable` class
- [ ] Buttons have `data-action` attributes
- [ ] Back buttons use `data-action="back"`
- [ ] Viewport is `width=600, height=600`
- [ ] `<head>` has a `<meta name="description">` tag with an app-specific summary (placeholder replaced)
- [ ] `<head>` has `<meta name="mrbd-web-app-capable" content="yes">`
- [ ] D-pad navigation works (arrow keys move focus with wrap-around)
- [ ] Enter key activates focused elements
- [ ] Escape key navigates back
- [ ] Focus ring is visible (cyan glow) on selected elements
- [ ] Loading states shown during API calls
- [ ] Error states handle API failures gracefully
- [ ] Demo mode works when sensors are unavailable
- [ ] Data persists via localStorage
- [ ] All text is readable on dark background
- [ ] Content fits within 600x600 viewport
- [ ] Scrollable lists use `overflow-y: auto` with `max-height`
- [ ] Focused elements scroll into view automatically
- [ ] `favicon.png` exists at the app root, is >52×52 PNG (not SVG), and is referenced from both `index.html` and `manifest.webmanifest`
- [ ] Agent surfaced the hosting/test next-step prompt (Step 10)

### Step 9: Guide Next Steps

```
Created: ~/meta-display-glasses-webapps/<app-name>/
  index.html              (screens, structure)
  styles.css              (dark theme, focus states, loading/error states)
  app.js                  (D-pad nav, API calls, SDK integration)
  favicon.png             (themed app icon)
  manifest.webmanifest    (web app manifest)

Expand with:
  /add-ui               Add screens, buttons, UI components
  /connect-api          Connect to more APIs
  /add-device-sensors   Add motion/orientation/GPS sensors
  /add-local-storage    Add data persistence

Test locally by opening index.html in a browser and using arrow keys + Enter.
```

### Step 10: Offer a Hosting Path

After expansion options, ask the user how they want to run the app on Meta Display Glasses. The glasses load webapps via HTTPS, so the app needs to be hosted on a public URL.

Prompt the user with:

> Your webapp is ready and works locally. To run it on Meta Display Glasses, it needs to be hosted on a public HTTPS URL. Two options:
>
> - **`/test-on-device`** — deploy to a public staging URL (e.g. `stage-<app>.vercel.app`) for iterating
> - **`/publish-to-vercel`** — publish to a stable production URL (e.g. `<app>.vercel.app`)
>
> Both use Vercel (free tier works) and I can set the whole thing up for you. If you'd rather host the app yourself elsewhere, you can skip both — anywhere that serves HTTPS will work.

Do not auto-invoke either skill. Wait for the user's choice.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Webapp doesn't load on device | Check browser console for JS errors |
| Focus ring not visible | Verify `.focusable` class on interactive elements |
| D-pad not navigating | Check `moveFocus()` handles the current screen |
| Enter not activating | Verify `data-action` attribute on element |
| Back button not working | Check `data-action="back"` or Escape handler |
| API calls failing | Check CORS headers, use proxy if needed |
| API data not updating | Clear cache: `state.cache = {}` |
| Sensor data not flowing | Check sensor types are valid, verify device support |
| Data not persisting | Verify `saveData()` called after state changes |
| Screen not showing | Check `hidden` class and `navigateTo()` call |
| Demo mode not working | Verify fallback code in sensor helpers |

Use browser developer tools to view console.log output for debugging.
