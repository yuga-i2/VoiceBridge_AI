"""Test the exact webhook URL that Twilio calls"""
import requests
from urllib.parse import urlencode

# Simulate exactly what Twilio does
webhook_base = 'https://164a-43-229-91-78.ngrok-free.app'
farmer_name = 'Ramesh'
scheme_param = 'PM_KISAN'

twiml_url = (
    f"{webhook_base}/api/call/twiml"
    f"?{urlencode({'farmer_name': farmer_name, 'schemes': scheme_param})}"
)

print('Full URL that Twilio will call:')
print(twiml_url)
print()

try:
    r = requests.get(twiml_url, verify=False, timeout=10)
    print('Status:', r.status_code)
    print('Content-Type:', r.headers.get('content-type'))
    print()
    
    if r.status_code == 200:
        print('First 500 chars of response:')
        print(r.text[:500])
        print()
        
        if r.text.startswith('<?xml'):
            print('✅ SUCCESS - Valid TwiML XML returned')
        else:
            print('❌ ERROR - Not XML!')
            print('Full response:', r.text[:500])
    else:
        print('❌ ERROR - Bad status code:', r.status_code)
        print(r.text[:500])
        
except Exception as e:
    print('❌ ERROR:', e)
    import traceback
    traceback.print_exc()
