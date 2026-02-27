"""Final verification before Twilio test call."""
import requests
import sys

def test_flask_running():
    """Check if Flask is running."""
    try:
        r = requests.get('http://localhost:5000/api/health', timeout=2)
        if r.status_code == 200:
            print('✅ Flask is running on localhost:5000')
            return True
        else:
            print(f'❌ Flask returned status {r.status_code}')
            return False
    except Exception as e:
        print(f'❌ Flask is NOT running: {e}')
        print('To start Flask: python app.py')
        return False


def test_twiml_endpoint():
    """Verify TwiML endpoint returns valid XML."""
    try:
        url = 'http://localhost:5000/api/call/twiml?farmer_name=Ramesh&schemes=PM_KISAN'
        r = requests.get(url, timeout=5)
        
        print(f'✅ TwiML endpoint status: {r.status_code}')
        ct = r.headers.get('Content-Type', '')
        print(f'✅ Content-Type header: "{ct}"')
        
        # Verify it's correct TwiML header
        if ct.strip() == 'text/xml; charset=utf-8':
            print('✅ CORRECT Header: text/xml; charset=utf-8')
        else:
            print(f'⚠️  Header differs from expected')
        
        # Check XML structure
        if r.text.strip().startswith('<?xml'):
            print('✅ Response starts with XML declaration')
        else:
            print('❌ Response does NOT start with XML declaration')
            print(f'First 100 chars: {r.text[:100]}')
            return False
        
        if('<Response>' in r.text or '<Response >' in r.text) and '<Say' in r.text:
            print('✅ Valid TwiML structure detected (has <Response> and <Say>)')
        else:
            print('❌ Invalid TwiML structure')
            print(f'Response snippet: {r.text[:200]}')
            return False
        
        # Verify Polly voice
        if 'Polly.Kajal' in r.text and 'hi-IN' in r.text:
            print('✅ Polly.Kajal Hindi voice configured')
        else:
            print('⚠️  Polly voice not detected in TwiML')
        
        return True
        
    except Exception as e:
        print(f'❌ TwiML endpoint error: {e}')
        return False


def test_ngrok():
    """Check ngrok tunnel and .env configuration."""
    import os
    from pathlib import Path
    from dotenv import load_dotenv
    
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path, override=True)
    
    webhook_url = os.getenv('WEBHOOK_BASE_URL', '')
    
    if not webhook_url:
        print('❌ WEBHOOK_BASE_URL not set in .env')
        return False
    
    print(f'✅ WEBHOOK_BASE_URL in .env: {webhook_url}')
    
    # Test if ngrok URL is reachable
    test_endpoint = f'{webhook_url}/api/call/ping'
    try:
        r = requests.get(test_endpoint, timeout=5)
        if r.status_code == 200:
            print(f'✅ ngrok tunnel is ACTIVE and reachable')
            print(f'✅ Ping endpoint returned: {r.status_code}')
            return True
        else:
            print(f'❌ ngrok tunnel returned status {r.status_code}')
            return False
    except Exception as e:
        print(f'❌ ngrok tunnel is NOT reachable: {e}')
        print(f'   Make sure: ngrok http 5000 is running')
        print(f'   And WEBHOOK_BASE_URL={webhook_url} is current')
        return False


def main():
    print('=' * 70)
    print('FINAL VERIFICATION BEFORE TWILIO CALL TEST')
    print('=' * 70)
    print()
    
    print('Checking Flask...')
    if not test_flask_running():
        sys.exit(1)
    print()
    
    print('Checking TwiML endpoint...')
    if not test_twiml_endpoint():
        sys.exit(1)
    print()
    
    print('Checking ngrok tunnel...')
    if not test_ngrok():
        sys.exit(1)
    print()
    
    print('=' * 70)
    print('✅ ALL CHECKS PASSED - READY FOR CALL TEST')
    print('=' * 70)
    print()
    print('To make a test call:')
    print('  python tests/test_call_system.py')
    print()
    print('Or manually:'  )
    print('  python -c "')
    print('    from services.call_service import initiate_call')
    print('    initiate_call(')
    print('      phone_number=\"+917736448307\",')
    print('      farmer_name=\"Ramesh Kumar\",')
    print('      scheme_ids=[\"PM_KISAN\"]')
    print('    )')
    print('  "')
    print()
    print('When your phone rings:')
    print('  1. Press any key (Twilio trial requirement)')
    print('  2. Listen for Hindi voice: नमस्ते Ramesh Kumar जी!')
    print('  3. Follow the DTMF prompts (press 1, 2, or 3 as instructed)')
    print()


if __name__ == '__main__':
    main()
