'use client'

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts'
import { format, parseISO } from 'date-fns'
import type { CognitiveTrend } from '@/lib/api'
import { cn } from '@/lib/utils'

interface CognitiveChartProps {
  data: CognitiveTrend[]
  metric: keyof Omit<CognitiveTrend, 'timestamp'>
  baselineValue?: number
  height?: number
  showGradient?: boolean
  showArea?: boolean
  animated?: boolean
  className?: string
}

interface CustomTooltipProps {
  active?: boolean
  payload?: { value: number; payload: { timestamp: string } }[]
  label?: string
  metricName?: string
  baselineValue?: number
  higherIsBetter?: boolean
}

function CustomTooltip({ active, payload, label, metricName, baselineValue, higherIsBetter }: CustomTooltipProps) {
  if (!active || !payload?.length || !label) return null
  
  const value = payload[0].value
  const date = format(parseISO(label), 'EEEE, MMM d, yyyy')
  const shortDate = format(parseISO(label), 'MMM d')
  
  // Calculate deviation from baseline
  const deviation = baselineValue && baselineValue > 0 
    ? ((value - baselineValue) / baselineValue) * 100 
    : null
  
  const isBetterThanBaseline = deviation !== null 
    ? (higherIsBetter ? deviation > 0 : deviation < 0)
    : null

  return (
    <div className="min-w-[180px] rounded-xl border border-gray-100 bg-white/95 px-4 py-3 text-xs shadow-xl backdrop-blur-sm">
      <p className="mb-2 font-semibold text-gray-900">{shortDate}</p>
      
      <div className="space-y-1.5">
        <div className="flex items-center justify-between gap-4">
          <span className="text-gray-500">{metricName}</span>
          <span className="font-bold text-clara-600">{value.toFixed(2)}</span>
        </div>
        
        {deviation !== null && Math.abs(deviation) > 1 && (
          <div className={cn(
            "flex items-center justify-between gap-4 rounded-md px-2 py-1",
            isBetterThanBaseline 
              ? 'bg-emerald-50 text-emerald-700' 
              : 'bg-amber-50 text-amber-700'
          )}>
            <span className="text-gray-600">vs baseline</span>
            <span className="font-semibold">
              {deviation > 0 ? '+' : ''}{deviation.toFixed(1)}%
            </span>
          </div>
        )}
      </div>
      
      <p className="mt-2 text-[10px] text-gray-400">{date}</p>
    </div>
  )
}

export default function CognitiveChart({
  data,
  metric,
  baselineValue,
  height = 220,
  showGradient = true,
  showArea = true,
  animated = true,
  className,
}: CognitiveChartProps) {
  const filtered = data
    .map((d) => ({
      timestamp: d.timestamp,
      value: d[metric],
    }))
    .filter((d) => d.value !== null && d.value !== undefined)

  const metricNames: Record<string, string> = {
    vocabulary_diversity: 'Vocabulary',
    topic_coherence: 'Coherence',
    repetition_rate: 'Repetition',
    word_finding_pauses: 'Word-finding',
    response_latency: 'Response time',
  }

  const higherIsBetter = metric !== 'repetition_rate' && metric !== 'word_finding_pauses' && metric !== 'response_latency'

  // Calculate min/max for Y axis domain
  const values = filtered.map(d => d.value).filter((v): v is number => v !== null && v !== undefined)
  const baseline = baselineValue ?? 0
  const minValue = values.length > 0 ? Math.min(...values, baseline) : baseline
  const maxValue = values.length > 0 ? Math.max(...values, baseline) : baseline
  const padding = (maxValue - minValue) * 0.15 || 0.1

  // Gradient colors based on metric type
  const gradientColor = higherIsBetter ? '#10b981' : '#f59e0b'
  const lineGradient = ['#2563eb', '#7c3aed', '#2563eb']

  return (
    <div className={cn("relative", className)} aria-hidden={filtered.length === 0}>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={filtered} margin={{ top: 12, right: 8, bottom: 8, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          
          <XAxis
            dataKey="timestamp"
            tickFormatter={(v: string) => {
              try {
                const date = parseISO(v)
                if (data.length > 14) {
                  return format(date, 'MMM d')
                }
                return format(date, 'MMM d')
              } catch {
                return ''
              }
            }}
            tick={{ fontSize: 11, fill: '#94a3b8', fontFamily: 'inherit' }}
            axisLine={false}
            tickLine={false}
            tickMargin={8}
            minTickGap={30}
          />
          
          <YAxis
            domain={[Math.max(0, minValue - padding), maxValue + padding]}
            tick={{ fontSize: 11, fill: '#94a3b8', fontFamily: 'inherit' }}
            axisLine={false}
            tickLine={false}
            tickMargin={8}
            tickCount={5}
          />
          
          <Tooltip 
            content={
              <CustomTooltip 
                metricName={metricNames[metric] || metric}
                baselineValue={baselineValue}
                higherIsBetter={higherIsBetter}
              />
            }
            cursor={{ stroke: '#7c3aed', strokeWidth: 1, strokeDasharray: '4 4' }}
          />
          
          {baselineValue !== undefined && baselineValue !== null && (
            <ReferenceLine
              y={baselineValue}
              stroke="#94a3b8"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{ 
                value: 'Baseline', 
                fontSize: 10, 
                fill: '#64748b',
                position: 'right',
                fontWeight: 500
              }}
            />
          )}
          
          {showArea && (
            <Area
              type="monotone"
              dataKey="value"
              stroke={`url(#lineGradient-${metric})`}
              strokeWidth={2.5}
              fillOpacity={1}
              fill={`url(#areaGradient-${metric})`}
              animationDuration={animated ? 1500 : 0}
              activeDot={{ 
                r: 5, 
                fill: '#7c3aed', 
                strokeWidth: 2, 
                stroke: '#fff',
                filter: 'drop-shadow(0 2px 4px rgba(124, 58, 237, 0.3))'
              }}
            />
          )}
          
          {!showArea && (
            <Area
              type="monotone"
              dataKey="value"
              stroke={`url(#lineGradient-${metric})`}
              strokeWidth={2.5}
              fill="transparent"
              animationDuration={animated ? 1500 : 0}
              activeDot={{ 
                r: 5, 
                fill: '#7c3aed', 
                strokeWidth: 2, 
                stroke: '#fff',
                filter: 'drop-shadow(0 2px 4px rgba(124, 58, 237, 0.3))'
              }}
            />
          )}
          
          {/* Define gradients inline */}
          <defs>
            <linearGradient id={`areaGradient-${metric}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={gradientColor} stopOpacity={0.4} />
              <stop offset="100%" stopColor={gradientColor} stopOpacity={0.05} />
            </linearGradient>
            <linearGradient id={`lineGradient-${metric}`} x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor={lineGradient[0]} stopOpacity={1} />
              <stop offset="50%" stopColor={lineGradient[1]} stopOpacity={1} />
              <stop offset="100%" stopColor={lineGradient[2]} stopOpacity={1} />
            </linearGradient>
          </defs>
        </AreaChart>
      </ResponsiveContainer>
      
      {/* Decorative gradient glow */}
      <div className="pointer-events-none absolute -inset-x-4 -bottom-8 h-16 bg-gradient-to-t from-clara-50/50 to-transparent blur-xl" />
    </div>
  )
}
