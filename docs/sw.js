// sw.js -- service worker
// It intercepts the two hardcoded URLs from tikzjax.com and responds from your self-hosted copies
const CACHE = 'tikzjax-v1';

// Map upstream URLs → your self-hosted paths
const REMAP = {
  'https://s3.us-east-2.amazonaws.com/tikzjax.com/3f69afb974a1e83f66a36f7618f88a38c254034b.wasm':
      '/tikzjax-assets/tex.wasm.gz',
  'https://s3.us-east-2.amazonaws.com/tikzjax.com/b565ab0b474e8e557d954694b7379a57db669ac9.gz':
      '/tikzjax-assets/core.dump.gz',
};

const PRECACHE = [
  '/tikzjax-assets/tikzjax.js',
  '/tikzjax-assets/fonts.css',
  '/tikzjax-assets/tex.wasm.gz',
  '/tikzjax-assets/core.dump.gz',
];

// On install, cache everything immediately
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  const url = event.request.url;

  // Remap tikzjax.com fetches → local assets
  if (REMAP[url]) {
    event.respondWith(
      caches.open(CACHE).then(cache =>
        cache.match(REMAP[url]).then(cached =>
          cached || fetch(REMAP[url]).then(resp => {
            cache.put(REMAP[url], resp.clone());
            return resp;
          })
        )
      )
    );
    return;
  }

  // Cache-first for all self-hosted tikzjax assets
  if (url.includes('/tikzjax-assets/')) {
    event.respondWith(
      caches.open(CACHE).then(cache =>
        cache.match(event.request).then(cached =>
          cached || fetch(event.request).then(resp => {
            cache.put(event.request, resp.clone());
            return resp;
          })
        )
      )
    );
  }
});