import json

# Simulate receiving Malayalam message as JSON (like Flask would)
json_str = '{"message": "പിഎം കിസാൻ പറ്റി പറയൂ"}'
data = json.loads(json_str)
message = data['message']

print(f"Message from JSON: {message}")
print(f"Message repr: {repr(message)}")

# Check if the keyword is in the message
keyword = 'പിഎം കിസാൻ'
print(f"Keyword: {keyword}")
print(f"Keyword repr: {repr(keyword)}")
print(f"Keyword in message: {keyword in message}")
print()

# Now test the detect_scheme function with the JSON-parsed message
def detect_scheme(msg):
    m = msg.lower()
    # PM_KISAN — Hindi + Malayalam + Tamil keywords
    keywords = ['pm kisan','pmkisan','pm-kisan','kisan samman','6000','kisaan','पीएम किसान','पी एम किसान','pihem kisan','piem kisan','പി എം കിസാൻ','പിഎം കിസാൻ','കിസാൻ സമ്മാൻ','pm kisan','கிсaan்','பிஎம் கிசான்','किसान् समmaan्']
    
    for k in keywords:
        if k in m:
            print(f"  Match found: '{k}'")
            return ['PM_KISAN'], 'PM_KISAN'
    
    print(f"  No match found")
    return [], None

print("Testing detect_scheme with JSON-parsed message:")
schemes, clip = detect_scheme(message)
print(f"Result: schemes={schemes}, clip={clip}")
