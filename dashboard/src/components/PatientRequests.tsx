'use client'

import { Check, ChevronRight } from 'lucide-react'
import Link from 'next/link'
import type { Alert } from '@/lib/api'
import { alertIcon, formatTimeAgo } from '@/lib/utils'

// Alert types that represent actionable patient requests (not cognitive signals)
const REQUEST_TYPES = ['patient_request', 'medication_concern', 'social_connection']

interface PatientRequestsProps {
    alerts: Alert[]
    patientName: string
    onAcknowledge: (id: string) => void
}

export default function PatientRequests({ alerts, patientName, onAcknowledge }: PatientRequestsProps) {
    const requests = alerts.filter(
        (a) => REQUEST_TYPES.includes(a.alert_type) && !a.acknowledged
    )

    if (requests.length === 0) return null

    const firstName = patientName?.split(' ')[0] || 'Your loved one'

    return (
        <section
            aria-label="Patient Requests"
            className="rounded-2xl border border-amber-100 bg-gradient-to-br from-amber-50/80 to-orange-50/40 p-4 shadow-sm"
        >
            <div className="mb-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="text-lg" aria-hidden="true">💬</span>
                    <h2 className="text-sm font-semibold text-gray-900">{firstName}&apos;s Requests</h2>
                </div>
                <Link
                    href="/dashboard/alerts"
                    className="flex items-center gap-0.5 text-xs font-medium text-amber-700"
                >
                    View All
                    <ChevronRight className="h-3.5 w-3.5" />
                </Link>
            </div>

            <div className="space-y-2">
                {requests.slice(0, 3).map((req) => (
                    <div
                        key={req.id}
                        className="flex items-start gap-3 rounded-xl bg-white/80 px-3 py-3 shadow-sm"
                    >
                        <span className="mt-0.5 text-lg shrink-0" aria-hidden="true">
                            {alertIcon(req.alert_type)}
                        </span>
                        <div className="min-w-0 flex-1">
                            <p className="text-[13px] leading-snug text-gray-800">{req.description}</p>
                            <p className="mt-1 text-[11px] text-gray-400">{formatTimeAgo(req.timestamp)}</p>
                        </div>
                        <button
                            onClick={() => onAcknowledge(req.id)}
                            className="inline-flex shrink-0 items-center gap-1 rounded-lg border border-amber-200 bg-amber-50 px-2.5 py-1 text-[11px] font-medium text-amber-800 transition-colors active:bg-amber-100"
                            type="button"
                        >
                            <Check className="h-3 w-3" />
                            Done
                        </button>
                    </div>
                ))}
            </div>
        </section>
    )
}
