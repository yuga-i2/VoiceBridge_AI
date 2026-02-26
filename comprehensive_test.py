import requests
import time
time.sleep(2)

BASE = 'http://localhost:5000'
passed = 0
failed = 0

def check(name, condition, detail=''):
    global passed, failed
    if condition:
        print(f'  PASS: {name}')
        passed += 1
    else:
        print(f'  FAIL: {name}', detail)
        failed += 1

print('=== COMPREHENSIVE ENDPOINT TESTS ===')
print()

# Test 1: Health must show mock_mode False
print('1. GET /api/health')
r = requests.get(f'{BASE}/api/health').json()
print('   Response:', r)
check('mock_mode is False', r.get('mock_mode') == False, 
      f'got: {r.get("mock_mode")}')

# Test 2: TTS must return S3 URL
print('2. POST /api/text-to-speech')
r = requests.post(f'{BASE}/api/text-to-speech', json={
    'text': 'नमस्ते! मैं सहाया हूं।',
    'voice': 'Kajal'
}).json()
print('   Success:', r.get('success'))
print('   Audio URL:', r.get('audio_url')[:50] if r.get('audio_url') else None)
check('TTS success', r.get('success') == True)
check('S3 URL not null', r.get('audio_url') is not None,
      f'got: {r.get("audio_url")}')
check('S3 URL is real', 's3.amazonaws.com' in str(r.get('audio_url','')))

# Test 3: Voice Memory must return S3 URL
print('3. GET /api/voice-memory/PMFBY')
r = requests.get(f'{BASE}/api/voice-memory/PMFBY').json()
print('   Success:', r.get('success'))
print('   Audio URL:', r.get('audio_url')[:50] if r.get('audio_url') else None)
check('voice memory success', r.get('success') == True)
check('S3 URL not null', r.get('audio_url') is not None,
      f'got: {r.get("audio_url")}')

# Test 4: Chat still working
print('4. POST /api/chat')
r = requests.post(f'{BASE}/api/chat', json={
    'message': 'PM-KISAN kya hai',
    'farmer_profile': {
        'name': 'Ramesh Kumar', 'land_acres': 2,
        'state': 'Karnataka', 'has_kcc': False,
        'has_bank_account': True
    },
    'conversation_history': []
}).json()
check('chat success', r.get('success') == True)
check('voice clip correct', r.get('voice_memory_clip') == 'PM_KISAN')
check('Hindi response', len(r.get('response_text','')) > 20)

# Test 5: Schemes
print('5. GET /api/schemes')
r = requests.get(f'{BASE}/api/schemes').json()
check('10 schemes', r.get('total') == 10)

# Test 6: Eligibility
print('6. POST /api/eligibility-check')
r = requests.post(f'{BASE}/api/eligibility-check', json={
    'farmer_profile': {
        'name': 'Ramesh Kumar', 'land_acres': 2,
        'state': 'Karnataka', 'has_kcc': False,
        'has_bank_account': True
    }
}).json()
ids = [s['scheme_id'] for s in r.get('eligible_schemes', [])]
check('PM_KISAN eligible', 'PM_KISAN' in ids)
check('PMFBY eligible', 'PMFBY' in ids)
check('6+ schemes', len(ids) >= 6)

# Test 7: SMS
print('7. POST /api/send-sms')
r = requests.post(f'{BASE}/api/send-sms', json={
    'phone_number': '+919876543210',
    'scheme_ids': ['PM_KISAN', 'KCC']
}).json()
check('SMS success', r.get('success') == True)

print()
print(f'=== RESULTS: {passed} passed, {failed} failed ===')
if failed == 0:
    print('✅ ALL 15 TESTS PASSING')
    print('✅ PHASE 3 COMPLETE')
else:
    print('❌ Still failing - check details above')
