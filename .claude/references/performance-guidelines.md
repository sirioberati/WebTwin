# Performance Guidelines — Meta Display Glasses

The glasses run a mobile-grade processor with limited battery. Every web app must be built for constrained hardware.

## Targets

| Metric | Target |
|--------|--------|
| Initial page load | < 3s on 4G |
| JavaScript bundle | < 500KB gzipped |
| Frame rate | 60fps |
| Memory usage | < 128MB |
| Network requests on load | < 10 |

## Code

- Keep JS minimal. No heavy frameworks — vanilla JS or lightweight alternatives.
- Avoid continuous `setInterval`/`requestAnimationFrame` loops. Start them on demand, stop them when not visible.
- Sensor polling: use 10–30 Hz for UI updates. Only use 60+ Hz when motion analysis requires it. Always stop sensors when leaving the screen.
- Batch DOM updates. Avoid layout thrashing (interleaving reads and writes).
- Prefer CSS transitions over JS animations — they run on the GPU and use less CPU/battery.
- Keep animations subtle (150–300ms). Avoid continuous or looping animations that drain battery.

## Assets

- Use Unicode symbols or inline PNGs for icons. No external icon fonts, no SVG icon libraries that require network downloads.
- Inline small assets (< 2KB) as data URIs to reduce network requests.
- No external font downloads. Use the system font stack.

## Offline & Network

Design for intermittent Wi-Fi connectivity.

```javascript
// Service Worker for offline support
const CACHE = 'app-v1';
const URLS = ['/', '/app.js', '/styles.css'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(URLS)));
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request))
  );
});
```

- Cache static assets with a Service Worker.
- Show meaningful UI immediately — don't block render on API calls.
- Handle fetch failures gracefully with cached or fallback content.

## Checklist

- [ ] Viewport is `width=600, height=600` with `overflow: hidden`
- [ ] Page background is `#000000` (transparent on additive display — real world shows through)
- [ ] UI surfaces (cards, headers, nav) use dark grays, not `#000000` (they must remain visible)
- [ ] Light/bright text and UI elements
- [ ] `keydown` listener present, `preventDefault()` on arrow keys and Enter
- [ ] Every screen reachable via D-pad from home
- [ ] Enter activates focused elements
- [ ] No continuous animations running when idle
- [ ] Sensors stopped when leaving their screen
- [ ] Total JS < 500KB gzipped
- [ ] < 10 network requests on initial load
