'use client'

import { useState, useMemo } from 'react'
import { Search, MapPin } from 'lucide-react'
import { getAllTimezones, getCommonTimezones, detectUserTimezone } from '@/lib/timezones'
import type { TimezoneOption } from '@/lib/timezones'

interface TimezoneSelectProps {
  value: string
  onChange: (value: string) => void
  className?: string
}

export default function TimezoneSelect({ value, onChange, className = '' }: TimezoneSelectProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [showDropdown, setShowDropdown] = useState(false)
  
  const allTimezones = useMemo(() => getAllTimezones(), [])
  const commonTimezones = useMemo(() => getCommonTimezones(), [])
  
  // Filter timezones based on search
  const filteredTimezones = useMemo(() => {
    if (!searchQuery.trim()) return allTimezones
    
    const query = searchQuery.toLowerCase()
    return allTimezones.filter(tz => 
      tz.label.toLowerCase().includes(query) ||
      tz.value.toLowerCase().includes(query) ||
      tz.region.toLowerCase().includes(query)
    )
  }, [searchQuery, allTimezones])
  
  // Get current timezone display
  const currentTz = allTimezones.find(tz => tz.value === value)
  const displayValue = currentTz ? `${currentTz.label}` : value
  
  // Auto-detect button handler
  const handleAutoDetect = () => {
    const detected = detectUserTimezone()
    onChange(detected)
    setShowDropdown(false)
  }
  
  // Group timezones by region for display
  const groupedTimezones = useMemo(() => {
    const grouped: Record<string, TimezoneOption[]> = {}
    for (const tz of filteredTimezones) {
      if (!grouped[tz.region]) {
        grouped[tz.region] = []
      }
      grouped[tz.region].push(tz)
    }
    return grouped
  }, [filteredTimezones])
  
  const regionOrder = ['America', 'Europe', 'Asia', 'Pacific', 'Africa', 'Atlantic', 'Indian', 'Antarctica']
  const sortedRegions = Object.keys(groupedTimezones).sort((a, b) => {
    const aIndex = regionOrder.indexOf(a)
    const bIndex = regionOrder.indexOf(b)
    if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex
    if (aIndex !== -1) return -1
    if (bIndex !== -1) return 1
    return a.localeCompare(b)
  })

  return (
    <div className="relative">
      {/* Current Selection Display */}
      <button
        type="button"
        onClick={() => setShowDropdown(!showDropdown)}
        className={`min-h-[44px] w-full rounded-lg border border-gray-200 px-3 py-2 text-left text-body focus:border-clara-500 focus:outline-none focus:ring-2 focus:ring-clara-500 focus:ring-offset-0 ${className}`}
      >
        <div className="flex items-center justify-between">
          <span className="truncate">{displayValue}</span>
          <svg
            className={`ml-2 h-5 w-5 text-gray-400 transition-transform ${showDropdown ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Dropdown Panel */}
      {showDropdown && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setShowDropdown(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute left-0 right-0 top-full z-20 mt-2 max-h-96 overflow-hidden rounded-lg border border-gray-200 bg-white shadow-lg">
            {/* Search Bar */}
            <div className="border-b border-gray-100 p-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search timezones..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-md border border-gray-200 py-2 pl-10 pr-3 text-sm focus:border-clara-500 focus:outline-none focus:ring-1 focus:ring-clara-500"
                  autoFocus
                />
              </div>
              
              {/* Auto-detect button */}
              <button
                type="button"
                onClick={handleAutoDetect}
                className="mt-2 flex w-full items-center justify-center gap-2 rounded-md bg-clara-50 px-3 py-2 text-sm font-medium text-clara-700 hover:bg-clara-100"
              >
                <MapPin className="h-4 w-4" />
                Auto-detect my timezone
              </button>
            </div>

            {/* Common Timezones */}
            {!searchQuery && (
              <div className="border-b border-gray-100 bg-gray-50 px-3 py-2">
                <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Common Timezones
                </div>
                <div className="space-y-0.5">
                  {commonTimezones.map((tz) => (
                    <button
                      key={tz.value}
                      type="button"
                      onClick={() => {
                        onChange(tz.value)
                        setShowDropdown(false)
                        setSearchQuery('')
                      }}
                      className={`w-full rounded px-2 py-1.5 text-left text-sm hover:bg-white ${
                        value === tz.value ? 'bg-clara-100 font-medium text-clara-700' : 'text-gray-700'
                      }`}
                    >
                      {tz.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* All Timezones by Region */}
            <div className="max-h-64 overflow-y-auto p-2">
              {sortedRegions.length === 0 ? (
                <div className="py-8 text-center text-sm text-gray-500">
                  No timezones found matching &quot;{searchQuery}&quot;
                </div>
              ) : (
                sortedRegions.map((region) => (
                  <div key={region} className="mb-3">
                    <div className="mb-1 px-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                      {region}
                    </div>
                    <div className="space-y-0.5">
                      {groupedTimezones[region].map((tz) => (
                        <button
                          key={tz.value}
                          type="button"
                          onClick={() => {
                            onChange(tz.value)
                            setShowDropdown(false)
                            setSearchQuery('')
                          }}
                          className={`w-full rounded px-2 py-1.5 text-left text-sm hover:bg-gray-50 ${
                            value === tz.value ? 'bg-clara-100 font-medium text-clara-700' : 'text-gray-700'
                          }`}
                        >
                          {tz.label}
                        </button>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
