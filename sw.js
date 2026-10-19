/* Hear — service worker.
   The page itself (index.html) is fetched from the network first, so an online phone always runs the current build;
   the cached copy is only used offline. Icons and the manifest are served cache-first. Catalog requests
   (MusicBrainz, Cover Art Archive, Discogs, Claude) never touch the cache.
   Bump VERSION whenever index.html changes (the page's BUILD constant must match). */
const VERSION = 'hear-v24';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-512-maskable.png', './icons/apple-touch-icon.png'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

function withTimeout(promise, ms) {
  return new Promise((resolve, reject) => { const t = setTimeout(() => reject(new Error('timeout')), ms); promise.then((v) => { clearTimeout(t); resolve(v); }, (e) => { clearTimeout(t); reject(e); }); });
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // catalog APIs and images: network only
  const isPage = req.mode === 'navigate' || /\/(index\.html)?$/.test(url.pathname);
  if (isPage) {
    // Network first (revalidated, so GitHub Pages' 10-minute HTTP cache can't hand back an old build), cache as the offline fallback.
    event.respondWith((async () => {
      try {
        const res = await withTimeout(fetch(req.url, { cache: 'no-cache', credentials: 'same-origin' }), 6000);
        if (res && res.ok) { const c = await caches.open(VERSION); c.put(req.url, res.clone()); }
        return res;
      } catch (e) {
        return (await caches.match(req.url)) || (await caches.match('./index.html')) || (await caches.match('./')) || Response.error();
      }
    })());
    return;
  }
  event.respondWith(
    caches.match(req).then((cached) => {
      const fresh = fetch(req).then((res) => { if (res && res.ok) caches.open(VERSION).then((c) => c.put(req, res.clone())); return res; }).catch(() => cached);
      return cached || fresh;
    })
  );
});
