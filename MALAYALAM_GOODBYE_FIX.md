# Malayalam Goodbye Detection Fix

## Problem
When user said goodbye in Malayalam ("കോൾ അവസാനിപ്പിക്കും"), the system was:
1. ✓ Correctly detecting goodbye (is_goodbye=true)
2. ✓ Correctly setting voice_memory_clip=null
3. ✗ BUT returning matched_schemes=["KCC"] from stale previous turn

This caused frontend to fetch and play voice memory based on matched_schemes, even though goodbye was detected.

## Root Cause
The backend was clearing `voice_memory_clip` but still returning the previous turn's `matched_schemes`. The frontend checks both fields to decide whether to fetch/play voice memory.

## Solution Applied
**Commit: c9643d4** - Clear matched_schemes=[] when goodbye is detected

### Changes in `voicebridge-backend/services/ai_service.py`:
- **Lines 513-517 (MOCK path)**: Already had the fix
- **Lines 579-586 (AWS path)**: Updated to also clear matched_schemes

When `is_goodbye=true`:
```python
if is_goodbye:
    voice_clip = None
    final_schemes = []  # NEW: Clear schemes to prevent frontend fetch
else:
    voice_clip = get_voice_memory_clip(scheme_ids, message)
    final_schemes = scheme_ids
```

## How It Works
1. User says goodbye in ANY language
2. Backend detects goodbye (using unicode-aware keyword matching)
3. Backend returns:
   - `is_goodbye`: true
   - `voice_memory_clip`: null
   - `matched_schemes`: [] (EMPTY - prevents fetch)
4. Frontend receives response
5. Frontend checks `if (aiResponse.voice_memory_clip)` - it's null, so no fetch
6. Voice memory is NOT played ✓

## Verification
Tested goodbye detection for:
- ✓ Malayalam: "കോൾ അവസാനിപ്പിക്കും" → Detected
- ✓ Hindi: "कॉल कम करो" → Detected  
- ✓ English: "bye" → Detected
- ✓ Multiple regional languages - all working

## Testing Instructions
Try these goodbye inputs in different languages:
- **Malayalam**: കോൾ അവസാനിപ്പിക്കും
- **Hindi**: कॉल कम करो  
- **Tamil**: பை / வாழ்க
- **English**: bye / goodbye

Expected behavior: No voice memory audio plays, only TTS response.
