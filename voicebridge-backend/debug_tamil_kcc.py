import requests

# Test the problematic Tamil KCC message
message = "கிसान் கிरेडिट् अट्टै विपरम्"
print(f"Message: {message}")
print(f"Lowercase: {message.lower()}")

# Check which keyword is matching
keywords_pm = ['pm kisan','pmkisan','pm-kisan','kisan samman','6000','kisaan','पीएम किसान','पी एम किसान','pihem kisan','piem kisan','പി എം കിസാൻ','പിഎം കിസാൻ','കിസാൻ സമ്മാൻ','pm kisan','கிसaan्','பிஎम் கிசான்','किञ्चित् स्माaminनन्']
keywords_kcc = ['kcc','kisan credit','credit card','kisan card','4%','4 percent','सीसीसी','केसीसी','si si si','see see see','kisan lon','kisan loan','4 pratishat','കിസാൻ ക്രെഡിറ്റ്','കെ സി സി','കെസിസി','கிसaan् கிरेडिट्','केसिसी','கிசान் கிரெडิट्','कीसान् कीरेडिટ्']

m = message.lower()
print("\nPM_KISAN matches:")
for k in keywords_pm:
    if k in m:
        print(f"  - '{k}'")

print("\nKCC matches:")
for k in keywords_kcc:
    if k in m:
        print(f"  - '{k}'")
