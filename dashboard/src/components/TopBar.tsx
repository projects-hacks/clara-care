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
    <header className="sticky top-0 z-40 border-b border-gray-100 bg-white shadow-sm">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          {showBack && (
            <button
              onClick={() => router.back()}
              className="flex h-8 w-8 items-center justify-center rounded-full transition-colors active:bg-gray-100"
              aria-label="Go back"
            >
              <ArrowLeft className="h-5 w-5 text-gray-700" />
            </button>
          )}
          <div className="min-w-0">
            <h1 className="truncate text-lg font-semibold text-gray-900">{title}</h1>
            {subtitle && (
              <p className="truncate text-xs text-gray-500">{subtitle}</p>
            )}
          </div>
        </div>
        {rightAction && <div className="ml-2 shrink-0">{rightAction}</div>}
      </div>
    </header>
  )
}
