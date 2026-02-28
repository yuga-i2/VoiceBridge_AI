#!/usr/bin/env python
"""Detailed test to see Sarvam API error response"""

import requests
import json
from config.settings import SARVAM_API_KEY, SARVAM_API_URL

print('Sarvam API Detailed Error Testing')
print('=' * 70)
print(f'SARVAM_API_URL: {SARVAM_API_URL}')
print(f'SARVAM_API_KEY: {SARVAM_API_KEY[:20]}...' if SARVAM_API_KEY else 'NOT SET')
print()

headers = {'api-subscription-key': SARVAM_API_KEY}

# Test with Malayalam
payload = {
    'inputs': [{'text': 'നമസ്കാരം'}],
    'target_language_code': 'ml-IN',
    'speaker': 'pavithra',
    'pitch': 1.0,
    'pace': 1.0,
    'loudness': 1.5
}

print('Test Request:')
print(f'  Language: ml-IN')
print(f'  Speaker: pavithra')
print(f'  Text: നമസ്കാരം')
print()

print('Sending request to Sarvam API...')
response = requests.post(SARVAM_API_URL, json=payload, headers=headers, timeout=30)

print(f'Response Status: {response.status_code}')
print('Response Headers:')
for k, v in response.headers.items():
    print(f'  {k}: {v}')
print()
print('Response Body:')
try:
    resp_json = response.json()
    print(json.dumps(resp_json, indent=2, ensure_ascii=False))
except:
    print(response.text)
