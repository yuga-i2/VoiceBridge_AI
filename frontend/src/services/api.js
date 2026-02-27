/**
 * VoiceBridge AI — API Service Layer
 * 
 * ALL frontend API calls MUST go through here.
 * This ensures we call our Flask backend on AWS Lambda,
 * NOT Anthropic directly. We need AWS service integration
 * to demonstrate Bedrock, DynamoDB, Polly, Transcribe etc.
 */

const BACKEND_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000'

/**
 * Generic API call handler with error handling
 */
const call = async (method, path, body = null) => {
  try {
    const options = {
      method,
      headers: { 'Content-Type': 'application/json' },
    }
    if (body) options.body = JSON.stringify(body)
    
    const response = await fetch(`${BACKEND_URL}${path}`, options)
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error(`API call failed: ${method} ${path}`, error)
    throw error
  }
}

/**
 * ════════════════════════════════════════════════════
 * CORE ENDPOINTS — All call our Flask backend on Lambda
 * ════════════════════════════════════════════════════
 */

/**
 * Health check — proves backend is live
 */
export const getHealth = () => call('GET', '/api/health')

/**
 * Get all 10 welfare schemes from DynamoDB
 */
export const getSchemes = () => call('GET', '/api/schemes')

/**
 * Check farmer eligibility against schemes (DynamoDB + logic)
 */
export const checkEligibility = (farmerProfile) =>
  call('POST', '/api/eligibility-check', { farmer_profile: farmerProfile })

/**
 * MAIN CONVERSATION — uses Bedrock Claude 3 Haiku
 * Calls our Flask backend which calls Amazon Bedrock
 */
export const chat = (message, farmerProfile, conversationHistory) =>
  call('POST', '/api/chat', {
    message,
    farmer_profile: farmerProfile,
    conversation_history: conversationHistory,
  })

/**
 * Hindi text-to-speech via Polly
 * Calls our Flask backend which calls Amazon Polly
 */
export const textToSpeech = (text, voice = 'Kajal') =>
  call('POST', '/api/text-to-speech', { text, voice })

/**
 * Hindi speech-to-text via Transcribe
 * Calls our Flask backend which calls Amazon Transcribe
 */
export const speechToText = (audioBase64, mimeType = 'audio/webm') =>
  call('POST', '/api/speech-to-text', {
    audio_data: audioBase64,
    mime_type: mimeType,
  })

/**
 * Get Voice Memory Network peer clip from S3
 * Farmer testimonial for scheme
 */
export const getVoiceMemory = (schemeId) =>
  call('GET', `/api/voice-memory/${schemeId}`)

/**
 * Initiate outbound call via Amazon Connect or Twilio
 * Calls our Flask backend which triggers real phone call
 */
export const initiateCall = (farmerPhone, farmerName, schemeIds) =>
  call('POST', '/api/initiate-call', {
    farmer_phone: farmerPhone,
    farmer_name: farmerName,
    scheme_ids: schemeIds,
  })

/**
 * Send SMS with scheme documents via SNS
 * Calls our Flask backend which calls Amazon SNS
 */
export const sendSms = (phoneNumber, schemeIds) =>
  call('POST', '/api/send-sms', {
    phone_number: phoneNumber,
    scheme_ids: schemeIds,
  })

/**
 * ════════════════════════════════════════════════════
 * CRITICAL: Every API call above goes to our Flask backend
 * The Flask backend is deployed on AWS Lambda + API Gateway
 * The Flask backend is what calls Amazon Bedrock, Polly, etc.
 * 
 * DO NOT add any direct Anthropic API calls in React code.
 * DO NOT call api.anthropic.com from the browser.
 * ════════════════════════════════════════════════════
 */

export default {
  getHealth,
  getSchemes,
  checkEligibility,
  chat,
  textToSpeech,
  speechToText,
  getVoiceMemory,
  initiateCall,
  sendSms,
}
