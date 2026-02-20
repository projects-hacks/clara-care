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

type MetricKey = keyof Omit<CognitiveTrend, 'timestamp'>

const METRICS: {
  key: MetricKey
  baseline: number
  higherIsBetter: boolean
  description: string
  helperText: string
}[] = [
    {
      key: 'vocabulary_diversity',
      baseline: 0.63,
      higherIsBetter: true,
      description: 'How wide a range of words she used in conversation.',
      helperText: 'Higher is generally better here.',
    },
    {
      key: 'topic_coherence',
      baseline: 0.87,
      higherIsBetter: true,
      description: 'How smoothly the conversation flowed from topic to topic.',
      helperText: 'Higher means the conversation is easier to follow.',
    },
    {
      key: 'repetition_rate',
      baseline: 0.05,
      higherIsBetter: false,
      description: 'How often stories or phrases were repeated.',
      helperText: 'Lower is better for this metric.',
    },
    {
      key: 'word_finding_pauses',
      baseline: 1.5,
      higherIsBetter: false,
      description: 'How frequently she paused to search for words.',
      helperText: 'Lower is better; more pauses can signal strain.',
    },
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
      <TopBar title="Cognitive Trends" subtitle="See how key abilities change over time">
        <div className="flex gap-2 pt-1" aria-label="Time range">
          {PERIODS.map((p) => (
            <button
              key={p.days}
              onClick={() => setPeriod(p.days)}
              className={cn(
                'rounded-full px-4 py-1.5 text-xs font-medium transition-all duration-200',
                period === p.days
                  ? 'bg-clara-600 text-white shadow-sm ring-1 ring-clara-600'
                  : 'bg-gray-50 text-gray-600 ring-1 ring-gray-200/60 hover:bg-gray-100 hover:text-gray-900'
              )}
              type="button"
            >
              {p.label}
            </button>
          ))}
        </div>
      </TopBar>

      <main className="space-y-4 px-4 py-4">
        {loading && <LoadingSpinner />}

        {error && !loading && (
          <div className="py-8 text-center text-sm text-red-500">{error}</div>
        )}

        {!loading && !error && METRICS.map((m) => (
          <TrendMetricCard
            key={m.key}
            metric={m}
            trends={filteredTrends}
          />
        ))}
      </main>
    </>
  )
}

interface TrendMetricCardProps {
  metric: typeof METRICS[number]
  trends: CognitiveTrend[]
}

function TrendMetricCard({ metric, trends }: TrendMetricCardProps) {
  const [expanded, setExpanded] = useState(false)

  const metricPoints = trends
    .map((t) => t[metric.key])
    .filter((v): v is number => v !== null && v !== undefined)

  const latest = metricPoints.length > 0 ? metricPoints[metricPoints.length - 1] : null
  const baseline = metric.baseline
  const deltaPct = latest !== null && baseline
    ? ((latest - baseline) / baseline) * 100
    : null

  let deltaLabel: string | null = null
  if (deltaPct !== null) {
    const abs = Math.abs(deltaPct)
    if (abs < 3) {
      deltaLabel = 'Roughly in line with baseline'
    } else {
      const better = metric.higherIsBetter ? deltaPct > 0 : deltaPct < 0
      deltaLabel = better ? 'Healthier than baseline' : 'Below usual baseline'
    }
  }

  return (
    <section
      className="rounded-xl bg-white p-4 shadow-sm"
      aria-label={metricLabel(metric.key)}
    >
      {/* Header — always visible */}
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h2 className="text-sm font-semibold text-gray-900">
            {metricLabel(metric.key)}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          {latest !== null && (
            <div className="text-right">
              <p className="text-sm font-semibold text-gray-900">
                {latest.toFixed(2)}
              </p>
              {deltaPct !== null && (
                <p
                  className={cn(
                    'text-[11px] font-medium',
                    deltaPct === 0
                      ? 'text-gray-500'
                      : metric.higherIsBetter
                        ? deltaPct > 0
                          ? 'text-emerald-600'
                          : 'text-red-500'
                        : deltaPct < 0
                          ? 'text-emerald-600'
                          : 'text-red-500'
                  )}
                >
                  {deltaPct > 0 ? '+' : ''}
                  {deltaPct.toFixed(1)}%
                </p>
              )}
            </div>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className={cn(
              'flex h-7 w-7 items-center justify-center rounded-full transition-colors',
              expanded
                ? 'bg-clara-100 text-clara-700'
                : 'bg-gray-50 text-gray-400 hover:bg-gray-100'
            )}
            type="button"
            aria-label={expanded ? 'Hide details' : 'Show details'}
            aria-expanded={expanded}
          >
            <span className="text-sm">{expanded ? '✕' : 'ℹ️'}</span>
          </button>
        </div>
      </div>

      {/* Chart — always visible */}
      <CognitiveChart
        data={trends}
        metric={metric.key}
        baselineValue={baseline}
        height={190}
      />

      {/* Drawer — tap to expand */}
      <div
        className={cn(
          'overflow-hidden transition-all duration-300 ease-in-out',
          expanded ? 'mt-3 max-h-60 opacity-100' : 'max-h-0 opacity-0'
        )}
      >
        <div className="space-y-2 border-t border-gray-100 pt-3 text-[11px] text-gray-600">
          <p>{metric.description}</p>
          <p className="font-medium text-gray-500">{metric.helperText}</p>
          {latest !== null && (
            <p>
              <span className="font-medium text-gray-700">Latest vs. baseline: </span>
              {latest.toFixed(2)}{' '}
              <span className="text-gray-400">(baseline {baseline.toFixed(2)})</span>
              {deltaLabel && <span className="ml-1 text-gray-700">• {deltaLabel}</span>}
            </p>
          )}
          <p className="text-[10px] text-gray-400">
            Tip: Tap and hold anywhere on the line to see the exact value for that day.
          </p>
        </div>
      </div>
    </section>
  )
}
