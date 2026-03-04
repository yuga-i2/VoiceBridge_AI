#!/usr/bin/env python3
"""
Test goodbye detection with Unicode normalization to ensure
it works properly for all languages including Malayalam.
"""
import unicodedata

def _detect_goodbye_intent_old(message: str, response_text: str) -> bool:
    """Old version without Unicode normalization"""
    msg_lower = message.lower()
    resp_lower = response_text.lower()
    
    goodbye_keywords = [
        'കോൾ അവസാനിപ്പിക്കാം', 'കോൾ അവസാനിപ്പിക്കും', 'കോൾ അവസാനം', 'നിലയ്ക്കാം', 'നിന്നുപോകാം',
        'कॉल कम करो', 'अलविदा', 'bye',
    ]
    
    for kw in goodbye_keywords:
        try:
            if ord(kw[0]) > 127:  # Non-ASCII
                if kw in message:
                    return True
            elif kw.lower() in msg_lower:
                return True
        except Exception:
            pass
    
    return False

def _detect_goodbye_intent_new(message: str, response_text: str) -> bool:
    """New version with Unicode normalization"""
    # Normalize to NFC
    message_norm = unicodedata.normalize('NFC', message)
    response_norm = unicodedata.normalize('NFC', response_text)
    msg_lower = message_norm.lower()
    resp_lower = response_norm.lower()
    
    goodbye_keywords = [
        'കോൾ അവസാനിപ്പിക്കാം', 'കോൾ അവസാനിപ്പിക്കും', 'കോൾ അവസാനം', 'നിലയ്ക്കാം', 'നിന്നുപോകാം',
        'कॉल कम करो', 'अलविदा', 'bye',
    ]
    
    goodbye_keywords_norm = [unicodedata.normalize('NFC', kw) for kw in goodbye_keywords]
    
    for kw in goodbye_keywords_norm:
        try:
            if ord(kw[0]) > 127:  # Non-ASCII
                if kw in message_norm:
                    return True
            elif kw.lower() in msg_lower:
                return True
        except Exception:
            pass
    
    return False

# Test cases
test_cases = [
    ("കോൾ അവസാനിപ്പിക്കും", "response", True, "Malayalam goodbye 1"),
    ("കോൾ അവസാനിപ്പിക്കാം", "response", True, "Malayalam goodbye 2"),
    ("കോൾ അവസാനം", "response", True, "Malayalam goodbye 3"),
    ("കോൾ അവസാനിപ്പിക്കുന്നു", "response", False, "Malayalam not goodbye"),
    ("कॉल कम करो", "response", True, "Hindi goodbye"),
    ("bye", "response", True, "English goodbye"),
    ("പിഎം കിസാൻ പറ്റി", "response", False, "Malayalam not goodbye"),
]

print("Testing goodbye detection...")
print("=" * 80)

for message, response, expected, description in test_cases:
    old_result = _detect_goodbye_intent_old(message, response)
    new_result = _detect_goodbye_intent_new(message, response)
    
    status = "✓" if new_result == expected else "✗"
    print(f"{status} {description}")
    print(f"  Message: {message}")
    print(f"  Old: {old_result}, New: {new_result}, Expected: {expected}")
    if old_result != new_result:
        print(f"  ⚠ CHANGE: {old_result} → {new_result}")
    print()
