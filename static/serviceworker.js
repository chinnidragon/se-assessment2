const CACHE_NAME = "pwa-cache-v2";  // Increment version to force update
const urlsToCache = [
  "/",
  "/homepage.html",
  "/dice.html",
  "/stylesheet.css",
  "/images/millionsslices.png",
  "/images/logobig.png",
  "/images/logosmall.png",
  "/images/question.png",
  "/images/favicon.ico"
];

// Note that this is coded to minimise caching. This decreases performance but makes debugging easier
self.addEventListener("install", event => {
  // Immediately activate the service worker without caching anything
  self.skipWaiting();
  console.log("Service Worker installed. No caching performed.");
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => caches.delete(cache))
      );
    }).then(() => {
      console.log("All caches cleared during activation.");
      return self.clients.claim();
    })
  );
});

// Fetch event - Always bypass cache and fetch from network
self.addEventListener("fetch", event => {
  event.respondWith(
    fetch(event.request).catch(() => {
      // Fallback to index.html for navigation requests if offline
      if (event.request.mode === "navigate") {
        return fetch("/index.html");
      }
    })
  );
});
