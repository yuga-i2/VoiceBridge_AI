#!/usr/bin/env python3
"""Test real phone call via Twilio"""

from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Load .env
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path, override=True)

print('=' * 70)
print('TESTING REAL PHONE CALL VIA TWILIO')
print('=' * 70)

# Check configuration
provider = os.getenv('CALL_PROVIDER', 'mock').strip().lower()
verified_number = os.getenv('TWILIO_VERIFIED_NUMBER', '')
twilio_sid = os.getenv('TWILIO_ACCOUNT_SID', '')

print(f'\nConfiguration:')
print(f'  CALL_PROVIDER: {provider}')
print(f'  TWILIO_VERIFIED_NUMBER: {verified_number}')
print(f'  TWILIO_ACCOUNT_SID: {twilio_sid[:8]}...' if twilio_sid else '  TWILIO_ACCOUNT_SID: NOT SET')

if provider != 'twilio':
    print(f'\nERROR: PROVIDER IS NOT twilio (current: {provider})')
    print('   Cannot test real call')
    sys.exit(1)

if not verified_number:
    print(f'\nERROR: TWILIO_VERIFIED_NUMBER NOT SET')
    print('   Cannot test real call')
    sys.exit(1)

# Import and call
print(f'\nCalling {verified_number} via Twilio provider...')
print('(This will make a REAL outbound call)\n')

from services.call_service import initiate_sahaya_call

result = initiate_sahaya_call(
    farmer_phone=verified_number,
    farmer_name='Test Farmer Ranan',
    scheme_ids=['PM_KISAN', 'PMFBY']
)

print('=' * 70)
print('CALL RESULT:')
print('=' * 70)
print(f'Success: {result.get("success")}')
print(f'Provider: {result.get("provider")}')
print(f'Call ID: {result.get("call_id")}')
print(f'Message: {result.get("message")}')
if result.get('error'):
    print(f'Error: {result.get("error")}')

print()
if result.get('success'):
    print('✅ CALL INITIATED SUCCESSFULLY')
    print(f'📱 CHECK YOUR PHONE {verified_number}')
    print('   You should receive a call from Sahaya')
else:
    print('❌ CALL FAILED')
    print(f'   Error: {result.get("error", result.get("message"))}')

print('=' * 70)
