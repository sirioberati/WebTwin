---
name: publish-to-vercel
description: >-
  Publish a Meta Display Glasses webapp to Vercel for live HTTPS access on device.
  Use when the developer is ready to publish, host, ship, or release a webapp to a
  stable production URL for everyone. Handles server setup, Vercel project creation,
  and direct deploys without GitHub.
argument-hint: "[app-directory]"
---

# Publish to Vercel

Publish a Meta Display Glasses webapp to Vercel for live HTTPS hosting at a stable production URL. This enables loading the webapp directly on Meta Display Glasses, which require HTTPS URLs.

**Use this skill only when the webapp is ready to ship to everyone.** For iterating on uncommitted changes during development, use `/test-on-device` instead — it deploys to a `stage-<project-name>` URL without affecting production.

**No GitHub repo required** — code is pushed directly from local to Vercel.

## Why Vercel?

Meta Display Glasses load webapps via HTTPS URLs. Vercel provides instant static hosting with HTTPS out of the box, making it the fastest path from local development to on-device access.

## Prerequisites

### 1. Vercel-Compatible Node Server

The app directory must have these three files. If they don't exist, create them before proceeding.

**`package.json`:**

```json
{
  "name": "<app-name>",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "start": "node server.js"
  }
}
```

**`server.js`** — lightweight static file server:

```javascript
var http = require('http');
var fs = require('fs');
var path = require('path');

var PORT = process.env.PORT || 3000;

var mimeTypes = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
};

var server = http.createServer(function(req, res) {
  var filePath = '.' + (req.url === '/' ? '/index.html' : req.url);
  var ext = path.extname(filePath);
  var contentType = mimeTypes[ext] || 'application/octet-stream';

  fs.readFile(filePath, function(err, content) {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end('<h1>404 Not Found</h1>');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content);
  });
});

server.listen(PORT, function() {
  console.log('Server running at http://localhost:' + PORT);
});
```

**`vercel.json`:**

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/$1" }
  ]
}
```

If a server already exists, verify Vercel compatibility:
- Port must use `process.env.PORT || 3000` (not hard-coded)
- `vercel.json` must exist with rewrites config
- Server must only serve static files (no Express routes or SSR)
- `package.json` must have a `start` script

### 2. Existing Webapp

- Existing webapp with `index.html` (created via `/create-webapp` or manually)

## Steps

### 0. Verify Vercel Setup

Run `vercel whoami` to detect the user's current state, then branch:

**a. Authenticated** — `vercel whoami` returns a username. Skip to Step 0.5.

**b. CLI not installed** — command returns `vercel: command not found` (or similar). Tell the user:

> Publishing to Meta Display Glasses needs a public HTTPS URL. I can set this up for you via Vercel — it's free and takes a couple of minutes. You'll need to create a Vercel account at https://vercel.com/signup (free tier is fine), and then I'll handle installing the CLI and walking you through the rest.
>
> If you'd rather host this yourself on any HTTPS server, you can skip this skill entirely.
>
> Want me to proceed with Vercel?

If yes, wait for the user to confirm they've created the Vercel account, then run `npm i -g vercel` yourself. After install completes, proceed to the login branch below.

**c. Not logged in** — CLI is installed but `vercel whoami` returns an auth error. Tell the user:

> Vercel CLI is installed but not logged in. `vercel login` is interactive and needs your input — please type `! vercel login` in this prompt to run it in this session.

After they complete login, re-run `vercel whoami` to confirm. Only proceed once it returns a valid user.

### 0.5. Detect and Offer to Disable Existing Passcode

If `lock.html` exists in the app directory, the app was previously gated by `/test-on-device`'s passcode lock. Production releases shouldn't require visitors to enter a passcode, so ask the user:

> This app has a passcode lock screen from `/test-on-device`. For a public production release, do you want to disable it? (default: yes)
>
> I'll only disable the routing — `lock.html`, `lock.css`, and `lock.js` will stay in the directory in case you re-test later.

If yes, revert only the routing wiring (leave `lock.html`/`lock.css`/`lock.js` files in place):

1. **`server.js`** — change the root path back to serve `index.html`:
   ```javascript
   // Find this:
   var filePath = '.' + (req.url === '/' ? '/lock.html' : req.url);
   // Replace with:
   var filePath = '.' + (req.url === '/' ? '/index.html' : req.url);
   ```
2. **`vercel.json`** — remove the `{ "source": "/", "destination": "/lock.html" }` rewrite. Keep the catch-all.
3. **`index.html`** — remove the inline `localStorage` guard `<script>` from `<head>` (the one that redirects to `lock.html` when the storage key is unset).

If the user says no, leave everything in place — the production URL will continue to gate visitors with the passcode.

If `lock.html` does not exist, skip this step. Do **not** proactively add a passcode lock during publish.

### 1. Ensure No GitHub Repo Is Linked

This workflow pushes code directly from local to Vercel — no GitHub repo needed.

If a Vercel project was previously linked to GitHub, disconnect it:

```bash
vercel git disconnect --yes
```

### 2. Create Vercel Project and Publish

For a first-time publish, run from the app directory:

```bash
vercel --yes --prod
```

This will:
1. Create a new Vercel project (auto-named from directory)
2. Upload all files directly
3. Build and deploy to production
4. Output the live HTTPS URL

The project will be linked locally via a `.vercel/` directory (auto-added to `.gitignore`).

### 3. Disable Deployment Protection

Immediately after the first deploy, disable Vercel Authentication so the glasses browser can access the URL without login:

```bash
PROJECT_ID=$(python3 -c "import json; print(json.load(open('.vercel/project.json'))['projectId'])")
echo '{"ssoProtection":null}' | vercel api "/v9/projects/$PROJECT_ID" -X PATCH --input - --silent
```

> This is safe to run on every deploy — it's a no-op if already disabled.

### 4. Alias to a Stable Production URL

After deploying, alias the deployment to a predictable `<project-name>` URL:

```bash
URL=$(vercel --prod)
vercel alias set "$URL" <project-name>.vercel.app
```

Replace `<project-name>` with the actual project name (from `package.json` or `.vercel/project.json`). For example, if the project is `my-glasses-app`, the stable URL becomes `https://my-glasses-app.vercel.app`.

This is the URL to share with everyone. It never changes between deploys.

### 5. Generate QR Code for Easy Device Setup

Generate a QR code that users can scan from their phone to automatically add the webapp — no manual URL typing needed.

The QR code data must use this deep link format:
```
fb-viewapp://web_app_deep_link?appName=<app-name>&appUrl=<url-encoded-prod-url>
```

For example, if the app is called `my-glasses-app` and the stable URL is `https://my-glasses-app.vercel.app`:
```
fb-viewapp://web_app_deep_link?appName=my-glasses-app&appUrl=https%3A%2F%2Fmy-glasses-app.vercel.app
```

Use the `/qr-code` skill to generate the QR code:

```bash
python3 .claude/skills/qr-code/scripts/qr_generator.py --png <app-dir>/qr-publish.png "fb-viewapp://web_app_deep_link?appName=<app-name>&appUrl=<url-encoded-prod-url>"
```

The PNG is saved to the app directory. If your environment supports rendering images inline (e.g. Claude Code's Read tool), display the QR code directly. Otherwise, provide the file path and tell the user to open it and scan from their phone.

### 6. Give the User the Stable URL and Setup Instructions

After deploy, alias, and QR generation, present the user with:

**Stable URL:**
```
https://<project-name>.vercel.app
```

**Option A — Scan QR code (recommended):**
Scan the generated QR code with your phone camera. It will open the Meta AI app and automatically add the webapp.

**Option B — Manual setup:**
1. Open the **Meta AI app** on your phone
2. Go to **Devices** > **Display Glasses settings**
3. Navigate to **App connections** > **Web apps**
4. Tap **Add a web app**
5. Enter the name: `<app-name>`
6. Enter the URL: `https://<project-name>.vercel.app`

### 7. After Each Update — Republish

After making changes, republish, re-alias, and regenerate the QR code every time:

```bash
URL=$(vercel --prod)
vercel alias set "$URL" <project-name>.vercel.app

# Regenerate QR code
python3 .claude/skills/qr-code/scripts/qr_generator.py --png <app-dir>/qr-publish.png "fb-viewapp://web_app_deep_link?appName=<app-name>&appUrl=<url-encoded-prod-url>"
```

The stable URL automatically serves the latest version. No `git push` needed — Vercel receives the files directly.

After each republish, show the QR code and setup instructions (following Steps 5-6).

> **PS:** If the user has already added this webapp to their glasses, no need to re-add — the stable URL automatically serves the latest deploy.

## Verification

- [ ] Step 0 verified Vercel setup (`vercel whoami` returns a user) before any deploy
- [ ] If `lock.html` existed, user was offered the option to disable the passcode routing for production
- [ ] No new passcode lock was added during publish
- [ ] `package.json`, `server.js`, and `vercel.json` exist in app directory
- [ ] `server.js` uses `process.env.PORT`
- [ ] `vercel --prod` completes successfully
- [ ] `vercel alias set` succeeds and maps to `<project-name>.vercel.app`
- [ ] Stable URL returns the app (check in browser)
- [ ] URL uses HTTPS (required for Meta Display Glasses)
- [ ] App loads correctly on device via the stable URL
- [ ] Subsequent deploys + alias keep the same URL working

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `vercel: command not found` | Run `npm i -g vercel` |
| Auth error | Run `vercel login` |
| GitHub link error on deploy | Run `vercel git disconnect --yes` first |
| 404 on sub-pages | Check `vercel.json` rewrites config |
| Old version still showing | Run `vercel --prod --force` to skip cache, then re-alias |
| Alias name taken | The `<project-name>.vercel.app` subdomain may already be claimed. Try a more specific name like `<project-name>-<team>.vercel.app` |
| Permission denied on `gh` config | Ignore — this workflow doesn't need GitHub |
| QR code won't scan | Ensure the deep link format is correct and the URL is properly percent-encoded. Try increasing `--scale` for a larger QR image |

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/test-on-device` | Preview uncommitted changes on glasses | Quick iteration without committing |
| `/create-webapp` | Create a new webapp | Before first publish |
| `/add-ui` | Add screens, buttons, components | Adding UI before republish |
| `/connect-api` | Add API connections | Adding data sources before republish |
| `/qr-code` | Generate QR codes | Used automatically by this skill for device setup |
| `/passcode-for-testing` | Add passcode lock screen | Not added by this skill — if one already exists from `/test-on-device`, Step 0.5 offers to disable the routing for production |
