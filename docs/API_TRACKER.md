# VoiceBridge AI — API & Code Tracker

> This document is updated every time a file is created or modified.
> It is the single source of truth for what exists, what each file does,
> and what every API endpoint expects and returns.

---

## Project Status

| Component | File | Status |
|-----------|------|--------|
| Configuration | config/settings.py | ✅ Complete |
| Farmer Model | models/farmer.py | ✅ Complete |
| Scheme Service | services/scheme_service.py | ✅ Complete |
| AI Service | services/ai_service.py | ✅ Complete |
| STT Service | services/stt_service.py | ✅ Complete |
| TTS Service | services/tts_service.py | ✅ Complete |
| SMS Service | services/sms_service.py | ✅ Complete |
| Voice Memory Service | services/voice_memory_service.py | ✅ Complete |
| Main App | app.py | ✅ Complete |
| Schemes Data | data/schemes.json | ✅ Complete |

---

## API Endpoints

| Method | Endpoint | Status | Description |
|--------|----------|--------|-------------|
| GET | /api/health | ✅ Built | Health check |
| POST | /api/chat | ✅ Built | Main conversation |
| POST | /api/speech-to-text | ✅ Built | Audio to Hindi text |
| POST | /api/text-to-speech | ✅ Built | Hindi text to audio |
| GET | /api/voice-memory/<scheme_id> | ✅ Built | Get peer success clip |
| POST | /api/eligibility-check | ✅ Built | Check scheme eligibility |
| POST | /api/send-sms | ✅ Built | Send document checklist |
| GET | /api/schemes | ✅ Built | Get all schemes |

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
**Purpose:** Converts Hindi audio to text.  
**Mock mode:** Returns hardcoded Hindi test string  
**AWS mode:** Amazon Transcribe with hi-IN, custom vocab voicebridge-vocab  
**Key functions:** transcribe_audio()  

---

### services/tts_service.py
**Status:** ✅ Complete  
**Purpose:** Converts Hindi text to MP3 audio.  
**Mock mode:** Returns path to local mock audio file or placeholder  
**AWS mode:** Amazon Polly Kajal neural voice, saves to S3, returns presigned URL  
**Key functions:** synthesize_speech()  

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
**Purpose:** Serves correct peer success audio clip by scheme ID.  
**Mock mode:** Returns local file path in data/voice_memory/  
**AWS mode:** Returns presigned S3 URL  
**Key functions:** get_clip()  
**Supported scheme IDs:** PM_KISAN, KCC, PMFBY  

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
  "message": "string (Hindi text from farmer)",
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
  ]
}
```
**Response:**
```json
{
  "success": "boolean",
  "response_text": "string (Hindi)",
  "voice_memory_clip": "string | null (scheme_id or null)",
  "matched_schemes": ["array of scheme_id strings"],
  "conversation_id": "string"
}
```

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
**URL parameter:** scheme_id — one of: PM_KISAN, KCC, PMFBY  
**Response:**
```json
{
  "success": "boolean",
  "audio_url": "string (URL to MP3 clip)",
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
