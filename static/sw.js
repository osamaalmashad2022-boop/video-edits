/**
 * Video Trimmer - Progressive Web App Service Worker
 * Handles offline caching and intercepts Android Web Share Target video uploads.
 */

/* global idbStore */
importScripts('/static/idb-store.js');

const CACHE_NAME = 'video-trimmer-cache-v1';

const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/static/idb-store.js',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/icon-maskable-512.png',
  '/static/icons/icon.svg',
  '/static/vendor/ffmpeg/ffmpeg.js',
  '/static/vendor/ffmpeg/util.js',
  '/static/vendor/ffmpeg/814.ffmpeg.js'
];

// Install: Cache core app shell
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      // Cache assets gracefully (don't fail if optional file is unreachable)
      for (const url of STATIC_ASSETS) {
        try {
          await cache.add(url);
        } catch (e) {
          console.warn('[SW] Could not pre-cache:', url, e.message);
        }
      }
    })
  );
});

// Activate: Clean old caches and claim clients immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
      await self.clients.claim();
    })()
  );
});

// Fetch: Intercept Web Share Target POST requests & handle asset caching
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // 1. Intercept Web Share Target POST
  if (event.request.method === 'POST' && url.pathname.includes('/share-target')) {
    event.respondWith(
      (async () => {
        try {
          const formData = await event.request.formData();
          const videoFile = formData.get('video');

          if (videoFile && typeof idbStore !== 'undefined') {
            await idbStore.saveSharedVideo(videoFile, videoFile.name);
          }
        } catch (err) {
          console.error('[SW] Share target processing error:', err);
        }

        // Redirect to root app with ?shared=1 query param
        return Response.redirect('/?shared=1', 303);
      })()
    );
    return;
  }

  // 2. Bypass API requests to server
  if (url.pathname.startsWith('/api/')) {
    return;
  }

  // 3. Stale-while-revalidate / Cache-first for static assets
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Fetch updated version in background
        fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200 && event.request.method === 'GET') {
              caches.open(CACHE_NAME).then((cache) => {
                cache.put(event.request, networkResponse);
              });
            }
          })
          .catch(() => {});
        return cachedResponse;
      }
      return fetch(event.request);
    })
  );
});
