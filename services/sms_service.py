"""
VoiceBridge AI — SMS Service
Sends document checklist SMS after scheme recommendation.
"""

from config.settings import USE_MOCK, AWS_REGION, SNS_SENDER_ID
from services.scheme_service import format_scheme_for_sms

if not USE_MOCK:
    import boto3


def send_checklist(phone_number: str, scheme_ids: list[str]) -> dict:
    """
    Sends SMS with document checklist for selected schemes.
    """
    # Get formatted SMS text
    message_text = format_scheme_for_sms(scheme_ids)
    
    if USE_MOCK:
        # Mock path - print to console
        print("\n" + "=" * 70)
        print("MOCK SMS")
        print("=" * 70)
        print(f"To: {phone_number}")
        print(f"Message: {message_text}")
        print("=" * 70 + "\n")
        
        return {
            "success": True,
            "message_preview": message_text,
            "mock_mode": True
        }
    
    else:
        # AWS path - use SNS
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
            
            return {
                "success": True,
                "message_preview": message_text,
                "mock_mode": False,
                "message_id": response["MessageId"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message_preview": message_text,
                "mock_mode": False
            }
