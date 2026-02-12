import { defineType, defineField } from 'sanity'
import { CommentIcon } from '@sanity/icons'

export const conversation = defineType({
  name: 'conversation',
  title: 'Conversation',
  type: 'document',
  icon: CommentIcon,
  description: 'Daily conversation with cognitive analysis for elderly care tracking',
  fields: [
    defineField({
      name: 'patient',
      title: 'Patient',
      type: 'reference',
      to: [{ type: 'patient' }],
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'timestamp',
      title: 'Timestamp',
      type: 'datetime',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'duration',
      title: 'Duration (seconds)',
      type: 'number',
      description: 'Length of the conversation in seconds',
    }),
    defineField({
      name: 'transcript',
      title: 'Transcript',
      type: 'text',
      description: 'Full conversation transcript',
    }),
    defineField({
      name: 'summary',
      title: 'Summary',
      type: 'text',
      description: 'AI-generated summary for family digest',
    }),
    defineField({
      name: 'mood',
      title: 'Detected Mood',
      type: 'string',
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
      name: 'cognitiveMetrics',
      title: 'Cognitive Metrics',
      type: 'object',
      description: 'Analysis from this conversation',
      fields: [
        defineField({
          name: 'vocabularyDiversity',
          type: 'number',
          title: 'Vocabulary Diversity (TTR)',
          description: 'Type-token ratio, unique_words / total_words (0-1)',
          validation: (rule) => rule.min(0).max(1),
        }),
        defineField({
          name: 'topicCoherence',
          type: 'number',
          title: 'Topic Coherence',
          description: 'Cosine similarity of sentence embeddings (0-1)',
          validation: (rule) => rule.min(0).max(1),
        }),
        defineField({
          name: 'repetitionCount',
          type: 'number',
          title: 'Repetition Count',
          description: 'Number of repeated phrases or stories',
        }),
        defineField({
          name: 'repetitionRate',
          type: 'number',
          title: 'Repetition Rate',
          description: 'Repeated phrases / total phrases (0-1)',
          validation: (rule) => rule.min(0).max(1),
        }),
        defineField({
          name: 'wordFindingPauses',
          type: 'number',
          title: 'Word-Finding Pauses',
          description: 'Count of "um", "uh", "what\'s the word", long pauses',
        }),
        defineField({
          name: 'responseLatency',
          type: 'number',
          title: 'Response Latency (seconds)',
          description: 'Avg time between Clara finishing and patient responding',
        }),
      ],
    }),
    defineField({
      name: 'nostalgiaEngagement',
      title: 'Nostalgia Engagement',
      type: 'object',
      fields: [
        defineField({
          name: 'triggered',
          type: 'boolean',
          title: 'Nostalgia Mode Triggered',
        }),
        defineField({
          name: 'era',
          type: 'string',
          title: 'Era',
          description: 'e.g., "1960-1970"',
        }),
        defineField({
          name: 'contentUsed',
          type: 'text',
          title: 'Content Used',
          description: 'Era content or prompts used',
        }),
        defineField({
          name: 'engagementScore',
          type: 'number',
          title: 'Engagement Score',
          description: '0-10 scale',
          validation: (rule) => rule.min(0).max(10),
        }),
      ],
    }),
  ],
})
