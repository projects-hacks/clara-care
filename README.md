# ClaraCare

> **Voice-First AI Companion for Cognitive Health Monitoring**

<img width="1504" height="726" alt="Screenshot 2026-02-19 at 11 28 55 pm" src="https://github.com/user-attachments/assets/77cb7407-ae14-4ae6-ab6b-57d85cd32184" />

ClaraCare is an AI voice agent that calls elderly individuals daily to check in, detects early signs of cognitive decline through natural conversation, and keeps families informed.

## 🚀 Key Features

- **Daily Check-ins**: Proactive calls using Twilio & Deepgram Aura.
- **Cognitive Analysis**: Tracks vocabulary richness, topic coherence, and sentiment over time.
- **Nostalgia Mode**: Uses **You.com** to find music and news from the patient's "golden years" (ages 15-25).
- **Family Alerts**: Instant SMS/Email notifications for distress keywords.
- **Health Reports**: Automated PDF summaries generated via **Foxit** APIs.
- **Backend CMS**: Built on **Sanity** for structured longitudinal data.

## 🛠️ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for dashboard/CMS)
- Docker (optional)

### 1. Clone & Setup
```bash
git clone https://github.com/your-username/clara-care.git
cd clara-care/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
Copy the example file and fill in your API keys (Deepgram, Twilio, You.com, Sanity):
```bash
cp .env.example .env
nano .env
```

### 3. Run the Server
```bash
# Start FastAPI backend with Twilio webhook support
python3 -m app.main
```
Server runs on `http://localhost:8000`. Expose to internet via ngrok for Twilio access.

### 4. Run Tests
Verify all components (API connections, fallback logic, persona) are working:
```bash
python3 tests/verify_voice.py
```

## 📚 Documentation

Detailed documentation is available in the [`docs/`](docs/) directory:

- [**Project Overview**](docs/00-PROJECT-OVERVIEW.md): Product vision & market fit.
- [**Architecture**](docs/02-ARCHITECTURE.md): System diagrams & data flow.
- [**API Setup**](docs/05-API-SETUP.md): Getting your API keys.
- [**Sanity CMS**](docs/SANITY-SETUP.md): Database schema & setup.
- [**You.com Integration**](docs/YOUCOM-SETUP.md): Search & Nostalgia APIs.

## 🏗️ Architecture

- **Voice Core**: Deepgram Aura (STT/TTS) + Twilio Media Streams.
- **Brain**: OpenAI GPT-4o with "Clara" system prompt.
- **Tools**: `functions.py` handles external API calls (You.com, Sanity, Alerts).
- **Database**: Sanity CMS for structured content.
