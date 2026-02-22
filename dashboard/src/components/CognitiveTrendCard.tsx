'use client'

import { useMemo } from 'react'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis } from 'recharts'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import type { CognitiveTrend } from '@/lib/api'
import { cn } from '@/lib/utils'

interface CognitiveTrendCardProps {
  trends: CognitiveTrend[]
  period?: number
  compact?: boolean
}

interface TrendDataPoint {
  date: string
  score: number
}

// Calculate composite cognitive score from metrics
function calculateCognitiveScore(metrics: CognitiveTrend): number {
  const vocab = metrics.vocabulary_diversity || 0
  const coherence = metrics.topic_coherence || 0
  const repetition = metrics.repetition_rate || 0
  
  // Weight: 40% vocab, 40% coherence, 20% repetition (inverted)
  const vocabScore = vocab * 100
  const coherenceScore = coherence * 100
  const repetitionScore = (1 - repetition) * 100
  
  return Math.round(vocabScore * 0.4 + coherenceScore * 0.4 + repetitionScore * 0.2)
}

function getTrendDirection(scores: number[]): 'improving' | 'stable' | 'declining' {
  if (scores.length < 2) return 'stable'
  
  const firstHalf = scores.slice(0, Math.floor(scores.length / 2))
  const secondHalf = scores.slice(Math.floor(scores.length / 2))
  
  const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length
  const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length
  
  const change = secondAvg - firstAvg
  
  if (change > 3) return 'improving'
  if (change < -3) return 'declining'
  return 'stable'
}

function getTrendIcon(direction: 'improving' | 'stable' | 'declining') {
  switch (direction) {
    case 'improving':
      return <TrendingUp className="h-3.5 w-3.5" />
    case 'declining':
      return <TrendingDown className="h-3.5 w-3.5" />
    case 'stable':
      return <Minus className="h-3.5 w-3.5" />
  }
}

function getScoreColor(score: number): string {
  if (score >= 70) return 'text-emerald-600'
  if (score >= 40) return 'text-amber-600'
  return 'text-red-600'
}

function getScoreBgColor(score: number): string {
  if (score >= 70) return 'bg-emerald-50 ring-emerald-200'
  if (score >= 40) return 'bg-amber-50 ring-amber-200'
  return 'bg-red-50 ring-red-200'
}

export default function CognitiveTrendCard({ trends, period = 7, compact = false }: CognitiveTrendCardProps) {
  const chartData: TrendDataPoint[] = useMemo(() => {
    return trends.slice(-period).map((t) => ({
      date: t.timestamp,
      score: calculateCognitiveScore(t),
    }))
  }, [trends, period])

  const scores = chartData.map(d => d.score)
  const latestScore = scores.length > 0 ? scores[scores.length - 1] : 0
  const trendDirection = getTrendDirection(scores)
  const trendIcon = getTrendIcon(trendDirection)

  // Calculate score change
  const scoreChange = scores.length >= 2 ? scores[scores.length - 1] - scores[0] : 0

  if (chartData.length === 0) {
    return (
      <div className="rounded-2xl bg-white p-6 text-center shadow-sm ring-1 ring-gray-900/5">
        <p className="text-sm text-gray-500">No cognitive data available yet</p>
        <p className="mt-1 text-xs text-gray-400">Clara will start tracking after the first few calls</p>
      </div>
    )
  }

  if (compact) {
    return (
      <div className="relative overflow-hidden rounded-2xl bg-white p-4 shadow-sm ring-1 ring-gray-900/5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[10px] font-medium uppercase tracking-wider text-gray-400">
              Cognitive Score
            </p>
            <div className="mt-1 flex items-baseline gap-2">
              <span className={cn("text-2xl font-bold", getScoreColor(latestScore))}>
                {latestScore}
              </span>
              <span className={cn(
                "flex items-center gap-0.5 text-xs font-semibold",
                scoreChange > 0 ? 'text-emerald-600' : scoreChange < 0 ? 'text-red-500' : 'text-gray-400'
              )}>
                {trendIcon}
                {scoreChange > 0 ? '+' : ''}{scoreChange !== 0 ? scoreChange : 'No change'}
              </span>
            </div>
          </div>
          
          {/* Mini sparkline chart */}
          <div className="h-12 w-24">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 4, right: 0, bottom: 4, left: 0 }}>
                <defs>
                  <linearGradient id="miniGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={latestScore >= 70 ? '#10b981' : latestScore >= 40 ? '#f59e0b' : '#ef4444'} stopOpacity={0.4} />
                    <stop offset="100%" stopColor={latestScore >= 70 ? '#10b981' : latestScore >= 40 ? '#f59e0b' : '#ef4444'} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area
                  type="monotone"
                  dataKey="score"
                  stroke={latestScore >= 70 ? '#10b981' : latestScore >= 40 ? '#f59e0b' : '#ef4444'}
                  strokeWidth={2}
                  fill="url(#miniGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="relative overflow-hidden rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-900/5">
      {/* Header */}
      <div className="mb-4 flex items-start justify-between">
        <div>
          <p className="text-[10px] font-medium uppercase tracking-wider text-gray-400">
            Cognitive Score Trend
          </p>
          <h3 className="mt-1 text-sm font-semibold text-gray-900">
            Last {period} Days
          </h3>
        </div>
        
        <div className={cn(
          "flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1",
          getScoreBgColor(latestScore)
        )}>
          <span className={getScoreColor(latestScore)}>{latestScore}</span>
          <span className={cn(
            "flex items-center gap-0.5",
            scoreChange > 0 ? 'text-emerald-600' : scoreChange < 0 ? 'text-red-500' : 'text-gray-400'
          )}>
            {trendIcon}
            {scoreChange > 0 ? '+' : ''}{scoreChange !== 0 ? scoreChange : '0'}
          </span>
        </div>
      </div>

      {/* Chart */}
      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 8, right: 0, bottom: 0, left: -20 }}>
            <defs>
              <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                <stop 
                  offset="0%" 
                  stopColor={latestScore >= 70 ? '#10b981' : latestScore >= 40 ? '#f59e0b' : '#ef4444'} 
                  stopOpacity={0.3} 
                />
                <stop 
                  offset="100%" 
                  stopColor={latestScore >= 70 ? '#10b981' : latestScore >= 40 ? '#f59e0b' : '#ef4444'} 
                  stopOpacity={0.05} 
                />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="date"
              tickFormatter={(v: string) => {
                try {
                  return format(parseISO(v), 'MMM d')
                } catch {
                  return ''
                }
              }}
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              axisLine={false}
              tickLine={false}
              minTickGap={40}
            />
            <YAxis
              domain={[40, 100]}
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              axisLine={false}
              tickLine={false}
              tickCount={4}
            />
            <Area
              type="monotone"
              dataKey="score"
              stroke={latestScore >= 70 ? '#10b981' : latestScore >= 40 ? '#f59e0b' : '#ef4444'}
              strokeWidth={2.5}
              fill="url(#scoreGradient)"
              activeDot={{ r: 5, fill: '#fff', stroke: latestScore >= 70 ? '#10b981' : latestScore >= 40 ? '#f59e0b' : '#ef4444', strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Footer with interpretation */}
      <div className="mt-4 rounded-xl bg-gray-50 px-3 py-2.5">
        <p className="text-[11px] leading-relaxed text-gray-600">
          {trendDirection === 'improving' && (
            <>
              <span className="font-semibold text-emerald-600">Good news!</span> Cognitive performance has been trending upward over the last {period} days.
            </>
          )}
          {trendDirection === 'stable' && (
            <>
              <span className="font-semibold text-gray-700">Steady performance.</span> Cognitive metrics have remained consistent over the last {period} days.
            </>
          )}
          {trendDirection === 'declining' && (
            <>
              <span className="font-semibold text-amber-600">Worth watching.</span> There&apos;s been a slight downward trend. Consider reviewing the recommendations below.
            </>
          )}
        </p>
      </div>
    </div>
  )
}
