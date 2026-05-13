# ClaraCare Website (claracare.me)

The **marketing and landing page** for ClaraCare, hosted at [claracare.me](https://claracare.me).

> **Note:** This is NOT the patient/family dashboard. The interactive dashboard has been migrated to the **React Native mobile app** in [`../clara-care-mobile/`](../clara-care-mobile/). This directory now serves exclusively as the public-facing website.

## What This Contains

- **Landing page** (`src/app/page.tsx`) — A polished Next.js marketing page featuring:
  - Animated hero section with scroll-triggered fade-ins
  - Feature grid (AI Voice Calls, Deepgram NLP, Cognitive Trends, etc.)
  - "How It Works" 3-step explainer
  - Deepgram integration code showcase
  - "For Families" value proposition section
  - App download CTAs (iOS + Android)
- **Shared components** — `Button.tsx`, `ServiceWorkerRegistration.tsx`
- **Utility libraries** — `utils.ts`, `timezones.ts`

## Tech Stack

- [Next.js 15](https://nextjs.org) (App Router)
- [Tailwind CSS](https://tailwindcss.com)
- [Lucide React](https://lucide.dev) for icons
- Deployed on Vercel

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the landing page.

## Architecture Decision

The old web dashboard (patient data, conversations, alerts, settings) has been fully removed from this directory. All patient-facing functionality now lives in the **Expo React Native** mobile app:

| Concern | Location |
|---|---|
| Marketing site (claracare.me) | `dashboard/` (this directory) |
| Patient dashboard (mobile) | `clara-care-mobile/` |
| Backend API | `backend/` |

### Why the split?

- The web dashboard was a demo/prototype using mock data
- Production users need a **native mobile experience** with push notifications, offline support, and biometric auth
- The marketing site remains a lightweight Next.js deployment — fast, SEO-friendly, and easy to update

## Folder Rename Consideration

This directory should ideally be renamed from `dashboard/` → `website/` to reflect its current purpose. This rename was deferred to avoid breaking any CI/CD or Vercel deployment configs — but it's the recommended next step.
