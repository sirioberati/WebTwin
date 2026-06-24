---
name: test-on-device
description: >-
  Deploy uncommitted webapp changes to a public staging URL for live HTTPS testing
  on Meta Display Glasses. Use when the user wants to test, debug, preview, or try
  their webapp on the glasses without committing code. Uses Vercel by default.
argument-hint: "[app-directory]"
---

# Test on Device

Push uncommitted webapp changes to a public staging URL and open it on Meta Display Glasses — without committing code. Defaults to Vercel for hosting; you can also self-host on any HTTPS server and skip this skill.

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

> Testing on Meta Display Glasses needs a public HTTPS URL. I can set this up for you via Vercel — it's free and takes a couple of minutes. You'll need to create a Vercel account at https://vercel.com/signup (free tier is fine), and then I'll handle installing the CLI and walking you through the rest.
>
> If you'd rather host this yourself on any HTTPS server, you can skip this skill entirely.
>
> Want me to proceed with Vercel?

If yes, wait for the user to confirm they've created the Vercel account, then run `npm i -g vercel` yourself. After install completes, proceed to the login branch below.

**c. Not logged in** — CLI is installed but `vercel whoami` returns an auth error. Tell the user:

> Vercel CLI is installed but not logged in. `vercel login` is interactive and needs your input — please type `! vercel login` in this prompt to run it in this session.

After they complete login, re-run `vercel whoami` to confirm. Only proceed once it returns a valid user.

### 0.5. Optional Passcode Lock

The staging URL will be publicly reachable by anyone with the link (Vercel's deployment protection is disabled in Step 1 so the glasses browser can access it).

Check if `lock.html` already exists in the app directory:

- **If `lock.html` exists** — passcode is already in place. Skip to Step 1.
- **If `lock.html` does not exist** — ask the user:

> Want to add a 3-digit lock screen as a soft gate before the app loads? It's not real security — just keeps casual visitors out if someone guesses the URL. (default: no)

If yes, run `/passcode-for-testing`. If no, skip to Step 1.

### 1. Deploy Uncommitted Changes, Disable Auth, and Alias

Deploy with `vercel` (without `--prod`), disable Vercel Authentication via CLI so the glasses browser can access it without login, then alias to a stable URL:

```bash
# Deploy and capture the preview URL
URL=$(vercel --yes)

# Disable Vercel Authentication (glasses browser can't log in)
# Safe to run every time — no-op if already disabled
PROJECT_ID=$(python3 -c "import json; print(json.load(open('.vercel/project.json'))['projectId'])")
echo '{"ssoProtection":null}' | vercel api "/v9/projects/$PROJECT_ID" -X PATCH --input - --silent

# Alias to a stable, predictable URL
vercel alias set "$URL" stage-<project-name>.vercel.app
```

Replace `<project-name>` with the actual project name (from `package.json` or the `.vercel/project.json`). For example, if the project is `my-glasses-app`, the stable URL becomes `https://stage-my-glasses-app.vercel.app`.

Do **not** use `--prod`. Preview deploys keep your production URL unaffected.

### 2. Generate QR Code for Easy Device Setup

Generate a QR code that the user can scan from their phone to automatically add the webapp — no manual URL typing needed.

The QR code data must use this deep link format:
```
fb-viewapp://web_app_deep_link?appName=stage-<app-name>&appUrl=<url-encoded-stage-url>
```

For example, if the app is called `my-glasses-app` and the stable URL is `https://stage-my-glasses-app.vercel.app`:
```
fb-viewapp://web_app_deep_link?appName=stage-my-glasses-app&appUrl=https%3A%2F%2Fstage-my-glasses-app.vercel.app
```

Use the `/qr-code` skill to generate the QR code:

```bash
python3 .claude/skills/qr-code/scripts/qr_generator.py --png <app-dir>/qr-test-on-device.png "fb-viewapp://web_app_deep_link?appName=stage-<app-name>&appUrl=<url-encoded-stage-url>"
```

The PNG is saved to the app directory. If your environment supports rendering images inline (e.g. Claude Code's Read tool), display the QR code directly. Otherwise, provide the file path and tell the user to open it and scan from their phone.

> This QR code only needs to be generated once (on first deploy). The stable URL never changes, so the same QR code works for all future deploys.

### 3. Give the User the Stable URL and Setup Instructions

After deploy, alias, and QR generation, present the user with:

**Stable URL:**
```
https://stage-<project-name>.vercel.app
```

**Option A — Scan QR code (recommended):**
Scan the generated QR code with your phone camera. It will open the Meta AI app and automatically add the webapp.

**Option B — Manual setup:**
1. Open the **Meta AI app** on your phone
2. Go to **Devices** > **Display Glasses settings**
3. Navigate to **App connections** > **Web apps**
4. Tap **Add a web app**
5. Enter the name: `stage-<app-name>`
6. Enter the URL: `https://stage-<project-name>.vercel.app`

Both options only need to be done once — the URL never changes between deploys.

### 4. Iterate

Make changes locally, then deploy, disable auth, re-alias, and regenerate the QR code every time:

```bash
# Edit code...
URL=$(vercel --yes)

# Disable auth (safe to run every time)
PROJECT_ID=$(python3 -c "import json; print(json.load(open('.vercel/project.json'))['projectId'])")
echo '{"ssoProtection":null}' | vercel api "/v9/projects/$PROJECT_ID" -X PATCH --input - --silent

# Re-alias
vercel alias set "$URL" stage-<project-name>.vercel.app

# Regenerate QR code
python3 .claude/skills/qr-code/scripts/qr_generator.py --png <app-dir>/qr-test-on-device.png "fb-viewapp://web_app_deep_link?appName=stage-<app-name>&appUrl=<url-encoded-stage-url>"
```

After each deploy, show the QR code and setup instructions (following Steps 2-3).

> **PS:** If you've already added this webapp to your glasses, no need to re-add — the stable URL automatically serves the latest deploy.

## Verification

- [ ] Step 0 verified Vercel setup (`vercel whoami` returns a user) before any deploy
- [ ] User was offered the passcode lock as opt-in (not auto-added)
- [ ] `package.json`, `server.js`, and `vercel.json` exist in app directory
- [ ] `.vercel/` directory exists in app folder
- [ ] Deployment Protection is disabled (ssoProtection is null)
- [ ] `vercel` (no flags) completes and returns a preview URL
- [ ] `vercel alias set` succeeds and maps to `stage-<project-name>.vercel.app`
- [ ] Stable URL is accessible in an incognito browser (no login prompt)
- [ ] Webapp loads on Meta Display Glasses via the stable URL
- [ ] Subsequent deploys + alias keep the same URL working

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Preview URL shows Vercel login page | Run: `echo '{"ssoProtection":null}' \| vercel api "/v9/projects/$PROJECT_ID" -X PATCH --input - --silent` |
| `vercel: command not found` | Run `npm i -g vercel` |
| No `.vercel/` directory | Run `/publish-to-vercel` first to set up the project |
| Glasses show blank page | Check browser console — likely a JS error. Test URL in desktop browser first |
| Old version showing on glasses | Clear the glasses browser cache or hard-refresh — the stable URL should auto-serve the latest deploy |
| Alias name taken | The `stage-<project-name>.vercel.app` subdomain may already be claimed by another Vercel user. Try a more specific name like `stage-<project-name>-<team>.vercel.app` |
| CORS errors on API calls | APIs must allow cross-origin requests. Use a proxy or CORS-friendly API |
| QR code won't scan | Ensure the deep link format is correct and the URL is properly percent-encoded. Try increasing `--scale` for a larger QR image |

## Related Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/passcode-for-testing` | Add an optional passcode lock screen | Offered as opt-in in Step 0.5 to gate the public staging URL |
| `/publish-to-vercel` | Publish to stable production URL | Shipping a ready version |
| `/create-webapp` | Create a new webapp | Before you have an app to debug |
| `/connect-api` | Add API connections | If debugging API integration issues |
| `/qr-code` | Generate QR codes | Used automatically by this skill for device setup |
