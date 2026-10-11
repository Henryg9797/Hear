/* Hear — service worker. Caches the app shell so the icon on your home screen opens instantly.
   Catalog requests (MusicBrainz, Cover Art Archive, Discogs, Claude) always go to the network.
   Bump VERSION whenever index.html changes so phones pick up the new build. */
const VERSION = 'hear-v10';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-512-maskable.png', './icons/apple-touch-icon.png'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // catalog APIs and images: network only
  event.respondWith(
    caches.match(req).then((cached) => {
      const fresh = fetch(req).then((res) => { if (res && res.ok) caches.open(VERSION).then((c) => c.put(req, res.clone())); return res; }).catch(() => cached);
      return cached || fresh;
    })
  );
});
