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
  Save,
  Check,
  Loader2,
} from 'lucide-react'
import TopBar from '@/components/TopBar'
import LoadingSpinner from '@/components/LoadingSpinner'
import { getPatient, updatePatient, getPatientId } from '@/lib/api'
import type { Patient } from '@/lib/api'
import { cn } from '@/lib/utils'

const TIME_OPTIONS = [
  '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM', '10:30 AM',
  '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '1:00 PM', '1:30 PM',
  '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM',
  '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM',
  '8:00 PM',
]

const TIMEZONE_OPTIONS = [
  { value: 'America/Los_Angeles', label: 'Pacific (PT)' },
  { value: 'America/Denver', label: 'Mountain (MT)' },
  { value: 'America/Chicago', label: 'Central (CT)' },
  { value: 'America/New_York', label: 'Eastern (ET)' },
]

export default function SettingsPage() {
  const [patient, setPatient] = useState<Patient | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Editable fields
  const [phoneNumber, setPhoneNumber] = useState('')
  const [callTime, setCallTime] = useState('10:00 AM')
  const [callTimezone, setCallTimezone] = useState('America/Los_Angeles')
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const data = await getPatient(getPatientId())
        if (!data) {
          setError('Patient data not found')
          return
        }
        setPatient(data)
        setPhoneNumber(data.phone_number || '')
        setCallTime(data.call_schedule?.preferred_time || '10:00 AM')
        setCallTimezone(data.call_schedule?.timezone || 'America/Los_Angeles')
      } catch {
        setError('Failed to load settings')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleSave = async () => {
    if (!patient) return
    setSaving(true)
    try {
      await updatePatient(patient.id, {
        phone_number: phoneNumber,
        call_schedule: {
          preferred_time: callTime,
          timezone: callTimezone,
        },
      } as Partial<Patient>)
      setSaved(true)
      setHasChanges(false)
      setTimeout(() => setSaved(false), 3000)
    } catch {
      setError('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const handlePhoneChange = (value: string) => {
    setPhoneNumber(value)
    setHasChanges(true)
  }

  const handleTimeChange = (value: string) => {
    setCallTime(value)
    setHasChanges(true)
  }

  const handleTimezoneChange = (value: string) => {
    setCallTimezone(value)
    setHasChanges(true)
  }

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
        {/* Phone Number — Editable */}
        <section className="rounded-xl bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center gap-2">
            <Phone className="h-4 w-4 text-green-600" />
            <h2 className="text-sm font-semibold text-gray-900">Phone Number</h2>
          </div>
          <p className="mb-2 text-[11px] text-gray-400">
            The phone number Clara will call for daily check-ins
          </p>
          <input
            type="tel"
            value={phoneNumber}
            onChange={(e) => handlePhoneChange(e.target.value)}
            placeholder="+1 (555) 123-4567"
            className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400 outline-none transition-colors focus:border-clara-500 focus:bg-white focus:ring-2 focus:ring-clara-500/20"
          />
          <p className="mt-1.5 text-[10px] text-gray-400">
            Use E.164 format (e.g., +14155551234)
          </p>
        </section>

        {/* Call Schedule — Editable */}
        <section className="rounded-xl bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center gap-2">
            <Clock className="h-4 w-4 text-clara-600" />
            <h2 className="text-sm font-semibold text-gray-900">Call Schedule</h2>
          </div>
          <p className="mb-3 text-[11px] text-gray-400">
            When Clara should call for the daily check-in
          </p>
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-[11px] font-medium uppercase tracking-wide text-gray-400">
                Preferred Time
              </label>
              <select
                value={callTime}
                onChange={(e) => handleTimeChange(e.target.value)}
                className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm text-gray-900 outline-none transition-colors focus:border-clara-500 focus:bg-white focus:ring-2 focus:ring-clara-500/20"
              >
                {TIME_OPTIONS.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-[11px] font-medium uppercase tracking-wide text-gray-400">
                Timezone
              </label>
              <select
                value={callTimezone}
                onChange={(e) => handleTimezoneChange(e.target.value)}
                className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm text-gray-900 outline-none transition-colors focus:border-clara-500 focus:bg-white focus:ring-2 focus:ring-clara-500/20"
              >
                {TIMEZONE_OPTIONS.map((tz) => (
                  <option key={tz.value} value={tz.value}>{tz.label}</option>
                ))}
              </select>
            </div>
          </div>
        </section>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={!hasChanges || saving}
          className={cn(
            'flex w-full items-center justify-center gap-2 rounded-xl px-6 py-3.5 text-sm font-semibold text-white shadow-sm transition-all',
            saved
              ? 'bg-green-500'
              : hasChanges
                ? 'bg-clara-600 active:scale-[0.98] hover:bg-clara-700'
                : 'bg-gray-300 cursor-not-allowed'
          )}
          type="button"
        >
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : saved ? (
            <>
              <Check className="h-4 w-4" />
              Saved!
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              Save Changes
            </>
          )}
        </button>

        {/* Patient Profile — Read-Only */}
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

        {/* Medications — Read-Only */}
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

        {/* Preferences — Read-Only */}
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

        {/* Family Contacts — Read-Only */}
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

        {/* Cognitive Thresholds — Read-Only */}
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
