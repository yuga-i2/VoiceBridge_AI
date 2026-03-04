#!/usr/bin/env python3
import unicodedata

# Test the Malayalam goodbye text
text = "കോൾ അവസാനിപ്പിക്കും"
text_lower = text.lower()

print(f"Original: {text}")
print(f"Lowered: {text_lower}")
print(f"'കെ' in text_lower: {'കെ' in text_lower}")
print(f"'സ' in text_lower: {'സ' in text_lower}")
print(f"'ക' in text_lower: {'ക' in text_lower}")
print()

# Character breakdown
print("Character breakdown:")
for i, char in enumerate(text):
    try:
        name = unicodedata.name(char)
    except ValueError:
        name = "?"
    print(f"{i}: {char} (U+{ord(char):04X}) - {name}")

print("\n=== Testing detect_kcc_in_message logic ===")

def detect_kcc_in_message(msg_lower):
    # Malayalam: detect common substrings in KCC variations
    if 'കെ' in msg_lower and 'സ' in msg_lower:
        print(f"  Both 'കെ' and 'സ' found in message")
        parts = msg_lower.split()
        for part in parts:
            if 'കെ' in part and 'സ' in part:
                print(f"  Both in same word: {part}")
                return True
    print("  KCC check passed")
    return False

result = detect_kcc_in_message(text_lower)
print(f"detect_kcc_in_message result: {result}")

# Also test with actual KCC text
print("\n=== Testing with actual KCC text ===")
kcc_text = "കെ സി സി പറ്റി"
kcc_lower = kcc_text.lower()
print(f"KCC text: {kcc_text}")
print(f"'കെ' in kcc_lower: {'കെ' in kcc_lower}")
print(f"'സ' in kcc_lower: {'സ' in kcc_lower}")
result2 = detect_kcc_in_message(kcc_lower)
print(f"detect_kcc_in_message result for KCC: {result2}")
