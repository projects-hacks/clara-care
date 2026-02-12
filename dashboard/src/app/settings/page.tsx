'use client'

import { useState, useEffect } from 'react'
import {
  User,
  Pill,
  Heart,
  Clock,
  Users,
  Brain,
  Mail,
  Phone,
} from 'lucide-react'
import TopBar from '@/components/TopBar'
import LoadingSpinner from '@/components/LoadingSpinner'
import { getPatient, getPatientId } from '@/lib/api'
import type { Patient } from '@/lib/api'

export default function SettingsPage() {
  const [patient, setPatient] = useState<Patient | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const data = await getPatient(getPatientId())
        if (!data) {
          setError('Patient data not found')
          return
        }
        setPatient(data)
      } catch {
        setError('Failed to load settings')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <>
        <TopBar title="Settings" />
        <LoadingSpinner />
      </>
    )
  }

  if (error || !patient) {
    return (
      <>
        <TopBar title="Settings" />
        <div className="flex items-center justify-center px-4 py-16">
          <p className="text-sm text-red-500">{error || 'No data available'}</p>
        </div>
      </>
    )
  }

  return (
    <>
      <TopBar title="Settings" />

      <main className="space-y-4 px-4 py-4">
        <section className="rounded-xl bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center gap-2">
            <User className="h-4 w-4 text-clara-600" />
            <h2 className="text-sm font-semibold text-gray-900">Patient Profile</h2>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Name</span>
              <span className="font-medium text-gray-900">{patient.name}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Preferred Name</span>
              <span className="font-medium text-gray-900">{patient.preferred_name}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Age</span>
              <span className="font-medium text-gray-900">{patient.age}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Location</span>
              <span className="font-medium text-gray-900">
                {patient.location.city}, {patient.location.state}
              </span>
            </div>
          </div>
        </section>

        <section className="rounded-xl bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center gap-2">
            <Pill className="h-4 w-4 text-clara-600" />
            <h2 className="text-sm font-semibold text-gray-900">Medications</h2>
          </div>
          <div className="space-y-3">
            {patient.medications.map((med, i) => (
              <div key={i} className="rounded-lg bg-gray-50 p-3">
                <p className="text-sm font-medium text-gray-900">{med.name}</p>
                <p className="text-xs text-gray-500">
                  {med.dosage} · {med.schedule}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-xl bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center gap-2">
            <Heart className="h-4 w-4 text-clara-600" />
            <h2 className="text-sm font-semibold text-gray-900">Preferences</h2>
          </div>
          <div className="mb-3">
            <p className="mb-1.5 text-[11px] font-medium uppercase tracking-wide text-gray-400">
              Favorite Topics
            </p>
            <div className="flex flex-wrap gap-1.5">
              {patient.preferences.favorite_topics.map((topic) => (
                <span
                  key={topic}
                  className="rounded-full bg-clara-50 px-3 py-1 text-xs font-medium text-clara-700"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
          <div>
            <p className="mb-1 text-[11px] font-medium uppercase tracking-wide text-gray-400">
              Communication Style
            </p>
            <p className="text-sm capitalize text-gray-700">
              {patient.preferences.communication_style}
            </p>
          </div>
          {patient.preferences.topics_to_avoid && patient.preferences.topics_to_avoid.length > 0 && (
            <div className="mt-3">
              <p className="mb-1.5 text-[11px] font-medium uppercase tracking-wide text-gray-400">
                Topics to Avoid
              </p>
              <div className="flex flex-wrap gap-1.5">
                {patient.preferences.topics_to_avoid.map((topic) => (
                  <span
                    key={topic}
                    className="rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-600"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}
        </section>

        {patient.call_schedule && (
          <section className="rounded-xl bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <Clock className="h-4 w-4 text-clara-600" />
              <h2 className="text-sm font-semibold text-gray-900">Call Schedule</h2>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Preferred Time</span>
                <span className="font-medium text-gray-900">{patient.call_schedule.preferred_time}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Timezone</span>
                <span className="font-medium text-gray-900">{patient.call_schedule.timezone}</span>
              </div>
            </div>
          </section>
        )}

        {patient.family_contacts && patient.family_contacts.length > 0 && (
          <section className="rounded-xl bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              <Users className="h-4 w-4 text-clara-600" />
              <h2 className="text-sm font-semibold text-gray-900">Family Contacts</h2>
            </div>
            <div className="space-y-3">
              {patient.family_contacts.map((contact) => (
                <div key={contact.id} className="rounded-lg bg-gray-50 p-3">
                  <div className="mb-1 flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900">{contact.name}</p>
                    <span className="text-[11px] text-gray-400">{contact.relationship}</span>
                  </div>
                  <div className="space-y-0.5 text-xs text-gray-500">
                    <p className="flex items-center gap-1">
                      <Mail className="h-3 w-3" />
                      {contact.email}
                    </p>
                    <p className="flex items-center gap-1">
                      <Phone className="h-3 w-3" />
                      {contact.phone}
                    </p>
                  </div>
                  <div className="mt-2 flex gap-2">
                    {contact.notification_preferences.daily_digest && (
                      <span className="rounded-full bg-green-50 px-2 py-0.5 text-[10px] font-medium text-green-700">
                        Daily Digest
                      </span>
                    )}
                    {contact.notification_preferences.instant_alerts && (
                      <span className="rounded-full bg-blue-50 px-2 py-0.5 text-[10px] font-medium text-blue-700">
                        Instant Alerts
                      </span>
                    )}
                    {contact.notification_preferences.weekly_report && (
                      <span className="rounded-full bg-purple-50 px-2 py-0.5 text-[10px] font-medium text-purple-700">
                        Weekly Report
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="rounded-xl bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center gap-2">
            <Brain className="h-4 w-4 text-clara-600" />
            <h2 className="text-sm font-semibold text-gray-900">Cognitive Thresholds</h2>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Deviation Threshold</span>
              <span className="font-medium text-gray-900">
                {(patient.cognitive_thresholds.deviation_threshold * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Consecutive Trigger</span>
              <span className="font-medium text-gray-900">
                {patient.cognitive_thresholds.consecutive_trigger} sessions
              </span>
            </div>
          </div>
        </section>
      </main>
    </>
  )
}
