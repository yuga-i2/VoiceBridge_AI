"""
VoiceBridge AI — Text-to-Speech Service
Converts Hindi text to MP3 audio.
"""

import os
import uuid
from config.settings import USE_MOCK, AWS_REGION, S3_AUDIO_BUCKET

if not USE_MOCK:
    import boto3

MOCK_AUDIO_PATH = "data/voice_memory/mock_response.mp3"


def synthesize_speech(text: str) -> dict:
    """
    Converts Hindi text to audio MP3.
    Returns dict with audio_url, duration, success status.
    """
    if USE_MOCK:
        # Mock path - check if mock audio exists
        if os.path.exists(MOCK_AUDIO_PATH):
            return {
                "success": True,
                "audio_url": "http://localhost:5000/audio/mock_response.mp3",
                "duration_seconds": 5.0,
                "mock": True
            }
        else:
            return {
                "success": True,
                "audio_url": None,
                "duration_seconds": 0,
                "mock": True,
                "note": "Place a mock_response.mp3 in data/voice_memory/ for audio playback"
            }
    
    else:
        # AWS path - use Polly
        try:
            polly = boto3.client("polly", region_name=AWS_REGION)
            s3 = boto3.client("s3", region_name=AWS_REGION)
            
            # Call Polly to synthesize
            response = polly.synthesize_speech(
                Text=text,
                VoiceId="Kajal",
                Engine="neural",
                OutputFormat="mp3",
                LanguageCode="hi-IN"
            )
            
            # Save to S3
            audio_stream = response["AudioStream"].read()
            s3_key = f"tts_output/{uuid.uuid4()}.mp3"
            s3.put_object(
                Bucket=S3_AUDIO_BUCKET,
                Key=s3_key,
                Body=audio_stream,
                ContentType="audio/mpeg"
            )
            
            # Generate presigned URL
            presigned_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": S3_AUDIO_BUCKET, "Key": s3_key},
                ExpiresIn=3600
            )
            
            # Estimate duration (150 words per minute for Hindi)
            word_count = len(text.split())
            duration = (word_count / 150) * 60
            
            return {
                "success": True,
                "audio_url": presigned_url,
                "duration_seconds": round(duration, 1),
                "mock": False
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "audio_url": None,
                "mock": False
            }
