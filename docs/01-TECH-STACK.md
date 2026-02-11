# ClaraCare — Tech Stack

## Complete Technology Breakdown

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend API** | Python + FastAPI | Best NLP libraries (spaCy, NLTK) for cognitive analysis; async/WebSocket support |
| **Voice AI** | Deepgram Voice Agent API | Sub-second latency, function calling, Nova-3 STT + Aura-2 TTS |
| **Frontend / Family Dashboard** | Next.js (React) | SSR, routing, API routes, mobile-responsive, publishable on Replit |
| **CMS / Data Layer** | Sanity (+ MCP Server) | Structured content for patient profiles, cognitive baselines, conversation logs |
| **Real-Time Search** | You.com APIs | Nostalgia Mode content + live Q&A during conversations |
| **Document Generation** | Foxit APIs | Cognitive Health Report PDFs (Document Generation + PDF Services) |
| **Admin Dashboard** | Retool (AppGen / Assist) | Internal patient management tool |
| **Deployment** | Akamai LKE (Kubernetes) | Open-source requirement + $1,000 credit; CPU + GPU nodes |
| **Phone Calling (Bonus)** | Twilio | $15.50 free credit, free phone number, official Deepgram integration |
| **Mobile App** | Replit Mobile Apps | Family dashboard published as installable mobile app |

## Detailed Technology Specifications

### Backend: Python + FastAPI
- **Version**: Python 3.11+
- **Framework**: FastAPI (async support crucial for WebSocket)
- **Key Libraries**:
  - `spaCy` — NLP for cognitive analysis (model: `en_core_web_md`)
  - `sentence-transformers` — Sentence embeddings for topic coherence (model: `all-MiniLM-L6-v2`)
  - `NLTK` — Text processing utilities
  - `websockets` — Deepgram Voice Agent streaming
  - `httpx` — Async HTTP client for API calls
  - `pydantic` — Data validation
  - `python-dotenv` — Environment variables

### Voice AI: Deepgram
- **API**: Voice Agent API (WebSocket streaming)
- **STT Model**: Nova-3 (speech-to-text)
- **TTS Voice**: Aura-2 (text-to-speech)
- **LLM**: GPT-4o (via Deepgram's think parameter)
- **Features Used**:
  - Function calling
  - Streaming audio
  - Sentiment analysis
  - Real-time transcription
- **Free Credit**: $200
- **Documentation**: 
  - [Voice Agent Getting Started](https://developers.deepgram.com/docs/voice-agent)
  - [Medical Demo Reference](https://github.com/deepgram/medical-assistant-demo)
  - [Twilio Integration](https://developers.deepgram.com/docs/twilio-integration)

### Frontend: Next.js
- **Version**: Next.js 14+ (App Router)
- **UI Framework**: React 18+
- **Styling**: Tailwind CSS
- **Charts**: Chart.js or Recharts
- **State Management**: React Context / Zustand (if needed)
- **Deployment**: Replit (with Mobile Apps feature)

### CMS: Sanity (+ MCP Server)
- **Version**: Sanity v3
- **Client**: `@sanity/client` (JavaScript/TypeScript)
- **Query Language**: GROQ
- **MCP Server**: Used during development with AI coding assistants (Cursor, Claude Code, etc.) — **required by Sanity challenge track**
  - Setup: `npx -y @sanity/mcp-server` or add to AI assistant MCP config
  - Docs: https://www.sanity.io/docs/mcp-server
- **Features**:
  - Structured content schemas
  - Real-time updates
  - Asset management
  - Versioning
- **Free Tier**: Included

### Search: You.com
- **APIs Used**:
  - Search API — General queries
  - News API — Historical events for nostalgia
  - Music/Facts — Era-specific content
- **Hackathon Resources**: https://you.com/resources/hackathon
- **Contact**: mariane.bekker@you.com

### Document Generation: Foxit
- **APIs Used**:
  - **Document Generation API** — Create Cognitive Health Report PDFs from Sanity data
  - **PDF Services API** — Post-process PDFs (compression, watermarking, finalization)
- **Use Case**: Weekly cognitive health reports downloadable by families
- **Signup**: https://developer-api.foxit.com/ (free developer account)
- **Contact**: jorge_euceda@foxitsoftware.com
- **Note**: Foxit challenge requires **BOTH** APIs in a meaningful way

### Admin Dashboard: Retool
- **Method**: Retool Assist (AppGen) → iterate to production
- **Features**:
  - Patient CRUD
  - Conversation viewing
  - System health monitoring
- **Setup**: Email hasun@retool.com with your Retool domain after creating free tenant
- **Submission**: 5-minute recording explaining problem, how Assist helped, and the solution

### Deployment: Akamai LKE
- **Platform**: Linode Kubernetes Engine
- **Free Credit**: $1,000 (90 days)
- **Signup**: https://login.linode.com/signup?promo=akm-eve-dev-hack-1000-12126-M866
- **Requirements**: 
  - Credit card needed (NOT charged unless you deploy)
  - GitHub repo must be public
- **Infrastructure**:
  - Docker containers
  - Kubernetes deployment
  - HTTPS/SSL via cert-manager
  - **GPU node** (1x `g6-gpu-1`): For NLP/ML cognitive analysis pipeline — **bonus points for GPU usage**
  - Standard nodes (2x `g6-standard-2`): For backend + dashboard pods

### Phone Calling: Twilio (Bonus)
- **Free Trial**: $15.50 credit + 1 free phone number
- **Pricing**:
  - Inbound: $0.0085/min
  - Outbound: $0.014/min
- **Integration**: Official Deepgram + Twilio WebSocket bridge
- **Free Minutes**: ~1,100 minutes with trial credit

### Mobile: Replit
- **Feature**: Replit Mobile Apps
- **Promo Code**: `REPLITDEVWEEK` (free month of Replit Core)
- **Deployment**: One-click publish to mobile

## Development Tools

### Version Control
- **GitHub**: Public repository (required for Akamai submission)
- **Repository Name**: `claracare`

### Containerization
- **Docker**: Multi-stage builds for backend + dashboard
- **Docker Compose**: Local development orchestration

### CI/CD
- **GitHub Actions**: Automated deployment to Akamai LKE

### Monitoring (Optional)
- **Logging**: Python `logging` module
- **Metrics**: Basic health checks

## API Keys & Credentials Needed

| Service | Where to Get | Who Needs |
|---------|-------------|-----------|
| Deepgram API Key | console.deepgram.com | P1, P2 |
| You.com API Key | you.com developer dashboard | P3 |
| Sanity Project ID + Dataset + Token | sanity.io project settings | P3, P4 |
| Foxit API Key | developer-api.foxit.com | P3 |
| Twilio Account SID + Auth Token | twilio.com/console | P1 |
| Akamai API Token | Linode dashboard | P5 |
| Retool API Key (optional) | Retool settings | P5 |

## Environment Variables Structure

```bash
# Backend .env
DEEPGRAM_API_KEY=xxx
YOUCOM_API_KEY=xxx
SANITY_PROJECT_ID=xxx
SANITY_DATASET=production
SANITY_TOKEN=xxx
FOXIT_API_KEY=xxx
FOXIT_API_SECRET=xxx
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1xxxyyyzzzz
SMTP_HOST=smtp.gmail.com  # for email alerts
SMTP_PORT=587
SMTP_USER=xxx
SMTP_PASSWORD=xxx

# Dashboard .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SANITY_PROJECT_ID=xxx
NEXT_PUBLIC_SANITY_DATASET=production
```

## Why This Stack?

### Deepgram Voice Agent
- Only voice AI with sub-second latency
- Function calling built-in
- Medical assistant demo proves it works for healthcare use cases

### You.com
- Real-time search for nostalgia content
- News API for historical events
- No need to scrape or build content database
- Hackathon resources: https://you.com/resources/hackathon

### Sanity (+ MCP Server)
- Structured content = longitudinal tracking
- GROQ queries perfect for time-series data
- MCP Server enables AI coding assistants to understand schemas (required by Sanity track)
- Easy to build family dashboard queries

### Next.js on Replit
- One-click mobile app deployment
- No App Store approval needed
- Beautiful, responsive UI

### Akamai LKE
- $1,000 free credit
- Open-source requirement for submission
- Kubernetes = scalable, production-ready
- GPU node available for NLP/ML bonus scoring

### Foxit
- Cognitive Health Report PDFs give families a tangible deliverable
- Uses both Document Generation API and PDF Services API (required by Foxit track)
- Low implementation effort (4-6 hours) for an additional prize track

## Alternatives Considered (& Why We Didn't Choose)

| Alternative | Why Not? |
|-------------|---------|
| OpenAI Whisper + TTS | Too slow (RTF ~0.5), no streaming, manual LLM integration |
| Firebase | Not structured enough for cognitive baseline queries |
| AWS Amplify | More complex than Replit for mobile |
| Railway/Vercel | Akamai LKE has specific prize + free credit |
| React Native | Replit Mobile = faster to ship |
