const CACHE_NAME = "pedidos-cache-v1";
const urlsToCache = [
  "/accounts/login/",
  "/home/",
  "/static/css/login.css",
  "/static/css/nav.css",
  "/static/img/favicon.png",
  "/static/img/favicon.png"
];

// Instalar el Service Worker y cachear recursos
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Interceptar solicitudes para servir desde caché
self.addEventListener("fetch", (event) => {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request);
      })
    );
  });
  
  // Activar el Service Worker y limpiar cachés antiguas
  self.addEventListener("activate", (event) => {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cache) => {
            if (cache !== CACHE_NAME) {
              return caches.delete(cache);
            }
          })
        );
      })
    );
  });