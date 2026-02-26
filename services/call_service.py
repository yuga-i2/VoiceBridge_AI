"""
VoiceBridge AI — Call Service
Routes outbound calls through configured provider.
Supports: Twilio, Amazon Connect, Mock
Provider is read FRESH from .env on every call — zero caching.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Reload .env on every call to ensure fresh values
_BASE_DIR = Path(__file__).resolve().parent.parent
_DOTENV_PATH = _BASE_DIR / '.env'


def _get_provider():
    """Read CALL_PROVIDER fresh from .env every time. Never cached."""
    load_dotenv(dotenv_path=_DOTENV_PATH, override=True)
    return os.getenv('CALL_PROVIDER', 'mock').strip().lower()


def initiate_sahaya_call(farmer_phone, farmer_name, scheme_ids):
    """
    Initiate proactive outbound call to farmer.
    
    Provider is read FRESH from .env on every call.
    Switch providers by changing CALL_PROVIDER in .env:
        twilio  → Twilio (works now, India enabled)
        connect → Amazon Connect (when country permissions granted)
        mock    → Simulate call, no real call made
    
    Zero code changes needed to switch. Zero restarts needed.
    """
    provider = _get_provider()
    logger.info(f"Initiating call via provider: {provider}")

    if provider == 'twilio':
        from services.providers.twilio_call_provider import (
            initiate_outbound_call
        )
        return initiate_outbound_call(farmer_phone, farmer_name, scheme_ids)

    elif provider == 'connect':
        from services.providers.connect_call_provider import (
            initiate_outbound_call
        )
        return initiate_outbound_call(farmer_phone, farmer_name, scheme_ids)

    else:
        from services.providers.mock_call_provider import (
            initiate_outbound_call
        )
        return initiate_outbound_call(farmer_phone, farmer_name, scheme_ids)


def get_active_provider():
    """Returns current provider fresh from .env. Never cached."""
    return _get_provider()
