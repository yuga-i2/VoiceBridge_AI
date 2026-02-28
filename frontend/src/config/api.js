// ─── VoiceBridge API Configuration ───────────────────────────────────────────
// Single source of truth for all backend API calls.
// Backend: AWS Lambda + API Gateway (ap-southeast-1, Singapore)
// ──────────────────────────────────────────────────────────────────────────────

const API_BASE = process.env.REACT_APP_API_URL
  || 'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev'

console.log('[VoiceBridge] API_BASE configured:', API_BASE)

export const API = {
  health:           `${API_BASE}/api/health`,
  schemes:          `${API_BASE}/api/schemes`,
  eligibilityCheck: `${API_BASE}/api/eligibility-check`,
  chat:             `${API_BASE}/api/chat`,
  tts:              `${API_BASE}/api/text-to-speech`,
  sarvamTts:        `${API_BASE}/api/sarvam-tts`,
  stt:              `${API_BASE}/api/speech-to-text`,
  voiceMemory:      `${API_BASE}/api/voice-memory`,
  initiateCall:     `${API_BASE}/api/initiate-call`,
}

export default API
