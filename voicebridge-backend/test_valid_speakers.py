#!/usr/bin/env python
"""Test with valid Sarvam speakers"""

import requests
import json
from config.settings import SARVAM_API_KEY, SARVAM_API_URL

print('Testing with Valid Sarvam Speakers')
print('=' * 70)

languages = [
    ('ml-IN', 'നമസ്കാരം', 'ritu', 'Malayalam'),
    ('ta-IN', 'வணக்கம்', 'priya', 'Tamil'),
    ('kn-IN', 'ನಮಸ್ಕಾರ', 'shreya', 'Kannada'),
    ('te-IN', 'నమస్కారం', 'manisha', 'Telugu'),
    ('hi-IN', 'नमस्कार', 'kavya', 'Hindi'),
]

headers = {'api-subscription-key': SARVAM_API_KEY}

success_count = 0

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
    
    try:
        response = requests.post(SARVAM_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            r = response.json()
            has_audios = 'audios' in r and r['audios']
            print(f'  ✓ Status: 200 OK')
            print(f'  ✓ Has audios: {has_audios}')
            if has_audios:
                audio_len = len(r["audios"][0]) if r["audios"] else 0
                print(f'  ✓ Audio length: {audio_len} chars (base64)')
                success_count += 1
            else:
                print(f'  ✗ No audios in response')
        else:
            print(f'  ✗ Status: {response.status_code}')
            err = response.json()
            if 'error' in err:
                msg = err["error"].get("message", "Unknown")
                print(f'  ✗ Error: {msg[:100]}...')
    except Exception as e:
        print(f'  ✗ Exception: {str(e)[:80]}...')

print('\n' + '=' * 70)
print(f'✓ Successful: {success_count}/5')
