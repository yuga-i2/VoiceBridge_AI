import requests
import json

# Test Malayalam message
url = 'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat'
payload = {
    'message': 'പിഎം കിസാൻ പറ്റി പറയൂ',
    'farmer_profile': {
        'name': 'Ravi',
        'land_acres': 2,
        'state': 'Kerala',
        'has_kcc': False,
        'has_bank_account': True
    },
    'conversation_history': [],
    'language': 'ml-IN'
}

print(f"Sending request to: {url}")
print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
print("\n" + "="*60 + "\n")

try:
    r = requests.post(url, json=payload, timeout=30)
    response = r.json()
    
    print(f"Status Code: {r.status_code}")
    print(f"\nFull Response:")
    print(json.dumps(response, ensure_ascii=False, indent=2))
    
    print(f"\n" + "="*60)
    print(f"\nKey Values:")
    print(f"voice_memory_clip: {response.get('voice_memory_clip')}")
    print(f"matched_schemes: {response.get('matched_schemes')}")
    print(f"success: {response.get('success')}")
    
except Exception as e:
    print(f"Error: {e}")
