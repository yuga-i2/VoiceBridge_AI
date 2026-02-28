#!/usr/bin/env python3
"""Deploy script that loads .env credentials before calling zappa."""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Change to backend directory
os.chdir(Path(__file__).parent)

# Load .env file
env_file = Path.cwd() / '.env'
print(f'Loading credentials from: {env_file}')
load_dotenv(env_file, override=True)

# Verify credentials are loaded
ak = os.getenv('AWS_ACCESS_KEY_ID')
sk = os.getenv('AWS_SECRET_ACCESS_KEY')
print(f'AWS_ACCESS_KEY_ID loaded: {"Yes" if ak else "No"}')
print(f'AWS_SECRET_ACCESS_KEY loaded: {"Yes" if sk else "No"}')

# Make sure env vars are set for subprocess
os.environ['AWS_ACCESS_KEY_ID'] = ak or ''
os.environ['AWS_SECRET_ACCESS_KEY'] = sk or ''
os.environ['AWS_DEFAULT_REGION'] = 'ap-southeast-1'

# Run zappa update
print('\nStarting zappa update dev...\n')
result = subprocess.run(['zappa', 'update', 'dev'], cwd=Path.cwd())
sys.exit(result.returncode)
