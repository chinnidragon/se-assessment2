// Adapted from Mr Horan's Tutorial 

//manually updatinng cache forces app to update
const CACHE_NAME = "pwa-cache-v4";

//all static images (so that the website can still work offline)
const urlsToCache = [
  "/",
  "/static/stylesheet.css",
  "/static/favicon.ico",
  "/static/images/logobig.png",
  "/static/images/logosmall.png",
  "/static/images/question.png",
  "/static/images/nav/bell.png",
  "/static/images/nav/char.png",
  "/static/images/nav/note.png",
  "/static/images/nav/profile.png",
  "/static/images/nav/time.png",
  "/static/images/dice/4.png",
  "/static/images/dice/6.png",
  "/static/images/dice/8.png",
  "/static/images/dice/10.png",
  "/static/images/dice/12.png",
  "/static/images/dice/20.png"
];


self.addEventListener("install", (event) => {
  //keeps running until install has finished
  event.waitUntil(
    //Caching on installation
    caches.open(CACHE_NAME).then((cache) => {
      console.log("caching assets");
      //downloading ALL cached assets
      return cache.addAll(urlsToCache);
      //manually forces old service workers to stop running, so that it updates without users clsoing tabs
    }).then(() => self.skipWaiting())
  );
});


self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        //inspects all existing caches
        cacheNames.map((cache) => {
          //deletes old caches (that dont match the current cache's name) -- saves storage!
          if (cache !== CACHE_NAME) {
            console.log("PWA: Clearing outdated cache:", cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

//fires everytime webpage loads anything
self.addEventListener("fetch", (event) => {
  // only intercepts get requests
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse; // serves directly from local storage offline (PWA special!!)
      }
      // if not in cache, request it via the live internet connection
      return fetch(event.request).catch(() => {
        // fallback catch block if no network + not in cache
        if (event.request.mode === "navigate") {
          return caches.match("/");
        }
      });
    })
  );
});
