'use client'

import { useState, useEffect } from 'react'
import { Bell } from 'lucide-react'
import TopBar from '@/components/TopBar'
import LoadingSpinner from '@/components/LoadingSpinner'
import AlertCard from '@/components/AlertCard'
import EmptyState from '@/components/EmptyState'
import { getAlerts, acknowledgeAlert, getPatientId } from '@/lib/api'
import type { Alert } from '@/lib/api'
import { cn } from '@/lib/utils'

const SEVERITY_FILTERS = ['All', 'High', 'Medium', 'Low'] as const

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeFilter, setActiveFilter] = useState<string>('All')
  const [showUnacknowledgedOnly, setShowUnacknowledgedOnly] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const data = await getAlerts(getPatientId())
        setAlerts(data)
      } catch {
        setError('Failed to load alerts')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleAcknowledge = async (id: string) => {
    await acknowledgeAlert(id, 'Family Member')
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id ? { ...a, acknowledged: true, acknowledged_by: 'Family Member' } : a
      )
    )
  }

  const unacknowledgedCount = alerts.filter((a) => !a.acknowledged).length

  const filtered = alerts
    .filter((a) => {
      if (activeFilter !== 'All' && a.severity !== activeFilter.toLowerCase()) return false
      if (showUnacknowledgedOnly && a.acknowledged) return false
      return true
    })

  return (
    <>
      <TopBar
        title="Alerts"
        rightAction={
          unacknowledgedCount > 0 ? (
            <span className="flex h-6 min-w-6 items-center justify-center rounded-full bg-red-500 px-1.5 text-[11px] font-bold text-white">
              {unacknowledgedCount}
            </span>
          ) : undefined
        }
      />

      <div className="px-4 pt-3">
        <div className="mb-3 flex gap-2 overflow-x-auto">
          {SEVERITY_FILTERS.map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={cn(
                'shrink-0 rounded-full px-4 py-1.5 text-xs font-medium transition-colors',
                activeFilter === filter
                  ? 'bg-clara-600 text-white'
                  : 'bg-white text-gray-600 shadow-sm active:bg-gray-50'
              )}
              type="button"
            >
              {filter}
            </button>
          ))}
        </div>

        <label className="flex cursor-pointer items-center gap-2">
          <div className="relative">
            <input
              type="checkbox"
              checked={showUnacknowledgedOnly}
              onChange={(e) => setShowUnacknowledgedOnly(e.target.checked)}
              className="peer sr-only"
            />
            <div className="h-5 w-9 rounded-full bg-gray-200 transition-colors peer-checked:bg-clara-600" />
            <div className="absolute left-0.5 top-0.5 h-4 w-4 rounded-full bg-white transition-transform peer-checked:translate-x-4" />
          </div>
          <span className="text-xs text-gray-600">Unacknowledged only</span>
        </label>
      </div>

      <main className="px-4 py-3">
        {loading && <LoadingSpinner />}

        {error && (
          <div className="py-8 text-center text-sm text-red-500">{error}</div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <EmptyState
            icon={Bell}
            title="No alerts"
            description={
              showUnacknowledgedOnly
                ? 'All alerts have been acknowledged.'
                : 'No alerts match the current filter.'
            }
          />
        )}

        {!loading && !error && filtered.length > 0 && (
          <div className="space-y-2">
            {filtered.map((a) => (
              <AlertCard
                key={a.id}
                alert={a}
                onAcknowledge={handleAcknowledge}
              />
            ))}
          </div>
        )}
      </main>
    </>
  )
}
