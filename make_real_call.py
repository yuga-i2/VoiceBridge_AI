#!/usr/bin/env python3
"""Make real phone call via Twilio with ngrok public URL"""

from pathlib import Path
from dotenv import load_dotenv
import os
import sys
import time

# Reload .env to get updated WEBHOOK_BASE_URL
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path, override=True)

print('=' * 80)
print('MAKING REAL CALL WITH PUBLIC WEBHOOK URL')
print('=' * 80)

# Check configuration
provider = os.getenv('CALL_PROVIDER', 'mock').strip().lower()
verified_number = os.getenv('TWILIO_VERIFIED_NUMBER', '')
webhook_url = os.getenv('WEBHOOK_BASE_URL', '')
twilio_sid = os.getenv('TWILIO_ACCOUNT_SID', '')

print(f'\n✓ Configuration:')
print(f'  CALL_PROVIDER: {provider}')
print(f'  TWILIO_VERIFIED_NUMBER: {verified_number}')
print(f'  WEBHOOK_BASE_URL: {webhook_url}')
print(f'  TWILIO_ACCOUNT_SID: {twilio_sid[:8]}...' if twilio_sid else '  TWILIO_ACCOUNT_SID: NOT SET')

if provider != 'twilio':
    print(f'\nERROR: PROVIDER IS NOT twilio (current: {provider})')
    sys.exit(1)

if not verified_number:
    print(f'\nERROR: TWILIO_VERIFIED_NUMBER NOT SET')
    sys.exit(1)

if 'localhost' in webhook_url:
    print(f'\nERROR: WEBHOOK_BASE_URL is still localhost!')
    print(f'       Update .env with ngrok URL')
    sys.exit(1)

print(f'\n✓ All configuration valid')
print(f'\n⏳ Attempting to initiate call to {verified_number}...')
print(f'   Using webhook: {webhook_url}')
print(f'\n' + '=' * 80)

# Force fresh import
import importlib
import services.call_service
importlib.reload(services.call_service)

from services.call_service import initiate_sahaya_call

result = initiate_sahaya_call(
    farmer_phone=verified_number,
    farmer_name='Ranan Test',
    scheme_ids=['PM_KISAN', 'PMFBY']
)

print('=' * 80)
print('CALL RESULT:')
print('=' * 80)
print(f'Success: {result.get("success")}')
print(f'Provider Used: {result.get("provider")}')
print(f'Call ID: {result.get("call_id")}')
print(f'Message: {result.get("message")}')
if result.get('error'):
    print(f'Error Details: {result.get("error")}')

print()
if result.get('success'):
    print('✅ CALL INITIATED SUCCESSFULLY!')
    print(f'')
    print(f'📱 YOUR PHONE SHOULD BE RINGING NOW')
    print(f'   Incoming call from Twilio')
    print(f'   Phone: {verified_number}')
    print(f'   Call ID: {result.get("call_id")}')
    print(f'')
    print(f'⏱️  Check your phone for the incoming call...')
else:
    print('❌ CALL FAILED')
    print(f'   Error: {result.get("error", result.get("message"))}')

print('=' * 80)
