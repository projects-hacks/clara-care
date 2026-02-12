'use client'

import { Check } from 'lucide-react'
import type { Alert } from '@/lib/api'
import { cn, alertTypeLabel, formatTimeAgo } from '@/lib/utils'
import AlertBadge from './AlertBadge'

interface AlertCardProps {
  alert: Alert
  onAcknowledge?: (id: string) => void
}

const borderColor: Record<string, string> = {
  low: 'border-l-blue-400',
  medium: 'border-l-yellow-400',
  high: 'border-l-red-500',
}

export default function AlertCard({ alert, onAcknowledge }: AlertCardProps) {
  return (
    <div
      className={cn(
        'rounded-xl bg-white p-4 transition-shadow',
        !alert.acknowledged && 'border-l-4 shadow-sm',
        !alert.acknowledged && borderColor[alert.severity],
        alert.acknowledged && 'opacity-70'
      )}
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-gray-900">
            {alertTypeLabel(alert.alert_type)}
          </p>
          <p className="text-[11px] text-gray-400">{formatTimeAgo(alert.timestamp)}</p>
        </div>
        <AlertBadge severity={alert.severity} />
      </div>

      <p className="mb-3 text-[13px] leading-relaxed text-gray-600">{alert.description}</p>

      {!alert.acknowledged && onAcknowledge && (
        <button
          onClick={() => onAcknowledge(alert.id)}
          className="inline-flex items-center gap-1.5 rounded-lg bg-clara-50 px-3 py-1.5 text-xs font-medium text-clara-700 transition-colors active:bg-clara-100"
          type="button"
        >
          <Check className="h-3.5 w-3.5" />
          Acknowledge
        </button>
      )}

      {alert.acknowledged && alert.acknowledged_by && (
        <p className="text-[11px] text-gray-400">
          Acknowledged by {alert.acknowledged_by}
        </p>
      )}
    </div>
  )
}
