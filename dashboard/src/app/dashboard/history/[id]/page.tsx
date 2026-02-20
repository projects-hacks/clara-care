'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Clock, Sparkles, Star, MessageCircle, Brain, AlertTriangle, TrendingUp, TrendingDown, Minus, Pill } from 'lucide-react'
import TopBar from '@/components/TopBar'
import LoadingSpinner from '@/components/LoadingSpinner'
import MoodBadge from '@/components/MoodBadge'
import { getConversation } from '@/lib/api'
import type { Conversation } from '@/lib/api'
import { formatDate, formatDuration, metricLabel, cn } from '@/lib/utils'

// ─── Metric helpers ──────────────────────────────────────────────────────────

const METRIC_THRESHOLDS: Record<string, { good: number; warn: number; higherIsBetter: boolean }> = {
  vocabulary_diversity: { good: 0.6, warn: 0.4, higherIsBetter: true },
  topic_coherence: { good: 0.5, warn: 0.35, higherIsBetter: true },
  repetition_rate: { good: 0.05, warn: 0.12, higherIsBetter: false },
  word_finding_pauses: { good: 2, warn: 4, higherIsBetter: false },
  response_latency: { good: 2, warn: 4, higherIsBetter: false },
}

const METRIC_PLAIN_LABELS: Record<string, string> = {
  vocabulary_diversity: 'Word variety',
  topic_coherence: 'Conversation flow',
  repetition_rate: 'Repeated phrases',
  word_finding_pauses: 'Pauses to find words',
  response_latency: 'Response speed',
}

const METRIC_DESCRIPTIONS: Record<string, { good: string; warn: string; bad: string }> = {
  vocabulary_diversity: {
    good: 'Talking with a healthy range of words today.',
    warn: 'Slightly fewer word choices than usual.',
    bad: 'Using a noticeably limited vocabulary today.',
  },
  topic_coherence: {
    good: 'Conversation flowed well from topic to topic.',
    warn: 'A few moments of jumping between topics.',
    bad: 'Conversation was hard to follow today.',
  },
  repetition_rate: {
    good: 'No unusual repetition today.',
    warn: 'Repeated a few topics or phrases.',
    bad: 'Repeated stories or phrases more than usual.',
  },
  word_finding_pauses: {
    good: 'No notable pauses to find words.',
    warn: 'A few pauses while searching for words.',
    bad: 'Stopped frequently to search for words.',
  },
  response_latency: {
    good: 'Responding quickly and confidently.',
    warn: 'Slightly slower to respond than usual.',
    bad: 'Taking noticeably longer to respond.',
  },
}

type MetricStatus = 'good' | 'warn' | 'bad' | 'neutral'

function getMetricStatus(key: string, value: number): MetricStatus {
  const t = METRIC_THRESHOLDS[key]
  if (!t) return 'neutral'
  if (t.higherIsBetter) {
    if (value >= t.good) return 'good'
    if (value >= t.warn) return 'warn'
    return 'bad'
  } else {
    if (value <= t.good) return 'good'
    if (value <= t.warn) return 'warn'
    return 'bad'
  }
}

function MetricStatusIcon({ status }: { status: MetricStatus }) {
  if (status === 'good') return <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />
  if (status === 'bad') return <TrendingDown className="h-3.5 w-3.5 text-red-400" />
  if (status === 'warn') return <Minus className="h-3.5 w-3.5 text-amber-400" />
  return null
}

const STATUS_COLORS: Record<MetricStatus, string> = {
  good: 'bg-emerald-50 border-emerald-100',
  warn: 'bg-amber-50  border-amber-100',
  bad: 'bg-red-50    border-red-100',
  neutral: 'bg-gray-50   border-gray-100',
}

const STATUS_TEXT: Record<MetricStatus, string> = {
  good: 'text-emerald-700',
  warn: 'text-amber-700',
  bad: 'text-red-600',
  neutral: 'text-gray-500',
}

// ─── Mood tone helper ────────────────────────────────────────────────────────

const MOOD_CONTEXT: Record<string, { emoji: string; label: string; description: string; color: string }> = {
  happy: { emoji: '😊', label: 'Happy', description: 'She seemed cheerful and in good spirits today.', color: 'text-emerald-600 bg-emerald-50' },
  positive: { emoji: '🙂', label: 'Positive', description: 'Her mood came across as warm and positive.', color: 'text-emerald-600 bg-emerald-50' },
  neutral: { emoji: '😐', label: 'Neutral', description: 'She seemed calm and steady during the call.', color: 'text-gray-600 bg-gray-50' },
  distressed: { emoji: '😟', label: 'Distressed', description: 'She seemed upset or troubled during this call.', color: 'text-red-600 bg-red-50' },
  anxious: { emoji: '😰', label: 'Anxious', description: 'She sounded worried or anxious during this call.', color: 'text-amber-600 bg-amber-50' },
  sad: { emoji: '😢', label: 'Sad', description: 'She sounded low or sad during this call.', color: 'text-blue-600 bg-blue-50' },
  confused: { emoji: '😕', label: 'Confused', description: 'She seemed confused or uncertain at times.', color: 'text-amber-600 bg-amber-50' },
  lonely: { emoji: '🌧️', label: 'Lonely', description: 'She seemed withdrawn or in need of connection today.', color: 'text-indigo-600 bg-indigo-50' },
}

function getMoodContext(mood: string) {
  return MOOD_CONTEXT[mood?.toLowerCase()] ?? {
    emoji: '💬',
    label: mood ?? 'Unknown',
    description: 'The overall mood of this call was noted.',
    color: 'text-gray-600 bg-gray-50',
  }
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function ConversationDetailPage() {
  const params = useParams()
  const id = params.id as string
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const data = await getConversation(id)
        if (!data) {
          setError('Conversation not found')
          return
        }
        setConversation(data)
      } catch {
        setError('Failed to load conversation')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) {
    return (
      <>
        <TopBar title="Call Summary" showBack />
        <LoadingSpinner />
      </>
    )
  }

  if (error || !conversation) {
    return (
      <>
        <TopBar title="Call Summary" showBack />
        <div className="flex items-center justify-center px-4 py-16">
          <p className="text-sm text-red-500">{error || 'Conversation not found'}</p>
        </div>
      </>
    )
  }

  const metrics = conversation.cognitive_metrics
  const metricEntries = metrics
    ? [
      { key: 'vocabulary_diversity', value: metrics.vocabulary_diversity },
      { key: 'topic_coherence', value: metrics.topic_coherence },
      { key: 'repetition_rate', value: metrics.repetition_rate },
      { key: 'word_finding_pauses', value: metrics.word_finding_pauses },
      { key: 'response_latency', value: metrics.response_latency },
    ].filter(({ value }) => value !== null && value !== undefined) as { key: string; value: number }[]
    : []

  const transcriptLines = conversation.transcript
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) => {
      const colonIndex = line.indexOf(':')
      if (colonIndex === -1) return { speaker: '', text: line }
      const speaker = line.slice(0, colonIndex).trim()
      const text = line.slice(colonIndex + 1).trim()
      return { speaker, text }
    })

  const nostalgia = conversation.nostalgia_engagement
  const moodCtx = getMoodContext(conversation.detected_mood)
  const medStatus = conversation.medication_status

  // Aggregate health signal — count bad/warn metrics
  const badCount = metricEntries.filter(({ key, value }) => getMetricStatus(key, value) === 'bad').length
  const warnCount = metricEntries.filter(({ key, value }) => getMetricStatus(key, value) === 'warn').length
  const overallSignal =
    badCount >= 2 ? 'needs-attention' :
      badCount === 1 || warnCount >= 2 ? 'watch' : 'ok'

  return (
    <>
      <TopBar title="Call Summary" showBack />

      <main className="space-y-4 px-4 py-4 pb-8">

        {/* ── Header card ── */}
        <section className="rounded-2xl bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-0.5">
                {formatDate(conversation.timestamp)}
              </p>
              <div className="flex items-center gap-1.5 text-xs text-gray-500">
                <Clock className="h-3 w-3" />
                <span>{formatDuration(conversation.duration)}</span>
              </div>
            </div>
            <MoodBadge mood={conversation.detected_mood} size="md" />
          </div>

          {/* Mood context strip */}
          <div className={cn('mt-3 flex items-start gap-2 rounded-xl px-3 py-2.5', moodCtx.color)}>
            <span className="text-base leading-none mt-0.5">{moodCtx.emoji}</span>
            <p className="text-xs leading-relaxed font-medium">{moodCtx.description}</p>
          </div>
        </section>

        {/* ── What happened ── */}
        {conversation.summary && (
          <section className="rounded-2xl bg-white p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <MessageCircle className="h-4 w-4 text-clara-500" />
              <h2 className="text-sm font-semibold text-gray-900">What happened in this call</h2>
            </div>
            <p className="text-sm leading-relaxed text-gray-600">{conversation.summary}</p>
          </section>
        )}

        {/* ── Cognitive snapshot ── */}
        {metricEntries.length > 0 && (
          <section className="rounded-2xl bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4 text-purple-500" />
                <h2 className="text-sm font-semibold text-gray-900">Cognitive snapshot</h2>
              </div>
              {overallSignal === 'needs-attention' && (
                <span className="flex items-center gap-1 text-[10px] font-semibold text-red-500 bg-red-50 rounded-full px-2 py-0.5">
                  <AlertTriangle className="h-3 w-3" /> Needs attention
                </span>
              )}
              {overallSignal === 'watch' && (
                <span className="text-[10px] font-semibold text-amber-600 bg-amber-50 rounded-full px-2 py-0.5">
                  Worth watching
                </span>
              )}
              {overallSignal === 'ok' && (
                <span className="text-[10px] font-semibold text-emerald-600 bg-emerald-50 rounded-full px-2 py-0.5">
                  Looking good
                </span>
              )}
            </div>
            <p className="text-[11px] text-gray-400 mb-3">
              These signals come from the conversation and help track patterns over time.
            </p>
            <div className="space-y-2">
              {metricEntries.map(({ key, value }) => {
                const status = getMetricStatus(key, value)
                const desc = METRIC_DESCRIPTIONS[key]
                const plainLabel = METRIC_PLAIN_LABELS[key] ?? metricLabel(key)
                const descText =
                  desc
                    ? status === 'good' ? desc.good : status === 'bad' ? desc.bad : desc.warn
                    : null
                return (
                  <div
                    key={key}
                    className={cn(
                      'flex items-center justify-between rounded-xl border px-3 py-2.5',
                      STATUS_COLORS[status]
                    )}
                  >
                    <div className="flex-1 min-w-0 pr-2">
                      <p className="text-xs font-semibold text-gray-700">{plainLabel}</p>
                      {descText && (
                        <p className={cn('text-[11px] mt-0.5', STATUS_TEXT[status])}>{descText}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      <MetricStatusIcon status={status} />
                    </div>
                  </div>
                )
              })}
            </div>
          </section>
        )}

        {/* ── Medication check ── */}
        {medStatus && (
          <section className="rounded-2xl bg-white p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Pill className="h-4 w-4 text-blue-500" />
              <h2 className="text-sm font-semibold text-gray-900">Medication check</h2>
            </div>
            {medStatus.discussed ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2 rounded-xl bg-emerald-50 border border-emerald-100 px-3 py-2.5">
                  <span className="text-base">✅</span>
                  <p className="text-xs font-medium text-emerald-700">Clara asked about medications during this call.</p>
                </div>
                {medStatus.medications_mentioned && medStatus.medications_mentioned.length > 0 && (
                  <div className="space-y-1 pl-1">
                    {medStatus.medications_mentioned.map((med, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs text-gray-600">
                        <span>{med.taken === true ? '✅' : med.taken === false ? '❌' : '➖'}</span>
                        <span className="font-medium">{med.name}</span>
                        <span className="text-gray-400">{med.taken === true ? 'Confirmed taken' : med.taken === false ? 'Not taken' : 'Mentioned'}</span>
                      </div>
                    ))}
                  </div>
                )}
                {medStatus.notes && (
                  <p className="text-[11px] text-gray-500 pl-1 mt-1">{medStatus.notes}</p>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2 rounded-xl bg-amber-50 border border-amber-100 px-3 py-2.5">
                <span className="text-base">⚠️</span>
                <p className="text-xs font-medium text-amber-700">Medications weren&apos;t discussed in this call.</p>
              </div>
            )}
          </section>
        )}

        {/* ── Nostalgia ── */}
        {nostalgia && nostalgia.triggered && (
          <section className="rounded-2xl bg-gradient-to-br from-purple-50 to-clara-50 p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-500" />
              <h2 className="text-sm font-semibold text-gray-900">Memory lane moment</h2>
            </div>
            <p className="text-xs text-gray-500 mb-3">
              Clara shared era-specific content to spark joy and connection.
            </p>
            <div className="space-y-2">
              {nostalgia.era && (
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-medium text-gray-400 w-20 shrink-0">Era</span>
                  <span className="text-sm font-semibold text-gray-800">{nostalgia.era}</span>
                </div>
              )}
              {nostalgia.content_used && (
                <div className="flex items-start gap-2">
                  <span className="text-[11px] font-medium text-gray-400 w-20 shrink-0 pt-0.5">Shared</span>
                  <span className="text-sm text-gray-600">{nostalgia.content_used}</span>
                </div>
              )}
              <div className="flex items-center gap-2 pt-1">
                <span className="text-[11px] font-medium text-gray-400 w-20 shrink-0">Engagement</span>
                <div className="flex items-center gap-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star
                      key={i}
                      className={cn(
                        'h-3.5 w-3.5',
                        i < Math.round(nostalgia.engagement_score / 2)
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'fill-gray-200 text-gray-200'
                      )}
                    />
                  ))}
                  <span className="ml-1 text-xs font-semibold text-gray-600">
                    {nostalgia.engagement_score}/10
                  </span>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* ── Transcript ── */}
        <section className="rounded-2xl bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-sm font-semibold text-gray-900">Call transcript</h2>
          <div className="max-h-96 space-y-2 overflow-y-auto">
            {transcriptLines.map((line, i) => {
              const isClara = line.speaker.toLowerCase() === 'clara'
              return (
                <div
                  key={i}
                  className={cn('flex', isClara ? 'justify-start' : 'justify-end')}
                >
                  <div
                    className={cn(
                      'max-w-[85%] rounded-2xl px-3 py-2',
                      isClara
                        ? 'rounded-bl-sm bg-gray-100 text-gray-700'
                        : 'rounded-br-sm bg-clara-500 text-white'
                    )}
                  >
                    <p className={cn('mb-0.5 text-[10px] font-semibold', isClara ? 'text-gray-400' : 'text-clara-100')}>
                      {isClara ? 'Clara' : line.speaker}
                    </p>
                    <p className="text-sm leading-relaxed">{line.text}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </section>
      </main>
    </>
  )
}
