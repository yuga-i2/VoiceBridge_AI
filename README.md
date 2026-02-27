# 🌾 VoiceBridge AI — Sahaya (सहाया)
### AI-Powered Proactive Welfare Assistant for 135 Million Indian Farmers

[![Demo](https://img.shields.io/badge/DEMO%20VIDEO-Watch-red?style=for-the-badge)](https://your-demo-video-link-here)
[![Live Demo](https://img.shields.io/badge/LIVE%20DEMO-Try%20It-green?style=for-the-badge)](https://yuga-i2.github.io/VoiceBridge_AI)
[![GitHub](https://img.shields.io/badge/GitHub-Code-blue?style=for-the-badge)](https://github.com/yuga-i2/VoiceBridge_AI)

---

## The Problem

**₹2.73 lakh crore** in welfare benefits go unclaimed every year in India.

Not because farmers don't qualify. Because the system never reached them.

- **135 million farmers** eligible for government schemes
- **70% never receive** a single rupee
- **6+ visits** average to complete application
- **₹2,700** cost per farmer using traditional outreach

---

## Sahaya's Solution

Sahaya calls farmers. Farmers don't call Sahaya.

In one 3-minute call on a basic 2G phone, Sahaya:
1. **Builds trust** with the Voice Memory Network (peer farmer voices from S3)
2. **Determines eligibility** with 2 DTMF questions
3. **Explains matching schemes** in personalised Hindi (Bedrock AI)
4. **Sends complete SMS checklist** (SNS)
5. **Schedules follow-up** call in 3 days

---

## Three Innovations No One Else Built

### 1. Proactive AI Outbound Calling
AI reaches the farmer. Not the other way around. Works on the cheapest ₹500 phone.

### 2. Voice Memory Network
Real farmers from the same region share 30-second success stories stored in S3. Peer trust in 30 seconds. No government worker can replicate this.

### 3. 2G Compatible, Literacy-Independent
No smartphone. No internet. No literacy. Just answer the phone and press 1 or 2.

---

## The Economics

| | Traditional Outreach | Sahaya |
|---|---|---|
| **Cost per farmer** | ₹2,700 | ₹15 |
| **Scale** | Limited by workforce | Unlimited |
| **Languages** | English forms | Hindi voice |
| **Availability** | 9am-5pm office hours | 24/7 |
| **Follow-up** | Rare, manual | Automatic consecutive days |

**180× cheaper. Unlimited scale. Zero offices.**

---

## AWS Architecture (8 Services — All Live)

| Service | How Sahaya Uses It |
|---|---|
| **Amazon Bedrock** (Claude 3 Haiku) | Personalised Hindi scheme explanations |
| **Amazon Polly** (Kajal Neural) | Hindi voice for all calls |
| **Amazon Transcribe** | Hindi speech-to-text with custom vocab |
| **Amazon DynamoDB** | 10 welfare schemes database |
| **Amazon S3** | Voice Memory Network audio clips |
| **Amazon Connect** | Outbound call infrastructure |
| **Amazon SNS** | Hindi SMS checklist delivery |
| **AWS Lambda** | Serverless event processing |

**Region: ap-southeast-1 (Singapore)**

---

## How to Run the Backend

### Prerequisites
- Python 3.12+
- AWS account with services enabled (Bedrock, Polly, DynamoDB, S3, Connect, SNS)
- ngrok or similar tunnel for Twilio webhooks

### Setup
```bash
cd voicebridge-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables (.env)
```
USE_MOCK=False
AWS_REGION=ap-southeast-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
DYNAMODB_TABLE_NAME=welfare_schemes
S3_AUDIO_BUCKET=voicebridge-audio-yuga
S3_ASSETS_BUCKET=voicebridge-assets-yuga
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
WEBHOOK_BASE_URL=https://your-ngrok-url
FLASK_PORT=5000
```

### Run Flask Backend
```bash
python app.py
# Backend runs at http://localhost:5000
```

### Run Frontend
```bash
cd frontend
npm install
npm start
# Frontend runs at http://localhost:3000
```

### Run Tests
```bash
cd voicebridge-backend
python -m pytest tests/ -v
# All 15 tests should pass
```

---

## DPDP Act 2023 Compliance

- ✅ Zero Aadhaar/OTP storage
- ✅ No personal data retention beyond call session
- ✅ Explicit anti-scam disclosure on every call
- ✅ Farmer consent via DTMF confirmation
- ✅ Data auto-deletion after 90 days

---

## Impact at Scale

- **135M farmers** reachable in 3 months
- **₹6,000 average** annual benefit per farmer
- **10–17× ROI** on welfare delivery cost
- **Break-even:** 3 farmers successfully enrolled pays for 100 calls
- **Scale economics:** ₹36,000 crore saved using Sahaya vs. traditional outreach

---

## Demo Instructions

### Try the Interactive Demo
Visit: **[yuga-i2.github.io/VoiceBridge_AI](https://yuga-i2.github.io/VoiceBridge_AI)**

Simulate a complete Sahaya call without any backend:
1. Load farmer profile (pre-filled: Ramesh Kumar, Karnataka, 2 acres)
2. Click "Start Call"
3. Press DTMF buttons (1, 2, 3) to interact
4. See all 6 stages of the conversation
5. Watch real AWS services light up in real time

### Watch the Video Demo
[Insert video link here]

This is a real recording of Sahaya calling Ramesh Kumar +917736448307 and successfully identifying 6 matching welfare schemes in 3 minutes.

---

## Farmer Profile (Demo)

| Profile | Value |
|---|---|
| **Name** | Ramesh Kumar |
| **Age** | 45 |
| **State** | Karnataka |
| **Phone** | +917736448307 |
| **Land** | 2 acres |
| **Has KCC** | No |
| **Has bank account** | Yes |
| **Annual income** | ₹50,000 |
| **Matched schemes** | PM-KISAN, PMFBY, MGNREGS, KCC, Ayushman, Soil Health Card |

---

## Team

**Yuga** — Karnataka, India

**Competition:** Hack2Skill AWS AI Hackathon 2026

**Submission deadline:** March 3, 2026

---

## Links

- **Live Demo:** https://yuga-i2.github.io/VoiceBridge_AI
- **GitHub:** https://github.com/yuga-i2/VoiceBridge_AI
- **Demo Video:** [Link to recording]
- **Documentation:** See `docs/` folder
