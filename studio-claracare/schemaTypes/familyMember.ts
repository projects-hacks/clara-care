import { defineType, defineField, defineArrayMember } from 'sanity'
import { UserIcon } from '@sanity/icons'

export const familyMember = defineType({
  name: 'familyMember',
  title: 'Family Member',
  type: 'document',
  icon: UserIcon,
  description: 'Family contacts who receive alerts and digests',
  fields: [
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'email',
      title: 'Email',
      type: 'string',
      validation: (rule) => rule.required().email(),
    }),
    defineField({
      name: 'phone',
      title: 'Phone',
      type: 'string',
    }),
    defineField({
      name: 'relationship',
      title: 'Relationship',
      type: 'string',
      description: 'e.g., Daughter, Son',
    }),
    defineField({
      name: 'patients',
      title: 'Patients',
      type: 'array',
      of: [defineArrayMember({ type: 'reference', to: [{ type: 'patient' }] })],
      description: 'Can be responsible for multiple patients',
    }),
    defineField({
      name: 'notificationPreferences',
      title: 'Notification Preferences',
      type: 'object',
      description: 'Which alerts and digests this contact receives',
      fields: [
        defineField({ name: 'dailyDigest', type: 'boolean', title: 'Daily Digest' }),
        defineField({ name: 'instantAlerts', type: 'boolean', title: 'Instant Alerts' }),
        defineField({ name: 'weeklyReport', type: 'boolean', title: 'Weekly Report' }),
      ],
    }),
  ],
})
