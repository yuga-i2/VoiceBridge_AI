#!/usr/bin/env python3
"""
Comprehensive testing of goodbye detection and scheme detection across all languages.
"""
import unicodedata

def _detect_goodbye_intent(message: str, response_text: str) -> bool:
    """Test version with full Unicode normalization"""
    message_norm = unicodedata.normalize('NFC', message)
    response_norm = unicodedata.normalize('NFC', response_text)
    msg_lower = message_norm.lower()
    resp_lower = response_norm.lower()
    
    goodbye_keywords = [
        # ENGLISH
        'bye', 'goodbye', 'done', 'enough', 'stop', 'thanks', 'thank you', 
        'ok bye', 'bye now', 'see you', 'take care', 'this is enough',
        'i don\'t have anything to ask', 'i dont have anything to ask anymore',
        'i don\'t want to know anymore', 'i dont want to know anymore',
        
        # HINDI
        'बाय', 'अलविदा', 'जाना है', 'खत्म', 'कॉल खत्म', 'धन्यवाद',
        'कॉल कम करो', 'यह काफी है', 'मुझे और कुछ नहीं पूछना',
        
        # TAMIL
        'பை', 'வாழ்க', 'இது போதும்', 'எனக்கு கேட்க ஒன்றுமில்லை',
        
        # KANNADA
        'ವಿದಾ', 'ಧನ್ಯವಾದ', 'ಇದು ಸಾಕು', 'ನನಗೆ ಪ್ರಶ್ನೆಗಳು ಇಲ್ಲ',
        
        # MALAYALAM
        'കോൾ അവസാനിപ്പിക്കും', 'കോൾ അവസാനം', 'നന്ദി',
        'ഇത് മതി', 'എനിക്കൊരു ചോദ്യവും ഇല്ല'
    ]
    
    goodbye_keywords_norm = [unicodedata.normalize('NFC', kw) for kw in goodbye_keywords]
    
    for kw in goodbye_keywords_norm:
        try:
            if ord(kw[0]) > 127:  # Non-ASCII
                if kw in message_norm:
                    return True
            elif kw.lower() in msg_lower:
                return True
        except:
            pass
    
    return False

def detect_scheme(msg):
    """Test version of scheme detection"""
    m = msg.lower()
    
    if any(k in m for k in ['pm kisan','pmkisan','₹6000','₹ 6000','6000','கிசான்']):
        return 'PM_KISAN'
    if any(k in m for k in ['kcc','kisan credit','credit card','கிறெடிட் கார்ட்','கிసான் கிறெடிட்']):
        return 'KCC'
    if any(k in m for k in ['pmfby','fasal bima','crop insurance','பயிர் காப்பீடு']):
        return 'PMFBY'
    
    return None

# Test cases
test_cases = [
    # ENGLISH
    ("i dont have anything to ask anymore", True, "English - ambiguous goodbye"),
    ("i dont want to know anymore", True, "English - ambiguous goodbye"),
    ("this is enough", True, "English - enough"),
    ("bye", True, "English - bye"),
    
    # HINDI
    ("कॉल कम करो", True, "Hindi - call cut"),
    ("यह काफी है", True, "Hindi - enough"),
    ("मुझे और कुछ नहीं पूछना है", True, "Hindi - nothing to ask"),
    
    # TAMIL
    ("இது போதும்", True, "Tamil - enough"),
    ("வாழ்க", True, "Tamil - goodbye"),
    ("பை", True, "Tamil - bye"),
    ("எனக்கு நன்றி", True, "Tamil - thanks"),
    
    # KANNADA
    ("ವಿದಾ", True, "Kannada - goodbye"),
    ("ಇದು ಸಾಕು", True, "Kannada - enough"),
    ("ನನಗೆ ಪ್ರಶ್ನೆಗಳು ಇಲ್ಲ", True, "Kannada - no questions"),
    
    # MALAYALAM
    ("കോൾ അവസാനിപ്പിക്കും", True, "Malayalam - goodbye"),
    ("ഇത് മതി", True, "Malayalam - enough"),
    ("എനിക്കൊരു ചോദ്യവും ഇല്ല", True, "Malayalam - no questions"),
    
    # SCHEME DETECTION
    ("PM_KISAN பற்றி கூறு", "PM_KISAN", "Tamil PM_KISAN"),
    ("KCC கிறெடிட் கார্ட் பற்றி", "KCC", "Tamil KCC"),
    ("பயிர් காப்பீடு", "PMFBY", "Tamil PMFBY"),
]

print("=" * 80)
print("TESTING GOODBYE DETECTION & SCHEME DETECTION")
print("=" * 80)

goodbye_passed = 0
goodbye_failed = 0
scheme_passed = 0
scheme_failed = 0

for test_input, expected, description in test_cases:
    if isinstance(expected, bool):
        result = _detect_goodbye_intent(test_input, "response")
        status = "✓" if result == expected else "✗"
        if result == expected:
            goodbye_passed += 1
        else:
            goodbye_failed += 1
        print(f"{status} {description}")
        print(f"   Input: {test_input}")
        print(f"   Expected: {expected}, Got: {result}")
    else:
        result = detect_scheme(test_input)
        status = "✓" if result == expected else "✗"
        if result == expected:
            scheme_passed += 1
        else:
            scheme_failed += 1
        print(f"{status} {description}")
        print(f"   Input: {test_input}")
        print(f"   Expected: {expected}, Got: {result}")
    print()

print("=" * 80)
print(f"GOODBYE DETECTION: {goodbye_passed} passed, {goodbye_failed} failed")
print(f"SCHEME DETECTION: {scheme_passed} passed, {scheme_failed} failed")
print(f"TOTAL: {goodbye_passed + scheme_passed} passed, {goodbye_failed + scheme_failed} failed")
print("=" * 80)
