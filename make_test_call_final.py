#!/usr/bin/env python3
"""
Make a real test call with the current setup to verify fix
"""
from services.call_service import initiate_sahaya_call
from dotenv import load_dotenv
import os
import time

load_dotenv()

print("=" * 80)
print("TESTING SAHAYA CALL FLOW")
print("=" * 80)

phone = os.getenv('TWILIO_VERIFIED_NUMBER')
print(f"\n📞 Calling: {phone}")
print("Expected: You'll hear 'Namaste... Main Sahaya hoon...' in Hindi")
print("NOT Expected: 'Press any key to execute your code'")
print()

try:
    call_sid = initiate_sahaya_call(
        farmer_phone=phone,
        farmer_name="Ranan Test",
        scheme_ids=['PM_KISAN']
    )
    
    print(f"✅ Call initiated!")
    print(f"🆔 Call SID: {call_sid}")
    print(f"⏰ Timestamp: {time.strftime('%H:%M:%S IST')}")
    print()
    print("📱 YOUR PHONE SHOULD BE RINGING NOW...")
    print()
    print("=" * 80)
    print("PLEASE REPORT WHAT YOU HEARD:")
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
