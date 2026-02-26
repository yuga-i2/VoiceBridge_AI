import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlencode
from twilio.rest import Client

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent.parent.parent
_DOTENV_PATH = _BASE_DIR / '.env'


def initiate_outbound_call(farmer_phone, farmer_name, scheme_ids):
    """Twilio provider - makes real outbound calls.
    All credentials read FRESH from .env on every call."""
    
    # Read all credentials fresh every call
    load_dotenv(dotenv_path=_DOTENV_PATH, override=True)
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
    webhook_base = os.getenv('WEBHOOK_BASE_URL', 'http://localhost:5000')

    if not account_sid or not auth_token or not twilio_number:
        return {
            'success': False,
            'provider': 'twilio',
            'error': 'Missing Twilio credentials in .env',
            'message': 'Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER'
        }

    try:
        client = Client(account_sid, auth_token)
        scheme_param = ','.join(scheme_ids[:3])
        twiml_url = (
            f"{webhook_base}/api/call/twiml"
            f"?{urlencode({'farmer_name': farmer_name, 'schemes': scheme_param})}"
        )
        
        # Log the exact URL being sent to Twilio
        logger.info(f"Webhook URL: {twiml_url}")

        call = client.calls.create(
            to=farmer_phone,
            from_=twilio_number,
            url=twiml_url,
            method='POST'
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
            'message': 'Twilio call failed — check credentials and webhook URL'
        }
