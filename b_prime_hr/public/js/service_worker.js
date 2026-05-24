const CACHE_NAME = "employee-offline-hr-v1";
const APP_SHELL = [
    "/offline-hr",
    "/assets/b_prime_hr/css/offline_hr.css",
    "/assets/b_prime_hr/js/offline_hr.js",
    "/assets/b_prime_hr/images/logo.svg",
    "/assets/b_prime_hr/manifest.json"
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)).catch(() => null)
    );
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", event => {
    const req = event.request;

    if (req.method !== "GET") {
        return;
    }

    event.respondWith(
        fetch(req)
            .then(response => {
                const copy = response.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(req, copy)).catch(() => null);
                return response;
            })
            .catch(() => caches.match(req).then(res => res || caches.match("/offline-hr")))
    );
});
