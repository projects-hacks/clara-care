# ClaraCare Backend

AI voice companion for elderly care - phone-based daily check-ins with Clara, featuring cognitive analysis and family notifications.

## Overview

ClaraCare provides a complete cognitive health monitoring system:
- **P1: Voice Agent** - Natural phone conversations with Clara (Deepgram + GPT-4)
- **P2: Cognitive Analysis Engine** - NLP-based metrics, baseline tracking, alerts, and wellness digests
- **P3: Sanity CMS Integration** (In Progress)
- **P4: Next.js Dashboard** (Next)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Download NLP Models

```bash
# spaCy English model (12MB)
python -m spacy download en_core_web_sm

# NLTK data
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords')"
```

### 3. Configure Environment

Create `.env` file:

```bash
# Voice Agent (P1)
DEEPGRAM_API_KEY=your_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
SERVER_PUBLIC_URL=https://your-domain.com

# Email Notifications (P2)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=clara@claracare.ai
```

### 4. Run Server

```bash
python3 -m app.main
```

Server runs at `http://localhost:8000` with API docs at `/docs`.

## Architecture

### Complete System Flow

```
Patient Phone → Twilio → Clara (P1) → Cognitive Pipeline (P2) → Alerts & Digests
                                            ↓
                                    Data Store + Notifications
```

### P1: Voice Agent

```
Patient Phone → Twilio → Clara (Deepgram + GPT-4) → Functions → Sanity/APIs
```

**Clara can:**
- Have natural conversations
- Remind about medications
- Share nostalgia and news
- Detect distress and alert family
- Save conversation summaries with cognitive analysis

### P2: Cognitive Analysis Pipeline

```
Voice Conversation (P1)
        ↓
Cognitive Pipeline (P2)
        ↓
┌─────────────────────────────────────┐
│ 1. Cognitive Analyzer               │ → 5 NLP metrics
│    - Vocabulary Diversity (TTR)     │
│    - Topic Coherence (embeddings)   │
│    - Repetition Detection           │
│    - Word-Finding Pauses            │
│    - Response Latency               │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ 2. Baseline Tracker                 │ → Compare to baseline
│    - Establish baseline (7 convos)  │
│    - Detect deviations (>20%)       │
│    - Track consecutive flags        │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ 3. Alert Engine                     │ → Generate alerts
│    - Cognitive decline alerts       │
│    - Severity categorization        │
│    - Family notifications           │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ 4. Wellness Digest Generator        │ → Daily summary
│    - Cognitive score (0-100)        │
│    - Trend detection                │
│    - Recommendations                │
└─────────────────────────────────────┘
        ↓
    Data Store + Notifications
```

## File Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI application
│   ├── voice/                       # P1: Voice Agent
│   │   ├── agent.py                 # Clara voice assistant
│   │   ├── functions.py             # Available functions for Clara
│   │   ├── persona.py               # Clara's personality
│   │   ├── twilio_bridge.py         # Twilio WebSocket handler
│   │   └── outbound.py              # Outbound call handler
│   │
│   ├── cognitive/                   # P2: Cognitive Analysis
│   │   ├── models.py                # Pydantic models (CognitiveMetrics, Baseline, etc.)
│   │   ├── analyzer.py              # 5 NLP metrics engine
│   │   ├── baseline.py              # Baseline tracking and deviation detection
│   │   ├── alerts.py                # Alert generation
│   │   ├── pipeline.py              # Orchestrator (chains all steps)
│   │   └── utils.py                 # Shared utilities (cognitive score calculation)
│   │
│   ├── storage/                     # Data layer
│   │   ├── base.py                  # DataStore protocol
│   │   └── memory.py                # In-memory implementation (with seeded data)
│   │
│   ├── notifications/               # Email system
│   │   ├── email.py                 # Async SMTP + Jinja2 templates
│   │   └── templates/
│   │       ├── _base.html           # Shared email base
│   │       ├── alert_email.html     # Alert notifications
│   │       └── daily_digest.html    # Wellness digests
│   │
│   └── routes/                      # REST API
│       ├── patients.py              # GET /api/patients/{id}
│       ├── conversations.py         # GET /api/conversations
│       ├── wellness.py              # GET /api/wellness-digests, /api/cognitive-trends
│       └── alerts.py                # GET /api/alerts
│
├── tests/
│   ├── test_voice.py                # P1 voice agent tests
│   ├── test_cognitive_analyzer.py   # P2 NLP metrics tests
│   ├── test_baseline_tracker.py     # P2 baseline tracking tests
│   └── test_api_routes.py           # API endpoint tests
│
├── requirements.txt
├── quickstart.py                    # Quick test script
└── README.md                        # This file
```

## API Endpoints

### Voice Agent (P1)

- `GET /health` - Server status
- `POST /voice/call/patient` - Clara calls a patient
- `GET /voice/calls` - List active calls
- `WS /voice/twilio` - Twilio media stream

### Patient API (P2)

- `GET /api/patients/{patient_id}` - Get patient profile + baseline + latest digest
- `PATCH /api/patients/{patient_id}` - Update patient preferences

### Conversations API (P2)

- `GET /api/conversations?patient_id={id}` - List conversations (paginated)
- `GET /api/conversations/{conversation_id}` - Get full conversation details

### Wellness API (P2)

- `GET /api/wellness-digests?patient_id={id}` - List wellness digests
- `GET /api/wellness-digests/latest?patient_id={id}` - Get latest digest
- `GET /api/cognitive-trends?patient_id={id}&days=30` - Time-series data for charts

### Alerts API (P2)

- `GET /api/alerts?patient_id={id}&severity=high` - List alerts (filterable)
- `PATCH /api/alerts/{alert_id}` - Acknowledge alert

## NLP Metrics (P2)

### 1. Vocabulary Diversity (TTR)
- **Metric**: Type-Token Ratio = unique lemmas / total lemmas
- **Range**: 0.0 - 1.0 (higher = better)
- **Implementation**: spaCy lemmatization + stopword filtering
- **Baseline concern**: Drop > 20% indicates vocabulary shrinkage

### 2. Topic Coherence
- **Metric**: Average cosine similarity between consecutive utterances
- **Range**: 0.0 - 1.0 (higher = more coherent)
- **Implementation**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Baseline concern**: Drop > 20% indicates conversation fragmentation

### 3. Repetition Detection
- **Metric**: Count and rate of repeated trigrams
- **Implementation**: spaCy tokenization + n-gram extraction
- **Baseline concern**: Increase > 20% indicates repetitive speech

### 4. Word-Finding Pauses
- **Metric**: Count of filler words and explicit word-finding indicators
- **Patterns**: "um", "uh", "what's the word", "you know", "the thing", etc.
- **Baseline concern**: Increase indicates word retrieval difficulty

### 5. Response Latency
- **Metric**: Average time between end-of-agent-speech and start-of-patient-speech
- **Range**: Typically 1-3 seconds
- **Implementation**: Timing metadata from Deepgram STT events
- **Baseline concern**: Significant increase indicates processing delays

## Cognitive Score Formula

Composite score (0-100) calculated as:

```python
# TTR component (25 pts): scale 0.3-0.8 to 0-25
ttr_score = ((TTR - 0.3) / 0.5) * 25

# Coherence component (25 pts): scale 0.4-1.0 to 0-25
coh_score = ((coherence - 0.4) / 0.6) * 25

# Repetition component (25 pts): inverse scaling
rep_score = ((1 - rep_rate - 0.7) / 0.3) * 25

# Word-finding component (25 pts): inverse scaling
wf_score = (1 - min(pauses / 10, 1.0)) * 25

cognitive_score = ttr_score + coh_score + rep_score + wf_score
```

## Baseline & Alerts

### Baseline Establishment
1. **Trigger**: After 7 conversations with valid metrics
2. **Metrics**: Mean + std for each metric
3. **Update Strategy**: Rolling window (last 30 conversations) after initial establishment

### Alert Thresholds
- **Deviation Threshold**: 20% from baseline (configurable per patient)
- **Consecutive Trigger**: 3 consecutive conversations (configurable)
- **Severity Mapping**:
  - **Low**: 20-30% deviation
  - **Medium**: 30-50% deviation
  - **High**: >50% deviation

### P1 + P2 Integration

The cognitive pipeline automatically runs after every conversation:

```python
# In voice/functions.py save_conversation()
if self.cognitive_pipeline:
    result = await self.cognitive_pipeline.process_conversation(
        patient_id=patient_id,
        transcript=transcript,
        duration=duration,
        summary=summary,
        detected_mood=detected_mood,
        response_times=response_times
    )
```

**Flow:**
1. Voice call completes (P1)
2. `save_conversation` function called
3. P2 cognitive pipeline runs automatically
4. Metrics analyzed → baseline compared → alerts generated → digest created
5. Family notified via email (if alerts exist)

## Seeded Test Data

The `InMemoryDataStore` includes pre-seeded data for demo/testing:

- **Dorothy patient** (`patient-dorothy-001`)
  - Age: 75, born 1951
  - Location: San Francisco, CA
  - Medications: Lisinopril, Vitamin D
  - Preferences: gardening, 1960s music, family

- **7 baseline conversations** (realistic metrics)
- **Established baseline** (from first 7 conversations)
- **7 wellness digests** (showing stable cognitive trend)
- **2 alerts** (1 acknowledged, 1 pending)
- **Sarah family contact** (daughter)

## Email Notifications

Configure SMTP in `.env` (see Quick Start). If not configured, emails are logged to console (mock mode).

**Email templates:**
- **Alert emails**: Sent to family when cognitive deviations detected
- **Daily digests**: Wellness summaries with cognitive score and trends

Templates use table-based layouts for compatibility with Outlook, Gmail, Yahoo Mail, and Apple Mail.

## Testing

### Quick Test
```bash
python3 quickstart.py
```

### Run Test Suite
```bash
cd backend
python -m pytest tests/ -v
```

### Test API Endpoints
```bash
# Start server
python3 -m app.main

# Get Dorothy's patient profile
curl http://localhost:8000/api/patients/patient-dorothy-001

# Get cognitive trends (last 30 days)
curl "http://localhost:8000/api/cognitive-trends?patient_id=patient-dorothy-001&days=30"

# Get latest wellness digest
curl "http://localhost:8000/api/wellness-digests/latest?patient_id=patient-dorothy-001"

# Get alerts
curl "http://localhost:8000/api/alerts?patient_id=patient-dorothy-001"
```

## Deployment

Update `SERVER_PUBLIC_URL` in `.env` with your public domain, then deploy to Replit or any cloud platform.

**Requirements:**
- Python 3.9+
- Public HTTPS endpoint for Twilio webhooks
- SMTP access for email notifications (optional)

## Troubleshooting

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### NLTK data not found
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"
```

### sentence-transformers slow on first load
The first run downloads the `all-MiniLM-L6-v2` model (~80MB). Subsequent runs use cached model.

### Import errors
```bash
pip install -r requirements.txt
```

## Design Decisions

1. **Protocol-based storage**: `DataStore` protocol allows easy swapping between in-memory, Sanity, or other backends
2. **Lazy model loading**: NLP models loaded on first use to avoid slow startup
3. **Async-first**: All I/O operations are async for performance
4. **Composable pipeline**: Each stage (analyze → baseline → alert → digest) is independent and testable
5. **Graceful degradation**: System works even if NLP models fail (returns defaults)
6. **Email client compatibility**: Table-based layouts, gradient fallbacks, plain-text alternatives