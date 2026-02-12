'use client'

import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
  /** 'line' | 'circle' | 'rect' - line = narrow bar, circle = round, rect = block */
  variant?: 'line' | 'circle' | 'rect'
}

export default function Skeleton({ className, variant = 'line' }: SkeletonProps) {
  return (
    <div
      role="status"
      aria-busy
      aria-label="Loading"
      className={cn(
        'animate-pulse rounded bg-gray-200 motion-reduce:animate-none',
        variant === 'line' && 'h-4',
        variant === 'circle' && 'rounded-full aspect-square',
        variant === 'rect' && 'min-h-[4rem]',
        className
      )}
    />
  )
}

export function SkeletonLine({ className }: { className?: string }) {
  return <Skeleton variant="line" className={className} />
}

export function SkeletonCircle({ className }: { className?: string }) {
  return <Skeleton variant="circle" className={className} />
}

export function SkeletonRect({ className }: { className?: string }) {
  return <Skeleton variant="rect" className={className} />
}
