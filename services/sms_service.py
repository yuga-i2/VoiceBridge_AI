"""
VoiceBridge AI — SMS Service
Sends document checklist SMS after scheme recommendation.
Supports multi-provider: Twilio, SNS (AWS), or Mock
"""

import os
import logging
from config.settings import USE_MOCK, AWS_REGION, SNS_SENDER_ID
from services.scheme_service import format_scheme_for_sms

logger = logging.getLogger(__name__)

SMS_PROVIDER = os.getenv('SMS_PROVIDER', 'mock')

if not USE_MOCK:
    import boto3

# Twilio imports (only if provider is twilio)
if SMS_PROVIDER == 'twilio':
    try:
        from twilio.rest import Client
        TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
        TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
        TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
        TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception as e:
        logger.warning(f"Twilio not configured: {e}")
        TWILIO_CLIENT = None


def send_checklist(phone_number: str, scheme_ids: list[str]) -> dict:
    """
    Sends SMS with document checklist for selected schemes.
    Provider can be switched via SMS_PROVIDER env var:
    - 'twilio': Use Twilio
    - 'sns': Use AWS SNS
    - 'mock': Print to console
    """
    # Get formatted SMS text
    message_text = format_scheme_for_sms(scheme_ids)
    
    if SMS_PROVIDER == 'twilio':
        return _send_via_twilio(phone_number, message_text)
    elif SMS_PROVIDER == 'sns':
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
        if not TWILIO_CLIENT:
            return {
                "success": False,
                "error": "Twilio not configured",
                "message_preview": message_text,
                "provider": "twilio"
            }
        
        message = TWILIO_CLIENT.messages.create(
            body=message_text,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
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
