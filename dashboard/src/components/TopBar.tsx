'use client'

import { useRouter } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import type { ReactNode } from 'react'

interface TopBarProps {
  title: string
  subtitle?: string
  showBack?: boolean
  rightAction?: ReactNode
  children?: ReactNode
}

export default function TopBar({ title, subtitle, showBack, rightAction, children }: TopBarProps) {
  const router = useRouter()

  return (
    <header className="sticky top-0 z-40 border-b border-gray-100/50 bg-white/80 shadow-sm ring-1 ring-gray-900/5 backdrop-blur-xl supports-[backdrop-filter]:bg-white/60">
      <div className="flex items-center justify-between px-4 pb-3 pt-[calc(0.75rem+env(safe-area-inset-top))]">
        <div className="flex items-center gap-3">
          {showBack && (
            <button
              onClick={() => router.back()}
              className="flex h-9 w-9 items-center justify-center rounded-full border border-gray-100 bg-white shadow-sm transition-all hover:bg-gray-50 hover:shadow-md active:scale-95 active:bg-gray-100"
              aria-label="Go back"
            >
              <ArrowLeft className="h-5 w-5 text-gray-700" />
            </button>
          )}
          <div className="min-w-0">
            <h1 className="truncate text-[17px] font-bold tracking-tight text-gray-900">{title}</h1>
            {subtitle && (
              <p className="truncate text-[13px] leading-snug text-gray-500 font-medium">{subtitle}</p>
            )}
          </div>
        </div>
        {rightAction && <div className="ml-2 shrink-0">{rightAction}</div>}
      </div>
      {children && (
        <div className="px-4 pb-3">
          {children}
        </div>
      )}
    </header>
  )
}
