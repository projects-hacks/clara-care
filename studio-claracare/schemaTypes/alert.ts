import { defineType, defineField } from 'sanity'
import { WarningOutlineIcon } from '@sanity/icons'

export const alert = defineType({
  name: 'alert',
  title: 'Alert',
  type: 'document',
  icon: WarningOutlineIcon,
  description: 'Cognitive or wellness alerts with cross-document references for family follow-up',
  fields: [
    defineField({
      name: 'patient',
      title: 'Patient',
      type: 'reference',
      to: [{ type: 'patient' }],
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'conversation',
      title: 'Conversation',
      type: 'reference',
      to: [{ type: 'conversation' }],
      description: 'Conversation where this alert was triggered',
    }),
    defineField({
      name: 'alertType',
      title: 'Alert Type',
      type: 'string',
      description: 'e.g., word_finding_difficulty, coherence_drop, repetition_spike',
    }),
    defineField({
      name: 'severity',
      title: 'Severity',
      type: 'string',
      options: {
        list: [
          { title: 'Low', value: 'low' },
          { title: 'Medium', value: 'medium' },
          { title: 'High', value: 'high' },
        ],
        layout: 'radio',
      },
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
    }),
    defineField({
      name: 'acknowledged',
      title: 'Acknowledged',
      type: 'boolean',
      initialValue: false,
    }),
    defineField({
      name: 'acknowledgedBy',
      title: 'Acknowledged By',
      type: 'string',
      description: 'Name of the person who acknowledged this alert',
      hidden: ({ parent }) => !parent?.acknowledged,
    }),
    defineField({
      name: 'acknowledgedAt',
      title: 'Acknowledged At',
      type: 'datetime',
      description: 'When this alert was acknowledged',
      hidden: ({ parent }) => !parent?.acknowledged,
    }),
    defineField({
      name: 'timestamp',
      title: 'Timestamp',
      type: 'datetime',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'relatedMetrics',
      title: 'Related Metrics',
      type: 'object',
      description: 'Metric values that triggered or support this alert',
      fields: [
        defineField({
          name: 'metricName',
          type: 'string',
          title: 'Metric Name',
          description: 'e.g., vocabularyDiversity, topicCoherence',
        }),
        defineField({
          name: 'currentValue',
          type: 'number',
          title: 'Current Value',
        }),
        defineField({
          name: 'baselineValue',
          type: 'number',
          title: 'Baseline Value',
        }),
        defineField({
          name: 'deviationPercent',
          type: 'number',
          title: 'Deviation %',
          description: 'How much current deviates from baseline',
        }),
      ],
    }),
  ],
})
