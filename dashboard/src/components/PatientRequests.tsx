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
            className="relative overflow-hidden rounded-2xl border border-amber-200/50 bg-gradient-to-br from-amber-50/90 to-orange-50/50 p-5 shadow-[0_2px_15px_-3px_rgba(251,191,36,0.15)] ring-1 ring-amber-100/50"
        >
            <div className="absolute -left-10 -top-10 h-32 w-32 rounded-full bg-amber-400/10 blur-2xl"></div>
            <div className="relative z-10 mb-4 flex items-center justify-between">
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
                        className="group relative flex items-start gap-3 rounded-xl border border-white/40 bg-white/70 px-4 py-3 shadow-[0_2px_10px_-4px_rgba(0,0,0,0.03)] backdrop-blur-md transition-all duration-300 hover:bg-white hover:shadow-md"
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
                            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-amber-200/60 bg-gradient-to-b from-amber-50 to-amber-100/50 px-3 py-1.5 text-xs font-medium text-amber-800 shadow-sm transition-all hover:-translate-y-0.5 hover:border-amber-300 hover:from-amber-100 hover:to-amber-200 hover:shadow-md active:scale-95"
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
