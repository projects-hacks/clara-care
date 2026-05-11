-- ============================================================
-- ClaraCare — Supabase Migration 001
-- ============================================================
-- TABLES first, then RLS POLICIES at the end
-- (avoids circular dependency: patients policy → family_contacts)
-- ============================================================


-- ============================================================
-- STEP 1: PROFILES (extends auth.users)
-- ============================================================

CREATE TABLE public.profiles (
    id          UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    display_name TEXT,
    avatar_url  TEXT,
    phone       TEXT,
    onboarding_completed BOOLEAN DEFAULT false,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- STEP 2: AUTO-CREATE PROFILE ON SIGNUP (TRIGGER)
-- ============================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name, phone)
    VALUES (
        NEW.id,
        NEW.raw_user_meta_data ->> 'display_name',
        NEW.raw_user_meta_data ->> 'phone'
    );
    RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- ============================================================
-- STEP 3: PATIENTS
-- ============================================================

CREATE TABLE patients (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by      UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Profile
    name            TEXT NOT NULL,
    preferred_name  TEXT NOT NULL,
    date_of_birth   DATE,
    birth_year      INTEGER NOT NULL CHECK (birth_year BETWEEN 1900 AND 2020),
    age             INTEGER,
    phone_number    TEXT NOT NULL,

    -- Location
    city            TEXT,
    state           TEXT,
    timezone        TEXT DEFAULT 'America/Los_Angeles',

    -- Call preferences
    preferred_call_time TEXT DEFAULT '10:00',
    call_enabled    BOOLEAN DEFAULT true,

    -- Clara persona tuning
    communication_style TEXT DEFAULT 'warm and patient',
    favorite_topics TEXT[] DEFAULT '{}',
    interests       TEXT[] DEFAULT '{}',
    topics_to_avoid TEXT[] DEFAULT '{}',
    medical_notes   TEXT,

    -- Cognitive thresholds
    deviation_threshold  NUMERIC(3,2) DEFAULT 0.20,
    consecutive_trigger  INTEGER DEFAULT 3,

    -- Billing
    stripe_subscription_id TEXT,
    plan            TEXT DEFAULT 'trial' CHECK (plan IN ('basic', 'premium', 'trial')),

    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- STEP 4: MEDICATIONS
-- ============================================================

CREATE TABLE medications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id  UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    dosage      TEXT,
    schedule    TEXT
);


-- ============================================================
-- STEP 5: FAMILY CONTACTS
-- ============================================================

CREATE TABLE family_contacts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES auth.users(id),

    -- Contact info
    name            TEXT NOT NULL,
    email           TEXT NOT NULL,
    phone           TEXT,
    relationship    TEXT,

    -- Notification prefs
    daily_digest    BOOLEAN DEFAULT true,
    instant_alerts  BOOLEAN DEFAULT true,
    weekly_report   BOOLEAN DEFAULT false,

    -- Access control
    is_primary      BOOLEAN DEFAULT false,
    can_manage      BOOLEAN DEFAULT false,

    -- Invitation flow
    invite_token    TEXT,
    invited_at      TIMESTAMPTZ,
    accepted_at     TIMESTAMPTZ,

    created_at      TIMESTAMPTZ DEFAULT now(),

    UNIQUE(patient_id, email)
);


-- ============================================================
-- STEP 6: CONVERSATIONS
-- ============================================================

CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
    duration        INTEGER,
    transcript      TEXT,
    summary         TEXT,
    detected_mood   TEXT CHECK (detected_mood IN ('happy','neutral','sad','confused','distressed','nostalgic')),

    -- Cognitive metrics
    vocab_diversity         NUMERIC(5,4),
    topic_coherence         NUMERIC(5,4),
    repetition_count        INTEGER,
    repetition_rate         NUMERIC(5,4),
    word_finding_pauses     INTEGER,
    response_latency        NUMERIC(6,2),

    -- Nostalgia engagement
    nostalgia_triggered         BOOLEAN DEFAULT false,
    nostalgia_era               TEXT,
    nostalgia_content           TEXT,
    nostalgia_engagement_score  NUMERIC(4,2),

    created_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- STEP 7: COGNITIVE BASELINES
-- ============================================================

CREATE TABLE cognitive_baselines (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id          UUID UNIQUE NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    established         BOOLEAN DEFAULT false,
    baseline_date       DATE,
    vocab_diversity     NUMERIC(5,4),
    vocab_diversity_std NUMERIC(5,4),
    topic_coherence     NUMERIC(5,4),
    topic_coherence_std NUMERIC(5,4),
    repetition_rate     NUMERIC(5,4),
    repetition_rate_std NUMERIC(5,4),
    word_finding_pauses     NUMERIC(5,2),
    word_finding_pauses_std NUMERIC(5,2),
    avg_response_time   NUMERIC(6,2),
    response_time_std   NUMERIC(6,2),
    conversation_count  INTEGER DEFAULT 0,
    last_updated        TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- STEP 8: ALERTS
-- ============================================================

CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id),
    alert_type      TEXT NOT NULL,
    severity        TEXT CHECK (severity IN ('low','medium','high')),
    description     TEXT,
    suggested_action TEXT,
    source          TEXT,
    acknowledged    BOOLEAN DEFAULT false,
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMPTZ,
    related_metrics JSONB,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ============================================================
-- STEP 9: WELLNESS DIGESTS
-- ============================================================

CREATE TABLE wellness_digests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id),
    date            DATE NOT NULL,
    overall_mood    TEXT,
    highlights      TEXT[] DEFAULT '{}',
    cognitive_score INTEGER CHECK (cognitive_score BETWEEN 0 AND 100),
    cognitive_trend TEXT CHECK (cognitive_trend IN ('improving','stable','declining')),
    recommendations TEXT[] DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- STEP 10: DEVIATION TRACKERS
-- ============================================================

CREATE TABLE deviation_trackers (
    patient_id  UUID PRIMARY KEY REFERENCES patients(id) ON DELETE CASCADE,
    metrics     JSONB DEFAULT '{}',
    updated_at  TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- STEP 11: ENABLE RLS ON ALL TABLES
-- ============================================================
-- (must be done AFTER all tables exist, BEFORE creating policies)

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE medications ENABLE ROW LEVEL SECURITY;
ALTER TABLE family_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE cognitive_baselines ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE wellness_digests ENABLE ROW LEVEL SECURITY;
ALTER TABLE deviation_trackers ENABLE ROW LEVEL SECURITY;


-- ============================================================
-- STEP 12: CREATE ALL RLS POLICIES
-- ============================================================
-- Now all tables exist, so cross-table references work.

-- Profiles: users see/edit only their own
CREATE POLICY "profiles_select_own" ON profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "profiles_update_own" ON profiles
    FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "profiles_insert_own" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Patients: creator OR any linked family contact
CREATE POLICY "patients_access" ON patients
    FOR ALL USING (
        created_by = auth.uid()
        OR id IN (SELECT patient_id FROM family_contacts WHERE user_id = auth.uid())
    );

-- Medications: same access as patient
CREATE POLICY "medications_access" ON medications
    FOR ALL USING (
        patient_id IN (
            SELECT id FROM patients
            WHERE created_by = auth.uid()
               OR id IN (SELECT patient_id FROM family_contacts WHERE user_id = auth.uid())
        )
    );

-- Family Contacts: own contacts OR contacts of patients you created
CREATE POLICY "family_contacts_access" ON family_contacts
    FOR ALL USING (
        user_id = auth.uid()
        OR patient_id IN (SELECT id FROM patients WHERE created_by = auth.uid())
    );

-- Conversations
CREATE POLICY "conversations_access" ON conversations
    FOR ALL USING (
        patient_id IN (
            SELECT id FROM patients
            WHERE created_by = auth.uid()
               OR id IN (SELECT patient_id FROM family_contacts WHERE user_id = auth.uid())
        )
    );

-- Cognitive Baselines
CREATE POLICY "baselines_access" ON cognitive_baselines
    FOR ALL USING (
        patient_id IN (
            SELECT id FROM patients
            WHERE created_by = auth.uid()
               OR id IN (SELECT patient_id FROM family_contacts WHERE user_id = auth.uid())
        )
    );

-- Alerts
CREATE POLICY "alerts_access" ON alerts
    FOR ALL USING (
        patient_id IN (
            SELECT id FROM patients
            WHERE created_by = auth.uid()
               OR id IN (SELECT patient_id FROM family_contacts WHERE user_id = auth.uid())
        )
    );

-- Wellness Digests
CREATE POLICY "digests_access" ON wellness_digests
    FOR ALL USING (
        patient_id IN (
            SELECT id FROM patients
            WHERE created_by = auth.uid()
               OR id IN (SELECT patient_id FROM family_contacts WHERE user_id = auth.uid())
        )
    );

-- Deviation Trackers
CREATE POLICY "trackers_access" ON deviation_trackers
    FOR ALL USING (
        patient_id IN (
            SELECT id FROM patients
            WHERE created_by = auth.uid()
               OR id IN (SELECT patient_id FROM family_contacts WHERE user_id = auth.uid())
        )
    );


-- ============================================================
-- STEP 13: INDEXES
-- ============================================================

CREATE INDEX idx_patients_created_by       ON patients(created_by);
CREATE INDEX idx_conversations_patient_ts  ON conversations(patient_id, timestamp DESC);
CREATE INDEX idx_alerts_patient_sev        ON alerts(patient_id, severity, timestamp DESC);
CREATE INDEX idx_alerts_unack              ON alerts(patient_id, acknowledged) WHERE acknowledged = false;
CREATE INDEX idx_digests_patient_date      ON wellness_digests(patient_id, date DESC);
CREATE INDEX idx_family_contacts_user      ON family_contacts(user_id);
CREATE INDEX idx_family_contacts_patient   ON family_contacts(patient_id);
CREATE INDEX idx_family_contacts_token     ON family_contacts(invite_token) WHERE invite_token IS NOT NULL;


-- ============================================================
-- DONE ✅
-- ============================================================
-- 10 tables, 1 trigger, 11 RLS policies, 8 indexes
-- ============================================================
