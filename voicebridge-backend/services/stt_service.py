"""
VoiceBridge AI — Speech-to-Text Service
Converts Hindi audio to text.
"""

import time
import uuid
import os
from config.settings import USE_MOCK, AWS_REGION, S3_AUDIO_BUCKET

if not USE_MOCK:
    import boto3


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.mp3") -> dict:
    """
    Converts Hindi audio to text.
    Returns dict with transcript, confidence, success status.
    """
    if USE_MOCK:
        # Mock path
        return {
            "success": True,
            "transcript": "मुझे पीएम किसान के बारे में बताओ",
            "confidence": 0.95,
            "mock": True
        }
    
    else:
        # AWS path - use Transcribe
        try:
            s3 = boto3.client("s3", region_name=AWS_REGION)
            transcribe = boto3.client("transcribe", region_name=AWS_REGION)
            
            # Upload audio to S3
            s3_key = f"transcribe_input/{uuid.uuid4()}_{filename}"
            s3.put_object(
                Bucket=S3_AUDIO_BUCKET,
                Key=s3_key,
                Body=audio_bytes
            )
            
            s3_uri = f"s3://{S3_AUDIO_BUCKET}/{s3_key}"
            
            # Determine format from filename
            if filename.endswith(".wav"):
                media_format = "wav"
            else:
                media_format = "mp3"
            
            # Start transcription job
            job_name = f"vb_{uuid.uuid4().hex[:8]}"
            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={"MediaFileUri": s3_uri},
                MediaFormat=media_format,
                LanguageCode="hi-IN"
            )
            
            # Poll for completion (max 60 seconds)
            max_wait = 60
            poll_interval = 3
            elapsed = 0
            
            while elapsed < max_wait:
                response = transcribe.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                status = response["TranscriptionJob"]["TranscriptionJobStatus"]
                
                if status == "COMPLETED":
                    # Get transcript
                    transcript_uri = response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
                    s3_transcript_key = transcript_uri.split(f"{S3_AUDIO_BUCKET}/")[1]
                    
                    transcript_obj = s3.get_object(Bucket=S3_AUDIO_BUCKET, Key=s3_transcript_key)
                    import json as json_lib
                    transcript_data = json_lib.loads(transcript_obj["Body"].read().decode("utf-8"))
                    
                    transcript_text = transcript_data["results"]["transcripts"][0]["transcript"]
                    confidence = transcript_data["results"]["transcripts"][0].get("confidence", 0.9)
                    
                    return {
                        "success": True,
                        "transcript": transcript_text,
                        "confidence": float(confidence),
                        "mock": False
                    }
                
                elif status == "FAILED":
                    return {
                        "success": False,
                        "error": "Transcription job failed",
                        "transcript": "",
                        "mock": False
                    }
                
                time.sleep(poll_interval)
                elapsed += poll_interval
            
            # Timeout
            return {
                "success": False,
                "error": "Transcription timeout after 60 seconds",
                "transcript": "",
                "mock": False
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "transcript": "",
                "mock": False
            }
