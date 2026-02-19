'use client'

import { useState, useEffect } from 'react'
import { Sparkles, Plus, X, Save } from 'lucide-react'
import TopBar from '@/components/TopBar'
import { SkeletonLine } from '@/components/Skeleton'
import ErrorState from '@/components/ErrorState'
import { getPatient, getInsights, getPatientId, updatePatient } from '@/lib/api'
import type { Patient, Insights } from '@/lib/api'

function EditableTagList({
  tags,
  onChange,
  placeholder = 'Add item',
  maxTags = 10,
}: {
  tags: string[]
  onChange: (tags: string[]) => void
  placeholder?: string
  maxTags?: number
}) {
  const [input, setInput] = useState('')

  const add = () => {
    const v = input.trim()
    if (!v || tags.length >= maxTags || tags.includes(v)) return
    onChange([...tags, v])
    setInput('')
  }

  const remove = (i: number) => {
    onChange(tags.filter((_, idx) => idx !== i))
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1.5">
        {tags.map((tag, i) => (
          <span
            key={`${tag}-${i}`}
            className="inline-flex items-center gap-1 rounded-full bg-clara-100 px-3 py-1 text-xs font-medium text-clara-700"
          >
            {tag}
            <button
              type="button"
              onClick={() => remove(i)}
              className="rounded-full p-0.5 transition-colors hover:bg-clara-200"
              aria-label={`Remove ${tag}`}
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
      </div>
      {tags.length < maxTags && (
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), add())}
            placeholder={placeholder}
            className="min-h-[44px] flex-1 rounded-lg border border-gray-200 px-3 py-2 text-body focus:border-clara-500 focus:outline-none focus:ring-2 focus:ring-clara-500 focus:ring-offset-0"
          />
          <button
            type="button"
            onClick={add}
            className="flex h-11 min-h-[44px] w-11 shrink-0 items-center justify-center rounded-lg border border-gray-200 bg-clara-100 text-clara-600 transition-colors hover:bg-clara-200 focus:outline-none focus:ring-2 focus:ring-clara-500 focus:ring-offset-2"
            aria-label="Add"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  )
}

export default function NostalgiaPage() {
  const [patient, setPatient] = useState<Patient | null>(null)
  const [insights, setInsights] = useState<Insights | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  const [favoriteTopics, setFavoriteTopics] = useState<string[]>([])
  const [interests, setInterests] = useState<string[]>([])
  const [topicsToAvoid, setTopicsToAvoid] = useState<string[]>([])

  useEffect(() => {
    async function load() {
      try {
        const pid = getPatientId()
        const [p, i] = await Promise.all([getPatient(pid), getInsights(pid)])
        if (!p) {
          setError('Patient not found')
          return
        }
        setPatient(p)
        setInsights(i ?? null)
        setFavoriteTopics(p.preferences.favorite_topics ?? [])
        setInterests(p.preferences.interests ?? [])
        setTopicsToAvoid(p.preferences.topics_to_avoid ?? [])
      } catch {
        setError('Failed to load nostalgia preferences')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleSave = async () => {
    if (!patient) return
    setSaving(true)
    setSaveSuccess(false)
    try {
      const ok = await updatePatient(patient.id, {
        preferences: {
          ...patient.preferences,
          favorite_topics: favoriteTopics,
          interests,
          topics_to_avoid: topicsToAvoid,
        },
      })
      if (ok) {
        setSaveSuccess(true)
        setTimeout(() => setSaveSuccess(false), 2000)
      }
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <>
        <TopBar title="Nostalgia" subtitle="Tune what Clara talks about" />
        <main className="space-y-6 px-5 py-6" aria-busy>
          {[1, 2, 3, 4].map((i) => (
            <section
              key={i}
              className="rounded-xl border border-gray-100 bg-white p-5 shadow-card"
            >
              <SkeletonLine className="mb-4 h-5 w-36" />
              <div className="space-y-2">
                <SkeletonLine className="w-full" />
                <SkeletonLine className="w-2/3" />
              </div>
            </section>
          ))}
        </main>
      </>
    )
  }

  if (error || !patient) {
    return (
      <>
        <TopBar title="Nostalgia" subtitle="Tune what Clara talks about" />
        <main className="px-5 py-6">
          <ErrorState
            message={error || 'No data available'}
            onRetry={() => {
              setError(null)
              setLoading(true)
              const pid = getPatientId()
              Promise.all([getPatient(pid), getInsights(pid)])
                .then(([p, i]) => {
                  if (!p) setError('Patient not found')
                  else {
                    setPatient(p)
                    setInsights(i ?? null)
                    setFavoriteTopics(p.preferences.favorite_topics ?? [])
                    setInterests(p.preferences.interests ?? [])
                    setTopicsToAvoid(p.preferences.topics_to_avoid ?? [])
                  }
                })
                .catch(() => setError('Failed to load nostalgia preferences'))
                .finally(() => setLoading(false))
            }}
          />
        </main>
      </>
    )
  }

  const birthYear = patient.birth_year ?? 1950
  const goldenStart = birthYear + 15
  const goldenEnd = birthYear + 25

  return (
    <>
      <TopBar title="Nostalgia" subtitle="Help Clara pick stories that land" />

      <main className="space-y-6 px-5 py-6">
        <section className="rounded-xl border border-gray-100 bg-gradient-to-br from-purple-50/80 to-clara-50/80 p-5 shadow-card">
          <div className="mb-3 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-purple-500" />
            <h2 className="font-heading text-heading text-gray-900">Golden Years</h2>
          </div>
          <p className="text-body text-gray-600">
            {goldenStart}–{goldenEnd} — {patient.preferred_name}&apos;s peak memory years. Nostalgia
            content from this era tends to resonate most.
          </p>
        </section>

        <section className="rounded-xl border border-gray-100 bg-white p-5 shadow-card">
          <h2 className="mb-4 font-heading text-heading text-gray-900">Favorite Topics</h2>
          <EditableTagList
            tags={favoriteTopics}
            onChange={setFavoriteTopics}
            placeholder="e.g. gardening, 1960s music"
          />
        </section>

        <section className="rounded-xl border border-gray-100 bg-white p-5 shadow-card">
          <h2 className="mb-4 font-heading text-heading text-gray-900">Music &amp; Interests</h2>
          <EditableTagList
            tags={interests}
            onChange={setInterests}
            placeholder="e.g. music, family history"
          />
        </section>

        <section className="rounded-xl border border-gray-100 bg-white p-5 shadow-card">
          <h2 className="mb-4 font-heading text-heading text-gray-900">Topics to Avoid</h2>
          <EditableTagList
            tags={topicsToAvoid}
            onChange={setTopicsToAvoid}
            placeholder="e.g. politics, health scares"
          />
        </section>

        {insights?.nostalgia_effectiveness && (
          <section className="rounded-xl border border-gray-100 bg-white p-5 shadow-card">
            <h2 className="mb-3 font-heading text-heading text-gray-900">Nostalgia Effectiveness</h2>
            <p className="mb-4 text-body text-gray-500">
              Conversations with nostalgia engagement show measurable cognitive improvement.
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border border-green-100 bg-green-50 p-4 text-center">
                <p className="text-heading-lg font-bold text-green-600">
                  +{insights.nostalgia_effectiveness.improvement_pct.vocabulary.toFixed(1)}%
                </p>
                <p className="text-caption text-gray-500">Vocabulary</p>
              </div>
              <div className="rounded-lg border border-green-100 bg-green-50 p-4 text-center">
                <p className="text-heading-lg font-bold text-green-600">
                  +{insights.nostalgia_effectiveness.improvement_pct.coherence.toFixed(1)}%
                </p>
                <p className="text-caption text-gray-500">Coherence</p>
              </div>
            </div>
          </section>
        )}

        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            className="inline-flex min-h-[44px] flex-1 items-center justify-center gap-2 rounded-xl bg-clara-600 px-5 py-3 text-body font-medium text-white transition-colors duration-150 hover:bg-clara-700 active:bg-clara-800 focus:outline-none focus:ring-2 focus:ring-clara-500 focus:ring-offset-2 disabled:opacity-70"
          >
            <Save className="h-4 w-4" />
            {saving ? 'Saving…' : 'Save Preferences'}
          </button>
          {saveSuccess && (
            <span className="text-body font-medium text-green-600">Saved</span>
          )}
        </div>
      </main>
    </>
  )
}
