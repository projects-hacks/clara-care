'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Clock, Sparkles, Star } from 'lucide-react'
import TopBar from '@/components/TopBar'
import LoadingSpinner from '@/components/LoadingSpinner'
import MoodBadge from '@/components/MoodBadge'
import { getConversation } from '@/lib/api'
import type { Conversation } from '@/lib/api'
import { formatDate, formatDuration, metricLabel, cn } from '@/lib/utils'

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
        <TopBar title="Conversation Detail" showBack />
        <LoadingSpinner />
      </>
    )
  }

  if (error || !conversation) {
    return (
      <>
        <TopBar title="Conversation Detail" showBack />
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
      ]
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

  return (
    <>
      <TopBar title="Conversation Detail" showBack />

      <main className="space-y-4 px-4 py-4">
        <section className="rounded-xl bg-white p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <MoodBadge mood={conversation.detected_mood} size="md" />
            <div className="text-xs text-gray-500">
              <p>{formatDate(conversation.timestamp)}</p>
              <p className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {formatDuration(conversation.duration)}
              </p>
            </div>
          </div>
        </section>

        <section className="rounded-xl bg-white p-4 shadow-sm">
          <h2 className="mb-2 text-sm font-semibold text-gray-900">Summary</h2>
          <p className="text-sm leading-relaxed text-gray-600">{conversation.summary}</p>
        </section>

        {metrics && metricEntries.length > 0 && (
          <section className="rounded-xl bg-white p-4 shadow-sm">
            <h2 className="mb-3 text-sm font-semibold text-gray-900">Cognitive Metrics</h2>
            <div className="grid grid-cols-2 gap-3">
              {metricEntries.map(({ key, value }) => (
                <div key={key} className="rounded-lg bg-gray-50 p-3">
                  <p className="mb-0.5 text-[11px] text-gray-400">{metricLabel(key)}</p>
                  <p className="text-base font-semibold text-gray-900">
                    {value !== null && value !== undefined ? (typeof value === 'number' && value < 1 ? value.toFixed(2) : value) : '—'}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}

        {nostalgia && nostalgia.triggered && (
          <section className="rounded-xl bg-gradient-to-br from-purple-50 to-clara-50 p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-500" />
              <h2 className="text-sm font-semibold text-gray-900">Nostalgia Engagement</h2>
            </div>
            <div className="space-y-2">
              <div>
                <p className="text-[11px] text-gray-400">Era</p>
                <p className="text-sm font-medium text-gray-800">{nostalgia.era}</p>
              </div>
              <div>
                <p className="text-[11px] text-gray-400">Content Used</p>
                <p className="text-sm text-gray-600">{nostalgia.content_used}</p>
              </div>
              <div className="flex items-center gap-1">
                <p className="text-[11px] text-gray-400">Engagement Score</p>
                <div className="flex items-center gap-0.5">
                  <Star className="h-3.5 w-3.5 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm font-semibold text-gray-900">{nostalgia.engagement_score}/10</span>
                </div>
              </div>
            </div>
          </section>
        )}

        <section className="rounded-xl bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-sm font-semibold text-gray-900">Transcript</h2>
          <div className="max-h-96 space-y-2 overflow-y-auto">
            {transcriptLines.map((line, i) => {
              const isClara = line.speaker.toLowerCase() === 'clara'
              return (
                <div
                  key={i}
                  className={cn(
                    'flex',
                    isClara ? 'justify-start' : 'justify-end'
                  )}
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
                      {line.speaker}
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
