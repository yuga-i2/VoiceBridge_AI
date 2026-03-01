# VoiceBridge AI — Development Constraints

## Purpose of This Document
This document defines hard rules that every line of code in this project must follow. These constraints exist to keep the project aligned with its original vision, prevent scope creep, and ensure the prototype can be completed within the 7-day hackathon deadline.

If a suggestion, feature, or implementation contradicts anything in this document, reject it.

## Hard Constraints — Never Violate

### Accuracy Constraint
Welfare scheme benefit amounts are verified from official government sources.
Never change these numbers without checking the official website:
- PM-KISAN: ₹6,000/year (₹2,000 × 3 installments)
- KCC: Up to ₹3 lakh at 4% interest
- PMFBY: 2% premium Kharif, 1.5% Rabi
- Ayushman Bharat: ₹5 lakh per family per year
- MGNREGS: 100 days, ₹220-357/day depending on state
Wrong amounts in the demo = immediate credibility failure with judges.

### Privacy Constraint
The system must never store, log, or transmit:
- Aadhaar numbers
- OTP codes
- Bank account numbers
- Passwords or PINs
If any code attempts to collect these, it is a bug, not a feature.

### Scope Constraint — What NOT to Build in Prototype
Do not build any of the following (production features, not prototype scope):
- Real USSD integration (*123*CHECK# is a UI label only)
- 20-language support (Hindi only for prototype)
- Real-time AI on live phone calls (pre-scripted Connect flow only)
- ElastiCache Redis
- Amazon Neptune
- Amazon OpenSearch
- Amazon RDS PostgreSQL
- Amazon EC2
- Real farmer phone number discovery engine
- Actual DPDP compliance audit (mention architecture, don't build full system)

### AWS Region Constraint
All AWS services: ap-southeast-1 (Singapore) only.
Never use ap-south-1 (Mumbai) — Indian phone numbers take weeks.
Never mix regions — latency and permission issues will break the demo.

### Code Quality Constraints
- Every service file must have USE_MOCK check at the top
- Mock responses must be realistic Hindi text, not placeholder strings
- No hardcoded AWS credentials anywhere in code (use .env only)
- Every API endpoint must return consistent JSON structure always
- Every endpoint must handle errors and return meaningful error messages
- No print statements in production paths (use proper logging)

### File and Folder Constraints
- No phase names in any file or folder name
- No temporary or experimental files committed to the repo
- No extra markdown files beyond the three in docs/
- No README.md until final submission day
- All audio files in data/voice_memory/ only
- All configuration via .env and config/settings.py only
- No inline configuration in service files

### Demo Constraints — The Demo Must Show
1. A real Hindi voice conversation (speech in → speech out)
2. The Voice Memory Network clip playing in context
3. Accurate scheme data with correct rupee amounts
4. A live URL that works when judges click it
5. An outbound call demo (recorded video of phone receiving call)
These five things are non-negotiable for a competitive submission.

## Tech Stack — Exactly This, Nothing Else

Backend:
- Python 3.12
- Flask (web framework)
- flask-cors (cross-origin requests from frontend)
- boto3 (AWS SDK)
- python-dotenv (environment variables)

AWS Services (8 only):
- Amazon Bedrock (Claude 3 Haiku) — AI reasoning
- Amazon Transcribe — Hindi speech to text
- Amazon Polly (Kajal neural) — Hindi text to speech
- Amazon DynamoDB — welfare schemes database
- Amazon S3 — audio file storage
- Amazon Connect — outbound phone calls
- Amazon SNS — SMS delivery
- AWS Lambda — serverless deployment target

Frontend (separate repository):
- React (Vite)
- AWS Amplify (deployment)

Do not add any package, service, or tool not listed above without explicit justification against the project goals.

## The Definition of Done for This Project
The project is complete when ALL of the following are true:
1. GET /api/health returns 200 OK
2. POST /api/chat returns accurate Hindi scheme advice
3. POST /api/speech-to-text accepts audio and returns Hindi text
4. POST /api/text-to-speech returns playable audio URL
5. GET /api/voice-memory/PMFBY returns playable audio URL
6. POST /api/eligibility-check returns correct scheme matches for Ramesh (2 acres, Karnataka, no KCC) — must include PM_KISAN, PMFBY, MGNREGS
7. POST /api/send-sms logs correct document list to console (mock) or sends real SMS (AWS)
8. All 7 tests above pass with USE_MOCK=True
9. All 7 tests above pass with USE_MOCK=False (AWS connected)
10. Live URL works on mobile browser
11. Demo video is recorded showing all 5 demo requirements above
