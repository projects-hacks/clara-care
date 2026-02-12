'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, MessageSquare, TrendingUp, Bell, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

const tabs = [
  { href: '/', label: 'Home', icon: Home },
  { href: '/history', label: 'History', icon: MessageSquare },
  { href: '/trends', label: 'Trends', icon: TrendingUp },
  { href: '/alerts', label: 'Alerts', icon: Bell },
  { href: '/settings', label: 'Settings', icon: Settings },
]

interface NavigationProps {
  unreadAlerts?: number
}

export default function Navigation({ unreadAlerts = 0 }: NavigationProps) {
  const pathname = usePathname()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-gray-200 bg-white safe-bottom">
      <div className="mx-auto flex max-w-lg items-center justify-around px-2 py-1">
        {tabs.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || (href !== '/' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex flex-col items-center gap-0.5 px-3 py-2 text-[10px] font-medium transition-colors',
                isActive ? 'text-clara-600' : 'text-gray-400'
              )}
              aria-current={isActive ? 'page' : undefined}
            >
              <span className="relative">
                <Icon className="h-5 w-5" strokeWidth={isActive ? 2.5 : 2} />
                {label === 'Alerts' && unreadAlerts > 0 && (
                  <span className="absolute -right-2 -top-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[9px] font-bold text-white">
                    {unreadAlerts > 9 ? '9+' : unreadAlerts}
                  </span>
                )}
              </span>
              <span>{label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
