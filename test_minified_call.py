"""Test call - MINIFIED TWIML (no whitespace)"""
from services.call_service import initiate_sahaya_call

print('Making call with MINIFIED TwiML (no line breaks)...')
print()

result = initiate_sahaya_call(
    farmer_phone='+917736448307',
    farmer_name='Minified Test',
    scheme_ids=['PM_KISAN']
)

if result.get('success'):
    print('✅ CALL INITIATED')
    print('Call ID:', result.get('call_id'))
    print()
    print('NOW - Your phone should ring')
    print()
    print('EXPECTED: Sahaya speaks Hindi')
    print()
    print('If you hear "press any key" →')
    print('  This means Twilio cannot parse our TwiML')
    print()
    print('If you hear Sahaya speaking →')
    print('  The minified version works! Problem was whitespace.')
else:
    print('❌ CALL FAILED:', result.get('error'))
