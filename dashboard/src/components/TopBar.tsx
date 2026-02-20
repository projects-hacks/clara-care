'use client'

import { useRouter } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import type { ReactNode } from 'react'

interface TopBarProps {
  title: string
  subtitle?: string
  showBack?: boolean
  rightAction?: ReactNode
}

export default function TopBar({ title, subtitle, showBack, rightAction }: TopBarProps) {
  const router = useRouter()

  return (
    <header className="sticky top-0 z-40 border-b border-white/20 bg-white/70 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] backdrop-blur-md supports-[backdrop-filter]:bg-white/60">
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
            <h1 className="truncate text-[17px] font-semibold leading-tight text-gray-900">{title}</h1>
            {subtitle && (
              <p className="truncate text-xs leading-snug text-gray-500">{subtitle}</p>
            )}
          </div>
        </div>
        {rightAction && <div className="ml-2 shrink-0">{rightAction}</div>}
      </div>
    </header>
  )
}
