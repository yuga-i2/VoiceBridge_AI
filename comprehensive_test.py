"""Direct test of keyword matching without API"""

# Test 1: Check if Malayalam keyword is in the list
keywords = ['pm kisan','pmkisan','pm-kisan','kisan samman','6000','kisaan','पीएम किसान','पी एम किसान','pihem kisan','piem kisan','പി എം കിസാൻ','പിഎം കിസാൻ','കിസാൻ സമ്മാൻ','pm kisan','கிசான்','பிஎம் கிசான்','கிசான் சम्मান्']

msg = 'പിഎം കിസാൻ'
m = msg.lower()

print("=" * 60)
print("TEST 1: Direct Keyword Matching")
print("=" * 60)
print(f"Message: '{msg}'")
print(f"Lowercased: '{m}'")
print(f"Keyword to find: 'പിെം കിസാൻ'")
print()

# Check if keyword exists in list
if 'പിെം കിസാൻ' in keywords:
    print("✅ Keyword IS in the list")
else:
    print("❌ Keyword is NOT in the list")

# Check if keyword matches
test_keyword = 'പിെം കിസാൻ'
if test_keyword in m:
    print(f"✅ '{test_keyword}' matches in '{m}'")
else:
    print(f"❌ '{test_keyword}' does NOT match in '{m}'")

# Show all keywords that could match
print("\nKeywords that would match:")
matching = []
for k in keywords:
    if k in m:
        matching.append(k)
        print(f"  ✅ '{k}'")

if not matching:
    print("  (None)")

print("\n" + "=" * 60)
print("TEST 2: Function Simulation")
print("=" * 60)

def detect_scheme(msg):
    m = msg.lower()
    pm_kisan_keywords = ['pm kisan','pmkisan','pm-kisan','kisan samman','6000','kisaan','पीएम किसान','पी एम किसान','pihem kisan','piem kisan','പി എം കിസാൻ','പിെം കിസാൻ','കിസാൻ സമ്മാൻ','pm kisan','கிசான்','பிஎம் கிசान்','கிसान् सम्मान्']
    
    print(f"Input message: '{msg}'")
    print(f"Lowercased: '{m}'")
    print(f"Total PM_KISAN keywords: {len(pm_kisan_keywords)}")
    
    if any(k in m for k in pm_kisan_keywords):
        print("✅ DETECTED: PM_KISAN")
        return ['PM_KISAN'], 'PM_KISAN'
    else:
        print("❌ NOT DETECTED")
        return [], None

schemes, clip = detect_scheme('പിെം കിസാൻ')
print(f"Result: schemes={schemes}, clip={clip}")

print("\n" + "=" * 60)
print("TEST 3: Live API Test")
print("=" * 60)

import requests
payload = {
    'message': 'പിെം കിസാൻ',
    'farmer_profile': {'name': 'Ravi', 'land_acres': 2, 'state': 'Kerala', 'has_kcc': False, 'has_bank_account': True},
    'conversation_history': [],
    'language': 'ml-IN'
}

try:
    r = requests.post('https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat', json=payload, timeout=10)
    result = r.json()
    
    schemes = result.get('matched_schemes', [])
    clip = result.get('voice_memory_clip')
    
    if schemes or clip:
        print("✅ API DETECTED SCHEME")
        print(f"   matched_schemes: {schemes}")
        print(f"   voice_memory_clip: {clip}")
    else:
        print("❌ API DID NOT DETECT SCHEME")
        print(f"   matched_schemes: {schemes}")
        print(f"   voice_memory_clip: {clip}")
        print(f"\n   Full response: {result}")
        
except Exception as e:
    print(f"❌ API Error: {e}")
