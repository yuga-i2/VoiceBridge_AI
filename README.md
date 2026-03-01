# 🌾 VoiceBridge AI — Sahaya (सहाया)

> **AI that calls farmers. Farmers don't call AI.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-Amplify-brightgreen)](https://master.dk0lrulrclio3.amplifyapp.com)
[![API](https://img.shields.io/badge/API-Lambda_Live-orange)](https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/health)
[![AWS Services](https://img.shields.io/badge/AWS_Services-8%2F8_Live-blue)](#aws-architecture)
[![Region](https://img.shields.io/badge/Region-ap--southeast--1-yellow)](#aws-architecture)

**🔗 Live Demo:** https://master.dk0lrulrclio3.amplifyapp.com  
**🔗 API Health:** https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/health

---

## The Problem

**₹2.73 lakh crore** in welfare benefits go unclaimed every year in India.

Not because farmers don't qualify. Because nobody told them.

| Access Method | Reality | Completion Rate |
|---|---|---|
| Web portals | Require digital literacy | 5% |
| Mobile apps | Need smartphones (58% excluded) | 8% |
| Call centres | Farmer must call first | 5% |
| Field officers | ₹2,700 per farmer → only 200K/year | 100% but unscalable |

**135 million farmers eligible. 70% receive nothing.**

---

## Sahaya's Solution

Sahaya **calls farmers first** on any phone — even a ₹500 Nokia from 2005.
In one 3-minute Hindi call, Sahaya:

1. 🔊 **Plays a 30-second peer success story** from the farmer's own district (Voice Memory Network)
2. ❓ **Asks 2 simple questions** — land size + KCC status (press 1 or 2)
3. 🎯 **Matches eligible schemes** from 10 verified government programmes
4. 📢 **Explains benefits in clear Hindi** with exact ₹ amounts
5. 📱 **Sends SMS checklist** — documents needed + where to apply
6. 📞 **Calls again in 3 days** — confirms application progress

Zero internet required. Zero digital literacy required. Zero app install required.

---

## Three Core Innovations

### 🔊 Voice Memory Network
Real 30-second audio clips from farmers in the same district who already received benefits.
- Stored on Amazon S3 (presigned URLs, 15-min expiry)
- Played automatically before asking any eligibility question
- **Peer trust in 30 seconds — more powerful than any government message**

### 📞 Proactive AI Outbound Calling
The system calls the farmer. The farmer just answers.
- Amazon Connect initiates outbound calls
- Works on 2G feature phones
- **Reaches 58% of rural India that smartphones and apps cannot**

### 🧠 Contextual Hindi AI
Claude 3 Haiku (Amazon Bedrock) generates personalized responses in Devanagari Hindi.
- Knows farmer's land size, state, KCC status
- Injects real peer success stories into responses
- Never invents benefit amounts — all data from DynamoDB
- **180× cheaper than field officers at ₹15 per farmer**

---

## AWS Architecture — 8 Live Services

```
Browser / Phone Call
        ↓
React (AWS Amplify CDN)
        ↓ HTTPS
API Gateway (ap-southeast-1)
        ↓
AWS Lambda — Flask/Zappa (512MB, 30s timeout)
        │
        ├─── Amazon Bedrock ──── Claude 3 Haiku
        │                        Hindi scheme explanations
        │                        [PLAY_VOICE_MEMORY:X] tags
        │
        ├─── Amazon DynamoDB ─── welfare_schemes table
        │                        10 schemes, verified ₹ amounts
        │
        ├─── Amazon S3 ──────── voicebridge-audio-yuga bucket
        │                        Voice Memory clips (farmer stories)
        │                        Polly TTS output audio
        │
        ├─── Amazon Polly ────── Kajal Neural voice (Hindi)
        │                        Generates Sahaya's voice responses
        │
        ├─── Amazon Transcribe ─ hi-IN, ml-IN, ta-IN
        │                        Converts farmer speech to text
        │
        ├─── Amazon SNS ─────── SMS document checklist
        │                        Sent after scheme recommendation
        │
        ├─── Amazon Connect ──── Outbound call infrastructure
        │                        6-stage TwiML call flow
        │
        └─── AWS Lambda ─────── Serverless, auto-scales
                                 Flask + Zappa deployment
```

**Region:** ap-southeast-1 (Singapore) — All 8 services live, none mocked.

### Regional Language Support (v1.3.2b)
Sarvam AI Bulbul v2 handles 5 Indian languages on the frontend:

| Language | Code | Speaker |
|---|---|---|
| Hindi | hi-IN | (backend Polly Kajal) |
| Tamil | ta-IN | anushka |
| Kannada | kn-IN | anushka |
| Telugu | te-IN | anushka |
| Malayalam | ml-IN | manisha |

---

## The Economics

| | Sahaya | Field Officers |
|---|---|---|
| Cost per farmer | **₹15** | ₹2,700 |
| Annual capacity | Unlimited | ~200,000 |
| Languages | Hindi + 4 regional | Hindi only |
| Availability | 24/7 | Business hours |
| **Cost multiplier** | **180× cheaper** | Baseline |

At 135 million farmers: **₹36,000 crore in savings vs field officers**

Break-even: **3 successful applications per 100 calls**

---

## API Reference

**Base URL:** `https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Service status + mock_mode flag |
| GET | `/api/schemes` | All 10 welfare schemes (DynamoDB) |
| POST | `/api/eligibility-check` | Match farmer to eligible schemes |
| POST | `/api/chat` | Main AI conversation (Bedrock) |
| GET | `/api/voice-memory/{scheme_id}` | Farmer success story audio (S3) |
| POST | `/api/text-to-speech` | Hindi TTS via Polly (Kajal neural) |
| POST | `/api/sarvam-tts` | Regional TTS via Sarvam AI bulbul:v2 |
| POST | `/api/speech-to-text` | Hindi/Regional STT via Transcribe |
| POST | `/api/initiate-call` | Outbound call via Connect/Twilio |

### Key API Example

**POST /api/chat — request:**
```json
{
  "message": "पीएम किसान के बारे में बताओ",
  "farmer_profile": {
    "name": "Ramesh Kumar",
    "land_acres": 2,
    "state": "Karnataka",
    "has_kcc": false,
    "has_bank_account": true
  },
  "conversation_history": [
    {"role": "assistant", "content": "नमस्ते! मैं सहाया हूँ।"}
  ],
  "language": "hi-IN"
}
```

**Response:**
```json
{
  "success": true,
  "response_text": "PM-किसान योजना से आपको ₹6,000 मिलेंगे...",
  "audio_url": "https://s3-presigned-polly-audio.mp3",
  "voice_memory_clip": "PM_KISAN",
  "matched_schemes": ["PM_KISAN"],
  "stage": "scheme_explanation"
}
```

---

## The 10 Welfare Schemes

All amounts verified against official government sources.

| scheme_id | Hindi Name | Benefit |
|---|---|---|
| PM_KISAN | प्रधानमंत्री किसान सम्मान निधि | ₹6,000/year (3 × ₹2,000) |
| KCC | किसान क्रेडिट कार्ड | ₹3 lakh loan @ 4% interest |
| PMFBY | प्रधानमंत्री फसल बीमा योजना | Full crop value, 2% premium |
| AYUSHMAN_BHARAT | आयुष्मान भारत | ₹5 lakh/family health insurance |
| MGNREGS | मनरेगा | 100 days @ ₹220-357/day |
| SOIL_HEALTH_CARD | मृदा स्वास्थ्य कार्ड | Free soil testing + recommendations |
| PM_AWAS_GRAMIN | प्रधानमंत्री आवास (ग्रामीण) | ₹1.2-1.3 lakh housing subsidy |
| NFSA_RATION | राष्ट्रीय खाद्य सुरक्षा | Subsidised grain ₹1-3/kg |
| ATAL_PENSION | अटल पेंशन योजना | ₹1,000-5,000/month after 60 |
| SUKANYA_SAMRIDDHI | सुकन्या समृद्धि योजना | 8.2% interest girl child savings |

---

## Quick Start (New Machine)

### Prerequisites
- Node.js 16+, Python 3.10+, AWS CLI

### Frontend — localhost:3000
```bash
cd frontend
npm install
echo "REACT_APP_API_URL=http://localhost:5000" > .env.development
npm start
```

### Backend — localhost:5000
```bash
cd voicebridge-backend
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate        # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
python app.py
```

### Run All Tests
```bash
cd voicebridge-backend
pytest tests/ -v
```

### Test Live API
```bash
curl https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/health
```

---

## Project Structure

```
VoiceBridge_AI/
├── frontend/                          React app → AWS Amplify
│   ├── src/
│   │   ├── App.js                    Main conversation UI
│   │   └── config/api.js             API endpoints (don't hardcode!)
│   ├── .env                          REACT_APP_API_URL=Lambda
│   └── .env.development              REACT_APP_API_URL=localhost:5000
│
└── voicebridge-backend/              Flask → AWS Lambda via Zappa
    ├── app.py                        Entry point, 9 routes
    ├── config/settings.py            Loads .env, all config
    ├── services/
    │   ├── ai_service.py             Bedrock Claude 3 Haiku
    │   ├── tts_service.py            Polly Kajal Neural
    │   ├── stt_service.py            Transcribe (hi/ml/ta)
    │   ├── scheme_service.py         DynamoDB welfare_schemes
    │   ├── sms_service.py            SNS SMS
    │   └── voice_memory_service.py   S3 presigned URLs
    ├── routes/call_routes.py         TwiML 6-stage flow
    ├── data/
    │   ├── schemes.json              Local DynamoDB mirror
    │   └── voice_memory/             PM_KISAN.mp3, KCC.mp3, PMFBY.mp3
    ├── tests/                        All test files
    ├── docs/
    │   ├── CONSTRAINTS.md            Hard dev rules
    │   └── API_TRACKER.md            Endpoint status
    ├── .env.example                  Template
    ├── requirements.txt              Python deps
    └── zappa_settings.json           Lambda config
```

---

## Deployment

### Frontend (auto-redeploys on git push)
```bash
cd frontend && npm run build
git add -A && git commit -m "message"
git push origin master
# Amplify rebuilds in ~3 minutes
```

### Backend (Lambda)
```bash
cd voicebridge-backend
zappa update dev
```

### Fix S3 Audio Files
```bash
cd voicebridge-backend
python utils/normalize_s3_audio.py --apply
```

---

## Rules Never to Break

1. **Never hardcode `/api` URLs** in frontend — use `API.*` from `config/api.js`
2. **Never import from root folders** — all app code in `voicebridge-backend/`
3. **Never call Anthropic API from frontend** — all AI via Lambda
4. **Always pass full `conversation_history`** to `/api/chat`
5. **S3 audio files must end in `.mp3`** — not `.mp3.mpeg`
6. **Scheme IDs in `/api/eligibility-check`** — extract from objects: `res.data.eligible_schemes.map(s => s.scheme_id)`
7. **Set S3 CORS** to allow https://master.dk0lrulrclio3.amplifyapp.com
8. **Never commit `.env`** with real AWS credentials
9. **Sahaya always speaks first** — never wait for user input
10. **Never add packages** without checking docs/CONSTRAINTS.md

---

## Privacy & Compliance

- ✅ **DPDP Act 2023 compliant** by design
- ✅ Zero Aadhaar storage — never collected
- ✅ Zero OTP collection — never requested
- ✅ Anti-scam statement on every call
- ✅ Auto-delete after 90 days
- ✅ Farmer consent via DTMF before personal questions

---

## Need Help?

- **Live Demo:** https://master.dk0lrulrclio3.amplifyapp.com
- **API Status:** https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/health
- **GitHub Repo:** https://github.com/yuga-i2/VoiceBridge_AI
- **AWS Region:** ap-southeast-1 (Singapore)
- **Backup Branch:** origin/backup-before-final-cleanup

---

## Hack2Skill AWS AI Hackathon 2026

**Deadline:** March 3, 2026  
**Team:** Yuga Team  
**Status:** ✅ Production Ready

> "135 million farmers. ₹15 per call. Sahaya calls them."
