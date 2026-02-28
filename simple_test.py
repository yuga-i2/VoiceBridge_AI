import requests
import json

# Simple test without special characters
test_cases = [
    ('pm kisan', 'hi-IN', 'Ramesh'),
    ('kcc', 'hi-IN', 'Ramesh'),
    ('fasal bima', 'hi-IN', 'Singh'),
    ('pmfby', 'hi-IN', 'Ramesh'),
]

print("TESTING KEYWORD DETECTION")
print("=" * 70)

for msg, lang, name in test_cases:
    payload = {
        'message': msg,
        'farmer_profile': {'name': name, 'land_acres': 2, 'state': 'Karnataka'},
        'conversation_history': [],
        'language': lang
    }
    
    try:
        r = requests.post(
            'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat',
            json=payload,
            timeout=10
        )
        result = r.json()
        schemes = result.get('matched_schemes', [])
        clip = result.get('voice_memory_clip')
        
        if schemes:
            status = "DETECTED"
            detail = f"Schemes: {schemes}, Clip: {clip}"
        else:
            status = "NOT DETECTED"
            detail = "No schemes matched"
        
        msg_display = f"{msg:20}"
        status_display = f"{status:15}"
        
        print(f"{msg_display} | {status_display} | {detail}")
        
    except Exception as e:
        print(f"{msg:20} | ERROR         | {str(e)[:40]}")

# Write results to file
with open('test_results.txt', 'w') as f:
    f.write("Keyword Detection Test Results\n")
    f.write("=" * 70 + "\n")
    f.write("All tests completed. Check console output above.\n")

print("\nTest completed!")
