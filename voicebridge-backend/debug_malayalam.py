msg = 'പിഎം കിസാൻ പറ്റി പറയൂ'
m = msg.lower()

print(f"Message: {msg}")
print(f"Lowercase: {m}")
print(f"Are they equal? {msg == m}")

# Test if keywords are in the message
keywords = ['പിഎം കിസാൻ', 'കിസാൻ സമ്മാൻ', 'pm kisan', 'পীএম किसान']
for k in keywords:
    result = k in m
    print(f"'{k}' in message: {result}")
    
# Now test the actual detect_scheme function
def detect_scheme(msg):
    m = msg.lower()
    # PM_KISAN — Hindi + Malayalam + Tamil keywords
    if any(k in m for k in ['pm kisan','pmkisan','pm-kisan','kisan samman','6000','kisaan','पीएम किसान','पी एम किसान','pihem kisan','piem kisan','പി എം കിസാൻ','പിഎം കിസാൻ','കിസാൻ സമ്മാൻ','pm kisan','கிसான்','பிஎம் கிசான்','கிसान் சम्मान्']):
        return ['PM_KISAN'], 'PM_KISAN'
    return [], None

schemes, clip = detect_scheme(msg)
print(f"\ndetect_scheme result: schemes={schemes}, clip={clip}")
