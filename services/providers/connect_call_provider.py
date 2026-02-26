import os
import boto3
import logging

logger = logging.getLogger(__name__)

AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-1')
CONNECT_INSTANCE_ID = os.getenv('CONNECT_INSTANCE_ID')
CONNECT_CONTACT_FLOW_ID = os.getenv('CONNECT_CONTACT_FLOW_ID')
CONNECT_QUEUE_ARN = os.getenv('CONNECT_QUEUE_ARN')

def initiate_outbound_call(farmer_phone, farmer_name, scheme_ids):
    """Amazon Connect provider - used when AWS account fully activates"""
    if not CONNECT_INSTANCE_ID or CONNECT_INSTANCE_ID == 'pending':
        return {
            'success': False,
            'provider': 'connect',
            'error': 'Amazon Connect not yet configured',
            'message': 'Set CONNECT_INSTANCE_ID in .env when AWS activates'
        }
    try:
        # Extract Queue ID from ARN (last part after /queue/)
        queue_id = CONNECT_QUEUE_ARN.split('/queue/')[-1] if CONNECT_QUEUE_ARN else None
        
        connect_client = boto3.client('connect', region_name=AWS_REGION)
        response = connect_client.start_outbound_voice_contact(
            DestinationPhoneNumber=farmer_phone,
            ContactFlowId=CONNECT_CONTACT_FLOW_ID,
            InstanceId=CONNECT_INSTANCE_ID,
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
