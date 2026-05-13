'use client'

import { useEffect } from 'react'

export default function ServiceWorkerRegistration() {
    useEffect(() => {
        if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
            navigator.serviceWorker
                .register('/sw.js')
                .then((reg) => {
                    console.log('Service Worker registered:', reg.scope)
                })
                .catch((err) => {
                    console.warn('Service Worker registration failed:', err)
                })
        }
    }, [])

    return null
}
