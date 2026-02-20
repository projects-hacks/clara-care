import { defineType, defineField, defineArrayMember } from 'sanity'
import { HeartFilledIcon } from '@sanity/icons'

export const patient = defineType({
  name: 'patient',
  title: 'Patient',
  type: 'document',
  icon: HeartFilledIcon,
  description: 'Core profile for elderly care tracking in ClaraCare',
  fields: [
    // Core fields
    defineField({
      name: 'name',
      title: 'Full Name',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'preferredName',
      title: 'Preferred Name',
      type: 'string',
      description: 'What Clara should call them (e.g., "Dorothy")',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'dateOfBirth',
      title: 'Date of Birth',
      type: 'date',
    }),
    defineField({
      name: 'birthYear',
      title: 'Birth Year',
      type: 'number',
      description: 'Used for Nostalgia Mode era calculation',
      validation: (rule) => rule.required().min(1900).max(2020),
    }),
    defineField({
      name: 'age',
      title: 'Age',
      type: 'number',
      description: 'Can be derived from birthYear/dateOfBirth or stored for display',
    }),
    // Location (object)
    defineField({
      name: 'location',
      title: 'Location',
      type: 'object',
      fields: [
        defineField({ name: 'city', type: 'string', title: 'City' }),
        defineField({ name: 'state', type: 'string', title: 'State' }),
        defineField({
          name: 'timezone',
          type: 'string',
          title: 'Timezone',
          description: 'e.g., America/Los_Angeles',
        }),
      ],
    }),
    // Phone & Call Schedule  
    defineField({
      name: 'phoneNumber',
      title: 'Phone Number',
      type: 'string',
      description: 'Patient phone number (E.164 format, e.g., +14155551234)',
    }),
    defineField({
      name: 'callSchedule',
      title: 'Call Schedule',
      type: 'object',
      description: 'Uses the timezone from Location above',
      fields: [
        defineField({
          name: 'preferredTime',
          type: 'string',
          title: 'Preferred Time',
          description: 'e.g., 10:00 AM',
        }),
      ],
    }),
    // Medications (array of objects)
    defineField({
      name: 'medications',
      title: 'Medications',
      type: 'array',
      of: [
        defineArrayMember({
          type: 'object',
          name: 'medication',
          title: 'Medication',
          fields: [
            defineField({ name: 'name', type: 'string', title: 'Medication Name' }),
            defineField({ name: 'dosage', type: 'string', title: 'Dosage' }),
            defineField({
              name: 'schedule',
              type: 'string',
              title: 'Schedule',
              description: 'e.g., "9 AM, 2 PM, 9 PM"',
            }),
          ],
          preview: {
            select: { name: 'name' },
            prepare: ({ name }) => ({ title: name || 'Medication' }),
          },
        }),
      ],
    }),
    // Family contacts (inline objects — single source of truth)
    defineField({
      name: 'familyContacts',
      title: 'Family Contacts',
      type: 'array',
      of: [
        defineArrayMember({
          type: 'object',
          name: 'familyContact',
          title: 'Family Contact',
          fields: [
            defineField({ name: 'name', type: 'string', title: 'Name', validation: (rule) => rule.required() }),
            defineField({ name: 'email', type: 'string', title: 'Email', validation: (rule) => rule.required().email() }),
            defineField({ name: 'phone', type: 'string', title: 'Phone' }),
            defineField({
              name: 'relationship',
              type: 'string',
              title: 'Relationship',
              description: 'e.g., Daughter, Son',
            }),
            defineField({
              name: 'notificationPreferences',
              title: 'Notification Preferences',
              type: 'object',
              fields: [
                defineField({ name: 'dailyDigest', type: 'boolean', title: 'Daily Digest', initialValue: true }),
                defineField({ name: 'instantAlerts', type: 'boolean', title: 'Instant Alerts', initialValue: true }),
                defineField({ name: 'weeklyReport', type: 'boolean', title: 'Weekly Report', initialValue: false }),
              ],
            }),
          ],
          preview: {
            select: { title: 'name', subtitle: 'relationship' },
          },
        }),
      ],
    }),
    // Preferences (nested object with string arrays)
    defineField({
      name: 'preferences',
      title: 'Preferences',
      type: 'object',
      fields: [
        defineField({
          name: 'favoriteTopics',
          type: 'array',
          title: 'Favorite Topics',
          description: 'e.g., gardening, baseball, cooking',
          of: [{ type: 'string' }],
          options: { layout: 'tags' },
        }),
        defineField({
          name: 'communicationStyle',
          type: 'string',
          title: 'Communication Style',
          description: 'How they prefer to communicate (e.g., warm and patient)',
          options: {
            list: [
              { title: 'Warm and Patient', value: 'warm and patient' },
              { title: 'Direct and Clear', value: 'direct and clear' },
              { title: 'Gentle and Encouraging', value: 'gentle and encouraging' },
              { title: 'Cheerful and Energetic', value: 'cheerful and energetic' },
            ],
          },
        }),
        defineField({
          name: 'interests',
          type: 'array',
          title: 'Interests',
          description: 'Hobbies and interests',
          of: [{ type: 'string' }],
          options: { layout: 'tags' },
        }),
        defineField({
          name: 'topicsToAvoid',
          type: 'array',
          title: 'Topics to Avoid',
          description: 'Sensitive topics Clara should not bring up',
          of: [{ type: 'string' }],
          options: { layout: 'tags' },
        }),
      ],
    }),
    // Medical notes
    defineField({
      name: 'medicalNotes',
      title: 'Medical Notes',
      type: 'text',
      description: 'Health context for Clara to be aware of during calls',
    }),
    // Cognitive thresholds (nested object with defaults)
    defineField({
      name: 'cognitiveThresholds',
      title: 'Cognitive Thresholds',
      type: 'object',
      description: 'Alert thresholds for cognitive deviation detection',
      initialValue: {
        deviationThreshold: 0.2,
        consecutiveTrigger: 3,
      },
      fields: [
        defineField({
          name: 'deviationThreshold',
          type: 'number',
          title: 'Deviation Threshold',
          description: 'Alert when metric deviates this much from baseline (e.g., 0.20 = 20%)',
          initialValue: 0.2,
          validation: (rule) => rule.min(0).max(1),
        }),
        defineField({
          name: 'consecutiveTrigger',
          type: 'number',
          title: 'Consecutive Trigger',
          description: 'Number of consecutive calls exceeding threshold before alerting',
          initialValue: 3,
          validation: (rule) => rule.min(1).integer(),
        }),
      ],
    }),
  ],
})
