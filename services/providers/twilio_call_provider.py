import os
import logging
from twilio.rest import Client

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Publicly accessible URL where your Flask app is deployed
# During development use ngrok URL, in production use Amplify URL
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'http://localhost:5000')

def initiate_outbound_call(farmer_phone, farmer_name, scheme_ids):
    """Twilio provider - makes real outbound calls"""
    try:
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            return {
                'success': False,
                'provider': 'twilio',
                'error': 'Twilio credentials not configured',
                'message': 'Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env'
            }
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Build TwiML webhook URL - Twilio calls this to get call instructions
        scheme_param = ','.join(scheme_ids[:3])
        twiml_url = f"{WEBHOOK_BASE_URL}/api/call/twiml?farmer_name={farmer_name}&schemes={scheme_param}"
        
        call = client.calls.create(
            to=farmer_phone,
            from_=TWILIO_PHONE_NUMBER,
            url=twiml_url,
            status_callback=f"{WEBHOOK_BASE_URL}/api/call/status",
            method='GET'
        )
        
        logger.info(f"Twilio call initiated: {call.sid} to {farmer_phone}")
        return {
            'success': True,
            'provider': 'twilio',
            'call_id': call.sid,
            'farmer_phone': farmer_phone,
            'farmer_name': farmer_name,
            'scheme_ids': scheme_ids,
            'status': 'initiated',
            'message': f'Sahaya is calling {farmer_name} at {farmer_phone}'
        }
    except Exception as e:
        logger.error(f"Twilio call failed: {e}")
        return {
            'success': False,
            'provider': 'twilio',
            'error': str(e),
            'message': 'Call initiation failed'
        }
