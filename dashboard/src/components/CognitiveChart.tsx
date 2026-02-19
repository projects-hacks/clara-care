'use client'

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts'
import { format, parseISO } from 'date-fns'
import type { CognitiveTrend } from '@/lib/api'

interface CognitiveChartProps {
  data: CognitiveTrend[]
  metric: keyof Omit<CognitiveTrend, 'timestamp'>
  baselineValue?: number
  height?: number
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: { value: number }[]; label?: string }) {
  if (!active || !payload?.length || !label) return null
  return (
    <div className="rounded-lg border border-gray-100 bg-white px-3 py-2 text-xs shadow-lg">
      <p className="mb-0.5 font-medium text-gray-500">
        {format(parseISO(label), 'MMM d, yyyy')}
      </p>
      <p className="font-semibold text-clara-600">
        {typeof payload[0].value === 'number' ? payload[0].value.toFixed(2) : '—'}
      </p>
    </div>
  )
}

export default function CognitiveChart({
  data,
  metric,
  baselineValue,
  height = 200,
}: CognitiveChartProps) {
  const filtered = data
    .map((d) => ({
      timestamp: d.timestamp,
      value: d[metric],
    }))
    .filter((d) => d.value !== null && d.value !== undefined)

  return (
    <div aria-hidden={filtered.length === 0}>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={filtered} margin={{ top: 4, right: 8, bottom: 4, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis
            dataKey="timestamp"
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
          />
          <YAxis
            tick={{ fontSize: 10, fill: '#94a3b8' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          {baselineValue !== undefined && (
            <ReferenceLine
              y={baselineValue}
              stroke="#94a3b8"
              strokeDasharray="6 4"
              strokeWidth={1}
              label={{ value: 'Baseline', fontSize: 10, fill: '#94a3b8', position: 'right' }}
            />
          )}
          <Line
            type="monotone"
            dataKey="value"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#2563eb', strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
