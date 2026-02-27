"""
VoiceBridge AI — Twilio Call Routes
TwiML endpoints implementing the complete 6-stage Sahaya conversation.
Called by Twilio when farmer answers the phone.

Stage 1: Trust introduction + anti-scam statement
Stage 2: Voice Memory Network clip from S3
Stage 3: Eligibility questions (land size + KCC)
Stage 4: Bedrock AI scheme matching + explanation
Stage 5: Document guidance
Stage 6: SMS confirmation + warm close
"""
import os
import logging
from pathlib import Path
from flask import Blueprint, request, make_response, jsonify
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
_BASE_DIR = Path(__file__).resolve().parent.parent
call_bp = Blueprint('call', __name__)


def _load():
    """Fresh .env load — never use cached values for credentials."""
    load_dotenv(dotenv_path=_BASE_DIR / '.env', override=True)


def _base_url():
    _load()
    return os.getenv('WEBHOOK_BASE_URL', 'http://localhost:5000').rstrip('/')


def _twiml(xml: str):
    """
    Return TwiML response with EXACTLY the header Twilio requires.
    Using make_response + explicit header is the only reliable method.
    """
    resp = make_response(xml)
    resp.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return resp


def _get_scheme(scheme_id: str) -> dict:
    """Get scheme details from DynamoDB via scheme_service. Falls back to verified data."""
    try:
        from services.scheme_service import get_scheme_by_id
        s = get_scheme_by_id(scheme_id)
        if s:
            return {
                'name_hi': s.get('name_hi', ''),
                'benefit': s.get('benefit', ''),
                'documents': s.get('documents', [])[:3],
                'apply_at': s.get('apply_at', 'nazdiki CSC kendra')
            }
    except Exception as e:
        logger.error(f"Scheme fetch failed for {scheme_id}: {e}")

    # Verified fallback — amounts from official government sources
    FALLBACK = {
        'PM_KISAN': {
            'name_hi': 'पीएम किसान सम्मान निधि',
            'benefit': '6,000 rupaye pratisaal, teen kisht mein seedha bank mein',
            'documents': ['Aadhaar card', 'Zameen ke kagaz (Khatauni)', 'Bank passbook'],
            'apply_at': 'pmkisan.gov.in ya nazdiki CSC kendra'
        },
        'KCC': {
            'name_hi': 'किसान क्रेडिट कार्ड',
            'benefit': '3 lakh rupaye tak ka loan, sirf 4 pratishat byaaj par saal mein',
            'documents': ['Aadhaar card', 'Zameen ke kagaz', 'Bank passbook', 'Passport photo'],
            'apply_at': 'nazdiki bank shaakha mein'
        },
        'PMFBY': {
            'name_hi': 'प्रधानमंत्री फसल बीमा योजना',
            'benefit': 'Fasal kharab hone par poora muavza, sirf 2 pratishat premium',
            'documents': ['Aadhaar card', 'Zameen ke kagaz', 'Bank passbook', 'Baayi fasal ki jaankari'],
            'apply_at': 'nazdiki bank ya bima company mein'
        },
        'AYUSHMAN_BHARAT': {
            'name_hi': 'आयुष्मान भारत',
            'benefit': '5 lakh rupaye tak ka muft ilaaj har saal parivar ke liye',
            'documents': ['Aadhaar card', 'Ration card'],
            'apply_at': 'nazdiki sarkari aspatal ya CSC kendra'
        },
        'MGNREGS': {
            'name_hi': 'मनरेगा',
            'benefit': '100 din ka guaranteed kaam, 220 se 357 rupaye rozana state ke hisaab se',
            'documents': ['Aadhaar card', 'Bank passbook'],
            'apply_at': 'gram panchayat office'
        }
    }
    return FALLBACK.get(scheme_id, FALLBACK['PM_KISAN'])


def _get_voice_memory_url(scheme_id: str) -> str:
    """Public S3 URL for Voice Memory clip. Twilio fetches directly."""
    _load()
    bucket = os.getenv('S3_AUDIO_BUCKET', 'voicebridge-audio-yuga')
    region = os.getenv('AWS_REGION', 'ap-southeast-1')
    clip_map = {
        'PM_KISAN': 'voice_memory_PM_KISAN.mp3',
        'KCC': 'voice_memory_KCC.mp3',
        'PMFBY': 'voice_memory_PMFBY.mp3',
    }
    filename = clip_map.get(scheme_id, 'voice_memory_PM_KISAN.mp3')
    return f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"


def _get_ai_intro(farmer_name: str, scheme_id: str, land: float, has_kcc: bool) -> str:
    """Bedrock AI personalised intro — short, warm, accurate. Falls back to template."""
    scheme = _get_scheme(scheme_id)
    try:
        from models.farmer import FarmerProfile
        from services.ai_service import generate_response
        farmer = FarmerProfile.from_dict({
            'name': farmer_name, 'land_acres': land,
            'state': 'Karnataka', 'has_kcc': has_kcc,
            'has_bank_account': True
        })
        result = generate_response(
            f"{farmer_name} ji ko {scheme['name_hi']} ke baare mein 2 vaakya mein batao. Sirf Hindi mein.",
            [scheme_id], farmer, []
        )
        text = result.get('response_text', '')
        if text and len(text) > 20:
            parts = text.split('।')
            return ('। '.join(parts[:2]) + '।')[:280]
    except Exception as e:
        logger.error(f"Bedrock intro failed: {e}")
    return (
        f"{farmer_name} ji, {scheme['name_hi']} mein "
        f"aapko {scheme['benefit']} milega. "
        f"Yeh yojana aapke liye bilkul sahi hai."
    )


def _get_matched_schemes(land: float, has_kcc: bool) -> list:
    """DynamoDB eligibility check via scheme_service."""
    try:
        from models.farmer import FarmerProfile
        from services.scheme_service import check_eligibility
        farmer = FarmerProfile.from_dict({
            'name': 'Kisan', 'land_acres': land,
            'state': 'Karnataka', 'has_kcc': has_kcc,
            'has_bank_account': True, 'age': 40
        })
        eligible = check_eligibility(farmer)
        return [s['scheme_id'] for s in eligible[:2]]
    except Exception as e:
        logger.error(f"Eligibility check failed: {e}")
    return ['PM_KISAN', 'PMFBY']


def _send_sms_async(farmer_phone: str, scheme_ids: list):
    """Send SMS in background — non-blocking."""
    try:
        from services.sms_service import send_checklist
        result = send_checklist(farmer_phone, scheme_ids)
        logger.info(f"SMS result: success={result.get('success')}")
    except Exception as e:
        logger.error(f"SMS failed (non-critical): {e}")


# ─────────────────────────────────────────────────────────────
# STAGE 1: TRUST INTRODUCTION
# Called when farmer answers. Sahaya introduces + anti-scam.
# ─────────────────────────────────────────────────────────────

@call_bp.route('/api/call/twiml', methods=['GET', 'POST'])
def stage1_intro():
    farmer_name = request.args.get('farmer_name', 'Kisan bhai')
    schemes_param = request.args.get('schemes', 'PM_KISAN')
    base = _base_url()

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Namaste {farmer_name} ji!
        Main Sahaya hoon, ek sarkaari kalyan sahayak.
        Aapko sarkaari yojanaon ke baare mein batane ke liye call ki hai.
    </Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">
        Ek zaroori baat — main kabhi bhi aapka Aadhaar number,
        OTP, ya bank password nahi maangti.
        Yeh call bilkul safe hai.
    </Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">
        Pehle Tumkur ke ek kisan, Suresh Kumar ji ka sandesh suniye.
    </Say>
    <Play>{_get_voice_memory_url('PM_KISAN')}</Play>
    <Pause length="1"/>
    <Gather numDigits="1"
            action="{base}/api/call/stage2?farmer={farmer_name}&amp;schemes={schemes_param}"
            method="POST" timeout="10" finishOnKey="">
        <Say voice="Polly.Kajal" language="hi-IN">
            Ab main aapki thodi jaankari lena chahti hoon.
            Aapke paas kitni zameen hai?
            2 acre se kam ke liye 1 dabayein.
            2 se 5 acre ke liye 2 dabayein.
            5 acre se zyada ke liye 3 dabayein.
        </Say>
    </Gather>
    <Say voice="Polly.Kajal" language="hi-IN">
        Koi jawab nahi mila. Sahaya dobara call karegi. Dhanyavaad.
    </Say>
</Response>"""
    return _twiml(xml)


# ─────────────────────────────────────────────────────────────
# STAGE 2: LAND SIZE → KCC QUESTION
# ─────────────────────────────────────────────────────────────

@call_bp.route('/api/call/stage2', methods=['POST'])
def stage2_land():
    digit = request.form.get('Digits', '2').strip()
    farmer_name = request.args.get('farmer', 'Kisan bhai')
    schemes_param = request.args.get('schemes', 'PM_KISAN')
    land_map = {'1': 1.0, '2': 3.0, '3': 7.0}
    land = land_map.get(digit, 2.0)
    base = _base_url()

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">Achha. Ek aur sawaal.</Say>
    <Gather numDigits="1"
            action="{base}/api/call/stage3?farmer={farmer_name}&amp;land={land}&amp;schemes={schemes_param}"
            method="POST" timeout="10" finishOnKey="">
        <Say voice="Polly.Kajal" language="hi-IN">
            Kya aapke paas Kisan Credit Card hai?
            Haan ke liye 1 dabayein. Nahi ke liye 2 dabayein.
        </Say>
    </Gather>
    <Say voice="Polly.Kajal" language="hi-IN">Sahaya dobara call karegi. Dhanyavaad.</Say>
</Response>"""
    return _twiml(xml)


# ─────────────────────────────────────────────────────────────
# STAGE 3: SCHEME MATCHING + AI EXPLANATION + VOICE MEMORY
# ─────────────────────────────────────────────────────────────

@call_bp.route('/api/call/stage3', methods=['POST'])
def stage3_schemes():
    digit = request.form.get('Digits', '2').strip()
    farmer_name = request.args.get('farmer', 'Kisan bhai')
    land = float(request.args.get('land', '2.0'))
    has_kcc = (digit == '1')
    base = _base_url()

    matched = _get_matched_schemes(land, has_kcc)
    primary = matched[0] if matched else 'PM_KISAN'
    scheme = _get_scheme(primary)
    ai_intro = _get_ai_intro(farmer_name, primary, land, has_kcc)
    vm_url = _get_voice_memory_url(primary)
    schemes_str = ','.join(matched[:2])

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Mujhe {farmer_name} ji ke liye sahi yojana mil gayi.
    </Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">{ai_intro}</Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">
        Is yojana se laabh paane wale ek kisan ka anubhav suniye.
    </Say>
    <Play>{vm_url}</Play>
    <Pause length="1"/>
    <Gather numDigits="1"
            action="{base}/api/call/stage4?farmer={farmer_name}&amp;schemes={schemes_str}"
            method="POST" timeout="10" finishOnKey="">
        <Say voice="Polly.Kajal" language="hi-IN">
            Kya aap apply karne ke liye zarori kagaz jaanna chahte hain?
            Haan ke liye 1. Baad mein call ke liye 2.
        </Say>
    </Gather>
    <Say voice="Polly.Kajal" language="hi-IN">
        Sahaya ne aapko SMS bhej diya hai. Dhanyavaad.
    </Say>
</Response>"""

    # Send SMS
    verified = os.getenv('TWILIO_VERIFIED_NUMBER', '')
    if verified:
        _send_sms_async(verified, matched)

    return _twiml(xml)


# ─────────────────────────────────────────────────────────────
# STAGE 4: DOCUMENT GUIDANCE
# ─────────────────────────────────────────────────────────────

@call_bp.route('/api/call/stage4', methods=['POST'])
def stage4_docs():
    digit = request.form.get('Digits', '1').strip()
    farmer_name = request.args.get('farmer', 'Kisan bhai')
    schemes_param = request.args.get('schemes', 'PM_KISAN')
    primary = schemes_param.split(',')[0].strip()
    base = _base_url()

    if digit == '2':
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Bilkul {farmer_name} ji.
        Sahaya ne SMS bhej diya hai. 3 din mein dobara call karenge.
        Dhanyavaad. Jai Kisan.
    </Say>
</Response>"""
        return _twiml(xml)

    scheme = _get_scheme(primary)
    docs = scheme['documents']
    docs_speech = ' '.join([f"Number {i+1}: {d}." for i, d in enumerate(docs)])

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        {scheme['name_hi']} ke liye zarori kagaz hain:
    </Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">{docs_speech}</Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">
        Yeh sab lekar {scheme['apply_at']} mein jaaiye.
        Sahaya ne aapke phone par poori list SMS ki hai.
    </Say>
    <Pause length="1"/>
    <Gather numDigits="1"
            action="{base}/api/call/stage5?farmer={farmer_name}&amp;schemes={schemes_param}"
            method="POST" timeout="8" finishOnKey="">
        <Say voice="Polly.Kajal" language="hi-IN">
            Kya aap doosri yojana ke baare mein bhi jaanna chahte hain?
            Haan ke liye 1. Nahi ke liye 2.
        </Say>
    </Gather>
    <Say voice="Polly.Kajal" language="hi-IN">
        Dhanyavaad {farmer_name} ji. Jai Kisan. Jai Hind.
    </Say>
</Response>"""
    return _twiml(xml)


# ─────────────────────────────────────────────────────────────
# STAGE 5: CLOSE OR SECOND SCHEME
# ─────────────────────────────────────────────────────────────

@call_bp.route('/api/call/stage5', methods=['POST'])
def stage5_close():
    digit = request.form.get('Digits', '2').strip()
    farmer_name = request.args.get('farmer', 'Kisan bhai')
    schemes_param = request.args.get('schemes', 'PM_KISAN')
    scheme_list = [s.strip() for s in schemes_param.split(',')]

    if digit == '1' and len(scheme_list) > 1:
        second = scheme_list[1]
        scheme2 = _get_scheme(second)
        vm_url2 = _get_voice_memory_url(second)
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        {farmer_name} ji, ek aur yojana hai jo aapke liye sahi hai.
        {scheme2['name_hi']} mein {scheme2['benefit']}.
    </Say>
    <Pause length="1"/>
    <Play>{vm_url2}</Play>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">
        SMS mein yeh bhi jaankari hai.
        3 din mein Sahaya phir call karegi.
        Dhanyavaad {farmer_name} ji. Jai Kisan.
    </Say>
</Response>"""
    else:
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Bahut achha {farmer_name} ji.
        SMS mein poori jaankari hai.
        3 din mein Sahaya dobara call karegi.
        Dhanyavaad. Jai Kisan. Jai Hind.
    </Say>
</Response>"""
    return _twiml(xml)


# ─────────────────────────────────────────────────────────────
# STATUS + TEST ENDPOINTS
# ─────────────────────────────────────────────────────────────

@call_bp.route('/api/call/status', methods=['POST'])
def call_status():
    """Twilio status callback."""
    sid = request.form.get('CallSid', '')
    status = request.form.get('CallStatus', '')
    duration = request.form.get('CallDuration', '0')
    logger.info(f"Call {sid}: {status} ({duration}s)")
    return '', 200


@call_bp.route('/api/call/ping', methods=['GET', 'POST'])
def ping():
    """Simplest valid TwiML. Use to verify Twilio can reach server."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Namaste! Main Sahaya hoon. Server bilkul theek kaam kar raha hai.
    </Say>
</Response>"""
    return _twiml(xml)


@call_bp.route('/api/call/preview', methods=['GET'])
def preview():
    """Preview call script for testing. GET /api/call/preview?scheme=PM_KISAN&name=Ramesh"""
    scheme_id = request.args.get('scheme', 'PM_KISAN')
    farmer_name = request.args.get('name', 'Ramesh Kumar')
    land = float(request.args.get('land', '2'))
    has_kcc = request.args.get('kcc', 'false').lower() == 'true'

    scheme = _get_scheme(scheme_id)
    ai_intro = _get_ai_intro(farmer_name, scheme_id, land, has_kcc)
    vm_url = _get_voice_memory_url(scheme_id)

    return jsonify({
        'farmer_name': farmer_name,
        'scheme_id': scheme_id,
        'scheme_name_hi': scheme['name_hi'],
        'benefit': scheme['benefit'],
        'documents': scheme['documents'],
        'apply_at': scheme['apply_at'],
        'ai_intro': ai_intro,
        'voice_memory_url': vm_url,
        'twiml_url': f"{_base_url()}/api/call/twiml?farmer_name={farmer_name}&schemes={scheme_id}",
        'note': 'This is exactly what Sahaya will say when farmer answers'
    })

