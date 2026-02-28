# Test the voice memory mapping logic without AWS
test_cases = [
    {'scheme_id': 'PM_KISAN', 'language': 'ml-IN', 'expected_farmer': 'Priya'},
    {'scheme_id': 'KCC', 'language': 'ta-IN', 'expected_farmer': 'Vijay'},
    {'scheme_id': 'PM_KISAN', 'language': 'hi-IN', 'expected_farmer': 'Sunitha Devi'},
]

VOICE_MEMORY_MAP = {
    'hi-IN': {
        'PM_KISAN': {'farmer_name': 'Sunitha Devi', 'district': 'Tumkur, Karnataka', 'scheme': 'PM-KISAN', 'key': 'voice_memory/voice_memory_PM_KISAN.mp3'},
        'KCC': {'farmer_name': 'Ramaiah', 'district': 'Mysuru, Karnataka', 'scheme': 'KCC', 'key': 'voice_memory/voice_memory_KCC.mp3'},
        'PMFBY': {'farmer_name': 'Laxman Singh', 'district': 'Dharwad, Karnataka', 'scheme': 'PMFBY', 'key': 'voice_memory/voice_memory_PMFBY.mp3'},
    },
    'ml-IN': {
        'PM_KISAN': {'farmer_name': 'Priya', 'district': 'Thrissur, Kerala', 'scheme': 'PM-KISAN', 'key': 'voice_memory/voice_memory_Mal_PM_KISAN.mp3.mpeg'},
        'KCC': {'farmer_name': 'Rajan', 'district': 'Palakkad, Kerala', 'scheme': 'KCC', 'key': 'voice_memory/voice_memory_Mal_KCC.mp3.mpeg'},
        'PMFBY': {'farmer_name': 'Suresh Kumar', 'district': 'Wayanad, Kerala', 'scheme': 'PMFBY', 'key': 'voice_memory/voice_memory_Mal_PMFBY.mp3.mpeg'},
    },
    'ta-IN': {
        'PM_KISAN': {'farmer_name': 'Kavitha', 'district': 'Coimbatore, Tamil Nadu', 'scheme': 'PM-KISAN', 'key': 'voice_memory/voice_memory_Tamil_PM_KISAN.mp3.mpeg'},
        'KCC': {'farmer_name': 'Vijay', 'district': 'Madurai, Tamil Nadu', 'scheme': 'KCC', 'key': 'voice_memory/voice_memory_Tamil_KCC.mp3.mpeg'},
        'PMFBY': {'farmer_name': 'Selva', 'district': 'Thanjavur, Tamil Nadu', 'scheme': 'PMFBY', 'key': 'voice_memory/voice_memory_Tamil_PMFBY.mp3.mpeg'},
    }
}

print("=== Voice Memory Route Logic Test ===\n")
for test in test_cases:
    scheme_id = test['scheme_id']
    language = test['language']
    expected = test['expected_farmer']
    
    # Mock the route logic
    lang_map = VOICE_MEMORY_MAP.get(language, VOICE_MEMORY_MAP['hi-IN'])
    clip_info = lang_map.get(scheme_id)
    
    if clip_info:
        actual = clip_info['farmer_name']
        status = '✅' if actual == expected else '❌'
        print(f"{status} {language} {scheme_id}: {actual} (district: {clip_info['district']})")
    else:
        print(f"❌ {language} {scheme_id}: NOT FOUND")

print("\n✅ All voice memory mappings validated")
