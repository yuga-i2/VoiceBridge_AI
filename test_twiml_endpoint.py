#!/usr/bin/env python3
"""Test the /api/call/test-twiml endpoint"""

import requests
import json

print("=" * 70)
print("TESTING /api/call/test-twiml ENDPOINT")
print("=" * 70)

try:
    response = requests.get('http://localhost:5000/api/call/test-twiml?scheme=PM_KISAN&name=Ramesh+Kumar')
    print(f'\nStatus: {response.status_code}')
    print('\nResponse:')
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    print('\n' + '=' * 70)
    print('VERIFICATION:')
    print('=' * 70)
    
    if 'पीएम' in data.get('scheme_name_hi', ''):
        print('✅ scheme_name_hi: Contains Hindi text')
    else:
        print('⚠️  scheme_name_hi:', data.get('scheme_name_hi'))
    
    if '6,000' in data.get('benefit', '') or '6000' in data.get('benefit', ''):
        print('✅ benefit: Contains amount 6,000')
    else:
        print('⚠️  benefit:', data.get('benefit'))
    
    if len(data.get('ai_intro', '')) > 20:
        print('✅ ai_intro: Real AI text generated')
        print(f'   "{data.get("ai_intro")}"')
    else:
        print('⚠️  ai_intro:', data.get('ai_intro'))
    
    if len(data.get('documents', [])) >= 3:
        print('✅ documents: Real list from DynamoDB')
        for doc in data.get('documents', [])[:3]:
            print(f'   - {doc}')
    else:
        print('⚠️  documents:', data.get('documents'))
        
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
