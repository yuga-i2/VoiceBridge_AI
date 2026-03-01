# VoiceBridge AI — Project Reference

## What This Product Is
Community Voice Bridge is a proactive AI system that calls rural Indian farmers on basic 2G feature phones (₹500 Nokia phones), speaks in Hindi, identifies which government welfare schemes they qualify for, builds trust using real peer success audio stories, and guides them from discovery to benefit delivery through persistent follow-up calls over 14 days.

The AI reaches OUT to farmers. Farmers do not visit any website or app. The web portal exists only for judge demos and public inquiries.

## The Core Problem Being Solved
135 million Indian farmers cannot access welfare schemes they are legally entitled to (PM-KISAN, KCC, PMFBY, Ayushman Bharat, MGNREGS) because:
- Web portals assume digital literacy (30% are illiterate → 95% dropout)
- Mobile apps assume smartphones (only 42% penetration → excludes 58%)
- Call centres are reactive (farmer must call → 5% completion rate)
- Field officers cost ₹2,700 per farmer → reaches only 200,000/year

## The Three Core Innovations (Never Compromise These)
1. PROACTIVE OUTREACH: The system calls the farmer. Not the other way around. Amazon Connect initiates outbound calls to farmer phone numbers.
2. VOICE MEMORY NETWORK: When discussing a scheme, the AI plays a 30-second real peer success story audio clip from the farmer's district. Peer trust beats official messaging. This is the single biggest differentiator.
3. 2G FEATURE PHONE COMPATIBLE: Works on any phone that can receive calls. No internet. No app. No data plan. No digital literacy required.

## The 6-Stage Farmer Journey
Stage 1 — DISCOVERY: System identifies eligible farmers from phone number database. No personal data collected at this stage.
Stage 2 — TRUST BUILDING: Outbound call with verified caller ID. Sahaya introduces herself, plays peer success story, explains she will never ask for OTP or Aadhaar.
Stage 3 — ELIGIBILITY CONFIRMATION: AI asks simple questions (land size, state, KCC status). Matches farmer to eligible schemes.
Stage 4 — DOCUMENT COLLECTION: SMS sent with visual document checklist. AI available for questions.
Stage 5 — APPLICATION SUPPORT: AI guides through application process. Persistent follow-up if farmer gets stuck.
Stage 6 — BENEFIT DELIVERY: Final call confirms benefit received. Success story recorded with consent. Farmer becomes advocate.

## The AI Persona
Name: Sahaya
Language: 
  - Primary response: Hindi (Devanagari script) — AI always responds in Hindi regardless of input
  - Input languages supported: Hindi (hi-IN), Malayalam (ml-IN), Tamil (ta-IN), Kannada (experimental)
  - Voice memory clips: Available in Hindi (farmer stories translated/localized for regional context)
Personality: Warm, patient, encouraging, trustworthy
Hard rules Sahaya NEVER breaks:
- Never asks for Aadhaar number
- Never asks for OTP
- Never asks for bank account details or passwords
- Always offers verification code (*123*CHECK#) when farmer is suspicious
- Always explains data collection in simple Hindi before collecting anything
- Must include farmer success story reference [PLAY_VOICE_MEMORY:scheme_id] when recommending schemes

## Backend Architecture
The backend is a Flask REST API with a mock/live toggle system deployed on AWS Lambda.
USE_MOCK=True → all services return realistic local data (no AWS needed)
USE_MOCK=False → all services call real AWS services via boto3

Services:
- scheme_service: matches farmer profile + message to welfare schemes (language-aware keyword detection)
- ai_service: sends scheme context + conversation to Bedrock Claude 3 Haiku, returns Hindi response with [PLAY_VOICE_MEMORY:scheme_id] tags
- stt_service: converts speech to text via Amazon Transcribe (supports hi-IN, ml-IN, ta-IN)
- tts_service: converts text to audio via Amazon Polly (Kajal neural voice for Hindi, fallback Sarvam AI for regional)
- voice_memory_service: serves correct peer success story audio clip by scheme ID and language (S3 + DynamoDB)
- sms_service: sends document checklist SMS via Amazon SNS

All services follow the same pattern:
  if USE_MOCK: return realistic mock data
  else: call real AWS service via boto3

## Audio Strategy (Current Implementation)
1. Backend ALWAYS generates Polly TTS for response text (Hindi)
   - Returns: audio_url (S3 presigned URL), audio_type: 'tts'
2. Backend ALSO extracts voice_memory_clip parameter (e.g., "KCC")
   - Frontend fetches actual audio separately via /api/voice-memory/<scheme_id>?language=ml-IN
3. Frontend plays audio sequentially:
   - Hindi: Polly TTS → 1s pause → voice memory clip → 600ms pause → resume listening
   - Regional (Malayalam/Tamil): Sarvam AI TTS → 800ms pause → voice memory clip → 500ms pause → resume listening
   - Fallback: Browser SpeechSynthesis API if Sarvam unavailable

This separation ensures:
- TTS always plays (backend responsibility)
- Voice memory clip is optional and language-aware (frontend responsibility)
- No hardcoded delays or assumption about clip availability

## API Endpoints Summary
POST /api/chat — main conversation endpoint (accepts language parameter, returns audio_url + voice_memory_clip)
POST /api/speech-to-text — audio to text (language-aware)
POST /api/text-to-speech — text to audio URL (Hindi output, supports language in request)
GET  /api/voice-memory/<scheme_id> — get peer success story clip by scheme and language
POST /api/eligibility-check — check which schemes farmer qualifies for
POST /api/send-sms — send document checklist SMS
GET  /api/schemes — get all 10 schemes with multilingual names
GET  /api/health — health check with mode status

## The 10 Welfare Schemes (Accurate Data Only)
1. PM-KISAN: ₹6,000/year in three installments of ₹2,000
2. KCC (Kisan Credit Card): Crop loan up to ₹3 lakh at 4% interest
3. PMFBY (Crop Insurance): 2% premium Kharif, 1.5% Rabi, govt pays rest
4. Ayushman Bharat PM-JAY: ₹5 lakh/family/year health insurance
5. MGNREGS: 100 days guaranteed employment, ₹220-357/day by state
6. Soil Health Card: Free soil testing and crop recommendation
7. PM Awas Yojana Gramin: Housing subsidy ₹1.2-1.3 lakh for rural BPL
8. National Food Security Act: Subsidised grain ₹1-3/kg
9. Atal Pension Yojana: Pension ₹1,000-5,000/month after age 60
10. Sukanya Samriddhi Yojana: 8.2% interest savings for girl child

CRITICAL: These rupee amounts are verified. Never change them without checking the official government website. Wrong amounts = failed demo.

## Cost Model (For Demo and README)
Prototype cost: ~$12-15 USD total using $100 AWS credits
Per user cost in production: ₹15-25 per successful user
Field officer comparison: ₹2,700 per farmer → we are 180x cheaper
ROI: 10:1 to 17:1 on welfare delivered

## Privacy Architecture
- DPDP Act 2023 compliant
- Zero Aadhaar storage (sent directly to government portal)
- Auto-delete after 90 days
- User can delete data via USSD *123*PRIVACY# (production feature)
- Anti-scam verification: *123*CHECK# (production feature)
