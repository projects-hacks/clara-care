# ClaraCare - AI Elder Care Companion

## Overview
ClaraCare is an AI voice companion that helps families care for aging parents. It provides daily check-in calls, cognitive health tracking, nostalgia mode, and smart alerts. The project consists of a Python FastAPI backend and a Next.js mobile-first family dashboard.

## Project Architecture
- **Dashboard (Frontend)**: Next.js 16 app in `dashboard/`
  - `dashboard/src/app/` - App Router pages (Home, History, Trends, Alerts, Settings)
  - `dashboard/src/components/` - Shared UI components (Navigation, TopBar, MoodBadge, CognitiveScoreBadge, AlertBadge, ConversationCard, AlertCard, CognitiveChart, EmptyState, LoadingSpinner)
  - `dashboard/src/lib/api.ts` - Typed API client with mock data fallback (USE_MOCK flag)
  - `dashboard/src/lib/mock-data.ts` - Realistic mock data for Dorothy Chen patient
  - `dashboard/src/lib/utils.ts` - Formatting, color, and utility functions
  - Uses Tailwind v4 with @theme custom colors (clara-*, mood-*, severity-*)
  - Dependencies: React 19, recharts, lucide-react, date-fns, clsx
- **Backend**: Python FastAPI application in `backend/`
  - `backend/app/main.py` - Main FastAPI entry point
  - `backend/app/routes/` - API route handlers (patients, conversations, wellness, alerts, insights, reports)
  - `backend/app/cognitive/` - NLP-based cognitive analysis (analyzer, baseline tracker, alert engine, pipeline)
  - `backend/app/voice/` - Twilio voice integration (agent, bridge, outbound calls)
  - `backend/app/storage/` - Data storage (in-memory and Sanity CMS)
  - `backend/app/notifications/` - Email notifications via SMTP
  - `backend/app/reports/` - PDF report generation via Foxit
  - `backend/app/nostalgia/` - Nostalgia mode with You.com API
- **Sanity Studio**: `studio-claracare/` - CMS studio for managing patient data
- **Docs**: `docs/` - Project documentation

## Running
- Dashboard (frontend) runs on port 5000 via `cd dashboard && npm run dev`
- Backend runs on port 3001 via `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload`
- Frontend proxies API calls to backend via next.config.ts rewrites

## Dashboard Pages
- **Home** (`/`) - Wellness summary, quick stats, recent conversations, active alerts, nostalgia insights
- **History** (`/history`) - Conversation list with mood filters, click for detail
- **Conversation Detail** (`/history/[id]`) - Full transcript as chat bubbles, cognitive metrics, nostalgia engagement
- **Trends** (`/trends`) - Cognitive metric charts (vocabulary, coherence, repetition, pauses) with period selector
- **Alerts** (`/alerts`) - Alert list with severity filters, unacknowledged toggle, acknowledge action
- **Settings** (`/settings`) - Patient profile, medications, preferences, call schedule, family contacts, thresholds

## Key Dependencies
### Dashboard
- next, react, react-dom - Framework
- tailwindcss v4, @tailwindcss/postcss - Styling
- recharts - Charts
- lucide-react - Icons
- date-fns - Date formatting
- clsx - Classnames

### Backend
- FastAPI, uvicorn, pydantic - Web framework
- spacy, sentence-transformers, scikit-learn - NLP/cognitive analysis
- httpx - HTTP client for external APIs
- aiosmtplib, jinja2 - Email notifications
- python-dotenv - Environment config

## Design Decisions
- Mobile-first design (375-428px width target)
- Mock data layer with USE_MOCK flag for independent frontend development
- Tailwind v4 with @theme for custom design tokens
- Bottom tab navigation (iOS-style)
- All data fetched client-side with loading/error states

## External Services (optional, app runs without them)
- Sanity CMS (SANITY_PROJECT_ID, SANITY_DATASET, SANITY_TOKEN)
- Twilio (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER)
- Deepgram (DEEPGRAM_API_KEY)
- You.com (YOUCOM_API_KEY)
- Foxit PDF Services (FOXIT_* variables)
- SMTP Email (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)
