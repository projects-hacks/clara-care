# ClaraCare — Data Models (Sanity Schemas)

## Overview
All patient data, conversation logs, cognitive baselines, and wellness digests are stored in **Sanity CMS** as structured content.

**Why Sanity?**
- Structured content enables longitudinal cognitive tracking
- GROQ queries perfect for time-series data
- Real-time updates
- Easy to build family dashboard
- This is our **key differentiator** for the Sanity challenge track

---

## Schema 1: Patient

### Purpose
Core profile for each elderly person using ClaraCare.

### Schema Definition

```typescript
// sanity/schemas/patient.ts
export default {
  name: 'patient',
  title: 'Patient',
  type: 'document',
  fields: [
    {
      name: 'name',
      title: 'Full Name',
      type: 'string',
      validation: Rule => Rule.required()
    },
    {
      name: 'preferredName',
      title: 'Preferred Name',
      type: 'string',
      description: 'What Clara should call them (e.g., "Dorothy")',
      validation: Rule => Rule.required()
    },
    {
      name: 'dateOfBirth',
      title: 'Date of Birth',
      type: 'date'
    },
    {
      name: 'birthYear',
      title: 'Birth Year',
      type: 'number',
      description: 'Used for Nostalgia Mode era calculation',
      validation: Rule => Rule.required().min(1900).max(2020)
    },
    {
      name: 'location',
      title: 'Location',
      type: 'object',
      fields: [
        { name: 'city', type: 'string', title: 'City' },
        { name: 'state', type: 'string', title: 'State' },
        { name: 'timezone', type: 'string', title: 'Timezone', description: 'e.g., America/Los_Angeles' }
      ]
    },
    {
      name: 'medicalNotes',
      title: 'Medical Notes',
      type: 'text',
      description: 'General medical context for Clara (NOT diagnoses)'
    },
    {
      name: 'medications',
      title: 'Medications',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'name', type: 'string', title: 'Medication Name' },
            { name: 'dosage', type: 'string', title: 'Dosage' },
            { name: 'schedule', type: 'string', title: 'Schedule', description: 'e.g., "9 AM, 2 PM, 9 PM"' }
          ]
        }
      ]
    },
    {
      name: 'familyContacts',
      title: 'Family Contacts',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'familyMember' }] }]
    },
    {
      name: 'preferences',
      title: 'Preferences',
      type: 'object',
      fields: [
        {
          name: 'favoriteTopics',
          type: 'array',
          of: [{ type: 'string' }],
          title: 'Favorite Topics',
          description: 'e.g., gardening, baseball, cooking'
        },
        {
          name: 'avoidTopics',
          type: 'array',
          of: [{ type: 'string' }],
          title: 'Topics to Avoid',
          description: 'e.g., politics, religion'
        },
        {
          name: 'musicPreferences',
          type: 'array',
          of: [{ type: 'string' }],
          title: 'Music Preferences',
          description: 'Artists, genres from their era'
        },
        {
          name: 'callTime',
          type: 'string',
          title: 'Preferred Call Time',
          description: 'e.g., "9:00 AM"'
        }
      ]
    },
    {
      name: 'cognitiveBaseline',
      title: 'Cognitive Baseline',
      type: 'object',
      description: 'Established after first 7 conversations',
      fields: [
        { name: 'established', type: 'boolean', title: 'Baseline Established' },
        { name: 'baselineDate', type: 'date', title: 'Baseline Date' },
        { name: 'vocabularyDiversity', type: 'number', title: 'Baseline Vocabulary Diversity (TTR)' },
        { name: 'avgResponseTime', type: 'number', title: 'Baseline Response Time (seconds)' },
        { name: 'topicCoherence', type: 'number', title: 'Baseline Topic Coherence (0-1)' },
        { name: 'repetitionRate', type: 'number', title: 'Baseline Repetition Rate' }
      ]
    }
  ]
}
```

### Example Document

```json
{
  "_id": "patient-dorothy-001",
  "_type": "patient",
  "name": "Dorothy Margaret Chen",
  "preferredName": "Dorothy",
  "dateOfBirth": "1945-03-15",
  "birthYear": 1945,
  "location": {
    "city": "San Francisco",
    "state": "CA",
    "timezone": "America/Los_Angeles"
  },
  "medicalNotes": "Heart condition (managed with medication). No cognitive diagnosis. Generally healthy for age.",
  "medications": [
    {
      "name": "Lisinopril",
      "dosage": "10mg",
      "schedule": "9 AM daily"
    },
    {
      "name": "Aspirin",
      "dosage": "81mg",
      "schedule": "9 AM daily"
    }
  ],
  "familyContacts": [
    { "_ref": "family-sarah-001" }
  ],
  "preferences": {
    "favoriteTopics": ["gardening", "baseball", "her grandchildren", "classic movies"],
    "avoidTopics": ["politics", "her late husband's death"],
    "musicPreferences": ["Frank Sinatra", "The Beatles", "Motown"],
    "callTime": "9:00 AM"
  },
  "cognitiveBaseline": {
    "established": true,
    "baselineDate": "2026-02-18",
    "vocabularyDiversity": 0.62,
    "avgResponseTime": 2.8,
    "topicCoherence": 0.87,
    "repetitionRate": 0.05
  }
}
```

---

## Schema 2: Conversation

### Purpose
Records every conversation Clara has with a patient, including transcript, cognitive metrics, and alerts.

### Schema Definition

```typescript
// sanity/schemas/conversation.ts
export default {
  name: 'conversation',
  title: 'Conversation',
  type: 'document',
  fields: [
    {
      name: 'patient',
      title: 'Patient',
      type: 'reference',
      to: [{ type: 'patient' }],
      validation: Rule => Rule.required()
    },
    {
      name: 'timestamp',
      title: 'Timestamp',
      type: 'datetime',
      validation: Rule => Rule.required()
    },
    {
      name: 'duration',
      title: 'Duration (seconds)',
      type: 'number'
    },
    {
      name: 'transcript',
      title: 'Transcript',
      type: 'text',
      description: 'Full conversation transcript'
    },
    {
      name: 'summary',
      title: 'Summary',
      type: 'text',
      description: 'AI-generated summary for family digest'
    },
    {
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
          { title: 'Nostalgic', value: 'nostalgic' }
        ]
      }
    },
    {
      name: 'cognitiveMetrics',
      title: 'Cognitive Metrics',
      type: 'object',
      fields: [
        {
          name: 'vocabularyDiversity',
          type: 'number',
          title: 'Vocabulary Diversity (TTR)',
          description: 'unique_words / total_words'
        },
        {
          name: 'responseLatency',
          type: 'number',
          title: 'Avg Response Latency (seconds)',
          description: 'Time between Clara finishing and patient responding'
        },
        {
          name: 'topicCoherence',
          type: 'number',
          title: 'Topic Coherence (0-1)',
          description: 'Cosine similarity of sentence embeddings'
        },
        {
          name: 'repetitionCount',
          type: 'number',
          title: 'Repetition Count',
          description: 'Number of repeated phrases/stories'
        },
        {
          name: 'wordFindingPauses',
          type: 'number',
          title: 'Word-Finding Pauses',
          description: 'Count of "um", "uh", "what\'s the word"'
        }
      ]
    },
    {
      name: 'nostalgiaEngagement',
      title: 'Nostalgia Engagement',
      type: 'object',
      fields: [
        { name: 'triggered', type: 'boolean', title: 'Nostalgia Mode Triggered' },
        { name: 'era', type: 'string', title: 'Era (e.g., "1960-1970")' },
        { name: 'contentUsed', type: 'text', title: 'Content Used' },
        { name: 'engagementScore', type: 'number', title: 'Engagement Score (0-10)' }
      ]
    },
    {
      name: 'alerts',
      title: 'Alerts',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            { name: 'type', type: 'string', title: 'Alert Type' },
            { name: 'severity', type: 'string', title: 'Severity', options: { list: ['low', 'medium', 'high'] } },
            { name: 'description', type: 'text', title: 'Description' },
            { name: 'timestamp', type: 'datetime', title: 'Timestamp' }
          ]
        }
      ]
    }
  ]
}
```

### Example Document

```json
{
  "_id": "conversation-001",
  "_type": "conversation",
  "patient": { "_ref": "patient-dorothy-001" },
  "timestamp": "2026-02-15T09:05:00Z",
  "duration": 245,
  "transcript": "Clara: Good morning, Dorothy! How did you sleep?\nDorothy: Oh, not too well. I kept thinking about the old days...\n[full transcript]",
  "summary": "Dorothy sounded nostalgic this morning. She shared memories of the 1960s and seemed engaged when discussing The Beatles. No major concerns.",
  "mood": "nostalgic",
  "cognitiveMetrics": {
    "vocabularyDiversity": 0.58,
    "responseLatency": 3.2,
    "topicCoherence": 0.84,
    "repetitionCount": 1,
    "wordFindingPauses": 2
  },
  "nostalgiaEngagement": {
    "triggered": true,
    "era": "1960-1970",
    "contentUsed": "The Beatles released 'I Want to Hold Your Hand' in 1963",
    "engagementScore": 9
  },
  "alerts": [
    {
      "type": "word_finding_difficulty",
      "severity": "low",
      "description": "Dorothy had slight difficulty recalling medication name",
      "timestamp": "2026-02-15T09:12:00Z"
    }
  ]
}
```

---

## Schema 3: Family Member

### Purpose
Contact information for family members who receive wellness digests and alerts.

### Schema Definition

```typescript
// sanity/schemas/familyMember.ts
export default {
  name: 'familyMember',
  title: 'Family Member',
  type: 'document',
  fields: [
    {
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: Rule => Rule.required()
    },
    {
      name: 'email',
      title: 'Email',
      type: 'string',
      validation: Rule => Rule.required().email()
    },
    {
      name: 'phone',
      title: 'Phone',
      type: 'string'
    },
    {
      name: 'relationship',
      title: 'Relationship',
      type: 'string',
      description: 'e.g., Daughter, Son, Grandchild'
    },
    {
      name: 'patients',
      title: 'Patients',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'patient' }] }],
      description: 'Can be responsible for multiple patients'
    },
    {
      name: 'notificationPreferences',
      title: 'Notification Preferences',
      type: 'object',
      fields: [
        { name: 'dailyDigest', type: 'boolean', title: 'Receive Daily Digest' },
        { name: 'instantAlerts', type: 'boolean', title: 'Receive Instant Alerts' },
        { name: 'weeklyReport', type: 'boolean', title: 'Receive Weekly Report' }
      ]
    }
  ]
}
```

### Example Document

```json
{
  "_id": "family-sarah-001",
  "_type": "familyMember",
  "name": "Sarah Chen",
  "email": "sarah.chen@email.com",
  "phone": "+1-415-555-0123",
  "relationship": "Daughter",
  "patients": [
    { "_ref": "patient-dorothy-001" }
  ],
  "notificationPreferences": {
    "dailyDigest": true,
    "instantAlerts": true,
    "weeklyReport": true
  }
}
```

---

## Schema 4: Wellness Digest

### Purpose
Daily summary of patient's wellness for family members.

### Schema Definition

```typescript
// sanity/schemas/wellnessDigest.ts
export default {
  name: 'wellnessDigest',
  title: 'Wellness Digest',
  type: 'document',
  fields: [
    {
      name: 'patient',
      title: 'Patient',
      type: 'reference',
      to: [{ type: 'patient' }],
      validation: Rule => Rule.required()
    },
    {
      name: 'date',
      title: 'Date',
      type: 'date',
      validation: Rule => Rule.required()
    },
    {
      name: 'overallMood',
      title: 'Overall Mood',
      type: 'string',
      options: {
        list: ['happy', 'neutral', 'sad', 'confused', 'distressed', 'nostalgic']
      }
    },
    {
      name: 'highlights',
      title: 'Highlights',
      type: 'array',
      of: [{ type: 'string' }],
      description: 'Key points from the conversation'
    },
    {
      name: 'cognitiveScore',
      title: 'Cognitive Score (0-100)',
      type: 'number',
      description: 'Composite score based on all cognitive metrics'
    },
    {
      name: 'cognitiveTrend',
      title: 'Cognitive Trend',
      type: 'string',
      options: {
        list: [
          { title: 'Improving', value: 'improving' },
          { title: 'Stable', value: 'stable' },
          { title: 'Declining', value: 'declining' }
        ]
      }
    },
    {
      name: 'recommendations',
      title: 'Recommendations',
      type: 'array',
      of: [{ type: 'string' }],
      description: 'Suggested actions for family'
    },
    {
      name: 'conversationReference',
      title: 'Conversation',
      type: 'reference',
      to: [{ type: 'conversation' }]
    }
  ]
}
```

### Example Document

```json
{
  "_id": "digest-001",
  "_type": "wellnessDigest",
  "patient": { "_ref": "patient-dorothy-001" },
  "date": "2026-02-15",
  "overallMood": "nostalgic",
  "highlights": [
    "Shared fond memories of the 1960s",
    "Mentioned upcoming lunch with neighbor",
    "Slight word-finding difficulty with medication name"
  ],
  "cognitiveScore": 85,
  "cognitiveTrend": "stable",
  "recommendations": [
    "Continue monitoring word-finding patterns",
    "Consider scheduling doctor appointment if trend continues"
  ],
  "conversationReference": { "_ref": "conversation-001" }
}
```

---

## GROQ Queries

### Query 1: Get Patient with Recent Conversations

```groq
*[_type == "patient" && _id == $patientId][0]{
  ...,
  "recentConversations": *[_type == "conversation" && references(^._id)] | order(timestamp desc)[0...10]{
    _id,
    timestamp,
    duration,
    summary,
    mood,
    cognitiveMetrics
  }
}
```

### Query 2: Get Cognitive Trend (Last 30 Days)

```groq
*[_type == "conversation" && 
  references($patientId) && 
  timestamp > $startDate] | order(timestamp asc){
  timestamp,
  cognitiveMetrics
}
```

### Query 3: Get All Alerts for Patient

```groq
*[_type == "conversation" && references($patientId)]{
  timestamp,
  "alerts": alerts[]{
    type,
    severity,
    description,
    timestamp
  }
} | order(timestamp desc)
```

### Query 4: Get Latest Wellness Digest

```groq
*[_type == "wellnessDigest" && references($patientId)] | order(date desc)[0]
```

### Query 5: Get Family Dashboard Data

```groq
{
  "patient": *[_type == "patient" && _id == $patientId][0],
  "latestDigest": *[_type == "wellnessDigest" && references($patientId)] | order(date desc)[0],
  "recentConversations": *[_type == "conversation" && references($patientId)] | order(timestamp desc)[0...5],
  "alerts": *[_type == "conversation" && references($patientId)]{
    timestamp,
    "alerts": alerts[]
  } | order(timestamp desc)[0...10]
}
```

---

## Cognitive Metrics Explained

### 1. Vocabulary Diversity (TTR - Type-Token Ratio)
- **Formula**: `unique_words / total_words`
- **Range**: 0.0 to 1.0
- **Normal**: 0.55 - 0.70
- **Declining**: < 0.50
- **Clinical Significance**: Reduced vocabulary is early sign of dementia

### 2. Response Latency
- **Formula**: `avg(seconds between Clara finishing → patient responding)`
- **Normal**: 2-4 seconds
- **Concerning**: > 5 seconds consistently
- **Clinical Significance**: Increased processing time indicates cognitive difficulty

### 3. Topic Coherence
- **Formula**: `cosine_similarity(sentence_embeddings)` across consecutive patient turns
- **Range**: 0.0 to 1.0
- **Normal**: > 0.75
- **Concerning**: < 0.60
- **Clinical Significance**: Low coherence = tangential thinking, confusion

### 4. Repetition Rate
- **Formula**: `repeated_phrases / total_phrases`
- **Normal**: < 0.10 (10%)
- **Concerning**: > 0.20 (20%)
- **Clinical Significance**: Repetitive storytelling is hallmark of cognitive decline

### 5. Word-Finding Difficulty
- **Formula**: Count of "um", "uh", "what's the word", long pauses (>3s mid-sentence)
- **Normal**: 0-3 per conversation
- **Concerning**: > 5 per conversation
- **Clinical Significance**: Classic symptom of early dementia

## Baseline Establishment

**Process**:
1. First 7 conversations establish personal baseline
2. Compute mean and standard deviation for each tracked metric:
   - Vocabulary Diversity (TTR)
   - Topic Coherence
   - Repetition Rate
   - Word-Finding Pauses
   - Response Latency (optional, requires timing data)
3. Store in `patient.cognitiveBaseline`
4. Alert if any metric deviates >20% from baseline for 3+ consecutive calls

**Why 7 conversations?**
- Enough to establish pattern
- Not so many that family waits too long
- Statistically significant for variance detection
