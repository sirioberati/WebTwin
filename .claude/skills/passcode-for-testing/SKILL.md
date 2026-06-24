---
name: passcode-for-testing
description: >-
  Add a 3-digit combination lock passcode screen to a Meta Display Glasses webapp
  to gate public access during testing. Offered as an opt-in step within
  /test-on-device since Vercel deployment protection is disabled for glasses
  browser compatibility.
argument-hint: "[app-directory]"
---

# Passcode for Testing

Add a combination lock screen that gates access to your webapp during Vercel preview deployments. Since `/test-on-device` disables Vercel's deployment protection, this prevents the public from accessing your app.

This skill is offered as an opt-in by `/test-on-device` (Step 0.5) — it is not auto-invoked. `/publish-to-vercel` will not add a passcode, and if one already exists it will offer to disable the routing for production (the lock files stay on disk).

## Prerequisites

- Existing webapp with `index.html` (created via `/create-webapp` or manually)
- The app directory must have `server.js` and `vercel.json` (created by `/create-webapp` or `/test-on-device`)

## Steps

### 1. Gather Information

Ask the user:
- **Passcode** — 3 digits, each 0-9 (e.g. 2-4-7)

### 2. Create `lock.html`

Read [templates/lock.html](templates/lock.html) and write it to the app directory.

Replace the two placeholder values in the `<script>` block:
- `__DIGIT_0__`, `__DIGIT_1__`, `__DIGIT_2__` — the user's chosen passcode digits (as integers)
- `__APP_NAME__` in the `STORAGE_KEY` — the project name from `package.json` with hyphens replaced by underscores (e.g. `ipl-live-scores` → `ipl_live_scores`)

### 3. Update Routing

**`server.js`** — change the root path to serve `lock.html`:

```javascript
// Find this:
var filePath = '.' + (req.url === '/' ? '/index.html' : req.url);
// Replace with:
var filePath = '.' + (req.url === '/' ? '/lock.html' : req.url);
```

**`vercel.json`** — add a rewrite rule before the catch-all:

```json
{
  "rewrites": [
    { "source": "/", "destination": "/lock.html" },
    { "source": "/(.*)", "destination": "/$1" }
  ]
}
```

### 4. Add Guard to `index.html`

Add this inline script in `<head>`, after `<meta>` tags and before any `<link>` or `<script>` tags:

```html
<script>if(localStorage.getItem('<STORAGE_KEY>')!=='1')window.location.replace('lock.html');</script>
```

Replace `<STORAGE_KEY>` with the same key used in `lock.html` (e.g. `ipl_live_scores_unlocked`).

This prevents bypassing the lock by navigating directly to `index.html`.

## Verify

- [ ] `lock.html` exists in the app directory
- [ ] Passcode digits and `STORAGE_KEY` are set correctly in `lock.html`
- [ ] `server.js` serves `lock.html` on root path `/`
- [ ] `vercel.json` has the `/` → `/lock.html` rewrite before the catch-all
- [ ] `index.html` has the localStorage guard script in `<head>`
- [ ] Correct passcode shows green digits, "Unlocked" animation, and redirects
- [ ] After unlock, refreshes and new tabs skip the lock (localStorage persists)
- [ ] Direct navigation to `/index.html` redirects back to lock if not unlocked

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Lock screen doesn't appear | Check `server.js` serves `lock.html` on `/` and `vercel.json` has the rewrite |
| Can bypass lock via `/index.html` | Ensure the localStorage guard script is in `index.html` `<head>` |
| Wrong passcode unlocks | Verify `PASSCODE` array in `lock.html` matches the user's chosen digits |
| Unlock doesn't redirect | Ensure `STORAGE_KEY` is consistent between `lock.html` and `index.html` guard |

## Related Skills

- `/test-on-device` — Offers this skill as an opt-in (Step 0.5) before deploying
- `/create-webapp` — Create a new webapp before adding passcode protection
- `/publish-to-vercel` — Will not add a passcode; if one already exists, offers to disable the routing for production while leaving the lock files on disk
