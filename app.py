"""
VoiceBridge AI — Flask REST API
All endpoints defined here. No business logic - only delegation to services.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid

from config.settings import USE_MOCK, FLASK_PORT, FLASK_ENV
from models.farmer import FarmerProfile
from services.scheme_service import (
    get_all_schemes,
    match_schemes_to_message,
    check_eligibility
)
from services.ai_service import generate_response
from services.stt_service import transcribe_audio
from services.tts_service import synthesize_speech
from services.sms_service import send_checklist
from services.voice_memory_service import get_clip
from services.call_service import initiate_sahaya_call, get_active_provider
import os

# Create Flask app
app = Flask(__name__)
CORS(app)


# ==================== HEALTH & UTILITIES ====================

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "mock_mode": USE_MOCK,
        "version": "1.0.0",
        "call_provider": get_active_provider(),
        "sms_provider": os.getenv('SMS_PROVIDER', 'mock'),
        "services": {
            "bedrock": "live" if not USE_MOCK else "mock",
            "dynamodb": "live" if not USE_MOCK else "mock",
            "polly": "live" if not USE_MOCK else "mock",
            "s3": "live" if not USE_MOCK else "mock",
            "transcribe": "live" if not USE_MOCK else "mock",
            "call": get_active_provider(),
            "sms": os.getenv('SMS_PROVIDER', 'mock')
        }
    }), 200


@app.route("/audio/<filename>", methods=["GET"])
def serve_audio(filename):
    """Serve local audio files for mock mode."""
    try:
        return send_from_directory("data/voice_memory", filename)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404


# ==================== SCHEME ENDPOINTS ====================

@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    """Get all 10 welfare schemes."""
    try:
        schemes = get_all_schemes()
        return jsonify({
            "success": True,
            "schemes": schemes,
            "total": len(schemes)
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "SERVICE_ERROR"
        }), 500


@app.route("/api/eligibility-check", methods=["POST"])
def eligibility_check():
    """Check which schemes a farmer qualifies for."""
    try:
        data = request.get_json()
        farmer_data = data.get("farmer_profile")
        
        if not farmer_data:
            return jsonify({
                "success": False,
                "error": "farmer_profile is required",
                "code": "INVALID_INPUT"
            }), 400
        
        farmer = FarmerProfile.from_dict(farmer_data)
        
        if not farmer.is_valid():
            return jsonify({
                "success": False,
                "error": "Invalid farmer profile: land_acres must be > 0 and state must be specified",
                "code": "INVALID_INPUT"
            }), 400
        
        eligible_schemes = check_eligibility(farmer)
        
        # Calculate total benefit summary
        total_summary_parts = []
        for scheme in eligible_schemes[:3]:  # Top 3
            total_summary_parts.append(f"{scheme['name_hi']}: {scheme['benefit'][:50]}...")
        total_benefit_summary = " | ".join(total_summary_parts) if total_summary_parts else "No schemes"
        
        return jsonify({
            "success": True,
            "eligible_schemes": [
                {
                    "scheme_id": s["scheme_id"],
                    "name_en": s["name_en"],
                    "name_hi": s["name_hi"],
                    "benefit": s["benefit"],
                    "reason_eligible": s.get("reason_eligible", "")
                }
                for s in eligible_schemes
            ],
            "total_eligible": len(eligible_schemes),
            "total_schemes": 10,
            "total_benefit_summary": total_benefit_summary
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "SERVICE_ERROR"
        }), 500


# ==================== AI CONVERSATION ====================

@app.route("/api/chat", methods=["POST"])
def chat():
    """Main conversation endpoint."""
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        farmer_data = data.get("farmer_profile")
        conversation_history = data.get("conversation_history", [])
        
        if not message:
            return jsonify({
                "success": False,
                "error": "message is required and cannot be empty",
                "code": "INVALID_INPUT"
            }), 400
        
        if not farmer_data:
            return jsonify({
                "success": False,
                "error": "farmer_profile is required",
                "code": "INVALID_INPUT"
            }), 400
        
        farmer = FarmerProfile.from_dict(farmer_data)
        
        # Match schemes based on message
        matched_schemes = match_schemes_to_message(message)
        
        # Generate response
        response_data = generate_response(message, matched_schemes, farmer, conversation_history)
        
        conversation_id = str(uuid.uuid4())
        
        return jsonify({
            "success": response_data.get("success", True),
            "response_text": response_data["response_text"],
            "voice_memory_clip": response_data.get("voice_memory_clip"),
            "matched_schemes": matched_schemes,
            "conversation_id": conversation_id
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "SERVICE_ERROR"
        }), 500


# ==================== SPEECH SERVICES ====================

@app.route("/api/speech-to-text", methods=["POST"])
def speech_to_text():
    """Convert audio to Hindi text."""
    try:
        # Check if audio file present
        if "audio" not in request.files:
            return jsonify({
                "success": False,
                "error": "audio file is required",
                "code": "INVALID_INPUT"
            }), 400
        
        audio_file = request.files["audio"]
        if not audio_file:
            return jsonify({
                "success": False,
                "error": "audio file is empty",
                "code": "INVALID_INPUT"
            }), 400
        
        # Read file bytes
        audio_bytes = audio_file.read()
        filename = audio_file.filename or "audio.mp3"
        
        # Transcribe
        result = transcribe_audio(audio_bytes, filename)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "transcript": result["transcript"],
                "confidence": result.get("confidence", 0.9)
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Transcription failed"),
                "code": "SERVICE_ERROR"
            }), 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "SERVICE_ERROR"
        }), 500


@app.route("/api/text-to-speech", methods=["POST"])
def text_to_speech():
    """Convert Hindi text to audio."""
    try:
        data = request.get_json()
        text = data.get("text", "").strip()
        voice = data.get("voice", "Kajal")
        
        if not text:
            return jsonify({
                "success": False,
                "error": "text is required and cannot be empty",
                "code": "INVALID_INPUT"
            }), 400
        
        # Synthesize
        result = synthesize_speech(text)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "audio_url": result.get("audio_url"),
                "duration_seconds": result.get("duration_seconds", 0)
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Synthesis failed"),
                "code": "SERVICE_ERROR"
            }), 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "SERVICE_ERROR"
        }), 500


# ==================== VOICE MEMORY ====================

@app.route("/api/voice-memory/<scheme_id>", methods=["GET"])
def voice_memory(scheme_id):
    """Get peer success story audio clip."""
    try:
        result = get_clip(scheme_id)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "audio_url": result.get("audio_url"),
                "farmer_name": result.get("farmer_name"),
                "district": result.get("district"),
                "scheme": result.get("scheme")
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Clip not found"),
                "code": "NOT_FOUND"
            }), 404
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "SERVICE_ERROR"
        }), 500


# ==================== SMS ====================

@app.route("/api/send-sms", methods=["POST"])
def send_sms():
    """Send document checklist SMS."""
    try:
        data = request.get_json()
        phone_number = data.get("phone_number", "").strip()
        scheme_ids = data.get("scheme_ids", [])
        
        if not phone_number:
            return jsonify({
                "success": False,
                "error": "phone_number is required",
                "code": "INVALID_INPUT"
            }), 400
        
        if not isinstance(scheme_ids, list) or len(scheme_ids) == 0:
            return jsonify({
                "success": False,
                "error": "scheme_ids must be a non-empty array",
                "code": "INVALID_INPUT"
            }), 400
        
        # Send SMS
        result = send_checklist(phone_number, scheme_ids)
        
        return jsonify({
            "success": result["success"],
            "message_preview": result.get("message_preview"),
            "mock_mode": result.get("mock_mode", False)
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "code": "SERVICE_ERROR"
        }), 500


# ==================== CALL INITIATION ====================

@app.route("/api/initiate-call", methods=["POST"])
def initiate_call():
    """
    Initiate outbound call to farmer.
    Body: { farmer_phone, farmer_name, scheme_ids[] }
    Provider switches via CALL_PROVIDER env var.
    """
    try:
        data = request.get_json()
        farmer_phone = data.get('farmer_phone', '').strip()
        farmer_name = data.get('farmer_name', 'Kisan bhai')
        scheme_ids = data.get('scheme_ids', ['PM_KISAN'])
        
        if not farmer_phone:
            return jsonify({
                'success': False,
                'error': 'farmer_phone required',
                'code': 'INVALID_INPUT'
            }), 400
        
        result = initiate_sahaya_call(farmer_phone, farmer_name, scheme_ids)
        result['active_provider'] = get_active_provider()
        
        return jsonify(result), 200 if result['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'SERVICE_ERROR'
        }), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "code": "NOT_FOUND"
    }), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "code": "SERVER_ERROR"
    }), 500


# ==================== REGISTER BLUEPRINTS ====================

from routes.call_routes import call_bp
app.register_blueprint(call_bp)


# ==================== RUN ====================

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print("VoiceBridge AI — Flask Server Starting")
    print(f"{'='*60}")
    print(f"Environment:  {FLASK_ENV}")
    print(f"Mock Mode:    {USE_MOCK}")
    print(f"Port:         {FLASK_PORT}")
    print(f"{'='*60}\n")
    
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=(FLASK_ENV == "development"))
