"""Test multilingual keyword detection - output safe version"""
import sys

# Test the detect_scheme function
def test_detection():
    def detect_scheme(msg):
        m = msg.lower()
        if any(k in m for k in ['pm kisan','pmkisan','pm-kisan','kisan samman','6000','kisaan','पीएम किसान','पी एम किसान','pihem kisan','piem kisan','പി എം കിസാൻ','പിെം കിസാൻ','കിസാൻ സമ്മാൻ','pm kisan','கிசான்','பிএம் கிசான்','கிसान् सम्मान्']):
            return ['PM_KISAN'], 'PM_KISAN'
        if any(k in m for k in ['kcc','kisan credit','credit card','kisan card','4%','4 percent','सीसीसी','केसीसी','si si si','see see see','kisan lon','kisan loan','4 pratishat','കിസാൻ ക്രെഡിറ്റ്','കെ സി സി','കെസിസി','கிสान् कि रे डि ट्','केसिसी']):
            return ['KCC'], 'KCC'
        if any(k in m for k in ['pmfby','fasal bima','crop insurance','bima yojana','fasal insurance','फसल बीमा','piem ef bi','fasal bima yojana','ഫസൽ ബീമ','വിള ഇൻഷുറൻസ്','പിെംഎഫ്ബിവൈ','பയির् काप्पीडु','पि एम एफ पि ओ वाय्']):
            return ['PMFBY'], 'PMFBY'
        return [], None

    tests = [
        ('pm kisan', 'ENGLISH: pm kisan'),
        ('पीएम किसान', 'HINDI: pim kisan'),
        ('കിസാൻ', 'MALAYALAM: part of word'),
        ('kcc', 'ENGLISH: kcc'),
        ('pmfby', 'ENGLISH: pmfby'),
        ('fasal bima', 'ENGLISH: fasal bima'),
    ]
    
    print("Direct Function Test Results:")
    print("=" * 60)
    
    for msg, desc in tests:
        schemes, clip = detect_scheme(msg)
        status = "DETECTED" if schemes else "NOT DETECTED"
        print(f"{status:15} | {desc:30} | {schemes}")
    
    print("\n" + "=" * 60)
    print("Live API Tests:")
    print("=" * 60)
    
    import requests
    
    api_tests = [
        ({
            'message': 'pm kisan',
            'farmer_profile': {'name': 'Ramesh', 'land_acres': 2, 'state': 'Karnataka'},
            'conversation_history': [],
            'language': 'hi-IN'
        }, 'Hindi: pm kisan'),
        ({
            'message': 'kcc',
            'farmer_profile': {'name': 'Vijay', 'land_acres': 1.5, 'state': 'Tamil Nadu'},
            'conversation_history': [],
            'language': 'ta-IN'
        }, 'Tamil: kcc'),
        ({
            'message': 'fasal bima',
            'farmer_profile': {'name': 'Singh', 'land_acres': 3, 'state': 'Punjab'},
            'conversation_history': [],
            'language': 'hi-IN'
        }, 'Hindi: fasal bima'),
    ]
    
    for payload, desc in api_tests:
        try:
            r = requests.post(
                'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/chat',
                json=payload,
                timeout=10
            )
            result = r.json()
            schemes = result.get('matched_schemes', [])
            status = "DETECTED" if schemes else "NOT DETECTED"
            print(f"{status:15} | {desc:30} | {schemes}")
        except Exception as e:
            print(f"ERROR         | {desc:30} | {str(e)[:30]}")

if __name__ == '__main__':
    test_detection()
    print("\n✅ Test complete!")
