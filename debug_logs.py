#!/usr/bin/env python3
"""
Fetch Twilio call logs and notifications for debugging
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client
import json

load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Call ID you mentioned
call_sid = "CA586b082323bd59657c2510769cdbf764"

print(f"Fetching logs for Call SID: {call_sid}")
print("=" * 80)

# Get call details
call = client.calls(call_sid).fetch()
print("\n📱 CALL DETAILS:")
print(f"  Status: {call.status}")
print(f"  Duration: {call.duration} seconds")
print(f"  Start Time: {call.start_time}")
print(f"  End Time: {call.end_time}")
print(f"  Direction: {call.direction}")

# Get notifications (this shows what webhook received)
print("\n📬 NOTIFICATIONS (Webhook interaction):")
try:
    notifications = client.calls(call_sid).notifications.stream()
    notif_list = list(notifications)
    
    if not notif_list:
        print("  ❌ No notifications found!")
    else:
        for i, notif in enumerate(notif_list, 1):
            print(f"\n  Notification #{i}:")
            print(f"    Type: {notif.notification_class}")
            print(f"    Error Code: {notif.error_code}")
            print(f"    Message: {notif.message_text}")
            print(f"    Log Level: {notif.log_level}")
            print(f"    Timestamp: {notif.timestamp}")
            
except Exception as e:
    print(f"  Error fetching notifications: {e}")

# Get events 
print("\n📊 CALL EVENTS:")
try:
    events = client.calls(call_sid).events.stream()
    for event in events:
        print(f"  - {event.type}: {event.timestamp}")
except Exception as e:
    print(f"  Error fetching events: {e}")

print("\n" + "=" * 80)
print("\nIf you see error messages above, that's what Twilio received!")
print("Most common issues:")
print("  - 'Connection refused' = ngrok tunnel down")
print("  - 'timeout' = Flask server not responding")
print("  - 'HTML error page' = Flask crashed and returned error page instead of XML")
