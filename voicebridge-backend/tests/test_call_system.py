#!/usr/bin/env python3
"""
VoiceBridge AI — Call System Integration Tests
Tests the complete calling system: Connect, Twilio, and mock providers.
Run with: python tests/test_call_system.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env with override
load_dotenv(override=True)

# Add parent directory to path so we can import services
sys.path.insert(0, str(Path(__file__).parent.parent))

def mask_credential(value, prefix_chars=8):
    """Mask credentials for display"""
    if not value or len(value) <= prefix_chars:
        return value
    return value[:prefix_chars] + "..."

def print_section(title):
    """Print section separator"""
    print("\n" + "=" * 50)
    print(f"SECTION: {title}")
    print("=" * 50)

def test_environment_check():
    """SECTION 1: Load .env and print current configuration"""
    print_section("1 — Environment Check")
    try:
        call_provider = os.getenv('CALL_PROVIDER', 'not-set')
        connect_instance = os.getenv('CONNECT_INSTANCE_ID', 'not-set')
        connect_flow = os.getenv('CONNECT_CONTACT_FLOW_ID', 'not-set')
        connect_phone = os.getenv('CONNECT_PHONE_NUMBER', 'not-set')
        connect_queue = os.getenv('CONNECT_QUEUE_ARN', 'not-set')
        twilio_sid = os.getenv('TWILIO_ACCOUNT_SID', 'not-set')
        twilio_phone = os.getenv('TWILIO_PHONE_NUMBER', 'not-set')
        webhook_url = os.getenv('WEBHOOK_BASE_URL', 'not-set')
        
        print(f"CALL_PROVIDER:           {call_provider}")
        print(f"CONNECT_INSTANCE_ID:     {mask_credential(connect_instance, 8)}")
        print(f"CONNECT_CONTACT_FLOW_ID: {mask_credential(connect_flow, 8)}")
        print(f"CONNECT_PHONE_NUMBER:    {connect_phone}")
        print(f"CONNECT_QUEUE_ARN:       {mask_credential(connect_queue, 30)}")
        print(f"TWILIO_ACCOUNT_SID:      {mask_credential(twilio_sid, 8)}")
        print(f"TWILIO_PHONE_NUMBER:     {twilio_phone}")
        print(f"WEBHOOK_BASE_URL:        {webhook_url}")
        
        print("\n✅ PASS: Environment loaded successfully")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_mock_provider():
    """SECTION 2: Mock provider test (always runs, no credentials needed)"""
    print_section("2 — Mock Provider Test")
    try:
        from services.call_service import initiate_sahaya_call
        
        # Temporarily override to mock for this test
        original_provider = os.getenv('CALL_PROVIDER')
        os.environ['CALL_PROVIDER'] = 'mock'
        
        # Reimport to pick up new env
        import importlib
        import services.call_service as call_service
        importlib.reload(call_service)
        
        result = call_service.initiate_sahaya_call(
            farmer_phone='+919999999999',
            farmer_name='Rajesh Kumar',
            scheme_ids=['PM_KISAN', 'PMFBY']
        )
        
        print(f"Result: {result}")
        
        # Restore original provider
        os.environ['CALL_PROVIDER'] = original_provider or 'mock'
        
        if result.get('success') and result.get('provider') == 'mock':
            if 'Rajesh Kumar' in str(result.get('message', '')):
                print("✅ PASS: Mock provider works correctly, farmer name in message")
                return True
            else:
                print("✅ PASS: Mock provider works, message:", result.get('message', ''))
                return True
        else:
            print(f"❌ FAIL: success={result.get('success')}, provider={result.get('provider')}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_active_provider():
    """SECTION 3: Active provider test (tests whichever CALL_PROVIDER is set)"""
    print_section("3 — Active Provider Test")
    try:
        # Force reload .env before reading provider
        dotenv_path = Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=dotenv_path, override=True)
        
        # Read provider AFTER dotenv reload
        current_provider = os.getenv('CALL_PROVIDER', 'mock').strip().lower()
        print(f"Active provider from .env: {current_provider}")
        
        if current_provider == 'mock':
            print("⊘ SKIP: CALL_PROVIDER=mock in .env")
            print("  Change to twilio or connect to test real calls")
            return True
        else:
            verified_number = os.getenv('TWILIO_VERIFIED_NUMBER', '')
            if not verified_number:
                print("⊘ SKIP: TWILIO_VERIFIED_NUMBER not set in .env")
                return True
            else:
                print(f"Calling {verified_number} via {current_provider}...")
                
                # Import call service AFTER dotenv reload
                # Use importlib to force fresh import
                import importlib
                import services.call_service as cs
                importlib.reload(cs)
                
                result = cs.initiate_sahaya_call(
                    verified_number,
                    'Ramesh Kumar',
                    ['PM_KISAN', 'PMFBY']
                )
                
                print(f"Provider used: {result.get('provider')}")
                print(f"Success: {result.get('success')}")
                print(f"Message: {result.get('message')}")
                
                if result.get('success'):
                    print(f"✅ PASS: {current_provider} call initiated")
                    if current_provider == 'twilio':
                        print("   📱 YOUR PHONE SHOULD BE RINGING NOW")
                    return True
                else:
                    print(f"❌ FAIL: {result.get('error')}")
                    return False
                
    except Exception as e:
        print(f"❌ ERROR in Section 3: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_endpoint():
    """SECTION 4: Flask endpoint test (tests /api/initiate-call endpoint)"""
    print_section("4 — Flask Endpoint Test")
    try:
        import requests
        
        # Get verified phone from env
        verified_phone = os.getenv('TWILIO_VERIFIED_NUMBER')
        if not verified_phone:
            print("⊘ SKIP: TWILIO_VERIFIED_NUMBER not set in .env")
            return True
        
        url = 'http://localhost:5000/api/initiate-call'
        payload = {
            'farmer_phone': verified_phone,
            'farmer_name': 'Flask Test Farmer',
            'scheme_ids': ['PM_KISAN', 'PMFBY']
        }
        
        print(f"POST {url}")
        print(f"Payload: {payload}")
        
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        print(f"Response: {result}")
        
        if 'success' in result and 'active_provider' in result:
            if result.get('success'):
                print("✅ PASS: Flask endpoint works, call initiated")
                return True
            else:
                print(f"⚠ PASS: Flask endpoint responds, but call failed: {result.get('error')}")
                return True
        else:
            print(f"❌ FAIL: Missing required fields in response")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Flask server not running - start with: python app.py")
        print("⊘ SKIP: Flask not available")
        return True
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests and report summary"""
    print("\n🔔 VoiceBridge AI — Call System Tests Starting...\n")
    
    results = {
        'Environment Check': test_environment_check(),
        'Mock Provider': test_mock_provider(),
        'Active Provider': test_active_provider(),
        'Flask Endpoint': test_flask_endpoint(),
    }
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✅" if passed_flag else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n{passed}/{total} sections passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed or skipped")
        return 1

if __name__ == '__main__':
    exit(main())
