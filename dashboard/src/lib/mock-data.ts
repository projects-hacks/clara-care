import type { Patient, Conversation, CognitiveMetrics, Alert, WellnessDigest, CognitiveTrend, Insights } from './api'

const now = new Date()
const daysAgo = (d: number) => new Date(now.getTime() - d * 86400000).toISOString()

export const mockPatient: Patient = {
  id: 'patient-dorothy-001',
  name: 'Dorothy Chen',
  preferred_name: 'Dorothy',
  date_of_birth: '1951-03-15',
  birth_year: 1951,
  age: 75,
  location: {
    city: 'San Francisco',
    state: 'CA',
    timezone: 'America/Los_Angeles',
  },
  medical_notes: 'Generally healthy, occasional memory concerns',
  medications: [
    { name: 'Lisinopril', dosage: '10mg', schedule: '9 AM daily' },
    { name: 'Vitamin D', dosage: '2000 IU', schedule: 'Morning with breakfast' },
  ],
  preferences: {
    favorite_topics: ['gardening', '1960s music', 'family', 'cooking'],
    communication_style: 'warm and patient',
    interests: ['music', 'gardening', 'family history'],
    topics_to_avoid: ['politics', 'health scares'],
  },
  cognitive_thresholds: {
    deviation_threshold: 0.20,
    consecutive_trigger: 3,
  },
  call_schedule: { preferred_time: '10:00 AM', timezone: 'America/Los_Angeles' },
  phone_number: '+14155550199',
  family_contacts: [
    {
      id: 'family-sarah-001',
      name: 'Sarah Chen',
      email: 'sarah.chen@email.com',
      phone: '+14155550123',
      relationship: 'Daughter',
      notification_preferences: {
        daily_digest: true,
        instant_alerts: true,
        weekly_report: true,
      },
    },
  ],
}

export const mockConversations: Conversation[] = [
  {
    id: 'conv-001',
    patient_id: 'patient-dorothy-001',
    timestamp: daysAgo(0),
    duration: 420,
    transcript: "Clara: Good morning, Dorothy! How did you sleep last night?\nDorothy: Oh, good morning Clara! I slept wonderfully, actually. I had the most beautiful dream about my garden from when I was growing up.\nClara: That sounds lovely! Tell me about that garden.\nDorothy: Well, my mother had the most incredible rose bushes. She used to spend hours tending them. I remember the smell of those roses to this day. We had red ones and yellow ones, and this one special pink variety that she got from her mother.\nClara: What a beautiful memory. Do you still enjoy gardening?\nDorothy: Oh yes! I have a little herb garden on my windowsill. Nothing like Mother's garden, but it keeps me company. I've got basil and rosemary and a little mint plant.\nClara: That's wonderful, Dorothy. Fresh herbs make everything better.",
    summary: 'Dorothy shared fond memories of her mother\'s rose garden from childhood. Currently maintains a windowsill herb garden. Mood was warm and nostalgic.',
    detected_mood: 'nostalgic',
    cognitive_metrics: {
      vocabulary_diversity: 0.67,
      topic_coherence: 0.91,
      repetition_count: 1,
      repetition_rate: 0.02,
      word_finding_pauses: 0,
      response_latency: 1.3,
    },
    nostalgia_engagement: {
      triggered: true,
      era: '1966-1976',
      content_used: 'Shared memories of 1960s gardening with mother',
      engagement_score: 9,
    },
  },
  {
    id: 'conv-002',
    patient_id: 'patient-dorothy-001',
    timestamp: daysAgo(1),
    duration: 360,
    transcript: "Clara: Good morning, Dorothy! How are you feeling today?\nDorothy: Morning, Clara. I'm alright, a bit tired. Didn't sleep very well.\nClara: I'm sorry to hear that. Did something keep you up?\nDorothy: No, nothing in particular. Just one of those nights, you know.\nClara: I understand. Have you had your morning medications yet?\nDorothy: Oh, yes, I took them. Though sometimes I wonder if I already took them or not. I should really start using that pill organizer Sarah got me.\nClara: That's a great idea! A pill organizer can really help.",
    summary: 'Dorothy reported poor sleep and expressed some uncertainty about medication tracking. Mood was neutral but slightly fatigued.',
    detected_mood: 'neutral',
    cognitive_metrics: {
      vocabulary_diversity: 0.58,
      topic_coherence: 0.83,
      repetition_count: 3,
      repetition_rate: 0.07,
      word_finding_pauses: 2,
      response_latency: 1.8,
    },
    nostalgia_engagement: null,
  },
  {
    id: 'conv-003',
    patient_id: 'patient-dorothy-001',
    timestamp: daysAgo(2),
    duration: 480,
    transcript: "Clara: Good morning, Dorothy! Any exciting plans today?\nDorothy: Oh yes! My grandson Tommy is coming to visit! He's graduating from college next month, can you believe it?\nClara: How wonderful! You must be so proud!\nDorothy: I am, I really am. He's studying computer science. I don't understand half of what he does but I'm so proud of him. He's going to change the world, I just know it.\nClara: That's beautiful, Dorothy. What are you planning to do together?\nDorothy: Well, I'm going to make his favorite - my apple pie! I've been making it since he was little.",
    summary: 'Dorothy was very excited about grandson Tommy\'s upcoming visit and graduation. Plans to bake his favorite apple pie. Very engaged and happy throughout.',
    detected_mood: 'happy',
    cognitive_metrics: {
      vocabulary_diversity: 0.70,
      topic_coherence: 0.92,
      repetition_count: 1,
      repetition_rate: 0.02,
      word_finding_pauses: 0,
      response_latency: 1.1,
    },
    nostalgia_engagement: null,
  },
  {
    id: 'conv-004',
    patient_id: 'patient-dorothy-001',
    timestamp: daysAgo(3),
    duration: 300,
    transcript: "Clara: Good morning, Dorothy!\nDorothy: Good morning. I... I had a strange morning. I went to make tea and I couldn't find the... the thing... you know, the thing you put the water in.\nClara: The kettle?\nDorothy: Yes! The kettle. That's it. It was right there on the counter the whole time. I feel so silly.\nClara: Don't feel silly at all, Dorothy. Those moments happen to everyone.\nDorothy: I suppose. It's just... it worries me sometimes.",
    summary: 'Dorothy experienced a word-finding difficulty (couldn\'t recall "kettle"). Expressed some worry about the incident. Brief conversation.',
    detected_mood: 'confused',
    cognitive_metrics: {
      vocabulary_diversity: 0.52,
      topic_coherence: 0.76,
      repetition_count: 4,
      repetition_rate: 0.10,
      word_finding_pauses: 4,
      response_latency: 2.4,
    },
    nostalgia_engagement: null,
  },
  {
    id: 'conv-005',
    patient_id: 'patient-dorothy-001',
    timestamp: daysAgo(5),
    duration: 450,
    transcript: "Clara: Good morning, Dorothy! I heard a fun fact - did you know The Beatles released 'I Want to Hold Your Hand' in 1963?\nDorothy: Oh my goodness, yes! I remember that so clearly. I was at a school dance when I first heard it. Everyone was screaming and dancing!\nClara: What a wonderful memory!\nDorothy: Those were the days. We used to go to record shops after school. I saved up my allowance for weeks to buy that album. My father thought it was just noise, but my mother secretly loved it too.",
    summary: 'Dorothy recalled vivid memories of hearing Beatles songs at a school dance in the 1960s. Very engaged with nostalgia mode. High vocabulary and coherence.',
    detected_mood: 'nostalgic',
    cognitive_metrics: {
      vocabulary_diversity: 0.72,
      topic_coherence: 0.93,
      repetition_count: 1,
      repetition_rate: 0.02,
      word_finding_pauses: 0,
      response_latency: 1.0,
    },
    nostalgia_engagement: {
      triggered: true,
      era: '1966-1976',
      content_used: "The Beatles released 'I Want to Hold Your Hand' in 1963",
      engagement_score: 10,
    },
  },
  {
    id: 'conv-006',
    patient_id: 'patient-dorothy-001',
    timestamp: daysAgo(7),
    duration: 390,
    transcript: "Clara: Good morning, Dorothy! How's your week going?\nDorothy: Hi Clara. It's been okay. I had lunch with my neighbor Margaret yesterday. We went to that little Italian place on the corner.\nClara: That sounds nice! What did you have?\nDorothy: I had the... oh what's it called... the pasta with the red sauce and the cheese on top.\nClara: Spaghetti?\nDorothy: No, no, the one that's like tubes.\nClara: Penne?\nDorothy: Yes! Penne! It was delicious.",
    summary: 'Dorothy had lunch with neighbor Margaret. Experienced minor word-finding pause for "penne" but overall good spirits.',
    detected_mood: 'happy',
    cognitive_metrics: {
      vocabulary_diversity: 0.60,
      topic_coherence: 0.85,
      repetition_count: 2,
      repetition_rate: 0.05,
      word_finding_pauses: 2,
      response_latency: 1.6,
    },
    nostalgia_engagement: null,
  },
  {
    id: 'conv-007',
    patient_id: 'patient-dorothy-001',
    timestamp: daysAgo(9),
    duration: 330,
    transcript: "Clara: Good morning, Dorothy! How are you doing?\nDorothy: I'm feeling a bit down today, Clara. I miss my husband. It's been... it would have been our anniversary next week.\nClara: I'm so sorry, Dorothy. It's natural to feel that way. Would you like to share a memory of your time together?\nDorothy: He used to bring me flowers every Friday. Not expensive ones, just wildflowers from the field behind our house. Every Friday, without fail.",
    summary: 'Dorothy expressed sadness about upcoming wedding anniversary. Shared touching memory about late husband bringing wildflowers every Friday.',
    detected_mood: 'sad',
    cognitive_metrics: {
      vocabulary_diversity: 0.61,
      topic_coherence: 0.88,
      repetition_count: 2,
      repetition_rate: 0.04,
      word_finding_pauses: 1,
      response_latency: 1.7,
    },
    nostalgia_engagement: {
      triggered: true,
      era: '1966-1976',
      content_used: 'Shared memory about late husband',
      engagement_score: 7,
    },
  },
  {
    id: 'conv-008',
    patient_id: 'patient-dorothy-001',
    timestamp: daysAgo(11),
    duration: 360,
    transcript: "Clara: Good morning, Dorothy!\nDorothy: Oh hello Clara, good morning! I just finished watering my plants. The basil is growing so well!\nClara: That's great! Are you using it in your cooking?\nDorothy: Oh yes, I made a lovely caprese salad yesterday. Fresh tomatoes from the farmer's market and my own basil. Simple but delicious.\nClara: That sounds absolutely delicious, Dorothy!",
    summary: 'Dorothy in good spirits, talked about her herb garden and cooking. Made caprese salad with fresh basil.',
    detected_mood: 'happy',
    cognitive_metrics: {
      vocabulary_diversity: 0.64,
      topic_coherence: 0.89,
      repetition_count: 1,
      repetition_rate: 0.03,
      word_finding_pauses: 0,
      response_latency: 1.2,
    },
    nostalgia_engagement: null,
  },
]

export const mockAlerts: Alert[] = [
  {
    id: 'alert-001',
    patient_id: 'patient-dorothy-001',
    alert_type: 'word_finding_difficulty',
    severity: 'medium',
    description: 'Dorothy experienced significant word-finding difficulty during morning conversation. Could not recall "kettle" and showed extended pauses.',
    acknowledged: false,
    acknowledged_by: null,
    timestamp: daysAgo(3),
    conversation_id: 'conv-004',
  },
  {
    id: 'alert-002',
    patient_id: 'patient-dorothy-001',
    alert_type: 'repetition_increase',
    severity: 'low',
    description: 'Repetition rate increased to 0.10 (baseline: 0.05). Consecutive deviation count: 2.',
    acknowledged: false,
    acknowledged_by: null,
    timestamp: daysAgo(3),
    conversation_id: 'conv-004',
  },
  {
    id: 'alert-003',
    patient_id: 'patient-dorothy-001',
    alert_type: 'vocabulary_decline',
    severity: 'low',
    description: 'Vocabulary diversity dropped below baseline (0.52 vs 0.63 baseline). May be related to fatigue or mood.',
    acknowledged: true,
    acknowledged_by: 'Sarah Chen',
    timestamp: daysAgo(5),
    conversation_id: 'conv-004',
  },
  {
    id: 'alert-004',
    patient_id: 'patient-dorothy-001',
    alert_type: 'mood_distress',
    severity: 'high',
    description: 'Dorothy expressed feelings of loneliness and sadness related to upcoming wedding anniversary. Recommend family check-in.',
    acknowledged: true,
    acknowledged_by: 'Sarah Chen',
    timestamp: daysAgo(9),
    conversation_id: 'conv-007',
  },
  {
    id: 'alert-005',
    patient_id: 'patient-dorothy-001',
    alert_type: 'response_latency',
    severity: 'medium',
    description: 'Response latency increased to 2.4s (baseline: 1.5s). May indicate cognitive fatigue or confusion.',
    acknowledged: false,
    acknowledged_by: null,
    timestamp: daysAgo(3),
    conversation_id: 'conv-004',
  },
]

export const mockDigest: WellnessDigest = {
  id: 'digest-today',
  patient_id: 'patient-dorothy-001',
  date: daysAgo(0),
  overall_mood: 'nostalgic',
  cognitive_score: 85,
  cognitive_trend: 'stable',
  highlights: [
    'Shared fond memories of her mother\'s rose garden',
    'Maintaining her windowsill herb garden actively',
    'Vocabulary diversity was above average today (0.67)',
    'Strong topic coherence during nostalgic conversation',
  ],
  recommendations: [
    'Continue nostalgia-focused conversations - they boost engagement',
    'Monitor word-finding pauses from 3 days ago',
    'Encourage use of pill organizer for medication tracking',
  ],
}

export const mockCognitiveTrends: CognitiveTrend[] = Array.from({ length: 30 }, (_, i) => {
  const dayOffset = 29 - i
  const base = {
    vocabulary_diversity: 0.63,
    topic_coherence: 0.87,
    repetition_rate: 0.05,
    word_finding_pauses: 1.5,
    response_latency: 1.5,
  }

  const jitter = () => (Math.random() - 0.5) * 0.08

  let vocab = base.vocabulary_diversity + jitter()
  let coherence = base.topic_coherence + jitter()
  let repetition = base.repetition_rate + Math.abs(jitter()) * 0.5
  let pauses = Math.max(0, base.word_finding_pauses + (Math.random() - 0.5) * 2)
  let latency = base.response_latency + (Math.random() - 0.5) * 0.6

  if (dayOffset === 3) {
    vocab = 0.52
    coherence = 0.76
    repetition = 0.10
    pauses = 4
    latency = 2.4
  }
  if (dayOffset === 0 || dayOffset === 5) {
    vocab = 0.70
    coherence = 0.92
    pauses = 0
    latency = 1.1
  }

  return {
    timestamp: daysAgo(dayOffset),
    vocabulary_diversity: Math.round(vocab * 100) / 100,
    topic_coherence: Math.round(coherence * 100) / 100,
    repetition_rate: Math.round(repetition * 100) / 100,
    word_finding_pauses: Math.round(pauses * 10) / 10,
    response_latency: Math.round(latency * 10) / 10,
  }
})

export const mockInsights: Insights = {
  cognitive_by_mood: {
    happy: { avg_vocabulary: 0.65, avg_coherence: 0.89, conversation_count: 4 },
    nostalgic: { avg_vocabulary: 0.70, avg_coherence: 0.92, conversation_count: 3 },
    neutral: { avg_vocabulary: 0.59, avg_coherence: 0.84, conversation_count: 2 },
    sad: { avg_vocabulary: 0.61, avg_coherence: 0.88, conversation_count: 1 },
    confused: { avg_vocabulary: 0.52, avg_coherence: 0.76, conversation_count: 1 },
  },
  nostalgia_effectiveness: {
    with_nostalgia: { avg_vocabulary: 0.70, avg_coherence: 0.92 },
    without_nostalgia: { avg_vocabulary: 0.61, avg_coherence: 0.85 },
    improvement_pct: { vocabulary: 14.8, coherence: 8.2 },
  },
  alert_summary: {
    total: 5,
    by_severity: { low: 2, medium: 2, high: 1 },
    most_common_type: 'word_finding_difficulty',
    unacknowledged: 3,
  },
}
