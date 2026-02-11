# ClaraCare — Project Structure

## Complete Monorepo Layout

```
claracare/
├── README.md                          # Main project README (P5)
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore rules
├── docker-compose.yml                 # Local development orchestration
├── .github/
│   └── workflows/
│       └── deploy.yml                 # CI/CD to Akamai LKE
│
├── docs/                              # 📚 MEMORY BANK (This directory!)
│   ├── 00-PROJECT-OVERVIEW.md
│   ├── 01-TECH-STACK.md
│   ├── 02-ARCHITECTURE.md
│   ├── 03-TEAM-ROLES.md
│   ├── 04-DATA-MODELS.md
│   ├── 05-API-SETUP.md
│   ├── 06-PROJECT-STRUCTURE.md        # ← You are here
│   ├── 07-DEVELOPMENT-TIMELINE.md
│   ├── 08-CLARA-PERSONA.md
│   ├── 09-DEMO-SCRIPT.md
│   └── 10-SUBMISSION-STRATEGY.md
│
├── backend/                           # Python FastAPI (P1, P2, P3)
│   ├── README.md
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Backend container
│   ├── .env.example                   # Example environment variables
│   ├── pyproject.toml                 # Python project config (optional)
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py                    # FastAPI app entry point
│       ├── config.py                  # Configuration (ENV vars)
│       │
│       ├── voice/                     # P1 — Voice AI
│       │   ├── __init__.py
│       │   ├── agent.py               # Deepgram Voice Agent WebSocket handler
│       │   ├── functions.py           # Function calling definitions
│       │   ├── persona.py             # Clara's system prompt
│       │   └── twilio_bridge.py       # Twilio WebSocket bridge (bonus)
│       │
│       ├── cognitive/                 # P2 — NLP & Cognitive Analysis
│       │   ├── __init__.py
│       │   ├── analyzer.py            # spaCy NLP metrics
│       │   ├── baseline.py            # Baseline establishment
│       │   └── alerts.py              # Threshold detection + notifications
│       │
│       ├── nostalgia/                 # P3 — Nostalgia Mode
│       │   ├── __init__.py
│       │   ├── era.py                 # Era calculation + content strategy
│       │   └── youcom_client.py       # You.com API wrapper
│       │
│       ├── sanity_client/             # P3 — Sanity CMS
│       │   ├── __init__.py
│       │   ├── client.py              # Sanity Python client
│       │   └── queries.py             # GROQ queries
│       │
│       ├── notifications/             # P2 — Alerts
│       │   ├── __init__.py
│       │   ├── email.py               # Email alerts (SMTP)
│       │   └── sms.py                 # Twilio SMS (bonus)
│       │
│       ├── routes/                    # P2, P3 — API Endpoints
│           ├── __init__.py
│           ├── patients.py            # CRUD for patient data
│           ├── conversations.py       # Conversation history
│           ├── wellness.py            # Wellness digests + trends
│           ├── reports.py             # Cognitive Health Report PDF download
│           ├── auth.py                # Simple authentication
│           └── websocket.py           # WebSocket endpoint for voice
│
│       └── reports/                   # P3 — Foxit PDF Reports
│           ├── __init__.py
│           ├── generator.py           # Report data assembly + Foxit API calls
│           ├── foxit_client.py        # Foxit Document Gen + PDF Services wrapper
│           └── templates/
│               └── cognitive_report.docx  # DOCX template for Foxit Doc Gen
│
├── dashboard/                         # Next.js (P4)
│   ├── README.md
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── .env.local.example
│   ├── Dockerfile                     # Dashboard container
│   │
│   ├── public/
│   │   ├── logo.svg
│   │   └── favicon.ico
│   │
│   └── src/
│       ├── app/                       # Next.js App Router
│       │   ├── layout.tsx             # Root layout
│       │   ├── page.tsx               # Home — Today's Summary
│       │   ├── globals.css            # Global styles
│       │   │
│       │   ├── history/
│       │   │   └── page.tsx           # Conversation history
│       │   │
│       │   ├── trends/
│       │   │   └── page.tsx           # Cognitive trend charts
│       │   │
│       │   ├── alerts/
│       │   │   └── page.tsx           # Alert timeline
│       │   │
│       │   ├── nostalgia/
│       │   │   └── page.tsx           # Nostalgia preferences
│       │   │
│       │   └── settings/
│       │       └── page.tsx           # Settings (meds, call schedule, contacts)
│       │
│       ├── components/                # Reusable React components
│       │   ├── MoodIndicator.tsx
│       │   ├── CognitiveChart.tsx
│       │   ├── ConversationCard.tsx
│       │   ├── AlertBadge.tsx
│       │   ├── Navigation.tsx
│       │   └── Layout.tsx
│       │
│       └── lib/
│           ├── api.ts                 # Backend API client
│           ├── sanity.ts              # Sanity client (if direct queries)
│           └── utils.ts               # Utility functions
│
├── sanity/                            # Sanity Studio (P3)
│   ├── README.md
│   ├── package.json
│   ├── sanity.config.ts               # Sanity Studio config
│   ├── sanity.cli.ts
│   │
│   └── schemas/
│       ├── index.ts                   # Schema exports
│       ├── patient.ts                 # Patient schema
│       ├── conversation.ts            # Conversation schema
│       ├── familyMember.ts            # Family member schema
│       └── wellnessDigest.ts          # Wellness digest schema
│
├── voice-web/                         # Simple web voice interface (P1)
│   ├── index.html                     # Main HTML
│   ├── app.js                         # WebSocket + microphone logic
│   ├── style.css                      # Basic styling
│   └── README.md
│
├── k8s/                               # Kubernetes manifests (P5)
│   ├── namespace.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── dashboard-deployment.yaml
│   ├── dashboard-service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── secrets.yaml.example           # Example secrets (NOT committed)
│
└── scripts/                           # Utility scripts (P5)
    ├── setup.sh                       # Initial setup script
    ├── deploy.sh                      # Deployment script
    └── seed-data.py                   # Seed Sanity with test data (P3)
```

---

## File Ownership Matrix

| Directory | Primary Owner | Support |
|-----------|--------------|---------|
| `/docs` | P5, P3 | All |
| `/backend/app/voice` | P1 | P2 |
| `/backend/app/cognitive` | P2 | - |
| `/backend/app/nostalgia` | P3 | P1 |
| `/backend/app/sanity_client` | P3 | - |
| `/backend/app/notifications` | P2 | - |
| `/backend/app/routes` | P2, P3 | - |
| `/dashboard` | P4 | - |
| `/sanity` | P3 | P4 |
| `/voice-web` | P1 | - |
| `/k8s` | P5 | - |
| `/scripts` | P5, P3 | - |

---

## Key Configuration Files

### `backend/requirements.txt`
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
websockets==12.0
httpx==0.26.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
spacy==3.7.2
nltk==3.8.1
numpy==1.26.3
scikit-learn==1.4.0
sentence-transformers==2.3.1
requests==2.31.0
twilio==8.11.0
python-multipart==0.0.6
```

### `backend/.env.example`
```bash
# Deepgram
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# You.com
YOUCOM_API_KEY=your_youcom_api_key_here

# Sanity
SANITY_PROJECT_ID=your_sanity_project_id
SANITY_DATASET=production
SANITY_TOKEN=your_sanity_token

# Foxit
FOXIT_API_KEY=your_foxit_api_key
FOXIT_API_SECRET=your_foxit_api_secret

# Twilio (Optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Email Alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Application
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=info
```

### `dashboard/package.json`
```json
{
  "name": "claracare-dashboard",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@sanity/client": "^6.10.0",
    "chart.js": "^4.4.1",
    "react-chartjs-2": "^5.2.0",
    "date-fns": "^3.0.6"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "typescript": "^5",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33",
    "eslint": "^8",
    "eslint-config-next": "14.1.0"
  }
}
```

### `dashboard/.env.local.example`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SANITY_PROJECT_ID=your_sanity_project_id
NEXT_PUBLIC_SANITY_DATASET=production
```

### `docker-compose.yml`
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  dashboard:
    build: ./dashboard
    ports:
      - "3000:3000"
    env_file:
      - ./dashboard/.env.local
    volumes:
      - ./dashboard:/app
      - /app/node_modules
    command: npm run dev

  sanity-studio:
    working_dir: /app
    image: node:18-alpine
    ports:
      - "3333:3333"
    volumes:
      - ./sanity:/app
    command: npm run dev
```

### `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_md

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `dashboard/Dockerfile`
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build Next.js app
RUN npm run build

# Expose port
EXPOSE 3000

# Run application
CMD ["npm", "start"]
```

### `.gitignore`
```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Node
node_modules/
.next/
out/
build/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Kubernetes secrets
k8s/secrets.yaml

# Testing
.pytest_cache/
coverage/
*.cover
.coverage

# Sanity
sanity/dist/
```

---

## Development Workflow

### Initial Setup (P5)
```bash
# Create directory structure
mkdir -p claracare/{docs,backend/app/{voice,cognitive,nostalgia,sanity_client,notifications,routes},dashboard/src/{app,components,lib},sanity/schemas,voice-web,k8s,scripts}

# Initialize Git
cd claracare
git init
git add .
git commit -m "Initial project structure"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/claracare.git
git push -u origin main
```

### Local Development

#### Backend (P1, P2, P3)
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download models
python -m spacy download en_core_web_md
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy .env.example to .env and fill in API keys
cp .env.example .env

# Run server
uvicorn app.main:app --reload --port 8000
```

#### Dashboard (P4)
```bash
cd dashboard

# Install dependencies
npm install

# Copy .env.local.example to .env.local and fill in values
cp .env.local.example .env.local

# Run dev server
npm run dev
```

#### Sanity Studio (P3)
```bash
cd sanity

# Install dependencies
npm install

# Initialize Sanity (if not done)
sanity init

# Run Sanity Studio
npm run dev
# Opens at http://localhost:3333
```

#### Full Stack (Using Docker Compose)
```bash
# From project root
docker-compose up

# Backend: http://localhost:8000
# Dashboard: http://localhost:3000
# Sanity Studio: http://localhost:3333
```

---

## Deployment Structure

### Kubernetes (Akamai LKE)
```
claracare-namespace
├── backend-deployment (2 replicas)
│   └── backend-service (ClusterIP)
├── dashboard-deployment (1 replica)
│   └── dashboard-service (ClusterIP)
└── ingress (NGINX)
    ├── /api → backend-service:8000
    └── / → dashboard-service:3000
```

### External Services (Not in Kubernetes)
- **Sanity**: Hosted by Sanity.io
- **Deepgram**: Cloud API
- **You.com**: Cloud API
- **Twilio**: Cloud API
- **Retool**: Cloud-hosted admin dashboard

---

## Documentation Standards

### Code Comments
- **Functions**: Docstrings with params, return type, description
- **Complex Logic**: Inline comments explaining "why", not "what"
- **TODOs**: Mark with `# TODO(P1): Description` if urgent

### Commit Messages
```
Format: <type>(<scope>): <subject>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Examples:
feat(voice): Add Deepgram Voice Agent WebSocket handler
fix(cognitive): Correct TTR calculation for empty responses
docs(readme): Add deployment instructions
```

### Pull Requests
- **Title**: Clear, descriptive (e.g., "Add cognitive metrics analyzer")
- **Description**: What changed, why, how to test
- **Reviewers**: At least 1 team member
- **Labels**: `backend`, `frontend`, `docs`, `infra`

---

## Testing Structure (If Time Permits)

```
backend/tests/
├── __init__.py
├── test_voice_agent.py
├── test_cognitive_analyzer.py
├── test_nostalgia_mode.py
└── test_api_routes.py

dashboard/tests/
└── (Jest tests for components)

# Run backend tests
cd backend
pytest

# Run frontend tests
cd dashboard
npm test
```

---

## Scripts Directory

### `scripts/setup.sh`
```bash
#!/bin/bash
# Initial setup for ClaraCare development environment

echo "🚀 Setting up ClaraCare..."

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_md
cp .env.example .env
echo "✅ Backend setup complete"

# Dashboard
cd ../dashboard
npm install
cp .env.local.example .env.local
echo "✅ Dashboard setup complete"

# Sanity
cd ../sanity
npm install
echo "✅ Sanity setup complete"

echo "🎉 Setup complete! Check docs/ for next steps."
```

### `scripts/seed-data.py`
```python
#!/usr/bin/env python3
"""
Seed Sanity with test patient data
"""
import requests
import os
from datetime import datetime

SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID")
SANITY_DATASET = os.getenv("SANITY_DATASET", "production")
SANITY_TOKEN = os.getenv("SANITY_TOKEN")

# Create test patient "Dorothy"
# ... (See separate script file for full implementation)
```

---

## Naming Conventions

### Python
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`

### TypeScript/React
- **Files**: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Components**: `PascalCase`
- **Functions**: `camelCase()`
- **Constants**: `UPPER_SNAKE_CASE`

### Sanity Schemas
- **Schema names**: `camelCase` (e.g., `familyMember`)
- **Field names**: `camelCase` (e.g., `preferredName`)
