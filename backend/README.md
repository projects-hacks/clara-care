# ClaraCare Backend

AI voice companion for elderly care - phone-based daily check-ins with Clara.

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure .env
DEEPGRAM_API_KEY=your_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Run
python3 -m app.main
```

## Architecture

```
Patient Phone → Twilio → Clara (Deepgram + GPT-4) → Functions → Sanity/APIs
```

**Clara can:**
- Have natural conversations
- Remind about medications
- Share nostalgia and news
- Detect distress and alert family
- Save conversation summaries

## API

- `GET /health` - Server status
- `POST /voice/call/patient` - Clara calls a patient
- `GET /voice/calls` - List active calls
- `WS /voice/twilio` - Twilio media stream

## Deployment

Update `SERVER_PUBLIC_URL` in `.env` with your public domain, then deploy to Replit or any cloud platform.

## Testing

```bash
python3 tests/test_voice.py
python3 quickstart.py
```
