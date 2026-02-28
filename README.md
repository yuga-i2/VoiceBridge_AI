# 🌾 VoiceBridge AI — Sahaya

> **AI-powered proactive welfare caller for 135 million Indian farmers**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Amplify-brightgreen)](https://master.dk0lrulrclio3.amplifyapp.com)
[![API Health](https://img.shields.io/badge/API-Lambda-orange)](https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/health)
[![AWS](https://img.shields.io/badge/AWS%20Services-8%2F8-blue)](#architecture)

**🔗 Live Demo:** https://master.dk0lrulrclio3.amplifyapp.com

---

## 💡 Problem

135 million Indian farmers eligible for welfare schemes but 76% never access them.
Field officers cost ₹2,700 per farmer — impossible at national scale.

## 🌟 Solution — Sahaya Calls First

Sahaya calls farmers proactively, speaks Hindi, and guides them through eligibility.
Farmer just answers the phone.

| | Sahaya | Field Officers |
|---|---|---|
| Cost per farmer | ₹15-25 | ₹2,700 |
| Scale | Unlimited | Headcount-limited |
| Languages | Hindi + 4 regional | Hindi only |
| **Savings** | **180× cheaper** | Baseline |

---

## 🏗️ Architecture

```
React (Amplify)
      ↓
API Gateway → Lambda (Flask/Zappa) — ap-southeast-1
      ↓
Bedrock · DynamoDB · S3 · Polly · Transcribe · SNS · Connect
```

**8/8 AWS Services active**

---

## 🎙️ Conversation Flow

1. Sahaya calls first → Hindi greeting + anti-scam disclaimer
2. Eligibility questions → land, KCC, income
3. Scheme matching → 10 DynamoDB records, highlighted live
4. Voice Memory Network → real farmer audio from S3
5. Document guidance → Hindi checklist
6. SMS confirmation → SNS

---

## 🌍 Regional Languages (v1.3.2b)

Sarvam AI Bulbul v2: **Hindi · Tamil · Kannada · Telugu · Malayalam**

---

## 🚀 Quick Start

### Frontend (localhost:3000)
```bash
cd frontend && npm install && npm start
```

### Backend (localhost:5000)
```bash
cd voicebridge-backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # Add AWS credentials
python app.py
```

---

## 📖 Full Documentation

→ [`voicebridge-backend/docs/VOICEBRIDGE_COMPLETE_REFERENCE.md`](./voicebridge-backend/docs/VOICEBRIDGE_COMPLETE_REFERENCE.md)

Complete API reference, DynamoDB schema, S3 structure, troubleshooting, deployment guide.

---

## 🏆 AWS Hackathon 2026 — Submission: March 3, 2026
