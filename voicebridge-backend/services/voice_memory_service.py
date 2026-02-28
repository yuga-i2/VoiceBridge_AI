"""
VoiceBridge AI — Voice Memory Service
Serves peer success story audio clips by scheme ID.
"""

import os
from config.settings import USE_MOCK, AWS_REGION, S3_AUDIO_BUCKET

if not USE_MOCK:
    import boto3


VOICE_MEMORY_CLIPS = {
    "PM_KISAN": {
        "en-IN": {
            "filename": "voice_memory_PM_KISAN.mp3",
            "farmer_name": "Sunitha Devi",
            "district": "Tumkur, Karnataka",
            "scheme": "PM-KISAN"
        },
        "ml-IN": {
            "filename": "voice_memory_Mal_PM_KISAN.mp3.mpeg",
            "farmer_name": "Priya",
            "district": "Thrissur, Kerala",
            "scheme": "PM-KISAN"
        },
        "ta-IN": {
            "filename": "voice_memory_Tamil_PM_KISAN.mp3.mpeg",
            "farmer_name": "Kavitha",
            "district": "Coimbatore, Tamil Nadu",
            "scheme": "PM-KISAN"
        }
    },
    "KCC": {
        "en-IN": {
            "filename": "voice_memory_KCC.mp3",
            "farmer_name": "Ramaiah",
            "district": "Mysuru, Karnataka",
            "scheme": "Kisan Credit Card"
        },
        "ml-IN": {
            "filename": "voice_memory_Mal_KCC.mp3.mpeg",
            "farmer_name": "Rajan",
            "district": "Palakkad, Kerala",
            "scheme": "Kisan Credit Card"
        },
        "ta-IN": {
            "filename": "voice_memory_Tamil_KCC.mp3.mpeg",
            "farmer_name": "Vijay",
            "district": "Madurai, Tamil Nadu",
            "scheme": "Kisan Credit Card"
        }
    },
    "PMFBY": {
        "en-IN": {
            "filename": "voice_memory_PMFBY.mp3",
            "farmer_name": "Laxman Singh",
            "district": "Dharwad, Karnataka",
            "scheme": "PM Fasal Bima Yojana"
        },
        "ml-IN": {
            "filename": "voice_memory_Mal_PMFBY.mp3.mpeg",
            "farmer_name": "Suresh Kumar",
            "district": "Wayanad, Kerala",
            "scheme": "PM Fasal Bima Yojana"
        },
        "ta-IN": {
            "filename": "voice_memory_Tamil_PMFBY.mp3.mpeg",
            "farmer_name": "Selva",
            "district": "Thanjavur, Tamil Nadu",
            "scheme": "PM Fasal Bima Yojana"
        }
    }
}


def get_clip(scheme_id: str, language: str = 'en-IN') -> dict:
    """
    Returns audio clip details for a given scheme_id and language.
    """
    scheme_id = scheme_id.upper()
    language = language or 'en-IN'  # Default to English
    
    if scheme_id not in VOICE_MEMORY_CLIPS:
        return {
            "success": False,
            "error": f"No voice memory clip available for {scheme_id}"
        }
    
    scheme_clips = VOICE_MEMORY_CLIPS[scheme_id]
    
    # Get language-specific clip, fallback to English
    if language in scheme_clips:
        clip_info = scheme_clips[language]
    elif 'en-IN' in scheme_clips:
        clip_info = scheme_clips['en-IN']
    else:
        return {
            "success": False,
            "error": f"No language variant available for {scheme_id}"
        }
    
    if USE_MOCK:
        # Mock path - check if file exists locally
        local_path = f"data/voice_memory/{clip_info['filename']}"
        file_exists = os.path.exists(local_path)
        
        if file_exists:
            audio_url = f"http://localhost:5000/audio/{clip_info['filename']}"
        else:
            audio_url = None
        
        return {
            "success": True,
            "audio_url": audio_url,
            "farmer_name": clip_info["farmer_name"],
            "district": clip_info["district"],
            "scheme": clip_info["scheme"],
            "language": language,
            "mock": True,
            "file_exists": file_exists,
            "note": "Place audio files in data/voice_memory/ for playback"
        }
    
    else:
        # AWS path - generate presigned S3 URL
        try:
            s3 = boto3.client("s3", region_name=AWS_REGION)
            
            presigned_url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": S3_AUDIO_BUCKET,
                    "Key": f"voice_memory/{clip_info['filename']}"
                },
                ExpiresIn=3600
            )
            
            return {
                "success": True,
                "audio_url": presigned_url,
                "farmer_name": clip_info["farmer_name"],
                "district": clip_info["district"],
                "scheme": clip_info["scheme"],
                "language": language,
                "mock": False
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
