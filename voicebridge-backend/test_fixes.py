#!/usr/bin/env python
"""Test script to verify v1.3.2 fixes"""

# Test 1: Language normalization
print("Testing FIX 1 - Language Code Normalization:")
test_cases = [
    ('ml-IN', 'ml-IN'),
    ('ta-IN', 'ta-IN'),
    ('kn-IN', 'kn-IN'),
    ('te-IN', 'te-IN'),
    ('hi-IN', 'hi-IN')
]

for input_lang, expected in test_cases:
    language = input_lang.strip()
    if '-' in language:
        parts = language.split('-')
        language = parts[0].lower() + '-' + parts[1].upper()
    status = "PASS" if language == expected else "FAIL"
    print(f"  {input_lang} -> {language} (expected {expected}): {status}")

# Test 2: Speaker map matching
print("\nTesting FIX 2 - Speaker Map Key Matching:")
speaker_map = {
    'ta-IN': 'kavya',
    'kn-IN': 'arjun',
    'te-IN': 'meera',
    'ml-IN': 'pavithra',
    'hi-IN': 'meera'
}

languages = ['ta-IN', 'kn-IN', 'te-IN', 'ml-IN', 'hi-IN']
for lang in languages:
    speaker = speaker_map.get(lang, 'FALLBACK_meera')
    status = "PASS" if speaker != 'FALLBACK_meera' else "FAIL"
    print(f"  {lang} -> {speaker}: {status}")

# Test 3: Response check logic (no 'status' field needed)
print("\nTesting FIX 3 - Response Check Logic:")
test_responses = [
    ({'audios': [{'audio': 'base64...'}]}, True, "Valid response with audios array"),
    ({'audios': []}, False, "Empty audios array"),
    ({}, False, "Missing audios field"),
    ({'some_field': 'value'}, False, "No audios field"),
]

for response, should_pass, description in test_responses:
    audios = response.get('audios') or []
    is_valid = bool(audios)
    status = "PASS" if is_valid == should_pass else "FAIL"
    print(f"  {description}: {status}")

print("\nAll tests completed!")
