# VoiceBridge AI — Quick Reference: Deployment Checklist

## What Just Happened (This Commit)

**CRITICAL ARCHITECTURAL FIX:**
- Frontend was calling `api.anthropic.com` directly ❌ (WRONG - judges see zero AWS)
- Frontend now calls our Flask backend ✅ (CORRECT - judges see all 10 AWS services)

**Files Created/Modified:**
```
✅ frontend/src/services/api.js          — API layer (calls Flask only)
✅ frontend/.env.development              — Dev config (localhost:5000)
✅ frontend/.env.production               — Prod config (Lambda URL)
✅ voicebridge-backend/zappa_settings.json — Lambda deployment config
✅ voicebridge-backend/requirements.txt    — +zappa for Lambda
✅ DEPLOYMENT.md                           — Full 50-page guide
```

---

## 7-Step Deployment (35-50 minutes total)

### STEP 1: Deploy Backend to Lambda (10 min)
```bash
cd voicebridge-backend
python -m venv venv
venv\Scripts\activate        # Windows
# OR: source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
pip install zappa

zappa deploy dev
```
**SAVE URL:** `https://xxxxxxxxxx.execute-api.ap-southeast-1.amazonaws.com/dev`

### STEP 2: Add Secrets to Lambda (5 min)
1. AWS Console → Lambda → voicebridge-dev
2. Configuration → Environment variables → Edit
3. Add these 9 variables (from your local .env):
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - TWILIO_ACCOUNT_SID
   - TWILIO_AUTH_TOKEN
   - TWILIO_PHONE_NUMBER
   - TWILIO_VERIFIED_NUMBER
   - WEBHOOK_BASE_URL (your Lambda URL)
   - CONNECT_INSTANCE_ID
   - CONNECT_CONTACT_FLOW_ID
4. Click Save

### STEP 3: Update Frontend Config (2 min)
Edit: `frontend/.env.production`
```
REACT_APP_API_URL=https://xxxxxxxxxx.execute-api.ap-southeast-1.amazonaws.com/dev
```
(Use your ACTUAL Lambda URL from STEP 1)

### STEP 4: Build Frontend (5 min)
```bash
cd frontend
npm install
npm run build
```
Creates: `frontend/build/` (~2MB optimized)

### STEP 5: Deploy to Amplify (15 min)
1. AWS Console → Amplify → New app → Host web app
2. GitHub → select VoiceBridge_AI repo → Branch master
3. Add environment variable:
   ```
   REACT_APP_API_URL = https://xxxxxxxxxx.execute-api.ap-southeast-1.amazonaws.com/dev
   ```
4. Click "Save and deploy"
5. Wait 5-10 minutes for build

**SAVE URL:** `https://main.xxxxxxxxxx.amplifyapp.com`

### STEP 6: Test Everything (5 min)
See DEPLOYMENT.md → TASK 6 → Run full test suite

### STEP 7: Verify in Browser (2 min)
Open: `https://main.xxxxxxxxxx.amplifyapp.com`

Click "Load Demo Farmer (Ramesh Kumar)"
Click "Start Talking to Sahaya"
Type: "PM-KISAN ke baare mein batao"

Should see:
- ✅ Hindi response from Claude (Bedrock)
- ✅ Real audio playing (Polly)
- ✅ AWS services lighting up
- ✅ Scheme matches appearing
- ✅ Voice Memory clip (farmer testimonial)

---

## What Judges Will See

| Component | Technology | Live? |
|-----------|-----------|-------|
| Frontend | React → Amplify | ✅ Yes |
| Backend API | Flask → Lambda + API Gateway | ✅ Yes |
| AI Brain | Claude 3 Haiku → Bedrock | ✅ Yes |
| Database | Welfare schemes → DynamoDB | ✅ Yes |
| Voice Generation | Hindi TTS → Polly | ✅ Yes |
| Eligibility Check | Logic + DynamoDB queries | ✅ Yes |
| Voice Memory Clips | Farmer testimonials → S3 | ✅ Yes |
| Phone Calling | Outbound dial → Connect | ✅ Yes |
| SMS Alerts | Document guidance → SNS | ✅ Yes |
| Frontend Hosting | CDN deployment → Amplify | ✅ Yes |

---

## Key URLs After Deployment

- **Frontend URL** (judges visit): `https://main.xxxxxxxxxx.amplifyapp.com`
- **Backend API** (hidden, frontend uses): `https://xxxxxxxxxx.execute-api.ap-southeast-1.amazonaws.com/dev`
- **AWS Services**: All in ap-southeast-1 region
- **GitHub Repo**: https://github.com/yuga-i2/VoiceBridge_AI

---

## Before Submitting

- [ ] Both URLs working (test in browser)
- [ ] Test suite passing (DEPLOYMENT.md TASK 6)
- [ ] Record 3-min demo video of full interaction
- [ ] Update README.md with live URLs
- [ ] Final commit: `git commit -m "Production deployment live"`
- [ ] Push: `git push origin master`
- [ ] Submit to Hack2Skill with:
  - GitHub URL
  - Live Demo URL
  - Demo video link

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Lambda times out | Increase timeout in zappa_settings.json to 120s, run `zappa update dev` |
| Frontend can't reach backend | Check REACT_APP_API_URL in .env.production |
| CORS errors | Verify Lambda environment variable CORS_ORIGINS includes Amplify URL |
| DynamoDB 403 error | Check IAM user has AmazonDynamoDBFullAccess |
| Amplify build fails | Check npm logs, usually missing package — run `npm install` |

---

## Full Documentation

See `DEPLOYMENT.md` for:
- Detailed step-by-step instructions
- AWS credential setup
- S3 bucket creation
- Complete test suite
- Troubleshooting guide

---

## What This Fixes

**Problem:** Frontend called anthropic.com directly
- ❌ Judges saw zero AWS services
- ❌ Looked like simple Claude API wrapper
- ❌ Zero points on "AWS Implementation" criterion

**Solution:** Frontend calls Flask backend
- ✅ Judges see all 10 AWS services firing
- ✅ Each response demonstrates: Bedrock + DynamoDB + Polly + etc
- ✅ Full points on "AWS Implementation" criterion

---

## Timeline

- Commit 8cf044a: Infrastructure ready
- Steps 1-7: 35-50 minutes
- Test suite: 5 minutes
- Demo video: 10 minutes
- Total: **~60 minutes from now to submission-ready**

---

**NEXT ACTION:** Start STEP 1 above  
**REFERENCE:** Open DEPLOYMENT.md in side-by-side editor while following these steps

Good luck! 🚀
