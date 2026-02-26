"""
TwiML Webhook Routes for Twilio Call Handling
When farmer answers the call, Twilio calls these endpoints to get instructions.
Uses Amazon Polly Kajal voice for Hindi + real DynamoDB scheme data + Bedrock AI.
"""

from flask import Blueprint, request, Response, jsonify
from pathlib import Path
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_BASE_DIR / '.env', override=True)

call_bp = Blueprint('call', __name__)


def _get_scheme_details(scheme_id):
    """Get real scheme data from DynamoDB via scheme_service."""
    try:
        from services.scheme_service import get_scheme_by_id
        scheme = get_scheme_by_id(scheme_id)
        if scheme:
            return {
                'name_hi': scheme.get('name_hi', 'PM-KISAN yojana'),
                'name_en': scheme.get('name_en', scheme_id),
                'benefit': scheme.get('benefit', '6,000 rupaye pratisaal'),
                'documents': scheme.get('documents', [
                    'Aadhaar card',
                    'Zameen ke kagaz',
                    'Bank passbook'
                ]),
                'apply_at': scheme.get('apply_at', 'nazdiki CSC kendra')
            }
    except Exception as e:
        logger.error(f"Could not fetch scheme {scheme_id}: {e}")

    # Fallback data if DynamoDB fails
    fallbacks = {
        'PM_KISAN': {
            'name_hi': 'पीएम किसान सम्मान निधि',
            'name_en': 'PM Kisan Samman Nidhi',
            'benefit': '6,000 rupaye pratisaal, teen kisht mein',
            'documents': ['Aadhaar card', 'Zameen ke kagaz', 'Bank passbook'],
            'apply_at': 'nazdiki CSC kendra ya pmkisan.gov.in'
        },
        'KCC': {
            'name_hi': 'किसान क्रेडिट कार्ड',
            'name_en': 'Kisan Credit Card',
            'benefit': '3 lakh rupaye tak ka loan, sirf 4% byaaj par',
            'documents': ['Aadhaar card', 'Zameen ke kagaz', 
                         'Bank passbook', 'Passport photo'],
            'apply_at': 'nazdiki bank shaakha mein'
        },
        'PMFBY': {
            'name_hi': 'प्रधानमंत्री फसल बीमा योजना',
            'name_en': 'PM Fasal Bima Yojana',
            'benefit': 'Fasal kharab hone par poora muavza, sirf 2% premium par',
            'documents': ['Aadhaar card', 'Zameen ke kagaz',
                         'Bank passbook', 'Baayi hui fasal ki jaankari'],
            'apply_at': 'nazdiki bank ya CSC kendra mein'
        }
    }
    return fallbacks.get(scheme_id, fallbacks['PM_KISAN'])


def _get_ai_intro(farmer_name, scheme_id, scheme_details):
    """
    Get a real Bedrock AI response for the scheme introduction.
    Falls back to a well-written template if Bedrock fails.
    Under 40 words — must be short for phone call.
    """
    try:
        from models.farmer import FarmerProfile
        from services.ai_service import generate_response

        farmer = FarmerProfile.from_dict({
            'name': farmer_name,
            'land_acres': 2,
            'state': 'Karnataka',
            'has_kcc': False,
            'has_bank_account': True
        })

        prompt = (
            f"{farmer_name} ji ko {scheme_details['name_hi']} ke baare "
            f"mein batao. Sirf 2 vaakya mein. Hindi mein."
        )

        result = generate_response(prompt, [scheme_id], farmer, [])
        text = result.get('response_text', '')

        # Keep it short for phone — max 200 chars
        if text and len(text) > 20:
            return text[:200]

    except Exception as e:
        logger.error(f"Bedrock intro failed: {e}")

    # Template fallback — well written Hindi
    return (
        f"{farmer_name} ji, aapko "
        f"{scheme_details['name_hi']} "
        f"ka laabh mil sakta hai. "
        f"Is yojana mein aapko "
        f"{scheme_details['benefit']} milta hai."
    )


@call_bp.route('/api/call/twiml', methods=['GET', 'POST'])
def twiml_handler():
    """
    Twilio calls this when farmer answers.
    Returns TwiML with Sahaya speaking in Hindi using Polly Kajal voice.
    Uses real DynamoDB scheme data and Bedrock AI introductions.
    """
    farmer_name = request.args.get('farmer_name', 'Kisan bhai')
    schemes_param = request.args.get('schemes', 'PM_KISAN')
    scheme_list = [s.strip() for s in schemes_param.split(',') if s.strip()]
    primary_scheme = scheme_list[0] if scheme_list else 'PM_KISAN'

    # Get real scheme data from DynamoDB
    scheme = _get_scheme_details(primary_scheme)

    # Get AI-generated introduction from Bedrock
    intro_text = _get_ai_intro(farmer_name, primary_scheme, scheme)

    # Build document list in Hindi
    docs = scheme['documents'][:3]
    docs_hindi = ', '.join(docs)

    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Namaste! Main Sahaya hoon, ek sarkaari kalyan sahayak.
        Yeh call bilkul free hai. Main kabhi OTP ya password nahi
        maangti.
    </Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">
        {intro_text}
    </Say>
    <Pause length="1"/>
    <Gather numDigits="1" action="/api/call/gather?schemes={schemes_param}&amp;farmer_name={farmer_name}" 
            method="POST" timeout="10" finishOnKey="">
        <Say voice="Polly.Kajal" language="hi-IN">
            Is yojana ke baare mein aur jaankari ke liye ek dabaayein.
            Doosri yojanaon ke liye do dabaayein.
            SMS mein jaankari paane ke liye teen dabaayein.
            Wapas sunne ke liye chaar dabaayein.
        </Say>
    </Gather>
    <Say voice="Polly.Kajal" language="hi-IN">
        Koi jawab nahi mila. Sahaya aapko baad mein dobara call
        karegi. Dhanyavaad. Jai Hind.
    </Say>
</Response>'''

    return Response(twiml, mimetype='text/xml')


@call_bp.route('/api/call/gather', methods=['POST'])
def gather_handler():
    """
    Handles farmer's DTMF keypress during call.
    Returns relevant Hindi information using real scheme data.
    """
    digit = request.form.get('Digits', '').strip()
    farmer_name = request.args.get('farmer_name', 'Kisan bhai')
    schemes_param = request.args.get('schemes', 'PM_KISAN')
    scheme_list = [s.strip() for s in schemes_param.split(',') if s.strip()]
    primary_scheme = scheme_list[0] if scheme_list else 'PM_KISAN'

    scheme = _get_scheme_details(primary_scheme)
    docs = scheme['documents'][:3]
    docs_hindi = ', '.join(docs)
    apply_at = scheme.get('apply_at', 'nazdiki CSC kendra')

    if digit == '1':
        # Full scheme details
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        {scheme["name_hi"]} ke liye yeh kagaz chahiye:
        {docs_hindi}.
        Aap {apply_at} jaake apply kar sakte hain.
        Sahaya aapko SMS mein poori jaankari bhejegi.
    </Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">
        Kya aap aur jaanna chahte hain? Haan ke liye ek dabaayein.
        Call khatam karne ke liye do dabaayein.
    </Say>
    <Gather numDigits="1" 
            action="/api/call/gather?schemes={schemes_param}&amp;farmer_name={farmer_name}&amp;step=followup"
            method="POST" timeout="8">
    </Gather>
</Response>'''

    elif digit == '2':
        # Other schemes
        other_schemes = [s for s in scheme_list[1:3]] if len(scheme_list) > 1 \
            else ['KCC', 'PMFBY']
        other_details = [_get_scheme_details(s) for s in other_schemes[:2]]
        other_names = ' aur '.join([d['name_hi'] for d in other_details])

        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Aapke liye aur yojanaayein hain: {other_names}.
        Sahaya aapko in sabke baare mein SMS bhejegi.
        Dhanyavaad {farmer_name} ji.
    </Say>
</Response>'''

    elif digit == '3':
        # Send SMS
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Bilkul. Sahaya aapko abhi SMS bhej rahi hai.
        Usme {scheme["name_hi"]} ki poori jaankari hogi.
        Apna phone dekhein. Dhanyavaad {farmer_name} ji.
    </Say>
</Response>'''

    elif digit == '4':
        # Repeat
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Redirect>/api/call/twiml?farmer_name={farmer_name}&amp;schemes={schemes_param}</Redirect>
</Response>'''

    else:
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Kripya 1, 2, 3, ya 4 dabaayein.
    </Say>
    <Gather numDigits="1" 
            action="/api/call/gather?schemes={schemes_param}&amp;farmer_name={farmer_name}"
            method="POST" timeout="8">
    </Gather>
</Response>'''

    return Response(twiml, mimetype='text/xml')


@call_bp.route('/api/call/gather-followup', methods=['POST'])
def gather_followup():
    """Handles follow-up responses after scheme details."""
    digit = request.form.get('Digits', '').strip()
    farmer_name = request.args.get('farmer_name', 'Kisan bhai')
    schemes_param = request.args.get('schemes', 'PM_KISAN')

    if digit == '1':
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Sahaya aapko SMS mein poori jaankari bhej rahi hai.
        Kisi bhi samasya mein, hum phir call karenge.
        Dhanyavaad {farmer_name} ji. Jai Kisan.
    </Say>
</Response>'''
    else:
        twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Dhanyavaad. Sahaya hamesha aapke saath hai. 
        Jai Kisan. Jai Hind.
    </Say>
</Response>'''

    return Response(twiml, mimetype='text/xml')


@call_bp.route('/api/call/status', methods=['POST'])
def call_status():
    """Twilio status callback — logs call events."""
    call_sid = request.form.get('CallSid', '')
    status = request.form.get('CallStatus', '')
    duration = request.form.get('CallDuration', '0')
    logger.info(f"Call {call_sid}: {status}, duration: {duration}s")
    return '', 200


@call_bp.route('/api/call/test-twiml', methods=['GET'])
def test_twiml():
    """
    Test endpoint — returns TwiML for a test call.
    Use this URL in browser to preview what Sahaya says.
    GET /api/call/test-twiml?scheme=PM_KISAN&name=Ramesh
    """
    scheme_id = request.args.get('scheme', 'PM_KISAN')
    farmer_name = request.args.get('name', 'Ramesh Kumar')
    scheme = _get_scheme_details(scheme_id)
    intro = _get_ai_intro(farmer_name, scheme_id, scheme)

    return jsonify({
        'farmer_name': farmer_name,
        'scheme_id': scheme_id,
        'scheme_name_hi': scheme['name_hi'],
        'benefit': scheme['benefit'],
        'ai_intro': intro,
        'documents': scheme['documents'],
        'note': 'This is what Sahaya will say on the call using Polly.Kajal voice'
    })
