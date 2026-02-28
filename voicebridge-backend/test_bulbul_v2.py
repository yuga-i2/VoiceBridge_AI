import requests

languages = {
    'ml-IN': 'നമസ്കാരം, സഹായം നേടാനുള്ള സ്കീമുകൾ',
    'ta-IN': 'வணக்கம், உதவி சேமிப்பு திட்டங்கள்',
    'kn-IN': 'ನಮಸ್ಕಾರ, ಸಹಾಯಕ ಸಂರಕ್ಷಣೆ ಯೋಜನೆಗಳು',
    'te-IN': 'నమస్కారం, సహాయ ఆదాయ పయోజనాలు',
    'hi-IN': 'नमस्कार, सहायता बचत योजनाएं'
}

print('=' * 50)
print('Testing all 5 regional languages with bulbul:v2')
print('=' * 50)

for lang, text in languages.items():
    try:
        r = requests.post(
            'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/sarvam-tts',
            json={'text': text, 'language': lang},
            timeout=10
        ).json()
        status = 'OK' if r.get('success') else 'FAIL'
        audio = 'audio' if r.get('audio_url') else f"error: {r.get('error')}"
        print(f'{status:4} | {lang}: {audio}')
    except Exception as e:
        print(f'FAIL | {lang}: {str(e)[:40]}')
