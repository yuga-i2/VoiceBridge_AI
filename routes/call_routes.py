"""
COMPLETE SAHAYA 6-STAGE CALL FLOW
Stage 1: Trust Building — Introduction + Voice Memory clip from S3
Stage 2: Land size question via DTMF (1/2/3)
Stage 3: KCC question + Scheme matching + Bedrock AI explanation
Stage 4: Document guidance + SMS sent
Stage 5: Closing + second scheme option

Uses Amazon Polly.Kajal neural voice for authentic Hindi.
Uses real DynamoDB scheme data.
Uses Bedrock AI for personalised explanations.
Uses S3 for peer success Voice Memory clips.
"""

from flask import Blueprint, request, Response, jsonify
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_BASE_DIR / '.env', override=True)

call_bp = Blueprint('call', __name__)



# ─────────────────────────────────────────────
# STAGE 1: TRUST INTRODUCTION + VOICE MEMORY
# Called when farmer answers the phone
# ─────────────────────────────────────────────

@call_bp.route('/api/call/twiml', methods=['GET', 'POST'])
def twiml_stage1_intro():
    """
    CRITICAL FIX: Twilio returns "Press any key" when endpoint returns ERROR.
    This version has ZERO function calls - just hardcoded strings.
    No exceptions possible = Twilio always gets valid XML.
    """
    try:
        farmer_name = request.args.get('farmer_name', 'Farmer')
        # HARDCODED - NO FUNCTION CALLS ALLOWED
        twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Say voice="Polly.Kajal" language="hi-IN">Namaste {farmer_name} ji. Main Sahaya hoon. Ek sarkaari kalyan sahayak. Main aapko sarkaari yojanaon ke baare mein jaankari dene ke liye call kar rahi hoon.</Say><Pause length="1"/><Say voice="Polly.Kajal" language="hi-IN">Ek important baat. Main kabhi aapka Aadhaar number, OTP, ya bank password nahi maangti.</Say><Pause length="1"/><Say voice="Polly.Kajal" language="hi-IN">Ab main aapki thodi jaankari lena chahti hoon taaki sahi yojana bataa sakoon.</Say><Gather numDigits="1" action="https://164a-43-229-91-78.ngrok-free.app/api/call/stage2-land?farmer_name={farmer_name}" method="POST" timeout="10"><Say voice="Polly.Kajal" language="hi-IN">Aapke paas kitni zameen hai? 1 dabayen. 2 dabayen. 3 dabayen.</Say></Gather></Response>'
        return Response(twiml, mimetype='text/xml; charset=utf-8')
    except Exception as e:
        logger.error(f"CRITICAL: twiml_stage1_intro crashed: {e}")
        return Response('<?xml version="1.0" encoding="UTF-8"?><Response><Say voice="Polly.Kajal" language="hi-IN">Error occurred.</Say></Response>', mimetype='text/xml')


# ─────────────────────────────────────────────
# STAGE 2: ELIGIBILITY QUESTION 1 — LAND SIZE
# ─────────────────────────────────────────────

@call_bp.route('/api/call/stage2-land', methods=['POST'])
def twiml_stage2_land():
    """Stage 2: Get land size from DTMF, ask KCC question."""
    digit = request.form.get('Digits', '2').strip()
    farmer_name = request.args.get('farmer_name', 'Kisan bhai')
    
    # Map digit to land acres
    land_map = {'1': 1.0, '2': 3.0, '3': 7.0}
    land_acres = land_map.get(digit, 2.0)
    
    base_url = _get_base_url()

    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>

    <Say voice="Polly.Kajal" language="hi-IN">
        Achha. Ab ek aur sawaal.
    </Say>

    <Gather numDigits="1"
            action="{base_url}/api/call/stage3-schemes?farmer_name={farmer_name}&amp;land={land_acres}"
            method="POST" timeout="10" finishOnKey="">
        <Say voice="Polly.Kajal" language="hi-IN">
            Kya aapke paas Kisan Credit Card hai?
            Haan ke liye 1 dabaayein.
            Nahi ke liye 2 dabaayein.
        </Say>
    </Gather>

    <Say voice="Polly.Kajal" language="hi-IN">
        Koi jawab nahi mila. Sahaya dobara call karegi.
    </Say>

</Response>'''

    return Response(twiml, mimetype='text/xml')


# ─────────────────────────────────────────────
# STAGE 3: SCHEME MATCHING + AI EXPLANATION
# ─────────────────────────────────────────────

@call_bp.route('/api/call/stage3-schemes', methods=['POST'])
def twiml_stage3_schemes():
    """
    Stage 3: Match schemes using DynamoDB eligibility check.
    Get Bedrock AI explanation personalised for this farmer.
    Play Voice Memory clip for matched scheme.
    """
    digit = request.form.get('Digits', '2').strip()
    farmer_name = request.args.get('farmer_name', 'Kisan bhai')
    land_acres = float(request.args.get('land', '2.0'))
    has_kcc = digit == '1'
    
    from services.call_conversation import (
        get_scheme_for_farmer,
        get_scheme_details_for_call,
        get_ai_scheme_explanation,
        get_voice_memory_url
    )
    
    # Get matching schemes from DynamoDB
    matched_schemes = get_scheme_for_farmer(land_acres, has_kcc)
    primary_scheme = matched_schemes[0]
    scheme = get_scheme_details_for_call(primary_scheme)
    
    # Get Bedrock AI personalised explanation
    ai_explanation = get_ai_scheme_explanation(
        farmer_name, primary_scheme, land_acres, has_kcc
    )
    
    # Get Voice Memory clip for this scheme from S3
    voice_memory_url = get_voice_memory_url(primary_scheme)
    
    # Format schemes for next stage
    schemes_param = ','.join(matched_schemes[:2])
    base_url = _get_base_url()

    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>

    <!-- Announce scheme match -->
    <Say voice="Polly.Kajal" language="hi-IN">
        Mujhe {farmer_name} ji ke liye sahi yojana 
        mil gayi hai.
    </Say>

    <Pause length="1"/>

    <!-- AI-generated personalised explanation from Bedrock -->
    <Say voice="Polly.Kajal" language="hi-IN">
        {ai_explanation}
    </Say>

    <Pause length="1"/>

    <!-- Voice Memory clip for this scheme from S3 -->
    <Say voice="Polly.Kajal" language="hi-IN">
        Is yojana ke baare mein ek aur kisan ka anubhav 
        suniye.
    </Say>

    <Play>{voice_memory_url}</Play>

    <Pause length="1"/>

    <!-- Move to document guidance -->
    <Gather numDigits="1"
            action="{base_url}/api/call/stage4-docs?farmer_name={farmer_name}&amp;schemes={schemes_param}"
            method="POST" timeout="10" finishOnKey="">
        <Say voice="Polly.Kajal" language="hi-IN">
            Kya aap apply karne ke liye 
            zarori kagzaat jaanna chahte hain?
            Haan ke liye 1 dabaayein.
            Baad mein sunne ke liye 2 dabaayein.
        </Say>
    </Gather>

    <Say voice="Polly.Kajal" language="hi-IN">
        Koi jawab nahi mila. Sahaya aapko SMS 
        bhejegi. Dhanyavaad.
    </Say>

</Response>'''

    # Send SMS in background
    _send_sms_background(farmer_name, matched_schemes)

    return Response(twiml, mimetype='text/xml')


# ─────────────────────────────────────────────
# STAGE 4: DOCUMENT GUIDANCE
# ─────────────────────────────────────────────

@call_bp.route('/api/call/stage4-docs', methods=['POST'])
def twiml_stage4_docs():
    """Stage 4: Tell farmer exactly what documents they need."""
    digit = request.form.get('Digits', '1').strip()
    farmer_name = request.args.get('farmer_name', 'Kisan bhai')
    schemes_param = request.args.get('schemes', 'PM_KISAN')
    scheme_list = schemes_param.split(',')
    primary_scheme = scheme_list[0].strip()
    
    base_url = _get_base_url()

    if digit == '2':
        # Farmer wants to hear later — send SMS and close
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Bilkul {farmer_name} ji. Sahaya ne aapko SMS 
        bhej diya hai. Usme poori jaankari hai.
        Hum 3 din mein dobara call karenge.
        Dhanyavaad. Jai Kisan.
    </Say>
</Response>'''
        return Response(twiml, mimetype='text/xml')
    
    from services.call_conversation import get_scheme_details_for_call
    scheme = get_scheme_details_for_call(primary_scheme)
    docs = scheme['documents']
    apply_at = scheme['apply_at']
    
    # Build document list for speech
    doc_count = len(docs)
    docs_speech = ''
    for i, doc in enumerate(docs, 1):
        docs_speech += f"Number {i}: {doc}. "

    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>

    <Say voice="Polly.Kajal" language="hi-IN">
        {scheme["name_hi"]} ke liye aapko 
        {doc_count} kagaz chahiye.
    </Say>

    <Pause length="1"/>

    <Say voice="Polly.Kajal" language="hi-IN">
        {docs_speech}
    </Say>

    <Pause length="1"/>

    <Say voice="Polly.Kajal" language="hi-IN">
        Yeh kagaz lekar {apply_at} mein jaaiye 
        aur apply kariye.
    </Say>

    <Pause length="1"/>

    <!-- Stage 5: SMS confirmation -->
    <Say voice="Polly.Kajal" language="hi-IN">
        Sahaya ne aapke phone par SMS bhej diya hai.
        Usme yeh sabhi jaankari likhi hui hai.
    </Say>

    <Pause length="1"/>

    <Gather numDigits="1"
            action="{base_url}/api/call/stage5-close?farmer_name={farmer_name}&amp;schemes={schemes_param}"
            method="POST" timeout="8" finishOnKey="">
        <Say voice="Polly.Kajal" language="hi-IN">
            Kya aap doosri yojanaon ke baare mein 
            bhi jaanna chahte hain?
            Haan ke liye 1 dabaayein.
            Nahi ke liye 2 dabaayein.
        </Say>
    </Gather>

    <Say voice="Polly.Kajal" language="hi-IN">
        Dhanyavaad {farmer_name} ji. 
        Sahaya hamesha aapke saath hai.
        Jai Kisan. Jai Hind.
    </Say>

</Response>'''

    return Response(twiml, mimetype='text/xml')


# ─────────────────────────────────────────────
# STAGE 5: CLOSING
# ─────────────────────────────────────────────

@call_bp.route('/api/call/stage5-close', methods=['POST'])
def twiml_stage5_close():
    """Stage 5: Warm close, offer callback."""
    digit = request.form.get('Digits', '2').strip()
    farmer_name = request.args.get('farmer_name', 'Kisan bhai')
    schemes_param = request.args.get('schemes', 'PM_KISAN')
    scheme_list = schemes_param.split(',')
    
    base_url = _get_base_url()

    if digit == '1' and len(scheme_list) > 1:
        # Tell about second scheme
        second_scheme = scheme_list[1].strip()
        from services.call_conversation import (
            get_scheme_details_for_call,
            get_voice_memory_url,
            get_ai_scheme_explanation
        )
        scheme2 = get_scheme_details_for_call(second_scheme)
        explanation2 = get_ai_scheme_explanation(
            farmer_name, second_scheme, 2.0, False
        )
        voice_url2 = get_voice_memory_url(second_scheme)

        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        {farmer_name} ji, ek aur yojana hai 
        jo aapke liye sahi hai.
    </Say>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">
        {explanation2}
    </Say>
    <Pause length="1"/>
    <Play>{voice_url2}</Play>
    <Pause length="1"/>
    <Say voice="Polly.Kajal" language="hi-IN">
        Sahaya ne SMS mein yeh bhi jaankari bhej 
        di hai. Hum 3 din mein phir call karenge.
        Dhanyavaad {farmer_name} ji. Jai Kisan.
    </Say>
</Response>'''
    else:
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Bahut achha {farmer_name} ji.
        Sahaya ne aapke phone par poori jaankari 
        ke saath SMS bhej diya hai.
        3 din mein Sahaya dobara call karegi 
        aur progress poochegi.
        Kisi bhi samasya mein, SMS ka jawab dein.
        Dhanyavaad. Jai Kisan. Jai Hind.
    </Say>
</Response>'''

    return Response(twiml, mimetype='text/xml')


# ─────────────────────────────────────────────
# STATUS + TEST ENDPOINTS
# ─────────────────────────────────────────────

@call_bp.route('/api/call/status', methods=['POST'])
def call_status():
    """Twilio status webhook."""
    call_sid = request.form.get('CallSid', '')
    status = request.form.get('CallStatus', '')
    duration = request.form.get('CallDuration', '0')
    logger.info(
        f"Call {call_sid}: status={status}, duration={duration}s"
    )
    return '', 200


@call_bp.route('/api/call/preview', methods=['GET'])
def preview_call():
    """
    Preview what Sahaya will say for a given farmer + scheme.
    Use this to verify before making real calls.
    GET /api/call/preview?scheme=PM_KISAN&name=Ramesh&land=2&kcc=false
    """
    scheme_id = request.args.get('scheme', 'PM_KISAN')
    farmer_name = request.args.get('name', 'Ramesh Kumar')
    land_acres = float(request.args.get('land', '2'))
    has_kcc = request.args.get('kcc', 'false').lower() == 'true'

    from services.call_conversation import (
        get_scheme_details_for_call,
        get_ai_scheme_explanation,
        get_voice_memory_url
    )

    scheme = get_scheme_details_for_call(scheme_id)
    ai_intro = get_ai_scheme_explanation(
        farmer_name, scheme_id, land_acres, has_kcc
    )
    voice_memory = get_voice_memory_url(scheme_id)

    return jsonify({
        'farmer_name': farmer_name,
        'scheme_id': scheme_id,
        'scheme_name_hi': scheme['name_hi'],
        'benefit': scheme['benefit'],
        'documents': scheme['documents'],
        'apply_at': scheme['apply_at'],
        'ai_intro_text': ai_intro,
        'voice_memory_url': voice_memory,
        'call_flow': [
            'Stage 1: Trust intro + anti-scam + Voice Memory clip',
            'Stage 2: Land size question (DTMF)',
            'Stage 3: KCC question + Scheme match + AI explanation',
            'Stage 4: Document list + SMS sent',
            'Stage 5: Second scheme offer + warm close'
        ],
        'note': 'This is exactly what Sahaya will say on the call'
    })


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def _get_base_url():
    """Get webhook base URL fresh from .env."""
    load_dotenv(dotenv_path=_BASE_DIR / '.env', override=True)
    return os.getenv('WEBHOOK_BASE_URL', 'http://localhost:5000')


def _send_sms_background(farmer_name, scheme_ids):
    """Send SMS checklist in background — non-blocking."""
    try:
        from services.sms_service import send_checklist
        result = send_checklist('+917736448307', scheme_ids)
        logger.info(f"SMS sent: {result.get('success')}")
    except Exception as e:
        logger.error(f"SMS failed (non-critical): {e}")


@call_bp.route('/api/call/simple-test', methods=['GET', 'POST'])
def twiml_simple_test():
    """Bare minimum TwiML - just a simple greeting to test basic functionality."""
    try:
        farmer_name = request.args.get('farmer_name', 'Farmer')
        
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Namaste {farmer_name}. Main Sahaya hoon.
        Mera naam Sahaya hai.
        Yeh ek test call hai.
    </Say>
    <Pause length="2"/>
    <Say voice="Polly.Kajal" language="hi-IN">
        Ek, do, teen. Test pura ho gaya.
    </Say>
</Response>'''
        
        logger.info(f"Simple test TwiML returned for {farmer_name}")
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"ERROR in simple test: {e}", exc_info=True)
        error_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Error. Namaste.
    </Say>
</Response>'''
        return Response(error_twiml, mimetype='text/xml')

