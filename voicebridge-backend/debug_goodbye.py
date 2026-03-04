#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

from services.ai_service import generate_response, _detect_goodbye_intent
from models.farmer import FarmerProfile

# Test with the exact message
msg = 'कॉल खत्म करो'

print('\nDEBUGGING: Message "कॉल खत्म करो"')
print('=' * 60)

# Check if goodbye is detected directly
directly_detected = _detect_goodbye_intent(msg, '')
print(f'[1] Direct goodbye detection: {directly_detected}')

# Now test through generate_response
farmer = FarmerProfile.from_dict({
    'name': 'Test',
    'language': 'hi-IN',
    'state': 'Karnataka',
    'land_acres': 2
})

result = generate_response(msg, [], farmer, [], '')

print(f'[2] Generate response is_goodbye: {result.get("is_goodbye")}')
print(f'[3] Response text: {result.get("response_text")[:80]}...')
print(f'[4] Result keys: {list(result.keys())}')

# Check components
print('\n' + '=' * 60)
print('BREAKDOWN:')
print(f'Mock mode: {result.get("mock")}')
print(f'Success: {result.get("success")}')
print(f'Voice memory: {result.get("voice_memory_clip")}')
