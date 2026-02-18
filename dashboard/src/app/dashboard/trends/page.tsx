'use client'

import { useState, useEffect } from 'react'
import TopBar from '@/components/TopBar'
import LoadingSpinner from '@/components/LoadingSpinner'
import CognitiveChart from '@/components/CognitiveChart'
import { getCognitiveTrends, getPatientId } from '@/lib/api'
import type { CognitiveTrend } from '@/lib/api'
import { cn, metricLabel } from '@/lib/utils'

const PERIODS = [
  { label: '7d', days: 7 },
  { label: '14d', days: 14 },
  { label: '30d', days: 30 },
] as const

const METRICS: { key: keyof Omit<CognitiveTrend, 'timestamp'>; baseline: number }[] = [
  { key: 'vocabulary_diversity', baseline: 0.63 },
  { key: 'topic_coherence', baseline: 0.87 },
  { key: 'repetition_rate', baseline: 0.05 },
  { key: 'word_finding_pauses', baseline: 1.5 },
]

export default function TrendsPage() {
  const [trends, setTrends] = useState<CognitiveTrend[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [period, setPeriod] = useState(30)

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const data = await getCognitiveTrends(getPatientId(), period)
        setTrends(data)
      } catch {
        setError('Failed to load cognitive trends')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [period])

  const filteredTrends = trends.slice(-period)

  return (
    <>
      <TopBar title="Cognitive Trends" />

      <div className="flex gap-2 px-4 pt-3">
        {PERIODS.map((p) => (
          <button
            key={p.days}
            onClick={() => setPeriod(p.days)}
            className={cn(
              'rounded-full px-4 py-1.5 text-xs font-medium transition-colors',
              period === p.days
                ? 'bg-clara-600 text-white'
                : 'bg-white text-gray-600 shadow-sm active:bg-gray-50'
            )}
            type="button"
          >
            {p.label}
          </button>
        ))}
      </div>

      <main className="space-y-4 px-4 py-4">
        {loading && <LoadingSpinner />}

        {error && (
          <div className="py-8 text-center text-sm text-red-500">{error}</div>
        )}

        {!loading &&
          !error &&
          METRICS.map((m) => (
            <section
              key={m.key}
              className="rounded-xl bg-white p-4 shadow-sm"
              aria-label={metricLabel(m.key)}
            >
              <h2 className="mb-1 text-sm font-semibold text-gray-900">
                {metricLabel(m.key)}
              </h2>
              <CognitiveChart
                data={filteredTrends}
                metric={m.key}
                baselineValue={m.baseline}
                height={180}
              />
            </section>
          ))}
      </main>
    </>
  )
}
