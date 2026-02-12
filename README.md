# ClaraCare — AI Elder Care Companion

> *Because no one should age alone.*

**DeveloperWeek 2026 Hackathon Project**  
**Dates**: February 11-20, 2026

---

## 🎯 Overview

ClaraCare is an AI voice companion that helps 54 million Americans care for their aging parents. Clara calls elderly people living alone every morning, has warm natural conversations, tracks cognitive health through speech analysis, and sends families a daily wellness digest.

**Think**: $15/month AI caregiver that catches early signs of dementia, instead of $5,000/month human caregiver who visits once a week.

---

## 🚀 Quick Links

- **Demo Video**: [YouTube Link] (TBD)
- **Live Demo**: [URL] (TBD)
- **GitHub**: [github.com/YOUR_USERNAME/claracare](https://github.com/YOUR_USERNAME/claracare)
- **DevPost**: [DevPost Link] (TBD)
- **Documentation**: See `/docs` directory

---

## ✨ Key Features

### 1. Daily Check-In Calls
Clara calls every morning with natural, warm conversations:
> "Good morning, Dorothy! How did you sleep? What are your plans today?"

### 2. Cognitive Tracking
Tracks 5 speech metrics over time to detect early cognitive decline:
- Vocabulary diversity
- Response latency
- Topic coherence
- Repetition rate
- Word-finding difficulty

### 3. Nostalgia Mode
When patient seems sad, Clara shares memories from their "golden years":
> "Did you know that in 1963, The Beatles released their first album? I bet you remember that!"

### 4. Smart Alerts
Detects distress signals and alerts family immediately:
- Falls
- Confusion
- Pain
- Panic

### 5. Family Dashboard
Mobile app (published on Replit) shows:
- Daily wellness summaries
- Cognitive trend charts
- Conversation history
- Alert timeline

### 6. Cognitive Health Reports
Downloadable PDF reports for families to share with doctors:
- 30-day cognitive metric trends
- Alert history & recommendations
- Professional, branded documents (Foxit APIs)

### 7. Medication Reminders
Natural, caring reminders woven into conversation:
> "Don't forget your heart medication at 2 PM!"

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Voice AI | Deepgram Voice Agent (Nova-3 STT, Aura-2 TTS) |
| Backend | Python + FastAPI |
| NLP | spaCy, sentence-transformers |
| CMS | Sanity (+ MCP Server) |
| Search | You.com API |
| Reports | Foxit (Document Generation + PDF Services) |
| Frontend | Next.js + React |
| Charts | Chart.js |
| Mobile | Replit Mobile Apps |
| Admin | Retool (Assist / AppGen) |
| Deployment | Akamai LKE (Kubernetes: CPU + GPU nodes) |
| Phone | Twilio (bonus) |

---

## 📂 Project Structure

```
claracare/
├── docs/                  # 📚 Memory bank (full context)
├── backend/               # Python FastAPI + voice agent + cognitive + nostalgia + reports
├── dashboard/             # Next.js family dashboard
├── studio-claracare/      # Sanity Studio v5 (5 schemas)
├── .cursor/mcp.json       # Sanity MCP Server config
├── voice-web/             # Simple web voice interface
├── k8s/                   # Kubernetes manifests
└── scripts/               # Utility scripts
```

See [docs/06-PROJECT-STRUCTURE.md](docs/06-PROJECT-STRUCTURE.md) for complete structure.

---

## 🏃 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Kubernetes (kubectl)

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/claracare.git
cd claracare
```

### 2. Set Up Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Copy and fill in API keys
cp .env.example .env

# Run server
uvicorn app.main:app --reload --port 8000
```

### 3. Set Up Dashboard
```bash
cd dashboard
npm install

# Copy and fill in environment variables
cp .env.local.example .env.local

# Run dev server
npm run dev
```

### 4. Set Up Sanity Studio
```bash
cd studio-claracare
npm install
npm run dev  # Opens Sanity Studio at localhost:3333
```

### 5. Seed Demo Data (Optional)
```bash
cd backend
python3 -m scripts.seed_sanity
```

### 5. Or Use Docker Compose
```bash
docker-compose up
# Backend: http://localhost:8000
# Dashboard: http://localhost:3000
# Sanity: http://localhost:3333
```

---

## 📖 Documentation

**New to the project?** Start here:

1. **[docs/00-PROJECT-OVERVIEW.md](docs/00-PROJECT-OVERVIEW.md)** — The problem, solution, business case
2. **[docs/03-TEAM-ROLES.md](docs/03-TEAM-ROLES.md)** — Find your role
3. **[docs/05-API-SETUP.md](docs/05-API-SETUP.md)** — Sign up for all services
4. **[docs/07-DEVELOPMENT-TIMELINE.md](docs/07-DEVELOPMENT-TIMELINE.md)** — Day-by-day plan

**Full Documentation Index**: [docs/README.md](docs/README.md)

---

## 🎬 Demo

### 3-Minute Video (TBD)
[YouTube Link]

### Live Demo (TBD)
[URL to deployed app]

### Screenshots (TBD)
- Clara voice interface
- Family dashboard (mobile)
- Cognitive trend charts
- Alert timeline

---

## 👥 Team

- **P1 — Voice AI Engineer**: [Name] — Deepgram integration, Clara persona, phone calling
- **P2 — Backend / NLP Engineer**: [Name] — FastAPI, cognitive analysis, alerts
- **P3 — Full-Stack / Integrations**: [Name] — Sanity, You.com, nostalgia mode
- **P4 — Frontend Engineer**: [Name] — Next.js dashboard, mobile app
- **P5 — DevOps / Demo Lead**: [Name] — Kubernetes, demo video, submissions

---

## 🏆 Challenge Tracks

Submitted to **8 tracks**:

1. ✅ Overall Winner ($12,500)
2. ✅ Deepgram "Smart Listener" (Keychron keyboards ×5)
3. ✅ Deepgram "Voice Operator" (Sennheiser headphones)
4. ✅ You.com ($700)
5. ✅ Sanity ($1,000)
6. ✅ Replit Mobile ($2,000)
7. ✅ Akamai/Linode ($1,250)
8. ✅ Retool (TBD)

See [docs/10-SUBMISSION-STRATEGY.md](docs/10-SUBMISSION-STRATEGY.md) for our strategy per track.

---

## 🚀 Deployment

### Akamai LKE (Kubernetes)

```bash
# Build Docker images
docker build -t claracare-backend:latest ./backend
docker build -t claracare-dashboard:latest ./dashboard

# Push to registry
docker push YOUR_REGISTRY/claracare-backend:latest
docker push YOUR_REGISTRY/claracare-dashboard:latest

# Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl create secret generic claracare-secrets --from-env-file=.env
kubectl apply -f k8s/

# Verify
kubectl get pods -n claracare
```

See [docs/06-PROJECT-STRUCTURE.md](docs/06-PROJECT-STRUCTURE.md) for full deployment docs.

---

## 🧪 Testing

### Backend Tests (109 tests)
```bash
cd backend
python3 -m pytest tests/ -v
```

Covers:
- P2: Cognitive analyzer, baseline tracker, alert engine, pipeline, API routes
- P3: SanityDataStore mappings, insights endpoint, nostalgia engine, PDF reports

### Frontend Tests
```bash
cd dashboard
npm test
```

### Manual Testing Checklist
- [ ] Talk to Clara via web interface
- [ ] Verify conversation saved in Sanity
- [ ] Check cognitive metrics computed
- [ ] Trigger nostalgia mode (say something sad)
- [ ] Trigger alert (mention falling)
- [ ] View dashboard on mobile
- [ ] Check cognitive trend charts

---

## 📊 Business Case

- **Market**: 54 million caregivers in the US
- **TAM**: $9.7 billion (54M × $15/month)
- **Pricing**: $15/month per patient (vs. $5,000/month human caregiver)
- **Potential Partners**: Medicare Advantage plans, AARP, assisted living facilities
- **Regulatory**: FDA-exempt (wellness product, not medical device)

---

## 🔮 Future Roadmap

### v2.0 Features (Post-Hackathon)
- [ ] Multi-language support (Deepgram supports 30+ languages)
- [ ] Voice customization (choose Clara's accent, age, personality)
- [ ] Weekly wellness reports
- [ ] Integration with electronic medical records (EMR)
- [ ] Music therapy mode
- [ ] Video calls (when available)
- [ ] Group calls (patient + family)

### v3.0 Features
- [ ] Predictive alerts (ML model trained on patterns)
- [ ] Integration with wearables (heart rate, sleep tracking)
- [ ] Caregiver marketplace (connect to human caregivers if needed)
- [ ] Insurance integration (Medicare/Medicaid billing)

---

## 🤝 Contributing

This project is open-source under the MIT License.

**We welcome contributions!**

- **Bug reports**: Open an issue on GitHub
- **Feature requests**: Open an issue with "Feature:" prefix
- **Pull requests**: Fork, create branch, submit PR
- **Documentation**: Improvements always welcome

### Development Setup
See [Quick Start](#-quick-start) above.

### Code Style
- **Python**: PEP 8, type hints, docstrings
- **TypeScript**: ESLint + Prettier
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

### Sponsors
- **Deepgram** — Voice Agent API ($200 credit)
- **You.com** — Search API
- **Sanity** — Structured content CMS
- **Replit** — Mobile app deployment
- **Akamai/Linode** — Kubernetes hosting ($1,000 credit)
- **Retool** — Admin dashboard
- **Twilio** — Phone integration ($15.50 credit)

### Inspiration
Built for the 54 million Americans caring for aging parents, and for our own parents who will one day need this.

---

## 📞 Contact

- **GitHub**: [YOUR_USERNAME/claracare](https://github.com/YOUR_USERNAME/claracare)
- **Email**: [your-email@example.com]
- **Discord**: [Your Discord Handle]
- **DevPost**: [DevPost Profile]

---

## 📈 Project Status

- **Phase 0**: ✅ Complete (Setup & Documentation)
- **Phase 1**: ✅ Complete (Voice Agent Core — Deepgram + Twilio)
- **Phase 2**: ✅ Complete (Cognitive Analysis, Alerts, Notifications, API Routes)
- **Phase 3**: ✅ Complete (Sanity CMS, SanityDataStore, Nostalgia Engine, Foxit Reports, Insights API)
- **Current Phase**: Phase 4 (Frontend Dashboard)
- **Test Suite**: ✅ 109 tests passing
- **Deployment**: 🚧 In Progress
- **Demo Video**: 🚧 In Progress
- **Submissions**: ⏳ Pending

---

## 💡 Why ClaraCare?

Every one of us will face this: parents aging alone, unable to be there 24/7. We built ClaraCare because:

1. **It's personal**: We've all worried about our parents
2. **It's real**: 54M Americans need this today
3. **It's possible**: Voice AI is finally good enough
4. **It's necessary**: Early cognitive decline detection saves lives

**ClaraCare. Because no one should age alone.** 💙

---

**Built with ❤️ for DeveloperWeek 2026 Hackathon**

*Last Updated: February 11, 2026*
