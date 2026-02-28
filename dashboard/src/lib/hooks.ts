import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from './api'
import { getPatientId } from './api'

// ─── Query Keys ────────────────────────────────────────────────────────────────
// Centralised keys for cache invalidation and deduplication.
export const queryKeys = {
    patient: (id: string) => ['patient', id] as const,
    conversations: (id: string, limit?: number) => ['conversations', id, limit] as const,
    alerts: (id: string) => ['alerts', id] as const,
    cognitiveTrends: (id: string, days?: number) => ['cognitiveTrends', id, days] as const,
    latestDigest: (id: string) => ['latestDigest', id] as const,
    wellnessDigests: (id: string) => ['wellnessDigests', id] as const,
}

// ─── Patient ───────────────────────────────────────────────────────────────────
export function usePatient(patientId?: string) {
    const id = patientId ?? getPatientId()
    return useQuery({
        queryKey: queryKeys.patient(id),
        queryFn: () => api.getPatient(id),
        staleTime: 60_000, // patient profile rarely changes
    })
}

// ─── Conversations ─────────────────────────────────────────────────────────────
export function useConversations(patientId?: string, limit = 20) {
    const id = patientId ?? getPatientId()
    return useQuery({
        queryKey: queryKeys.conversations(id, limit),
        queryFn: () => api.getConversations(id, limit),
    })
}

// ─── Alerts ────────────────────────────────────────────────────────────────────
export function useAlerts(patientId?: string) {
    const id = patientId ?? getPatientId()
    return useQuery({
        queryKey: queryKeys.alerts(id),
        queryFn: () => api.getAlerts(id),
        refetchInterval: 60_000, // poll every 60s for new alerts
    })
}

// ─── Cognitive Trends ──────────────────────────────────────────────────────────
export function useCognitiveTrends(patientId?: string, days = 30) {
    const id = patientId ?? getPatientId()
    return useQuery({
        queryKey: queryKeys.cognitiveTrends(id, days),
        queryFn: () => api.getCognitiveTrends(id, days),
        staleTime: 5 * 60_000, // trends don't change often
    })
}

// ─── Latest Digest ─────────────────────────────────────────────────────────────
export function useLatestDigest(patientId?: string) {
    const id = patientId ?? getPatientId()
    return useQuery({
        queryKey: queryKeys.latestDigest(id),
        queryFn: () => api.getLatestDigest(id),
    })
}

// ─── Mutations ─────────────────────────────────────────────────────────────────

export function useAcknowledgeAlert() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: ({ alertId, acknowledgedBy }: { alertId: string; acknowledgedBy: string }) =>
            api.acknowledgeAlert(alertId, acknowledgedBy),
        onSuccess: () => {
            // Invalidate alerts cache so the list refreshes
            queryClient.invalidateQueries({ queryKey: ['alerts'] })
        },
    })
}
