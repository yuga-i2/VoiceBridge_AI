import requests
import json

# Test with English message to ensure basic functionality works
url = 'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat'
payload = {
    'message': 'pm kisan ke baare mein batao',
    'farmer_profile': {
        'name': 'Ramesh',
        'land_acres': 2,
        'state': 'Karnataka',
        'has_kcc': False,
        'has_bank_account': True
    },
    'conversation_history': [],
    'language': 'hi-IN'
}

print("Testing with English PM KISAN message...")
r = requests.post(url, json=payload, timeout=30).json()
print(f"matched_schemes: {r.get('matched_schemes')}")
print(f"voice_memory_clip: {r.get('voice_memory_clip')}")
print()

# Now test Malayalam
payload['message'] = 'പിഎം കിസാൻ പറ്റി പറയൂ'
payload['language'] = 'ml-IN'
print("Testing with Malayalam PM KISAN message...")
r = requests.post(url, json=payload, timeout=30).json()
print(f"matched_schemes: {r.get('matched_schemes')}")
print(f"voice_memory_clip: {r.get('voice_memory_clip')}")

# Check if response contains ENGLISH scheme name
if '6000' in r.get('response_text', '').lower() or '₹6' in r.get('response_text', ''):
    print("✓ Response contains PM-KISAN amount (₹6,000)")
else:
    print("✗ Response does not contain PM-KISAN amount")
