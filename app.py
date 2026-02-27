"""
VoiceBridge AI — Flask Application Entry Point
Registers all blueprints. No business logic here.
"""
import logging
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Load .env before everything else
_BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=_BASE_DIR / '.env', override=True)

from config.settings import FLASK_PORT, USE_MOCK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ── Create Flask app ──────────────────────────────────────
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Register blueprints ───────────────────────────────────
from routes.call_routes import call_bp
app.register_blueprint(call_bp)

# ── Serve local audio files (mock mode) ──────────────────
from flask import send_from_directory
import os

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serve local Voice Memory clips in mock mode."""
    return send_from_directory(
        os.path.join(_BASE_DIR, 'data', 'voice_memory'),
        filename
    )

# ── API Routes ────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'mock_mode': USE_MOCK,
        'version': '1.0.0',
        'service': 'VoiceBridge AI — Sahaya'
    })


@app.route('/api/schemes', methods=['GET'])
def get_schemes():
    try:
        from services.scheme_service import get_all_schemes
        schemes = get_all_schemes()
        return jsonify({'success': True, 'schemes': schemes, 'total': len(schemes)})
    except Exception as e:
        logger.error(f"Schemes error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/eligibility-check', methods=['POST'])
def eligibility_check():
    try:
        data = request.get_json() or {}
        fp = data.get('farmer_profile', {})
        from models.farmer import FarmerProfile
        from services.scheme_service import check_eligibility
        farmer = FarmerProfile.from_dict(fp)
        if not farmer.is_valid():
            return jsonify({'success': False, 'error': 'Invalid farmer profile',
                           'code': 'INVALID_INPUT'}), 400
        eligible = check_eligibility(farmer)
        total_benefit = f"₹{sum_benefit(eligible)}+ per year" if eligible else "₹0"
        return jsonify({
            'success': True,
            'eligible_schemes': eligible,
            'total_eligible': len(eligible),
            'total_schemes': 10,
            'total_benefit_summary': total_benefit
        })
    except Exception as e:
        logger.error(f"Eligibility error: {e}")
        return jsonify({'success': False, 'error': str(e), 'code': 'SERVICE_ERROR'}), 500


def sum_benefit(schemes):
    """Rough benefit sum for display."""
    total = 0
    benefit_map = {
        'PM_KISAN': 6000, 'MGNREGS': 22000, 'AYUSHMAN_BHARAT': 500000,
        'PMFBY': 5000, 'KCC': 0, 'SOIL_HEALTH_CARD': 0,
        'PM_AWAS_GRAMIN': 120000, 'NFSA_RATION': 3600,
        'ATAL_PENSION': 12000, 'SUKANYA_SAMRIDDHI': 0
    }
    for s in schemes:
        total += benefit_map.get(s.get('scheme_id', ''), 0)
    return total


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        message = (data.get('message') or '').strip()
        if not message:
            return jsonify({'success': False, 'error': 'Message is required',
                           'code': 'INVALID_INPUT'}), 400
        fp = data.get('farmer_profile', {})
        history = data.get('conversation_history', [])
        from models.farmer import FarmerProfile
        from services.scheme_service import match_schemes_to_message
        from services.ai_service import generate_response
        import uuid
        farmer = FarmerProfile.from_dict(fp)
        scheme_ids = match_schemes_to_message(message)
        result = generate_response(message, scheme_ids, farmer, history)
        return jsonify({
            'success': True,
            'response_text': result.get('response_text', ''),
            'voice_memory_clip': result.get('voice_memory_clip'),
            'matched_schemes': result.get('matched_schemes', scheme_ids),
            'conversation_id': uuid.uuid4().hex
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'success': False, 'error': str(e), 'code': 'SERVICE_ERROR'}), 500


@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file',
                           'code': 'INVALID_INPUT'}), 400
        audio_file = request.files['audio']
        audio_bytes = audio_file.read()
        from services.stt_service import transcribe_audio
        result = transcribe_audio(audio_bytes, audio_file.filename or 'audio.mp3')
        return jsonify(result)
    except Exception as e:
        logger.error(f"STT error: {e}")
        return jsonify({'success': False, 'error': str(e), 'code': 'SERVICE_ERROR'}), 500


@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json() or {}
        text = (data.get('text') or '').strip()
        if not text:
            return jsonify({'success': False, 'error': 'Text is required',
                           'code': 'INVALID_INPUT'}), 400
        from services.tts_service import synthesize_speech
        result = synthesize_speech(text)
        return jsonify(result)
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return jsonify({'success': False, 'error': str(e), 'code': 'SERVICE_ERROR'}), 500


@app.route('/api/voice-memory/<scheme_id>', methods=['GET'])
def voice_memory(scheme_id):
    try:
        from services.voice_memory_service import get_clip
        result = get_clip(scheme_id.upper())
        return jsonify(result)
    except Exception as e:
        logger.error(f"Voice memory error: {e}")
        return jsonify({'success': False, 'error': str(e), 'code': 'SERVICE_ERROR'}), 500


@app.route('/api/send-sms', methods=['POST'])
def send_sms():
    try:
        data = request.get_json() or {}
        phone = (data.get('phone_number') or '').strip()
        scheme_ids = data.get('scheme_ids', [])
        if not phone:
            return jsonify({'success': False, 'error': 'Phone number required',
                           'code': 'INVALID_INPUT'}), 400
        if not isinstance(scheme_ids, list):
            return jsonify({'success': False, 'error': 'scheme_ids must be a list',
                           'code': 'INVALID_INPUT'}), 400
        from services.sms_service import send_checklist
        result = send_checklist(phone, scheme_ids)
        return jsonify(result)
    except Exception as e:
        logger.error(f"SMS error: {e}")
        return jsonify({'success': False, 'error': str(e), 'code': 'SERVICE_ERROR'}), 500


@app.route('/api/initiate-call', methods=['POST'])
def initiate_call():
    """Initiate Sahaya outbound call via configured provider."""
    try:
        data = request.get_json() or {}
        farmer_phone = (data.get('farmer_phone') or '').strip()
        farmer_name = (data.get('farmer_name') or 'Kisan bhai').strip()
        scheme_ids = data.get('scheme_ids', ['PM_KISAN', 'PMFBY'])
        if not farmer_phone:
            return jsonify({'success': False, 'error': 'farmer_phone required',
                           'code': 'INVALID_INPUT'}), 400
        from services.call_service import initiate_sahaya_call, get_active_provider
        result = initiate_sahaya_call(farmer_phone, farmer_name, scheme_ids)
        result['active_provider'] = get_active_provider()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Call error: {e}")
        return jsonify({'success': False, 'error': str(e), 'code': 'SERVICE_ERROR'}), 500


# ── Run ───────────────────────────────────────────────────
if __name__ == '__main__':
    logger.info(f"Starting VoiceBridge AI on port {FLASK_PORT}")
    logger.info(f"Mock mode: {USE_MOCK}")
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=True)
