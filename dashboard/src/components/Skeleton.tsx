'use client'

import { Phone, PhoneOff } from 'lucide-react'
import { cn } from '@/lib/utils'

export function SkeletonLine({ className }: { className?: string }) {
  return <div className={cn("h-3 animate-pulse rounded bg-gray-200", className)} />
}

export function LiveCallStatusSkeleton() {
  return (
    <div className="flex items-center gap-2 rounded-xl bg-white px-4 py-3 shadow-sm ring-1 ring-gray-900/5">
      <div className="h-2 w-2 animate-pulse rounded-full bg-gray-200" />
      <div className="h-3 w-24 animate-pulse rounded bg-gray-200" />
    </div>
  )
}

export function CognitiveTrendCardSkeleton({ compact = false }: { compact?: boolean }) {
  if (compact) {
    return (
      <div className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-gray-900/5">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-2.5 w-20 animate-pulse rounded bg-gray-200" />
            <div className="h-6 w-16 animate-pulse rounded bg-gray-200" />
          </div>
          <div className="h-12 w-24 animate-pulse rounded bg-gray-100" />
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
      <div className="mb-4 flex items-start justify-between">
        <div className="space-y-2">
          <div className="h-2.5 w-28 animate-pulse rounded bg-gray-200" />
          <div className="h-4 w-20 animate-pulse rounded bg-gray-200" />
        </div>
        <div className="h-7 w-20 animate-pulse rounded-full bg-gray-200" />
      </div>
      <div className="h-40 animate-pulse rounded-lg bg-gray-100" />
      <div className="mt-4 h-10 animate-pulse rounded-xl bg-gray-100" />
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-6 px-4 py-4">
      {/* Top bar skeleton */}
      <div className="h-16 animate-pulse rounded-3xl bg-gray-200" />
      
      {/* Call button skeleton */}
      <div className="h-14 animate-pulse rounded-2xl bg-gray-200" />
      
      {/* Wellness summary skeleton */}
      <div className="h-48 animate-pulse rounded-3xl bg-gray-200" />
      
      {/* Quick stats skeleton */}
      <div className="grid grid-cols-3 gap-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 animate-pulse rounded-xl bg-gray-200" />
        ))}
      </div>
      
      {/* Cognitive trend card skeleton */}
      <CognitiveTrendCardSkeleton />
      
      {/* Recent conversations skeleton */}
      <div className="space-y-2">
        <div className="h-5 w-32 animate-pulse rounded bg-gray-200" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-20 animate-pulse rounded-xl bg-gray-200" />
        ))}
      </div>
    </div>
  )
}
