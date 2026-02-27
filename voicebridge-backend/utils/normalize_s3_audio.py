#!/usr/bin/env python3
"""
VoiceBridge Audio Normalizer
=============================
Scans the voicebridge-audio-yuga S3 bucket and:
1. Finds any audio file with wrong/double extensions (.mp3.mpeg, .mpeg, .wav, .ogg etc)
2. Re-uploads it with the correct .mp3 filename
3. Deletes the old wrongly-named file
4. Prints a report of everything it changed

WHEN TO RUN THIS SCRIPT:
  Run this script whenever new voice memory clips are uploaded to S3.
  New uploads from local machine often get wrong MIME types or double extensions.
  This script fixes both issues automatically.
  
  It is safe to run multiple times (idempotent).

Usage:
  pip install boto3
  python utils/normalize_s3_audio.py           # dry run first
  python utils/normalize_s3_audio.py --apply   # apply fixes

Requirements:
  - AWS credentials configured (same account as your Lambda)
  - boto3 installed
  - REGION: ap-southeast-1 (hardcoded)
  - BUCKET: voicebridge-audio-yuga (hardcoded)
"""

import boto3
import os
import sys
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
BUCKET_NAME = 'voicebridge-audio-yuga'
REGION = 'ap-southeast-1'

# Audio files anywhere in these prefixes will be checked
SCAN_PREFIXES = ['voice_memory/', 'tts_output/', '']  # '' = root level

# Any file ending with these will be normalized to .mp3
AUDIO_EXTENSIONS = [
    '.mp3.mpeg',   # your current problem - double extension
    '.mpeg',
    '.mp4',
    '.m4a',
    '.wav',
    '.ogg',
    '.webm',
    '.aac',
    '.flac',
]

# These are already correct - skip them
CORRECT_EXTENSIONS = ['.mp3']

# ── Main Logic ───────────────────────────────────────────────────────────────

def normalize_audio_files(dry_run=False):
    """
    Scan S3 bucket and normalize all audio filenames to .mp3
    
    dry_run=True: only print what would change, don't actually do it
    dry_run=False: actually rename the files
    """
    s3 = boto3.client('s3', region_name=REGION)
    
    print(f"\n{'='*60}")
    print(f"VoiceBridge Audio Normalizer")
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will rename files)'}")
    print(f"{'='*60}\n")
    
    # List all objects in bucket
    paginator = s3.get_paginator('list_objects_v2')
    
    renamed = []
    skipped = []
    errors = []
    
    try:
        pages = paginator.paginate(Bucket=BUCKET_NAME)
        
        for page in pages:
            if 'Contents' not in page:
                print("Bucket is empty or no objects found.")
                return
                
            for obj in page['Contents']:
                key = obj['Key']
                
                # Skip folders
                if key.endswith('/'):
                    continue
                
                # Check if this file needs renaming
                needs_rename = False
                new_key = key
                
                for bad_ext in AUDIO_EXTENSIONS:
                    if key.lower().endswith(bad_ext.lower()):
                        # Remove the bad extension and add .mp3
                        base = key[:-len(bad_ext)]
                        new_key = base + '.mp3'
                        needs_rename = True
                        break
                
                if not needs_rename:
                    # Already has correct extension or not an audio file
                    is_audio = any(key.lower().endswith(ext) for ext in CORRECT_EXTENSIONS)
                    if is_audio:
                        skipped.append(key)
                    continue
                
                if key == new_key:
                    skipped.append(key)
                    continue
                
                print(f"  RENAME: {key}")
                print(f"      → : {new_key}")
                
                if not dry_run:
                    try:
                        # Copy with new name
                        s3.copy_object(
                            Bucket=BUCKET_NAME,
                            CopySource={'Bucket': BUCKET_NAME, 'Key': key},
                            Key=new_key,
                            MetadataDirective='REPLACE',
                            ContentType='audio/mpeg',  # Set correct MIME type
                        )
                        
                        # Delete old file
                        s3.delete_object(Bucket=BUCKET_NAME, Key=key)
                        
                        renamed.append((key, new_key))
                        print(f"      ✅ Done\n")
                        
                    except Exception as e:
                        errors.append((key, str(e)))
                        print(f"      ❌ Error: {e}\n")
                else:
                    renamed.append((key, new_key))
                    print(f"      (dry run - no change)\n")
    
    except Exception as e:
        print(f"❌ Failed to list bucket: {e}")
        print("Make sure AWS credentials are configured and bucket name is correct.")
        sys.exit(1)
    
    # ── Report ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"REPORT")
    print(f"{'='*60}")
    print(f"  Files renamed:  {len(renamed)}")
    print(f"  Files skipped:  {len(skipped)} (already correct)")
    print(f"  Errors:         {len(errors)}")
    
    if renamed:
        print(f"\nRenamed files:")
        for old, new in renamed:
            print(f"  {old} → {new}")
    
    if errors:
        print(f"\nErrors:")
        for key, err in errors:
            print(f"  {key}: {err}")
    
    if dry_run and renamed:
        print(f"\n⚠️  This was a DRY RUN. Run with dry_run=False to apply changes.")
        print(f"   Or run: python normalize_s3_audio.py --apply")
    elif not dry_run and renamed:
        print(f"\n✅ All files normalized successfully!")
        print(f"   Your audio players should now work correctly.")
    elif not renamed:
        print(f"\n✅ All audio files already have correct extensions. Nothing to do.")


def also_fix_content_type():
    """
    Fix S3 ContentType metadata on all .mp3 files.
    Some files may be stored as 'binary/octet-stream' which prevents browser playback.
    This ensures all .mp3 files have ContentType: audio/mpeg
    """
    s3 = boto3.client('s3', region_name=REGION)
    
    print(f"\n{'='*60}")
    print(f"Fixing ContentType metadata on .mp3 files...")
    print(f"{'='*60}\n")
    
    paginator = s3.get_paginator('list_objects_v2')
    fixed = 0
    
    for page in paginator.paginate(Bucket=BUCKET_NAME):
        if 'Contents' not in page:
            continue
            
        for obj in page['Contents']:
            key = obj['Key']
            
            if not key.lower().endswith('.mp3'):
                continue
            
            # Check current ContentType
            head = s3.head_object(Bucket=BUCKET_NAME, Key=key)
            current_type = head.get('ContentType', '')
            
            if current_type == 'audio/mpeg':
                print(f"  ✅ {key} — already audio/mpeg")
                continue
            
            print(f"  🔧 {key} — fixing {current_type} → audio/mpeg")
            
            # Re-copy to self with correct ContentType
            s3.copy_object(
                Bucket=BUCKET_NAME,
                CopySource={'Bucket': BUCKET_NAME, 'Key': key},
                Key=key,
                MetadataDirective='REPLACE',
                ContentType='audio/mpeg',
            )
            fixed += 1
            print(f"      ✅ Fixed")
    
    print(f"\n✅ Fixed ContentType on {fixed} files.")


if __name__ == '__main__':
    apply = '--apply' in sys.argv
    
    # Step 1: Rename wrong extensions to .mp3
    normalize_audio_files(dry_run=not apply)
    
    # Step 2: Fix ContentType metadata (only in apply mode)
    if apply:
        also_fix_content_type()
    
    if not apply:
        print("\nTo apply changes, run:")
        print("  python normalize_s3_audio.py --apply")
