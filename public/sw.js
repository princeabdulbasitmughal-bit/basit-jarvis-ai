/**
 * 👑 BASIT JARVIS AI — SERVICE WORKER (PWA Offline & Asset Caching)
 */

const CACHE_NAME = 'jarvis-pwa-v2.0';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon.svg'
];

// Install Event — Pre-cache core shell
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[JARVIS SW] Pre-caching offline app shell');
      return cache.addAll(STATIC_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// Activate Event — Clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log('[JARVIS SW] Removing old cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event — Network-first for API, Cache-first for static UI
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // If API request or POST request — pass straight to network without caching
  if (url.pathname.startsWith('/api/') || event.request.method !== 'GET') {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(JSON.stringify({
          error: 'Offline Mode Active',
          message: 'Jarvis PC server offline ya unreachable hai.'
        }), {
          headers: { 'Content-Type': 'application/json' }
        });
      })
    );
    return;
  }

  // Static files — Stale-While-Revalidate
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const fetchPromise = fetch(event.request).then(networkResponse => {
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => cachedResponse);

      return cachedResponse || fetchPromise;
    })
  );
});
