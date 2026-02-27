"""
VoiceBridge AI — Call Service Provider Router
CRITICAL: CALL_PROVIDER is read FRESH from .env on EVERY call.
Never cached at import time. One .env change → instant switch.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
_BASE_DIR = Path(__file__).resolve().parent.parent
_ENV_PATH = _BASE_DIR / '.env'


def _fresh_provider() -> str:
    """Read CALL_PROVIDER fresh from .env. Never cached. Never fails."""
    load_dotenv(dotenv_path=_ENV_PATH, override=True)
    return os.getenv('CALL_PROVIDER', 'mock').strip().lower()


def get_active_provider() -> str:
    """Public accessor — always fresh."""
    return _fresh_provider()


def initiate_sahaya_call(farmer_phone: str, farmer_name: str,
                          scheme_ids: list) -> dict:
    """
    Route call to correct provider based on .env CALL_PROVIDER.
    Switch providers by changing CALL_PROVIDER in .env only.
    No code changes. No restarts needed.
    """
    provider = _fresh_provider()
    logger.info(f"Initiating Sahaya call via provider: {provider}")

    if provider == 'twilio':
        from services.providers.twilio_call_provider import initiate_outbound_call
        return initiate_outbound_call(farmer_phone, farmer_name, scheme_ids)
    elif provider == 'connect':
        from services.providers.connect_call_provider import initiate_outbound_call
        return initiate_outbound_call(farmer_phone, farmer_name, scheme_ids)
    else:
        from services.providers.mock_call_provider import initiate_outbound_call
        return initiate_outbound_call(farmer_phone, farmer_name, scheme_ids)
