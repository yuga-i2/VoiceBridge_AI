#!/usr/bin/env python
# Script to fix voice memory deduplication in app.py

with open('voicebridge-backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace from "Check if we've already" to the break line
old_text = '''        # Check if we've already played voice memory for this scheme in the conversation
        if final_voice_clip and history and len(history) > 1:
            # Keywords that indicate voice memory was already played
            # Includes farmer names, success story indicators, specific scheme mentions
            vm_keywords = {
                'PM_KISAN': {
                    'hindi': ['सुनीता', 'sunitha', 'farmer', 'success', 'story', 'कहानी', '6000'],
                    'malayalam': ['പ്രിയ', 'priya', 'നന്ദി', 'കഥ', 'കേരളം', 'കൃഷി'],
                    'tamil': ['విചయ', 'farmer', 'success', 'കഥ'],
                    'marathi': ['सुनीता', 'sunita', 'farmer', 'कहानी']
                },
                'KCC': {
                    'hindi': ['किसान credit', 'farmer credit', 'credit card', 'card holder'],
                    'malayalam': ['കടം', 'കാര്ഷിക', 'വിതരണം', 'ബാങ്ക്']
                },
                'PMFBY': {
                    'hindi': ['बीमा', 'insurance', 'crop', 'फसल', 'premium'],
                    'malayalam': ['ഇൻസുറൻസ്', 'ബീമ', 'സുരക്ഷ', 'കൃഷി']
                }
            }
            
            # Scan assistant messages to see if this scheme's VM already played
            for msg in history:
                if msg.get('role') == 'assistant':
                    response_text = (msg.get('content') or msg.get('response_text') or '').lower()
                    
                    # Check if any VM keywords for this scheme appear in previous responses
                    if final_voice_clip in vm_keywords:
                        all_keywords = []
                        # Combine keywords from all languages
                        for lang_keywords in vm_keywords[final_voice_clip].values():
                            all_keywords.extend(lang_keywords)
                        
                        # If any keyword matches, skip this voice memory
                        if any(kw.lower() in response_text for kw in all_keywords):
                            logger.info(f"[FIX 4] Voice memory for {final_voice_clip} already played - skipping")
                            final_voice_clip = None
                            break'''

new_text = '''        # Check if we've already played voice memory for this scheme in the conversation
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
                final_voice_clip = None'''

if old_text in content:
    new_content = content.replace(old_text, new_text, 1)
    with open('voicebridge-backend/app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✓ Voice memory dedup logic fixed successfully!")
else:
    print("✗ Could not find exact string to replace")
    # Try to find what we have
    if "# Check if we've already played" in content:
        print("  Found start marker")
    if "if any(kw.lower() in response_text" in content:
        print("  Found inner marker")

