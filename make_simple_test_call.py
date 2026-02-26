"""Make a simple test call to verify basic TwiML works"""
from twilio.rest import Client
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_PHONE_NUMBER')

client = Client(account_sid, auth_token)

print('Making SIMPLE TEST call...')
print()

call = client.calls.create(
    to='+917736448307',
    from_=twilio_number,
    url='https://164a-43-229-91-78.ngrok-free.app/api/call/simple-test?farmer_name=Simple',
    method='GET'
)

print('Call created:')
print('Call SID:', call.sid)
print('Status:', call.status)
print()
print('Your phone should ring NOW')
print('You should hear: "Namaste Simple. Main Sahaya hoon..."')
print()
print('If you hear something else (like "press any key"), then:')
print('- Twilio is not parsing our TwiML correctly')
print('- Or the ngrok tunnel is having issues')
print('- Or there is an XML parsing error in the response')
