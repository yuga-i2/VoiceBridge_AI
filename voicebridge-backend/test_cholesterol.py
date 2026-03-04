#!/usr/bin/env python3
import unicodedata

# Test cholesterol text
text = "കോളസ്ട്രോൾ"
print(f"Text: {text}")
print(f"'കെ' in text: {'കെ' in text}")
print(f"'സ' in text: {'സ' in text}")
print()

# Check each character
for i, char in enumerate(text):
    try:
        name = unicodedata.name(char)
    except:
        name = "?"
    print(f"{char} (U+{ord(char):04X})")
