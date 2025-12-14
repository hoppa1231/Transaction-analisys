const CACHE_VERSION = 'v2';
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const API_CACHE = `api-${CACHE_VERSION}`;
const OFFLINE_FALLBACK = '/static/offline.html';

const STATIC_ASSETS = [
  '/',
  '/static/offline.html',
  '/static/manifest.json',
  '/static/css/index.css',
  '/static/js/index.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
].map((path) => new URL(path, self.location.origin).toString());

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => ![STATIC_CACHE, API_CACHE].includes(key))
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const requestUrl = new URL(request.url);

  // Network-first for API data
  if (requestUrl.pathname.startsWith('/get/operations')) {
    event.respondWith(networkFirstForApi(request));
    return;
  }

  // Navigation fallback to offline page
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match(OFFLINE_FALLBACK))
    );
    return;
  }

  // Static assets: stale-while-revalidate
  const isStaticAsset =
    STATIC_ASSETS.includes(request.url) ||
    request.destination === 'style' ||
    request.destination === 'script' ||
    request.destination === 'image';

  if (isStaticAsset) {
    event.respondWith(staleWhileRevalidate(request));
  }
});

function networkFirstForApi(request) {
  return fetch(request)
    .then((response) => {
      const clone = response.clone();
      caches.open(API_CACHE).then((cache) => cache.put(request, clone));
      return response;
    })
    .catch(async () => {
      const cache = await caches.open(API_CACHE);
      const cached = await cache.match(request);
      if (cached) return cached;
      return new Response(
        JSON.stringify({ operations: [], total: 0, offline: true }),
        { headers: { 'Content-Type': 'application/json' } }
      );
    });
}

function staleWhileRevalidate(request) {
  return caches.match(request).then((cachedResponse) => {
    const fetchPromise = fetch(request)
      .then((response) => {
        caches.open(STATIC_CACHE).then((cache) =>
          cache.put(request, response.clone())
        );
        return response;
      })
      .catch(() => cachedResponse);

    return cachedResponse || fetchPromise;
  });
}
