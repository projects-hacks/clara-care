import { clsx, type ClassValue } from 'clsx'
import { format, formatDistanceToNow, parseISO } from 'date-fns'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatDate(iso: string): string {
  try {
    return format(parseISO(iso), 'MMM d, yyyy')
  } catch {
    return iso
  }
}

export function formatDateTime(iso: string): string {
  try {
    return format(parseISO(iso), 'MMM d, yyyy h:mm a')
  } catch {
    return iso
  }
}

export function formatTimeAgo(iso: string): string {
  try {
    return formatDistanceToNow(parseISO(iso), { addSuffix: true })
  } catch {
    return iso
  }
}

export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  if (m === 0) return `${s}s`
  if (s === 0) return `${m}m`
  return `${m}m ${s}s`
}

export function moodEmoji(mood: string): string {
  const map: Record<string, string> = {
    happy: '😊',
    neutral: '😐',
    sad: '😢',
    confused: '😕',
    distressed: '😰',
    nostalgic: '🥰',
    anxious: '😟',
  }
  return map[mood?.toLowerCase()] ?? '😐'
}

export function moodColor(mood: string): string {
  const map: Record<string, string> = {
    happy: 'text-mood-happy bg-green-50',
    neutral: 'text-mood-neutral bg-gray-50',
    sad: 'text-mood-sad bg-blue-50',
    confused: 'text-mood-confused bg-yellow-50',
    distressed: 'text-mood-distressed bg-red-50',
    nostalgic: 'text-mood-nostalgic bg-purple-50',
  }
  return map[mood?.toLowerCase()] ?? 'text-gray-500 bg-gray-50'
}

export function moodLabel(mood: string): string {
  return mood ? mood.charAt(0).toUpperCase() + mood.slice(1) : 'Unknown'
}

export function severityColor(severity: string): string {
  const map: Record<string, string> = {
    low: 'text-blue-700 bg-blue-100',
    medium: 'text-yellow-700 bg-yellow-100',
    high: 'text-red-700 bg-red-100',
  }
  return map[severity?.toLowerCase()] ?? 'text-gray-700 bg-gray-100'
}

export function cognitiveScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

export function cognitiveScoreBg(score: number): string {
  if (score >= 80) return 'bg-green-100 text-green-700'
  if (score >= 60) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}

export function alertTypeLabel(alertType: string): string {
  const map: Record<string, string> = {
    word_finding_difficulty: 'Word Finding Difficulty',
    repetition_increase: 'Repetition Increase',
    vocabulary_decline: 'Vocabulary Decline',
    mood_distress: 'Mood Distress',
    response_latency: 'Response Latency',
    coherence_drop: 'Coherence Drop',
  }
  return map[alertType] ?? alertType.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export function metricLabel(key: string): string {
  const map: Record<string, string> = {
    vocabulary_diversity: 'Vocabulary Diversity',
    topic_coherence: 'Topic Coherence',
    repetition_rate: 'Repetition Rate',
    word_finding_pauses: 'Word-Finding Pauses',
    response_latency: 'Response Latency',
  }
  return map[key] ?? key
}

export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`
}
