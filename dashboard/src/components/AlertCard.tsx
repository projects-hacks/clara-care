'use client'

import { Check, Lightbulb } from 'lucide-react'
import type { Alert } from '@/lib/api'
import { cn, alertTypeLabel, alertIcon, alertSuggestedAction, formatTimeAgo } from '@/lib/utils'
import AlertBadge from './AlertBadge'

interface AlertCardProps {
  alert: Alert
  onAcknowledge?: (id: string) => void
  familyContacts?: { id: string; name: string }[]
}

const borderColor: Record<string, string> = {
  low: 'border-l-blue-400',
  medium: 'border-l-yellow-400',
  high: 'border-l-red-500',
}

const iconBg: Record<string, string> = {
  low: 'bg-blue-50 text-blue-500',
  medium: 'bg-yellow-50 text-yellow-600',
  high: 'bg-red-50 text-red-500',
}

const tipBg: Record<string, string> = {
  low: 'bg-blue-50/60 border-blue-100',
  medium: 'bg-amber-50/60 border-amber-100',
  high: 'bg-red-50/60 border-red-100',
}

export default function AlertCard({ alert, onAcknowledge, familyContacts }: AlertCardProps) {
  const icon = alertIcon(alert.alert_type)
  const title = alertTypeLabel(alert.alert_type)
  // Use backend-provided suggested_action first, fall back to client-side map
  const tip = alert.suggested_action ?? alertSuggestedAction(alert.alert_type)
  // Resolve family member ID to display name
  const reviewerName = familyContacts?.find(f => f.id === alert.acknowledged_by)?.name
    || alert.acknowledged_by

  return (
    <div
      className={cn(
        'rounded-2xl border border-gray-100 bg-white shadow-sm transition-all',
        !alert.acknowledged && 'border-l-4 shadow-sm',
        !alert.acknowledged && borderColor[alert.severity],
        alert.acknowledged && 'opacity-60',
        !alert.acknowledged && 'active:bg-gray-50'
      )}
    >
      {/* Header */}
      <div className="flex items-start gap-3 p-4 pb-2">
        {/* Icon pill */}
        <div
          className={cn(
            'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-xl',
            iconBg[alert.severity]
          )}
          aria-hidden="true"
        >
          {icon}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-semibold leading-snug text-gray-900">{title}</p>
            <AlertBadge severity={alert.severity} />
          </div>
          <p className="mt-0.5 text-[11px] text-gray-400">{formatTimeAgo(alert.timestamp)}</p>
        </div>
      </div>

      {/* Description */}
      <div className="px-4 pb-3">
        <p className="text-[13px] leading-relaxed text-gray-600">{alert.description}</p>
      </div>

      {/* Suggested action tip */}
      {!alert.acknowledged && tip && (
        <div
          className={cn(
            'mx-4 mb-3 flex items-start gap-2 rounded-xl border px-3 py-2.5',
            tipBg[alert.severity]
          )}
        >
          <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" aria-hidden="true" />
          <p className="text-[12px] leading-snug text-gray-700">
            <span className="font-medium">What you can do: </span>
            {tip}
          </p>
        </div>
      )}

      {/* Acknowledge button / acknowledged note */}
      <div className="px-4 pb-4">
        {!alert.acknowledged && onAcknowledge && (
          <button
            onClick={() => onAcknowledge(alert.id)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-clara-100 bg-clara-50 px-3 py-1.5 text-xs font-medium text-clara-700 transition-colors active:bg-clara-100"
            type="button"
          >
            <Check className="h-3.5 w-3.5" />
            Mark as reviewed
          </button>
        )}

        {alert.acknowledged && alert.acknowledged_by && (
          <p className="text-[11px] text-gray-400">✓ Reviewed by {reviewerName}</p>
        )}
      </div>
    </div>
  )
}
