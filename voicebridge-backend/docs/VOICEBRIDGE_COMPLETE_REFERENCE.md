# VoiceBridge AI — Complete Project Reference

> **Upload this file to any new chat or Copilot session to instantly understand the entire project.**

This document contains 100% of the project information needed to understand, set up, develop, and deploy VoiceBridge AI.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Live URLs & Credentials](#live-urls--credentials)
3. [Architecture](#architecture)
4. [Repository Structure](#repository-structure)
5. [Frontend Setup (New Laptop)](#frontend-setup-new-laptop)
6. [Backend Setup (New Laptop)](#backend-setup-new-laptop)
7. [Configuration Files](#configuration-files)
8. [API Reference](#api-reference)
9. [Database Schema](#database-schema)
10. [S3 Structure & CORS](#s3-structure--cors)
11. [Conversation Flow](#conversation-flow)
12. [Voice Memory Clips](#voice-memory-clips)
13. [Farmer Profiles](#farmer-profiles)
14. [Running Locally](#running-locally)
15. [Deployment](#deployment)
16. [Known Issues & Fixes](#known-issues--fixes)
17. [Rules Never to Break](#rules-never-to-break)
18. [Troubleshooting](#troubleshooting)
19. [Recent Updates (v1.3.2b)](#recent-updates-v132b---february-28-2026)
20. [Sarvam AI Regional Language Implementation](#recent-implementation-details-v132b)

---

## Project Overview

**VoiceBridge AI** is an outbound AI voice caller named **Sahaya** that proactively calls Indian farmers, speaks Hindi, and guides them through government welfare scheme eligibility.

### Core Value Proposition
- **Cost:** ₹15-25 per farmer (Sahaya) vs ₹2,700 for field officers
- **ROI:** 180× cheaper
- **Scale:** Covers 135 million farmers
- **Approach:** Proactive outbound calling (Sahaya initiates, farmer just answers)
- **Language:** Hindi only (Devanagari script)
- **Region:** ap-southeast-1 (Singapore)

### Key Features
1. **Bedrock AI** (Claude 3 Haiku) generates personalized Hindi responses
2. **Polly TTS** (Kajal neural voice) generates natural-sounding responses
3. **Web Speech API** for farmer speech-to-text (hi-IN language)
4. **Voice Memory Network** — peer farmer success story audio clips
5. **Eligibility Matching** — recommends welfare schemes based on farmer profile
6. **Progressive Conversation** — 6-stage call flow
7. **Document Guidance** — lists required documents in Hindi
8. **SMS Confirmation** — SNS sends follow-up via SMS

---

## Live URLs & Credentials

### Public URLs

| Service | URL |
|---------|-----|
| Frontend (Amplify) | https://master.dk0lrulrclio3.amplifyapp.com |
| Backend (Lambda + API Gateway) | https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev |
| GitHub Repository | https://github.com/yuga-i2/VoiceBridge_AI |

### AWS Configuration

| Service | Value |
|---------|-------|
| AWS Region | ap-southeast-1 (Singapore) |
| DynamoDB Table | welfare_schemes |
| S3 Bucket (Audio) | voicebridge-audio-yuga |
| S3 Bucket (Assets) | voicebridge-assets-yuga |
| Bedrock Model | anthropic.claude-3-haiku-20240307-v1:0 |
| Polly Voice | Kajal (Hindi, neural) |
| Sarvam AI TTS | bulbul:v2 (v1.3.2b+) |
| Sarvam Speakers | anushka, manisha |
| Zappa Stage | dev |

### Sarvam AI Configuration (NEW in v1.3.2b)

| Setting | Value |
|---------|-------|
| Endpoint | https://api.sarvam.ai/text-to-speech |
| API Key | sk_4kqzt... (in zappa_settings.json) |
| Model | bulbul:v2 |
| Languages | hi-IN, ta-IN, kn-IN, te-IN, ml-IN |
| Speakers | anushka (hi/ta/kn/te), manisha (ml) |
| Pace | 0.75 (slower for clarity) |
| Pitch | 0 (neutral) |
| Loudness | 1.5 (enhanced) |
| Preprocessing | enabled |
| Timeout | 30 seconds |

### Twilio (for Call Simulation)

| Setting | Value |
|---------|-------|
| Phone Number | +12282252952 |
| Verified India Number | +917736448307 |
| Account SID | ACee22e452... (in Twilio Console) |
| Auth Token | (never commit to git) |

### Important Notes

⚠️ **Credentials Management:**
- AWS credentials in `~/.aws/credentials` (local) or Lambda environment (production)
- Twilio Auth Token in `.env` only, never commit to git
- Frontend uses environment variable: `REACT_APP_API_URL`

---

## Architecture

### System Diagram

```
User's Browser
    ↓
React Frontend (Amplify)
    ↓ API calls using API.* constants
API Gateway (ap-southeast-1)
    ↓
Lambda (Flask Zappa)
    ├─→ Bedrock (Claude 3 Haiku)     [AI responses]
    ├─→ DynamoDB                     [welfare schemes]
    ├─→ S3                           [audio files, presigned URLs]
    ├─→ Polly                        [text-to-speech]
    ├─→ Transcribe                   [speech-to-text]
    ├─→ SNS                          [SMS alerts]
    └─→ Connect                      [outbound calls]
```

### Request Flow Example

1. User asks: "पीएम किसान के बारे में बताओ" (Tell me about PM-KISAN)
2. Frontend sends POST to `/api/chat` with conversation history
3. Lambda:
   - Validates farmer profile
   - Gets eligible scheme details from DynamoDB
   - Calls Bedrock to generate personalized Hindi response (with farmer story injected)
   - Extracts voice memory clip ID from response (e.g., "PM_KISAN")
   - Generates presigned S3 URL for voice memory audio
   - Calls Polly to generate audio for Sahaya's response
   - Returns: response_text, audio_url, voice_memory_clip
4. Frontend:
   - Plays Sahaya's Polly audio
   - After 0.8s pause, auto-plays voice memory clip
   - Highlights matched scheme in sidebar
   - Auto-resumes listening after playback (if continuous mode)

---

## Repository Structure

```
VoiceBridge_AI/
│
├── frontend/                          ← React app (Amplify)
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── src/
│   │   ├── App.js                    [MAIN LOGIC: 1238 lines]
│   │   │   ├── CLIP_INFO dict         (farmer stories)
│   │   │   ├── DEMO_FARMER            (test profile)
│   │   │   ├── CALL_STATES            (UI state machine)
│   │   │   ├── speakHindi()           (TTS fallback)
│   │   │   ├── Header component
│   │   │   ├── EligibilityScore component
│   │   │   ├── VoiceMemoryClip component (with isAutoPlaying prop)
│   │   │   ├── CallInitiator component
│   │   │   ├── playSequentially()     (NEW: auto-play voice memory)
│   │   │   ├── startListening()       (Web Speech API)
│   │   │   ├── sendMessage()          (chat handler)
│   │   │   ├── handleTextInput()      (text input handler)
│   │   │   └── Main App state machine
│   │   ├── config/
│   │   │   └── api.js                 [API constants]
│   │   ├── App.css
│   │   ├── index.js
│   │   └── setupTests.js
│   ├── .env                           (REACT_APP_API_URL for production)
│   ├── .env.development               (REACT_APP_API_URL=http://localhost:5000)
│   ├── package.json
│   ├── package-lock.json
│   └── README.md
│
├── voicebridge-backend/               ← Flask (Lambda)
│   ├── app.py                         [MAIN ENTRY: routes definition]
│   │   ├── /api/health                (GET: status check)
│   │   ├── /api/schemes               (GET: all schemes)
│   │   ├── /api/eligibility-check     (POST: check eligibility)
│   │   ├── /api/chat                  (POST: main conversation)
│   │   ├── /api/text-to-speech        (POST: Polly)
│   │   ├── /api/speech-to-text        (POST: Transcribe)
│   │   ├── /api/voice-memory/{id}     (GET: presigned URLs)
│   │   └── /api/initiate-call         (POST: outbound call)
│   │
│   ├── config/
│   │   └── settings.py                [load .env, all config vars]
│   │
│   ├── models/
│   │   └── farmer.py                  [FarmerProfile dataclass]
│   │
│   ├── services/
│   │   ├── ai_service.py              [Bedrock integration]
│   │   │   ├── FARMER_STORIES dict    (farmer success stories)
│   │   │   ├── SAHAYA_SYSTEM_PROMPT   (Bedrock system prompt)
│   │   │   ├── MOCK_RESPONSES dict    (fallback responses)
│   │   │   └── generate_response()    (main AI logic)
│   │   ├── tts_service.py             [Polly TTS]
│   │   ├── stt_service.py             [Transcribe]
│   │   ├── scheme_service.py          [DynamoDB queries]
│   │   ├── sms_service.py             [SNS SMS]
│   │   ├── call_service.py            [Connect outbound]
│   │   ├── voice_memory_service.py    [S3 presigned URLs]
│   │   └── providers/                 [Call provider implementations]
│   │       ├── twilio_call_provider.py
│   │       ├── connect_call_provider.py
│   │       └── mock_call_provider.py
│   │
│   ├── routes/
│   │   └── call_routes.py             [Twilio TwiML endpoints]
│   │
│   ├── data/
│   │   └── voice_memory/              [local audio clips]
│   │       ├── voice_memory_PM_KISAN.mp3
│   │       ├── voice_memory_KCC.mp3
│   │       └── voice_memory_PMFBY.mp3
│   │
│   ├── docs/
│   │   ├── API_TRACKER.md
│   │   ├── AWS_REFERENCE.md
│   │   ├── CONSTRAINTS.md
│   │   ├── PROJECT_REFERENCE.md
│   │   └── VOICEBRIDGE_COMPLETE_REFERENCE.md  [THIS FILE]
│   │
│   ├── tests/
│   │   ├── test_ai.py
│   │   ├── test_call_system.py
│   │   ├── test_schemes.py
│   │   ├── test_stt.py
│   │   └── test_tts.py
│   │
│   ├── utils/
│   │   └── normalize_s3_audio.py      [fixes wrong audio extensions]
│   │
│   ├── .env                           [AWS credentials, config vars]
│   ├── .env.example                   [template]
│   ├── requirements.txt               [Python dependencies]
│   ├── zappa_settings.json            [Lambda deployment config]
│   └── README.md
│
├── .gitignore
├── .git/
├── PHASE_4_SUMMARY.md
├── README.md
├── SUBMISSION_CHECKLIST.md
└── package-lock.json
```

---

## Frontend Setup (New Laptop)

### Prerequisites

- Node.js 16+ (check: `node --version`)
- npm 8+ (check: `npm --version`)
- Git (check: `git --version`)

### Step 1: Clone Repository

```bash
git clone https://github.com/yuga-i2/VoiceBridge_AI.git
cd VoiceBridge_AI/frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

This installs:
- react (main framework)
- axios (HTTP client for API calls)
- tailwindcss (styling)

### Step 3: Environment Configuration

**For Development (Local Backend):**

Create `.env.development`:
```bash
REACT_APP_API_URL=http://localhost:5000
```

**For Production (AWS Lambda):**

Amplify Console → App Settings → Environment variables:
```
REACT_APP_API_URL=https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev
```

### Step 4: Run Locally

```bash
npm start
```

Opens at `http://localhost:3000`

### Step 5: Build for Production

```bash
npm run build
```

Creates optimized `build/` folder (~83 KB gzipped)

### Step 6: Deploy to Amplify (Automatic)

```bash
git add -A
git commit -m "your message"
git push origin master
```

Amplify automatically builds and deploys on push.

### Troubleshooting Frontend Setup

**Issue:** "Cannot find module 'react'"
```bash
# Solution:
rm -rf node_modules package-lock.json
npm install
```

**Issue:** "REACT_APP_API_URL is undefined"
```bash
# Check:
echo $REACT_APP_API_URL

# In .env:
REACT_APP_API_URL=https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev

# Restart npm start
npm start
```

**Issue:** "Mic permission denied" (browser)
```
Click browser mic icon in address bar → Allow
```

---

## Backend Setup (New Laptop)

### Prerequisites

- Python 3.10+ (check: `python --version`)
- pip (check: `pip --version`)
- AWS CLI configured (check: `aws configure list`)
- Git (check: `git --version`)

### Step 1: Clone Repository

```bash
git clone https://github.com/yuga-i2/VoiceBridge_AI.git
cd VoiceBridge_AI/voicebridge-backend
```

### Step 2: Create Virtual Environment

```bash
# Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
```

Check activation:
```bash
which python  # should show .venv path
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt** includes:
```
flask                    (web framework)
flask-cors              (CORS handling)
boto3                   (AWS SDK)
python-dotenv           (load .env)
pydub                   (audio processing)
requests                (HTTP)
twilio                  (Twilio API)
zappa                   (Lambda deployment)
```

### Step 4: AWS Configuration

**Option A: Local Development**

```bash
aws configure
# Enter:
# AWS Access Key ID: ...
# AWS Secret Access Key: ...
# Default region: ap-southeast-1
# Default output format: json
```

Credentials stored in: `~/.aws/credentials`

**Option B: Lambda Deployment**

Set environment variables in Lambda console or `zappa_settings.json`:
```json
{
  "dev": {
    "aws_region": "ap-southeast-1",
    "environment_variables": {
      "AWS_REGION": "ap-southeast-1",
      "USE_MOCK": "false",
      "DYNAMODB_TABLE_NAME": "welfare_schemes",
      "S3_AUDIO_BUCKET": "voicebridge-audio-yuga"
    }
  }
}
```

### Step 5: Configure Environment File

Create `.env`:
```bash
# ─── Flask ─────────────────────────
FLASK_ENV=development
FLASK_PORT=5000

# ─── AWS Core ──────────────────────
AWS_REGION=ap-southeast-1
USE_MOCK=false
# (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY: rely on ~/.aws/credentials)

# ─── AWS Services ──────────────────
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
DYNAMODB_TABLE_NAME=welfare_schemes
S3_AUDIO_BUCKET=voicebridge-audio-yuga
S3_ASSETS_BUCKET=voicebridge-assets-yuga
SNS_SENDER_ID=Sahaya

# ─── Twilio ────────────────────────
TWILIO_ACCOUNT_SID=ACee22e452...
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_PHONE_NUMBER=+12282252952

# ─── Mock Mode ─────────────────────
# SET TO 'true' for testing without AWS:
USE_MOCK=true
```

Copy from `.env.example` if exists:
```bash
cp .env.example .env
# Then edit with your values
```

### Step 6: Run Locally

```bash
python app.py
```

Server starts at `http://localhost:5000`

**Test health endpoint:**
```bash
curl http://localhost:5000/api/health
# Response: {"status":"ok","mock_mode":false,"version":"1.0.0"}
```

### Step 7: Run Tests

```bash
pytest tests/ -v
```

### Step 8: Deploy to AWS Lambda

**First time:**
```bash
zappa init dev
# Follow prompts...
```

**Update existing deployment:**
```bash
zappa update dev
```

**View logs:**
```bash
zappa tail dev
```

### Troubleshooting Backend Setup

**Issue:** "ModuleNotFoundError: No module named 'flask'"
```bash
# Check venv is activated (should see (.venv) in prompt)
pip install -r requirements.txt
```

**Issue:** "Unable to locate credentials"
```bash
# AWS credentials not found
aws configure
# OR set environment variables:
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=ap-southeast-1
```

**Issue:** "zappa command not found"
```bash
# Zappa not installed
pip install zappa
```

**Issue:** "DynamoDB table not found"
```bash
# Table doesn't exist in your AWS account
# Create in AWS Console or via boto3:
python
>>> import boto3
>>> dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
>>> table = dynamodb.create_table(
...   TableName='welfare_schemes',
...   KeySchema=[{'AttributeName': 'scheme_id', 'KeyType': 'HASH'}],
...   AttributeDefinitions=[{'AttributeName': 'scheme_id', 'AttributeType': 'S'}],
...   BillingMode='PAY_PER_REQUEST'
... )
```

**Issue:** "S3 bucket not found"
```bash
# Create bucket:
aws s3 mb s3://voicebridge-audio-yuga --region ap-southeast-1

# Create subdirectories:
aws s3api put-object --bucket voicebridge-audio-yuga --key voice_memory/
aws s3api put-object --bucket voicebridge-audio-yuga --key tts_output/
aws s3api put-object --bucket voicebridge-audio-yuga --key transcribe_input/
```

---

## Configuration Files

### frontend/.env.development

Used during `npm start` (local development):
```bash
REACT_APP_API_URL=http://localhost:5000
```

### frontend/.env

Used during `npm run build` (production):
```bash
REACT_APP_API_URL=https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev
```

Or set in Amplify Console Environment Variables:
```
REACT_APP_API_URL=https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev
```

### voicebridge-backend/.env

```bash
# Flask
FLASK_ENV=development
FLASK_PORT=5000

# AWS
AWS_REGION=ap-southeast-1
USE_MOCK=false

# Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# DynamoDB
DYNAMODB_TABLE_NAME=welfare_schemes

# S3
S3_AUDIO_BUCKET=voicebridge-audio-yuga
S3_ASSETS_BUCKET=voicebridge-assets-yuga

# SNS
SNS_SENDER_ID=Sahaya

# Twilio
TWILIO_ACCOUNT_SID=ACee22e452...
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+12282252952
```

### voicebridge-backend/zappa_settings.json

```json
{
  "dev": {
    "app_function": "app.app",
    "aws_region": "ap-southeast-1",
    "runtime": "python3.13",
    "s3_bucket": "zappa-deployments-yuga",
    
    "environment_variables": {
      "FLASK_ENV": "production",
      "USE_MOCK": "false",
      "AWS_REGION": "ap-southeast-1",
      "BEDROCK_MODEL_ID": "anthropic.claude-3-haiku-20240307-v1:0",
      "DYNAMODB_TABLE_NAME": "welfare_schemes",
      "S3_AUDIO_BUCKET": "voicebridge-audio-yuga",
      "S3_ASSETS_BUCKET": "voicebridge-assets-yuga",
      "SNS_SENDER_ID": "Sahaya"
    },
    
    "keep_warm": false,
    "lambda_handler": "app.app",
    "memory_size": 512,
    "timeout": 30,
    "cors": true,
    "cors_allow_headers": ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"],
    "logs_level": "INFO",
    "xray_tracing": false
  }
}
```

### frontend/src/config/api.js

```javascript
const API_BASE = process.env.REACT_APP_API_URL
  || 'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev'

export const API = {
  health:           `${API_BASE}/api/health`,
  schemes:          `${API_BASE}/api/schemes`,
  eligibilityCheck: `${API_BASE}/api/eligibility-check`,
  chat:             `${API_BASE}/api/chat`,
  tts:              `${API_BASE}/api/text-to-speech`,
  stt:              `${API_BASE}/api/speech-to-text`,
  voiceMemory:      `${API_BASE}/api/voice-memory`,
  initiateCall:     `${API_BASE}/api/initiate-call`,
}

export default API
```

**CRITICAL:** All frontend API calls MUST use `API.*` constants, never hardcode URLs or use relative `/api/...`.

---

## API Reference

### Base URL

**Production:** https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev
**Local:** http://localhost:5000

---

### GET /api/health

Health check. Always returns 200.

**Response:**
```json
{
  "status": "ok",
  "mock_mode": false,
  "version": "1.0.0",
  "service": "VoiceBridge AI — Sahaya"
}
```

---

### GET /api/schemes

Get all 10 welfare schemes.

**Response:**
```json
{
  "success": true,
  "schemes": [
    {
      "scheme_id": "PM_KISAN",
      "name_en": "Pradhan Mantri Kisan Samman Nidhi",
      "name_hi": "प्रधानमंत्री किसान सम्मान निधि",
      "benefit": "₹6,000 per year in 3 installments of ₹2,000",
      "eligibility": "Small and marginal farmers",
      "apply_at": "Common Service Centre or PM-KISAN portal",
      "documents": ["Aadhaar card", "Land records", "Bank passbook"],
      "min_land_acres": "0",
      "income_limit": "0",
      "requires_kcc": false,
      "requires_bank_account": true
    },
    ...9 more schemes
  ],
  "total": 10
}
```

---

### POST /api/eligibility-check

Check farmer eligibility for schemes.

**Request:**
```json
{
  "farmer_profile": {
    "name": "Ramesh Kumar",
    "phone": "+919876543210",
    "land_acres": 2,
    "state": "Karnataka",
    "age": 45,
    "has_kcc": false,
    "has_bank_account": true,
    "annual_income": 50000
  }
}
```

**Response:** Returns FULL SCHEME OBJECTS, not just IDs.
```json
{
  "success": true,
  "eligible_schemes": [
    {
      "scheme_id": "PM_KISAN",
      "name_en": "Pradhan Mantri Kisan Samman Nidhi",
      "name_hi": "प्रधानमंत्री किसान सम्मान निधि",
      "benefit": "₹6,000 per year in 3 installments of ₹2,000"
    },
    {
      "scheme_id": "KCC",
      "name_en": "Kisan Credit Card",
      "name_hi": "किसान क्रेडिट कार्ड",
      "benefit": "Up to ₹3 lakh loan at 4% annual interest"
    },
    ...more schemes
  ],
  "total_eligible": 10,
  "total_schemes": 10,
  "total_benefit_summary": "₹2,500,000+ per year"
}
```

**Frontend Usage:**
```javascript
const res = await axios.post(API.eligibilityCheck, { farmer_profile })
// CRITICAL: Extract IDs only:
const schemeIds = res.data.eligible_schemes.map(s => s.scheme_id)
// schemeIds = ['PM_KISAN', 'KCC', 'PMFBY', ...]
```

---

### POST /api/chat

Main conversation endpoint. Generates Sahaya's response using Bedrock.

**Request:**
```json
{
  "message": "पीएम किसान योजना के बारे में बताओ",
  "farmer_profile": {
    "name": "Ramesh Kumar",
    "land_acres": 2,
    "state": "Karnataka",
    "has_kcc": false,
    "has_bank_account": true,
    "age": 45,
    "annual_income": 50000
  },
  "conversation_history": [
    {
      "role": "assistant",
      "content": "नमस्ते! मैं सहाया हूँ, एक सरकारी कल्याण सहायक।"
    },
    {
      "role": "user",
      "content": "आप कौन हो?"
    }
  ]
}
```

**CRITICAL:** Always pass full `conversation_history` — Lambda needs context.

**Response:**
```json
{
  "success": true,
  "response_text": "PM-किसान योजना बहुत अच्छी है! आपको हर साल ₹6,000 मिलते हैं...",
  "matched_schemes": ["PM_KISAN"],
  "voice_memory_clip": "PM_KISAN",
  "audio_url": "https://voicebridge-audio-yuga.s3.ap-southeast-1.amazonaws.com/tts_output/audio_20240301_123456.mp3?AWSAccessKeyId=...",
  "stage": "scheme_explanation"
}
```

**What to do with response:**
1. Display `response_text` to user
2. Play `audio_url` via Polly (if available)
3. Fetch voice memory clip from `/api/voice-memory/{voice_memory_clip}`
4. Highlight matched schemes in sidebar
5. Auto-resume listening (if conversation mode)

---

### GET /api/voice-memory/{scheme_id}

Get presigned URL for voice memory clip.

**scheme_id values:** PM_KISAN, KCC, PMFBY

**Response:**
```json
{
  "success": true,
  "audio_url": "https://voicebridge-audio-yuga.s3.ap-southeast-1.amazonaws.com/voice_memory/voice_memory_PM_KISAN.mp3?AWSAccessKeyId=...",
  "farmer_name": "Suresh Kumar",
  "district": "Tumkur, Karnataka",
  "quote": "PM-KISAN se ₹6,000 mile. Bacchon ki fees bhari."
}
```

**Frontend Usage:**
```javascript
const vmRes = await fetch(
  `https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/voice-memory/${schemeId}`
)
const vmData = await vmRes.json()
// Play: vmData.audio_url
```

Presigned URL expires in 900 seconds (15 minutes).

---

### POST /api/text-to-speech

Generate Polly audio for Hindi text.

**Request:**
```json
{
  "text": "नमस्ते! मैं सहाया हूँ।",
  "voice": "Kajal"
}
```

**Response:**
```json
{
  "success": true,
  "audio_url": "https://voicebridge-audio-yuga.s3.ap-southeast-1.amazonaws.com/tts_output/audio_20240301_123456.mp3?AWSAccessKeyId=...",
  "duration_seconds": 2.5
}
```

Voice options: Kajal (Hindi, neural, female), Aditi (Hindi, neural, female)

---

### POST /api/sarvam-tts

Generate regional language audio using Sarvam AI Bulbul v2 model. Supports 5 Indian languages with natural-sounding voices.

**NEW in v1.3.2b (Feb 28, 2026):** Now uses bulbul:v2 model with anushka speaker for Tamil, Kannada, Telugu, and Hindi. Malayalam uses manisha speaker. Slower pace (0.75) for clarity.

**Request:**
```json
{
  "text": "नमस्कार, मैं आपकी सहायता के लिए यहाँ हूँ।",
  "language": "hi-IN"
}
```

**Supported Languages:**
| Language Code | Language | Speaker |
|---|---|---|
| hi-IN | Hindi (Devanagari) | anushka |
| ta-IN | Tamil (Tamil script) | anushka |
| kn-IN | Kannada (Kannada script) | anushka |
| te-IN | Telugu (Telugu script) | anushka |
| ml-IN | Malayalam (Malayalam script) | manisha |

**Response:**
```json
{
  "success": true,
  "audio_url": "https://voicebridge-audio-yuga.s3.ap-southeast-1.amazonaws.com/sarvam-audio/abc123def456.wav?AWSAccessKeyId=...",
  "language": "hi-IN",
  "duration_seconds": 3.2
}
```

**Error Responses:**
```json
{
  "success": false,
  "error": "Sarvam API returned 400"
}
```

**Sarvam API Configuration (Backend):**
- **Model:** bulbul:v2 (supports pitch/loudness controls, excludes unwanted parameters)
- **Pace:** 0.75 (0.5-1.0 range; 0.75 is slower, clearer for farmer understanding)
- **Pitch:** 0 (neutral, natural tone)
- **Loudness:** 1.5 (enhanced for phone systems)
- **Preprocessing:** enabled (removes background noise, normalizes text)
- **Timeout:** 30 seconds

**CRITICAL Payload Format:**
```python
payload = {
    'inputs': [text],  # Array of single text item
    'target_language_code': language,  # BCP-47 format (hi-IN, ml-IN, etc.)
    'speaker': speaker_id,  # anushka or manisha
    'model': 'bulbul:v2',  # Important: v2 only
    'pace': 0.75,
    'pitch': 0,
    'loudness': 1.5,
    'enable_preprocessing': True
}
```

**Frontend Usage:**
```javascript
// Call Sarvam endpoint for regional language support
const res = await axios.post(`${API_URL}/api/sarvam-tts`, {
  text: responseText,
  language: selectedLanguage  // e.g., 'ml-IN'
})
const audioUrl = res.data.audio_url
// Play audioUrl in Audio element
```

**Fallback Logic (in /api/chat):**
If Sarvam fails, falls back to Polly TTS (Hindi only).

---

### POST /api/speech-to-text

Transcribe farmer's voice using AWS Transcribe.

**Request:**
FormData with file:
```
audio: <audio blob from Web Speech API>
language: "hi-IN"
```

**Response:**
```json
{
  "success": true,
  "transcript": "पीएम किसान योजना के बारे में बताओ",
  "confidence": 0.92
}
```

**NOTE:** DO NOT add `VocabularyName` parameter — vocabulary 'voicebridge-vocab' doesn't exist.

---

### POST /api/initiate-call

Initiate outbound call to farmer (via Connect or Twilio mock).

**Request:**
```json
{
  "farmer_phone": "+919876543210",
  "farmer_name": "Ramesh Kumar",
  "scheme_ids": ["PM_KISAN", "KCC"]
}
```

**Response:**
```json
{
  "success": true,
  "call_id": "contact_abc123xyz",
  "provider": "amazon-connect",
  "message": "Call initiated. Farmer will receive call in 30 seconds."
}
```

---

## Database Schema

### DynamoDB Table: welfare_schemes

**Key:** scheme_id (partition key)

**10 Schemes:**

| scheme_id | name_hi | min_land | requires_kcc | benefit |
|-----------|---------|----------|-------------|---------|
| PM_KISAN | प्रधानमंत्री किसान सम्मान निधि | 0 | false | ₹6,000/year |
| KCC | किसान क्रेडिट कार्ड | 0 | false | ₹3L loan @ 4% |
| PMFBY | प्रधानमंत्री फसल बीमा | 0 | false | Full crop value |
| MGNREGS | मनरेगा | 0 | false | ₹22,000/year (100 days) |
| AYUSHMAN_BHARAT | आयुष्मान भारत | 0 | false | ₹5L health insurance |
| SOIL_HEALTH_CARD | मिट्टी स्वास्थ्य कार्ड | 0 | false | Free soil testing |
| PM_AWAS_GRAMIN | प्रधानमंत्री आवास (ग्रामीण) | 0 | false | ₹1.2L house subsidy |
| NFSA_RATION | अन्नपूर्णा योजना | 0 | false | Subsidized food grain |
| ATAL_PENSION | अटल पेंशन योजना | 0 | false | ₹1,000-5,000/month |
| SUKANYA_SAMRIDDHI | सुकन्या समृद्धि योजना | 0 | false | Girls' education fund |

**Complete Schema:**
```python
{
  "scheme_id": "PM_KISAN",              # String (Partition Key)
  "name_en": "Pradhan Mantri Kisan...", # String
  "name_hi": "प्रधानमंत्री किसान...",      # String (Devanagari)
  "benefit": "₹6,000 per year",         # String (human-readable)
  "eligibility": "Small and marginal",  # String
  "apply_at": "Common Service Centre",  # String
  "documents": ["Aadhaar", ...],        # List of Strings
  "min_land_acres": 0,                  # Number
  "income_limit": 0,                    # Number (0 = no limit)
  "requires_kcc": false,                # Boolean
  "requires_bank_account": true,        # Boolean
  "created_at": "2024-01-01T00:00:00Z", # String (ISO 8601)
  "updated_at": "2024-01-01T00:00:00Z"  # String (ISO 8601)
}
```

**Query Examples:**

```python
# Get single scheme
table.get_item(Key={'scheme_id': 'PM_KISAN'})

# Scan all schemes
table.scan()

# Get schemes requiring bank account
import boto3
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.Table('welfare_schemes')
response = table.scan(FilterExpression='requires_bank_account = :val',
                      ExpressionAttributeValues={':val': True})
eligible_schemes = response['Items']
```

---

## S3 Structure & CORS

### Bucket: voicebridge-audio-yuga

**Region:** ap-southeast-1

**Folder Structure:**
```
voicebridge-audio-yuga/
├── voice_memory/                  [Farmer success story clips]
│   ├── voice_memory_PM_KISAN.mp3  [Suresh Kumar's story]
│   ├── voice_memory_KCC.mp3       [Ramaiah's story]
│   └── voice_memory_PMFBY.mp3     [Laxman Singh's story]
├── tts_output/                    [Polly TTS audio (auto-created)]
│   ├── audio_20240301_123456.mp3
│   └── ...
└── transcribe_input/              [STT temp files (auto-created)]
    ├── input_123456.wav
    └── ...
```

### CORS Configuration

**CRITICAL:** Required for browser to play S3 audio.

Set in AWS S3 Console → Bucket → Permissions → CORS:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": [
      "https://master.dk0lrulrclio3.amplifyapp.com",
      "http://localhost:3000"
    ],
    "ExposeHeaders": ["Content-Length"],
    "MaxAgeSeconds": 3000
  }
]
```

### Presigned URLs

**Expiration:** 900 seconds (15 minutes)

Generated by Lambda before returning to frontend:
```python
import boto3
s3 = boto3.client('s3', region_name='ap-southeast-1')
presigned_url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'voicebridge-audio-yuga', 'Key': 'voice_memory/voice_memory_PM_KISAN.mp3'},
    ExpiresIn=900
)
```

### Audio File Requirements

- **Format:** MP3
- **Codec:** MP3 (128 kbps)
- **Sample Rate:** 22050 Hz (minimum)
- **Duration:** 5-15 seconds
- **File Names:** MUST end in `.mp3` exactly (not `.mp3.mpeg` or `.mpeg`)
- **ContentType:** `audio/mpeg`

**Fixing Wrong Audio Extensions:**
```bash
cd voicebridge-backend
python utils/normalize_s3_audio.py         # dry run (shows what will change)
python utils/normalize_s3_audio.py --apply # apply fixes
```

This script:
1. Lists all S3 objects
2. Detects files with wrong extensions (.mp3.mpeg, .mpeg, .webm, etc.)
3. Copies to correct name with .mp3 extension
4. Sets ContentType to audio/mpeg
5. Deletes old file

---

## Conversation Flow

### 6-Stage Call Machine

React state machine with 7 states:

```
IDLE
  ↓
(User clicks "Start Conversation")
  ↓
CONNECTING
  ↓
SAHAYA_SPEAKING (plays opening message)
  ↓
WAITING (user can speak or type)
  ↓
RECORDING (capturing voice)
  ↓
TRANSCRIBING (processing audio)
  ↓
THINKING (Bedrock generating response)
  ↓
SAHAYA_SPEAKING (plays Polly response + voice memory)
  ↓
WAITING (repeat)
```

### Conversation History

Always passes full history in each request:

```javascript
conversationHistory = [
  { role: 'assistant', content: 'नमस्ते! मैं सहाया हूँ।' },
  { role: 'user', content: 'आप कौन हो?' },
  { role: 'assistant', content: 'मैं एक AI सहायक हूँ...' }
]

// Each new request includes FULL history:
await axios.post(API.chat, {
  message: new_user_message,
  farmer_profile: {...},
  conversation_history: conversationHistory  // ALL previous turns
})
```

### Voice Memory Auto-Play (Latest Feature)

**Sequence:**
1. Bedrock generates response mentioning farmer story
2. Frontend receives: `response_text`, `audio_url`, `voice_memory_clip`
3. Plays sequence:
   - Play Sahaya's Polly audio → wait for finish
   - 0.8s pause
   - Play voice memory clip → wait for finish
   - 0.5s pause
   - Auto-resume listening (if conversation mode)

**Code:**
```javascript
const playSequentially = async (sahayaAudioUrl, voiceMemoryUrl, onComplete) => {
  // Step 1: Play Sahaya
  if (sahayaAudioUrl) {
    await new Promise((resolve) => {
      const audio = new Audio(sahayaAudioUrl)
      audio.crossOrigin = 'anonymous'
      audio.onended = resolve
      audio.onerror = resolve
      audio.play().catch(resolve)
    })
  }
  
  // Step 2: Pause
  await new Promise(resolve => setTimeout(resolve, 800))
  
  // Step 3: Play voice memory
  if (voiceMemoryUrl) {
    await new Promise((resolve) => {
      const vmAudio = new Audio(voiceMemoryUrl)
      vmAudio.crossOrigin = 'anonymous'
      vmAudio.onended = resolve
      vmAudio.onerror = resolve
      vmAudio.play().catch(resolve)
    })
  }
  
  // Step 4: Resume listening
  await new Promise(resolve => setTimeout(resolve, 500))
  if (onComplete) onComplete()
}
```

---

## Voice Memory Clips

Real farmer success stories. Audio files hosted on S3.

### PM_KISAN (Pradhan Mantri Kisan Samman Nidhi)

**Farmer:** Suresh Kumar  
**Location:** Tumkur, Karnataka  
**Story:** "Suresh Kumar ne PM-KISAN se ₹6,000 haasil kiye aur apne bacchon ki school fees bhari."  
**Quote:** "PM-KISAN se ₹6,000 mile. Bacchon ki fees bhari. Sahaya ne bataya tha!"  
**Audio File:** voice_memory_PM_KISAN.mp3  

### KCC (Kisan Credit Card)

**Farmer:** Ramaiah  
**Location:** Mysuru, Karnataka  
**Story:** "Ramaiah ko KCC se sirf 4% byaaj par ₹3 lakh ka loan mila aur sahukaar ka chakkar band hua."  
**Quote:** "KCC se 4% pe loan mila. Sahukaar se hamesha ke liye chhutkaara!"  
**Audio File:** voice_memory_KCC.mp3  

### PMFBY (Pradhan Mantri Fasal Bima Yojana)

**Farmer:** Laxman Singh  
**Location:** Dharwad, Karnataka  
**Story:** "Laxman Singh ki fasal barbaad hui lekin PMFBY se ₹18,000 mile aur parivar bachaa."  
**Quote:** "Fasal barbaad hui par PMFBY se ₹18,000 mile. Parivar bachaa!"  
**Audio File:** voice_memory_PMFBY.mp3  

### How They're Used

1. **Bedrock Prompt Injection:** When recommending a scheme, Bedrock's system prompt includes farmer story context
2. **Natural Introduction:** Sahaya naturally mentions the farmer's story in her response
3. **Audio Tag:** Response includes `[PLAY_VOICE_MEMORY:SCHEME_ID]` tag
4. **Frontend Extract:** Frontend parses tag, fetches presigned URL, auto-plays
5. **Visual Indicator:** Amber card shows "▶ Playing" badge during playback

---

## Farmer Profiles

### Demo Farmer (Built-in)

```javascript
{
  name: 'Ramesh Kumar',
  phone: '+919876543210',
  land_acres: 2,
  state: 'Karnataka',
  age: 45,
  has_kcc: false,
  has_bank_account: true,
  annual_income: 50000
}
```

Uses this to test eligibility matching and conversation flow.

### Farmer Model (Python)

```python
class FarmerProfile:
    name: str                    # Farmer's name
    phone: str                   # Phone number (+91...)
    land_acres: float            # Acres (0.5, 1.5, 2, etc.)
    state: str                   # State name (Karnataka, Maharashtra, etc.)
    age: int                      # Age (18-80)
    has_kcc: bool                # Has Kisan Credit Card?
    has_bank_account: bool       # Has bank account?
    annual_income: float         # Annual income (rupees)
    
    def is_valid(self) -> bool:
        """Validates farmer profile completeness."""
        return (
            self.name and len(self.name) > 0 and
            self.phone and self.phone.startswith('+91') and
            self.land_acres >= 0 and
            self.state and
            self.age >= 18
        )
```

---

## Running Locally

### Terminal 1: Backend

```bash
cd voicebridge-backend
python -m venv .venv
source .venv/bin/activate  # on macOS/Linux
# or .\.venv\Scripts\Activate.ps1  (Windows)

pip install -r requirements.txt
python app.py
# Server at http://localhost:5000
```

### Terminal 2: Frontend

```bash
cd frontend
npm install
npm start
# Browser at http://localhost:3000
```

### Terminal 3: Test Backend (Optional)

```bash
cd voicebridge-backend
python -m pytest tests/ -v
```

### Testing Endpoints (cURL)

```bash
# Health
curl http://localhost:5000/api/health

# Schemes
curl http://localhost:5000/api/schemes

# Eligibility check
curl -X POST http://localhost:5000/api/eligibility-check \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_profile": {
      "name": "Ramesh Kumar",
      "phone": "+919876543210",
      "land_acres": 2,
      "state": "Karnataka",
      "age": 45,
      "has_kcc": false,
      "has_bank_account": true,
      "annual_income": 50000
    }
  }'

# Chat
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "पीएम किसान के बारे में बताओ",
    "farmer_profile": {...},
    "conversation_history": [
      {"role": "assistant", "content": "नमस्ते"}
    ]
  }'
```

---

## Deployment

### Frontend Deployment (Amplify)

**Automatic on Push:**
```bash
git add -A
git commit -m "Update frontend"
git push origin master
```

Amplify automatically:
1. Pulls latest code
2. Runs `npm run build`
3. Deploys to CloudFront
4. Available at https://master.dk0lrulrclio3.amplifyapp.com

**Manual Build:**
```bash
cd frontend
npm run build
# Creates optimized build/ folder
```

### Backend Deployment (Lambda + Zappa)

**First Time Setup:**
```bash
cd voicebridge-backend
pip install zappa
zappa init dev
# Follow prompts, creates zappa_settings.json
```

**Update Existing:**
```bash
zappa update dev
```

**View Logs:**
```bash
zappa tail dev
```

**Rollback:**
```bash
zappa rollback dev 1  # go back 1 version
```

**Undeploy:**
```bash
zappa undeploy dev  # WARNING: deletes Lambda function
```

---

## Known Issues & Fixes

### Issue 1: Scheme Names Showing Blank

**Symptom:** 10 grey bars instead of scheme names

**Root Cause:** `eligibilityCheck` returns FULL OBJECTS, not just IDs. Code tried to use objects as scheme_id.

**Fix:** Extract IDs before setting state:
```javascript
const res = await axios.post(API.eligibilityCheck, { farmer_profile })
// WRONG: setEligibleSchemes(res.data.eligible_schemes)
// RIGHT:
const ids = res.data.eligible_schemes.map(s => s.scheme_id)
setEligibleSchemes(ids)
```

### Issue 2: Voice Memory Audio Shows 0:00/0:00

**Symptom:** Audio player visible but shows no duration

**Root Causes:**
1. CORS not enabled on S3 bucket
2. Audio files have wrong extensions (`.mp3.mpeg` instead of `.mp3`)
3. Elements missing `crossOrigin="anonymous"`

**Fix:**
```javascript
// 1. Add CORS to audio elements:
<audio crossOrigin="anonymous" preload="metadata">

// 2. Set CORS policy on S3 bucket (see S3 CORS section)

// 3. Fix audio file extensions:
cd voicebridge-backend
python utils/normalize_s3_audio.py --apply
```

### Issue 3: Transcribe Service Times Out

**Symptom:** "TimeoutException during speech-to-text"

**Root Cause:** Code adds `VocabularyName='voicebridge-vocab'` but vocabulary doesn't exist

**Fix:** Remove VocabularyName parameter:
```python
# WRONG:
client.start_transcription_job(
    TranscriptionJobName=job_name,
    VocabularyName='voicebridge-vocab',  # ❌ DELETE THIS LINE
    ...
)

# RIGHT:
client.start_transcription_job(
    TranscriptionJobName=job_name,
    ...
)
```

### Issue 4: API URL Hitting Amplify Instead of Lambda

**Symptom:** API calls fail with CORS error from Amplify domain

**Root Cause:** Code uses relative `/api/...` URLs which resolve to Amplify hosting server

**Fix:** Use `API.*` constants everywhere:
```javascript
// WRONG:
const res = await axios.post('/api/chat', { ... })

// RIGHT:
import API from './config/api'
const res = await axios.post(API.chat, { ... })
```

### Issue 5: Conversation History Breaks Multi-turn

**Symptom:** Bedrock doesn't remember previous context

**Root Cause:** `conversation_history` not passed to `/api/chat`

**Fix:** Always pass full history:
```javascript
const historyToSend = [
  ...conversationHistory,
  { role: 'user', content: userMessage }
]
await axios.post(API.chat, {
  message: userMessage,
  farmer_profile: farmer,
  conversation_history: historyToSend  // ✓ ALWAYS include
})
```

### Issue 6: Microphone Permission Denied

**Symptom:** "Microphone permission denied" error on browser

**Fix:**
1. Click mic icon in address bar → "Allow"
2. Reload page
3. Try again

### Issue 7: AWS Credentials Not Found

**Symptom:** "Unable to locate credentials" when running locally

**Fix:**
```bash
aws configure
# Enter Access Key, Secret Key, region: ap-southeast-1

# OR set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=ap-southeast-1
```

### Issue 8: S3 Bucket Not Found

**Symptom:** "NoSuchBucket" error

**Fix:** Check bucket exists and is in correct region:
```bash
# List buckets:
aws s3 ls

# Create bucket if missing:
aws s3 mb s3://voicebridge-audio-yuga --region ap-southeast-1
```

### Issue 9: DynamoDB Table Not Found

**Symptom:** "ResourceNotFoundException" when fetching schemes

**Fix:** Create table:
```bash
# Via AWS Console: DynamoDB → Create table
# Table name: welfare_schemes
# Partition key: scheme_id (String)
# Billing: Pay-per-request

# OR via boto3:
import boto3
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.create_table(
    TableName='welfare_schemes',
    KeySchema=[{'AttributeName': 'scheme_id', 'KeyType': 'HASH'}],
    AttributeDefinitions=[{'AttributeName': 'scheme_id', 'AttributeType': 'S'}],
    BillingMode='PAY_PER_REQUEST'
)
```

### Issue 10: Zappa Deployment Fails

**Symptom:** "Unable to create Lambda role" or "S3 bucket not found during deployment"

**Fix:**
```bash
# Ensure role has permissions:
aws iam attach-role-policy \
  --role-name zappa-dev-role \
  --policy-arn arn:aws:iam::aws:policy/AWSLambdaFullAccess

# Ensure S3 bucket exists for Zappa:
aws s3 mb s3://zappa-deployments-yuga --region ap-southeast-1

# Try update again:
zappa update dev
```

### Issue 11: Sarvam API Returns 400 Bad Request (v1.3.2 FIX)

**Symptom:** `/api/sarvam-tts` returns `{"error": "Items in 'inputs' cannot be empty..."}`

**Root Cause:** Incorrect API payload format. Old format used `'text': text` but Sarvam v2 requires `'inputs': [text]` array format.

**Fix Applied (v1.3.2b - Feb 28, 2026):**
```python
# WRONG (v1.3.2):
payload = {
    'text': text,
    'target_language_code': language,
    'speaker': speaker_id,
    ...
}

# CORRECT (v1.3.2b):
payload = {
    'inputs': [text],  # Array format required
    'target_language_code': language,
    'speaker': speaker_id,
    'model': 'bulbul:v2',  # Explicit model
    'pace': 0.75,
    'pitch': 0,
    'loudness': 1.5,
    'enable_preprocessing': True
}
```

**Status:** ✅ FIXED. Deployed to Lambda Feb 28, 2026.

### Issue 12: Sarvam Speaker Compatibility (v1.3.2b FIX)

**Symptom:** Sarvam returns 400 with "Speaker 'X' is not compatible with model bulbul:v2"

**Root Cause:** Initial speakers (pavithra, priya, shreya, arjun, ritu, kavya) were designed for bulbul v3, not v2.

**Original Testing Results:**
- pavithra: ✗ Incompatible
- priya: ✗ Incompatible
- shreya: ✗ Incompatible
- arjun: ✗ Incompatible
- ritu: ✗ Incompatible
- kavya: ✗ Incompatible
- manisha: ✓ Works (tested with Telugu)
- anushka: ✓ Works (universal)

**Fix Applied (v1.3.2b - Feb 28, 2026):**
```python
# Updated speaker_map to use compatible speakers:
speaker_map = {
    'ta-IN': 'anushka',   # Tamil → anushka
    'kn-IN': 'anushka',   # Kannada → anushka
    'te-IN': 'anushka',   # Telugu → anushka
    'ml-IN': 'manisha',   # Malayalam → manisha (tested)
    'hi-IN': 'anushka'    # Hindi → anushka
}
```

**Status:** ✅ FIXED and TESTED. All 5 languages verified Feb 28, 2026.

### Issue 13: Speech Pace Too Fast for Farmers (v1.3.2b FIX)

**Symptom:** Sarvam audio plays at pace 0.9, too fast for farmers to understand

**Fix Applied (Feb 28, 2026):**
```python
# Changed from:
'pace': 0.9,

# Changed to:
'pace': 0.75,  # 25% slower for clarity
```

**Status:** ✅ FIXED. Live in production.

### Issue 14: Voice Memory Clips Playing for Non-Hindi Languages (v1.3.2b FIX)

**Symptom:** Malayalam, Tamil, Kannada, Telugu users hear Hindi voice memory clips (confusing)

**Root Cause:** `/api/chat` was sending `voice_memory_clip` for all languages, but clips are only available in Hindi

**Fix Applied (v1.3.2b - Feb 28, 2026):**
```python
# In /api/chat route:
# Only send voice_memory_clip for Hindi
language = data.get('language', 'hi-IN')
send_voice_clip = final_voice_clip if language == 'hi-IN' else None

return jsonify({
    'success': True,
    'response_text': response_text,
    'matched_schemes': matched_schemes,
    'voice_memory_clip': send_voice_clip,  # None for non-Hindi
    'audio_url': tts_audio_url,
    'conversation_id': uuid.uuid4().hex
})
```

**Test Results (Feb 28, 2026):**
- Malayalam chat: `voice_memory_clip = None` ✓
- Hindi chat: `voice_memory_clip = "PM_KISAN"` ✓

**Status:** ✅ FIXED and VERIFIED.

---

## Recent Updates (v1.3.2b - February 28, 2026)

### Rule 1: Never Use Relative URLs

❌ **WRONG:**
```javascript
const res = await axios.post('/api/chat', { ... })
```

✅ **CORRECT:**
```javascript
import API from './config/api'
const res = await axios.post(API.chat, { ... })
```

### Rule 2: Never Add VocabularyName to Transcribe

❌ **WRONG:**
```python
client.start_transcription_job(
    TranscriptionJobName=job_name,
    VocabularyName='voicebridge-vocab',  # THIS VOCABULARY DOESN'T EXIST
    ...
)
```

✅ **CORRECT:**
```python
client.start_transcription_job(
    TranscriptionJobName=job_name,
    ...
)
```

### Rule 3: Never Call Anthropic API from Frontend

❌ **WRONG:**
```javascript
const res = await axios.post('https://api.anthropic.com/v1/messages', { ... })
```

✅ **CORRECT:**
All AI calls go through Lambda:
```javascript
const res = await axios.post(API.chat, { ... })
```

### Rule 4: Never Hardcode API Keys in Frontend

❌ **WRONG:** `const API_KEY = 'sk-12345'` (bad!)

✅ **CORRECT:** Use Lambda to proxy all requests

### Rule 5: Always Pass Full conversation_history

❌ **WRONG:**
```javascript
await axios.post(API.chat, {
  message: userMessage,
  farmer_profile: farmer
  // missing: conversation_history
})
```

✅ **CORRECT:**
```javascript
await axios.post(API.chat, {
  message: userMessage,
  farmer_profile: farmer,
  conversation_history: [
    { role: 'assistant', content: '...' },
    { role: 'user', content: '...' }
  ]
})
```

### Rule 6: Always Use crossOrigin="anonymous" on Audio

❌ **WRONG:**
```javascript
<audio src={url} controls />
```

✅ **CORRECT:**
```javascript
<audio src={url} controls crossOrigin="anonymous" preload="metadata" />
```

### Rule 7: S3 Audio Files Must Be .mp3 Exactly

❌ **WRONG:** `voice_memory_PM_KISAN.mp3.mpeg`

✅ **CORRECT:** `voice_memory_PM_KISAN.mp3`

Fix with:
```bash
python utils/normalize_s3_audio.py --apply
```

### Rule 8: eligibilityCheck Returns Objects, Extract IDs

❌ **WRONG:**
```javascript
const schemes = res.data.eligible_schemes
// schemes[0] = {scheme_id: 'PM_KISAN', name_hi: '...', ...}
setEligibleSchemes(schemes)  // Wrong! This is an object, not an ID
```

✅ **CORRECT:**
```javascript
const schemeIds = res.data.eligible_schemes.map(s => s.scheme_id)
// schemeIds = ['PM_KISAN', 'KCC', ...]
setEligibleSchemes(schemeIds)
```

### Rule 9: Sahaya Always Speaks First

Never wait for user to initiate. Sahaya's opening message plays automatically when conversation starts.

### Rule 10: Use Web Speech API for Micophone

❌ **WRONG:** Make batch Transcribe requests (timeout)

```javascript
// This times out:
await axios.post('/api/speech-to-text', formData)
```

✅ **CORRECT:** Use browser's Web Speech API (real-time):

```javascript
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)()
recognition.lang = 'hi-IN'
recognition.onresult = (e) => {
  const transcript = e.results[0][0].transcript
  sendMessage(transcript)
}
recognition.start()
```

---

## Troubleshooting

### Frontend Troubleshooting

**Q: "Cannot find module 'axios'"**
```bash
npm install
```

**Q: "REACT_APP_API_URL is undefined"**
Check `.env` or `.env.development`:
```
REACT_APP_API_URL=https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev
```

**Q: Audio player shows but doesn't load**
1. Check S3 CORS policy
2. Verify `crossOrigin="anonymous"` on audio element
3. Check S3 file extension is `.mp3` (not `.mp3.mpeg`)

**Q: Microphone not working**
1. Check browser permissions (address bar mic icon)
2. Check browser is Chrome, Edge, or Safari (Firefox has limited support)
3. Reload page

**Q: Schemes list empty**
1. Check `/api/schemes` returns data: `curl http://localhost:5000/api/schemes`
2. Check DynamoDB table exists and has data
3. Check AWS credentials configured

### Backend Troubleshooting

**Q: "ModuleNotFoundError: No module named 'boto3'"**
```bash
pip install -r requirements.txt
```

**Q: "Unable to locate credentials"**
```bash
aws configure
# OR:
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
```

**Q: "Table welfare_schemes not found"**
Create table in DynamoDB console or:
```bash
aws dynamodb create-table \
  --table-name welfare_schemes \
  --attribute-definitions AttributeName=scheme_id,AttributeType=S \
  --key-schema AttributeName=scheme_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-southeast-1
```

**Q: "NoSuchBucket" error**
```bash
aws s3 mb s3://voicebridge-audio-yuga --region ap-southeast-1
```

**Q: "Bedrock quota exceeded"**
Wait 1 hour or request quota increase in AWS Console.

**Q: Transcribe returns empty**
Check language is `hi-IN` and don't add `VocabularyName`.

**Q: Polly audio is robotic/unnatural**
Using neural voice (Kajal)? If not:
```python
# Use neural voice:
client.synthesize_speech(
    Text='नमस्ते',
    OutputFormat='mp3',
    VoiceId='Kajal',  # Neural voice
    Engine='neural'   # Add this!
)
```

### Deployment Troubleshooting

**Q: Amplify build fails**
Check `package.json` and errors in Amplify Console → Build logs.

**Q: Zappa deployment fails**
```bash
# Check IAM role has Lambda permissions:
aws iam attach-role-policy \
  --role-name zappa-dev-role \
  --policy-arn arn:aws:iam::aws:policy/AWSLambdaFullAccess

# Check S3 bucket for Zappa exists:
aws s3 ls s3://zappa-deployments-yuga

# Try update again:
zappa update dev
```

**Q: Lambda timeout**
Increase timeout in `zappa_settings.json`:
```json
{
  "dev": {
    "timeout": 60,    // was 30, now 60 seconds
    ...
  }
}
```

---

## Quick Reference

### Environment Setup Checklist (New Laptop)

Frontend:
- [ ] Clone repo: `git clone https://github.com/yuga-i2/VoiceBridge_AI.git`
- [ ] Enter dir: `cd VoiceBridge_AI/frontend`
- [ ] Install: `npm install`
- [ ] Create `.env.development`: `REACT_APP_API_URL=http://localhost:5000`
- [ ] Run: `npm start` → http://localhost:3000

Backend:
- [ ] Enter dir: `cd ../voicebridge-backend`
- [ ] Create venv: `python -m venv .venv` + `.\.venv\Scripts\Activate.ps1`
- [ ] Install: `pip install -r requirements.txt`
- [ ] Configure: `aws configure` (access key, secret, region: ap-southeast-1)
- [ ] Create `.env` (copy from `.env.example`)
- [ ] Run: `python app.py` → http://localhost:5000

### API Endpoints Quick List

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Status check |
| GET | `/api/schemes` | List all schemes |
| POST | `/api/eligibility-check` | Check farmer eligibility |
| POST | `/api/chat` | Main conversation (Bedrock) |
| GET | `/api/voice-memory/{id}` | Get farmer story audio |
| POST | `/api/text-to-speech` | Generate Polly audio (Hindi) |
| POST | `/api/sarvam-tts` | Generate Sarvam audio (5 languages) |
| POST | `/api/speech-to-text` | Transcribe voice |
| POST | `/api/initiate-call` | Outbound call |

### CLI Commands Quick List

```bash
# Frontend
npm install               # Install dependencies
npm start                 # Dev server (localhost:3000)
npm run build             # Production build
npm test                  # Run tests

# Backend
pip install -r requirements.txt   # Install Python deps
python app.py                     # Dev server (localhost:5000)
pytest tests/ -v                  # Run tests
zappa update dev                  # Deploy to Lambda

# S3 Audio
python utils/normalize_s3_audio.py         # Check (dry-run)
python utils/normalize_s3_audio.py --apply # Fix extensions

# AWS
aws configure                     # Set credentials
aws s3 ls                         # List buckets
aws dynamodb scan                 # Query DynamoDB
zappa tail dev                    # View Lambda logs
```

---

## Support & Links

- **GitHub:** https://github.com/yuga-i2/VoiceBridge_AI
- **Frontend:** https://master.dk0lrulrclio3.amplifyapp.com
- **Backend:** https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev
- **AWS Region:** ap-southeast-1 (Singapore)
- **Deadline:** March 3, 2026

---

**Last Updated:** February 28, 2026 (22:45 IST)  
**Version:** 1.3.2b (Sarvam AI Regional Language TTS + Fixes)  
**Status:** ✅ Production Ready — Full regional language support verified & live

---

## Recent Implementation Details (v1.3.2b)

### Sarvam AI TTS - Regional Language Support

**What Was Implemented:**
Complete regional language support for 5 Indian languages using Sarvam AI Bulbul v2.

**Critical Bug Fixes:**

1. **Payload Format Issue (CRITICAL)**
   - Original: `'text': text`
   - Fixed to: `'inputs': [text]` (array required by Sarvam v2)
   - Sarvam Error Message: "Items in 'inputs' cannot be empty. Needs to contain strings..."
   - Status: ✅ Fixed and verified

2. **Speaker Compatibility Issue (CRITICAL)**
   - Tested speakers: pavithra, priya, shreya, arjun, ritu, kavya
   - Result: All returned 400 "Speaker not compatible with bulbul:v2"
   - Solution: Switched to anushka (all languages), manisha (Malayalam)
   - Test Result: Telugu + manisha = HTTP 200 OK, 37.6KB base64 audio ✓

3. **Speech Pace Optimization**
   - Before: 0.9 (too fast for farmers)
   - After: 0.75 (25% slower, clearer)
   - Impact: Better comprehension for non-native Hindi speakers

4. **Voice Memory Clip Language Filtering**
   - Before: Sent Hindi clips to all languages
   - After: Only send for Hindi (language == 'hi-IN')
   - Test: ML=None, HI=PM_KISAN ✓

**Testing Timeline:**
- Feb 26: Initial Sarvam endpoint (v1.3.0)
- Feb 27: Language normalization + response parsing (v1.3.2)
- Feb 28: Payload format fix + speaker optimization + language filtering (v1.3.2b) ✅

**Production Deployment:**
- Command: `zappa update dev` (with AWS credentials)
- Package: 20.1 MiB
- Status: Live at https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev
- Verified: All 5 languages producing audio

---

**Last Updated:** February 28, 2026 (22:45 IST)  
**Version:** 1.3.2b (Sarvam AI Regional Language TTS)  
**Status:** ✅ Production Ready — All 5 languages verified & live
