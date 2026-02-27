import requests
import os
from dotenv import load_dotenv

load_dotenv()

try:
    r = requests.get('http://localhost:4040/api/tunnels', timeout=2)
    data = r.json()
    for tunnel in data['tunnels']:
        if 'http' in tunnel.get('proto', ''):
            ngrok_url = tunnel['public_url']
            print(f"✅ ngrok is RUNNING")
            print(f"URL: {ngrok_url}")
            
            # Check if .env needs updating
            env_url = os.getenv('WEBHOOK_BASE_URL', '')
            if ngrok_url in env_url:
                print(f"✅ .env already has correct URL")
            else:
                print(f"❌ .env has OLD URL: {env_url}")
                print(f"   Need to update to: {ngrok_url}")
            break
except requests.exceptions.ConnectionError:
    print("❌ ngrok is NOT running")
    print("Start ngrok with: ngrok http 5000 --log=stdout")
except Exception as e:
    print(f"Error: {e}")
