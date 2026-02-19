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
    <header className="sticky top-0 z-40 border-b border-gray-100 bg-white/85 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-white/75">
      <div className="flex items-center justify-between px-4 pb-3 pt-[calc(0.75rem+env(safe-area-inset-top))]">
        <div className="flex items-center gap-3">
          {showBack && (
            <button
              onClick={() => router.back()}
              className="flex h-9 w-9 items-center justify-center rounded-full border border-gray-100 bg-white shadow-sm transition-colors active:bg-gray-50"
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
