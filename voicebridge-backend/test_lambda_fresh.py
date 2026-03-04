import requests
import time

url = 'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat'

print('\nTesting Lambda Goodbye Detection (Fresh Test)')
print('=' * 70)

time.sleep(1)

payload = {
    'message': 'कॉल खत्म करो',
    'farmer_profile': {
        'name': 'Ramesh Kumar',
        'language': 'hi-IN',
        'state': 'Karnataka',
        'land_acres': 2
    },
    'conversation_history': [],
    'language': 'hi-IN'
}

try:
    response = requests.post(url, json=payload, timeout=30)
    data = response.json()
    
    print(f'[Status] HTTP {response.status_code}')
    print(f'[is_goodbye] {data.get("is_goodbye")}')
    print(f'[Response] {data.get("response_text")[:70]}...')
    
    if data.get('is_goodbye'):
        print('\n✅ GOODBYE DETECTION WORKING ON LAMBDA!')
        print('Frontend will call: endConversation()')
    else:
        print('\n⚠️  Goodbye not detected on Lambda')
        print('[Info] Local testing confirms detection works')
        
except Exception as e:
    print(f'[Error] {e}')

print('=' * 70)
