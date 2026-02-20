// ClaraCare API Client
// Connects to the ClaraCare backend API for patient data, conversations, and call initiation

export interface Patient {
  id: string
  name: string
  preferred_name: string
  date_of_birth: string
  birth_year: number
  age: number
  location: {
    city: string
    state: string
    timezone: string
  }
  medical_notes: string
  medications: { name: string; dosage: string; schedule: string }[]
  preferences: {
    favorite_topics: string[]
    communication_style: string
    interests: string[]
    topics_to_avoid?: string[]
  }
  cognitive_thresholds: {
    deviation_threshold: number
    consecutive_trigger: number
  }
  call_schedule?: { preferred_time: string; timezone: string }
  phone_number?: string
  family_contacts?: {
    id: string
    name: string
    email: string
    phone: string
    relationship: string
    notification_preferences: {
      daily_digest: boolean
      instant_alerts: boolean
      weekly_report: boolean
    }
  }[]
}

export interface CognitiveMetrics {
  vocabulary_diversity: number
  topic_coherence: number
  repetition_count: number
  repetition_rate: number
  word_finding_pauses: number
  response_latency: number | null
}

export interface Conversation {
  id: string
  patient_id: string
  timestamp: string
  duration: number
  transcript: string
  summary: string
  detected_mood: string
  cognitive_metrics: CognitiveMetrics | null
  nostalgia_engagement?: {
    triggered: boolean
    era: string
    content_used: string
    engagement_score: number
  } | null
  medication_status?: {
    discussed: boolean
    medications_mentioned: { name: string; taken?: boolean }[]
    notes: string
  } | null
}

export interface Alert {
  id: string
  patient_id: string
  alert_type: string
  severity: 'low' | 'medium' | 'high'
  description: string
  suggested_action?: string
  acknowledged: boolean
  acknowledged_by: string | null
  timestamp: string
  conversation_id?: string
}


export interface WellnessDigest {
  id: string
  patient_id: string
  date: string
  overall_mood: string
  cognitive_score: number
  cognitive_trend: string
  highlights: string[]
  recommendations: string[]
}

export interface CognitiveTrend {
  timestamp: string
  vocabulary_diversity: number
  topic_coherence: number
  repetition_rate: number
  word_finding_pauses: number
  response_latency: number | null
}

export interface Insights {
  cognitive_by_mood: Record<string, { avg_vocabulary: number; avg_coherence: number; conversation_count: number }>
  nostalgia_effectiveness: {
    with_nostalgia: { avg_vocabulary: number; avg_coherence: number }
    without_nostalgia: { avg_vocabulary: number; avg_coherence: number }
    improvement_pct: { vocabulary: number; coherence: number }
  }
  alert_summary: {
    total: number
    by_severity: Record<string, number>
    most_common_type: string
    unacknowledged?: number
  }
}

export interface CallResult {
  success: boolean
  call_sid?: string
  patient_id?: string
  patient_phone?: string
  status?: string
  error?: string
}

import {
  mockPatient,
  mockConversations,
  mockAlerts,
  mockDigest,
  mockCognitiveTrends,
  mockInsights,
} from './mock-data'

// Toggle mock mode — set to false for live backend
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.claracare.me'
const PATIENT_ID = process.env.NEXT_PUBLIC_PATIENT_ID || 'patient-dorothy-001'

export function getPatientId(): string {
  return PATIENT_ID
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T | null> {
  if (USE_MOCK) return null
  const url = `${API_URL}${path}`
  try {
    console.debug(`[ClaraCare API] ${options?.method || 'GET'} ${path}`)
    const res = await fetch(url, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options?.headers },
    })
    if (!res.ok) {
      console.warn(`[ClaraCare API] ${path} → ${res.status} ${res.statusText}`)
      return null
    }
    return await res.json()
  } catch (e) {
    console.error(`[ClaraCare API] ${path} → Network error:`, e)
    return null
  }
}

export async function getPatient(patientId: string): Promise<Patient | null> {
  if (USE_MOCK) return mockPatient
  const data = await apiFetch<{ patient: Patient }>(`/api/patients/${patientId}`)
  return data?.patient ?? null
}

export async function getConversations(patientId: string, limit = 20, offset = 0): Promise<Conversation[]> {
  if (USE_MOCK) return mockConversations
  const data = await apiFetch<{ conversations: Conversation[] }>(
    `/api/conversations?patient_id=${patientId}&limit=${limit}&offset=${offset}`
  )
  return data?.conversations ?? []
}

export async function getConversation(conversationId: string): Promise<Conversation | null> {
  if (USE_MOCK) return mockConversations.find((c) => c.id === conversationId) ?? null
  return apiFetch<Conversation>(`/api/conversations/${conversationId}`)
}

export async function getCognitiveTrends(patientId: string, days = 30): Promise<CognitiveTrend[]> {
  if (USE_MOCK) return mockCognitiveTrends
  const data = await apiFetch<{ data_points: CognitiveTrend[] }>(
    `/api/cognitive-trends?patient_id=${patientId}&days=${days}`
  )
  return data?.data_points ?? []
}

export async function getAlerts(patientId: string, severity?: string): Promise<Alert[]> {
  if (USE_MOCK) {
    if (severity) return mockAlerts.filter((a) => a.severity === severity)
    return mockAlerts
  }
  const params = new URLSearchParams({ patient_id: patientId })
  if (severity) params.set('severity', severity)
  const data = await apiFetch<{ alerts: Alert[] }>(`/api/alerts?${params}`)
  return data?.alerts ?? []
}

export async function acknowledgeAlert(alertId: string, acknowledgedBy: string): Promise<boolean> {
  if (USE_MOCK) {
    const alert = mockAlerts.find((a) => a.id === alertId)
    if (alert) {
      alert.acknowledged = true
      alert.acknowledged_by = acknowledgedBy
    }
    return true
  }
  const res = await apiFetch(`/api/alerts/${alertId}`, {
    method: 'PATCH',
    body: JSON.stringify({ acknowledged_by: acknowledgedBy }),
  })
  return res !== null
}

export async function getWellnessDigests(patientId: string, limit = 10): Promise<WellnessDigest[]> {
  if (USE_MOCK) return [mockDigest]
  const data = await apiFetch<{ digests: WellnessDigest[] }>(
    `/api/wellness-digests?patient_id=${patientId}&limit=${limit}`
  )
  return data?.digests ?? []
}

export async function getLatestDigest(patientId: string): Promise<WellnessDigest | null> {
  if (USE_MOCK) return mockDigest
  return apiFetch<WellnessDigest>(`/api/wellness-digests/latest?patient_id=${patientId}`)
}

export async function getInsights(patientId: string): Promise<Insights | null> {
  if (USE_MOCK) return mockInsights
  const data = await apiFetch<{ insights: Insights }>(`/api/patients/${patientId}/insights`)
  return data?.insights ?? null
}

export async function downloadReport(patientId: string, days = 30): Promise<Blob | null> {
  try {
    const res = await fetch(`${API_URL}/api/reports/${patientId}/cognitive-report?days=${days}`)
    if (!res.ok) return null
    return await res.blob()
  } catch {
    return null
  }
}

export async function updatePatient(patientId: string, updates: Partial<Patient>): Promise<boolean> {
  const res = await apiFetch(`/api/patients/${patientId}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  })
  return res !== null
}

// Call initiation — triggers an outbound call to the patient
export async function callPatient(
  patientId: string,
  patientPhone: string,
  patientName?: string
): Promise<CallResult> {
  console.log(`[ClaraCare Call] Initiating call to ${patientName} (${patientPhone}) patient=${patientId}`)
  try {
    const res = await fetch(`${API_URL}/voice/call/patient`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_id: patientId,
        patient_phone: patientPhone,
        patient_name: patientName || 'Patient',
      }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      console.error(`[ClaraCare Call] Failed: ${res.status}`, err)
      return { success: false, error: err.detail || 'Call failed' }
    }
    const result = await res.json()
    console.log(`[ClaraCare Call] Success:`, result)
    return result
  } catch (e) {
    console.error(`[ClaraCare Call] Network error:`, e)
    return { success: false, error: e instanceof Error ? e.message : 'Network error' }
  }
}
