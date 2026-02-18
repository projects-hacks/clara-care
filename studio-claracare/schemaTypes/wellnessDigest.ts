import { defineType, defineField } from 'sanity'
import { DocumentTextIcon } from '@sanity/icons'

export const wellnessDigest = defineType({
  name: 'wellnessDigest',
  title: 'Wellness Digest',
  type: 'document',
  icon: DocumentTextIcon,
  description: 'Daily wellness summaries sent to families',
  fields: [
    defineField({
      name: 'patient',
      title: 'Patient',
      type: 'reference',
      to: [{ type: 'patient' }],
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'date',
      title: 'Date',
      type: 'date',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'conversation',
      title: 'Conversation',
      type: 'reference',
      to: [{ type: 'conversation' }],
      description: 'Conversation this digest is based on',
    }),
    defineField({
      name: 'overallMood',
      title: 'Overall Mood',
      type: 'string',
      description: 'Detected mood from the conversation',
      options: {
        list: [
          { title: 'Happy', value: 'happy' },
          { title: 'Neutral', value: 'neutral' },
          { title: 'Sad', value: 'sad' },
          { title: 'Confused', value: 'confused' },
          { title: 'Distressed', value: 'distressed' },
          { title: 'Nostalgic', value: 'nostalgic' },
        ],
        layout: 'dropdown',
      },
    }),
    defineField({
      name: 'highlights',
      title: 'Highlights',
      type: 'array',
      of: [{ type: 'string' }],
      description: 'Key highlights from the conversation',
    }),
    defineField({
      name: 'cognitiveScore',
      title: 'Cognitive Score',
      type: 'number',
      description: 'Composite score 0-100 based on cognitive metrics',
      validation: (rule) => rule.min(0).max(100),
    }),
    defineField({
      name: 'trend',
      title: 'Cognitive Trend',
      type: 'string',
      options: {
        list: [
          { title: 'Improving', value: 'improving' },
          { title: 'Stable', value: 'stable' },
          { title: 'Declining', value: 'declining' },
        ],
        layout: 'radio',
      },
    }),
    defineField({
      name: 'summary',
      title: 'Summary',
      type: 'text',
      description: 'Daily summary for family',
    }),
    defineField({
      name: 'recommendations',
      title: 'Recommendations',
      type: 'array',
      of: [{ type: 'string' }],
      description: 'Suggested actions for family',
    }),
    defineField({
      name: 'generatedAt',
      title: 'Generated At',
      type: 'datetime',
      description: 'When this digest was generated',
    }),
  ],
})
