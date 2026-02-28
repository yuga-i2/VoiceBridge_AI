"""
VoiceBridge AI — Flask Application Entry Point
Registers all blueprints. No business logic here.
"""
import logging
import os
import base64
import uuid
import requests
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
        
        # Inline scheme detection — does not depend on any service function
        def detect_scheme(msg):
            m = msg.lower()
            # PM_KISAN — Hindi + Malayalam + Tamil keywords
            if any(k in m for k in ['pm kisan','pmkisan','pm-kisan','kisan samman','6000','kisaan','पीएम किसान','पी एम किसान','pihem kisan','piem kisan','പി എം കിസാൻ','പിഎം കിസാൻ','കിസാൻ സമ്മാൻ','pm kisan','கிசான்','பிஎம் கிசான்','கிசான் சம்மான்']):
                return ['PM_KISAN'], 'PM_KISAN'
            # KCC — Hindi + Malayalam + Tamil keywords
            if any(k in m for k in ['kcc','kisan credit','credit card','kisan card','4%','4 percent','सीसीसी','केसीसी','si si si','see see see','kisan lon','kisan loan','4 pratishat','കിസാൻ ക്രെഡിറ്റ്','കെ സി സി','കെസിസി','கிசான் கிரெடிட்','கேசिसी','கிசான் கிரெடิட்','கிரெடிट்']):
                return ['KCC'], 'KCC'
            # PMFBY — Hindi + Malayalam + Tamil keywords
            if any(k in m for k in ['pmfby','fasal bima','crop insurance','bima yojana','fasal insurance','फसल बीमा','piem ef bi','fasal bima yojana','ഫസൽ ബീമ','വിള ഇൻഷുറൻസ്','പിഎംഎഫ്ബിവൈ','பயிர் காப்பீடு','பிஎம்எஃப்பிஒய்']):
                return ['PMFBY'], 'PMFBY'
            if any(k in m for k in ['mgnrega','mnrega','manrega','nrega','100 days','job card','rozgar']):
                return ['MGNREGS'], None
            if any(k in m for k in ['ayushman','pmjay','health insurance','5 lakh health']):
                return ['AYUSHMAN_BHARAT'], None
            if any(k in m for k in ['pm awas','awas yojana','pucca house','ghar yojana']):
                return ['PM_AWAS_GRAMIN'], None
            if any(k in m for k in ['soil health','soil card','mitti','soil test']):
                return ['SOIL_HEALTH_CARD'], None
            return [], None

        matched_schemes, voice_memory_clip = detect_scheme(message)
        
        # Fallback: if no scheme detected in current message,
        # check last assistant message in conversation history
        if not matched_schemes:
            history = data.get('conversation_history', [])
            # Look at last 4 messages for scheme mentions
            recent = history[-4:] if len(history) >= 4 else history
            for msg in reversed(recent):
                content = (msg.get('content') or '').lower()
                fallback_schemes, fallback_clip = detect_scheme(content)
                if fallback_schemes:
                    matched_schemes = fallback_schemes
                    voice_memory_clip = fallback_clip
                    break
        
        fp = data.get('farmer_profile', {})
        history = data.get('conversation_history', [])
        
        # Language support with instructions
        LANG_INSTRUCTIONS = {
            'hi-IN': 'Please respond ONLY in Hindi (Devanagari script).',
            'ta-IN': 'Please respond ONLY in Tamil script.',
            'kn-IN': 'Please respond ONLY in Kannada script.',
            'te-IN': 'Please respond ONLY in Telugu script.',
            'ml-IN': 'Please respond ONLY in Malayalam script.'
        }
        language = data.get('language', 'hi-IN')
        lang_instruction = LANG_INSTRUCTIONS.get(language, LANG_INSTRUCTIONS['hi-IN'])
        
        from models.farmer import FarmerProfile
        from services.ai_service import generate_response
        import uuid
        
        farmer = FarmerProfile.from_dict(fp)
        result = generate_response(message, matched_schemes, farmer, history, lang_instruction)
        response_text = result.get('response_text', '')
        
        # Use voice_memory_clip from AI response first (most accurate)
        # Fall back to detect_scheme result if AI didn't return one
        final_voice_clip = result.get('voice_memory_clip') or voice_memory_clip
        
        # Fallback: detect voice clip from AI response text
        if not final_voice_clip and response_text:
            # Check English scheme names (always present in AI response regardless of language)
            rt = response_text.lower()
            if 'pm-kisan' in rt or 'pm kisan' in rt or 'pmkisan' in rt or '6,000' in rt or '6000' in rt:
                final_voice_clip = 'PM_KISAN'
            elif 'kisan credit' in rt or 'kcc' in rt or 'credit card' in rt:
                final_voice_clip = 'KCC'
            elif 'pmfby' in rt or 'fasal bima' in rt or 'crop insurance' in rt or 'pm fasal' in rt:
                final_voice_clip = 'PMFBY'

        # Fallback: use first matched scheme if still no clip
        if not final_voice_clip and matched_schemes:
            clip_eligible = ['PM_KISAN', 'KCC', 'PMFBY']
            for scheme in matched_schemes:
                if scheme in clip_eligible:
                    final_voice_clip = scheme
                    break

        
        # Generate TTS audio for Sahaya's response
        tts_audio_url = None
        voice_memory_url = None
        
        # First, try to get pre-recorded voice memory clip
        if final_voice_clip:
            from services.voice_memory_service import get_clip
            clip_result = get_clip(final_voice_clip, language)
            if clip_result.get('success'):
                voice_memory_url = clip_result.get('audio_url')
        
        # ALWAYS generate TTS for the response (for intro/context)
        # Voice memory is separate and plays after TTS
        try:
            from services.tts_service import synthesize_speech
            tts_result = synthesize_speech(response_text)
            if tts_result.get('success'):
                tts_audio_url = tts_result.get('audio_url')
        except Exception as tts_err:
            logger.warning(f"TTS failed (non-fatal): {tts_err}")
        
        # For responses with voice memory, return BOTH:
        # - audio_url: Polly TTS for the intro/context
        # - voice_memory_clip: Pre-recorded farmer story to play after
        final_audio_url = tts_audio_url  # Always return TTS if available
        
        return jsonify({
            'success': True,
            'response_text': response_text,
            'matched_schemes': matched_schemes,
            'voice_memory_clip': final_voice_clip,
            'audio_url': final_audio_url,
            'audio_type': 'tts' if final_audio_url else 'none',  # TTS is always primary
            'conversation_id': uuid.uuid4().hex
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'success': False, 'error': str(e), 'code': 'SERVICE_ERROR'}), 500


@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        audio_bytes = None
        filename = 'audio.mp3'
        
        # Try FormData first (from browser MediaRecorder)
        if 'audio' in request.files:
            audio_file = request.files['audio']
            audio_bytes = audio_file.read()
            filename = audio_file.filename or 'audio.mp3'
        # Try JSON with base64 (fallback)
        elif request.is_json:
            import base64
            data = request.get_json() or {}
            audio_b64 = data.get('audio_data', '')
            if audio_b64:
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                except Exception:
                    audio_bytes = None
        
        if not audio_bytes:
            return jsonify({'success': False, 'error': 'No audio file',
                           'code': 'INVALID_INPUT'}), 400
        
        from services.stt_service import transcribe_audio
        result = transcribe_audio(audio_bytes, filename)
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


@app.route('/api/sarvam-tts', methods=['POST'])
def sarvam_tts():
    """Regional language TTS via Sarvam AI Bulbul v3."""
    try:
        import boto3
        from config.settings import SARVAM_API_KEY, SARVAM_API_URL, AWS_REGION, S3_AUDIO_BUCKET, USE_MOCK
        
        data = request.get_json() or {}
        text = (data.get('text') or '').strip()
        language = (data.get('language') or '').strip()
        # Normalize to BCP-47 format e.g. ml-IN (not ml-in)
        if '-' in language:
            parts = language.split('-')
            language = parts[0].lower() + '-' + parts[1].upper()
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        if not language:
            return jsonify({'success': False, 'error': 'Language is required'}), 400
        
        # Mock mode for testing without Sarvam API
        if USE_MOCK:
            return jsonify({
                'success': True,
                'audio_url': 'https://mock-sarvam-audio.s3.amazonaws.com/mock-audio.wav',
                'language': language
            })
        
        # Speaker mapping: language → Sarvam speaker ID
        speaker_map = {
            'ta-IN': 'anushka',
            'kn-IN': 'anushka',
            'te-IN': 'anushka',
            'ml-IN': 'manisha',
            'hi-IN': 'anushka'
        }
        
        speaker_id = speaker_map.get(language, 'meera')
        logger.info(f"Sarvam TTS: lang={language} speaker={speaker_id} text_len={len(text)}")
        
        # Call Sarvam API
        headers = {'api-subscription-key': SARVAM_API_KEY}
        payload = {
            'inputs': [text],
            'target_language_code': language,
            'speaker': 'manisha',
            'model': 'bulbul:v2',
            'pace': 0.78,
            'pitch': 0,
            'loudness': 1.5,
            'enable_preprocessing': True
        }
        
        response = requests.post(SARVAM_API_URL, json=payload, headers=headers, timeout=30)
        if response.status_code != 200:
            logger.error(f"Sarvam API error: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'error': f'Sarvam API returned {response.status_code}'
            }), 500
        
        result = response.json()
        audios = result.get('audios') or []
        if not audios:
            logger.error(f"Sarvam API no audio in response: {result}")
            return jsonify({'success': False, 'error': 'No audio from Sarvam'}), 500
        
        # Decode base64 audio and upload to S3
        audio_base64 = result['audios'][0]
        audio_bytes = base64.b64decode(audio_base64)
        
        # Generate S3 key
        s3_key = f"sarvam-audio/{uuid.uuid4()}.wav"
        
        # Upload to S3
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        s3_client.put_object(
            Bucket=S3_AUDIO_BUCKET,
            Key=s3_key,
            Body=audio_bytes,
            ContentType='audio/wav'
        )
        
        # Generate presigned URL (1 hour expiry)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_AUDIO_BUCKET, 'Key': s3_key},
            ExpiresIn=3600
        )
        
        return jsonify({
            'success': True,
            'audio_url': presigned_url,
            'language': language,
            'speaker': speaker_id
        })
        
    except Exception as e:
        logger.error(f"Sarvam TTS error: {e}")
        return jsonify({'success': False, 'error': str(e), 'code': 'SERVICE_ERROR'}), 500


@app.route('/api/voice-memory/<scheme_id>', methods=['GET'])
def voice_memory(scheme_id):
    try:
        import boto3
        from config.settings import AWS_REGION, S3_AUDIO_BUCKET
        
        # Language from query param, default Hindi
        language = request.args.get('language', 'hi-IN')
        
        # S3 key mapping per language per scheme
        VOICE_MEMORY_MAP = {
            'hi-IN': {
                'PM_KISAN': {
                    'key': 'voice_memory/voice_memory_PM_KISAN.mp3',
                    'farmer_name': 'Sunitha Devi',
                    'district': 'Tumkur, Karnataka',
                    'scheme': 'PM-KISAN'
                },
                'KCC': {
                    'key': 'voice_memory/voice_memory_KCC.mp3',
                    'farmer_name': 'Ramaiah',
                    'district': 'Mysuru, Karnataka',
                    'scheme': 'KCC'
                },
                'PMFBY': {
                    'key': 'voice_memory/voice_memory_PMFBY.mp3',
                    'farmer_name': 'Laxman Singh',
                    'district': 'Dharwad, Karnataka',
                    'scheme': 'PMFBY'
                }
            },
            'ml-IN': {
                'PM_KISAN': {
                    'key': 'voice_memory/voice_memory_Mal_PM_KISAN.mp3.mpeg',
                    'farmer_name': 'Priya',
                    'district': 'Thrissur, Kerala',
                    'scheme': 'PM-KISAN'
                },
                'KCC': {
                    'key': 'voice_memory/voice_memory_Mal_KCC.mp3.mpeg',
                    'farmer_name': 'Rajan',
                    'district': 'Palakkad, Kerala',
                    'scheme': 'KCC'
                },
                'PMFBY': {
                    'key': 'voice_memory/voice_memory_Mal_PMFBY.mp3.mpeg',
                    'farmer_name': 'Suresh Kumar',
                    'district': 'Wayanad, Kerala',
                    'scheme': 'PMFBY'
                }
            },
            'ta-IN': {
                'PM_KISAN': {
                    'key': 'voice_memory/voice_memory_Tamil_PM_KISAN.mp3.mpeg',
                    'farmer_name': 'Kavitha',
                    'district': 'Coimbatore, Tamil Nadu',
                    'scheme': 'PM-KISAN'
                },
                'KCC': {
                    'key': 'voice_memory/voice_memory_Tamil_KCC.mp3.mpeg',
                    'farmer_name': 'Vijay',
                    'district': 'Madurai, Tamil Nadu',
                    'scheme': 'KCC'
                },
                'PMFBY': {
                    'key': 'voice_memory/voice_memory_Tamil_PMFBY.mp3.mpeg',
                    'farmer_name': 'Selva',
                    'district': 'Thanjavur, Tamil Nadu',
                    'scheme': 'PMFBY'
                }
            }
        }
        
        # Fallback: if language not supported, use Hindi
        lang_map = VOICE_MEMORY_MAP.get(language, VOICE_MEMORY_MAP['hi-IN'])
        
        # Fallback: if scheme not in map, return no clip
        clip_info = lang_map.get(scheme_id)
        if not clip_info:
            return jsonify({'success': False, 'error': 'No clip for this scheme'})
        
        # Generate presigned URL
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_AUDIO_BUCKET, 'Key': clip_info['key']},
            ExpiresIn=3600
        )
        
        return jsonify({
            'success': True,
            'audio_url': presigned_url,
            'farmer_name': clip_info['farmer_name'],
            'district': clip_info['district'],
            'scheme': clip_info['scheme'],
            'language': language,
            'mock': False
        })
        
    except Exception as e:
        logger.error(f'Voice memory error: {e}')
        return jsonify({'success': False, 'error': str(e)})


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
