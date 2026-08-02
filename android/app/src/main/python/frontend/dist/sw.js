/* FinWise service worker — app-shell cache so the installed app opens offline.
   API calls (/api, /health, /exports) are always network-first and never cached. */
const CACHE = 'finwise-shell-v1';
const SHELL = ['/', '/index.html', '/manifest.webmanifest',
  '/favicon.svg', '/pwa-192.png', '/pwa-512.png', '/apple-touch-icon.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const { request } = e;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);

  // Never cache dynamic backend calls.
  if (url.pathname.startsWith('/api') || url.pathname.startsWith('/health') ||
      url.pathname.startsWith('/exports') || url.pathname.startsWith('/docs')) {
    return; // fall through to network
  }

  // Navigation requests: network-first, fall back to cached shell (SPA / offline).
  if (request.mode === 'navigate') {
    e.respondWith(
      fetch(request).catch(() => caches.match('/index.html'))
    );
    return;
  }

  // Static assets: cache-first, then network (and cache it).
  e.respondWith(
    caches.match(request).then((cached) =>
      cached || fetch(request).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(request, copy)).catch(() => {});
        return res;
      }).catch(() => cached)
    )
  );
});
