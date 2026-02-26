"""Make a final test call with simplified hardcoded TwiML"""
from services.call_service import initiate_sahaya_call

print('Making FINAL TEST CALL with hardcoded TwiML...')
print('(No function calls = zero chance of crashing)')
print()

result = initiate_sahaya_call(
    farmer_phone='+917736448307',
    farmer_name='Final Test',
    scheme_ids=['PM_KISAN']
)

if result.get('success'):
    print('✅ Call initiated')
    print('Call ID:', result.get('call_id'))
    print()
    print('YOUR PHONE RINGING NOW')
    print()
    print('EXPECTED TO HEAR:')
    print('"Namaste Final Test ji. Main Sahaya hoon..."')
    print()
    print('NOT expected:')
    print('"Press any key to execute your code"')
else:
    print('❌ Call failed:', result.get('error'))
