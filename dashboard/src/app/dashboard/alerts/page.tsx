'use client'

import { useState, useEffect } from 'react'
import { Bell } from 'lucide-react'
import TopBar from '@/components/TopBar'
import LoadingSpinner from '@/components/LoadingSpinner'
import AlertCard from '@/components/AlertCard'
import EmptyState from '@/components/EmptyState'
import { getAlerts, getPatient, acknowledgeAlert, getPatientId } from '@/lib/api'
import type { Alert } from '@/lib/api'
import { cn } from '@/lib/utils'

const SEVERITY_FILTERS = ['All', 'High', 'Medium', 'Low'] as const

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeFilter, setActiveFilter] = useState<string>('All')
  const [patient, setPatient] = useState<{ family_contacts?: { id: string, name: string }[] } | null>(null)
  const [showUnacknowledgedOnly, setShowUnacknowledgedOnly] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const pid = getPatientId()
        const [alertData, patientData] = await Promise.all([
          getAlerts(pid),
          getPatient(pid)
        ])
        setAlerts(alertData)
        setPatient(patientData)
      } catch {
        setError('Failed to load alerts')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const familyId = patient?.family_contacts?.[0]?.id || 'family-member'
  const familyName = patient?.family_contacts?.[0]?.name || 'Family Member'

  const handleAcknowledge = async (id: string) => {
    await acknowledgeAlert(id, familyId)
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id ? { ...a, acknowledged: true, acknowledged_by: familyName } : a
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
        subtitle="Things Clara is worried about"
        rightAction={
          unacknowledgedCount > 0 ? (
            <span className="flex h-6 min-w-6 items-center justify-center rounded-full bg-red-500 px-1.5 text-[11px] font-bold text-white">
              {unacknowledgedCount}
            </span>
          ) : undefined
        }
      />

      <div className="px-4 pt-3">
        <section className="mb-3 rounded-2xl bg-white p-3 shadow-sm" aria-label="Alert filters">
          <div className="mb-2 flex items-center justify-between text-[11px] text-gray-500">
            <span>Total alerts: {alerts.length}</span>
            <span>Unacknowledged: {unacknowledgedCount}</span>
          </div>
          <div className="flex gap-2 overflow-x-auto pb-1">
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

          <label className="mt-2 flex cursor-pointer items-center justify-between gap-3 rounded-xl bg-gray-50 px-3 py-2">
            <div className="flex flex-col text-[11px]">
              <span className="font-medium text-gray-700">Show only unreviewed</span>
              <span className="text-gray-400">Hide alerts you’ve already marked as reviewed</span>
            </div>
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
          </label>
        </section>
      </div>

      <main className="space-y-3 px-4 py-3">
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
