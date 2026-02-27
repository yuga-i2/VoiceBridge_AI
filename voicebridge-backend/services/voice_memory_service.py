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
        "filename": "voice_memory_PM_KISAN.mp3",
        "farmer_name": "Suresh Kumar",
        "district": "Tumkur, Karnataka",
        "scheme": "PM-KISAN"
    },
    "KCC": {
        "filename": "voice_memory_KCC.mp3",
        "farmer_name": "Ramaiah",
        "district": "Mysuru, Karnataka",
        "scheme": "Kisan Credit Card"
    },
    "PMFBY": {
        "filename": "voice_memory_PMFBY.mp3",
        "farmer_name": "Laxman Singh",
        "district": "Dharwad, Karnataka",
        "scheme": "PM Fasal Bima Yojana"
    }
}


def get_clip(scheme_id: str) -> dict:
    """
    Returns audio clip details for a given scheme_id.
    """
    scheme_id = scheme_id.upper()
    
    if scheme_id not in VOICE_MEMORY_CLIPS:
        return {
            "success": False,
            "error": f"No voice memory clip available for {scheme_id}"
        }
    
    clip_info = VOICE_MEMORY_CLIPS[scheme_id]
    
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
                "mock": False
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
