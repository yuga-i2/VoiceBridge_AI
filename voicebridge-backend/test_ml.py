import requests

# Test Malayalam message
r = requests.post(
    'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat',
    json={
        'message': 'പിഎം കിസാൻ പറ്റി പറയൂ',
        'farmer_profile': {'name': 'Ravi', 'land_acres': 2, 'state': 'Kerala', 'has_kcc': False, 'has_bank_account': True},
        'conversation_history': [],
        'language': 'ml-IN'
    }
).json()

print('voice_memory_clip:', r.get('voice_memory_clip'))
print('matched_schemes:', r.get('matched_schemes'))
print('response snippet:', r.get('response_text', '')[:100])
