# 🌾 VoiceBridge AI — Sahaya (सहाया)

> **AI that calls farmers. Farmers don't call AI.**

[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-brightgreen)](https://yuga-i2.github.io/VoiceBridge_AI)
[![GitHub](https://img.shields.io/badge/GitHub-VoiceBridge_AI-blue)](https://github.com/yuga-i2/VoiceBridge_AI)

---

## The Problem

**₹2.73 lakh crore** in welfare benefits go unclaimed every year in India.

Not because farmers don't qualify. Because nobody told them.

| Barrier | Reality |
|---------|---------|
| Web portals | Assume English literacy → 95% dropout |
| Mobile apps | Need smartphone → 58% excluded |
| Call centres | Reactive → farmer must call → 5% completion |
| Field officers | ₹2,700 per farmer → only 200,000/year reached |

**135 million farmers are eligible. 70% receive nothing.**

---

## Sahaya's Solution

In one 3-minute call on a basic 2G phone, Sahaya:

1. **Builds trust** — plays a 30-second peer success story from the farmer's district
2. **Asks 2 questions** — land size + KCC status (press 1 or 2)
3. **Matches schemes** — Bedrock AI + DynamoDB → correct schemes in seconds
4. **Explains clearly** — personalised Hindi explanation with exact rupee amounts
5. **Sends checklist** — SMS with documents needed + where to go
6. **Follows up** — calls again in 3 days to check progress

---

## Three Innovations

### 🔊 Voice Memory Network
Real 30-second audio clips from farmers in the same district sharing their success.  
Stored in Amazon S3. Played during every call before asking any question.  
**Peer trust in 30 seconds.** No government worker can replicate this.

### 📞 Proactive AI Outbound Calling
The system calls the farmer. Farmer does nothing.  
Works on any phone that can receive calls. No smartphone. No internet.  
**Zero digital literacy required.**

### 🌾 2G Feature Phone Compatible
A ₹500 Nokia from 2005 is enough.  
Voice call + SMS = full welfare guidance delivered.  
**Reaches 58% of rural India.**

---

## AWS Architecture — 8 Live Services

| Service | How Sahaya Uses It |
|---------|-------------------|
| 🧠 **Amazon Bedrock** (Claude 3 Haiku) | Personalised Hindi scheme explanations |
| 🔊 **Amazon Polly** (Kajal Neural) | Hindi voice on every call |
| 🎙️ **Amazon Transcribe** | Hindi speech-to-text with custom vocabulary |
| 🗄️ **Amazon DynamoDB** | 10 welfare schemes database with real rupee amounts |
| 📦 **Amazon S3** | Voice Memory Network audio clips from real farmers |
| 📞 **Amazon Connect** | Outbound call infrastructure |
| 💬 **Amazon SNS** | Hindi SMS document checklist |
| ⚡ **AWS Lambda** | Serverless event processing |

**Region: ap-southeast-1 (Singapore) | All services LIVE | All REAL, not mocked**

---

## The Economics

```
Traditional outreach:     ₹2,700 per farmer
Sahaya:                   ₹15 per farmer
                          ─────────────────
Cost reduction:           180× cheaper

At 135 million farmers:   ₹36,000 crore in savings
ROI:                      10:1 to 17:1 on welfare delivered
```

---

## Running Locally

### Backend (Flask)
```bash
cd voicebridge-backend
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
# Edit .env — add your AWS and Twilio credentials
python app.py
```

### Frontend (React)  
```bash
cd voicebridge-frontend
npm install && npm run dev
# Opens on http://localhost:3000
```

### Run Tests
```bash
cd voicebridge-backend
python -m pytest tests/ -v
```

---

## Making a Live Call

```bash
# Update .env: CALL_PROVIDER=twilio
# Start ngrok: ngrok http 5000
# Set WEBHOOK_BASE_URL in .env to your ngrok URL
python tests/test_call_system.py
# Phone rings → press any key to continue (Twilio trial message) → hear Sahaya in Hindi
```

---

## Privacy & Compliance

- ✅ **DPDP Act 2023 Compliant** by design
- ✅ Zero Aadhaar storage — never collected
- ✅ Zero OTP collection — never requested  
- ✅ Auto-delete after 90 days
- ✅ Anti-scam statement on every single call
- ✅ Farmer consent via DTMF before any personal question

---

## Project Structure

```
voicebridge-backend/      Flask API backend (8 endpoints)
  ├── app.py              Flask app with all blueprints
  ├── routes/call_routes.py  TwiML 6-stage call flow
  ├── services/           AWS integrations + AI
  ├── models/farmer.py    Farmer profile dataclass
  ├── tests/              All 4 tests PASSING
  └── docs/               Constraint docs + submission text

voicebridge-frontend/     React frontend (Amplify)
  └── src/components/     7 components for farmer interaction
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Farmers currently excluded | 135 million |
| Cost per farmer (traditional) | ₹2,700 |
| Cost per farmer (Sahaya) | ₹15 |
| Cost multiplier | 180× cheaper |
| Annual investment needed | ₹2,025 crore |
| Break-even | 3 successful farmers / 100 calls |
| Call duration | 3 minutes avg |
| Farmer profiles supported | All Indian states |

---

## Farmer Example

**Ramesh Kumar** | 45 years old | Karnataka | 2 acres | No KCC

Sahaya calls Ramesh at 2:30 PM.  
Hears Suresh Kumar's success story from Tumkur (same district).  
Presses "2" for 2-5 acres. Presses "2" (no KCC).  
Sahaya identifies 6 matching schemes. Explains PM-KISAN (₹6,000/year).  
Receives SMS with documents list + CSC location.  
3 days later: Sahaya calls again. Ramesh applied. Documents approved.  
Week 5: First ₹2,000 installment hits bank account.

**Outcome:** Ramesh gets ₹6,000/year ongoing. Sahaya cost: ₹15. ROI: 400×

---

## The 10 Welfare Schemes

All amounts verified against official government sources:

1. **PM-KISAN** — ₹6,000/year in 3 installments
2. **KCC** — Crop loan up to ₹3 lakh @ 4% interest
3. **PMFBY** — Crop insurance @ 2% premium  
4. **Ayushman Bharat** — ₹5 lakh/family/year health
5. **MGNREGS** — 100 days work @ ₹220-357/day
6. **Soil Health Card** — Free soil testing
7. **PM Awas Gramin** — Housing subsidy ₹1.2L
8. **NFSA Ration** — Subsidised grain ₹1-3/kg
9. **Atal Pension** — Retirement ₹1,000-5,000/month
10. **Sukanya Samriddhi** — Girl child savings @ 8.2%

---

*Hack2Skill AWS AI Hackathon 2026*  
*Team: VoiceBridge AI*  
*"135 million farmers. ₹15 per call. Sahaya calls them."*
