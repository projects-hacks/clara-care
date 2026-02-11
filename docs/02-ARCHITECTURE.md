# ClaraCare — System Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLARACARE SYSTEM                         │
│                                                                 │
│   ENTRY POINTS                                                  │
│   ┌──────────────┐         ┌──────────────┐                    │
│   │ Web Browser  │         │ Twilio Phone │ (Bonus)            │
│   │ (Microphone) │         │ Call Inbound │                    │
│   └──────┬───────┘         └──────┬───────┘                    │
│          │ WebSocket               │ WebSocket                  │
│          └──────────┬──────────────┘                            │
│                     ▼                                           │
│          ┌─────────────────────┐                                │
│          │  FastAPI Backend    │                                │
│          │  (Python, Async)    │                                │
│          │                     │                                │
│          │  ┌───────────────┐  │      ┌─────────────────┐      │
│          │  │ Voice Agent   │◄─┤─────►│ Deepgram API    │      │
│          │  │ Controller    │  │  WS  │ STT: Nova-3     │      │
│          │  └───────┬───────┘  │      │ TTS: Aura-2     │      │
│          │          │          │      │ Think: GPT-4o   │      │
│          │  Function Calls     │      │ Function Calling│      │
│          │          │          │      └─────────────────┘      │
│          │  ┌───────▼───────┐  │                                │
│          │  │ Function      │  │                                │
│          │  │ Router        │  │                                │
│          │  └──┬──┬──┬──┬──┘  │                                │
│          └─────┼──┼──┼──┼─────┘                                │
│                │  │  │  │                                       │
│       ┌────────┘  │  │  └────────┐                             │
│       ▼           ▼  ▼           ▼                             │
│  ┌─────────┐ ┌────────┐ ┌──────────┐ ┌───────────┐           │
│  │ Sanity  │ │You.com │ │Cognitive │ │ Alerts    │           │
│  │ CMS     │ │ API    │ │ Engine   │ │ (Email/   │           │
│  │ (+MCP)  │ │        │ │ (spaCy)  │ │  Twilio)  │           │
│  │-Patients│ │-News   │ │-Vocab    │ │           │           │
│  │-Convos  │ │-Search │ │-Latency  │ │           │           │
│  │-Digests │ │-Music  │ │-Coherence│ │           │           │
│  │-Baselines│ │-Facts │ │-Repeats  │ │           │           │
│  └────┬────┘ └────────┘ └──────────┘ └───────────┘           │
│       │                                 │                        │
│       │  GROQ Queries                   │                        │
│       ▼                                  ▼                        │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Foxit — Cognitive Health Report PDF Generator             │     │
│  │  Document Generation API → PDF Services API → Family PDF    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Next.js Family Dashboard (Replit Mobile App)         │     │
│  │  ┌────────┐┌──────────┐┌────────┐┌────────┐┌──────┐ │     │
│  │  │ Home   ││ History  ││ Trends ││ Alerts ││ Sett.│ │     │
│  │  │Summary ││ Transcr. ││ Charts ││Timeline││Meds  │ │     │
│  │  └────────┘└──────────┘└────────┘└────────┘└──────┘ │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Retool Admin Dashboard (via Retool Assist / AppGen)   │     │
│  │  Manage patients, view all conversations, system health│     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
│  INFRA: Docker → Akamai LKE (K8s: CPU + GPU nodes)            │
│  INFRA: GitHub (Public) | Sanity MCP Server (Dev Tooling)      │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Entry Points

#### Web Browser (Primary)
- Simple HTML/JS interface (`voice-web/`)
- Captures microphone input via Web Audio API
- Opens WebSocket to FastAPI backend
- Receives and plays audio responses

#### Twilio Phone (Bonus)
- Real phone number provided by Twilio
- Inbound/outbound calls
- WebSocket bridge to FastAPI backend
- Same conversation flow as web interface

### 2. Backend — FastAPI Server

#### Voice Agent Controller (`app/voice/agent.py`)
- Manages WebSocket connection to Deepgram Voice Agent API
- Handles audio streaming (browser/Twilio → Deepgram → browser/Twilio)
- Processes function calls from Deepgram
- Maintains conversation state

#### Function Router (`app/voice/functions.py`)
Routes function calls from Deepgram to appropriate handlers:

| Function Name | Trigger | Handler |
|--------------|---------|---------|
| `get_patient_context` | Call start | Fetch patient profile from Sanity |
| `search_nostalgia` | Sadness detected | You.com → era-specific content |
| `search_realtime` | Patient asks question | You.com → weather/news/facts |
| `log_medication_check` | Med schedule time | Log to Sanity |
| `trigger_alert` | Distress detected | Email/SMS family |
| `save_conversation` | Call ends | Save transcript + metrics to Sanity |

#### Cognitive Engine (`app/cognitive/analyzer.py`)
- spaCy NLP pipeline
- Computes 5 cognitive metrics (see Data Models doc)
- Compares to patient baseline
- Generates alerts if threshold crossed

#### Nostalgia Mode (`app/nostalgia/era.py`)
- Calculates "golden years" (birth year + 15 to +25)
- Queries You.com for era-specific content
- Content types:
  - Music hits from that era
  - News events
  - Sports championships
  - Pop culture facts

#### Cognitive Health Report Generator (`app/reports/generator.py`)
- Collects cognitive trend data from Sanity (last 7/30 days)
- Creates structured JSON payload for Foxit Document Generation API
- Generates professional PDF report with:
  - Patient summary
  - Cognitive metric charts (last 30 days)
  - Alert history
  - Recommendations for family
- Post-processes via Foxit PDF Services API (compression, watermarking)
- Makes PDF available for download in the family dashboard

#### Sanity Client (`app/sanity_client/client.py`)
- Python wrapper around Sanity HTTP API
- GROQ query builder
- CRUD operations for patients, conversations, digests
- **Development**: Sanity MCP Server configured in AI coding assistant for schema-aware code generation

#### Notification System (`app/notifications/`)
- Email alerts via SMTP (SendGrid or Gmail)
- SMS alerts via Twilio (bonus)
- Alert types: distress, cognitive decline, missed med

### 3. External Services

#### Deepgram Voice Agent API
- **Connection**: WebSocket (`wss://api.deepgram.com/v1/voice-agent`)
- **Auth**: API key in WebSocket headers
- **Input**: Raw audio bytes (16kHz, mono, PCM)
- **Output**: Audio bytes + function calls + events
- **Configuration**:
  ```json
  {
    "stt": {"model": "nova-3"},
    "tts": {"voice": "aura-asteria-en"},
    "think": {
      "provider": "openai",
      "model": "gpt-4o",
      "instructions": "[Clara's system prompt]",
      "functions": [...]
    }
  }
  ```

#### You.com API
- **Search Endpoint**: `/api/search`
- **News Endpoint**: `/api/news`
- **Query Structure**:
  ```json
  {
    "query": "Beatles music 1963",
    "time_range": "1963-01-01 to 1963-12-31"
  }
  ```

#### Sanity CMS
- **Project ID**: Set during signup
- **Dataset**: `production`
- **API**: `https://{projectId}.api.sanity.io/v{version}/data/query/{dataset}`
- **Auth**: Bearer token
- **Query Language**: GROQ
- **MCP Server**: `npx -y @sanity/mcp-server` (for AI coding assistants during dev)

#### Foxit APIs
- **Document Generation API**: `https://api.foxit.com/v1/document-generation`
  - Input: JSON data + DOCX template
  - Output: PDF
- **PDF Services API**: `https://api.foxit.com/v1/pdf-services`
  - Operations: compress, watermark, merge
- **Auth**: API key + secret

### 4. Frontend — Next.js Dashboard

#### Pages (App Router)
- `/` — Home (Today's Summary)
- `/history` — Conversation list
- `/trends` — Cognitive charts
- `/alerts` — Alert timeline
- `/nostalgia` — Nostalgia preferences
- `/settings` — Call schedule, medications, contacts

#### API Client (`lib/api.ts`)
- Fetches data from FastAPI backend
- Endpoints:
  - `GET /patients/{id}`
  - `GET /conversations?patient_id={id}&limit=10`
  - `GET /wellness-digests?patient_id={id}`
  - `GET /alerts?patient_id={id}`

#### Real-Time Updates
- Polling every 30 seconds for new conversations
- Or WebSocket (if time permits)

### 5. Admin Dashboard — Retool

#### Features
- Patient CRUD (create, read, update, delete)
- View all conversations across all patients
- System health: API uptime, Deepgram credits, error logs
- Manual alert creation

#### Setup
1. Create free Retool tenant
2. Email hasun@retool.com with your Retool domain
3. Use Retool Assist (AppGen) to generate initial dashboard
4. Connect to FastAPI backend
5. Iterate UI (drag-and-drop + custom code)
6. Record 5-minute walkthrough video for submission

### 6. Deployment — Akamai LKE

#### Infrastructure
```
GitHub Repo (Public)
    ↓
GitHub Actions CI/CD
    ↓
Docker Build
    ↓
Akamai LKE Kubernetes Cluster
    ├── Backend Pod (FastAPI) — on CPU nodes
    ├── Dashboard Pod (Next.js SSR) — on CPU nodes
    ├── NLP/ML Pod (Cognitive Engine) — on GPU node (bonus points)
    └── Ingress (HTTPS via cert-manager)
```

#### Node Pool
- **CPU pool**: 2x `g6-standard-2` (4GB RAM, 2 CPU each) — ~$20/month
- **GPU pool**: 1x `g6-gpu-1` (RTX 6000, 8GB VRAM) — ~$1.50/hr (use only during analysis)
- **Total**: Well within $1,000 credit

#### Kubernetes Resources
- **Deployment**: FastAPI backend (1-2 replicas)
- **Deployment**: Next.js dashboard (1 replica)
- **Service**: ClusterIP for backend, LoadBalancer for ingress
- **Ingress**: NGINX with SSL termination
- **ConfigMap**: Environment variables
- **Secret**: API keys

## Data Flow Examples

### Example 1: Daily Check-In Call

```
1. User clicks "Start Call" in web interface
   ↓
2. Browser opens WebSocket to FastAPI `/ws/voice`
   ↓
3. FastAPI opens WebSocket to Deepgram Voice Agent
   ↓
4. Deepgram sends "session_started" event
   ↓
5. FastAPI calls function `get_patient_context(patient_id="dorothy")`
   ↓
6. Sanity returns Dorothy's profile + recent conversations
   ↓
7. Browser streams microphone audio → FastAPI → Deepgram
   ↓
8. Deepgram STT: "Good morning Dorothy!"
   ↓
9. Deepgram Think (GPT-4o): Generates response using Clara's persona
   ↓
10. Deepgram TTS: Converts response to audio
    ↓
11. Audio streams: Deepgram → FastAPI → Browser
    ↓
12. User hears: "Good morning Dorothy! How did you sleep?"
    ↓
13. User responds: "Not too well. Kept thinking about the old days."
    ↓
14. Deepgram detects sadness → calls function `search_nostalgia(patient_id="dorothy")`
    ↓
15. FastAPI calculates golden years (1960-1970 if born 1945)
    ↓
16. You.com API: Search for music/news from 1960-1970
    ↓
17. Returns: "The Beatles released 'I Want to Hold Your Hand' in 1963"
    ↓
18. Deepgram incorporates into response
    ↓
19. User hears: "Did you know that on this day in 1963..."
    ↓
20. Conversation continues...
    ↓
21. Call ends → Deepgram calls `save_conversation(...)`
    ↓
22. FastAPI:
    - Runs cognitive analysis (spaCy)
    - Generates wellness digest
    - Saves to Sanity
    - Checks alert thresholds
    ↓
23. Family member opens mobile app
    ↓
24. Next.js queries Sanity via FastAPI
    ↓
25. Displays: "Mom sounded nostalgic today. Mood: stable."
```

### Example 2: Distress Alert

```
1. During conversation, Dorothy says: "Help! I fell!"
   ↓
2. Deepgram sentiment analysis detects distress
   ↓
3. Calls function `trigger_alert(patient_id="dorothy", severity="high", message="Possible fall")`
   ↓
4. FastAPI notifications module:
   - Sends email to family contacts
   - Sends SMS via Twilio
   - Creates alert in Sanity
   ↓
5. Family member receives: "URGENT: Dorothy may need help. She mentioned falling."
   ↓
6. Family can:
   - Call Dorothy
   - Call emergency services
   - Review conversation transcript in app
```

## Security Considerations

### API Key Management
- Never commit API keys to Git
- Use environment variables
- Kubernetes Secrets for production

### Patient Data Privacy
- HIPAA considerations (though we're wellness, not medical)
- Encrypt data at rest in Sanity
- HTTPS for all communications
- No PII in logs

### Authentication
- Family dashboard requires login (simple auth initially)
- Admin dashboard password-protected
- API endpoints require API key or JWT

## Scalability

### Current Architecture (Hackathon)
- Single backend pod
- Single dashboard pod
- Can handle ~100 concurrent calls

### Future Scaling
- Horizontal scaling: More backend pods
- WebSocket load balancing
- Redis for session state
- PostgreSQL for structured data (replace/augment Sanity)
- CDN for dashboard assets

## Monitoring & Logging

### Metrics to Track
- API response times
- Deepgram latency
- WebSocket connection count
- Cognitive analysis processing time
- Errors per endpoint

### Logging
- Python `logging` module
- JSON structured logs
- Levels: DEBUG, INFO, WARNING, ERROR
- Log to stdout → Kubernetes collects

## Disaster Recovery

### Backup Strategy
- Sanity auto-backups (built-in)
- Export Sanity data weekly
- Git for all code

### Failover
- If Deepgram is down: Use separate STT (Whisper) + LLM + TTS stack
- If You.com is down: Use pre-curated nostalgia database
- If Sanity is down: Use local PostgreSQL cache
