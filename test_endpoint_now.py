#!/usr/bin/env python3
"""
Test what the /api/call/twiml endpoint returns RIGHT NOW
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()
webhook_url = os.getenv('WEBHOOK_BASE_URL')

print('Testing endpoint directly...')
print(f'Webhook URL: {webhook_url}')
print()

# Test the endpoint
try:
    resp = requests.get(f'{webhook_url}/api/call/twiml?farmer_name=TestFarmer', verify=False, timeout=10)
    print(f'✅ Status Code: {resp.status_code}')
    print(f'Content-Type: {resp.headers.get("content-type")}')
    print(f'Response Length: {len(resp.text)} chars')
    print()
    print('Response (first 1000 chars):')
    print(resp.text[:1000])
    print()
    
    if resp.text.startswith('<?xml'):
        print('✅✅✅ VALID XML RESPONSE - endpoint is working')
    else:
        print('❌❌❌ NOT XML - endpoint returned something else!')
        print('This could be an error page or HTML')
        
except requests.exceptions.ConnectionError as e:
    print(f'❌ CONNECTION ERROR: ngrok tunnel might be down')
    print(f'   Error: {e}')
except Exception as e:
    print(f'❌ ERROR: {e}')
