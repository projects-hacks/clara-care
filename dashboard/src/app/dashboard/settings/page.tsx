'use client'

import { useState, useEffect, useCallback } from 'react'
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
  Plus,
  X,
  Trash2,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
} from 'lucide-react'
import TopBar from '@/components/TopBar'
import LoadingSpinner from '@/components/LoadingSpinner'
import { getPatient, updatePatient, getPatientId } from '@/lib/api'
import type { Patient } from '@/lib/api'
import { cn } from '@/lib/utils'

// ── Constants ───────────────────────────────────────────────────────

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

const TOPIC_SUGGESTIONS = [
  'gardening', 'music', 'cooking', 'family', 'travel', 'pets',
  'books', 'movies', 'sports', 'history', 'art', 'nature',
  'photography', 'crafts', 'puzzles', 'baking',
]

const AVOID_SUGGESTIONS = [
  'politics', 'death', 'health scares', 'finances', 'loneliness',
  'current events', 'religion', 'conflict',
]

const COMM_STYLES = [
  'Warm and Patient',
  'Direct and Clear',
  'Gentle and Encouraging',
  'Cheerful and Energetic',
]

const MED_SUGGESTIONS = [
  'Lisinopril', 'Metformin', 'Amlodipine', 'Vitamin D',
  'Aspirin', 'Donepezil', 'Levothyroxine', 'Omeprazole',
  'Atorvastatin', 'Metoprolol',
]

const SCHEDULE_PRESETS = [
  'Morning', 'Afternoon', 'Evening', 'Bedtime',
  'With meals', 'Twice daily', 'Every 8 hours',
]

const RELATIONSHIP_OPTIONS = [
  'Daughter', 'Son', 'Spouse', 'Sibling',
  'Grandchild', 'Friend', 'Caretaker', 'Other',
]

// ── Input CSS helper ────────────────────────────────────────────────

const inputCls =
  'w-full rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400 outline-none transition-colors focus:border-clara-500 focus:bg-white focus:ring-2 focus:ring-clara-500/20'

// ── Tag Input Component ─────────────────────────────────────────────

function TagInput({
  tags,
  onChange,
  suggestions,
  placeholder = 'Type and press Enter…',
  tagColor = 'bg-clara-50 text-clara-700',
}: {
  tags: string[]
  onChange: (tags: string[]) => void
  suggestions: string[]
  placeholder?: string
  tagColor?: string
}) {
  const [input, setInput] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)

  const filtered = suggestions.filter(
    (s) => !tags.includes(s) && s.toLowerCase().includes(input.toLowerCase())
  )

  const addTag = (tag: string) => {
    const trimmed = tag.trim().toLowerCase()
    if (trimmed && !tags.includes(trimmed)) {
      onChange([...tags, trimmed])
    }
    setInput('')
    setShowSuggestions(false)
  }

  const removeTag = (tag: string) => {
    onChange(tags.filter((t) => t !== tag))
  }

  return (
    <div className="relative">
      <div className="flex flex-wrap gap-1.5 mb-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className={cn('inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium', tagColor)}
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(tag)}
              className="ml-0.5 rounded-full p-0.5 transition-colors hover:bg-black/10"
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => {
          setInput(e.target.value)
          setShowSuggestions(true)
        }}
        onFocus={() => setShowSuggestions(true)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault()
            addTag(input)
          }
        }}
        placeholder={placeholder}
        className={inputCls}
      />
      {showSuggestions && filtered.length > 0 && (
        <div className="absolute z-10 mt-1 max-h-32 w-full overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg">
          {filtered.map((s) => (
            <button
              key={s}
              type="button"
              onMouseDown={(e) => {
                e.preventDefault()
                addTag(s)
              }}
              className="block w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-clara-50"
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Collapsible Section ─────────────────────────────────────────────

function Section({
  icon: Icon,
  title,
  iconColor = 'text-clara-600',
  children,
  defaultOpen = false,
}: {
  icon: React.ComponentType<{ className?: string }>
  title: string
  iconColor?: string
  children: React.ReactNode
  defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <section className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between p-4 transition-colors hover:bg-gray-50 active:bg-gray-50"
      >
        <div className="flex items-center gap-2">
          <Icon className={cn('h-4 w-4', iconColor)} />
          <h2 className="text-sm font-semibold text-gray-900">{title}</h2>
        </div>
        {open ? (
          <ChevronUp className="h-4 w-4 text-gray-400" />
        ) : (
          <ChevronDown className="h-4 w-4 text-gray-400" />
        )}
      </button>
      {open && <div className="border-t border-gray-100 p-4">{children}</div>}
    </section>
  )
}

// ── Medication type ─────────────────────────────────────────────────

interface Medication {
  name: string
  dosage: string
  schedule: string
}

interface FamilyContact {
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
}

// ── Main Settings Page ──────────────────────────────────────────────

export default function SettingsPage() {
  const [patient, setPatient] = useState<Patient | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasChanges, setHasChanges] = useState(false)

  // ─ Editable fields ─────────────────────────────
  const [phoneNumber, setPhoneNumber] = useState('')
  const [callTime, setCallTime] = useState('10:00 AM')
  const [callTimezone, setCallTimezone] = useState('America/Los_Angeles')

  // Patient profile
  const [patientName, setPatientName] = useState('')
  const [preferredName, setPreferredName] = useState('')
  const [patientAge, setPatientAge] = useState(0)

  // Medications
  const [medications, setMedications] = useState<Medication[]>([])
  const [showAddMed, setShowAddMed] = useState(false)
  const [newMedName, setNewMedName] = useState('')
  const [newMedDosage, setNewMedDosage] = useState('')
  const [newMedSchedule, setNewMedSchedule] = useState('')
  const [medSuggestions, setMedSuggestions] = useState<string[]>([])

  // Preferences
  const [favoriteTopics, setFavoriteTopics] = useState<string[]>([])
  const [commStyle, setCommStyle] = useState('')
  const [interests, setInterests] = useState<string[]>([])
  const [topicsToAvoid, setTopicsToAvoid] = useState<string[]>([])

  // Family contacts
  const [familyContacts, setFamilyContacts] = useState<FamilyContact[]>([])
  const [showAddContact, setShowAddContact] = useState(false)
  const [newContact, setNewContact] = useState<FamilyContact>({
    id: '',
    name: '',
    email: '',
    phone: '',
    relationship: 'Daughter',
    notification_preferences: { daily_digest: true, instant_alerts: true, weekly_report: false },
  })

  // Cognitive thresholds
  const [deviationThreshold, setDeviationThreshold] = useState(0.2)
  const [consecutiveTrigger, setConsecutiveTrigger] = useState(3)

  // ─ Load ──────────────────────────────────────────
  useEffect(() => {
    async function load() {
      try {
        const data = await getPatient(getPatientId())
        if (!data) {
          setError('Patient data not found')
          return
        }
        setPatient(data)

        // Phone & schedule
        setPhoneNumber(data.phone_number || '')
        setCallTime(data.call_schedule?.preferred_time || '10:00 AM')
        setCallTimezone(data.call_schedule?.timezone || 'America/Los_Angeles')

        // Profile
        setPatientName(data.name || '')
        setPreferredName(data.preferred_name || '')
        setPatientAge(data.age || 0)

        // Medications
        setMedications(data.medications || [])

        // Preferences
        setFavoriteTopics(data.preferences?.favorite_topics || [])
        setCommStyle(data.preferences?.communication_style || '')
        setInterests(data.preferences?.interests || [])
        setTopicsToAvoid(data.preferences?.topics_to_avoid || [])

        // Family contacts
        setFamilyContacts(data.family_contacts || [])

        // Cognitive thresholds
        setDeviationThreshold(data.cognitive_thresholds?.deviation_threshold ?? 0.2)
        setConsecutiveTrigger(data.cognitive_thresholds?.consecutive_trigger ?? 3)
      } catch {
        setError('Failed to load settings')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // ─ Change tracker ────────────────────────────────
  const markChanged = useCallback(() => setHasChanges(true), [])

  // ─ Save ──────────────────────────────────────────
  const handleSave = async () => {
    if (!patient) return
    setSaving(true)
    setError(null)
    try {
      await updatePatient(patient.id, {
        name: patientName,
        preferred_name: preferredName,
        age: patientAge,
        phone_number: phoneNumber,
        call_schedule: {
          preferred_time: callTime,
          timezone: callTimezone,
        },
        medications,
        preferences: {
          favorite_topics: favoriteTopics,
          communication_style: commStyle,
          interests,
          topics_to_avoid: topicsToAvoid,
        },
        family_contacts: familyContacts,
        cognitive_thresholds: {
          deviation_threshold: deviationThreshold,
          consecutive_trigger: consecutiveTrigger,
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

  // ─ Medication helpers ────────────────────────────
  const addMedication = () => {
    if (!newMedName.trim()) return
    setMedications((prev) => [
      ...prev,
      { name: newMedName.trim(), dosage: newMedDosage.trim(), schedule: newMedSchedule.trim() },
    ])
    setNewMedName('')
    setNewMedDosage('')
    setNewMedSchedule('')
    setShowAddMed(false)
    setMedSuggestions([])
    markChanged()
  }

  const removeMedication = (index: number) => {
    setMedications((prev) => prev.filter((_, i) => i !== index))
    markChanged()
  }

  const updateMedication = (index: number, field: keyof Medication, value: string) => {
    setMedications((prev) =>
      prev.map((m, i) => (i === index ? { ...m, [field]: value } : m))
    )
    markChanged()
  }

  // ─ Contact helpers ───────────────────────────────
  const addContact = () => {
    if (!newContact.name.trim()) return
    setFamilyContacts((prev) => [
      ...prev,
      { ...newContact, id: `contact-${Date.now()}` },
    ])
    setNewContact({
      id: '',
      name: '',
      email: '',
      phone: '',
      relationship: 'Daughter',
      notification_preferences: { daily_digest: true, instant_alerts: true, weekly_report: false },
    })
    setShowAddContact(false)
    markChanged()
  }

  const removeContact = (index: number) => {
    setFamilyContacts((prev) => prev.filter((_, i) => i !== index))
    markChanged()
  }

  const updateContact = (index: number, field: string, value: string | boolean) => {
    setFamilyContacts((prev) =>
      prev.map((c, i) => {
        if (i !== index) return c
        if (field.startsWith('notif_')) {
          const key = field.replace('notif_', '') as keyof FamilyContact['notification_preferences']
          return {
            ...c,
            notification_preferences: { ...c.notification_preferences, [key]: value },
          }
        }
        return { ...c, [field]: value }
      })
    )
    markChanged()
  }

  // ─ Med name autocomplete ─────────────────────────
  const handleMedNameChange = (value: string) => {
    setNewMedName(value)
    if (value.length > 0) {
      setMedSuggestions(
        MED_SUGGESTIONS.filter(
          (s) => s.toLowerCase().includes(value.toLowerCase()) && !medications.some((m) => m.name === s)
        )
      )
    } else {
      setMedSuggestions([])
    }
  }

  // ─ Render ────────────────────────────────────────
  if (loading) {
    return (
      <>
        <TopBar title="Settings" subtitle="Fine-tune calls, contacts, and alerts" />
        <LoadingSpinner />
      </>
    )
  }

  if (error && !patient) {
    return (
      <>
        <TopBar title="Settings" subtitle="Fine-tune calls, contacts, and alerts" />
        <div className="flex items-center justify-center px-4 py-16">
          <p className="text-sm text-red-500">{error}</p>
        </div>
      </>
    )
  }

  return (
    <>
      <TopBar
        title="Settings"
        subtitle="Update how and when Clara reaches your loved one"
      />

      <main className="space-y-3 px-4 py-4">
        <section className="rounded-2xl bg-gradient-to-br from-clara-50 to-white p-4 shadow-sm" aria-label="Settings overview">
          <h2 className="text-sm font-semibold text-gray-900">Personalize Clara for your family</h2>
          <p className="mt-1 text-[11px] leading-snug text-gray-600">
            Adjust call times, phone numbers, medications, and who should be notified when Clara detects something important.
          </p>
        </section>
        {/* ── Error Banner ────────────────────── */}
        {error && (
          <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-600">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        {/* ── Phone Number ────────────────────── */}
        <Section icon={Phone} title="Phone Number" iconColor="text-green-600" defaultOpen>
          <p className="mb-2 text-[11px] text-gray-400">
            The phone number Clara will call for daily check-ins
          </p>
          <input
            type="tel"
            value={phoneNumber}
            onChange={(e) => { setPhoneNumber(e.target.value); markChanged() }}
            placeholder="+1 (555) 123-4567"
            className={inputCls}
          />
          <p className="mt-1.5 text-[10px] text-gray-400">
            Use E.164 format (e.g., +14155551234)
          </p>
        </Section>

        {/* ── Call Schedule ───────────────────── */}
        <Section icon={Clock} title="Call Schedule" defaultOpen>
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
                onChange={(e) => { setCallTime(e.target.value); markChanged() }}
                className={inputCls}
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
                onChange={(e) => { setCallTimezone(e.target.value); markChanged() }}
                className={inputCls}
              >
                {TIMEZONE_OPTIONS.map((tz) => (
                  <option key={tz.value} value={tz.value}>{tz.label}</option>
                ))}
              </select>
            </div>
          </div>
        </Section>

        {/* ── Patient Profile ─────────────────── */}
        <Section icon={User} title="Patient Profile">
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-[11px] font-medium uppercase tracking-wide text-gray-400">
                Full Name
              </label>
              <input
                type="text"
                value={patientName}
                onChange={(e) => { setPatientName(e.target.value); markChanged() }}
                className={inputCls}
              />
            </div>
            <div>
              <label className="mb-1 block text-[11px] font-medium uppercase tracking-wide text-gray-400">
                Preferred Name
              </label>
              <input
                type="text"
                value={preferredName}
                onChange={(e) => { setPreferredName(e.target.value); markChanged() }}
                placeholder="What Clara calls the patient"
                className={inputCls}
              />
            </div>
            <div>
              <label className="mb-1 block text-[11px] font-medium uppercase tracking-wide text-gray-400">
                Age
              </label>
              <input
                type="number"
                value={patientAge || ''}
                onChange={(e) => { setPatientAge(parseInt(e.target.value) || 0); markChanged() }}
                min={0}
                max={150}
                className={inputCls}
              />
            </div>
            {patient?.location && (
              <div className="flex justify-between text-sm rounded-lg bg-gray-50 p-3">
                <span className="text-gray-400">Location</span>
                <span className="font-medium text-gray-900">
                  {patient.location.city}, {patient.location.state}
                </span>
              </div>
            )}
          </div>
        </Section>

        {/* ── Medications ─────────────────────── */}
        <Section icon={Pill} title="Medications">
          <div className="space-y-2">
            {medications.map((med, i) => (
              <div key={i} className="rounded-lg bg-gray-50 p-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <input
                      type="text"
                      value={med.name}
                      onChange={(e) => updateMedication(i, 'name', e.target.value)}
                      className="w-full bg-transparent text-sm font-medium text-gray-900 outline-none focus:bg-white focus:rounded focus:px-2 focus:py-1 focus:border focus:border-clara-300 transition-all"
                      placeholder="Medication name"
                    />
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={med.dosage}
                        onChange={(e) => updateMedication(i, 'dosage', e.target.value)}
                        className="w-1/2 bg-transparent text-xs text-gray-500 outline-none focus:bg-white focus:rounded focus:px-2 focus:py-1 focus:border focus:border-clara-300 transition-all"
                        placeholder="Dosage (e.g., 10mg)"
                      />
                      <input
                        type="text"
                        value={med.schedule}
                        onChange={(e) => updateMedication(i, 'schedule', e.target.value)}
                        className="w-1/2 bg-transparent text-xs text-gray-500 outline-none focus:bg-white focus:rounded focus:px-2 focus:py-1 focus:border focus:border-clara-300 transition-all"
                        placeholder="Schedule"
                      />
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeMedication(i)}
                    className="ml-2 rounded-full p-1.5 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            ))}

            {showAddMed ? (
              <div className="rounded-lg border-2 border-dashed border-clara-200 bg-clara-50/50 p-3 space-y-2">
                <div className="relative">
                  <input
                    type="text"
                    value={newMedName}
                    onChange={(e) => handleMedNameChange(e.target.value)}
                    placeholder="Medication name"
                    className={inputCls}
                    autoFocus
                  />
                  {medSuggestions.length > 0 && (
                    <div className="absolute z-10 mt-1 max-h-32 w-full overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg">
                      {medSuggestions.map((s) => (
                        <button
                          key={s}
                          type="button"
                          onClick={() => { setNewMedName(s); setMedSuggestions([]) }}
                          className="block w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-clara-50"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newMedDosage}
                    onChange={(e) => setNewMedDosage(e.target.value)}
                    placeholder="Dosage (e.g., 10mg)"
                    className={cn(inputCls, 'flex-1')}
                  />
                  <div className="relative flex-1">
                    <input
                      type="text"
                      value={newMedSchedule}
                      onChange={(e) => setNewMedSchedule(e.target.value)}
                      placeholder="Schedule"
                      className={inputCls}
                      list="schedule-presets"
                    />
                    <datalist id="schedule-presets">
                      {SCHEDULE_PRESETS.map((s) => (
                        <option key={s} value={s} />
                      ))}
                    </datalist>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={addMedication}
                    disabled={!newMedName.trim()}
                    className="flex-1 rounded-lg bg-clara-600 px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-clara-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    Add Medication
                  </button>
                  <button
                    type="button"
                    onClick={() => { setShowAddMed(false); setNewMedName(''); setNewMedDosage(''); setNewMedSchedule('') }}
                    className="rounded-lg bg-gray-100 px-3 py-2 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setShowAddMed(true)}
                className="flex w-full items-center justify-center gap-1.5 rounded-lg border-2 border-dashed border-gray-200 py-3 text-xs font-medium text-gray-400 transition-colors hover:border-clara-300 hover:text-clara-600"
              >
                <Plus className="h-3.5 w-3.5" />
                Add Medication
              </button>
            )}
          </div>
        </Section>

        {/* ── Preferences ─────────────────────── */}
        <Section icon={Heart} title="Preferences">
          <div className="space-y-4">
            <div>
              <label className="mb-2 block text-[11px] font-medium uppercase tracking-wide text-gray-400">
                Favorite Topics
              </label>
              <TagInput
                tags={favoriteTopics}
                onChange={(t) => { setFavoriteTopics(t); markChanged() }}
                suggestions={TOPIC_SUGGESTIONS}
                placeholder="Add a topic…"
              />
            </div>

            <div>
              <label className="mb-1 block text-[11px] font-medium uppercase tracking-wide text-gray-400">
                Communication Style
              </label>
              <select
                value={commStyle}
                onChange={(e) => { setCommStyle(e.target.value); markChanged() }}
                className={inputCls}
              >
                <option value="">Select a style…</option>
                {COMM_STYLES.map((s) => (
                  <option key={s} value={s.toLowerCase()}>{s}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-[11px] font-medium uppercase tracking-wide text-gray-400">
                Interests
              </label>
              <TagInput
                tags={interests}
                onChange={(t) => { setInterests(t); markChanged() }}
                suggestions={TOPIC_SUGGESTIONS}
                placeholder="Add an interest…"
              />
            </div>

            <div>
              <label className="mb-2 block text-[11px] font-medium uppercase tracking-wide text-gray-400">
                Topics to Avoid
              </label>
              <TagInput
                tags={topicsToAvoid}
                onChange={(t) => { setTopicsToAvoid(t); markChanged() }}
                suggestions={AVOID_SUGGESTIONS}
                placeholder="Add a topic to avoid…"
                tagColor="bg-red-50 text-red-600"
              />
            </div>
          </div>
        </Section>

        {/* ── Family Contacts ─────────────────── */}
        <Section icon={Users} title="Family Contacts">
          <div className="space-y-3">
            {familyContacts.map((contact, i) => (
              <div key={contact.id} className="rounded-lg bg-gray-50 p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <input
                    type="text"
                    value={contact.name}
                    onChange={(e) => updateContact(i, 'name', e.target.value)}
                    className="bg-transparent text-sm font-medium text-gray-900 outline-none focus:bg-white focus:rounded focus:px-2 focus:py-1 focus:border focus:border-clara-300 transition-all"
                    placeholder="Contact name"
                  />
                  <div className="flex items-center gap-2">
                    <select
                      value={contact.relationship}
                      onChange={(e) => updateContact(i, 'relationship', e.target.value)}
                      className="rounded bg-transparent text-[11px] text-gray-400 outline-none focus:bg-white focus:border focus:border-clara-300"
                    >
                      {RELATIONSHIP_OPTIONS.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => removeContact(i)}
                      className="rounded-full p-1 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <Mail className="h-3 w-3 text-gray-400 shrink-0" />
                    <input
                      type="email"
                      value={contact.email}
                      onChange={(e) => updateContact(i, 'email', e.target.value)}
                      className="w-full bg-transparent text-xs text-gray-500 outline-none focus:bg-white focus:rounded focus:px-2 focus:py-1 focus:border focus:border-clara-300 transition-all"
                      placeholder="email@example.com"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="h-3 w-3 text-gray-400 shrink-0" />
                    <input
                      type="tel"
                      value={contact.phone}
                      onChange={(e) => updateContact(i, 'phone', e.target.value)}
                      className="w-full bg-transparent text-xs text-gray-500 outline-none focus:bg-white focus:rounded focus:px-2 focus:py-1 focus:border focus:border-clara-300 transition-all"
                      placeholder="+1 555 000 0000"
                    />
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 pt-1">
                  {(['daily_digest', 'instant_alerts', 'weekly_report'] as const).map((key) => {
                    const labels: Record<string, string> = {
                      daily_digest: 'Daily Digest',
                      instant_alerts: 'Instant Alerts',
                      weekly_report: 'Weekly Report',
                    }
                    const colors: Record<string, string> = {
                      daily_digest: 'bg-green-50 text-green-700 border-green-200',
                      instant_alerts: 'bg-blue-50 text-blue-700 border-blue-200',
                      weekly_report: 'bg-purple-50 text-purple-700 border-purple-200',
                    }
                    const active = contact.notification_preferences[key]
                    return (
                      <button
                        key={key}
                        type="button"
                        onClick={() => updateContact(i, `notif_${key}`, !active)}
                        className={cn(
                          'rounded-full border px-2 py-0.5 text-[10px] font-medium transition-all',
                          active ? colors[key] : 'bg-gray-100 text-gray-400 border-gray-200'
                        )}
                      >
                        {labels[key]}
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}

            {showAddContact ? (
              <div className="rounded-lg border-2 border-dashed border-clara-200 bg-clara-50/50 p-3 space-y-2">
                <input
                  type="text"
                  value={newContact.name}
                  onChange={(e) => setNewContact((p) => ({ ...p, name: e.target.value }))}
                  placeholder="Contact name"
                  className={inputCls}
                  autoFocus
                />
                <div className="flex gap-2">
                  <input
                    type="email"
                    value={newContact.email}
                    onChange={(e) => setNewContact((p) => ({ ...p, email: e.target.value }))}
                    placeholder="Email"
                    className={cn(inputCls, 'flex-1')}
                  />
                  <input
                    type="tel"
                    value={newContact.phone}
                    onChange={(e) => setNewContact((p) => ({ ...p, phone: e.target.value }))}
                    placeholder="Phone"
                    className={cn(inputCls, 'flex-1')}
                  />
                </div>
                <select
                  value={newContact.relationship}
                  onChange={(e) => setNewContact((p) => ({ ...p, relationship: e.target.value }))}
                  className={inputCls}
                >
                  {RELATIONSHIP_OPTIONS.map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={addContact}
                    disabled={!newContact.name.trim()}
                    className="flex-1 rounded-lg bg-clara-600 px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-clara-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    Add Contact
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddContact(false)}
                    className="rounded-lg bg-gray-100 px-3 py-2 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setShowAddContact(true)}
                className="flex w-full items-center justify-center gap-1.5 rounded-lg border-2 border-dashed border-gray-200 py-3 text-xs font-medium text-gray-400 transition-colors hover:border-clara-300 hover:text-clara-600"
              >
                <Plus className="h-3.5 w-3.5" />
                Add Family Contact
              </button>
            )}
          </div>
        </Section>

        {/* ── Cognitive Thresholds ─────────────── */}
        <Section icon={Brain} title="Cognitive Thresholds">
          <div className="space-y-4">
            <div>
              <div className="mb-2 flex items-center justify-between">
                <label className="text-[11px] font-medium uppercase tracking-wide text-gray-400">
                  Deviation Threshold
                </label>
                <span className="text-sm font-semibold text-gray-900">
                  {(deviationThreshold * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min={5}
                max={50}
                step={1}
                value={deviationThreshold * 100}
                onChange={(e) => { setDeviationThreshold(parseInt(e.target.value) / 100); markChanged() }}
                className="w-full accent-clara-600"
              />
              <p className="mt-1 text-[10px] text-gray-400">
                How much a metric must deviate from baseline to trigger an alert
              </p>
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between">
                <label className="text-[11px] font-medium uppercase tracking-wide text-gray-400">
                  Consecutive Trigger
                </label>
                <span className="text-sm font-semibold text-gray-900">
                  {consecutiveTrigger} sessions
                </span>
              </div>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => { setConsecutiveTrigger((p) => Math.max(1, p - 1)); markChanged() }}
                  className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-100 text-gray-600 transition-colors hover:bg-gray-200"
                >
                  −
                </button>
                <div className="flex-1 rounded-lg bg-gray-50 py-2 text-center text-lg font-bold text-gray-900">
                  {consecutiveTrigger}
                </div>
                <button
                  type="button"
                  onClick={() => { setConsecutiveTrigger((p) => Math.min(10, p + 1)); markChanged() }}
                  className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-100 text-gray-600 transition-colors hover:bg-gray-200"
                >
                  +
                </button>
              </div>
              <p className="mt-1 text-[10px] text-gray-400">
                How many consecutive sessions with deviation before an alert is raised
              </p>
            </div>
          </div>
        </Section>
      </main>

      {/* ── Floating Save Button ──────────────── */}
      <div className="fixed bottom-16 left-0 right-0 z-40 px-4 pb-4">
        <div className="mx-auto max-w-lg">
          <button
            onClick={handleSave}
            disabled={!hasChanges || saving}
            className={cn(
              'flex w-full items-center justify-center gap-2 rounded-xl px-6 py-3.5 text-sm font-semibold text-white shadow-lg transition-all',
              saved
                ? 'bg-green-500'
                : hasChanges
                  ? 'bg-clara-600 active:scale-[0.98] hover:bg-clara-700'
                  : 'bg-gray-300 cursor-not-allowed opacity-0 pointer-events-none'
            )}
            type="button"
          >
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Saving…
              </>
            ) : saved ? (
              <>
                <Check className="h-4 w-4" />
                Saved!
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Save All Changes
              </>
            )}
          </button>
        </div>
      </div>
    </>
  )
}
