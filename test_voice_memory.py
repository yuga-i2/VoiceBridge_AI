from services.voice_memory_service import get_clip

print('Testing S3 Voice Memory...')
for scheme_id in ['PM_KISAN', 'KCC', 'PMFBY']:
    result = get_clip(scheme_id)
    url = result.get('audio_url', 'None')
    url_short = url[:50] if url else 'None'
    print(f'{scheme_id}: success={result["success"]}, url={url_short}')

print()
all_success = all(get_clip(s)['success'] for s in ['PM_KISAN', 'KCC', 'PMFBY'])
if all_success:
    print('PASS: S3 voice memory working')
else:
    print('FAIL: Some clips missing')
