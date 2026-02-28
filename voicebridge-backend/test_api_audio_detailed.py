"""
Test API response with detailed audio information
"""
import requests
import json

def test_api_response(message, language):
    """Test API and show detailed response"""
    url = 'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat'
    payload = {
        'message': message,
        'farmer_profile': {
            'name': 'Test Farmer',
            'land_acres': 2,
            'state': 'Kerala',
            'has_kcc': False,
            'has_bank_account': True
        },
        'conversation_history': [],
        'language': language
    }
    
    print(f"\n{'='*80}\nTesting: {language} - {message[:40]}")
    print('='*80)
    
    try:
        r = requests.post(url, json=payload, timeout=30).json()
        
        print(f"✅ Success: {r.get('success')}")
        print(f"Scheme Detected: {r.get('matched_schemes')}")
        print(f"Voice Memory Clip: {r.get('voice_memory_clip')}")
        print(f"Audio Type: {r.get('audio_type')}")
        
        audio_url = r.get('audio_url', '')
        if audio_url:
            # Extract filename from URL
            filename = audio_url.split('/')[-1].split('?')[0]
            print(f"Audio Filename: {filename}")
            
            if 'voice_memory' in audio_url.lower():
                print("✅ VOICE MEMORY FILE DETECTED")
            else:
                print("❌ TTS FILE DETECTED (Not using voice memory)")
        else:
            print("❌ NO AUDIO URL")
        
        # Show response snippet
        print(f"\nResponse Preview: {r.get('response_text', '')[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Test cases
test_cases = [
    ('പിഎം കിസാൻ പറ്റി പറയൂ', 'ml-IN', 'PM_KISAN'),
    ('கிசான் கிरेডिट்', 'ta-IN', 'KCC'),
    ('പിഎം കിസാൻ', 'ml-IN', 'PM_KISAN'),
]

for message, language, expected in test_cases:
    test_api_response(message, language)

print('\n' + '='*80)
print("SUMMARY:")
print("If audio files contain 'voice_memory' in the filename, native speaker clips are being used ✅")
print("If audio files are UUID-based (TTS), falling back to text-to-speech ❌")
print('='*80)
