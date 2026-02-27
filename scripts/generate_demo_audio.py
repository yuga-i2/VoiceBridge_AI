"""
Generate complete Sahaya demo audio files using Amazon Polly Kajal Hindi voice.
This script POSTs each segment to the Flask TTS endpoint and saves MP3 files locally.

Usage:
    python scripts/generate_demo_audio.py

Output:
    Creates 9 MP3 files in demo_audio/ folder with estimated durations and file sizes.
"""

import os
import sys
import requests
from pathlib import Path
from urllib.parse import urlparse
import time

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

FLASK_URL = "http://localhost:5000"
DEMO_AUDIO_DIR = Path(__file__).resolve().parent.parent / "demo_audio"
DEMO_AUDIO_DIR.mkdir(exist_ok=True)

# Hindi text for each segment — exactly as specified
SEGMENTS = [
    {
        "id": "01_intro",
        "text": "नमस्ते Ramesh Kumar जी! मैं सहाया हूँ — एक सरकारी कल्याण सहायक। आपको सरकारी योजनाओं का लाभ दिलाने के लिए call कर रही हूँ।",
        "duration_est": 8,
    },
    {
        "id": "02_antiscam",
        "text": "एक ज़रूरी बात — मैं कभी भी आपका Aadhaar number, OTP, या bank password नहीं माँगती। यह call बिल्कुल safe है और government द्वारा authorized है।",
        "duration_est": 7,
    },
    {
        "id": "03_voice_memory_intro",
        "text": "पहले Tumkur के एक किसान, Suresh Kumar जी का संदेश सुनिए जिन्हें PM-KISAN से फ़ायदा हुआ।",
        "duration_est": 5,
    },
    {
        "id": "04_land_question",
        "text": "अब मैं आपकी थोड़ी जानकारी लेना चाहती हूँ ताकि सही योजना बता सकूँ। आपके पास कितनी ज़मीन है? 2 acre से कम के लिए 1 दबाएं। 2 से 5 acre के लिए 2 दबाएं।",
        "duration_est": 8,
    },
    {
        "id": "05_kcc_question",
        "text": "अच्छा। क्या आपके पास Kisan Credit Card है? हाँ के लिए 1 दबाएं। नहीं के लिए 2 दबाएं।",
        "duration_est": 5,
    },
    {
        "id": "06_scheme_match",
        "text": "Ramesh Kumar जी, मुझे आपके लिए एक बहुत अच्छी योजना मिली है। PM-KISAN Samman Nidhi में आपको 6,000 रुपये प्रतिसाल मिलेंगे, तीन किश्त में सीधे आपके bank account में। यह पैसा आपका हक है।",
        "duration_est": 10,
    },
    {
        "id": "07_documents",
        "text": "Apply करने के लिए सिर्फ तीन चीज़ें चाहिए। एक: Aadhaar card। दो: ज़मीन के कागज़ यानी Khatauni। तीन: Bank passbook। इन्हें लेकर नज़दीकी CSC center जाइए।",
        "duration_est": 10,
    },
    {
        "id": "08_sms_sent",
        "text": "सहाया ने अभी आपके phone पर SMS भेज दिया है। उसमें documents की list, कहाँ जाना है, और सब कुछ Hindi में लिखा है।",
        "duration_est": 7,
    },
    {
        "id": "09_close",
        "text": "3 दिन में हम दोबारा call करेंगे और progress पूछेंगे। धन्यवाद Ramesh Kumar जी। सहाया हमेशा आपके साथ है। जय किसान। जय हिंद।",
        "duration_est": 8,
    },
]


# ─────────────────────────────────────────────
# MAIN FUNCTIONS
# ─────────────────────────────────────────────


def check_flask_running():
    """Verify Flask is running before proceeding."""
    print("Checking Flask server...", end=" ")
    try:
        r = requests.get(f"{FLASK_URL}/api/health", timeout=3)
        if r.status_code == 200:
            print("✅ Flask is running")
            return True
    except Exception as e:
        print(f"❌ Flask is NOT running: {e}")
        print(f"\nTo fix, run: cd {Path(__file__).resolve().parent.parent} && python app.py")
        return False


def download_audio(url, output_path):
    """Download audio file from URL, retry on failure."""
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(r.content)
                return True
        except requests.exceptions.RequestException as e:
            if attempt < 2:
                print(f"    Retry {attempt + 1}/3... ", end="")
                time.sleep(1)
    return False


def generate_audio_segment(segment):
    """Generate single audio segment via TTS endpoint."""
    segment_id = segment["id"]
    filename = f"{segment_id}.mp3"
    output_path = DEMO_AUDIO_DIR / filename

    print(f"\n▶ {segment_id:<25} ", end="")

    # POST to TTS endpoint
    try:
        payload = {"text": segment["text"], "voice": "Kajal"}
        r = requests.post(
            f"{FLASK_URL}/api/text-to-speech",
            json=payload,
            timeout=30,
        )

        if r.status_code != 200:
            print(f"❌ POST failed (status {r.status_code})")
            return False

        data = r.json()
        if not data.get("success"):
            print(f"❌ API returned error: {data.get('error', 'unknown')}")
            return False

        # Download audio
        audio_url = data.get("audio_url")
        if not audio_url:
            print(f"❌ No audio URL in response")
            return False

        print(f"Downloading... ", end="", flush=True)
        if not download_audio(audio_url, output_path):
            print(f"❌ Download failed")
            return False

        # Check file size
        file_size = output_path.stat().st_size
        size_kb = file_size / 1024
        duration_est = segment["duration_est"]

        print(f"✅ {size_kb:6.1f} KB  (~{duration_est}s)")
        return {
            "filename": filename,
            "size_kb": size_kb,
            "duration_est": duration_est,
        }

    except requests.exceptions.Timeout:
        print(f"❌ Request timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False


def main():
    """Generate all audio segments."""
    print("\n" + "═" * 70)
    print("SAHAYA DEMO AUDIO GENERATOR")
    print("═" * 70)
    print(f"\nAudio output directory: {DEMO_AUDIO_DIR}\n")

    # Check Flask
    if not check_flask_running():
        sys.exit(1)

    print(f"\nGenerating 9 demo audio files...\n")
    results = []

    for segment in SEGMENTS:
        result = generate_audio_segment(segment)
        if result:
            results.append(result)
        else:
            print(f"  ⚠️  Skipping due to error")

    # Summary table
    print("\n" + "─" * 70)
    print(f"SUMMARY: {len(results)}/9 files generated successfully")
    print("─" * 70)

    if not results:
        print("\n❌ No audio files were generated. Check Flask and try again.")
        sys.exit(1)

    print(f"\n{'File':<30} {'Size':<12} {'Est. Duration'}")
    print("─" * 70)
    total_duration = 0
    total_size = 0.0

    for result in results:
        print(
            f"{result['filename']:<30} {result['size_kb']:>8.1f} KB  {result['duration_est']:>3}s"
        )
        total_duration += result["duration_est"]
        total_size += result["size_kb"]

    print("─" * 70)
    print(f"{'TOTAL':<30} {total_size:>8.1f} KB  {total_duration:>3}s")
    print("─" * 70)

    print(f"\n✅ Demo audio ready for video recording!")
    print(f"Total duration: ~{total_duration} seconds")
    print(f"Total size: {total_size/1024:.1f} MB")

    if len(results) < 9:
        print(f"\n⚠️  Only {len(results)}/9 files generated. Some segments failed.")
        print("Check Flask logs for errors and re-run the script.")

    print("\n" + "═" * 70 + "\n")


if __name__ == "__main__":
    main()
