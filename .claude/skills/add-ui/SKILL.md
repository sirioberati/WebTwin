---
name: add-ui
description: >-
  Add UI components to a Meta Display Glasses webapp — screens, buttons,
  lists, cards, forms, toggles, counters, or nav bars. Works with vanilla
  JS and React apps. Use when the user wants to add any interactive UI
  element or new screen.
argument-hint: "[component-type] [name]"
---

## Required reading

Before generating or modifying any code, read both:

- `${CLAUDE_PLUGIN_ROOT}/references/display-guidelines.md`
- `${CLAUDE_PLUGIN_ROOT}/references/performance-guidelines.md`

These define the non-negotiable display physics, input model, and performance budgets for Meta Display Glasses webapps. Do not skip — generated UI that ignores these will fail on-device.

# Add UI Components to Meta Display Glasses WebApp

Add screens, buttons, lists, forms, and other interactive components to an existing webapp. This skill enforces the glasses design constraints and provides implementation patterns.

## Prerequisites

- Existing webapp created via `/create-webapp`

## Design Rules

All components must follow these constraints regardless of framework:

### Viewport & Layout
- **600x600** fixed viewport — all content must fit within this area
- Page background `#000000` (transparent on additive display — real world shows through). UI surfaces (cards, headers, nav) use dark grays so they remain visible. Light text (`#e8e8e8`).
- Use CSS variables from the theme: `--bg-primary`, `--bg-secondary`, `--bg-card`, `--text-primary`, `--text-secondary`, `--accent-primary`, `--danger`, `--success`

### D-pad Navigation
- All interactive elements must be **focusable** — keyboard-navigable via arrow keys
- Enter key activates the focused element
- Escape key navigates back
- Focus moves with **wrap-around** (last → first, first → last)
- Focused elements must scroll into view automatically
- Focus ring: cyan glow (`box-shadow: 0 0 20px rgba(0, 212, 255, 0.4)`)

### Accessibility
- Non-button interactive elements need `tabindex="0"`
- Scrollable containers use `overflow-y: auto` with constrained `max-height`
- Text must be readable on dark background (minimum contrast)

## Available Components

| Component | Purpose | When to Use |
|-----------|---------|-------------|
| Screen | Full-page view with header + content | Adding a new page/destination |
| Button | Triggers an action | Any interactive action |
| Nav Bar | Row of action buttons at bottom | Screen-level actions |
| List | Scrollable list of items | Displaying collections |
| Card | Data display block | Showing stats, values |
| Form | Input fields with submit | Collecting user input |
| Toggle | On/off setting | Boolean settings |
| Counter | +/- with value display | Numeric adjustments |

## Steps

### 1. Gather Information

Ask the user:
- **What component?** Screen, button, list, card, form, toggle, counter?
- **Where?** Which screen should it be added to (or is it a new screen)?
- **Behavior?** What happens on activation/interaction?

### 2. Add the Component

Use [Vanilla JS patterns](references/vanilla-patterns.md) for HTML structure, event handling, and state management. Always apply the design rules above.

### 3. Verify

- [ ] Component is focusable (D-pad navigable)
- [ ] Focus ring appears on the component (cyan glow)
- [ ] Enter key activates the component
- [ ] Escape key navigates back (if applicable)
- [ ] Content fits within 600x600 viewport
- [ ] Text is readable on dark background
- [ ] Scrollable content uses `overflow-y: auto` with `max-height`
- [ ] Focused elements scroll into view

## Related Skills

- `/create-webapp` — Create a new webapp from scratch
- `/connect-api` — Add API-connected actions
- `/add-device-sensors` — Add motion/orientation/GPS sensors
