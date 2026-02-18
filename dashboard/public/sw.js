// ClaraCare Service Worker
// Provides offline caching for the PWA shell and API responses

const CACHE_NAME = 'claracare-v1'

const PRECACHE_URLS = [
    '/',
    '/alerts',
    '/history',
    '/trends',
    '/settings',
    '/manifest.json',
    '/icon-192.png',
    '/icon-512.png',
]

// Install — precache app shell
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches
            .open(CACHE_NAME)
            .then((cache) => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    )
})

// Activate — clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((names) =>
            Promise.all(
                names
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => caches.delete(name))
            )
        ).then(() => self.clients.claim())
    )
})

// Fetch — network-first for API, cache-first for static assets
self.addEventListener('fetch', (event) => {
    const { request } = event
    const url = new URL(request.url)

    // Skip non-GET requests
    if (request.method !== 'GET') return

    // API requests — network first, cache fallback
    if (url.pathname.startsWith('/api/') || url.hostname === 'api.claracare.me') {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    const clone = response.clone()
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone))
                    return response
                })
                .catch(() => caches.match(request))
        )
        return
    }

    // Static/page requests — cache first, network fallback
    event.respondWith(
        caches.match(request).then((cached) => {
            if (cached) return cached
            return fetch(request).then((response) => {
                // Only cache same-origin requests
                if (url.origin === self.location.origin) {
                    const clone = response.clone()
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone))
                }
                return response
            })
        })
    )
})
