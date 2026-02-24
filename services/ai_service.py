"""
VoiceBridge AI — AI Service
Generates Sahaya's Hindi responses using Bedrock (AWS) or mock data (development).
"""

import json
import re
from config.settings import USE_MOCK, AWS_REGION, BEDROCK_MODEL_ID
from services.scheme_service import get_scheme_by_id
from models.farmer import FarmerProfile

if not USE_MOCK:
    import boto3


SAHAYA_SYSTEM_PROMPT = """You are Sahaya, a compassionate AI assistant helping rural Indian farmers access government welfare schemes.

RULES:
- Always respond in simple Hindi using Devanagari script.
- Use simple, everyday words. Not formal Hindi. Not English.
- Never ask for Aadhaar number, OTP, bank details, or passwords.
- Always be warm, patient, and encouraging.
- Farmers may be suspicious. Reassure them this is legitimate.
- Recommend ONLY schemes from SCHEME DATA provided.
- Never invent or change benefit amounts.
- If recommending PMFBY crop insurance, end response with exactly: [PLAY_VOICE_MEMORY:PMFBY]
- If recommending KCC, end response with exactly: [PLAY_VOICE_MEMORY:KCC]
- If recommending PM_KISAN, end response with exactly: [PLAY_VOICE_MEMORY:PM_KISAN]
- Keep responses under 150 words. Farmers are on a phone call.
- If farmer is confused, ask ONE simple question to clarify.
- If farmer says they got the benefit, congratulate them warmly."""


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
    farmer: FarmerProfile
) -> list[dict]:
    """
    Builds messages array for Bedrock Claude API.
    Injects scheme data and farmer profile into system prompt.
    """
    # Inject data into system prompt
    scheme_data_str = json.dumps(scheme_data, ensure_ascii=False, indent=2)
    farmer_profile_str = json.dumps(farmer.to_dict(), ensure_ascii=False, indent=2)
    
    system_with_data = SAHAYA_SYSTEM_PROMPT.replace("{scheme_data}", scheme_data_str)
    system_with_data = system_with_data.replace("{farmer_profile}", farmer_profile_str)
    
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


def generate_response(
    message: str,
    scheme_ids: list[str],
    farmer: FarmerProfile,
    conversation_history: list[dict] = None
) -> dict:
    """
    Main function. Generates Sahaya's response.
    Returns dict with response_text, voice_memory_clip, matched_schemes, raw_response.
    """
    try:
        if USE_MOCK:
            # Mock path
            raw_response = _select_mock_response(message, scheme_ids)
            clean_text, voice_clip = _extract_voice_memory_tag(raw_response)
            
            return {
                "success": True,
                "response_text": clean_text,
                "voice_memory_clip": voice_clip,
                "matched_schemes": scheme_ids,
                "raw_response": raw_response,
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
            
            # Build messages
            messages, system_final = _build_bedrock_messages(
                message,
                conversation_history or [],
                scheme_data,
                farmer
            )
            
            # Call Bedrock
            body = json.dumps({
                "messages": messages,
                "system": system_final,
                "max_tokens": 512,
                "temperature": 0.7
            })
            
            response = client.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                body=body
            )
            
            # Parse response
            response_body = json.loads(response["body"].read().decode("utf-8"))
            raw_response = response_body["content"][0]["text"]
            
            # Extract voice memory tag
            clean_text, voice_clip = _extract_voice_memory_tag(raw_response)
            
            return {
                "success": True,
                "response_text": clean_text,
                "voice_memory_clip": voice_clip,
                "matched_schemes": scheme_ids,
                "raw_response": raw_response,
                "mock": False
            }
    
    except Exception as e:
        # On error, return mock confused response
        return {
            "success": False,
            "response_text": MOCK_RESPONSES["confused"],
            "voice_memory_clip": None,
            "matched_schemes": scheme_ids,
            "error": str(e),
            "mock": True
        }
