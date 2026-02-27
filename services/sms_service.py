"""
VoiceBridge AI — SMS Service
Sends document checklist SMS after scheme recommendation.
Supports multi-provider: Twilio, SNS (AWS), or Mock
Provider is read FRESH from .env on every call — zero caching.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from config.settings import USE_MOCK, AWS_REGION, SNS_SENDER_ID
from services.scheme_service import format_scheme_for_sms

logger = logging.getLogger(__name__)

# Reload .env on every call to ensure fresh values
_BASE_DIR = Path(__file__).resolve().parent.parent
_DOTENV_PATH = _BASE_DIR / '.env'

if not USE_MOCK:
    import boto3


def _get_sms_provider():
    """Read SMS_PROVIDER fresh from .env every time. Never cached."""
    load_dotenv(dotenv_path=_DOTENV_PATH, override=True)
    return os.getenv('SMS_PROVIDER', 'mock').strip().lower()


def send_checklist(phone_number: str, scheme_ids: list[str]) -> dict:
    """
    Sends SMS with document checklist for selected schemes.
    Provider can be switched via SMS_PROVIDER env var:
    - 'twilio': Use Twilio
    - 'sns': Use AWS SNS
    - 'mock': Print to console
    
    Provider is read FRESH from .env on every call — zero caching.
    """
    # Reload .env and get provider fresh
    load_dotenv(dotenv_path=_DOTENV_PATH, override=True)
    sms_provider = os.getenv('SMS_PROVIDER', 'mock').strip().lower()
    
    # Get formatted SMS text
    message_text = format_scheme_for_sms(scheme_ids)
    
    if sms_provider == 'twilio':
        return _send_via_twilio(phone_number, message_text)
    elif sms_provider == 'sns':
        return _send_via_sns(phone_number, message_text)
    else:
        return _send_via_mock(phone_number, message_text)


def _send_via_mock(phone_number: str, message_text: str) -> dict:
    """Mock SMS provider - print to console"""
    print("\n" + "=" * 70)
    print("MOCK SMS")
    print("=" * 70)
    print(f"To: {phone_number}")
    print(f"Message: {message_text}")
    print("=" * 70 + "\n")
    
    return {
        "success": True,
        "message_preview": message_text,
        "provider": "mock"
    }


def _send_via_sns(phone_number: str, message_text: str) -> dict:
    """AWS SNS SMS provider"""
    try:
        sns = boto3.client("sns", region_name=AWS_REGION)
        
        response = sns.publish(
            PhoneNumber=phone_number,
            Message=message_text,
            MessageAttributes={
                "AWS.SNS.SMS.SenderID": {
                    "DataType": "String",
                    "StringValue": SNS_SENDER_ID
                },
                "AWS.SNS.SMS.SMSType": {
                    "DataType": "String",
                    "StringValue": "Transactional"
                }
            }
        )
        
        logger.info(f"SNS SMS sent: {response['MessageId']} to {phone_number}")
        return {
            "success": True,
            "message_preview": message_text,
            "provider": "sns",
            "message_id": response["MessageId"]
        }
    
    except Exception as e:
        logger.error(f"SNS SMS failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message_preview": message_text,
            "provider": "sns"
        }


def _send_via_twilio(phone_number: str, message_text: str) -> dict:
    """Twilio SMS provider"""
    try:
        # Read credentials fresh from .env
        load_dotenv(dotenv_path=_DOTENV_PATH, override=True)
        twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not twilio_account_sid or not twilio_auth_token:
            return {
                "success": False,
                "error": "Twilio not configured",
                "message_preview": message_text,
                "provider": "twilio"
            }
        
        from twilio.rest import Client
        twilio_client = Client(twilio_account_sid, twilio_auth_token)
        
        message = twilio_client.messages.create(
            body=message_text,
            from_=twilio_phone_number,
            to=phone_number
        )
        
        logger.info(f"Twilio SMS sent: {message.sid} to {phone_number}")
        return {
            "success": True,
            "message_preview": message_text,
            "provider": "twilio",
            "message_id": message.sid
        }
    
    except Exception as e:
        logger.error(f"Twilio SMS failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message_preview": message_text,
            "provider": "twilio"
        }
