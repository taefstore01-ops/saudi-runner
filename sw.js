/* Service worker: lets the game install and run offline.
   Game files are cached on install; CDN libraries and fonts are cached the first time they load.
   The leaderboard (Firestore) always goes to the network. Bump VERSION when shipping new files. */
const VERSION = 'sr-v1';
const CORE = [
  './',
  'index.html',
  'manifest.json',
  'privacy.html',
  'art/regions.js',
  'art/icon-192.png',
  'art/icon-512.png',
  'art/favicon-64.png',
  'js/firebase-config.js',
  'js/leaderboard.js',
  'models/saif.js',
  'models/sadeem.js',
];
const CDN = ['cdnjs.cloudflare.com', 'cdn.jsdelivr.net', 'fonts.googleapis.com', 'fonts.gstatic.com', 'www.gstatic.com'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const sameOrigin = url.origin === self.location.origin;
  if (!sameOrigin && !CDN.includes(url.hostname)) return;     // Firestore, auth, etc.: network only

  if (sameOrigin && req.mode === 'navigate') {
    // the page itself: network first so updates show up, cache when offline
    e.respondWith(fetch(req).then(res => {
      const copy = res.clone();
      caches.open(VERSION).then(c => c.put('index.html', copy));
      return res;
    }).catch(() => caches.match('index.html')));
    return;
  }

  // everything else: cache first, fill the cache from the network
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
    if (res.ok || res.type === 'opaque') {
      const copy = res.clone();
      caches.open(VERSION).then(c => c.put(req, copy));
    }
    return res;
  })));
});
