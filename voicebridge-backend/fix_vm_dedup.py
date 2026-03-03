#!/usr/bin/env python
# Fix voice memory deduplication to use voiceMemoryScheme field

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find start of problematic block
start = None
for i, line in enumerate(lines):
    if "Check if we've already played" in line:
        start = i
        break

end = None
if start:
    # Find the end - look for "# Generate TTS audio"
    for i in range(start, len(lines)):
        if "# Generate TTS audio for Sahaya" in lines[i]:
            end = i
            break

if start is not None and end is not None:
    print(f"Found block from line {start+1} to {end}")
    
    # Create new dedup code
    new_block = '''        # Check if we've already played voice memory for this scheme in the conversation
        if final_voice_clip and history and len(history) > 1:
            schemes_with_vm_already_played = set()
            
            # Scan history for voiceMemoryScheme field (sent by frontend when VM is played)
            for msg in history:
                if msg.get('role') == 'assistant':
                    # Frontend sends voiceMemoryScheme when voice memory is played
                    if msg.get('voiceMemoryScheme'):
                        schemes_with_vm_already_played.add(msg.get('voiceMemoryScheme'))
            
            # Skip voice memory if already played in this conversation
            if final_voice_clip in schemes_with_vm_already_played:
                logger.info(f"[FIX 4] Voice memory for {final_voice_clip} already played in conversation - skipping")
                final_voice_clip = None
        
'''
    
    # Replace lines
    new_lines = lines[:start] + [new_block] + lines[end:]
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("SUCCESS: Voice memory dedup fixed!")
else:
    print(f"ERROR: Could not find block to replace (start={start}, end={end})")
