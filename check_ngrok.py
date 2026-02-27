#!/usr/bin/env python3
"""Check if ngrok is running and get the active tunnel URL"""

import requests
import json

print("Checking if ngrok is running...")
try:
    r = requests.get('http://localhost:4040/api/tunnels', timeout=2)
    if r.status_code == 200:
        data = r.json()
        tunnels = data.get('tunnels', [])
        if tunnels:
            print(f"✅ ngrok IS running")
            for t in tunnels:
                url = t.get('public_url')
                proto = t.get('proto')
                print(f"   {proto}: {url}")
        else:
            print("❌ ngrok running but NO tunnels")
    else:
        print(f"❌ ngrok API status {r.status_code}")
except Exception as e:
    print(f"❌ ngrok NOT running")
    print(f"   Error: {e}")
    print("")
    print("You need to start ngrok with:")
    print("   ngrok http 5000 --log=stdout")
