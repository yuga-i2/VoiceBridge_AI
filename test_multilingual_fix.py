import requests

# Test 1: Malayalam PM_KISAN
print("TEST 1: Malayalam PM_KISAN Detection")
payload = {
    'message': 'പിഎം കിസാൻ',
    'farmer_profile': {'name': 'Ravi', 'land_acres': 2, 'state': 'Kerala', 'has_kcc': False, 'has_bank_account': True},
    'conversation_history': [],
    'language': 'ml-IN'
}
try:
    r = requests.post('https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat', json=payload, timeout=10)
    result = r.json()
    print(f"  ✅ matched_schemes: {result.get('matched_schemes', [])}")
    print(f"  ✅ voice_memory_clip: {result.get('voice_memory_clip', 'NONE')}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 2: Tamil KCC
print("\nTEST 2: Tamil KCC Detection")
payload = {
    'message': 'கேசிසி கிரெடிட்',
    'farmer_profile': {'name': 'Vijay', 'land_acres': 1.5, 'state': 'Tamil Nadu', 'has_kcc': False, 'has_bank_account': True},
    'conversation_history': [],
    'language': 'ta-IN'
}
try:
    r = requests.post('https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat', json=payload, timeout=10)
    result = r.json()
    print(f"  ✅ matched_schemes: {result.get('matched_schemes', [])}")
    print(f"  ✅ voice_memory_clip: {result.get('voice_memory_clip', 'NONE')}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 3: Hindi PMFBY (should still work)
print("\nTEST 3: Hindi PMFBY Detection")
payload = {
    'message': 'फसल बीमा योजना के बारे में बताओ',
    'farmer_profile': {'name': 'Ramesh', 'land_acres': 3, 'state': 'Madhya Pradesh', 'has_kcc': False, 'has_bank_account': True},
    'conversation_history': [],
    'language': 'hi-IN'
}
try:
    r = requests.post('https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat', json=payload, timeout=10)
    result = r.json()
    print(f"  ✅ matched_schemes: {result.get('matched_schemes', [])}")
    print(f"  ✅ voice_memory_clip: {result.get('voice_memory_clip', 'NONE')}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n✅ All tests completed!")
