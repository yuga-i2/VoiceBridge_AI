"""
TwiML Webhook Routes for Twilio Call Handling
When farmer answers the call, Twilio calls these endpoints to get instructions.
"""

from flask import Blueprint, request, Response
import logging
from services.scheme_service import get_scheme_by_id

logger = logging.getLogger(__name__)

call_bp = Blueprint('call', __name__)

@call_bp.route('/api/call/twiml', methods=['GET', 'POST'])
def twiml_handler():
    """
    Twilio calls this URL when farmer answers the phone.
    Returns TwiML instructions for the call flow.
    This is Sahaya's voice script.
    """
    farmer_name = request.args.get('farmer_name', 'Kisan bhai')
    schemes = request.args.get('schemes', 'PM_KISAN').split(',')
    
    logger.info(f"TwiML handler: {farmer_name}, schemes: {schemes}")
    
    # Get first scheme details
    first_scheme = get_scheme_by_id(schemes[0]) if schemes else None
    scheme_name = first_scheme.get('name', 'PM-KISAN') if first_scheme else 'PM-KISAN'
    benefit = first_scheme.get('benefit', '₹6,000 pratisaal') if first_scheme else '₹6,000 pratisaal'
    
    # TwiML response - Sahaya speaks in Hindi
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Namaste! Main Sahaya hoon, ek sarkaari kalyan sahayak.
        {farmer_name} ji, aapko {scheme_name} ka laabh mil sakta hai.
        Yeh laabh hai {benefit}.
    </Say>
    <Gather numDigits="1" action="/api/call/gather" method="POST" timeout="10">
        <Say voice="Polly.Kajal" language="hi-IN">
            Agar aap is yojana ke baare mein aur jaankari chahte hain, 
            toh 1 dabaayein. Doosri yojanaon ke liye 2 dabaayein.
            Agar aap SMS mein jaankari chahte hain, toh 3 dabaayein.
        </Say>
    </Gather>
    <Say voice="Polly.Kajal" language="hi-IN">
        Koi jawab nahi mila. Hum aapko baad mein call karenge. Dhanyavaad.
    </Say>
</Response>'''
    
    return Response(twiml, mimetype='text/xml')


@call_bp.route('/api/call/gather', methods=['POST'])
def gather_handler():
    """Handles DTMF input from farmer during call"""
    digit = request.form.get('Digits', '')
    farmer_name = request.args.get('farmer_name', 'Kisan bhai')
    schemes = request.args.get('schemes', 'PM_KISAN').split(',')
    
    logger.info(f"Gather handler: digit={digit} from {farmer_name}")
    
    if digit == '1':
        # More scheme info
        scheme = get_scheme_by_id(schemes[0]) if schemes else None
        docs = scheme.get('documents', ['Aadhaar', 'Zameen ke kagaz', 'Bank passbook']) if scheme else []
        docs_text = ', '.join(docs[:3])
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Is yojana ke liye aapko yeh kagaz chahiye: {docs_text}.
        Nazdiki Common Service Centre mein jaayein aur apply karein.
        Aapko SMS mein poori jaankari milegi.
    </Say>
    <Say voice="Polly.Kajal" language="hi-IN">Dhanyavaad. Sahaya aapke saath hai.</Say>
</Response>'''
    elif digit == '2':
        twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Hum aapko doosri yojanaon ke baare mein SMS bhejenge.
        Kisan Credit Card, Fasal Bima, aur Ayushman Bharat ke baare mein
        jaankari SMS mein milegi.
    </Say>
</Response>'''
    elif digit == '3':
        twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Bilkul! Hum aapko abhi SMS bhej rahe hain.
        Apna phone dekhein. Dhanyavaad.
    </Say>
</Response>'''
    else:
        twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Kajal" language="hi-IN">
        Kripya 1, 2, ya 3 dabaayein.
    </Say>
</Response>'''
    
    return Response(twiml, mimetype='text/xml')


@call_bp.route('/api/call/status', methods=['POST'])
def call_status():
    """Twilio calls this when call status changes"""
    call_sid = request.form.get('CallSid')
    status = request.form.get('CallStatus')
    logger.info(f"Call {call_sid} status: {status}")
    return '', 200
