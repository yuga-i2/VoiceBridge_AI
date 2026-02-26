import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_BASE_DIR / '.env', override=True)


def get_voice_memory_url(scheme_id):
    """
    Returns public S3 URL for Voice Memory clip.
    Twilio needs a direct public URL to play audio.
    """
    load_dotenv(dotenv_path=_BASE_DIR / '.env', override=True)
    bucket = os.getenv('S3_AUDIO_BUCKET', 'voicebridge-audio-yuga')
    region = os.getenv('AWS_REGION', 'ap-southeast-1')
    
    clip_map = {
        'PM_KISAN': 'voice_memory_PM_KISAN.mp3',
        'KCC': 'voice_memory_KCC.mp3',
        'PMFBY': 'voice_memory_PMFBY.mp3'
    }
    
    filename = clip_map.get(scheme_id, 'voice_memory_PM_KISAN.mp3')
    
    # Public S3 URL format
    url = (f"https://{bucket}.s3.{region}"
           f".amazonaws.com/{filename}")
    return url


def get_scheme_for_farmer(land_acres, has_kcc):
    """
    Simple eligibility logic for phone call.
    Returns top 2 matching scheme IDs.
    """
    try:
        from models.farmer import FarmerProfile
        from services.scheme_service import check_eligibility
        
        farmer = FarmerProfile.from_dict({
            'name': 'Kisan',
            'land_acres': land_acres,
            'state': 'Karnataka',
            'has_kcc': has_kcc,
            'has_bank_account': True,
            'age': 40
        })
        
        eligible = check_eligibility(farmer)
        ids = [s['scheme_id'] for s in eligible[:2]]
        return ids if ids else ['PM_KISAN']
        
    except Exception as e:
        logger.error(f"Eligibility check failed: {e}")
        return ['PM_KISAN', 'PMFBY']


def get_scheme_details_for_call(scheme_id):
    """
    Get scheme details for call script.
    Uses DynamoDB via scheme_service.
    Falls back to verified hardcoded data.
    """
    try:
        from services.scheme_service import get_scheme_by_id
        scheme = get_scheme_by_id(scheme_id)
        if scheme:
            return {
                'name_hi': scheme.get('name_hi', ''),
                'benefit': scheme.get('benefit', ''),
                'documents': scheme.get('documents', [])[:3],
                'apply_at': scheme.get('apply_at', 'nazdiki CSC kendra')
            }
    except Exception as e:
        logger.error(f"Scheme fetch failed: {e}")
    
    # Verified fallback data — amounts from official sources
    fallbacks = {
        'PM_KISAN': {
            'name_hi': 'पीएम किसान सम्मान निधि',
            'benefit': '6,000 rupaye pratisaal, '
                      'teen kisht mein seedha aapke bank mein',
            'documents': ['Aadhaar card', 
                         'Zameen ke kagaz (Khatauni)',
                         'Bank passbook'],
            'apply_at': 'pmkisan.gov.in ya nazdiki CSC kendra'
        },
        'KCC': {
            'name_hi': 'किसान क्रेडिट कार्ड',
            'benefit': '3 lakh rupaye tak ka loan, '
                      'sirf 4 pratishat byaaj par',
            'documents': ['Aadhaar card',
                         'Zameen ke kagaz',
                         'Bank passbook',
                         'Passport size photo'],
            'apply_at': 'nazdiki bank shaakha'
        },
        'PMFBY': {
            'name_hi': 'प्रधानमंत्री फसल बीमा योजना',
            'benefit': 'Fasal kharab hone par poora muavza, '
                      'sirf 2 pratishat premium par',
            'documents': ['Aadhaar card',
                         'Zameen ke kagaz',
                         'Bank passbook',
                         'Baayi hui fasal ki jaankari'],
            'apply_at': 'nazdiki bank ya CSC kendra'
        },
        'AYUSHMAN_BHARAT': {
            'name_hi': 'आयुष्मान भारत',
            'benefit': '5 lakh rupaye tak ka muft ilaaj '
                      'har saal parivar ke liye',
            'documents': ['Aadhaar card', 'Ration card'],
            'apply_at': 'nazdiki sarkari aspatal ya CSC kendra'
        },
        'MGNREGS': {
            'name_hi': 'मनरेगा',
            'benefit': '100 din ka guaranteed kaam, '
                      '220 se 357 rupaye rozana',
            'documents': ['Aadhaar card', 'Bank passbook'],
            'apply_at': 'gram panchayat office'
        }
    }
    return fallbacks.get(scheme_id, fallbacks['PM_KISAN'])


def get_ai_scheme_explanation(farmer_name, scheme_id, 
                               land_acres, has_kcc):
    """
    Get Bedrock AI explanation of scheme for this specific farmer.
    Short, personalised, in Hindi. Under 50 words.
    Falls back to template if Bedrock fails.
    """
    scheme = get_scheme_details_for_call(scheme_id)
    
    try:
        from models.farmer import FarmerProfile
        from services.ai_service import generate_response
        
        farmer = FarmerProfile.from_dict({
            'name': farmer_name,
            'land_acres': land_acres,
            'state': 'Karnataka',
            'has_kcc': has_kcc,
            'has_bank_account': True
        })
        
        prompt = (
            f"{farmer_name} ji ko {scheme['name_hi']} ke "
            f"baare mein 2 vaakya mein batao. "
            f"Unke paas {land_acres} acre zameen hai. "
            f"Sirf Hindi mein. Simple bhasha."
        )
        
        result = generate_response(prompt, [scheme_id], farmer, [])
        text = result.get('response_text', '')
        
        if text and len(text) > 20:
            # Keep phone-friendly length
            sentences = text.split('।')
            short = '। '.join(sentences[:2])
            return short[:300] if short else text[:300]
            
    except Exception as e:
        logger.error(f"Bedrock explanation failed: {e}")
    
    # Template fallback
    return (
        f"{farmer_name} ji, {scheme['name_hi']} mein "
        f"aapko {scheme['benefit']} milega. "
        f"Yeh yojana aapke liye bilkul sahi hai."
    )
