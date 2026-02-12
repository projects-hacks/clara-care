# P3: Sanity CMS Integration (DeveloperWeek 2026 Hackathon)

## Overview

**Priority 3 (P3)** adds production-ready content management through Sanity CMS, real-time web search via You.com, and automated PDF report generation using Foxit APIs.

**Status**: ✅ **Backend Complete** | 🔄 Schemas Complete | ⏳ Seed Data Pending

---

## 🎯 Challenge Tracks

### 1. Sanity CMS Challenge
**Track**: Structured Content Showcase  
**Requirement**: Use Sanity with 5+ document types, references, and MCP Server

**Our Implementation**:
- ✅ 5 Document Types: `patient`, `conversation`, `familyMember`, `wellnessDigest`, `alert`
- ✅ Cross-document References: Patients ↔ Family, Conversations → Patients
- ✅ MCP Server Integration: Cursor IDE with `.cursor/mcp.json`
- ✅ Showcase Endpoint: `/api/insights/{patient_id}` - GROQ queries across all types

**Deliverable**: Screenshots of MCP queries + insights dashboard demo

---

### 2. You.com Challenge
**Track**: Build AI Agents That Think, Reason & Search Live  
**Requirement**: Use You.com APIs for live, citation-backed search

**Our Implementation**:
- ✅ **Nostalgia Mode**: Era-specific content from patient's golden years (ages 15-25)
- ✅ **Real-time Q&A**: Live web search for patient questions (weather, news, facts)
- ✅ **$100 Free Credits**: All participants get credits + prizes for best use

**API Features**:
- LLM-ready, citation-backed answers
- Structured JSON with URLs, snippets, metadata
- Perfect for grounding Clara's conversations in real data

**Deliverable**: Voice agent demo showing nostalgia + real-time search in action

---

## 📦 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLARACARE P3 STACK                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Sanity    │  │   You.com    │  │    Foxit     │      │
│  │     CMS     │  │  Search API  │  │  PDF Gen API │      │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                │                  │              │
│         │                │                  │              │
│  ┌──────▼────────────────▼──────────────────▼───────┐      │
│  │         FastAPI Backend (Python 3.11+)          │      │
│  │                                                  │      │
│  │  • SanityDataStore (19 methods)                 │      │
│  │  • YouComClient (nostalgia + realtime)          │      │
│  │  • FoxitClient (cognitive reports)              │      │
│  │  • Insights Endpoint (GROQ showcase)            │      │
│  │  • Reports Endpoint (PDF download)              │      │
│  └──────────────────────────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Environment Setup

### Required API Keys

Add these to `backend/.env`:

```bash
# ========================================
# P3 - Sanity CMS Integration
# ========================================
SANITY_PROJECT_ID=5syqstxl
SANITY_DATASET=production
SANITY_TOKEN=your_sanity_token_here
# Get token: https://www.sanity.io/manage/personal/tokens
# Required permissions: Editor or Admin

# ========================================
# P3 - You.com Search API
# ========================================
YOUCOM_API_KEY=your_youcom_api_key_here
# Get key: https://you.com/platform
# Free $100 credits automatically provided!
# Challenge: Build AI Agents That Think, Reason & Search Live

# ========================================
# P3 - Foxit Document Generation API
# ========================================
FOXIT_BASE_URL=https://na1.fusion.foxit.com
FOXIT_DOCUMENT_GENERATION_CLIENT_ID=your_client_id
FOXIT_DOCUMENT_GENERATION_API_SECRET=your_client_secret
# Get credentials: https://developers.foxit.com/
# Used for: Cognitive health report PDFs
```

### Obtaining API Keys

#### Sanity CMS
1. Go to https://www.sanity.io/manage
2. Navigate to project `5syqstxl`
3. Go to **API** → **Tokens**
4. Create token with **Editor** permissions
5. Copy token to `SANITY_TOKEN`

#### You.com ($100 Free Credits!)
1. Visit https://you.com/platform
2. Sign up (free!)
3. $100 API credits automatically added
4. Go to **API Keys** → **Create Key**
5. Copy key to `YOUCOM_API_KEY`

**Hackathon Track**: Build AI Agents That Think, Reason & Search Live  
**Prizes**: $50 Amazon Gift Card + 200 API Credits for best use

#### Foxit PDF APIs
1. Visit https://developers.foxit.com/
2. Register for Developer account
3. Request **365-Day Free Trial** (instant approval)
4. Copy `Client ID` and `Client Secret`

---

## 🗂️ Sanity Schema

### Document Types (5 Required for Challenge)

#### 1. Patient
```javascript
{
  _type: 'patient',
  name: 'Dorothy Chen',
  birth_year: 1951,
  age: 75,
  location: 'San Francisco, CA',
  medications: [...],
  preferences: {
    interests: ['gardening', 'family'],
    communication_style: 'warm and patient'
  }
}
```

#### 2. Conversation
```javascript
{
  _type: 'conversation',
  patient: { _ref: 'patient-id' },  // Reference!
  transcript: 'Full conversation...',
  summary: 'Dorothy discussed...',
  detected_mood: 'happy',
  cognitive_metrics: {
    vocabulary_diversity: 0.72,
    topic_coherence: 0.85,
    repetition_rate: 0.03
  },
  timestamp: '2026-02-11T10:30:00Z'
}
```

#### 3. Family Member
```javascript
{
  _type: 'familyMember',
  patient: { _ref: 'patient-id' },  // Reference!
  name: 'Sarah Chen',
  relationship: 'daughter',
  email: 'sarah@example.com',
  phone: '+1234567890',
  notification_preferences: ['email', 'sms']
}
```

#### 4. Wellness Digest
```javascript
{
  _type: 'wellnessDigest',
  patient: { _ref: 'patient-id' },  // Reference!
  date: '2026-02-11',
  cognitive_score: 87,
  mood_summary: 'Positive engagement',
  alert_count: 0,
  conversation_count: 3
}
```

#### 5. Alert
```javascript
{
  _type: 'alert',
  patient: { _ref: 'patient-id' },  // Reference!
  severity: 'high',
  alert_type: 'cognitive_decline',
  message: 'Significant increase in repetition',
  acknowledged: false,
  timestamp: '2026-02-11T14:00:00Z'
}
```

### Schema Files Created (Phase 1 ✅)

Located in `studio-claracare/schemaTypes/`:
- `patient.ts`
- `conversation.ts`
- `familyMember.ts`
- `wellnessDigest.ts`
- `alert.ts`

---

## 🔌 API Integration Details

### 1. SanityDataStore (`backend/app/storage/sanity.py`)

**Purpose**: Production data store replacing InMemoryDataStore

**Key Features**:
- Implements all 19 `DataStore` protocol methods
- GROQ queries for cross-document retrieval
- Field mapping: `camelCase` (Sanity) ↔ `snake_case` (Python)
- Async HTTP client with connection pooling

**Example GROQ Query** (from `get_patient_insights`):
```python
*[_type == "conversation" && patient._ref == $patient_id] {
  detected_mood,
  cognitive_metrics
}
```

**Critical**: Automatically selected when `SANITY_PROJECT_ID`, `SANITY_DATASET`, and `SANITY_TOKEN` are set. Falls back to `InMemoryDataStore` if not configured.

---

### 2. YouComClient (`backend/app/nostalgia/youcom_client.py`)

**Purpose**: Real-time web search with citations

**Official API**: https://api.ydc-index.io/v1/search

#### Method 1: `search_nostalgia(birth_year, trigger_reason)`

Searches era-specific content from patient's **golden years** (ages 15-25):

```python
# Patient born 1951 → Golden years 1966-1976
nostalgia_data = await youcom_client.search_nostalgia(
    birth_year=1951,
    trigger_reason="feeling lonely"
)

# Returns:
{
    "music": ["The Beatles - Yesterday", "Led Zeppelin - Stairway to Heaven"],
    "events": ["Moon landing (1969)", "Woodstock (1969)"],
    "culture": "The British Invasion and counterculture movement",
    "era": "1966-1976"
}
```

#### Method 2: `search_realtime(query)`

Live web search for answering patient questions:

```python
result = await youcom_client.search_realtime("weather today in San Francisco")

# Returns:
{
    "answer": "Sunny, 68°F with light winds...",
    "results": [
        {"title": "SF Weather", "snippet": "...", "url": "https://..."},
        ...
    ],
    "citations": ["https://weather.com/...", ...]
}
```

**Hackathon Integration**: Powers Clara's ability to discuss current events, answer factual questions, and trigger nostalgia-based conversations.

---

### 3. FoxitClient (`backend/app/reports/foxit_client.py`)

**Purpose**: Generate cognitive health PDF reports for families

**Official API**: https://na1.fusion.foxit.com/document-generation/api/GenerateDocumentBase64

#### How It Works

1. **Template**: DOCX file with text tags (e.g., `{{patient_name}}`, `{{cognitive_score}}`)
2. **Data**: JSON with patient metrics, trends, recommendations
3. **API Call**: Foxit merges data into template → returns Base64 PDF
4. **Download**: Family members get polished report via `/api/reports/{patient_id}/download`

**Current Status**: Mock PDF fallback (API integration ready, template pending)

---

## 🚀 API Endpoints (P3)

### GET `/api/insights/{patient_id}`
**Purpose**: Sanity Challenge showcase - cross-document GROQ queries

**Response**:
```json
{
  "patient_id": "patient-dorothy-001",
  "cognitive_by_mood": {
    "happy": {"avg_vocabulary": 0.75, "avg_coherence": 0.88},
    "neutral": {"avg_vocabulary": 0.68, "avg_coherence": 0.82}
  },
  "nostalgia_effectiveness": {
    "total_nostalgia_conversations": 12,
    "avg_mood_improvement": 0.23
  },
  "alert_summary": {
    "total": 5,
    "by_severity": {"high": 1, "medium": 3, "low": 1}
  }
}
```

**Implementation**: Uses `SanityDataStore.get_patient_insights()` with GROQ aggregation

---

### GET `/api/reports/{patient_id}/download`
**Purpose**: Download cognitive health PDF report

**Query Parameters**:
- `days` (optional): Report period (default: 30)

**Response**: PDF file (Content-Type: application/pdf)

**Filename**: `cognitive-report-{patient_name}-{date}.pdf`

---

## 🧪 Testing P3 Integration

### 1. Test Sanity Connection
```bash
cd backend
python3 -c "
from app.storage.sanity import SanityDataStore
import asyncio
import os

async def test():
    store = SanityDataStore(
        project_id=os.getenv('SANITY_PROJECT_ID'),
        dataset=os.getenv('SANITY_DATASET'),
        token=os.getenv('SANITY_TOKEN')
    )
    patients = await store.get_all_patients()
    print(f'✅ Found {len(patients)} patients')
    await store.close()

asyncio.run(test())
"
```

### 2. Test You.com Search
```bash
python3 -c "
from app.nostalgia.youcom_client import YouComClient
import asyncio
import os

async def test():
    client = YouComClient(api_key=os.getenv('YOUCOM_API_KEY'))
    
    # Test nostalgia
    result = await client.search_nostalgia(birth_year=1951)
    print('Nostalgia:', result['music'][:2])
    
    # Test realtime
    result = await client.search_realtime('weather today')
    print('Weather:', result['answer'][:100])
    
    await client.close()

asyncio.run(test())
"
```

### 3. Test Insights Endpoint
```bash
# Start server
python3 -m app.main

# In another terminal:
curl http://localhost:8000/api/insights/patient-dorothy-001
```

---

## 📊 Cursor MCP Setup (Sanity Challenge)

### Configuration File: `.cursor/mcp.json`
```json
{
  "mcpServers": {
    "sanity": {
      "command": "npx",
      "args": [
        "-y",
        "@sanity/mcp-server@latest",
        "--project-id",
        "5syqstxl",
        "--dataset",
        "production"
      ]
    }
  }
}
```

### Why MCP?
- **Required** for Sanity Challenge compliance
- Enables AI-powered GROQ queries in Cursor
- Screenshots needed for submission

### Phase 1 Completion (User Done ✅)
1. Created 5 schema types in Cursor
2. Deployed to Sanity project
3. MCP screenshots pending (after seed data)

---

## 🌱 Next Steps: Seed Data Script

### Create `backend/scripts/seed_sanity.py`

**Purpose**: Populate Sanity with rich test data

**Requirements**:
1. Dorothy Chen (patient) + baseline cognitive data
2. Sarah Chen (daughter, family member)
3. 10+ realistic conversations with varying moods
4. Wellness digests for last 30 days
5. Sample alerts (mix of severities)

**Usage**:
```bash
cd backend
python3 scripts/seed_sanity.py
```

**Output**: Fully populated Sanity dataset ready for demo

---

## 🎬 Demo Script (Submission)

### Sanity Challenge Demo
1. **Show MCP in Cursor**: GROQ query screenshots
2. **Show Insights Endpoint**: Cross-document aggregation
3. **Show 5 Document Types**: References between types
4. **Highlight**: Production-ready CMS for elder care data

### You.com Challenge Demo
1. **Nostalgia Mode**: "Tell me about music from the 1960s" → Era-specific results
2. **Real-time Q&A**: "What's the weather today?" → Live citation-backed answer
3. **Voice Integration**: Show Clara using both in conversation
4. **Highlight**: Real-time grounding beats static training data

### Foxit Integration
1. **Generate Report**: `/api/reports/patient-dorothy-001/download`
2. **Show PDF**: Cognitive scores, trends, recommendations
3. **Highlight**: Automated family reporting (differentiation from competitors)

---

## 📈 Success Metrics

### Sanity Challenge
- ✅ 5 document types with references
- ✅ MCP Server configuration
- ✅ Cross-document GROQ queries
- ⏳ MCP screenshots (pending seed data)

### You.com Challenge
- ✅ Nostalgia mode with era calculation
- ✅ Real-time search with citations
- ✅ Voice agent integration
- ✅ $100 free credits utilized

### Technical Debt: None
All P3 code follows P2 rules:
- ✅ No `datetime.utcnow()` (using `datetime.now(UTC)`)
- ✅ No bare `except` clauses
- ✅ Field mapping exactly matches InMemoryDataStore
- ✅ 73 existing tests still pass (verified after integration)

---

## 🔗 Resources

- **Sanity Docs**: https://www.sanity.io/docs
- **You.com Platform**: https://you.com/platform
- **You.com Hackathon**: Build AI Agents That Think, Reason & Search Live
- **Foxit Developer Portal**: https://developers.foxit.com/
- **Project Repo**: github.com/your-username/clara-care

---

**P3 Status**: Backend ✅ | Schemas ✅ | Seed Data ⏳ | Testing ⏳ | Demo Ready 🎯
