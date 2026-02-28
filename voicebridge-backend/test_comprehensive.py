"""
Comprehensive multilingual test suite for VoiceBridge AI
Tests: English, Hindi, Malayalam, and Tamil language detection
"""
import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_language(message, language, expected_scheme, farmer_state):
    """Test a specific message in a language"""
    url = 'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat'
    payload = {
        'message': message,
        'farmer_profile': {
            'name': 'Test Farmer',
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
        schemes = r.get('matched_schemes', [])
        success = r.get('success', False)
        
        status = "PASS" if (clip == expected_scheme and success) else "FAIL"
        print(f"{status:6} | {language:8} | {message[:30]:30} | clip={clip} | schemes={schemes}")
        return clip == expected_scheme
    except Exception as e:
        print(f"ERROR  | {language:8} | {message[:30]:30} | {str(e)[:40]}")
        return False

# Test cases: (message, language, expected_scheme, farmer_state)
test_cases = [
    # English
    ("Tell me about PM KISAN", "en-IN", "PM_KISAN", "Karnataka"),
    ("KCC loan details please", "en-IN", "KCC", "Karnataka"),
    ("What is crop insurance?", "en-IN", "PMFBY", "Karnataka"),
    
    # Hindi
    ("पीएम किसान के बारे में बताएं", "hi-IN", "PM_KISAN", "Madhya Pradesh"),
    ("कीसीसी लोन चाहिए", "hi-IN", "KCC", "Madhya Pradesh"),
    ("फसल बीमा योजना क्या है", "hi-IN", "PMFBY", "Madhya Pradesh"),
    
    # Malayalam
    ("പിഎം കിസാൻ പറ്റി പറയൂ", "ml-IN", "PM_KISAN", "Kerala"),
    ("കിസാൻ ക്രെഡിറ്റ് കാർഡ് കുറിച്ച് ചോദ്യം", "ml-IN", "KCC", "Kerala"),
    ("വിള ഇൻഷുറൻസ് പദ്ധതി വിശദമായി പറയേണം", "ml-IN", "PMFBY", "Kerala"),
    
    # Tamil
    ("பிஎம் கிசான் பற்றி சொல்லு", "ta-IN", "PM_KISAN", "Tamil Nadu"),
    ("கிரெடிட் கார்டு பற்றி", "ta-IN", "KCC", "Tamil Nadu"),
    ("பயிர் காப்பீடு பற்றி", "ta-IN", "PMFBY", "Tamil Nadu"),
]

print("\n" + "="*100)
print("VoiceBridge AI — Multilingual Scheme Detection Test Suite")
print("="*100 + "\n")
print(f"{'Status':8} | {'Language':8} | {'Message':30} | {'Voice Clip':15} | {'Schemes'}")
print("-"*100)

passed = 0
failed = 0

for message, language, expected_scheme, state in test_cases:
    if test_language(message, language, expected_scheme, state):
        passed += 1
    else:
        failed += 1

print("\n" + "="*100)
print(f"Results: {passed} PASSED, {failed} FAILED out of {passed + failed} tests")
print("="*100 + "\n")
