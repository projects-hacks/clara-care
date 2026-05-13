// Types

export interface Patient {
  id: string;
  name: string;
  preferred_name: string;
  age: number;
  phone_number: string;
  location: {
    city?: string;
    state?: string;
    timezone?: string;
  };
}

export interface Conversation {
  id: string;
  patient_id: string;
  timestamp: string;
  duration: number;
  transcript: string;
  summary: string;
  detected_mood: string;
  cognitive_metrics: CognitiveMetrics;
}

export interface CognitiveMetrics {
  vocabulary_diversity: number;
  topic_coherence: number;
  repetition_count: number;
  repetition_rate: number;
  word_finding_pauses: number;
  response_latency: number;
}

export interface Alert {
  id: string;
  patient_id: string;
  alert_type: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
  suggested_action: string;
  acknowledged: boolean;
  timestamp: string;
}

export interface WellnessDigest {
  id: string;
  patient_id: string;
  date: string;
  overall_mood: string;
  highlights: string[];
  cognitive_score: number;
  cognitive_trend: 'stable' | 'improving' | 'declining';
  recommendations: string[];
  created_at: string;
}

export interface CognitiveTrend {
  date: string;
  vocabulary: number;
  coherence: number;
  score: number;
}

export interface CreatePatientPayload {
  name: string;
  preferred_name: string;
  birth_year: number;
  phone_number: string;
  city?: string;
  state?: string;
}

export interface PersonalizePayload {
  patient_id: string;
  favorite_topics?: string[];
  communication_style?: string;
}

export interface SchedulePayload {
  patient_id: string;
  preferred_call_time: string;
  invites?: { name: string; email: string; relationship: string }[];
}

export interface PatientDetail {
  patient: Patient;
  latest_digest?: WellnessDigest;
  recent_conversations?: Conversation[];
  baseline?: any;
}
