'use client'

import { useState } from 'react'
import { Phone, PhoneCall, PhoneOff, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import { callPatient } from '@/lib/api'
import { cn } from '@/lib/utils'

type CallState = 'idle' | 'calling' | 'ringing' | 'connected' | 'completed' | 'error'

interface CallButtonProps {
    patientId: string
    patientName: string
    patientPhone?: string
    className?: string
}

const stateConfig: Record<CallState, { label: string; bg: string; icon: React.ElementType; pulse?: boolean }> = {
    idle: { label: 'Call Now', bg: 'bg-gradient-to-r from-green-500 to-emerald-600', icon: Phone },
    calling: { label: 'Initiating...', bg: 'bg-amber-500', icon: Loader2, pulse: true },
    ringing: { label: 'Ringing...', bg: 'bg-amber-500', icon: PhoneCall, pulse: true },
    connected: { label: 'In Progress', bg: 'bg-green-600', icon: PhoneCall, pulse: true },
    completed: { label: 'Call Complete', bg: 'bg-clara-600', icon: CheckCircle2 },
    error: { label: 'Call Failed', bg: 'bg-red-500', icon: AlertCircle },
}

export default function CallButton({ patientId, patientName, patientPhone, className }: CallButtonProps) {
    const [state, setState] = useState<CallState>('idle')
    const [errorMsg, setErrorMsg] = useState<string>('')

    const handleCall = async () => {
        if (!patientPhone) {
            setErrorMsg('No phone number configured. Go to Settings to add one.')
            setState('error')
            setTimeout(() => { setState('idle'); setErrorMsg('') }, 4000)
            return
        }

        setState('calling')

        const result = await callPatient(patientId, patientPhone, patientName)

        if (result.success) {
            setState('ringing')
            // Transition through states to show the flow
            setTimeout(() => setState('connected'), 3000)
            // Reset after some time — in production, listen to Twilio status callback
            setTimeout(() => {
                setState('completed')
                setTimeout(() => setState('idle'), 5000)
            }, 10000)
        } else {
            setErrorMsg(result.error || 'Failed to initiate call')
            setState('error')
            setTimeout(() => { setState('idle'); setErrorMsg('') }, 5000)
        }
    }

    const config = stateConfig[state]
    const Icon = config.icon
    const isDisabled = state !== 'idle' && state !== 'error' && state !== 'completed'

    return (
        <div className={cn('space-y-2', className)}>
            <button
                onClick={handleCall}
                disabled={isDisabled}
                className={cn(
                    'relative flex w-full items-center justify-center gap-2.5 rounded-2xl px-6 py-4 text-sm font-semibold text-white shadow-lg transition-all duration-300',
                    config.bg,
                    isDisabled ? 'cursor-not-allowed opacity-90' : 'active:scale-[0.98]',
                    state === 'idle' && 'hover:shadow-xl hover:shadow-green-500/25'
                )}
                type="button"
            >
                {/* Pulse ring for active states */}
                {config.pulse && (
                    <span className="absolute inset-0 animate-ping rounded-2xl bg-white/10" />
                )}

                <Icon
                    className={cn(
                        'relative h-5 w-5',
                        state === 'calling' && 'animate-spin'
                    )}
                />
                <span className="relative">
                    {state === 'idle' ? `Call ${patientName}` : config.label}
                </span>
            </button>

            {/* Error message */}
            {state === 'error' && errorMsg && (
                <p className="text-center text-xs text-red-500">{errorMsg}</p>
            )}

            {/* No phone hint */}
            {state === 'idle' && !patientPhone && (
                <p className="text-center text-[11px] text-gray-400">
                    Set a phone number in Settings to enable calls
                </p>
            )}
        </div>
    )
}
