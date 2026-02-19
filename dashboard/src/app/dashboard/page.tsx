'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { MessageSquare, Bell, Calendar, Sparkles, ChevronRight, Download } from 'lucide-react'
import TopBar from '@/components/TopBar'
import CallButton from '@/components/CallButton'
import LoadingSpinner from '@/components/LoadingSpinner'
import CognitiveScoreBadge from '@/components/CognitiveScoreBadge'
import MoodBadge from '@/components/MoodBadge'
import ConversationCard from '@/components/ConversationCard'
import AlertCard from '@/components/AlertCard'
import {
  getPatient,
  getConversations,
  getAlerts,
  getLatestDigest,
  getInsights,
  acknowledgeAlert,
  getPatientId,
  downloadReport,
} from '@/lib/api'
import type { Patient, Conversation, Alert, WellnessDigest, Insights } from '@/lib/api'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const router = useRouter()
  const [patient, setPatient] = useState<Patient | null>(null)
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [digest, setDigest] = useState<WellnessDigest | null>(null)
  const [insights, setInsights] = useState<Insights | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    async function loadData() {
      try {
        const pid = getPatientId()
        const [p, c, a, d, i] = await Promise.all([
          getPatient(pid),
          getConversations(pid),
          getAlerts(pid),
          getLatestDigest(pid),
          getInsights(pid),
        ])
        setPatient(p)
        setConversations(c)
        setAlerts(a)
        setDigest(d)
        setInsights(i)
      } catch {
        setError('Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const familyId = patient?.family_contacts?.[0]?.id || 'family-member'
  const familyName = patient?.family_contacts?.[0]?.name || 'Family Member'

  const handleAcknowledge = async (id: string) => {
    await acknowledgeAlert(id, familyId)
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, acknowledged: true, acknowledged_by: familyName } : a))
    )
  }

  const handleDownloadReport = async () => {
    if (!patient) return
    setDownloading(true)
    try {
      const blob = await downloadReport(patient.id)
      if (blob) {
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `cognitive-report-${patient.id}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    } catch (e) {
      console.error('Download failed:', e)
    } finally {
      setDownloading(false)
    }
  }

  if (loading) {
    return (
      <>
        <TopBar title="ClaraCare" subtitle="Your loved one’s daily snapshot" />
        <LoadingSpinner />
      </>
    )
  }

  if (error) {
    return (
      <>
        <TopBar title="ClaraCare" subtitle="Your loved one’s daily snapshot" />
        <div className="flex items-center justify-center px-4 py-16">
          <p className="text-sm text-red-500">{error}</p>
        </div>
      </>
    )
  }

  const unacknowledgedAlerts = alerts.filter((a) => !a.acknowledged)
  const recentConversations = conversations.slice(0, 3)
  const displayAlerts = unacknowledgedAlerts.slice(0, 2)
  const daysTracked = conversations.length > 0
    ? Math.ceil(
      (new Date(conversations[0].timestamp).getTime() -
        new Date(conversations[conversations.length - 1].timestamp).getTime()) /
      86400000
    ) + 1
    : 0

  return (
    <>
      <TopBar
        title={patient?.preferred_name ? `${patient.preferred_name}’s Dashboard` : 'ClaraCare'}
        subtitle={patient?.name ? `Caring for ${patient.name}` : 'Today at a glance'}
      />

      <main className="space-y-4 px-4 py-4">
        <section className="rounded-2xl bg-gradient-to-br from-clara-50 to-white p-4 shadow-sm" aria-label="Overview">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium uppercase tracking-wide text-clara-700/70">
                Today’s snapshot
              </p>
              <h1 className="mt-1 text-xl font-semibold text-gray-900">
                Welcome back, {patient?.name.split(' ')[0] || 'Friend'}
              </h1>
              <p className="mt-1 text-[11px] leading-snug text-gray-500">
                See Clara’s latest check-in, mood, and any alerts that may need your attention.
              </p>
            </div>
            <button
              onClick={handleDownloadReport}
              disabled={downloading || !patient}
              className="flex shrink-0 flex-col items-center gap-1 rounded-xl bg-white px-3 py-2 text-[10px] font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 disabled:opacity-60"
              aria-label="Download cognitive report PDF"
            >
              <Download className={`h-4 w-4 ${downloading ? 'animate-bounce' : ''}`} />
              <span>{downloading ? 'Generating…' : 'PDF Report'}</span>
            </button>
          </div>
        </section>

        {/* Call Now Button */}
        {patient && (
          <section aria-label="Call patient">
            <CallButton
              patientId={patient.id}
              patientName={patient.preferred_name || patient.name}
              patientPhone={patient.phone_number}
              className="mt-1"
            />
          </section>
        )}

        {digest && (
          <section className="rounded-2xl bg-white p-4 shadow-sm" aria-label="Wellness Summary">
            <h2 className="mb-3 text-sm font-semibold text-gray-900">Today&apos;s Wellness</h2>
            <div className="flex items-center gap-4">
              <CognitiveScoreBadge
                score={digest.cognitive_score}
                trend={digest.cognitive_trend as 'improving' | 'stable' | 'declining'}
              />
              <div className="min-w-0 flex-1">
                <div className="mb-1 flex items-center gap-2">
                  <MoodBadge mood={digest.overall_mood} size="sm" />
                </div>
                <p className="text-xs text-gray-500">
                  Cognitive score is {digest.cognitive_trend}
                </p>
              </div>
            </div>
            {digest.highlights.length > 0 && (
              <div className="mt-3 border-t border-gray-50 pt-3">
                <p className="mb-2 text-[11px] font-medium uppercase tracking-wide text-gray-400">Highlights</p>
                <ul className="space-y-2">
                  {digest.highlights.slice(0, 3).map((h, i) => {
                    const isWarning = h.startsWith('⚠️')
                    return (
                      <li
                        key={i}
                        className={`flex items-start gap-2 rounded-lg p-2 text-xs ${isWarning
                            ? 'bg-amber-50 text-amber-900'
                            : 'text-gray-600'
                          }`}
                      >
                        {isWarning ? (
                          <span className="shrink-0 text-sm leading-none">⚠️</span>
                        ) : (
                          <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-clara-500" />
                        )}
                        <span>{isWarning ? h.replace(/^⚠️\s*/, '') : h}</span>
                      </li>
                    )
                  })}
                </ul>
              </div>
            )}
            {digest.recommendations && digest.recommendations.length > 0 && (
              <div className="mt-3 border-t border-gray-50 pt-3">
                <p className="mb-2 text-[11px] font-medium uppercase tracking-wide text-gray-400">💡 Suggested Actions</p>
                <ul className="space-y-1.5">
                  {digest.recommendations.slice(0, 2).map((r, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-gray-600">
                      <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-green-400" />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        <section className="rounded-2xl bg-white p-3 shadow-sm" aria-label="Quick Stats">
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded-xl bg-gray-50 p-3 text-center">
            <MessageSquare className="mx-auto mb-1 h-5 w-5 text-clara-500" />
            <p className="text-lg font-bold text-gray-900">{conversations.length}</p>
            <p className="text-[10px] text-gray-400">Conversations</p>
          </div>
            <div className="rounded-xl bg-gray-50 p-3 text-center">
            <Bell className="mx-auto mb-1 h-5 w-5 text-red-400" />
            <p className="text-lg font-bold text-gray-900">{unacknowledgedAlerts.length}</p>
            <p className="text-[10px] text-gray-400">Active Alerts</p>
          </div>
            <div className="rounded-xl bg-gray-50 p-3 text-center">
            <Calendar className="mx-auto mb-1 h-5 w-5 text-green-500" />
            <p className="text-lg font-bold text-gray-900">{daysTracked}</p>
            <p className="text-[10px] text-gray-400">Days Tracked</p>
          </div>
          </div>
        </section>

        <section aria-label="Recent Conversations" className="rounded-2xl bg-white p-4 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-900">Recent Conversations</h2>
            <Link
              href="/dashboard/history"
              className="flex items-center gap-0.5 text-xs font-medium text-clara-600"
            >
              View All
              <ChevronRight className="h-3.5 w-3.5" />
            </Link>
          </div>
          <div className="space-y-2">
            {recentConversations.map((c) => (
              <ConversationCard
                key={c.id}
                conversation={c}
                onClick={() => router.push(`/dashboard/history/${c.id}`)}
              />
            ))}
          </div>
        </section>

        {displayAlerts.length > 0 && (
          <section aria-label="Active Alerts" className="rounded-2xl bg-white p-4 shadow-sm">
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-900">Active Alerts</h2>
              <Link
                href="/dashboard/alerts"
                className="flex items-center gap-0.5 text-xs font-medium text-clara-600"
              >
                View All
                <ChevronRight className="h-3.5 w-3.5" />
              </Link>
            </div>
            <div className="space-y-2">
              {displayAlerts.map((a) => (
                <AlertCard key={a.id} alert={a} onAcknowledge={handleAcknowledge} />
              ))}
            </div>
          </section>
        )}

        {insights?.nostalgia_effectiveness && (
          <section
            className="rounded-2xl bg-gradient-to-br from-purple-50 to-clara-50 p-4 shadow-sm"
            aria-label="Nostalgia Insights"
          >
            <div className="mb-2 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-500" />
              <h2 className="text-sm font-semibold text-gray-900">Nostalgia Effectiveness</h2>
            </div>
            <p className="mb-3 text-xs text-gray-600">
              Conversations with nostalgia engagement show measurable cognitive improvement.
            </p>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-white/70 p-3 text-center">
                <p className="text-lg font-bold text-green-600">
                  +{insights.nostalgia_effectiveness.improvement_pct.vocabulary.toFixed(1)}%
                </p>
                <p className="text-[10px] text-gray-500">Vocabulary</p>
              </div>
              <div className="rounded-lg bg-white/70 p-3 text-center">
                <p className="text-lg font-bold text-green-600">
                  +{insights.nostalgia_effectiveness.improvement_pct.coherence.toFixed(1)}%
                </p>
                <p className="text-[10px] text-gray-500">Coherence</p>
              </div>
            </div>
          </section>
        )}
      </main>
    </>
  )
}

