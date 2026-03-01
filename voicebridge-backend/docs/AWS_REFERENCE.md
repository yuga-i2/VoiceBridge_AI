# VoiceBridge AI — AWS Services Reference

## AWS Region
All services must be in: ap-southeast-1 (Asia Pacific — Singapore)
This is non-negotiable. Indian phone numbers take weeks to provision.
Singapore region is used for all prototype development.

## AWS Services Used (8 Total)

### 1. Amazon Bedrock — The AI Brain
Model: Claude 3 Haiku (model ID: anthropic.claude-3-haiku-20240307-v1:0)
Why Haiku not Sonnet: 12x cheaper, same quality for scheme matching
Cost: ~$0.00025 per 1K input tokens, ~$0.00125 per 1K output tokens
Prototype cost: ~$0.20 for 500 test conversations
boto3 client: bedrock-runtime
Key method: invoke_model()
Input format: messages array with system prompt + conversation history
The system prompt defines Sahaya's persona and injects scheme data

### 2. Amazon Transcribe — Speech to Text (Multilingual)
Language codes: hi-IN (Hindi), ml-IN (Malayalam), ta-IN (Tamil)
Custom vocabulary name: voicebridge-vocab
(Add: PM-KISAN, PMFBY, KCC, MGNREGA, Ayushman, Aadhaar, Khatauni)
Cost: $0.024/minute after 60-min free tier
Prototype cost: ~$4 for 200 minutes of testing
boto3 client: transcribe
Flow: upload audio to S3 → start_transcription_job → poll for completion → get transcript from result URL
Note: Transcribe API is backend-only. Frontend uses browser Web Speech API (no cost).

### 3. Amazon Polly — Hindi Text to Speech  
Voice: Kajal (neural) — best quality Hindi voice
Engine: neural
Output format: mp3
Cost: Free tier 1M neural chars/month (first 12 months)
Prototype cost: ~$0 (well within free tier)
boto3 client: polly
Key method: synthesize_speech()
Save output to S3 → return presigned URL to frontend

### 4. Amazon DynamoDB — Welfare Schemes Database
Table name: welfare_schemes
Partition key: scheme_id (String)
Why DynamoDB not RDS: serverless, free tier, no setup, instant queries
Free tier: 25GB storage, 25 RCU, 25 WCU — more than enough
boto3 resource: dynamodb
Operations needed: get_item, scan, query
Local equivalent: data/schemes.json (identical structure)

### 5. Amazon S3 — Audio File Storage
Bucket 1: voicebridge-audio-[yourname] (Voice Memory clips + Polly output)
Bucket 2: voicebridge-assets-[yourname] (static assets)
Both buckets: ap-southeast-1 region
Audio bucket needs: presigned URL generation for frontend playback
Cost: ~$0.023/GB/month — negligible for prototype
boto3 client: s3
Key operations: upload_fileobj, generate_presigned_url, get_object

### 6. Amazon Connect — The Phone Call System
Instance alias: voicebridge-demo
Region: ap-southeast-1
IMPORTANT: Cannot get Indian +91 number in 7 days. Use Singapore +65 number.
This is a known prototype constraint — not a bug, not a failure.
For prototype: pre-scripted contact flow with Polly audio (not live AI)
boto3 client: connect
Key operation for outbound call: start_outbound_voice_contact()
Contact flow: Entry → Polly greeting → DTMF menu → Voice Memory clip → Scheme explanation → Trigger SMS Lambda → Goodbye → Disconnect

### 7. Amazon SNS — SMS Delivery
Used for: sending document checklist SMS after voice call
Cost: ~$0.00645 per SMS to Indian numbers
Prototype budget: ~$0.32 for 50 test SMS
boto3 client: sns
Key method: publish() with PhoneNumber and Message parameters
SMS format: scheme name + 3 required documents + helpline number

### 8. AWS Lambda — Serverless Backend (Deployment Target)
Runtime: Python 3.12
Memory: 512MB per function
Timeout: 30 seconds
IAM role: voicebridge-lambda-role
Required permissions: Bedrock, Transcribe, Polly, DynamoDB, S3, SNS, Connect
During development: Flask runs locally (Lambda is deployment target only)
Deployment: zip each service + lambda_function.py wrapper → upload to Lambda

## Non-AWS Services

### Sarvam AI — Regional Language TTS (Frontend)
Used by: Frontend only (via JavaScript fetch)
Endpoint: https://api.sarvam.ai/text-to-speech
Model: bulbul:v2
Languages: hi-IN, ta-IN, kn-IN, te-IN, ml-IN
Speakers: anushka (Hindi/Tamil/Kannada/Telugu), manisha (Malayalam)
Pace: 0.75 (slower for clarity)
Cost: Free tier covers prototype usage
Why: AWS Polly has no neural voices for regional languages
Why not backend: Frontend handles regional TTS to avoid backend roundtrip latency
Pipeline: Hindi text → Sarvam API → base64 audio → decode → Web Audio API

## Environment Variables Reference
USE_MOCK=True          → local development (no AWS calls)
USE_MOCK=False         → production (real AWS calls)
AWS_REGION=ap-southeast-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
DYNAMODB_TABLE_NAME=welfare_schemes
S3_AUDIO_BUCKET=voicebridge-audio-[yourname]
S3_ASSETS_BUCKET=voicebridge-assets-[yourname]

## The Mock → AWS Switch Protocol
Switch services in this order (one at a time, test after each):
1. DynamoDB (lowest risk — read only)
2. Amazon Polly (low risk — one-way call)
3. Amazon Bedrock (medium risk — needs model access approval)
4. Amazon Transcribe (medium risk — async job with S3)
5. Amazon SNS (low risk — verify SMS arrives on phone)

Never switch all services at once. If one breaks, you need to know which one.

## Sahaya System Prompt (For Bedrock Calls)

**Purpose:** Instructs Claude 3 Haiku to act as Sahaya, the warm farmer-friendly AI assistant.

**Key Features:**
- Always responds in Hindi (Devanagari script), simple words
- Recommends only eligible schemes
- Embeds farmer success stories via [PLAY_VOICE_MEMORY:scheme_id] tags
- Keeps responses short (phones calls, not essays)
- Never collects sensitive data (Aadhaar, OTP, passwords)

```
You are Sahaya, a compassionate AI assistant helping rural Indian farmers access government welfare schemes.

RULES:
- Always respond in simple Hindi (Devanagari script). Use easy, everyday words.
- Never ask for Aadhaar number, OTP, or bank account details.
- Always reassure: "This is a legitimate government service. Your data is safe."
- Be warm, patient, encouraging. Tone: Friend who wants to help.
- Recommend ONLY schemes from SCHEME DATA below.
- Never invent benefit amounts — use ONLY from SCHEME DATA.
- When recommending a scheme, include: [PLAY_VOICE_MEMORY:scheme_id]
  - If crop insurance → [PLAY_VOICE_MEMORY:PMFBY]
  - If KCC → [PLAY_VOICE_MEMORY:KCC]
  - If PM-KISAN → [PLAY_VOICE_MEMORY:PM_KISAN]
- Keep responses under 150 words (farmer is on phone call).
- Ask clarifying questions to understand: land size, bank account, current schemes.

SCHEME DATA: {scheme_data}
FARMER PROFILE: {farmer_profile}
CONVERSATION HISTORY: {history}
```

**Note:** Voice Memory clips are farmer success stories (translated to farmer's language). Frontend auto-plays these after Polly TTS finishes.
