# ClaraCare — Team Roles & Responsibilities

## Team of 5 — Role Assignments

### P1 — Voice AI Engineer
**Primary Focus**: Deepgram Voice Agent integration and phone calling

#### Responsibilities
- Deepgram Voice Agent WebSocket implementation
- Audio streaming (browser/Twilio → Deepgram → browser/Twilio)
- Function calling setup and testing
- Clara persona prompt engineering
- Twilio phone integration (bonus feature)
- Voice quality optimization

#### Key Deliverables
- Working WebSocket endpoint in FastAPI
- Clara persona system prompt
- Function definitions (JSON schema for Deepgram)
- Twilio bridge module (if time permits)
- Voice demo recordings

#### Skills Needed
- WebSocket programming
- Audio streaming
- API integration
- Understanding of voice AI

#### Day 1 Tasks
- Sign up for Deepgram ($200 credit)
- Sign up for Twilio (free trial)
- Read Deepgram Voice Agent docs
- Run medical assistant demo locally
- Read Deepgram + Twilio integration docs

#### Key Files Owned
- `backend/app/voice/agent.py`
- `backend/app/voice/persona.py`
- `backend/app/voice/functions.py`
- `backend/app/voice/twilio_bridge.py`
- `voice-web/index.html`
- `voice-web/app.js`

---

### P2 — Backend / NLP Engineer
**Primary Focus**: FastAPI server, cognitive analysis engine, and alert system

#### Responsibilities
- FastAPI application setup and structure
- Cognitive analysis engine (spaCy/NLTK)
- Baseline establishment algorithms
- Alert threshold detection
- Wellness digest generation
- Email/SMS notification system
- API route scaffolding

#### Key Deliverables
- FastAPI server with all routes
- Cognitive metrics calculator
- Baseline tracking system
- Alert logic with threshold detection
- Notification modules (email/SMS)
- API documentation

#### Skills Needed
- Python FastAPI
- NLP (spaCy, NLTK)
- Async programming
- Data analysis

#### Day 1 Tasks
- Set up FastAPI project structure
- Install spaCy and download `en_core_web_md` model
- Install NLTK and download required data
- Read cognitive metrics documentation
- Set up email SMTP credentials

#### Key Files Owned
- `backend/app/main.py`
- `backend/app/cognitive/analyzer.py`
- `backend/app/cognitive/baseline.py`
- `backend/app/cognitive/alerts.py`
- `backend/app/notifications/email.py`
- `backend/app/notifications/sms.py`
- `backend/app/routes/*.py`
- `backend/requirements.txt`

---

### P3 — Full-Stack / Integrations Engineer
**Primary Focus**: Sanity CMS, You.com API, and backend integrations

#### Responsibilities
- Sanity project setup and schema design
- Sanity MCP Server configuration
- Sanity Python client wrapper
- GROQ query development
- You.com API integration
- Foxit Document Generation + PDF Services integration
- Nostalgia Mode logic
- Era calculation and content fetching
- Seed data creation
- Backend API route implementation

#### Key Deliverables
- Sanity schemas (4 content types)
- Sanity MCP Server setup
- Sanity Python client
- GROQ queries for dashboard
- You.com API wrapper
- Nostalgia Mode engine
- Foxit Cognitive Health Report templates + integration
- Test patient data ("Dorothy")
- Function implementations for Sanity operations

#### Skills Needed
- Sanity CMS
- GROQ query language
- API integration
- Python backend development
- Data modeling

#### Day 1 Tasks
- Sign up for Sanity (free tier)
- Sign up for You.com (get API key)
- Sign up for Foxit (developer-api.foxit.com)
- Read Sanity Getting Started docs
- Install Sanity MCP Server
- Read You.com Hackathon guide PDF
- Create Sanity project "claracare"
- Design schema drafts

#### Key Files Owned
- `sanity/schemas/*.ts`
- `sanity/sanity.config.ts`
- `backend/app/sanity_client/client.py`
- `backend/app/sanity_client/queries.py`
- `backend/app/nostalgia/era.py`
- `backend/app/nostalgia/youcom_client.py`
- `backend/app/reports/foxit_client.py`
- `backend/app/reports/generator.py`
- `backend/app/routes/patients.py`
- `backend/app/routes/conversations.py`
- `backend/app/routes/wellness.py`

---

### P4 — Frontend Engineer
**Primary Focus**: Next.js family dashboard and mobile app deployment

#### Responsibilities
- Next.js application setup (App Router)
- All dashboard pages and components
- Chart.js/Recharts visualizations
- Backend API client
- Mobile-responsive UI design
- Replit mobile app deployment
- UI/UX polish

#### Key Deliverables
- Complete family dashboard (5+ pages)
- Cognitive trend charts
- Conversation history UI
- Alert timeline
- Mobile app published on Replit
- Beautiful, polished UI

#### Skills Needed
- React / Next.js
- TypeScript
- Tailwind CSS
- Data visualization
- Responsive design

#### Day 1 Tasks
- Sign up for Replit with promo code `REPLITDEVWEEK`
- Create Next.js app on Replit
- Explore Replit Mobile Apps feature
- Set up Tailwind CSS
- Design UI mockups/wireframes
- Choose charting library (Chart.js or Recharts)

#### Key Files Owned
- `dashboard/src/app/**/*`
- `dashboard/src/components/**/*`
- `dashboard/src/lib/api.ts`
- `dashboard/package.json`
- `dashboard/next.config.js`
- `dashboard/tailwind.config.js`

---

### P5 — DevOps / Demo Lead
**Primary Focus**: Infrastructure, deployment, and demo production

#### Responsibilities
- GitHub repository setup and management
- Docker and Docker Compose configuration
- Akamai LKE Kubernetes deployment
- Retool admin dashboard
- CI/CD pipeline (GitHub Actions)
- Domain and HTTPS setup
- Demo video production
- DevPost submission writing
- Live presentation preparation

#### Key Deliverables
- Public GitHub repo
- Docker images for backend + dashboard
- Kubernetes manifests
- Working deployment on Akamai LKE
- Retool admin dashboard
- 3-minute demo video
- DevPost project page (9 submissions)
- 5-minute live presentation

#### Skills Needed
- Docker / Kubernetes
- CI/CD
- Infrastructure as code
- Video editing
- Technical writing
- Presentation skills

#### Day 1 Tasks
- Create GitHub repo `claracare` (public)
- Sign up for Akamai/Linode ($1,000 credit)
- Sign up for Retool
- Email hasun@retool.com with domain
- Set up monorepo structure
- Create README.md skeleton
- Provision Akamai LKE cluster (CPU + GPU node)

#### Key Files Owned
- `README.md`
- `LICENSE`
- `.github/workflows/*.yml`
- `docker-compose.yml`
- `backend/Dockerfile`
- `dashboard/Dockerfile`
- `k8s/*.yaml`
- `docs/architecture.md`
- `docs/demo-script.md`
- DevPost submission text

---

## Collaboration Model

### Daily Standups
**Time**: Every morning at 9 AM (15 minutes)

**Format**:
- What did you complete yesterday?
- What are you working on today?
- Any blockers?

### Parallel Work Streams

#### Stream 1: Voice + Backend (P1 + P2)
- Days 2-3: Get voice agent working
- Days 4-5: Add cognitive analysis
- P1 and P2 work closely together

#### Stream 2: Data + Integrations (P3)
- Days 2-3: Sanity setup + You.com integration
- Days 4-5: Nostalgia Mode + backend routes
- P3 works independently, coordinates with P1/P2 for function calling

#### Stream 3: Frontend (P4)
- Days 5-7: Build all dashboard pages
- Day 7: Deploy to Replit as mobile app
- P4 works independently, coordinates with P3 for API

#### Stream 4: Infrastructure (P5)
- Day 1: Setup (repo, accounts, cluster)
- Days 7-8: Deployment
- Days 9-10: Demo + submission
- P5 supports everyone, then focuses on deployment and demo

### Code Review
- All PRs require 1 approval
- P5 reviews infrastructure changes
- P1/P2 cross-review backend
- P3 reviews data/integration code
- P4 reviews frontend

### Communication
- **Primary**: Slack or Discord channel
- **Code**: GitHub PRs and issues
- **Docs**: This memory bank in `/docs`
- **Meetings**: Daily standup + ad-hoc pairing sessions

## Work Distribution by Phase

### Phase 0 — Setup (Day 1)
| Person | Hours | Tasks |
|--------|-------|-------|
| P1 | 4.5 | Sign-ups, read Deepgram docs, run demo |
| P2 | 2 | FastAPI setup, spaCy installation |
| P3 | 4 | Sign-ups, read docs, create Sanity project |
| P4 | 3 | Sign up Replit, create Next.js app |
| P5 | 3 | GitHub repo, Akamai account, cluster setup |

### Phase 1 — Voice Agent Core (Days 2-3)
| Person | Hours | Tasks |
|--------|-------|-------|
| P1 | 12 | Deepgram WebSocket, Clara persona, browser interface |
| P2 | 6 | FastAPI routes, function handlers |
| P3 | 8 | Sanity client, function implementations, seed data |
| P4 | 0 | (Not started yet) |
| P5 | 0 | (Support only) |

### Phase 2 — Cognitive Engine + Nostalgia (Days 4-5)
| Person | Hours | Tasks |
|--------|-------|-------|
| P1 | 2 | Nostalgia trigger detection |
| P2 | 11 | Cognitive analyzer, baseline, alerts, digests |
| P3 | 7 | Nostalgia Mode, You.com integration |
| P4 | 0 | (Not started yet) |
| P5 | 0 | (Support only) |

### Phase 3 — Family Dashboard (Days 5-7)
| Person | Hours | Tasks |
|--------|-------|-------|
| P1 | 0 | (Done with core work) |
| P2 | 3 | Backend routes for dashboard |
| P3 | 0 | (Done with core work) |
| P4 | 22 | Build all pages, charts, UI polish, Replit deploy |
| P5 | 0 | (Support only) |

### Phase 4 — Bonus + Deployment (Days 7-9)
| Person | Hours | Tasks |
|--------|-------|-------|
| P1 | 5 | Twilio phone integration |
| P2 | 0 | (Testing only) |
| P3 | 2 | README, documentation |
| P4 | 0 | (Done with dashboard) |
| P5 | 10 | Retool, Docker, Kubernetes, deployment |

### Phase 5 — Demo + Submission (Days 9-10)
| Person | Hours | Tasks |
|--------|-------|-------|
| P1 | 3 | Demo script, voice recording |
| P2 | 0 | (Testing only) |
| P3 | 4 | DevPost write-ups for 9 tracks |
| P4 | 0 | (Testing only) |
| P5 | 7 | Video editing, DevPost submission, presentation prep |

## Skills Matrix

| Skill | P1 | P2 | P3 | P4 | P5 |
|-------|----|----|----|----|---- |
| Python | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| FastAPI | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| WebSocket | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ |
| NLP | ⭐ | ⭐⭐⭐ | ⭐ | - | - |
| React/Next.js | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| TypeScript | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| Sanity/GROQ | - | - | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Docker/K8s | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ |
| Video/Demo | ⭐⭐ | - | ⭐ | ⭐⭐ | ⭐⭐⭐ |

## Emergency Contact Protocol

If someone is blocked or unavailable:

| Primary | Backup | Area |
|---------|---------|------|
| P1 | P2 | Voice Agent issues |
| P2 | P3 | Backend/API issues |
| P3 | P2 | Sanity/data issues |
| P4 | P3 | Frontend/UI issues |
| P5 | P3 | Deployment issues |

## Success Metrics

### Individual Metrics
- P1: Clara has natural conversations, function calling works
- P2: Cognitive metrics compute correctly, alerts trigger
- P3: Nostalgia Mode works, data flows through Sanity
- P4: Dashboard looks professional, mobile app deployed
- P5: System runs on Akamai, demo video is compelling

### Team Metrics
- All 9 challenge track submissions completed
- Live demo works without errors
- Code is on public GitHub
- System is deployed and accessible
