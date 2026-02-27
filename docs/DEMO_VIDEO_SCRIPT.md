# SAHAYA DEMO VIDEO SCRIPT
## Complete 3-Minute Recording Guide

---

## 0:00 — 0:08 | TITLE CARD (8 seconds)

**VISUAL:** Dark background (soil brown #2C1810). Large text appears, centered.

**TEXT ON SCREEN:**
```
135 million Indian farmers qualify for welfare.

70% receive nothing.

Not because they don't deserve it.

Because nobody told them.
```

**VOICE:** Silence. Let the text speak.

**TIMING:** 8 seconds. Pause between lines for impact.

---

## 0:08 — 0:25 | THE PROBLEM (17 seconds)

**VISUAL:** 
- First: pmkisan.gov.in form on screen (screenshot). Show complexity.
- Then: Photo of farmer (Ramesh Kumar, 45, Karnataka). Use royalty-free image.
- Then: Land size "2 acres" label appears.

**VOICE (speak clearly, slow pace for translation):**
"Ramesh Kumar. 45 years old. Karnataka. 2 acres of land.
Qualifies for 6 government schemes. Has received zero rupees.
Not because he can't apply. Because nobody told him he qualifies."

**TIMING:** Read slowly. 17 seconds total.

---

## 0:25 — 0:35 | THE SOLUTION (10 seconds)

**VISUAL:**
- Show VoiceBridge React frontend loading
- Sahaya logo appears, pulsing gently
- "Sahaya" text in Hindi: सहाया

**VOICE:**
"We built Sahaya. An AI welfare assistant that calls farmers proactively.
No smartphone. No internet. No office visit. Just one incoming call."

**TIMING:** Fast pace, 10 seconds.

---

## 0:35 — 0:50 | FARMER PROFILE MATCHING (15 seconds)

**VISUAL:**
- React frontend on screen showing Farmer Profile panel
- Load "Ramesh Kumar" profile: name, age, state, land, KCC status
- Schemes appear one by one: PM-KISAN (green), PMFBY (gold), MGNREGS (blue)
- Each scheme card animates in with scheme name and rupee amount

**VOICE:**
"Sahaya checks 10 government schemes in real time using DynamoDB and Bedrock AI.
In 3 seconds, it knows which ones Ramesh qualifies for."

**TIMING:** 15 seconds. Sync scheme animations with voice.

---

## 0:50 — 1:35 | THE CALL (45 seconds)

### 0:50 — 0:57 | CALL INITIATION

**VISUAL:**
- Continue React frontend
- Click "Initiate Sahaya Call" button (green, prominent)
- Terminal window appears on side showing: `Call SID: CA...`

**VOICE:**
"Pressing the call button. Twilio instantly dials Ramesh."

**TIMING:** 7 seconds.

---

### 0:57 — 1:05 | STAGE 1 INTRO + ANTI-SCAM

**VISUAL:**
- Phone mockup on left showing "SAHAYA calling..." 
- Animated transcription on right showing what Sahaya is saying
- Red banner appears: "🛡️ ANTI-SCAM GUARANTEE"

**PLAY AUDIO:** `demo_audio/01_intro.mp3`
(Or show transcription while audio plays: "Namaste Ramesh Kumar jii. Main Sahaya hoon...")

**VOICE (narration over audio):**
"Sahaya introduces herself. Anti-scam statement first — always. This is baked into every single call by design."

**AWS SERVICE HIGHLIGHT:** Amazon Polly logo appears, glowing green (bottom right corner)

**TIMING:** 8 seconds.

---

### 1:05 — 1:20 | VOICE MEMORY NETWORK CLIP

**VISUAL:**
- Phone mockup still showing call active
- Animated waveform showing "peer farmer audio playing"
- Text overlay: "Suresh Kumar, Tumkur district — PM-KISAN success story"
- AWS S3 logo appears and glows green

**PLAY AUDIO:** 30-second Voice Memory clip (actual or description: "Mera nam Suresh hai. PM-KISAN se mujhe...")

**VOICE (narration):**
"Then the Voice Memory Network. A real farmer from Tumkur speaks for 30 seconds.
Peer trust. In their own voice. No government worker can do this."

**TIMING:** 15 seconds total (combining narration + audio).

---

### 1:20 — 1:28 | ELIGIBILITY QUESTIONS

**VISUAL:**
- Phone mockup showing DTMF tone pad appearing
- Animated keypresses: "1" for land size, "2" for KCC
- AWS DynamoDB logo glows green (bottom right)

**PLAY AUDIO:** 
- `demo_audio/04_land_question.mp3` (land size question)
- `demo_audio/05_kcc_question.mp3` (KCC question)

**VOICE (narration):**
"Two questions. Farmer presses 1 or 2 on their keypad. That's it.
No forms. No literacy required."

**TIMING:** 8 seconds.

---

### 1:28 — 1:35 | PERSONALIZED SCHEME EXPLANATION + DOCUMENTS

**VISUAL:**
- Phone mockup shows "Scheme explanation playing"
- Animated text: "PM-KISAN: ₹6,000/year, 3 installments"
- Scheme comparison shows benefits (rupee amounts, documents needed)
- AWS Bedrock logo glows green
- AWS SNS logo glows green (SMS being sent)

**PLAY AUDIO:**
- `demo_audio/06_scheme_match.mp3` (Bedrock AI explanation)
- `demo_audio/07_documents.mp3` (document requirements)
- `demo_audio/08_sms_sent.mp3` (SMS confirmation)

**VOICE (narration):**
"Bedrock AI generates a personalized explanation. Real rupee amounts.
Real scheme name in Hindi. SMS arrives instantly with complete checklist."

**TIMING:** 7 seconds of narration + 10+ seconds of audio.

---

## 1:35 — 1:55 | AWS ARCHITECTURE (20 seconds)

**VISUAL:** AWS Console split-screen showing:

1. **Amazon Bedrock** (first flip, 4 seconds)
   - Show Claude 3 Haiku model access
   - Input: farmer profile, schemes, language = Hindi
   - Output: personalized explanation

2. **Amazon DynamoDB** (second flip, 4 seconds)
   - Show welfare_schemes table
   - 10 items showing (PM-KISAN, KCC, PMFBY, etc.)
   - 6,000 rupees per year highlighted

3. **Amazon S3** (third flip, 4 seconds)
   - Show voicebridge-audio-yuga bucket
   - MP3 files visible (voice memory clips)
   - Presigned URLs being generated

4. **Amazon Connect** (fourth flip, 4 seconds)
   - Show voicebridge-demo instance active
   - Outbound call status: "Connected"
   - Call log showing call history

5. **Amazon Polly** (fifth flip, 4 seconds)
   - Show Kajal voice settings
   - Hindi language selected
   - Neural voice: High quality

**VOICE:**
"Eight AWS services. All live. All real. All in Singapore ap-southeast-1.
Not mocked for the demo. Every service is production-ready."

**TIMING:** 20 seconds (4s per service + voice).

---

## 1:55 — 2:05 | SMS PROOF (10 seconds)

**VISUAL:**
- Phone screen (mobile mockup) showing actual SMS received
- SMS in Hindi: Document list, CSC center address, scheme details
- Timestamp showing SMS arrived immediately after call

**VOICE:**
"Farmer gets this SMS even if they hung up. Even on 2G. Even if the call was 15 seconds long."

**TIMING:** 10 seconds. Let SMS be clearly readable on screen.

---

## 2:05 — 2:25 | IMPACT ECONOMICS (20 seconds)

**VISUAL:**
- Split-screen comparison:
  - LEFT: "Traditional Outreach" (red tint)
    - ₹2,700 per farmer (large text)
    - Field officer photo
    - "Limited by workforce"
  - RIGHT: "Sahaya" (green tint)
    - ₹15 per farmer (large text, gold color)
    - Phone icon
    - "Unlimited scale"
- Between them: Large text "180×" in gold rotating/pulsing

**VOICE:**
"Traditional government outreach: ₹2,700 per farmer. Sahaya: ₹15 per farmer.
That is a 180 times cost reduction. At 135 million farmers — that is
₹36,000 crore in savings. The same budget reaches 180 times more farmers."

**TIMING:** 20 seconds.

---

## 2:25 — 2:35 | PRIVACY & COMPLIANCE (10 seconds)

**VISUAL:**
- React frontend showing DPDP compliance banner
- "🛡️ DPDP Act 2023 Compliant" badge appears
- Anti-scam guarantee repeated: "Never asks for: Aadhaar • OTP • Bank Password"
- Green checkmarks appear next to each guarantee

**VOICE:**
"DPDP Act 2023 compliant by design. Sahaya never stores Aadhaar, OTP,
or bank data. Privacy protection is not a feature. It is the foundation."

**TIMING:** 10 seconds.

---

## 2:35 — 3:00 | CLOSING VISION (25 seconds)

**VISUAL:**
- Fade back to Ramesh Kumar farmer photo (from 0:08)
- Overlay text appearing, one line at a time:
  - "Doesn't need a smartphone"
  - "Doesn't need internet"
  - "Doesn't need to visit any office"
  - "Doesn't need to speak English"
  - "Just needs to answer one call"

**VOICE (spoken slowly, with emotion):**
"Ramesh doesn't need a smartphone.
Doesn't need internet.
Doesn't need to visit any office.
Doesn't need to speak English.
He just needs to answer one call.
That call is Sahaya."

**TIMING:** 20 seconds voice + final text.

---

## 2:55 — 3:00 | FINAL FRAME (5 seconds)

**VISUAL:**
- All AWS logos appearing in a circle, glowing green
- Center text:
  ```
  VoiceBridge AI — Sahaya
  Built for 135 million farmers
  ```
- GitHub URL displayed: github.com/yuga-i2/VoiceBridge_AI
- Live demo URL displayed: yuga-i2.github.io/VoiceBridge_AI

**VOICE:**
(fade to silence)

**MUSIC:** Soft, uplifting instrumental (royalty-free) fades in during 2:35-3:00

**TIMING:** Final 5 seconds.

---

## TECHNICAL RECORDING NOTES

### Software Setup
- Screen recording software: OBS Studio (free) or ScreenFlow (Mac)
- Audio: Microphone for narration + system audio for Sahaya voice
- Resolution: 1080p (1920×1080)
- Frame rate: 30 fps

### Narration Recording Tips
- Record narration separately, sync with screen recording later
- Speak clearly, slow enough for subtitles/translation
- Leave 1-second pauses between sentences
- Re-record sections if you make mistakes

### Screen Order
1. React frontend (farmer profile, scheme matching)
2. Call initiation button click
3. Phone mockup animation
4. AWS console screenshots (flip one by one)
5. SMS on phone screen
6. Final closing frame

### Audio Track
- Narration: Your voice (left channel)
- Sahaya voice: Polly Kajal Hindi (center/right channel) 
- Music: Royalty-free instrumental (background, low volume)
- Levels: Narration -6dB, Sahaya +0dB, Music -20dB

### Color Scheme (for visual consistency)
- Primary: Soil brown #2C1810
- Success/Active: Leaf green #4A7C44
- Highlight/Numbers: Gold #DAA520
- Text: Off-white #F5F5F5
- AWS Orange: #FF9900

### Post-Production
- Add subtitles in Hindi + English
- Add title card music (2-3 seconds)
- Add background music (low volume throughout)
- Fade in/out each section
- Total target duration: 3:00 (exactly 180 seconds)

---

## DELIVERY CHECKLIST

Before uploading demo video:
- [ ] All 9 audio segments play clearly
- [ ] Narration is clear and paced well
- [ ] Timestamps match script (0:00, 0:08, 0:25, etc.)
- [ ] AWS services are all highlighted
- [ ] Farmer story (Ramesh) is clear from opening
- [ ] Problem statement 135M farmers is visible
- [ ] ₹15 vs ₹2,700 comparison is clear
- [ ] DPDP compliance badge is shown
- [ ] SMS screenshot is legible
- [ ] Final URLs are visible for 5 seconds
- [ ] Total duration is 3:00 ± 2 seconds
- [ ] Video quality is 1080p or better
- [ ] Audio is clear (no background noise during narration)
- [ ] Subtitles added (if translating for international judges)

---

## THIS IS YOUR SCRIPT

Print this page. Read it while recording. Every word counts.
This script turns a technical project into a compelling story.
The story is: "One farmer. One phone. One call. Changed everything."

Now record it.
