# ClaraCare — API Setup & Sign-Up Guide

## ⚠️ CRITICAL: Sign Up on Day 1
**API approval can take hours.** Everyone must sign up for all services on Day 1.

---

## Required Sign-Ups (All Team Members)

### 1. Hackathon Registration

#### DevPost
- **URL**: https://developerweek-2026-hackathon.devpost.com/
- **What**: Official hackathon registration
- **Who**: Everyone
- **Action**: Register with email, join DeveloperWeek 2026 Hackathon

#### Eventbrite
- **URL**: Link from DevPost page
- **What**: Required alongside DevPost
- **Who**: Everyone
- **Action**: RSVP for event dates (Feb 11-20, 2026)

---

## Service-Specific Sign-Ups

### 2. Deepgram (P1 — Voice AI Engineer)

#### Sign-Up
- **URL**: https://console.deepgram.com/signup
- **What You Get**: $200 free credit
- **What You Need**: Email address
- **Credit Card**: Not required

#### After Sign-Up
1. Navigate to **API Keys** in console
2. Create new API key (name it "claracare-hackathon")
3. Copy API key → store in password manager
4. Set environment variable: `DEEPGRAM_API_KEY=xxx`

#### Key Documentation to Read
| Doc | URL | Purpose |
|-----|-----|---------|
| Voice Agent Getting Started | https://developers.deepgram.com/docs/voice-agent | Core API reference |
| Medical Assistant Demo | https://github.com/deepgram/medical-assistant-demo | Healthcare use case example |
| Function Calling Guide | https://developers.deepgram.com/docs/function-calling | How to add functions |
| Twilio Integration | https://developers.deepgram.com/docs/twilio-integration | Phone calling setup |
| Twilio + Deepgram Repo | https://github.com/deepgram-devs/twilio-voice-agent | Code reference |

#### Usage Limits
- **Free Credit**: $200
- **Voice Agent Pricing**: ~$0.025/minute (STT + TTS + LLM)
- **Estimated Usage**: 8,000 minutes (~133 hours)
- **Hackathon Usage**: Well within limits

---

### 3. You.com (P3 — Integrations Engineer)

#### Sign-Up
- **URL**: https://you.com → Developer Dashboard
- **What You Get**: API key for Search, News, Agents APIs
- **What You Need**: Email address
- **Credit Card**: May be required for higher tiers (check hackathon resources)
- **Contact**: mariane.bekker@you.com

#### After Sign-Up
1. Navigate to **Developer Dashboard**
2. Create API key
3. Review **Hackathon Resources Page**: https://you.com/resources/hackathon
4. Set environment variable: `YOUCOM_API_KEY=xxx`

#### APIs to Use
- **Search API**: Real-time web search
- **News API**: Historical news events (for nostalgia)
- **Music/Facts**: Era-specific content

#### Documentation
- **Hackathon Resources**: https://you.com/resources/hackathon
- **API Docs**: https://documentation.you.com/api-reference

---

### 4. Sanity (P3 — Integrations Engineer)

#### Sign-Up
- **URL**: https://sanity.io
- **What You Get**: Free tier with unlimited projects
- **What You Need**: Email or GitHub login
- **Credit Card**: Not required

#### After Sign-Up
1. Create new project: **"claracare"**
2. Choose dataset name: **"production"**
3. Get Project ID from project settings
4. Create API token:
   - Go to **Settings → API**
   - Create token with **Editor** permissions
   - Name: "claracare-backend"
5. Set environment variables:
   ```bash
   SANITY_PROJECT_ID=xxx
   SANITY_DATASET=production
   SANITY_TOKEN=xxx
   ```

#### Next Steps
1. Install Sanity CLI: `npm install -g @sanity/cli`
2. Initialize Sanity Studio:
   ```bash
   cd sanity/
   sanity init
   ```
3. Create schemas (see `04-DATA-MODELS.md`)
4. Deploy Studio: `sanity deploy`
5. **Set up Sanity MCP Server** (required for Sanity challenge track):
   ```bash
   # Option A: Add to AI coding assistant (Cursor, Claude Code) MCP config
   npx -y @sanity/mcp-server
   
   # Option B: Add to .cursor/mcp.json or AI assistant config
   {
     "mcpServers": {
       "sanity": {
         "command": "npx",
         "args": ["-y", "@sanity/mcp-server"],
         "env": {
           "SANITY_PROJECT_ID": "your-project-id",
           "SANITY_DATASET": "production",
           "SANITY_TOKEN": "your-token"
         }
       }
     }
   }
   ```
   - **Why**: The Sanity challenge track requires using Sanity's MCP Server with an AI coding assistant. This enables schema-aware code generation.
   - **Docs**: https://www.sanity.io/docs/mcp-server

#### Documentation
- **Getting Started**: https://www.sanity.io/docs/getting-started
- **GROQ Tutorial**: https://www.sanity.io/docs/how-queries-work
- **MCP Server**: https://www.sanity.io/docs/mcp-server
- **Python Client**: Use `requests` library with Sanity HTTP API
- **Contact**: knut@sanity.io

---

### 5. Replit (P4 — Frontend Engineer)

#### Sign-Up
- **URL**: https://replit.com/signup?coupon=REPLITDEVWEEK
- **What You Get**: Free month of Replit Core (use promo code **REPLITDEVWEEK**)
- **What You Need**: Email or GitHub login
- **Credit Card**: Not required with promo code

#### After Sign-Up
1. Create new Repl: **Next.js** template
2. Name it: **claracare-dashboard**
3. Explore **Mobile Apps** feature (left sidebar)
4. Connect to GitHub repo (optional but recommended)

#### Mobile App Publishing
- One-click publish to mobile
- No App Store submission needed
- Shareable link for family members

#### Documentation
- **Replit Docs**: https://docs.replit.com
- **Mobile Apps**: https://docs.replit.com/hosting/mobile-apps

---

### 6. Akamai / Linode (P5 — DevOps Lead)

#### Sign-Up
- **URL**: https://login.linode.com/signup?promo=akm-eve-dev-hack-1000-12126-M866
- **What You Get**: $1,000 promo credit (90 days)
- **What You Need**: Email address + **credit card** (NOT charged unless you exceed free tier)
- **Important**: You MUST have credit card even though you won't be charged

#### After Sign-Up
1. Navigate to **Kubernetes** section
2. Create LKE cluster:
   - **Name**: claracare-cluster
   - **Region**: Choose closest to you (e.g., US-West)
   - **CPU Node Pool**: 2x `g6-standard-2` (4GB RAM, 2 CPU each) — ~$20/month
   - **GPU Node Pool**: 1x `g6-gpu-1` (RTX 6000, 8GB VRAM) — ~$1.50/hr
   - **Cost**: Well within $1,000 credit
3. Download `kubeconfig.yaml`
4. Set up `kubectl`:
   ```bash
   export KUBECONFIG=/path/to/kubeconfig.yaml
   kubectl get nodes
   ```

> **GPU Node**: The Akamai challenge gives **bonus points for GPU-accelerated workloads**. We use the GPU node for:
> - Sentence embedding computation (topic coherence with `all-MiniLM-L6-v2`)
> - spaCy NLP batch processing
> - Cognitive analysis pipeline
>
> Even if the workload is lightweight, mentioning "GPU-accelerated cognitive analysis" scores bonus points.

#### Requirements for Submission
- Project must be **open-source** (public GitHub repo)
- Must be deployed on Akamai LKE
- Include clear deployment instructions in README
- **Bonus points** for GPU-accelerated workloads (AI/ML, data processing)

#### Documentation
- **LKE Docs**: https://www.linode.com/docs/products/compute/kubernetes/
- **GPU Instances**: https://www.linode.com/docs/products/compute/gpu/

---

### 7. Retool (P5 — DevOps Lead)

#### Sign-Up
- **URL**: https://retool.com
- **What You Get**: Free tenant for hackathon
- **What You Need**: Email address
- **Credit Card**: Not required
- **Contact**: hasun@retool.com

#### After Sign-Up
1. Create free account
2. Get your Retool domain (e.g., `claracare.retool.com`)
3. **Important**: Email **hasun@retool.com** with:
   - Your Retool domain
   - Mention you're participating in DeveloperWeek 2026 Hackathon
   - Request Retool Assist (AppGen) access (if not already enabled)

#### Using Retool Assist (AppGen)
1. Click "Create App"
2. Choose "Generate with AI" (Retool Assist)
3. Describe: "Admin dashboard for patient management with conversation logs and alerts"
4. Iterate on generated dashboard
5. Track your iteration process — judges value "depth of iteration"

#### Submission Requirements
- Submit a **5-minute recording** explaining:
  1. The problem you're solving
  2. How Retool Assist helped you build the solution
  3. The final solution and its production-grade quality
- Share your Retool domain with hasun@retool.com

#### Connect to Backend
- Add REST API resource
- Base URL: Your FastAPI backend
- Add authentication (API key header)

#### Documentation
- **Retool Docs**: https://docs.retool.com
- **Retool Assist Guide**: https://retool.com/products/retool-assist

---

### 8. Foxit (P3 — Integrations Engineer)

#### Sign-Up
- **URL**: https://developer-api.foxit.com/
- **What You Get**: Free developer account with API access
- **What You Need**: Email address
- **Credit Card**: Not required
- **Contact**: jorge_euceda@foxitsoftware.com

#### After Sign-Up
1. Create developer account
2. Navigate to **Dashboard** → Get API Key and API Secret
3. Set environment variables:
   ```bash
   FOXIT_API_KEY=xxx
   FOXIT_API_SECRET=xxx
   ```

#### APIs We Use (BOTH are required by Foxit challenge)

**Document Generation API** — Creates PDFs from structured data:
- Input: JSON data from Sanity (cognitive metrics, patient profile) + DOCX template
- Output: Professional PDF report
- Use Case: Weekly "Cognitive Health Report" for families

**PDF Services API** — Post-processes the generated PDF:
- Operations: compress, add watermark (ClaraCare branding), finalize
- Use Case: Optimize PDF for mobile download and add branding

#### Implementation Steps
1. Create a DOCX template for the Cognitive Health Report:
   - Patient name, date range
   - Cognitive metrics summary (table)
   - Trend indicators (↑ improving, ↓ declining, → stable)
   - Alert history
   - Recommendations
2. Use Document Generation API to fill template with Sanity data
3. Use PDF Services API to compress + watermark the generated PDF
4. Serve PDF via FastAPI endpoint: `GET /reports/{patient_id}/download`
5. Add "Download Report" button to family dashboard

#### Documentation
- **Getting Started**: https://developer-api.foxit.com/#getting-started
- **Document Generation**: https://developer-api.foxit.com/document-generation/
- **PDF Services**: https://developer-api.foxit.com/pdf-services/

---

### 8. Twilio (P1 — Voice AI Engineer) — BONUS

#### Sign-Up
- **URL**: https://www.twilio.com/try-twilio
- **What You Get**: $15.50 free credit + 1 free phone number
- **What You Need**: Email + phone number for verification
- **Credit Card**: Not required for trial

#### After Sign-Up
1. Get a free phone number:
   - **Console → Phone Numbers → Buy a Number**
   - Choose a local number
   - Free for trial accounts
2. Get credentials:
   - **Account SID**: From console dashboard
   - **Auth Token**: From console dashboard
3. Set environment variables:
   ```bash
   TWILIO_ACCOUNT_SID=xxx
   TWILIO_AUTH_TOKEN=xxx
   TWILIO_PHONE_NUMBER=+1xxxyyyzzzz
   ```

#### Usage Limits
- **Free Credit**: $15.50
- **Inbound Calls**: $0.0085/minute
- **Outbound Calls**: $0.014/minute
- **Total Minutes**: ~1,100 minutes inbound

#### Deepgram + Twilio Integration
- Follow: https://developers.deepgram.com/docs/twilio-integration
- Code reference: https://github.com/deepgram-devs/twilio-voice-agent

---

## GitHub Repository (P5 — DevOps Lead)

### Create Public Repo
```bash
# On GitHub
1. Go to https://github.com/new
2. Name: claracare
3. Description: AI Elder Care Companion — DeveloperWeek 2026 Hackathon
4. Public (required for Akamai submission)
5. Add MIT License
6. Create repository

# Locally
git clone https://github.com/YOUR_USERNAME/claracare.git
cd claracare
# Add monorepo structure (see 06-PROJECT-STRUCTURE.md)
git add .
git commit -m "Initial monorepo structure"
git push origin main
```

---

## Environment Variables Summary

### Backend `.env`
```bash
# Deepgram
DEEPGRAM_API_KEY=xxx

# You.com
YOUCOM_API_KEY=xxx

# Sanity
SANITY_PROJECT_ID=xxx
SANITY_DATASET=production
SANITY_TOKEN=xxx

# Foxit
FOXIT_API_KEY=xxx
FOXIT_API_SECRET=xxx

# Twilio (Bonus)
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1xxxyyyzzzz

# Email Alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Dashboard `.env.local`
```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Sanity (for direct queries from frontend)
NEXT_PUBLIC_SANITY_PROJECT_ID=xxx
NEXT_PUBLIC_SANITY_DATASET=production
```

---

## Troubleshooting

### Deepgram API Key Not Working
- Check API key is copied correctly (no extra spaces)
- Verify API key has correct permissions
- Try regenerating key

### You.com API 401 Unauthorized
- Check if hackathon promo code was applied
- Verify API key format
- Contact You.com support via developer dashboard

### Sanity API 403 Forbidden
- Check token has "Editor" permissions (not just "Viewer")
- Verify project ID matches
- Ensure dataset name is correct (case-sensitive)

### Twilio Phone Number Not Receiving Calls
- Check number is active in console
- Verify webhook URL is publicly accessible (use ngrok for local testing)
- Check Twilio error logs in console

### Akamai LKE Cluster Won't Create
- Verify credit card is on file (even though you won't be charged)
- Check region availability
- Try different node size

### Replit Mobile App Won't Publish
- Ensure app runs successfully in Replit first
- Check for build errors
- Verify all environment variables are set
- Try PWA deployment as fallback

---

## API Key Security

### DO NOT
- ❌ Commit API keys to Git
- ❌ Hardcode API keys in source code
- ❌ Share API keys in public Discord/Slack
- ❌ Include API keys in screenshots/demos

### DO
- ✅ Use `.env` files (add to `.gitignore`)
- ✅ Use environment variables
- ✅ Use Kubernetes Secrets for production
- ✅ Rotate keys after hackathon
- ✅ Use different keys for dev vs. production

---

## Cost Tracking

| Service | Free Tier | Expected Usage | Risk |
|---------|-----------|----------------|------|
| Deepgram | $200 credit | ~100 hours of calls | ✅ Safe |
| You.com | TBD | ~500 API calls | ✅ Safe |
| Sanity | Unlimited | < 100k documents | ✅ Safe |
| Foxit | Free dev tier | ~50 PDF reports | ✅ Safe |
| Replit | 1 month free | 1 app | ✅ Safe |
| Akamai LKE | $1,000 credit | ~$50/month (CPU + GPU) | ✅ Safe |
| Retool | Free tier | 1 dashboard | ✅ Safe |
| Twilio | $15.50 credit | ~20 hours calls | ✅ Safe |

**Total Hackathon Cost**: $0 (all within free tiers)

---

## Sponsor Contact Directory

| Sponsor | Contact Email | When to Reach Out |
|---------|--------------|-------------------|
| Deepgram | corey.weathers@deepgram.com | API issues, feature questions |
| You.com | mariane.bekker@you.com | Hackathon resources, API access |
| Sanity | knut@sanity.io | MCP Server setup, schema advice |
| Foxit | jorge_euceda@foxitsoftware.com | API access, template help |
| Replit | brendan.dugan@repl.it | Mobile app publishing issues |
| Akamai | linode.com/support | LKE cluster, GPU node availability |
| Retool | hasun@retool.com | Share Retool domain, get Assist access |
| CoCreate | tamish@cocreate.so | Not used by ClaraCare |
