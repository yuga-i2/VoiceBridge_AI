"""Test detect_scheme function with multilingual inputs"""

def detect_scheme(msg):
    m = msg.lower()
    # PM_KISAN — Hindi + Malayalam + Tamil keywords
    if any(k in m for k in ['pm kisan','pmkisan','pm-kisan','kisan samman','6000','kisaan','पीएम किसान','पी एम किसान','pihem kisan','piem kisan','പി എം കിസാൻ','പിഎം കിസാൻ','കിസാൻ സമ്മാൻ','pm kisan','கிசான்','பிஎம் கிசான்','கிசான் சம्మാൻ']):
        return ['PM_KISAN'], 'PM_KISAN'
    if any(k in m for k in ['kcc','kisan credit','credit card','kisan card','4%','4 percent','सीसीसी','केसीसी','si si si','see see see','kisan lon','kisan loan','4 pratishat','കിസാൻ ക്രെഡിറ്റ്','കെ സി സി','കെസിസി','कि सान् कि रे डि ट्','केसिसी']):
        return ['KCC'], 'KCC'
    if any(k in m for k in ['pmfby','fasal bima','crop insurance','bima yojana','fasal insurance','फसल बीमा','piem ef bi','fasal bima yojana','ഫസൽ ബീമ','വിള ഇൻഷുറൻസ്','പിഎംഎഫ്ബിവൈ','பயிர் काप्पीडु','पि एम एफ पि ओ वाय्']):
        return ['PMFBY'], 'PMFBY'
    return [], None

# Test cases
tests = [
    ('പിഎം കിസാൻ', 'Malayalam PM_KISAN'),
    ('கிசான்', 'Tamil Kisaan'),
    ('pm kisan', 'English PM KISAN'),
    ('फसल बीमा', 'Hindi PMFBY'),
]

print("Testing detect_scheme() function:\n")
for msg, desc in tests:
    schemes, clip = detect_scheme(msg)
    status = '✅' if schemes else '❌'
    print(f"{status} {desc:30s} → Schemes: {schemes}, Clip: {clip}")
