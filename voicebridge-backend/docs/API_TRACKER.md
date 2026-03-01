# VoiceBridge AI — API & Code Tracker

> This document is updated every time a file is created or modified.
> It is the single source of truth for what exists, what each file does,
> and what every API endpoint expects and returns.

---

## Project Status

| Component | File | Status |
|-----------|------|--------|
| Configuration | config/settings.py | ✅ Complete (Fixed: fresh load_dotenv) |
| Farmer Model | models/farmer.py | ✅ Complete |
| Scheme Service | services/scheme_service.py | ✅ Complete |
| AI Service | services/ai_service.py | ✅ Complete |
| STT Service | services/stt_service.py | ✅ Complete |
| TTS Service | services/tts_service.py | ✅ Complete |
| SMS Service | services/sms_service.py | ✅ Complete |
| Voice Memory Service | services/voice_memory_service.py | ✅ Complete |
| Call Service Router | services/call_service.py | ✅ Complete (Fresh .env reading) |
| Twilio Provider | services/providers/twilio_call_provider.py | ✅ Complete |
| Connect Provider | services/providers/connect_call_provider.py | ✅ Complete (Fixed: fresh .env) |
| Mock Provider | services/providers/mock_call_provider.py | ✅ Complete |
| Call Routes (6-stage flow) | routes/call_routes.py | ✅ Complete (TwiML headers fixed) |
| Main App | app.py | ✅ Complete (10 endpoints) |
| Schemes Data | data/schemes.json | ✅ Complete |

---

## API Endpoints

| Method | Endpoint | Status | Description |
|--------|----------|--------|-------------|
| GET | /api/health | ✅ Tested | Health check + mode status |
| POST | /api/chat | ✅ Built | Main conversation |
| POST | /api/speech-to-text | ✅ Built | Audio to Hindi text |
| POST | /api/text-to-speech | ✅ Built | Hindi text to audio |
| GET | /api/voice-memory/<scheme_id> | ✅ Built | Get peer success clip from S3 |
| POST | /api/eligibility-check | ✅ Built | Check scheme eligibility |
| POST | /api/send-sms | ✅ Built | Send document checklist via SNS |
| GET | /api/schemes | ✅ Tested | Get all 10 schemes |
| POST | /api/initiate-call | ✅ Built | Start outbound Twilio/Connect call |
| GET | /api/call/ping | ✅ Tested | Minimal TwiML response test |
| POST | /api/call/stage1 | ✅ Built | Trust intro + Voice Memory |
| POST | /api/call/stage2 | ✅ Built | Land size question (1/2/3 acres) |
| POST | /api/call/stage3 | ✅ Built | KCC status + scheme matching |
| POST | /api/call/stage4 | ✅ Built | Document guidance |
| POST | /api/call/stage5 | ✅ Built | Close or second scheme offer |

---

## File Details

### config/settings.py
**Status:** ✅ Complete  
**Purpose:** Loads all environment variables. Single source of config for entire app.  
**Exports:** FLASK_ENV, USE_MOCK, AWS_REGION, BEDROCK_MODEL_ID, DYNAMODB_TABLE_NAME, 
S3_AUDIO_BUCKET, S3_ASSETS_BUCKET, FLASK_PORT, SNS_SENDER_ID  

---

### models/farmer.py
**Status:** ✅ Complete  
**Purpose:** Farmer profile data structure used across all services.  
**Fields:** name, land_acres, state, has_kcc, has_bank_account, phone_number, age, annual_income  

---

### services/scheme_service.py
**Status:** ✅ Complete  
**Purpose:** Matches farmer profile + message keywords to eligible welfare schemes.  
**Mock mode:** Reads from data/schemes.json  
**AWS mode:** Reads from DynamoDB table welfare_schemes  
**Key functions:** get_all_schemes(), match_schemes_to_message(), 
check_eligibility(), format_scheme_for_sms()  

---

### services/ai_service.py
**Status:** ✅ Complete  
**Purpose:** Generates Hindi response as Sahaya using conversation + scheme context.  
**Mock mode:** Returns realistic Hindi mock responses from internal dictionary  
**AWS mode:** Calls Amazon Bedrock Claude 3 Haiku  
**Key functions:** generate_response(), _select_mock_response(), _extract_voice_memory_tag()  
**Special:** Parses [PLAY_VOICE_MEMORY:X] tags from response  

---

### services/stt_service.py
**Status:** ✅ Complete  
**Purpose:** Converts speech to text in multiple languages.  
**Mock mode:** Returns hardcoded test string  
**AWS mode:** Amazon Transcribe with language-specific settings (hi-IN, ml-IN, ta-IN), custom vocab voicebridge-vocab  
**Key functions:** transcribe_audio()  
**Languages supported:** Hindi (hi-IN), Malayalam (ml-IN), Tamil (ta-IN)  

---

### services/tts_service.py
**Status:** ✅ Complete  
**Purpose:** Converts text to audio URLs. Generates Polly TTS for Hindi (backend only).  
**Mock mode:** Returns presigned URL to mock audio file or placeholder  
**AWS mode:** Amazon Polly Kajal neural voice (Hindi), saves to S3, returns presigned URL  
**Regional languages:** Frontend handles via Sarvam AI TTS API (not backend responsibility)  
**Key functions:** synthesize_speech()  
**Strategy:** Backend ALWAYS generates Polly (even for regional inputs), Frontend calls Sarvam AI separately for regional TTS  

---

### services/sms_service.py
**Status:** ✅ Complete  
**Purpose:** Sends document checklist SMS after scheme recommendation.  
**Mock mode:** Prints formatted SMS to console, returns success  
**AWS mode:** Amazon SNS publish to phone number  
**Key functions:** send_checklist()  

---

### services/voice_memory_service.py
**Status:** ✅ Complete  
**Purpose:** Serves correct peer success audio clip by scheme ID and language.  
**Mock mode:** Returns local file path in data/voice_memory/  
**AWS mode:** Returns presigned S3 URL (1-hour expiry)  
**Key functions:** get_clip()  
**Supported scheme IDs:** PM_KISAN, KCC, PMFBY  
**Language variants:** Currently in Hindi; regional variants to be added (ml, ta, etc.)  
**Endpoint:** GET /api/voice-memory/<scheme_id>?language=ml-IN  

---

### app.py
**Status:** ✅ Complete  
**Purpose:** Flask application. Defines all 8 API routes. No business logic here.  

---

### data/schemes.json
**Status:** ✅ Complete  
**Purpose:** Local database of 10 welfare schemes. Mirrors DynamoDB structure exactly.  

---

## Request/Response Schemas

### POST /api/chat
**Request:**
```json
{
  "message": "string (user input in selected language)",
  "farmer_profile": {
    "name": "string",
    "land_acres": "number",
    "state": "string",
    "has_kcc": "boolean",
    "has_bank_account": "boolean",
    "phone_number": "string (optional)"
  },
  "conversation_history": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ],
  "language": "string (hi-IN | ml-IN | ta-IN)"
}
```
**Response:**
```json
{
  "success": "boolean",
  "response_text": "string (Hindi response, regardless of input language)",
  "audio_type": "tts",
  "audio_url": "string (URL to Polly TTS MP3, always generated)",
  "voice_memory_clip": "string | null (scheme_id e.g. 'KCC' or null)",
  "schemes_mentioned": ["array of scheme_id strings"],
  "stage": "string (conversation stage)",
  "conversation_id": "string"
}
```

**Note:** Frontend fetches voice_memory_clip audio separately via GET /api/voice-memory/{scheme_id}?language={language}

### POST /api/speech-to-text
**Request:** multipart/form-data with field "audio" (MP3 or WAV file)  
**Response:**
```json
{
  "success": "boolean",
  "transcript": "string (Hindi text)",
  "confidence": "number (0.0 to 1.0)"
}
```

### POST /api/text-to-speech
**Request:**
```json
{
  "text": "string (Hindi text to convert)",
  "voice": "string (default: Kajal)"
}
```
**Response:**
```json
{
  "success": "boolean",
  "audio_url": "string (URL to MP3 file)",
  "duration_seconds": "number"
}
```

### GET /api/voice-memory/<scheme_id>
**URL parameters:** 
- scheme_id — one of: PM_KISAN, KCC, PMFBY  
- language (query param) — hi-IN | ml-IN | ta-IN (optional, defaults to hi-IN)  

**Response:**
```json
{
  "success": "boolean",
  "audio_url": "string (presigned S3 URL to MP3 clip, 1-hour expiry)",
  "farmer_name": "string",
  "district": "string",
  "scheme": "string"
}
```

### POST /api/eligibility-check
**Request:**
```json
{
  "farmer_profile": {
    "name": "string",
    "land_acres": "number",
    "state": "string",
    "has_kcc": "boolean",
    "has_bank_account": "boolean",
    "age": "number (optional)",
    "annual_income": "number (optional)"
  }
}
```
**Response:**
```json
{
  "success": "boolean",
  "eligible_schemes": [
    {
      "scheme_id": "string",
      "name_en": "string",
      "name_hi": "string",
      "benefit": "string",
      "reason_eligible": "string"
    }
  ],
  "total_eligible": "number",
  "total_schemes": 10,
  "total_benefit_summary": "string"
}
```

### POST /api/send-sms
**Request:**
```json
{
  "phone_number": "string (+91XXXXXXXXXX format)",
  "scheme_ids": ["array of scheme_id strings"]
}
```
**Response:**
```json
{
  "success": "boolean",
  "message_preview": "string (the SMS text that was/would be sent)",
  "mock_mode": "boolean"
}
```

### GET /api/schemes
**Response:**
```json
{
  "success": "boolean",
  "schemes": [
    {
      "scheme_id": "string",
      "name_en": "string",
      "name_hi": "string",
      "benefit": "string",
      "eligibility": ["array of strings"],
      "documents": ["array of strings"],
      "keywords": ["array of strings"],
      "apply_at": "string"
    }
  ],
  "total": 10
}
```

### GET /api/health
**Response:**
```json
{
  "status": "ok",
  "mock_mode": "boolean",
  "version": "1.0.0"
}
```

### Error Response (all endpoints)
```json
{
  "success": false,
  "error": "string (human readable error message)",
  "code": "string (error code like INVALID_INPUT, SERVICE_ERROR)"
}
```
