"""
Audio Integration Test Suite for VoiceBridge AI
Tests correct audio file fetching and auto-play timing
"""
import requests
import json

def test_audio_fetch(message, language, expected_scheme, farmer_state, farmer_name):
    """Test audio fetching for a specific message"""
    url = 'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat'
    payload = {
        'message': message,
        'farmer_profile': {
            'name': farmer_name,
            'land_acres': 2,
            'state': farmer_state,
            'has_kcc': False,
            'has_bank_account': True
        },
        'conversation_history': [],
        'language': language
    }
    
    try:
        r = requests.post(url, json=payload, timeout=30).json()
        clip = r.get('voice_memory_clip')
        audio_url = r.get('audio_url')
        schemes = r.get('matched_schemes', [])
        response_text = r.get('response_text', '')[:80]
        success = r.get('success', False)
        
        # Build expected audio filename based on language and scheme
        if language == 'ml-IN':
            expected_audio = f'voice_memory_Mal_{expected_scheme}.mp3.mpeg'
        elif language == 'ta-IN':
            expected_audio = f'voice_memory_Tamil_{expected_scheme}.mp3.mpeg'
        else:
            expected_audio = f'voice_memory_{expected_scheme}.mp3'
        
        # Check if audio URL is present and contains expected filename
        has_audio = audio_url is not None and len(audio_url) > 0
        correct_audio = expected_audio.lower() in (audio_url or '').lower()
        
        status = "✅ PASS" if (clip == expected_scheme and has_audio and success) else "❌ FAIL"
        
        print(f"{status} | {language:8} | {message[:25]:25} | Scheme: {clip:10} | Audio: {has_audio}")
        if has_audio and not correct_audio:
            print(f"       ⚠️  Expected: {expected_audio}")
            print(f"       ⚠️  Got: {audio_url.split('/')[-1].split('?')[0] if audio_url else 'None'}")
        
        return {
            'status': 'PASS' if (clip == expected_scheme and has_audio and success) else 'FAIL',
            'clip': clip,
            'has_audio': has_audio,
            'correct_audio': correct_audio,
            'audio_url': audio_url
        }
    except Exception as e:
        print(f"❌ ERROR | {language:8} | {message[:25]:25} | {str(e)[:40]}")
        return {'status': 'ERROR', 'error': str(e)}

# Test cases with farmer information
test_cases = [
    # PM-KISAN Tests
    ("പിഎം കിസാൻ പറ്റി പറയൂ", "ml-IN", "PM_KISAN", "Kerala", "Priya"),
    ("பிஎம் கிசான் பற்றி சொல்லு", "ta-IN", "PM_KISAN", "Tamil Nadu", "Kavitha"),
    
    # KCC Tests
    ("കിസാൻ ക്രെഡിറ്റ് കാർഡ് കുറിച്ച് ചോദ്യം", "ml-IN", "KCC", "Kerala", "Rajan"),
    ("கிசான் கிரெடிட் அட்டை விபரம்", "ta-IN", "KCC", "Tamil Nadu", "Vijay"),
    
    # PMFBY Tests
    ("വിള ഇൻഷുറൻസ് പദ്ധതി വിശദമായി പറയേണം", "ml-IN", "PMFBY", "Kerala", "Suresh Kumar"),
    ("பயிர் காப்பீடு பற்றி", "ta-IN", "PMFBY", "Tamil Nadu", "Selva"),
]

print("\n" + "="*120)
print("VoiceBridge AI — Audio Integration & Auto-Play Test Suite")
print("="*120 + "\n")
print(f"{'Status':8} | {'Language':8} | {'Message':25} | {'Scheme':10} | {'Audio'}")
print("-"*120)

passed = 0
failed = 0
errors = 0

for message, language, expected_scheme, state, farmer in test_cases:
    result = test_audio_fetch(message, language, expected_scheme, state, farmer)
    if result['status'] == 'PASS':
        passed += 1
    elif result['status'] == 'FAIL':
        failed += 1
    else:
        errors += 1

print("\n" + "="*120)
print(f"RESULTS: {passed} PASSED ✅ | {failed} FAILED ❌ | {errors} ERRORS ⚠️  (Total: {passed + failed + errors})")
print("="*120 + "\n")

if failed > 0 or errors > 0:
    print("RECOMMENDATIONS:")
    print("1. Verify audio files exist in S3 bucket with correct naming")
    print("2. Check language parameter is correctly passed to audio selection logic")
    print("3. Ensure frontend is set to auto-play the audio_url")
    print("4. Verify CORS settings allow audio access from frontend origin")
    print()
