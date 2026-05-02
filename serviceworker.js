const VERSION = "v1";

const APP_STATIC_RESOURCES = [
    "/",
    "/index.html",
    "/stylesheet.css",
    "/app.js",
    "/icon-512.png",
  ];
// the cache includes all the NECESSARY files
// the service worker file itself does NOT need ot be cached

self.addEventListener("install", (e) => {
    e.waitUntil(
      (async () => {
        const cache = await caches.open("cacheName_identifier");
        cache.addAll(["/", "/index.html", "/style.css", "/app.js"]);
      })(),
    );
  });

self.addEventListener("install", (event) => {
    event.waitUntil(
      (async () => {
        const cache = await caches.open(CACHE_NAME);
        cache.addAll(APP_STATIC_RESOURCES);
      })(),
    );
  });

  self.addEventListener("activate", (event) => {
    event.waitUntil(
      (async () => {
        const names = await caches.keys();
        await Promise.all(
          names.map((name) => {
            if (name !== CACHE_NAME) {
              return caches.delete(name);
            }
            return undefined;
          }),
        );
        await clients.claim();
      })(),
    );
  });


  self.addEventListener("fetch", (event) => {
    // when seeking an HTML page
    if (event.request.mode === "navigate") {
      // Return to the index.html page
      event.respondWith(caches.match("/"));
      return;
    }

    // For every other request type
    event.respondWith(
      (async () => {
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(event.request.url);
        if (cachedResponse) {
          // Return the cached response if it's available.
          return cachedResponse;
        }
        // Respond with a HTTP 404 response status.
        return new Response(null, { status: 404 });
      })(),
    );
  });


// Does "serviceWorker" exist
if ("serviceWorker" in navigator) {
    // If yes, we register the service worker
  }

  if ("serviceWorker" in navigator) {
    // Register the app's service worker
    // Passing the filename where that worker is defined.
    navigator.serviceWorker.register("sw.js");
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js").then(
      (registration) => {
        console.log("Service worker registration successful:", registration);
      },
      (error) => {
        console.error(`Service worker registration failed: ${error}`);
      },
    );
  } else {
    console.error("Service workers are not supported.");
  }