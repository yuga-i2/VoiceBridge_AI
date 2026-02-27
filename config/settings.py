"""
VoiceBridge AI — Centralized Configuration
All environment variables loaded here. Import from this module everywhere.
NEVER read os.getenv() or .env directly in service files.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_BASE_DIR / '.env', override=True)

# ── Flask ──────────────────────────────────────────────
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))

# ── Mock Toggle ───────────────────────────────────────
# USE_MOCK=True  → all services use local data, no AWS calls
# USE_MOCK=False → all services call real AWS via boto3
USE_MOCK = os.getenv('USE_MOCK', 'True').strip().lower() in ('true', '1', 'yes')

# ── AWS Core ──────────────────────────────────────────
AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')

# ── Amazon Bedrock ────────────────────────────────────
BEDROCK_MODEL_ID = os.getenv(
    'BEDROCK_MODEL_ID',
    'anthropic.claude-3-haiku-20240307-v1:0'
)

# ── Amazon DynamoDB ───────────────────────────────────
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'welfare_schemes')

# ── Amazon S3 ─────────────────────────────────────────
S3_AUDIO_BUCKET = os.getenv('S3_AUDIO_BUCKET', 'voicebridge-audio-yuga')
S3_ASSETS_BUCKET = os.getenv('S3_ASSETS_BUCKET', 'voicebridge-assets-yuga')

# ── Amazon SNS ────────────────────────────────────────
SNS_SENDER_ID = os.getenv('SNS_SENDER_ID', 'Sahaya')

# ── Amazon Connect ────────────────────────────────────
CONNECT_INSTANCE_ID = os.getenv('CONNECT_INSTANCE_ID', '')
CONNECT_CONTACT_FLOW_ID = os.getenv('CONNECT_CONTACT_FLOW_ID', '')
CONNECT_PHONE_NUMBER = os.getenv('CONNECT_PHONE_NUMBER', '')
CONNECT_QUEUE_ARN = os.getenv('CONNECT_QUEUE_ARN', '')

# ── Twilio ────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
TWILIO_VERIFIED_NUMBER = os.getenv('TWILIO_VERIFIED_NUMBER', '')

# ── Call Provider ─────────────────────────────────────
# Valid values: 'twilio', 'connect', 'mock'
# This is READ FRESH inside call_service.py — not cached here
CALL_PROVIDER_DEFAULT = os.getenv('CALL_PROVIDER', 'mock')

# ── Webhook ───────────────────────────────────────────
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'http://localhost:5000')

# ── Startup Summary ───────────────────────────────────
if __name__ != '__main__':
    _mode = "🔴 LIVE AWS" if not USE_MOCK else "🟡 MOCK MODE"
    print(f"[Config] {_mode} | Region: {AWS_REGION} | Provider: {CALL_PROVIDER_DEFAULT}")
