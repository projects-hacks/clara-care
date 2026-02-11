# ClaraCare — Development Timeline (10 Days)

## Timeline Overview

| Phase | Days | Focus | Key Deliverables |
|-------|------|-------|-----------------|
| Phase 0 | Day 1 (Feb 11) | Setup & Sign-ups | All accounts, repo, initial structure |
| Phase 1 | Days 2-3 (Feb 12-13) | Voice Agent Core | Clara talks, saves conversations |
| Phase 2 | Days 4-5 (Feb 14-15) | Cognitive Engine + Nostalgia | Metrics computed, nostalgia works |
| Phase 3 | Days 5-7 (Feb 15-17) | Family Dashboard | Mobile app deployed |
| Phase 4 | Days 7-9 (Feb 17-19) | Bonus Features + Deployment | Phone calls, deployed to Akamai |
| Phase 5 | Days 9-10 (Feb 19-20) | Demo + Submission | Video, DevPost, presentation |

---

## Phase 0 — Setup (Day 1: February 11)

### Morning (4 hours)

#### All Team Members
- [ ] Register on DevPost for DeveloperWeek 2026 Hackathon
- [ ] RSVP on Eventbrite (link from DevPost)
- [ ] Join team Slack/Discord channel
- [ ] Review all docs in `/docs` directory

#### P5 — DevOps Lead
- [ ] Create GitHub repo `claracare` (public)
- [ ] Create monorepo directory structure
- [ ] Add `.gitignore`, `LICENSE` (MIT), initial `README.md`
- [ ] Push initial structure to GitHub
- [ ] Sign up for Akamai/Linode ($1,000 credit) — URL: `https://login.linode.com/signup?promo=akm-eve-dev-hack-1000-12126-M866`
- [ ] Provision LKE cluster:
  - CPU pool: 2x `g6-standard-2` nodes
  - GPU pool: 1x `g6-gpu-1` node (for cognitive analysis — Akamai bonus points)
- [ ] Set up `kubectl` with kubeconfig

#### P1 — Voice AI Engineer
- [ ] Sign up for Deepgram ($200 credit)
- [ ] Sign up for Twilio (free trial)
- [ ] Read Deepgram Voice Agent docs
- [ ] Read Deepgram + Twilio integration docs
- [ ] Clone medical assistant demo, run locally
- [ ] Verify API key works with simple test

#### P2 — Backend Engineer
- [ ] Set up Python virtual environment in `/backend`
- [ ] Create `requirements.txt` with all dependencies
- [ ] Install spaCy: `python -m spacy download en_core_web_md`
- [ ] Install NLTK: `nltk.download('punkt')`, `nltk.download('stopwords')`
- [ ] Create FastAPI app skeleton in `app/main.py`
- [ ] Test: `uvicorn app.main:app --reload`

#### P3 — Integrations Engineer
- [ ] Sign up for Sanity (free tier)
- [ ] Sign up for You.com — review hackathon resources: https://you.com/resources/hackathon
- [ ] Sign up for Foxit — URL: https://developer-api.foxit.com/ (get API key + secret)
- [ ] Create Sanity project "claracare"
- [ ] Create all 4 schemas in `/sanity/schemas` (patient, conversation, familyMember, wellnessDigest)
- [ ] Deploy Sanity Studio: `sanity deploy`
- [ ] **Set up Sanity MCP Server** in AI coding assistant (required by Sanity track):
  ```bash
  npx -y @sanity/mcp-server  # Or add to .cursor/mcp.json
  ```
- [ ] Create test patient "Dorothy" in Studio

#### P4 — Frontend Engineer
- [ ] Sign up for Replit with code `REPLITDEVWEEK`
- [ ] Create Next.js app "claracare-dashboard"
- [ ] Explore Replit Mobile Apps feature
- [ ] Set up Tailwind CSS
- [ ] Create page structure (empty files for now)
- [ ] Sketch UI wireframes on paper/Figma

### Afternoon (3 hours)

#### Team Sync (30 min)
- Demo: P1 shows Deepgram medical assistant demo
- Demo: P3 shows Sanity Studio with test patient
- Demo: P4 shows Next.js app running on Replit
- Demo: P5 shows Kubernetes cluster running

#### Individual Work
- **P1**: Create `backend/app/voice/persona.py` with Clara's initial system prompt
- **P2**: Implement basic API routes structure
- **P3**: Write GROQ queries for patient retrieval
- **P4**: Set up charting library (Chart.js or Recharts)
- **P5**: Sign up for Retool, email hasun@retool.com

### Evening (Optional)

#### All Team Members
- Read through all `/docs` files again
- Set up local development environment
- Test Docker Compose setup: `docker-compose up`

### End-of-Day Checklist
- ✅ All team members registered for hackathon
- ✅ All API accounts created
- ✅ GitHub repo exists with basic structure
- ✅ Backend runs locally
- ✅ Dashboard runs locally
- ✅ Sanity Studio has test data
- ✅ Akamai cluster provisioned

---

## Phase 1 — Voice Agent Core (Days 2-3: February 12-13)

### Goals
- Get Deepgram Voice Agent working
- Clara can have basic conversations
- Conversations are saved to Sanity
- Simple web interface for testing

### Day 2 (February 12)

#### Morning (4 hours)

**P1 — Voice AI Engineer**
- [ ] Implement `backend/app/voice/agent.py`:
  - WebSocket connection to Deepgram
  - Audio streaming (receive from browser, send to Deepgram)
  - Handle Deepgram events (session started, audio, function calls)
- [ ] Create `backend/app/routes/websocket.py`:
  - FastAPI WebSocket endpoint `/ws/voice`
  - Bridge browser audio ↔ Deepgram
- [ ] Test with Deepgram console first (no browser yet)

**P2 — Backend Engineer**
- [ ] Implement `backend/app/routes/patients.py`:
  - `GET /patients/{id}` — Get patient profile
  - `POST /patients` — Create patient (for testing)
- [ ] Implement `backend/app/routes/conversations.py`:
  - `GET /conversations?patient_id={id}` — List conversations
  - `POST /conversations` — Create conversation
- [ ] Basic error handling and validation

**P3 — Integrations Engineer**
- [ ] Implement `backend/app/sanity_client/client.py`:
  - Sanity HTTP API wrapper
  - Methods: `get_patient()`, `create_conversation()`, `update_patient()`
- [ ] Implement `backend/app/sanity_client/queries.py`:
  - GROQ query for patient + recent conversations
  - GROQ query for conversation history
- [ ] Test queries in Sanity Vision

**P4 — Frontend Engineer**
- [ ] Research charting libraries
- [ ] Design color palette and typography
- [ ] Create component stubs

**P5 — DevOps Lead**
- [ ] Set up Retool tenant
- [ ] Begin AppGen admin dashboard
- [ ] Support other team members with setup issues

#### Afternoon (4 hours)

**P1 + P2 — Pair Programming**
- [ ] Implement function calling in `backend/app/voice/functions.py`:
  - `get_patient_context(patient_id: str)` → calls P3's Sanity client
  - `save_conversation(...)` → calls P3's Sanity client
- [ ] Register functions with Deepgram Voice Agent
- [ ] Test function calls are triggered correctly

**P3 — Solo Work**
- [ ] Implement function handlers:
  - `def handle_get_patient_context(patient_id)` → query Sanity
  - `def handle_save_conversation(...)` → save to Sanity
- [ ] Test with mock data

**P4 — Solo Work**
- [ ] Start building Home page UI (without real data)

**P5 — Solo Work**
- [ ] Write `docker-compose.yml` for local dev
- [ ] Test Docker build for backend

#### Evening (Optional)
- **P1**: Start building simple web voice interface (`voice-web/`)

### Day 3 (February 13)

#### Morning (4 hours)

**P1 — Voice AI Engineer**
- [ ] Build `voice-web/index.html`:
  - Microphone permission request
  - WebSocket connection to backend
  - Audio playback
- [ ] Build `voice-web/app.js`:
  - Capture mic audio using Web Audio API
  - Send audio to backend via WebSocket
  - Receive audio from backend, play it
- [ ] Test full loop: Browser → FastAPI → Deepgram → FastAPI → Browser

**P2 — Backend Engineer**
- [ ] Add logging throughout backend
- [ ] Error handling for WebSocket disconnects
- [ ] Test API routes with Postman/curl

**P3 — Integrations Engineer**
- [ ] Implement `search_realtime` function:
  - `backend/app/nostalgia/youcom_client.py` — You.com API wrapper
  - Test with simple queries: "What's the weather in San Francisco?"
- [ ] Seed more test data in Sanity (2-3 test conversations)

**P4 — Frontend Engineer**
- [ ] Build `src/lib/api.ts` — Backend API client
- [ ] Test fetching patient data from backend
- [ ] Display test data on Home page

**P5 — DevOps Lead**
- [ ] Support team with blockers
- [ ] Start writing deployment documentation

#### Afternoon (4 hours)

**P1 — Voice AI Engineer**
- [ ] Refine Clara's persona prompt:
  - Warm, patient tone
  - Memory of past conversations
  - Natural medication reminders
- [ ] Test conversations with different prompts
- [ ] Record test conversation for later demo

**All Team Members — Integration Testing**
- [ ] Full flow test: Talk to Clara in browser → transcript saved in Sanity
- [ ] Verify function calling works: Clara fetches patient context
- [ ] Bug fixes

**Team Sync (30 min)**
- Demo: Talk to Clara live
- Review: What's working, what's broken
- Plan: Adjustments for Phase 2

### End of Phase 1 Milestone
✅ **Clara can have conversations in the browser**
✅ **Conversations are saved to Sanity with transcripts**
✅ **Clara knows patient's name and context**
✅ **search_realtime function works (basic)**

---

## Phase 2 — Cognitive Engine + Nostalgia (Days 4-5: February 14-15)

### Goals
- Cognitive metrics computed for every conversation
- Baseline established after 7 conversations
- Nostalgia Mode triggers and works
- Alerts sent when thresholds crossed
- Wellness digest generated

### Day 4 (February 14)

#### Morning (4 hours)

**P2 — Backend Engineer**
- [ ] Implement `backend/app/cognitive/analyzer.py`:
  - Load spaCy model `en_core_web_md`
  - Function: `compute_vocabulary_diversity(text)` → TTR
  - Function: `compute_topic_coherence(sentences)` → cosine similarity
  - Function: `count_repetitions(text)` → repetition rate
  - Function: `count_word_finding_pauses(text)` → "um", "uh", pauses
  - Function: `analyze_conversation(transcript)` → dict of all metrics
- [ ] Test with real conversation transcripts

**P3 — Integrations Engineer**
- [ ] Implement Nostalgia Mode in `backend/app/nostalgia/era.py`:
  - Function: `calculate_golden_years(birth_year)` → (start_year, end_year)
  - Function: `fetch_nostalgia_content(era, patient_preferences)` → You.com query
  - Content types: music, news, sports, pop culture
- [ ] Test with Dorothy (born 1945 → golden years 1960-1970)
- [ ] Implement `search_nostalgia` function for Deepgram
- [ ] **Start Foxit Cognitive Health Report** (`backend/app/reports/`):
  - Create DOCX template in `reports/templates/cognitive_report.docx`
  - Implement `foxit_client.py` — wrapper for Document Generation + PDF Services APIs
  - Implement `generator.py` — collects patient data from Sanity, generates report

**P1 — Voice AI Engineer**
- [ ] Add nostalgia trigger detection:
  - Deepgram sentiment analysis
  - Keyword detection ("old days", "I remember", "back then")
- [ ] Register `search_nostalgia` function with Deepgram
- [ ] Test: Say something sad → nostalgia content triggered

**P4 — Frontend Engineer**
- [ ] Build Conversation History page
- [ ] Build ConversationCard component
- [ ] Fetch real data from backend

#### Afternoon (4 hours)

**P2 — Backend Engineer**
- [ ] Implement `backend/app/cognitive/baseline.py`:
  - Function: `establish_baseline(patient_id)` → compute avg of first 7 conversations
  - Function: `update_baseline(patient_id)` → save to Sanity
  - Function: `check_baseline_ready(patient_id)` → True if 7+ conversations
- [ ] Implement `backend/app/cognitive/alerts.py`:
  - Function: `check_thresholds(metrics, baseline)` → list of alerts
  - Threshold: >20% deviation for 3+ consecutive calls
  - Function: `send_alert(alert, family_contacts)` → email/SMS

**P3 — Integrations Engineer**
- [ ] Implement wellness digest generation:
  - After each conversation, create wellnessDigest in Sanity
  - Summary, mood, cognitive score, recommendations
- [ ] Update `save_conversation` function to include:
  - Cognitive metrics
  - Nostalgia engagement score
  - Alerts

**P1 + P2 — Integration**
- [ ] Call cognitive analyzer from `save_conversation` function
- [ ] Save metrics to Sanity conversation document

### Day 5 (February 15)

#### Morning (4 hours)

**P2 — Backend Engineer**
- [ ] Implement `backend/app/notifications/email.py`:
  - SMTP email sending
  - Template for alerts
  - Template for daily digest
- [ ] Test email sending

**P3 — Integrations Engineer**
- [ ] Create 7 test conversations in Sanity for Dorothy
- [ ] Run baseline establishment
- [ ] Verify baseline is saved correctly

**All Team Members — Integration Testing**
- [ ] Full conversation with cognitive analysis
- [ ] Trigger nostalgia (say something sad)
- [ ] Verify metrics are saved
- [ ] Verify wellness digest is created
- [ ] Trigger alert (manually set bad metrics)

#### Afternoon (4 hours)

**P2 — Backend Engineer**
- [ ] Implement `GET /wellness-digests?patient_id={id}` route
- [ ] Implement `GET /cognitive-trends?patient_id={id}` route
  - Returns time-series data for charts
- [ ] Implement `GET /reports/{patient_id}/download` route (Foxit PDF)

**P3 — Integrations Engineer**
- [ ] Write comprehensive GROQ queries for dashboard:
  - Recent conversations with summaries
  - Cognitive metrics over time
  - All alerts sorted by severity
  - Latest wellness digest
- [ ] **Complete Foxit report integration**:
  - Test Document Generation API with real Sanity data
  - Test PDF Services API for compression + watermarking
  - Verify PDF download endpoint works end-to-end

**P1 — Voice AI Engineer**
- [ ] Refine Clara's responses when nostalgia is triggered
- [ ] Test different nostalgia content types
- [ ] Record demo conversation with nostalgia

**P4 — Frontend Engineer**
- [ ] Start building Trends page with Chart.js

**Team Sync (30 min)**
- Demo full flow: Sad conversation → nostalgia → metrics → digest
- Review cognitive scores
- Plan Phase 3

### End of Phase 2 Milestone
✅ **Cognitive metrics computed and saved**
✅ **Baseline established after 7 conversations**
✅ **Nostalgia Mode triggers and delivers content**
✅ **Alerts sent when thresholds crossed**
✅ **Wellness digest generated after each call**

---

## Phase 3 — Family Dashboard (Days 5-7: February 15-17)

### Goals
- All dashboard pages built
- Cognitive charts working
- Beautiful UI
- Mobile app deployed on Replit

### Day 5 Afternoon → Day 6 (February 15-16)

**P4 — Frontend Engineer (Full Focus)**

#### Home Page — Today's Summary
- [ ] Mood indicator (emoji based on overall mood)
- [ ] Key highlights (bullet points from digest)
- [ ] Cognitive score (0-100 with color coding)
- [ ] Quick actions (call patient, view alerts)
- [ ] Test with real data from backend

#### Conversation History Page
- [ ] List of all conversations (newest first)
- [ ] Each card shows: timestamp, duration, mood, summary
- [ ] Click to expand full transcript
- [ ] Filter by date range
- [ ] Pagination

#### Cognitive Trends Page
- [ ] Line chart: Vocabulary diversity over time
- [ ] Line chart: Response latency over time
- [ ] Line chart: Topic coherence over time
- [ ] Line chart: Repetition rate over time
- [ ] Baseline overlay (dotted line)
- [ ] Alert markers on chart where thresholds crossed
- [ ] Date range selector (7 days, 30 days, 90 days, all time)

#### Alerts Page
- [ ] Timeline view of all alerts
- [ ] Color-coded by severity (red=high, yellow=medium, blue=low)
- [ ] Filter by type (distress, cognitive decline, medication)
- [ ] Mark as "reviewed"
- [ ] Click to see related conversation

#### Nostalgia Preferences Page
- [ ] Edit favorite topics
- [ ] Edit music preferences
- [ ] Edit topics to avoid
- [ ] Preview nostalgia content (test with You.com)

#### Settings Page
- [ ] Edit call schedule time
- [ ] Edit medications (add/remove)
- [ ] Edit family contacts
- [ ] Notification preferences (daily digest, instant alerts)

**P2 + P3 — Backend Support for P4**
- [ ] Ensure all API routes return correct data
- [ ] Add pagination to conversation list
- [ ] Optimize GROQ queries for dashboard
- [ ] CORS setup for frontend

**P5 — DevOps**
- [ ] Continue Retool admin dashboard
- [ ] Start Docker builds for deployment

### Day 7 (February 17)

**P4 — Frontend Engineer**
- [ ] UI polish:
  - Consistent spacing and typography
  - Color palette refinement
  - Loading states and skeletons
  - Error handling (empty states, network errors)
  - Responsive design (mobile, tablet, desktop)
- [ ] Dark mode (if time permits)
- [ ] Accessibility (ARIA labels, keyboard navigation)

#### Replit Mobile Deployment
- [ ] Test app on Replit
- [ ] Click "Publish as Mobile App"
- [ ] Test on real mobile device (scan QR code)
- [ ] Share link with team
- [ ] Screenshot for demo

**Other Team Members**
- [ ] Test dashboard on different devices
- [ ] Give feedback to P4

### End of Phase 3 Milestone
✅ **All 6 dashboard pages built and working**
✅ **Cognitive charts display real data**
✅ **UI is polished and professional**
✅ **Mobile app deployed on Replit**

---

## Phase 4 — Bonus Features + Deployment (Days 7-9: February 17-19)

### Day 7 Afternoon → Day 8 (February 17-18)

**P1 — Voice AI Engineer**
- [ ] Twilio integration in `backend/app/voice/twilio_bridge.py`:
  - WebSocket bridge: Twilio ↔ FastAPI ↔ Deepgram
  - Reference: Deepgram + Twilio repo
- [ ] Test with Twilio phone number
- [ ] Make real phone call to Clara
- [ ] Record demo of phone call

**P5 — DevOps Lead**
- [ ] Retool admin dashboard completion:
  - Patient CRUD
  - View all conversations
  - System health (API uptime, Deepgram credits)
  - Manual alert creation
- [ ] Iterate AppGen dashboard to production quality

#### Docker & Kubernetes
- [ ] Finalize `backend/Dockerfile`
- [ ] Finalize `dashboard/Dockerfile`
- [ ] Build images: `docker build -t claracare-backend:latest ./backend`
- [ ] Push to Docker Hub or GitHub Container Registry
- [ ] Create Kubernetes manifests in `/k8s`:
  - `namespace.yaml`
  - `backend-deployment.yaml`
  - `backend-service.yaml`
  - `dashboard-deployment.yaml`
  - `dashboard-service.yaml`
  - `ingress.yaml`
  - `configmap.yaml`
  - `secrets.yaml` (example only, real secrets via kubectl)

### Day 9 (February 19)

**P5 — DevOps Lead (All Day)**

#### Akamai LKE Deployment
- [ ] Apply Kubernetes manifests:
  ```bash
  kubectl apply -f k8s/namespace.yaml
  kubectl create secret generic claracare-secrets --from-env-file=.env
  kubectl apply -f k8s/
  ```
- [ ] Verify pods are running: `kubectl get pods`
- [ ] Check logs: `kubectl logs -f deployment/backend`
- [ ] Set up ingress with HTTPS:
  - Install cert-manager
  - Configure Let's Encrypt
  - Get SSL certificate
- [ ] Point domain to Load Balancer IP (or use LKE-provided URL)
- [ ] Test live deployment:
  - Talk to Clara via web
  - View dashboard
  - Make API calls

**P3 — Documentation**
- [ ] Write comprehensive README.md:
  - Project description
  - Architecture diagram
  - Tech stack
  - Setup instructions
  - Deployment instructions
  - Environment variables
  - API documentation
  - Team members
  - Hackathon info
- [ ] Add screenshots to README
- [ ] Code comments cleanup

**P2 — Testing**
- [ ] End-to-end testing on deployed system
- [ ] Bug fixes

**P1 + P4 — Testing**
- [ ] Test phone calls
- [ ] Test mobile app
- [ ] Bug fixes

### End of Phase 4 Milestone
✅ **Twilio phone integration works**
✅ **Retool admin dashboard complete**
✅ **System deployed on Akamai LKE**
✅ **HTTPS working**
✅ **README.md comprehensive**

---

## Phase 5 — Demo + Submission (Days 9-10: February 19-20)

### Day 9 Afternoon (February 19)

**P5 + P1 — Demo Script Writing**
- [ ] Write 3-minute demo script (see `09-DEMO-SCRIPT.md`)
- [ ] Rehearse demo flow
- [ ] Prepare demo data (Dorothy with interesting conversation history)

**P3 + P5 — DevPost Write-Up**
- [ ] Start writing DevPost project page
- [ ] Tailor descriptions for each of 9 challenge tracks

### Day 10 (February 20)

#### Morning (4 hours)

**P5 — Video Production**
- [ ] Record demo video (3 minutes):
  - Opening: Problem statement
  - Live demo: Talk to Clara (web or phone)
  - Show nostalgia mode triggering
  - Show family dashboard on mobile
  - Show cognitive trend charts
  - Show alert
  - Architecture diagram
  - Closing: Impact statement
- [ ] Edit video (add music, transitions, captions)
- [ ] Export and upload to YouTube (unlisted)

**P1 — Voice Recording**
- [ ] Record "Dorothy" voice for demo
- [ ] Record Clara's responses
- [ ] Ensure audio quality is excellent

**P3 — DevPost Submissions (8 Tracks)**

| Track | Tailored Write-Up |
|-------|------------------|
| Overall Winner | Real-world problem, business feasibility, technical depth |
| Deepgram Smart Listener | Cognitive metrics from speech patterns |
| Deepgram Voice Operator | Function calling: meds, nostalgia, alerts |
| You.com | Nostalgia Mode + real-time Q&A |
| Sanity | Longitudinal tracking via structured content + MCP Server |
| Replit Mobile | Published mobile app |
| Akamai | Open-source on LKE + GPU-accelerated cognitive analysis |
| Retool | Admin dashboard (5-min walkthrough video) |
| Foxit | Cognitive Health Report PDFs (Doc Gen + PDF Services) |

- [ ] Submit to all 9 tracks with tailored descriptions
- [ ] Add screenshots for each track
- [ ] Add video link
- [ ] Add GitHub repo link
- [ ] Add live demo link
- [ ] Add team member info

#### Afternoon (4 hours)

**P5 — Live Presentation Prep (If Top 5)**
- [ ] Create 5-minute slide deck:
  - Slide 1: Problem (54M caregivers)
  - Slide 2: Solution (Clara overview)
  - Slide 3: Demo (embedded video or live)
  - Slide 4: Architecture
  - Slide 5: Tech stack (8 sponsor logos)
  - Slide 6: Business case ($9.7B TAM)
  - Slide 7: What's next
  - Slide 8: Team
- [ ] Rehearse presentation
- [ ] Prepare Q&A responses

**All Team Members**
- [ ] Review DevPost submissions
- [ ] Final bug fixes
- [ ] Celebrate! 🎉

#### Evening

**Team Sync (Final)**
- [ ] Review all submissions
- [ ] Ensure video is uploaded
- [ ] Ensure GitHub repo is public and has clear README
- [ ] Ensure live demo is accessible
- [ ] Submit before deadline

### End of Phase 5 Milestone
✅ **3-minute demo video complete and uploaded**
✅ **Submitted to all 9 challenge tracks on DevPost**
✅ **Live presentation prepared (if needed)**
✅ **GitHub repo is public and polished**
✅ **Project is DONE**

---

## Daily Standup Template

**Time**: Every morning at 9 AM (15 minutes)

**Format** (each person shares):
1. What did I complete yesterday?
2. What am I working on today?
3. Any blockers?

**Example**:
> **P1**: Yesterday I got the Deepgram WebSocket working. Today I'm building the web voice interface. No blockers.
>
> **P2**: Yesterday I implemented the cognitive analyzer. Today I'm working on baseline establishment. Blocker: Need P3's Sanity client to save baselines.
>
> **P3**: I'll have the Sanity client done by 11 AM. Yesterday I finished all the schemas. Today I'm implementing GROQ queries and the Sanity client.

---

## Risk Mitigation Plan

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Deepgram latency too high | Low | High | Use streaming API, optimize audio format |
| You.com returns poor content | Medium | Medium | Pre-curate backup nostalgia database |
| Cognitive metrics too noisy | Medium | Medium | Use rolling averages, require 3+ min calls |
| Replit mobile publishing fails | Low | Medium | Fallback: deploy as PWA |
| Akamai deployment issues | Medium | High | Start early (Day 7), fallback to Railway |
| Twilio integration blocks work | Low | Low | It's bonus — P1 does after core works |
| Team member unavailable | Medium | High | Cross-training, backup assignments |
| API rate limits hit | Low | Medium | Monitor usage, implement caching |

---

## Buffer Time

**Built-in buffers**:
- Phase 3 overlaps with Phase 2 (Days 5-7)
- Phase 4 has 3 days for what could be done in 2
- Phase 5 has 2 days for demo/submission

**If ahead of schedule**:
- Add features: Weekly report email, SMS reminders, voice customization
- Polish UI more
- Add animations
- Write more tests
- Improve documentation

**If behind schedule**:
- Cut Twilio phone integration (bonus feature)
- Cut Retool admin dashboard (use Sanity Studio instead)
- Simplify dashboard (fewer pages)
- Use pre-recorded demo instead of live
- Skip dark mode and fancy UI polish

---

## Success Metrics

### Technical Metrics
- [ ] Clara responds in < 1 second
- [ ] Conversation success rate > 95%
- [ ] Cognitive metrics compute correctly
- [ ] Dashboard loads in < 2 seconds
- [ ] System handles 10 concurrent conversations
- [ ] Uptime > 99% during hackathon

### Hackathon Metrics
- [ ] Submitted to all 9 challenge tracks
- [ ] Demo video is compelling (< 3 minutes)
- [ ] GitHub repo has > 100 commits
- [ ] README is comprehensive
- [ ] Live demo works without bugs
- [ ] Presentation is polished (if needed)

### Team Metrics
- [ ] All team members contribute code
- [ ] No major conflicts or blockers
- [ ] Daily standups happened every day
- [ ] Everyone understands the full system
- [ ] Team has fun! 😊
