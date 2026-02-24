"""
VoiceBridge AI — Configuration Module
Loads environment variables and exports module-level constants.
Single source of truth for all app configuration.
"""

import os
from dotenv import load_dotenv

# Load .env file at import time
load_dotenv()

# Configuration constants
FLASK_ENV = os.getenv("FLASK_ENV", "development")
USE_MOCK = os.getenv("USE_MOCK", "True").lower() == "true"
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "welfare_schemes")
S3_AUDIO_BUCKET = os.getenv("S3_AUDIO_BUCKET", "")
S3_ASSETS_BUCKET = os.getenv("S3_ASSETS_BUCKET", "")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
SNS_SENDER_ID = os.getenv("SNS_SENDER_ID", "Sahaya")

# Startup summary
print("\n" + "=" * 60)
print("VoiceBridge AI — Configuration Loaded")
print("=" * 60)
print(f"USE_MOCK:              {USE_MOCK}")
print(f"AWS_REGION:            {AWS_REGION}")
print(f"FLASK_PORT:            {FLASK_PORT}")
print(f"BEDROCK_MODEL_ID:      {BEDROCK_MODEL_ID}")
print(f"DYNAMODB_TABLE_NAME:   {DYNAMODB_TABLE_NAME}")
print("=" * 60 + "\n")
