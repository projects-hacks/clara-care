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
            <span className="flex h-6 min-w-6 items-center justify-center rounded-full bg-red-500 px-1.5 text-[11px] font-bold text-white shadow-sm ring-2 ring-white">
              {unacknowledgedCount}
            </span>
          ) : undefined
        }
      >
        <div className="overflow-x-auto pt-1" style={{ scrollbarWidth: 'none' }}>
          <div className="flex gap-2">
            {SEVERITY_FILTERS.map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                className={cn(
                  'shrink-0 rounded-full px-4 py-1.5 text-xs font-medium transition-all duration-200',
                  activeFilter === filter
                    ? 'bg-clara-600 text-white shadow-sm ring-1 ring-clara-600'
                    : 'bg-gray-50 text-gray-600 ring-1 ring-gray-200/60 hover:bg-gray-100 hover:text-gray-900'
                )}
                type="button"
              >
                {filter}
              </button>
            ))}
          </div>
        </div>
      </TopBar>

      <main className="space-y-4 px-4 py-4">
        {alerts.length > 0 && !loading && !error && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-[11px] font-medium uppercase tracking-wide text-gray-400 px-1">
              <span>Total alerts: {alerts.length}</span>
              <span>Unacknowledged: {unacknowledgedCount}</span>
            </div>
            <label className="flex cursor-pointer items-center justify-between gap-3 rounded-2xl bg-white shadow-sm ring-1 ring-gray-900/5 px-4 py-3 transition-all hover:bg-gray-50 active:scale-[0.98]">
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-gray-900">Show only unreviewed</span>
                <span className="mt-0.5 text-[11px] leading-snug text-gray-500">Hide alerts you’ve already verified</span>
              </div>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={showUnacknowledgedOnly}
                  onChange={(e) => setShowUnacknowledgedOnly(e.target.checked)}
                  className="peer sr-only"
                />
                <div className="h-5 w-9 rounded-full bg-gray-200 transition-colors peer-checked:bg-clara-600 ring-1 ring-inset ring-black/5" />
                <div className="absolute left-0.5 top-0.5 h-4 w-4 rounded-full bg-white shadow-sm ring-1 ring-black/5 transition-transform peer-checked:translate-x-4" />
              </div>
            </label>
          </div>
        )}

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
                familyContacts={patient?.family_contacts}
              />
            ))}
          </div>
        )}
      </main>
    </>
  )
}
