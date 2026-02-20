'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, MessageSquare, TrendingUp, Bell, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

const tabs = [
  { href: '/dashboard', label: 'Home', icon: Home },
  { href: '/dashboard/history', label: 'History', icon: MessageSquare },
  { href: '/dashboard/trends', label: 'Trends', icon: TrendingUp },
  { href: '/dashboard/alerts', label: 'Alerts', icon: Bell },
  { href: '/dashboard/settings', label: 'Settings', icon: Settings },
]

interface NavigationProps {
  unreadAlerts?: number
}

export default function Navigation({ unreadAlerts = 0 }: NavigationProps) {
  const pathname = usePathname()

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 border-t border-white/20 bg-white/75 pb-0 shadow-[0_-8px_30px_-4px_rgba(0,0,0,0.05)] backdrop-blur-lg safe-bottom supports-[backdrop-filter]:bg-white/60"
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="mx-auto flex max-w-md items-center justify-around px-2 py-1.5 sm:max-w-lg md:max-w-2xl">
        {tabs.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || (href !== '/dashboard' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex flex-col items-center gap-1 rounded-2xl px-4 py-2 text-[10px] font-medium transition-all duration-300 ease-out hover:scale-105',
                isActive
                  ? 'bg-clara-50/80 text-clara-700 shadow-sm ring-1 ring-clara-100/50'
                  : 'text-gray-400 hover:text-clara-600 hover:bg-gray-50/50'
              )}
              aria-current={isActive ? 'page' : undefined}
            >
              <span className="relative">
                <Icon
                  className={cn(
                    "h-[22px] w-[22px] transition-transform duration-300",
                    isActive ? "scale-110" : ""
                  )}
                  strokeWidth={isActive ? 2.5 : 2}
                />
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
