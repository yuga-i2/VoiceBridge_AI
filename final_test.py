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
        print(f'  FAIL: {name} {detail}')
        failed += 1

print('=== ENDPOINT TESTS (AWS MODE) ===')
print()

try:
    # Test 1: Health
    print('1. GET /api/health')
    r = requests.get(f'{BASE}/api/health', timeout=5).json()
    check('mock_mode is False', r.get('mock_mode') == False)
    check('status ok', r.get('status') == 'ok')
except Exception as e:
    print(f'  FAIL: Connection - {str(e)[:50]}')
    failed += 2
    exit(1)

# Test 2: Schemes
print('2. GET /api/schemes')
try:
    r = requests.get(f'{BASE}/api/schemes', timeout=5).json()
    check('10 schemes', r.get('total') == 10, f'got {r.get("total")}')
except Exception as e:
    print(f'  FAIL: {str(e)[:50]}')
    failed += 1

# Test 3: Eligibility
print('3. POST /api/eligibility-check')
try:
    r = requests.post(f'{BASE}/api/eligibility-check', json={
        'farmer_profile': {
            'name': 'Ramesh Kumar', 'land_acres': 2,
            'state': 'Karnataka', 'has_kcc': False,
            'has_bank_account': True, 'age': 45
        }
    }, timeout=5).json()
    ids = [s['scheme_id'] for s in r.get('eligible_schemes', [])]
    check('PM_KISAN eligible', 'PM_KISAN' in ids)
    check('PMFBY eligible', 'PMFBY' in ids)
    check('6+ schemes', len(ids) >= 6, f'got {len(ids)}')
except Exception as e:
    print(f'  FAIL: {str(e)[:50]}')
    failed += 3

# Test 4: Chat with Bedrock
print('4. POST /api/chat (real Bedrock)')
try:
    r = requests.post(f'{BASE}/api/chat', json={
        'message': 'PM-KISAN kya hai mujhe batao',
        'farmer_profile': {
            'name': 'Ramesh Kumar', 'land_acres': 2,
            'state': 'Karnataka', 'has_kcc': False,
            'has_bank_account': True
        },
        'conversation_history': []
    }, timeout=5).json()
    check('chat success', r.get('success') == True)
    check('voice clip PM_KISAN', r.get('voice_memory_clip') == 'PM_KISAN')
    check('Hindi response', len(r.get('response_text','')) > 20)
except Exception as e:
    print(f'  FAIL: {str(e)[:50]}')
    failed += 3

# Test 5: Polly TTS
print('5. POST /api/text-to-speech (real Polly)')
try:
    r = requests.post(f'{BASE}/api/text-to-speech', json={
        'text': 'नमस्ते! मैं सहाया हूं।',
        'voice': 'Kajal'
    }, timeout=5).json()
    check('TTS success', r.get('success') == True)
    url = r.get('audio_url')
    check('S3 audio URL', bool(url) and 'http' in str(url))
except Exception as e:
    print(f'  FAIL: {str(e)[:50]}')
    failed += 2

# Test 6: S3 Voice Memory
print('6. GET /api/voice-memory/PMFBY')
try:
    r = requests.get(f'{BASE}/api/voice-memory/PMFBY', timeout=5).json()
    check('voice memory success', r.get('success') == True)
    check('Laxman Singh', r.get('farmer_name') == 'Laxman Singh')
    url = r.get('audio_url')
    check('S3 URL', bool(url) and 'http' in str(url))
except Exception as e:
    print(f'  FAIL: {str(e)[:50]}')
    failed += 3

# Test 7: SMS
print('7. POST /api/send-sms')
try:
    r = requests.post(f'{BASE}/api/send-sms', json={
        'phone_number': '+919876543210',
        'scheme_ids': ['PM_KISAN', 'KCC']
    }, timeout=5).json()
    check('SMS success', r.get('success') == True)
except Exception as e:
    print(f'  FAIL: {str(e)[:50]}')
    failed += 1

print()
print(f'=== RESULTS: {passed} passed, {failed} failed ===')
if failed == 0:
    print('ALL TESTS PASSED')
    print('PHASE 3 COMPLETE - Ready for frontend')
elif failed <= 2:
    print('MOSTLY PASSING')
else:
    print('ISSUES FOUND')
