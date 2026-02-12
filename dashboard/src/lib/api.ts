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
}

export interface Alert {
  id: string
  patient_id: string
  alert_type: string
  severity: 'low' | 'medium' | 'high'
  description: string
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

import {
  mockPatient,
  mockConversations,
  mockAlerts,
  mockDigest,
  mockCognitiveTrends,
  mockInsights,
} from './mock-data'

const USE_MOCK = true

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'
const PATIENT_ID = process.env.NEXT_PUBLIC_PATIENT_ID || 'patient-dorothy-001'

export function getPatientId(): string {
  return PATIENT_ID
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T | null> {
  if (USE_MOCK) return null
  try {
    const res = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options?.headers },
    })
    if (!res.ok) return null
    return await res.json()
  } catch {
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
