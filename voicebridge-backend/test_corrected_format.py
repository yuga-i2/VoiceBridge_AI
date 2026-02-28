#!/usr/bin/env python
"""Test corrected Sarvam payload format locally"""

import requests
import json
from config.settings import SARVAM_API_KEY, SARVAM_API_URL

print('Testing Corrected Sarvam Payload Format')
print('=' * 70)

languages = [
    ('ml-IN', 'നമസ്കാരം', 'pavithra', 'Malayalam'),
    ('ta-IN', 'வணக்கம்', 'kavya', 'Tamil'),
    ('kn-IN', 'ನಮಸ್ಕಾರ', 'arjun', 'Kannada'),
    ('te-IN', 'నమస్కారం', 'meera', 'Telugu'),
]

headers = {'api-subscription-key': SARVAM_API_KEY}

for lang_code, text, speaker, lang_name in languages:
    payload = {
        'text': text,
        'target_language_code': lang_code,
        'speaker': speaker,
        'pitch': 1.0,
        'pace': 1.0,
        'loudness': 1.5
    }
    
    print(f'\n{lang_name} ({lang_code}):')
    print(f'  Speaker: {speaker}')
    print(f'  Text: {text}')
    
    try:
        response = requests.post(SARVAM_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            r = response.json()
            has_audios = 'audios' in r and r['audios']
            print(f'  ✓ Response: 200 OK')
            print(f'  ✓ Has audios: {has_audios}')
            if has_audios:
                print(f'  ✓ Audio length: {len(r["audios"][0])} chars')
        else:
            print(f'  ✗ Response: {response.status_code}')
            err = response.json()
            if 'error' in err:
                print(f'  ✗ Error: {err["error"].get("message", "Unknown")}')
    except Exception as e:
        print(f'  ✗ Exception: {str(e)}')

print('\n' + '=' * 70)
