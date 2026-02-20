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
    word_finding_difficulty: 'Struggling to Find Words',
    repetition_increase: 'Repeating Stories or Phrases',
    vocabulary_decline: 'Using Fewer Words Than Usual',
    vocabulary_shrinkage: 'Using Fewer Words Than Usual',
    mood_distress: 'Signs of Distress',
    distress: 'Signs of Distress',
    response_latency: 'Slower to Respond',
    response_delay: 'Slower to Respond',
    coherence_drop: 'Conversations Harder to Follow',
    cognitive_decline: 'Change in Conversation Pattern',
    confusion_detected: 'Signs of Confusion',
    emergency: 'Emergency Alert',
    fall: 'Possible Fall Detected',
    social_connection: 'Wants to Connect with Family',
    patient_request: 'Has a Request for You',
    medication_concern: 'Medication Concern',
  }
  return map[alertType] ?? alertType.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export function alertIcon(alertType: string): string {
  const map: Record<string, string> = {
    word_finding_difficulty: '💬',
    repetition_increase: '🔁',
    vocabulary_decline: '📉',
    vocabulary_shrinkage: '📉',
    mood_distress: '😰',
    distress: '😰',
    response_latency: '⏱️',
    response_delay: '⏱️',
    coherence_drop: '🧩',
    cognitive_decline: '🧠',
    confusion_detected: '❓',
    emergency: '🚨',
    fall: '⚠️',
    social_connection: '💕',
    patient_request: '📋',
    medication_concern: '💊',
  }
  return map[alertType] ?? '🔔'
}

export function alertSuggestedAction(alertType: string, fallback?: string): string {
  const map: Record<string, string> = {
    word_finding_difficulty:
      "Call her and let the conversation flow at her pace. If this keeps happening, mention it to her doctor at the next visit.",
    repetition_increase:
      "Give her a ring and bring up something new — upcoming family plans, a shared memory, or something she is looking forward to.",
    vocabulary_decline:
      "Give her a call and chat about something she loves — a favourite memory, a family story, or what has been on her mind.",
    vocabulary_shrinkage:
      "Give her a call and chat about something she loves — a favourite memory, a family story, or what has been on her mind.",
    mood_distress:
      "Call her right away and let her know you are thinking of her. If she seems very distressed, consider arranging a visit.",
    distress:
      "Call her right away and let her know you are thinking of her. If she seems very distressed, consider arranging a visit or contacting her caregiver.",
    response_latency:
      "Check in with her — a short call to ask how she is feeling today goes a long way.",
    response_delay:
      "Check in with her — a short call to ask how she is feeling today goes a long way.",
    coherence_drop:
      "Call her yourself today. Keep it light and ask one thing at a time — a familiar voice makes a real difference.",
    cognitive_decline:
      "Bring this up at her next doctor appointment — mention the dates and what you have noticed.",
    confusion_detected:
      "Give her a reassuring call or, if possible, pop in for a visit. Let her doctor know if this is becoming more frequent.",
    emergency:
      "Call her immediately. If you cannot reach her, contact emergency services or her on-site caregiver.",
    fall:
      "Call her immediately to confirm she is safe. If you cannot reach her, contact her caregiver or a neighbour right away.",
    social_connection:
      "She is missing you. Give her a call or plan a visit — even just 10 minutes together means a lot.",
    patient_request:
      "She asked Clara for help with something. Check the details and see if you can help.",
    medication_concern:
      "She mentioned a medication side effect. Consider calling to check in and mentioning it to her doctor.",
  }
  return map[alertType] ?? fallback ?? "Give her a call to check in, and mention this to her doctor if it keeps happening."
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
