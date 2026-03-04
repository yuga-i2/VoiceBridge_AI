"""
VoiceBridge AI — AI Service
Generates Sahaya's Hindi responses using Bedrock (AWS) or mock data (development).
"""

import json
import re
import unicodedata
from decimal import Decimal
from config.settings import USE_MOCK, AWS_REGION, BEDROCK_MODEL_ID
from services.scheme_service import get_scheme_by_id
from models.farmer import FarmerProfile

if not USE_MOCK:
    import boto3


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal objects from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) if '.' in str(obj) else int(obj)
        return super().default(obj)


# Farmer success stories from Voice Memory Network — multilingual
FARMER_STORIES = {
    'hi-IN': {
        'PM_KISAN': 'Sunitha Devi',
        'KCC': 'Ramaiah',
        'PMFBY': 'Laxman Singh',
        'PM_KISAN_DETAIL': 'Sunitha Devi se Tumkur, Karnataka',
        'KCC_DETAIL': 'Ramaiah se Mysuru, Karnataka',
        'PMFBY_DETAIL': 'Laxman Singh se Dharwad, Karnataka'
    },
    'ml-IN': {
        'PM_KISAN': 'Priya',
        'KCC': 'Rajan',
        'PMFBY': 'Suresh Kumar',
        'PM_KISAN_DETAIL': 'Priya ji from Thrissur, Kerala',
        'KCC_DETAIL': 'Rajan ji from Palakkad, Kerala',
        'PMFBY_DETAIL': 'Suresh Kumar ji from Wayanad, Kerala'
    },
    'ta-IN': {
        'PM_KISAN': 'Kavitha',
        'KCC': 'Vijay',
        'PMFBY': 'Selva',
        'PM_KISAN_DETAIL': 'Kavitha ji from Coimbatore, Tamil Nadu',
        'KCC_DETAIL': 'Vijay ji from Madurai, Tamil Nadu',
        'PMFBY_DETAIL': 'Selva ji from Thanjavur, Tamil Nadu'
    }
}


SAHAYA_SYSTEM_PROMPT = """You are Sahaya, an expert Hindi-speaking AI welfare navigator for Indian farmers. You have deep knowledge of all government schemes and speak like a trusted village elder who genuinely cares.

You have access to this farmer's profile: {farmer_profile}
Use their name, land size, and state to personalize EVERY response.
Relevant scheme data: {scheme_data}

═══════════════════════════════
GOODBYE DETECTION (CRITICAL)
═══════════════════════════════

DETECT FAREWELL INTENT: If the farmer is trying to end the conversation:

English Keywords: "bye", "goodbye", "done", "thanks", "thank you", "take care", "that's all"

Hindi Keywords (हिंदी): "बाय", "अलविदा", "खत्म", "खत्म करो", "कॉल खत्म", "जाना है", "धन्यवाद", "सुक्रिया", "खुदा हाफिज"

Tamil Keywords (தமிழ்): "பை", "போகிறேன்", "நன்றி", "வாழ்க", "முடிந்தது", "செல்லலாम்", "பேசலாம்"

Kannada Keywords (ಕನ್ನಡ): "ವಿದಾ", "ಧನ್ಯವಾದ", "ಹೋಗು", "ಕರೆ ಮುಗಿಸಿ", "ಸಾಕು", "ಮುಗಿಸು"

Malayalam Keywords (മലയാളം): "കോൾ അവസാനം", "നന്ദി", "വാഴ്ക", "പോകാം", "പോകുന്നു", "കഴിഞ്ഞു", "നിർത്തൽ"

HOW TO RESPOND:
1. If CLEAR goodbye → Respond warmly with gratitude and wish them well
2. If UNCERTAIN → Ask: "Are you sure you want to end? Any other questions?"
3. NEVER just end abruptly — always acknowledge their farewell meaningfully

═══════════════════════════════
LANGUAGE & FARMER STORY RULE
═══════════════════════════════

CRITICAL: Match all farmer stories to the user's LANGUAGE and REGION.
NEVER mention a Hindi farmer (Sunitha Devi, Ramaiah, Laxman Singh) to Malayalam or Tamil users.
NEVER mention a Malayalam farmer to Hindi or Tamil users.
NEVER mention a Tamil farmer to Hindi or Malayalam users.

Use ONLY these farmers for the user's language:

If responding in Malayalam (ml-IN), use ONLY:
- PM-KISAN: "Priya ji from Thrissur, Kerala"  
- KCC: "Rajan ji from Palakkad, Kerala"
- PMFBY: "Suresh Kumar ji from Wayanad, Kerala"

If responding in Tamil (ta-IN), use ONLY:
- PM-KISAN: "Kavitha ji from Coimbatore, Tamil Nadu"
- KCC: "Vijay ji from Madurai, Tamil Nadu"  
- PMFBY: "Selva ji from Thanjavur, Tamil Nadu"

If responding in Hindi (hi-IN), use ONLY:
- PM-KISAN: "Sunitha Devi from Tumkur, Karnataka"
- KCC: "Ramaiah from Mysuru, Karnataka"
- PMFBY: "Laxman Singh from Dharwad, Karnataka"

WHENEVER you mention a farmer success story (any name except the user),
you MUST end that paragraph with exactly one of these transition lines
(choose the one matching the language you are responding in):

Hindi:    "आप अपने क्षेत्र के किसान की सफलता की कहानी सुन सकते हैं।"
Malayalam: "നിങ്ങളുടെ പ്രദേശത്തെ കർഷകന്റെ വിജയകഥ കേൾക്കാം।"
Tamil:    "உங்கள் பகுதியிலுள்ള விവసായியின் வெற்றிக் கதையை கேளுங்கள്।"

═══════════════════════════════
CONVERSATION STAGES — follow in order
═══════════════════════════════

STAGE 1 — OPENING (first message only):
Greet using farmer's name from profile. Then show scheme menu.
Example:
"Namaste {name} ji! Main Sahaya hoon — aapki sarkari yojana sahayak.
Aaj main aapko inn yojanaon ke baare mein bata sakti hoon:
- PM-KISAN — ₹6,000 saal mein seedha bank mein
- KCC — sirf 4% byaaj par kisan loan
- PMFBY — fasal bima, nuksan hone par bhi paisa milega
Aap kaunsi yojana ke baare mein jaanna chahte hain?"

STAGE 2 — SCHEME INTRODUCTION (when farmer picks a scheme):
Use farmer profile to make it personal. 3 sentences maximum:
- Sentence 1: Personalized benefit — mention their specific situation
  Example for PM_KISAN with 2 acres: 
  "Ramesh ji, aapke 2 acre zameen ke saath aap PM-KISAN ke liye 
   bilkul eligible hain — ₹6,000 seedha aapke bank mein aayenge."

- Sentence 2: Farmer story from nearby region (builds trust):
  
  FARMER STORY INSTRUCTION (STRICT):
  When mentioning a farmer success story, keep it to ONE short sentence only.
  Just say who they are, where they are from, and that they got approved.
  Then immediately say the transition line. Nothing more.
  
  FORMAT (strictly follow this):
  [Farmer name] ജി [location] ൽ നിന്ന് [scheme name] അംഗീകരിച്ചു. നിങ്ങളുടെ പ്രദേശത്തെ കർഷകന്റെ വിജയകഥ കേൾക്കാം.
  
  Examples by language:
  
  Malayalam:
  - PM_KISAN: "തൃശ്ശൂരിൽ നിന്നുള്ള പ്രിയ ജിക്ക് പി എം കിസാൻ അംഗീകരിച്ചു. നിങ്ങളുടെ പ്രദേശത്തെ കർഷകന്റെ വിജയകഥ കേൾക്കാം."
  - KCC: "പാലക്കാട്ടിൽ നിന്നുള്ള രാജൻ ജിക്ക് KCC അംഗീകരിച്ചു. നിങ്ങളുടെ പ്രദേശത്തെ കർഷകന്റെ വിജയകഥ കേൾക്കാം."
  - PMFBY: "വയനാട്ടിൽ നിന്നുള്ള സുരേഷ് കുമാർ ജിക്ക് PMFBY അംഗീകരിച്ചു. നിങ്ങളുടെ പ്രദേശത്തെ കർഷകന്റെ വിജയകഥ കേൾക്കാം."
  
  Tamil:
  - PM_KISAN: "கோயம்புத்தூரிலிருந்து கவிதா ஜிக்கு PM-KISAN அங்கீகரிக்கப்பட்டது. உங்கள் பகுதியிலுள்ள விவசாயியின் வெற்றிக் கதையை கேளுங்கள்."
  - KCC: "மதுரையிலிருந்து விஜய் ஜிக்கு KCC அங்கீகரிக்கப்பட்டது. உங்கள் பகுதியிலுள்ள விவசாயியின் வெற்றிக் கதையை கேளுங்கள்."
  - PMFBY: "தஞ்சாவூரிலிருந்து செல்வா ஜிக்கு PMFBY அங்கீகரிக்கப்பட்டது. உங்கள் பகுதியிலுள்ள விவசாயியின் வெற்றிக் கதையை கேளுங்கள்."
  
  Hindi:
  - PM_KISAN: "तुमकुर की सुनीता देवी जी को PM-KISAN मंज़ूर हुआ। आप अपने क्षेत्र के किसान की सफलता की कहानी सुन सकते हैं।"
  - KCC: "मैसूर के रमैया जी को KCC मंज़ूर हुआ। आप अपने क्षेत्र के किसान की सफलता की कहानी सुन सकते हैं।"
  - PMFBY: "धारवाड़ के लक्ष्मण सिंह जी को PMFBY मंज़ूर हुआ। आप अपने क्षेत्र के किसान की सफलता की कहानी सुन सकते हैं।"
  
  RULES:
  - ONE sentence about farmer maximum
  - NEVER say what they did with the money
  - NEVER say how much they received  
  - ALWAYS end with the transition line in the correct language
  - NEVER use Hindi farmer names when speaking Malayalam or Tamil

- Sentence 3: Soft call to action:
  "Kya aap jaanna chahte hain ki aap kaise apply kar sakte hain?"

STAGE 3 — DEEPER DETAILS (only when farmer says yes/asks more):
Give ONE piece of info at a time. Choose the most important:
- If they seem ready: tell them WHERE to apply (CSC center)
- If they seem unsure: tell them the MAIN document needed
- If they ask cost: reassure them it is FREE to apply
Never dump all information at once. One thing, then ask:
"Aur koi sawaal hai?"

STAGE 4 — OBJECTION HANDLING (if farmer seems hesitant):
Common objections and how to handle them:
- "Itna mushkil lagta hai" → 
  "Bilkul nahi {name} ji — sirf ek baar CSC center jaana hai, 
   wahan sab ho jaata hai. 30 minute ka kaam hai."
- "Pehle try kiya tha nahi mila" →
  "Yeh problem bahut logon ko hoti hai. Galat jagah apply karte hain. 
   Main aapko sahi tarika bataati hoon."
- "Mujhe nahi pata kahan jaana hai" →
  "Aapke sabse nazdiki Common Service Centre mein jaayein — 
   wahan free mein apply ho jaata hai."

STAGE 5 — CLOSING (when farmer seems satisfied):
"Bahut accha {name} ji! Yaad rakhein — [one key action item].
Koi bhi sawaal ho toh Sahaya hamesha yahan hai."

═══════════════════════════════
PERSONALIZATION RULES
═══════════════════════════════
- ALWAYS use farmer's name from profile ({farmer_profile.name})
- If land_acres < 2: emphasize small farmer benefits
- If has_kcc is false: always mention KCC as next suggestion
- If has_bank_account is false: first tell them to open bank account
- Match farmer stories to their state when possible

═══════════════════════════════
STRICT RESPONSE RULES
═══════════════════════════════
1. Maximum 3 sentences per response — no exceptions
2. Always in Hindi Devanagari script
3. Never repeat information already given in this conversation
4. Never list multiple documents or steps at once
5. Never use bullet points mid-conversation — only in opening menu
6. End EVERY response with either a question or a clear next action
7. If farmer goes off-topic: answer briefly then redirect to schemes
8. Never sound like a government brochure — sound like a caring neighbor

═══════════════════════════════
ANTI-SCAM TRUST BUILDING
═══════════════════════════════
If farmer asks if this is real or expresses suspicion:
"Main Sahaya hoon — ek AI sahayak. Main aapka koi bhi personal 
data nahi maangti. Koi OTP, password ya Aadhaar number kabhi mat 
dena kisi ko bhi. Yeh service bilkul free hai."

FARMER PROFILE: {farmer_profile}
SCHEME DATA: {scheme_data}
CONVERSATION HISTORY: {conversation_history}"""


MOCK_RESPONSES = {
    "greeting": """नमस्ते! मैं साहया हूँ। मैं आपको सरकार की किसान योजनाओं के बारे में बताने के लिए कॉल करी हूँ। 
मैं कभी भी आपसे OTP या आधार नंबर नहीं माँगूँगी। अगर आप संदेह में हैं तो *123*CHECK# डायल करके पता लगा सकते हैं।
आपके पास कितने एकड़ खेत हैं?""",
    
    "pm_kisan": """PM-किसान एक बहुत अच्छी योजना है! आपको हर साल ₹6,000 मिलते हैं - यानी तीन बार ₹2,000।
यह सीधे आपके बैंक खाते में आता है। आपको बस अपने आधार को बैंक खाते से जोड़ना है।
Common Service Centre पर जाएँ या pmkisan.gov.in पर देखें।
[PLAY_VOICE_MEMORY:PM_KISAN]""",
    
    "kcc": """Kisan Credit Card बहुत मददगार है! इससे आप ₹3 लाख तक का लोन ले सकते हैं।
ब्याज दर सिर्फ 4% है - बहुत कम! किसी भी बैंक की शाखा में जाएँ और आवेदन करें।
आपको अपने खेत के कागजात और ID की जरूरत होगी।
[PLAY_VOICE_MEMORY:KCC]""",
    
    "pmfby": """फसल बीमा योजना आपकी फसल को सुरक्षित रखता है! अगर बारिश या कीट से नुकसान हो तो पूरा पैसा मिल जाता है।
खरीफ फसल के लिए सिर्फ 2% premium है, और रबी के लिए 1.5%।
पंचायत या बैंक में जाकर रजिस्ट्रेशन करवा दें।
[PLAY_VOICE_MEMORY:PMFBY]""",
    
    "ayushman": """आयुष्मान भारत बहुत बड़ी स्वास्थ्य योजना है! आपको और आपके परिवार को ₹5 लाख का health insurance मिलता है।
किसी भी सरकारी अस्पताल में मुफ्त इलाज करवा सकते हैं।
pmjay.gov.in पर अपना नाम देख सकते हैं कि आप eligible हैं या नहीं।""",
    
    "mgnregs": """मनरेगा योजना से आपको साल में 100 दिन की नौकरी मिल सकती है! हर दिन ₹220 से ₹357 तक।
पहले अपने Gram Panchayat में job card बनवा लें। फिर काम करें और पैसा मिलता है।
यह योजना गाँव में ही काम देती है।""",
    
    "confused": """मुझे समझ नहीं आया। कृपया अपना सवाल फिर से बताइए।
क्या आप PM-किसान, KCC, या फसल बीमा के बारे में जानना चाहते हैं? कोई एक चुन लीजिए।""",
    
    "already_applied": """वाह! यह बहुत अच्छी बात है कि आपने आवेदन कर दिया है।
क्या आपको लाभ मिल गया? मैं आपको दूसरी योजनाओं में भी मदद कर सकती हूँ।""",
    
    "scam_concern": """बिल्कुल सही चिंता! मैं साहया हूँ, सरकार की ओर से कॉल कर रही हूँ।
मैं कभी आपसे पैसा नहीं माँगूँगी, OTP नहीं माँगूँगी, न ही आधार नंबर माँगूँगी।
अगर शक है तो *123*CHECK# डायल करके verify कर लीजिए। हम सब सच कहते हैं।"""
}


def _select_mock_response(message: str, scheme_ids: list[str]) -> str:
    """
    Selects appropriate mock response based on message and matched schemes.
    """
    message_lower = message.lower()
    
    # Check for greeting
    if any(word in message_lower for word in ["namaste", "hello", "नमस्ते", "हैलो", "hallo"]):
        return MOCK_RESPONSES["greeting"]
    
    # Check for scam concern
    if any(word in message_lower for word in ["scam", "fraud", "fake", "otp", "धोखा", "जाली"]):
        return MOCK_RESPONSES["scam_concern"]
    
    # Check for already applied
    if any(word in message_lower for word in ["already", "applied", "mil gaya", "मिल गया", "करदिया"]):
        return MOCK_RESPONSES["already_applied"]
    
    # Check scheme matches
    if "PM_KISAN" in scheme_ids:
        return MOCK_RESPONSES["pm_kisan"]
    if "KCC" in scheme_ids:
        return MOCK_RESPONSES["kcc"]
    if "PMFBY" in scheme_ids:
        return MOCK_RESPONSES["pmfby"]
    if "AYUSHMAN_BHARAT" in scheme_ids:
        return MOCK_RESPONSES["ayushman"]
    if "MGNREGS" in scheme_ids:
        return MOCK_RESPONSES["mgnregs"]
    
    # Default
    return MOCK_RESPONSES["confused"]


def get_voice_memory_clip(matched_schemes: list[str], message_text: str) -> str | None:
    """
    Returns voice memory clip ID if relevant scheme discussed.
    Checks matched schemes first, then falls back to message text keywords.
    Voice memory clips exist only for: PM_KISAN, KCC, PMFBY
    """
    clip_schemes = ['PM_KISAN', 'KCC', 'PMFBY']
    
    # Check matched schemes first (most reliable)
    if matched_schemes:
        for scheme in matched_schemes:
            if scheme in clip_schemes:
                return scheme
    
    # Fallback: check message text for keywords
    message_lower = message_text.lower()
    if any(k in message_lower for k in ['pm kisan', 'pm-kisan', 'kisan samman', 'pmkisan']):
        return 'PM_KISAN'
    if any(k in message_lower for k in ['kcc', 'kisan credit', 'credit card']):
        return 'KCC'
    if any(k in message_lower for k in ['pmfby', 'fasal bima', 'crop insurance', 'bima']):
        return 'PMFBY'
    
    return None


def _extract_voice_memory_tag(response_text: str) -> tuple[str, str | None]:
    """
    Extracts [PLAY_VOICE_MEMORY:X] tag from response.
    Returns tuple: (clean_text_without_tag, scheme_id_or_None)
    """
    pattern = r'\[PLAY_VOICE_MEMORY:([A-Z_]+)\]'
    match = re.search(pattern, response_text)
    
    if match:
        scheme_id = match.group(1)
        clean_text = re.sub(pattern, '', response_text).strip()
        return (clean_text, scheme_id)
    
    return (response_text, None)


def _build_bedrock_messages(
    message: str,
    history: list[dict],
    scheme_data: list[dict],
    farmer: FarmerProfile,
    matched_scheme: str = None,
    lang_instruction: str = None
) -> list[dict]:
    """
    Builds messages array for Bedrock Claude API.
    Injects scheme data and farmer profile into system prompt.
    Injects farmer story if matched scheme is PM_KISAN, KCC, or PMFBY.
    """
    # Inject data into system prompt - use custom encoder for Decimal objects
    scheme_data_str = json.dumps(scheme_data, ensure_ascii=False, indent=2, cls=DecimalEncoder)
    farmer_profile_str = json.dumps(farmer.to_dict(), ensure_ascii=False, indent=2)
    
    system_with_data = SAHAYA_SYSTEM_PROMPT.replace("{scheme_data}", scheme_data_str)
    system_with_data = system_with_data.replace("{farmer_profile}", farmer_profile_str)
    
    # Replace {name} placeholder with farmer's actual name
    farmer_name = farmer.name if hasattr(farmer, 'name') else 'Kisan bhai'
    system_with_data = system_with_data.replace("{name}", farmer_name)
    
    # Prepend language instruction if provided
    if lang_instruction:
        system_with_data = f"LANGUAGE INSTRUCTION (HIGHEST PRIORITY):\n{lang_instruction}\n\n{system_with_data}"
    
    # Inject farmer story if matched scheme has one
    if matched_scheme and matched_scheme in FARMER_STORIES:
        story = FARMER_STORIES[matched_scheme]
        farmer_story_context = f"\n\nFARMER STORY TO SHARE: {story['farmer']} ji ne kaha: '{story['story']}' — yeh {story['district']} se hai."
        system_with_data = system_with_data.replace(
            "{farmer_story}",
            f"{story['farmer']} ji ne kaha: '{story['story']}' — yeh {story['district']} se hai"
        )
        system_with_data = system_with_data.replace("{farmer_name}", story['farmer'])
        system_with_data = system_with_data.replace("{district}", story['district'])
        system_with_data += farmer_story_context
    
    # Build messages array
    messages = []
    
    # Add conversation history
    for item in (history or []):
        messages.append({
            "role": item.get("role", "user"),
            "content": item.get("content", "")
        })
    
    # Add current message
    messages.append({
        "role": "user",
        "content": message
    })
    
    return messages, system_with_data


def _detect_goodbye_intent(message: str, response_text: str) -> bool:
    """
    Detect if user is trying to end the conversation based on:
    1. User message keywords
    2. AI response indicating farewell/end
    
    Uses Unicode NFC normalization for consistent matching across regional scripts.
    """
    msg_lower = message.lower()
    resp_lower = response_text.lower()
    
    # Normalize input strings to NFC (handles Unicode variations in regional scripts)
    message_norm = unicodedata.normalize('NFC', message)
    response_norm = unicodedata.normalize('NFC', response_text)
    msg_lower = message_norm.lower()
    resp_lower = response_norm.lower()
    
    # Goodbye keywords in ALL supported languages with multiple variations
    goodbye_keywords = [
        # ============ ENGLISH ============
        'bye', 'goodbye', 'done', 'enough', 'stop', 'thanks', 'thank you', 
        'ok bye', 'bye now', 'see you', 'take care', 'that\'s all', 'that\'s it',
        'gotta go', 'need to go', 'have to go', 'see ya', 'catch you later',
        'end call', 'finish', 'complete', 'thanks bye', 'this is enough',
        'i don\'t have anything to ask', 'i dont have anything to ask anymore',
        'i don\'t want to know anymore', 'i dont want to know anymore', 'nothing more to ask',
        
        # ============ HINDI (हिंदी) ============
        'बाय', 'अलविदा', 'जाना है', 'खत्म', 'खत्म करो', 'कॉल खत्म',
        'धन्यवाद', 'सुक्रिया', 'खुदा हाफिज', 'फिर मिलेंगे',
        'कॉल अंत करो', 'कॉल बंद करो', 'बंद करो', 'बंद कर',
        'जाता हूं', 'जाती हूं', 'जाऊँ', 'जाते हैं', 'जाते हो',
        'अलग करो', 'विदा', 'नमस्ते', 'अच्छा बाय', 'यह काफी है',
        'मुझे और कुछ नहीं पूछना', 'मुझे और जानना नहीं है', 'पर्याप्त है',
        
        # ============ TAMIL (தமிழ்) ============
        'பை', 'வணக்கம்', 'நன்றி', 'போய்விடு', 'போனேன்', 'போகிறேன்',
        'பேச முடிந்தவ', 'பேசலாம்', 'முடிந்தது', 'வாழ்க',
        'என்ற கோல் முடிக்க', 'கோல் முடிக்கவும்', 'அவசியம் செல்ல',
        'அழைப்பு முடி', 'செல்கிறேன்', 'நன்றி சொல்', 'மீண்டு பார்ப்போம்',
        'இது போதும்', 'எனக்கு கேட்க ஒன்றுமில்லை', 'இனி தெரிந்து கொள்ள வேண்டாம்',
        
        # ============ KANNADA (ಕನ್ನಡ) ============
        'ವಿದಾ', 'ಹೌದು', 'ಸರಿ', 'ಧನ್ಯವಾದ', 'ಶುಕ್ರಿಯೆ', 'ನಮಸ್ಕಾರ',
        'ಹೋಗು', 'ಹೋಗಬೇಕು', 'ಹೋಗುತ್ತೀನಿ', 'ಕರೆ ಮುಗಿಸು',
        'ಕರೆ ಮುಗಿಸಿ', 'ಸಾಕು', 'ಮುಗಿಸು', 'ಮುಗಿದು',
        'ನಿಲ್ಲಿಸು', 'ನಿಲ್ಲಬೇಕು', 'ಸರಿ ವಿದಾ', 'ಹಾಗಾದರೆ ಬಾಯ್',
        'ಇದು ಸಾಕು', 'ನನಗೆ ಪ್ರಶ್ನೆಗಳು ಇಲ್ಲ', 'ನಾನು ಹೆಚ್ಚು ತಿಳಿಯಲು ಬಯಸುತ್ತೇನೆ ಇಲ್ಲ',
        
        # ============ TELUGU (తెలుగు) ============
        'బై', 'సరిగ్గా', 'ఆ విధంగా', 'ధన్యవాదాలు', 'దయచేసి', 'నమస్కారం',
        'వెళ్ళవలసిన', 'పోకూ', 'నా వెళ్ళాలి', 'కాల్‌ ముగించండి',
        'కాల్ ముగిసిన', 'సరిపడింది', 'ఆపండి', 'విరమిస్తుంది',
        'ఆపుకోండి', 'చాలు', 'ఖతమ్', 'థాంక్ యూ బై',
        'ఇది సరిపోతుంది', 'నాకు ఏ ప్రశ్నలు లేవు', 'నేను ఇకపై తెలుసుకోవడానికి కోరుకోను',
        
        # ============ MALAYALAM (മലയാളം) ============
        'കോൾ അവസാനിപ്പിക്കാം', 'കോൾ അവസാനിപ്പിക്കും', 'കോൾ അവസാനം', 'കോൾ കം കരോ', 'കോൾ കഴിയ്ക്കാം', 'നിർത്തൽ', 'ഓകെ', 'പോകാം',
        'പോണം', 'പോകുന്നു', 'പോകണം', 'പോയ്', 'പോയ്‌', 'ജാ', 'വാഴ്ക', 'നന്ദി', 'നന്ദി പറയുന്നു',
        'നിലയ്ക്കാം', 'നില്‍ക്കാം', 'നിന്നുപോകാം', 'നിൽപ്പിച്ചോ', 'നിൽപ്പിക്കാം', 'സാധിച്ചു',
        'സാരമായി തീരുന്നു', 'കഴിഞ്ഞു', 'കഴിയുന്നു', 'തീരണ്ടെ', 'തീരുമ്പോൾ', 'കെട്ടിപ്പോകാം', 'അവ്സാനിപ്പിക്കാം',
        'ഇത് മതി', 'എനിക്കൊരു ചോദ്യവും ഇല്ല', 'എനിക്കൂടെ കൂടുതൽ അറിയാൻ താത്പര്യമില്ല'
    ]
    
    # Check if any goodbye keyword is in the message (BETTER: handle non-ASCII properly)
    for kw in goodbye_keywords:
        try:
            # Normalize keyword to NFC for comparison
            kw_norm = unicodedata.normalize('NFC', kw)
            # For Hindi/regional scripts: exact match WITHOUT lowercasing
            if ord(kw[0]) > 127:  # Non-ASCII
                if kw_norm in message_norm:
                    # [GOODBYE] Matched Hindi/regional '{kw}' in message
                    return True
            # For English: case-insensitive
            elif kw.lower() in msg_lower:
                # [GOODBYE] Matched English '{kw}' in message
                return True
        except Exception:
            pass
    
    # Check if AI response indicates goodbye (phrases like "take care", "all the best", etc.)
    goodbye_response_phrases = [
        'धन्यवाद', 'take care', 'all the best', 'வாழ்க', 'നന്ദി', 'good luck',
        'ಧನ್ಯವಾದ', 'థాంకు', 'thanks', 'farewell', 'કોલ/call शેষ'
    ]
    
    # More aggressive detection: if user says goodbye word AND any "end" signal from AI
    for phrase in goodbye_response_phrases:
        if phrase.lower() in resp_lower and any(
            kw.lower() in msg_lower for kw in ['thanks', 'bye', 'done', 'धन्यवाद', 'നന്ദി', 'thank', 'okay', 'ok']
        ):
            return True
    
    # If message includes multiple confirmed goodbye words, it's definitely goodbye
    strong_goodbye_words = ['bye', 'बाय', 'போகிறேന्', 'വാഴ്ക', 'कॉल खत्म', 'अलविदा', 'കോൾ അവസാനം', 'കോൾ അവസാനിപ്പിക്കും', 'കഴിഞ്ഞു']
    strong_goodbye_count = 0
    for word in strong_goodbye_words:
        word_norm = unicodedata.normalize('NFC', word)
        if word_norm in message_norm or word.lower() in msg_lower:
            strong_goodbye_count += 1
    
    if strong_goodbye_count >= 2:
        return True
    
    return False


def generate_response(
    message: str,
    scheme_ids: list[str],
    farmer: FarmerProfile,
    conversation_history: list[dict] = None,
    lang_instruction: str = None
) -> dict:
    """
    Main function. Generates Sahaya's response.
    Returns dict with response_text, voice_memory_clip, matched_schemes, raw_response.
    Automatically selects farmer story for the first matched scheme if available.
    """
    try:
        if USE_MOCK:
            # Mock path
            raw_response = _select_mock_response(message, scheme_ids)
            clean_text, _ = _extract_voice_memory_tag(raw_response)
            is_goodbye = _detect_goodbye_intent(message, clean_text)
            
            # CRITICAL: Do NOT return voice clip if this is a goodbye message
            if is_goodbye:
                voice_clip = None
                # Also clear matched_schemes so frontend doesn't fetch voice memory
                final_schemes = []
            else:
                voice_clip = get_voice_memory_clip(scheme_ids, message)
                final_schemes = scheme_ids
            
            return {
                "success": True,
                "response_text": clean_text,
                "voice_memory_clip": voice_clip,
                "matched_schemes": final_schemes,
                "raw_response": raw_response,
                "is_goodbye": is_goodbye,
                "mock": True
            }
        
        else:
            # AWS path - call Bedrock
            client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
            
            # Get full scheme data for context
            scheme_data = []
            for scheme_id in scheme_ids:
                scheme = get_scheme_by_id(scheme_id)
                if scheme:
                    scheme_data.append(scheme)
            
            # Use first matched scheme for farmer story context (if available)
            primary_scheme = scheme_ids[0] if scheme_ids else None
            
            # Build messages with primary scheme context
            messages, system_final = _build_bedrock_messages(
                message,
                conversation_history or [],
                scheme_data,
                farmer,
                primary_scheme,
                lang_instruction
            )
            
            # Call Bedrock with correct Claude Messages API format
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "temperature": 0.7,
                "system": system_final,
                "messages": messages
            }
            
            response = client.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                body=json.dumps(request_body, cls=DecimalEncoder),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response["body"].read())
            raw_response = response_body["content"][0]["text"]
            
            # Extract clean text (remove tags if any)
            clean_text, _ = _extract_voice_memory_tag(raw_response)
            # Detect if user is saying goodbye FIRST
            is_goodbye = _detect_goodbye_intent(message, clean_text)
            
            # CRITICAL: Do NOT return voice clip if this is a goodbye message
            if is_goodbye:
                voice_clip = None
                # Also clear matched_schemes so frontend doesn't fetch voice memory
                final_schemes = []
            else:
                # Only get voice memory for scheme discussions (not goodbye)
                voice_clip = get_voice_memory_clip(scheme_ids, message)
                final_schemes = scheme_ids
            
            return {
                "success": True,
                "response_text": clean_text,
                "voice_memory_clip": voice_clip,
                "matched_schemes": final_schemes,
                "raw_response": raw_response,
                "is_goodbye": is_goodbye,
                "mock": False
            }
    
    except Exception as e:
        # On error, return mock confused response
        return {
            "success": False,
            "response_text": MOCK_RESPONSES["confused"],
            "voice_memory_clip": None,
            "matched_schemes": scheme_ids,
            "is_goodbye": False,
            "error": str(e),
            "mock": True
        }
