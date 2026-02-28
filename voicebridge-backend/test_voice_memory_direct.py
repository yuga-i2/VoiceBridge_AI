"""
Debug test for voice memory service
"""
import sys
sys.path.insert(0, '.')

from services.voice_memory_service import get_clip

# Test the voice memory service directly
languages = ['en-IN', 'ml-IN', 'ta-IN']
schemes = ['PM_KISAN', 'KCC', 'PMFBY']

print("Testing Voice Memory Service:\n")

for scheme in schemes:
    print(f"\n{scheme}:")
    for lang in languages:
        result = get_clip(scheme, lang)
        print(f"  {lang}: success={result['success']}, audio_url={'✅ Present' if result.get('audio_url') else '❌ Missing'}")
        if not result['success']:
            print(f"         Error: {result.get('error')}")
        else:
            print(f"         Farmer: {result.get('farmer_name')}")
            print(f"         District: {result.get('district')}")
