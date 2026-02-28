#!/usr/bin/env python
"""Test Sarvam TTS endpoint after v1.3.2 fixes"""

import requests

print('Testing Sarvam TTS Endpoint (v1.3.2)')
print('=' * 70)

# Test 1: Malayalam
print('\nTest 1: Malayalam (ml-IN)')
response = requests.post(
  'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/sarvam-tts',
  json={'text': 'നമസ്കാരം, ഞാൻ സഹായ ആണ്', 'language': 'ml-IN'},
  timeout=30
)
r = response.json()
print(f'  HTTP Status: {response.status_code}')
print(f'  Success: {r.get("success")}')
print(f'  Audio URL: {"PRESENT" if r.get("audio_url") else "MISSING"}')
if r.get('error'):
    print(f'  Error: {r.get("error")}')

# Test 2: Tamil
print('\nTest 2: Tamil (ta-IN)')
response = requests.post(
  'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/sarvam-tts',
  json={'text': 'வணக்கம், நான் சஹாய', 'language': 'ta-IN'},
  timeout=30
)
r = response.json()
print(f'  HTTP Status: {response.status_code}')
print(f'  Success: {r.get("success")}')
print(f'  Audio URL: {"PRESENT" if r.get("audio_url") else "MISSING"}')
if r.get('error'):
    print(f'  Error: {r.get("error")}')

# Test 3: Kannada
print('\nTest 3: Kannada (kn-IN)')
response = requests.post(
  'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/sarvam-tts',
  json={'text': 'ನಮಸ್ಕಾರ, ನಾನು ಸಹಾಯ', 'language': 'kn-IN'},
  timeout=30
)
r = response.json()
print(f'  HTTP Status: {response.status_code}')
print(f'  Success: {r.get("success")}')
print(f'  Audio URL: {"PRESENT" if r.get("audio_url") else "MISSING"}')
if r.get('error'):
    print(f'  Error: {r.get("error")}')

# Test 4: Telugu
print('\nTest 4: Telugu (te-IN)')
response = requests.post(
  'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/sarvam-tts',
  json={'text': 'నమస్కారం, నేను సహాయ', 'language': 'te-IN'},
  timeout=30
)
r = response.json()
print(f'  HTTP Status: {response.status_code}')
print(f'  Success: {r.get("success")}')
print(f'  Audio URL: {"PRESENT" if r.get("audio_url") else "MISSING"}')
if r.get('error'):
    print(f'  Error: {r.get("error")}')

print('\n' + '=' * 70)
print('✓ All tests completed!')
