import os
import boto3
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
_BASE_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_PATH = _BASE_DIR / '.env'


def initiate_outbound_call(farmer_phone, farmer_name, scheme_ids):
    """Amazon Connect provider - reads .env fresh on every call."""
    load_dotenv(dotenv_path=_ENV_PATH, override=True)
    
    aws_region = os.getenv('AWS_REGION', 'ap-southeast-1')
    connect_instance_id = os.getenv('CONNECT_INSTANCE_ID', '')
    connect_contact_flow_id = os.getenv('CONNECT_CONTACT_FLOW_ID', '')
    connect_queue_arn = os.getenv('CONNECT_QUEUE_ARN', '')
    
    if not connect_instance_id:
        return {
            'success': False,
            'provider': 'connect',
            'error': 'Amazon Connect not yet configured',
            'message': 'Set CONNECT_INSTANCE_ID in .env when AWS activates'
        }
    try:
        queue_id = connect_queue_arn.split('/queue/')[-1] if connect_queue_arn else None
        
        connect_client = boto3.client('connect', region_name=aws_region)
        response = connect_client.start_outbound_voice_contact(
            DestinationPhoneNumber=farmer_phone,
            ContactFlowId=connect_contact_flow_id,
            InstanceId=connect_instance_id,
            QueueId=queue_id,
            Attributes={
                'farmerName': farmer_name,
                'schemeIds': ','.join(scheme_ids[:3]),
                'language': 'hi-IN'
            }
        )
        return {
            'success': True,
            'provider': 'connect',
            'call_id': response['ContactId'],
            'farmer_phone': farmer_phone,
            'farmer_name': farmer_name,
            'scheme_ids': scheme_ids,
            'status': 'initiated',
            'message': f'Sahaya is calling {farmer_name} via Amazon Connect'
        }
    except Exception as e:
        logger.error(f"Connect call failed: {e}")
        return {
            'success': False,
            'provider': 'connect',
            'error': str(e)
        }
