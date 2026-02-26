import os
import logging
from services.providers.mock_call_provider import initiate_outbound_call as mock_call
from services.providers.twilio_call_provider import initiate_outbound_call as twilio_call
from services.providers.connect_call_provider import initiate_outbound_call as connect_call

logger = logging.getLogger(__name__)

CALL_PROVIDER = os.getenv('CALL_PROVIDER', 'mock')

def initiate_sahaya_call(farmer_phone, farmer_name, scheme_ids):
    """
    Initiate outbound call to farmer.
    Provider controlled by CALL_PROVIDER env var:
    - 'twilio': Use Twilio (works now, free trial)
    - 'connect': Use Amazon Connect (when AWS activates)
    - 'mock': Simulate call for testing
    
    To switch providers: just change CALL_PROVIDER in .env
    No code changes needed ever.
    """
    logger.info(f"Initiating call via provider: {CALL_PROVIDER}")
    
    if CALL_PROVIDER == 'twilio':
        return twilio_call(farmer_phone, farmer_name, scheme_ids)
    elif CALL_PROVIDER == 'connect':
        return connect_call(farmer_phone, farmer_name, scheme_ids)
    else:
        return mock_call(farmer_phone, farmer_name, scheme_ids)

def get_active_provider():
    return CALL_PROVIDER
