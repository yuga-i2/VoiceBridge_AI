import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def initiate_outbound_call(farmer_phone, farmer_name, scheme_ids):
    """Mock provider - simulates call for testing"""
    logger.info(f"MOCK CALL: Would call {farmer_phone} for {farmer_name}")
    logger.info(f"Schemes to discuss: {scheme_ids}")
    return {
        'success': True,
        'provider': 'mock',
        'call_id': f'mock_call_{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'farmer_phone': farmer_phone,
        'farmer_name': farmer_name,
        'scheme_ids': scheme_ids,
        'status': 'simulated',
        'message': f'Mock: Sahaya would call {farmer_name} at {farmer_phone} to discuss {len(scheme_ids)} schemes'
    }
