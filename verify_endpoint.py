#!/usr/bin/env python3
"""Test the TwiML endpoint via ngrok tunnel"""

import requests
import sys

# Get ngrok URL
try:
    r = requests.get('http://localhost:4040/api/tunnels', timeout=2)
    tunnels = r.json()['tunnels']
    ngrok_url = [t['public_url'] for t in tunnels if t['proto'] == 'https'][0]
except:
    print("ERROR: ngrok not running")
    sys.exit(1)

endpoint = f"{ngrok_url}/api/call/twiml?farmer_name=TestFarmer&Digits=0"

print("Testing TwiML endpoint via ngrok...")
print(f"URL: {endpoint}")
print("")

try:
    response = requests.get(endpoint, verify=False, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {len(response.content)} bytes")
    print("")
    
    # Show response
    text = response.text if response.text else response.content.decode('utf-8', errors='ignore')
    
    if response.status_code == 200:
        print("RESPONSE BODY:")
        print(text[:500])  # First 500 chars
        if len(text) > 500:
            print(f"... ({len(text) - 500} more characters)")
        print("")
        
        # Check if it's valid XML
        if text.startswith('<?xml'):
            print("✅ Starts with XML declaration")
        else:
            print("❌ Does NOT start with XML declaration")
            
        if '<Say' in text:
            print("✅ Contains <Say> tag")
        else:
            print("❌ Missing <Say> tag")
            
        if '<Response>' in text:
            print("✅ Contains <Response> tag")
        else:
            print("❌ Missing <Response> tag")
    else:
        print(f"❌ ERROR {response.status_code}")
        print(f"Response: {text[:300]}")
        
except requests.exceptions.Timeout:
    print("❌ TIMEOUT waiting for response (10 seconds)")
    print("Action: Check if Flask is running")
except requests.exceptions.RequestException as e:
    print(f"❌ REQUEST ERROR: {e}")
except Exception as e:
    print(f"❌ ERROR: {e}")
