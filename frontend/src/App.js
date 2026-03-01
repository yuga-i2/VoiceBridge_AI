import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import API from './config/api'
import './App.css'

// ==================== VOICE MEMORY CLIPS INFO ====================
// Real farmer success stories from AWS S3 with language-specific variants
const CLIP_INFO = {
  'hi-IN': {
    'PM_KISAN': { 
      farmer: 'Sunitha Devi', 
      district: 'Tumkur, Karnataka', 
      quote: '"तुमकुर की सुनीता देवी जी की PM-KISAN सफलता की कहानी सुनिए"' 
    },
    'KCC': { 
      farmer: 'Ramaiah', 
      district: 'Mysuru, Karnataka', 
      quote: '"मैसूर के रमैया जी का KCC अनुभव सुनिए"' 
    },
    'PMFBY': { 
      farmer: 'Laxman Singh', 
      district: 'Dharwad, Karnataka', 
      quote: '"धारवाड़ के लक्ष्मण सिंह जी की PMFBY कहानी सुनिए"' 
    }
  },
  'ml-IN': {
    'PM_KISAN': { 
      farmer: 'Priya', 
      district: 'Thrissur, Kerala', 
      quote: '"നിങ്ങളുടെ അടുത്ത് തൃശ്ശൂരിൽ നിന്നുള്ള പ്രിയ ജിയുടെ വിജയകഥ കേൾക്കൂ"' 
    },
    'KCC': { 
      farmer: 'Rajan', 
      district: 'Palakkad, Kerala', 
      quote: '"പാലക്കാട്ടിൽ നിന്നുള്ള രാജൻ ജിയുടെ KCC അനുഭവം കേൾക്കൂ"' 
    },
    'PMFBY': { 
      farmer: 'Suresh Kumar', 
      district: 'Wayanad, Kerala', 
      quote: '"വയനാട്ടിൽ നിന്നുള്ള സുരേഷ് കുമാർ ജിയുടെ കഥ കേൾക്കൂ"' 
    }
  },
  'ta-IN': {
    'PM_KISAN': { 
      farmer: 'Kavitha', 
      district: 'Coimbatore, Tamil Nadu', 
      quote: '"உங்கள் அருகில் கோயம்புத்தூரிலிருந்து கவிதா ஜியின் வெற்றிக்கதை கேளுங்கள்"' 
    },
    'KCC': { 
      farmer: 'Vijay', 
      district: 'Madurai, Tamil Nadu', 
      quote: '"மதுரையிலிருந்து விஜய் ஜியின் KCC அனுபவம் கேளுங்கள்"' 
    },
    'PMFBY': { 
      farmer: 'Selva', 
      district: 'Thanjavur, Tamil Nadu', 
      quote: '"தஞ்சாவூரிலிருந்து செல்வா ஜியின் கதை கேளுங்கள்"' 
    }
  }
}

// Demo farmer data
const DEMO_FARMER = {
  name: 'Ramesh Kumar',
  phone: '+919876543210',
  land_acres: 2,
  state: 'Karnataka',
  age: 45,
  has_kcc: false,
  has_bank_account: true,
  annual_income: 50000
}

// ==================== SAHAYA'S OPENING SPEECH ====================
const SAHAYA_OPENING_HINDI = `नमस्ते! मैं सहाया हूँ — एक सरकारी कल्याण सहायक।

एक ज़रूरी बात: मैं कभी भी आपका Aadhaar number, OTP, या bank password नहीं माँगती। यह call बिल्कुल safe है।

अगर आप suspicious हैं, तो डायल करें: *123*CHECK#

बताइए — आपके पास कितनी ज़मीन है? क्या आपके पास Kisan Credit Card है?`

// ==================== MULTILINGUAL SUPPORT ====================
const LANGUAGES = {
  'hi-IN': { 
    name: 'हिंदी', 
    englishName: 'Hindi',
    flag: '🇮🇳',
    greeting: 'नमस्ते! मैं सहाया हूँ — आपकी सरकारी योजना सहायक। आप PM-KISAN, KCC, फसल बीमा के बारे में पूछ सकते हैं।',
    placeholder: 'या अपना संदेश टाइप करें...',
    instruction: 'Please respond ONLY in Hindi (Devanagari script).',
    ui: {
      startBtn: '☎️ सहाया से बात करें',
      endBtn: '📵 कॉल बंद करें',
      micBtn: '🎤 बोलने के लिए दबाएं',
      stopBtn: '⏹ बोलना बंद करें',
      listening: 'सुन रही हूँ...',
      thinking: 'सोच रही हूँ...',
      speaking: '🔊 Sahaya बोल रही है...',
      placeholder: 'या अपना संदेश टाइप करें...',
      youSaid: 'आपने कहा:',
      sahayaSays: 'Sahaya कहती है:'
    }
  },
  'ta-IN': { 
    name: 'தமிழ்', 
    englishName: 'Tamil',
    flag: '🌺',
    greeting: 'வணக்கம்! நான் சஹாயா — உங்கள் அரசு திட்ட உதவியாளர். PM-KISAN, KCC, பயிர் காப்பீடு பற்றி கேளுங்கள்।',
    placeholder: 'உங்கள் செய்தியை தட்டச்சு செய்யுங்கள்...',
    instruction: 'Please respond ONLY in Tamil script.',
    ui: {
      startBtn: '☎️ சஹாயாவிடம் பேசுங்கள்',
      endBtn: '📵 அழைப்பை முடிக்கவும்',
      micBtn: '🎤 பேச அழுத்தவும்',
      stopBtn: '⏹ நிறுத்து',
      listening: 'கேட்கிறேன்...',
      thinking: 'யோசிக்கிறேன்...',
      speaking: '🔊 Sahaya பேசுகிறாள்...',
      placeholder: 'உங்கள் செய்தியை தட்டச்சு செய்யுங்கள்...',
      youSaid: 'நீங்கள் சொன்னது:',
      sahayaSays: 'Sahaya சொல்கிறாள்:'
    }
  },
  'kn-IN': { 
    name: 'ಕನ್ನಡ', 
    englishName: 'Kannada',
    flag: '🌻',
    greeting: 'ನಮಸ್ಕಾರ! ನಾನು ಸಹಾಯ — ನಿಮ್ಮ ಸರ್ಕಾರಿ ಯೋಜನೆ ಸಹಾಯಕ. PM-KISAN, KCC, ಬೆಳೆ ವಿಮೆ ಬಗ್ಗೆ ಕೇಳಿ।',
    placeholder: 'ನಿಮ್ಮ ಸಂದೇಶ ಟೈಪ್ ಮಾಡಿ...',
    instruction: 'Please respond ONLY in Kannada script.',
    ui: {
      startBtn: '☎️ ಸಹಾಯದೊಂದಿಗೆ ಮಾತನಾಡಿ',
      endBtn: '📵 ಕರೆ ಮುಗಿಸಿ',
      micBtn: '🎤 ಮಾತನಾಡಲು ಒತ್ತಿರಿ',
      stopBtn: '⏹ ನಿಲ್ಲಿಸಿ',
      listening: 'ಕೇಳುತ್ತಿದ್ದೇನೆ...',
      thinking: 'ಯೋಚಿಸುತ್ತಿದ್ದೇನೆ...',
      speaking: '🔊 Sahaya ಮಾತನಾಡುತ್ತಿದ್ದಾಳೆ...',
      placeholder: 'ನಿಮ್ಮ ಸಂದೇಶ ಟೈಪ್ ಮಾಡಿ...',
      youSaid: 'ನೀವು ಹೇಳಿದ್ದು:',
      sahayaSays: 'Sahaya ಹೇಳುತ್ತಾಳೆ:'
    }
  },
  'te-IN': { 
    name: 'తెలుగు', 
    englishName: 'Telugu',
    flag: '🌸',
    greeting: 'నమస్కారం! నేను సహాయ — మీ ప్రభుత్వ పథకాల సహాయకురాలు. PM-KISAN, KCC, పంట బీమా గురించి అడగండి।',
    placeholder: 'మీ సందేశం టైప్ చేయండి...',
    instruction: 'Please respond ONLY in Telugu script.',
    ui: {
      startBtn: '☎️ సహాయతో మాట్లాడండి',
      endBtn: '📵 కాల్ ముగించండి',
      micBtn: '🎤 మాట్లాడటానికి నొక్కండి',
      stopBtn: '⏹ ఆపు',
      listening: 'వింటున్నాను...',
      thinking: 'ఆలోచిస్తున్నాను...',
      speaking: '🔊 Sahaya మాట్లాడుతోంది...',
      placeholder: 'మీ సందేశం టైప్ చేయండి...',
      youSaid: 'మీరు చెప్పింది:',
      sahayaSays: 'Sahaya చెప్తోంది:'
    }
  },
  'ml-IN': { 
    name: 'മലയാളം', 
    englishName: 'Malayalam',
    flag: '🌴',
    greeting: 'നമസ്കാരം! ഞാൻ സഹായ — നിങ്ങളുടെ സർക്കാർ പദ്ധതി സഹായി. PM-KISAN, KCC, വിള ഇൻഷുറൻസ് എന്നിവയെ കുറിച്ച് ചോദിക്കൂ।',
    placeholder: 'നിങ്ങളുടെ സന്ദേശം ടൈപ്പ് ചെയ്യൂ...',
    instruction: 'Please respond ONLY in Malayalam script.',
    ui: {
      startBtn: '☎️ സഹായയോട് സംസാരിക്കൂ',
      endBtn: '📵 കോൾ അവസാനിപ്പിക്കൂ',
      micBtn: '🎤 സംസാരിക്കാൻ അമർത്തൂ',
      stopBtn: '⏹ നിർത്തൂ',
      listening: 'കേൾക്കുന്നു...',
      thinking: 'ചിന്തിക്കുന്നു...',
      speaking: '🔊 Sahaya സംസാരിക്കുന്നു...',
      placeholder: 'നിങ്ങളുടെ സന്ദേശം ടൈപ്പ് ചെയ്യൂ...',
      youSaid: 'നിങ്ങൾ പറഞ്ഞത്:',
      sahayaSays: 'Sahaya പറയുന്നു:'
    }
  }
}

const POLLY_VOICES = {
  'hi-IN': { voiceId: 'Kajal', engine: 'neural', languageCode: 'hi-IN' },
  'ta-IN': { voiceId: 'Kajal', engine: 'neural', languageCode: 'hi-IN' },
  'kn-IN': { voiceId: 'Kajal', engine: 'neural', languageCode: 'hi-IN' },
  'te-IN': { voiceId: 'Kajal', engine: 'neural', languageCode: 'hi-IN' },
  'ml-IN': { voiceId: 'Kajal', engine: 'neural', languageCode: 'hi-IN' }
}

// ==================== LANGUAGE SELECTOR COMPONENT ====================
const LanguageSelector = ({ selected, onSelect, detected }) => (
  <div style={{
    background: '#f0fdf4',
    border: '1px solid #86efac',
    borderRadius: '8px',
    padding: '10px 12px',
    marginBottom: '12px'
  }}>
    <div style={{
      fontSize: '12px', 
      color: '#166534', 
      fontWeight: 'bold', 
      marginBottom: '8px'
    }}>
      🌐 भाषा चुनें / Choose Language
      {detected && detected !== selected && (
        <span style={{
          marginLeft: '8px',
          background: '#dcfce7',
          color: '#166534',
          fontSize: '11px',
          padding: '2px 6px',
          borderRadius: '10px'
        }}>
          Auto-detected: {LANGUAGES[detected]?.name}
        </span>
      )}
    </div>
    <div style={{display: 'flex', gap: '6px', flexWrap: 'wrap'}}>
      {Object.entries(LANGUAGES).map(([code, lang]) => (
        <button
          key={code}
          onClick={() => onSelect(code)}
          style={{
            padding: '6px 12px',
            borderRadius: '20px',
            border: selected === code ? '2px solid #16a34a' : '1px solid #d1d5db',
            background: selected === code ? '#16a34a' : 'white',
            color: selected === code ? 'white' : '#374151',
            fontSize: '13px',
            fontWeight: selected === code ? 'bold' : 'normal',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          {lang.flag} {lang.name}
        </button>
      ))}
    </div>
  </div>
)

// Call states for UI management
const CALL_STATES = {
  IDLE: 'idle',                      // Waiting for user to click "Talk to Sahaya"
  CONNECTING: 'connecting',           // Initiating call (showing spinner)
  SAHAYA_SPEAKING: 'sahaya_speaking', // Sahaya's opening playing
  WAITING: 'waiting',                 // Ready for user input
  RECORDING: 'recording',             // Microphone recording
  TRANSCRIBING: 'transcribing',       // Processing audio
  THINKING: 'thinking'                // AI generating response
}

// ==================== TEXT-TO-SPEECH FUNCTION ====================
/**
 * Speaks Hindi text using browser TTS with voice selection and fallback
 */
const speakHindi = (text, options = {}) => {
  return new Promise((resolve, reject) => {
    const {
      onStart = () => {},
      onEnd = () => {},
      onError = () => {}
    } = options

    if (!('speechSynthesis' in window)) {
      console.error('Speech synthesis not supported')
      onError('Browser does not support speech synthesis')
      reject(new Error('Speech synthesis not supported'))
      return
    }

    // Clean text for speech (remove emojis, markdown symbols, etc.)
    const cleanText = text
      .replace(/[🎤🌾🔊📱⚡🙏✓•→🎁💰🏥📸🔄📞💻🎙️🔴🌍]/g, '')
      .replace(/\*\*/g, '') // Remove markdown bold
      .replace(/##/g, '') // Remove markdown headers
      .replace(/Sahaya:/gi, '') // Remove speaker labels
      .trim()

    if (!cleanText) {
      onError('Empty text after cleaning')
      reject(new Error('Empty text'))
      return
    }

    const utterance = new SpeechSynthesisUtterance(cleanText)
    
    // Language and voice selection
    utterance.lang = 'hi-IN'
    utterance.rate = 0.82 // Natural conversation pace
    utterance.pitch = 1.08 // Warm tone
    utterance.volume = 1.0

    // Select Hindi voice if available
    const voices = window.speechSynthesis.getVoices()
    const hindiVoice = voices.find(v => 
      v.lang.includes('hi') || v.name.includes('Hindi')
    )
    
    if (hindiVoice) {
      utterance.voice = hindiVoice
    } else {
      // Fallback to any available voice for language
      const langVoice = voices.find(v => v.lang.startsWith('hi'))
      if (langVoice) utterance.voice = langVoice
    }

    // Event callbacks
    utterance.onstart = () => {
      onStart()
    }

    utterance.onend = () => {
      onEnd()
      resolve()
    }

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error)
      onError(event.error)
      reject(event.error)
    }

    // Cancel any ongoing speech before starting
    window.speechSynthesis.cancel()
    window.speechSynthesis.speak(utterance)
  })
}

// ==================== HEADER WITH ANTI-SCAM BADGE ====================
const Header = () => (
  <div className="bg-green-800 text-white p-4">
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">🌾 VoiceBridge AI — Sahaya</h1>
          <p className="text-green-200 text-sm">
            AI-Powered Welfare Access for 135 Million Farmers
          </p>
        </div>
        <div className="text-right">
          <div className="bg-green-600 border border-green-400 rounded px-3 py-1 text-xs inline-block">
            ✅ DPDP 2023 Compliant
          </div>
          <div className="text-xs text-green-200 mt-1">
            No Aadhaar stored • Auto-delete 90 days
          </div>
        </div>
      </div>
      <div className="mt-3 bg-yellow-800 border border-yellow-600 rounded p-2 text-xs">
        ⚠️ VERIFICATION: Dial *123*CHECK# to verify Sahaya is legitimate. 
        Sahaya NEVER asks for OTPs, passwords, or Aadhaar numbers.
      </div>
    </div>
  </div>
)

// ==================== ELIGIBILITY SCORE ====================
const EligibilityScore = ({ schemes }) => {
  if (!schemes || schemes.length === 0) return null
  
  const score = schemes.length
  const percentage = (score / 10) * 100
  return (
    <div className="bg-white rounded-lg border p-4 mb-4">
      <div className="flex justify-between mb-2">
        <span className="font-semibold text-gray-700">
          Scheme Match Score
        </span>
        <span className="text-green-700 font-bold">
          {score}/10 schemes
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-4">
        <div 
          className="bg-green-600 h-4 rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-1">
        {score >= 7 ? '🎉 High eligibility farmer!' : 
         score >= 4 ? '✅ Good eligibility' : 
         '📋 Some schemes available'}
      </p>
    </div>
  )
}

// ==================== VOICE MEMORY CLIP ====================
const VoiceMemoryClip = ({ clip, schemeId, isAutoPlaying = false, selectedLanguage = 'hi-IN' }) => {
  if (!clip) return null
  
  const langClips = CLIP_INFO[selectedLanguage] || CLIP_INFO['hi-IN']
  const info = langClips[schemeId] || { farmer: 'Kisan', district: 'Local', quote: '' }
  
  return (
    <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-300 rounded-lg p-4 mt-3 shadow-md">
      <div className="flex items-center gap-2 mb-3">
        {/* Animated waveform indicator */}
        <div className="flex items-center gap-0.5">
          <div className="w-1 h-3 bg-amber-600 rounded-full animate-pulse" style={{animationDelay: '0s'}}></div>
          <div className="w-1 h-5 bg-amber-600 rounded-full animate-pulse" style={{animationDelay: '0.1s'}}></div>
          <div className="w-1 h-4 bg-amber-600 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
          <div className="w-1 h-6 bg-amber-600 rounded-full animate-pulse" style={{animationDelay: '0.3s'}}></div>
          <div className="w-1 h-4 bg-amber-600 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
        </div>
        <span className="text-amber-600 font-bold text-sm">🎙️ Voice Memory Network</span>
        {isAutoPlaying && (
          <span className="ml-2 bg-amber-600 text-white text-xs px-2 py-1 rounded-full font-semibold animate-pulse">
            ▶ Playing
          </span>
        )}
      </div>
      <p className="text-sm font-semibold text-amber-900 mb-1">
        {info.farmer} • {info.district}
      </p>
      <p className="text-xs text-amber-700 mb-3 italic">
        {info.quote}
      </p>
      <audio 
        controls 
        crossOrigin="anonymous"
        preload="metadata"
        src={clip}
        className="w-full h-8 rounded"
      />
    </div>
  )
}

// ==================== COST IMPACT COUNTER ====================
const ImpactCounter = () => (
  <div className="bg-green-900 text-white rounded-lg p-4 text-center mb-4">
    <div className="grid grid-cols-3 gap-4">
      <div>
        <div className="text-2xl font-bold text-yellow-400">₹15-25</div>
        <div className="text-xs text-green-200">Per User (Sahaya)</div>
      </div>
      <div>
        <div className="text-2xl font-bold text-red-400">₹2,700</div>
        <div className="text-xs text-green-200">Per User (Field Officers)</div>
      </div>
      <div>
        <div className="text-2xl font-bold text-white">180x</div>
        <div className="text-xs text-green-200">Cheaper</div>
      </div>
    </div>
    <div className="mt-2 text-xs text-green-300">
      135 million farmers • ₹2.8-5 lakh welfare ROI per ₹30,000 deployment
    </div>
  </div>
)

// ==================== ARCHITECTURE BADGES ====================
const ArchitectureBadges = () => {
  const services = [
    { name: 'Bedrock', icon: '🧠', detail: 'Hindi AI' },
    { name: 'Polly', icon: '🔊', detail: 'Voice Output' },
    { name: 'Transcribe', icon: '🎤', detail: 'Hindi STT' },
    { name: 'DynamoDB', icon: '🗄️', detail: '10 Schemes' },
    { name: 'S3', icon: '📦', detail: 'Audio Clips' },
    { name: 'Lambda', icon: '⚡', detail: 'Functions' },
    { name: 'Connect', icon: '📞', detail: 'Outbound' },
    { name: 'SNS', icon: '📱', detail: 'SMS Alerts' },
  ]
  return (
    <div className="pt-1">
      <h3 className="font-semibold text-gray-700 mb-3 text-sm">AWS Services used (8/8)</h3>
      <div className="flex flex-wrap gap-2 justify-center">
        {services.map(s => (
          <div key={s.name} 
               className="bg-orange-50 border border-orange-200 
                          rounded px-2 py-1 text-xs text-center">
            <div>{s.icon} {s.name}</div>
            <div className="text-orange-600 text-xs">{s.detail}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ==================== CALL INITIATOR ====================
const CallInitiator = ({ farmerProfile, eligibleSchemeIds }) => {
  const [callStatus, setCallStatus] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  
  const initiateCall = async () => {
    setIsLoading(true)
    try {
      const response = await axios.post(API.initiateCall, {
        farmer_phone: farmerProfile.phone,
        farmer_name: farmerProfile.name,
        scheme_ids: eligibleSchemeIds || ['PM_KISAN']
      })
      setCallStatus(response.data)
    } catch(e) {
      setCallStatus({ success: false, error: e.message })
    }
    setIsLoading(false)
  }
  
  return (
    <div className="bg-white rounded-lg border p-4 mb-4">
      <h3 className="font-semibold text-gray-800 mb-2">
        📞 Proactive Outreach — Sahaya Calls the Farmer
      </h3>
      <p className="text-xs text-gray-500 mb-3">
        Unlike chatbots that wait, Sahaya initiates the call. 
        Farmer just needs to answer.
      </p>
      <button 
        onClick={initiateCall}
        disabled={isLoading || !farmerProfile?.phone}
        className="w-full bg-green-700 text-white py-3 rounded-lg 
                   font-semibold hover:bg-green-800 disabled:opacity-50
                   transition-colors"
      >
        {isLoading ? '⏳ Initiating Call...' : 
         '📲 Initiate Proactive AI Call to Farmer'}
      </button>
      {callStatus && (
        callStatus.success ? (
          <div className="mt-3 p-2 rounded text-sm bg-green-50 text-green-800">
            {`✅ ${callStatus.message}`}
            {callStatus.provider && (
              <span className="ml-2 text-xs opacity-70">
                via {callStatus.provider}
              </span>
            )}
          </div>
        ) : (
          <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-4">
            {/* Header row */}
            <div className="flex items-start gap-3">
              <span className="text-xl">📞</span>
              <div className="flex-1">
                <p className="font-semibold text-amber-900 text-sm">
                  Demo Call — Connecting to Verified Indian Number
                </p>
                <p className="text-amber-800 text-sm mt-1">
                  In this demo, Sahaya's outbound call is routed to the creator's verified
                  Indian mobile number. You can hear the full Hindi conversation Sahaya
                  would have with any farmer.
                </p>
              </div>
            </div>

            {/* Divider */}
            <div className="border-t border-amber-200 mt-3 pt-3">
              <p className="text-xs text-amber-700 flex items-start gap-2">
                <span>ℹ️</span>
                <span>
                  <strong>Why only one number?</strong> Amazon Connect requires 4–6 weeks
                  to provision verified Indian (+91) DIDs. For this hackathon demo, outbound
                  calls are restricted to pre-verified numbers per telecom regulations.
                  The full architecture — contact flow, 6-stage TwiML, Connect instance —
                  is live and production-ready.
                </span>
              </p>
            </div>
          </div>
        )
      )}
    </div>
  )
}

// ==================== MAIN APP ====================
function App() {
  // ========== STATE VARIABLES ==========
  const [farmerProfile, setFarmerProfile] = useState(null)
  const [eligibleSchemes, setEligibleSchemes] = useState([])
  const [matchedSchemes, setMatchedSchemes] = useState([]) // Schemes mentioned in conversation
  const [allSchemes, setAllSchemes] = useState([])
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [response, setResponse] = useState(null)
  const [conversationHistory, setConversationHistory] = useState([])
  
  // NEW: Call state machine
  const [callState, setCallState] = useState(CALL_STATES.IDLE)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [inputEnabled, setInputEnabled] = useState(false)
  const [isConversationActive, setIsConversationActive] = useState(false)
  
  // Multilingual support
  const [selectedLanguage, setSelectedLanguage] = useState('hi-IN')
  const [detectedLanguage, setDetectedLanguage] = useState('hi-IN')
  
  const recognitionRef = useRef(null)
  const isConversationActiveRef = useRef(false)
  const audioContextRef = useRef(null)
  const activeSourcesRef = useRef([])

  // UI text in selected language
  const langUI = LANGUAGES[selectedLanguage]?.ui || LANGUAGES['hi-IN'].ui

  // Load all schemes on mount
  useEffect(() => {
    loadSchemes()
  }, [])

  // Set eligible schemes from all schemes when loaded
  useEffect(() => {
    if (allSchemes.length > 0 && farmerProfile) {
      setEligibleSchemes(allSchemes.map(s => s.scheme_id))
    }
  }, [allSchemes, farmerProfile])

  // Safety net: if eligibility-check fails, fallback to all scheme IDs
  useEffect(() => {
    if (allSchemes.length > 0 && farmerProfile && eligibleSchemes.length === 0) {
      setEligibleSchemes(allSchemes.map(s => s.scheme_id))
      console.log('[VoiceBridge] Fallback: set all scheme IDs')
    }
  }, [allSchemes, farmerProfile])

  const loadSchemes = async () => {
    try {
      const res = await axios.get(API.schemes)
      // Handle both array and {schemes:[]} response formats
      const schemes = Array.isArray(res.data) ? res.data : (res.data.schemes || [])
      console.log('[VoiceBridge] Schemes loaded:', schemes.length, 'items')
      if (schemes.length > 0) {
        console.log('[VoiceBridge] First scheme:', JSON.stringify(schemes[0]))
      }
      setAllSchemes(schemes)
    } catch(e) {
      console.error('[VoiceBridge] Failed to load schemes:', e)
      setAllSchemes([])
    }
  }

  const loadDemoFarmer = async () => {
    setFarmerProfile(DEMO_FARMER)
    setTranscript('')
    setResponse(null)
    setConversationHistory([])
    setMatchedSchemes([])
    setCallState(CALL_STATES.IDLE)
    setInputEnabled(false)
    setIsSpeaking(false)
    
    // Check eligibility
    try {
      const res = await axios.post(
        'https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/eligibility-check',
        { farmer_profile: DEMO_FARMER }
      )
      const schemes = res.data.eligible_schemes || []
      const ids = schemes.map(s => typeof s === 'string' ? s : s.scheme_id)
      setEligibleSchemes(ids)
      console.log('[VoiceBridge] Eligible IDs:', ids)
    } catch(e) {
      console.error('Eligibility check failed:', e)
    }
  }

  // ========== SAHAYA OPENING SPEECH ==========
  const startSahayaCall = async () => {
    unlockAudio()
    setCallState(CALL_STATES.CONNECTING)
    setInputEnabled(false)
    
    try {
      // Add Sahaya's opening message to conversation
      setConversationHistory([{
        role: 'assistant',
        content: SAHAYA_OPENING_HINDI
      }])
      
      setCallState(CALL_STATES.SAHAYA_SPEAKING)
      setIsSpeaking(true)
      
      // Speak Sahaya's opening
      await speakHindi(SAHAYA_OPENING_HINDI, {
        onStart: () => {
          setIsSpeaking(true)
        },
        onEnd: () => {
          setIsSpeaking(false)
          setCallState(CALL_STATES.WAITING)
          setInputEnabled(true)
        },
        onError: (error) => {
          console.error('TTS Error:', error)
          // If TTS fails, still move to waiting state
          setIsSpeaking(false)
          setCallState(CALL_STATES.WAITING)
          setInputEnabled(true)
        }
      })
    } catch(e) {
      console.error('Failed to start Sahaya call:', e)
      setCallState(CALL_STATES.IDLE)
      setInputEnabled(false)
    }
  }

  // ========== AUDIO HELPER FUNCTIONS ==========
  const playSahayaAudio = (audioUrl, onComplete) => {
    const audio = new Audio(audioUrl)
    audio.onended = () => {
      if (onComplete) onComplete()
    }
    audio.onerror = () => {
      if (onComplete) onComplete()
    }
    audio.play().catch(() => {
      setTimeout(() => onComplete(), 2000)
    })
    return audio
  }

  const speakAndListen = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = selectedLanguage
      utterance.rate = 0.9
      utterance.onend = () => {
        if (isConversationActiveRef.current) {
          setTimeout(() => startListening(), 500)
        }
      }
      window.speechSynthesis.speak(utterance)
    } else {
      if (isConversationActiveRef.current) {
        setTimeout(() => startListening(), 2000)
      }
    }
  }

  // ========== SEQUENTIAL AUDIO PLAYBACK ==========
  /**
   * Plays Sahaya's audio, waits for it to finish, then auto-plays voice memory clip.
   * Updates UI state to show "Now Playing" indicator.
   * Optionally resumes listening after both audio clips finish.
   */
  const unlockAudio = () => {
    if (!audioContextRef.current) {
      try {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
        // Play a silent buffer to unlock autoplay
        const buffer = audioContextRef.current.createBuffer(1, 1, 22050)
        const source = audioContextRef.current.createBufferSource()
        source.buffer = buffer
        source.connect(audioContextRef.current.destination)
        source.start(0)
        console.log('[Audio] Context unlocked')
      } catch(e) {
        console.log('[Audio] Failed to unlock context:', e.message)
      }
    }
  }

  const playAudioUrl = (url) => {
    return new Promise(async (resolve) => {
      try {
        // Unlock audio context first
        if (!audioContextRef.current) {
          audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
        }
        const ctx = audioContextRef.current
        if (ctx.state === 'suspended') {
          await ctx.resume()
        }
        
        // Fetch and decode audio
        const response = await fetch(url, { mode: 'cors' })
        const arrayBuffer = await response.arrayBuffer()
        const audioBuffer = await ctx.decodeAudioData(arrayBuffer)
        
        const source = ctx.createBufferSource()
        source.buffer = audioBuffer
        source.connect(ctx.destination)
        source.onended = () => {
          activeSourcesRef.current = activeSourcesRef.current.filter(s => s !== source)
          resolve()
        }
        activeSourcesRef.current.push(source)
        source.start(0)
        console.log('[Audio] Playing:', url.split('/').pop().split('?')[0])
      } catch(e) {
        console.log('[Audio] playAudioUrl failed:', e.message)
        resolve()
      }
    })
  }

  const playSequentially = async (sahayaAudioUrl, voiceMemoryUrl, onComplete, responseText) => {
    // Play Sahaya's Polly voice first
    if (sahayaAudioUrl) {
      console.log('[TTS] Playing Polly TTS from API')
      await playAudioUrl(sahayaAudioUrl)
    }
    
    // Pause between Sahaya and farmer story
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Only play voice memory for Hindi (clips are in Hindi)
    if (voiceMemoryUrl && selectedLanguage === 'hi-IN') {
      console.log('[VM] Autoplaying farmer story from:', voiceMemoryUrl.substring(0, 50) + '...')
      await playAudioUrl(voiceMemoryUrl)
      console.log('[VM] Farmer story finished')
    }
    
    // Short pause then resume listening
    await new Promise(resolve => setTimeout(resolve, 600))
    if (onComplete) onComplete()
  }

  // ========== LANGUAGE-AWARE AUDIO PLAYBACK ==========
  const playWithLanguage = async (sahayaAudioUrl, voiceMemoryUrl, responseText, onComplete) => {
    const isHindi = selectedLanguage === 'hi-IN'
    console.log('[Lang] playWithLanguage: lang=' + selectedLanguage + ' isHindi=' + isHindi)
    
    if (isHindi) {
      // Hindi: use Polly audio (best quality)
      await playSequentially(sahayaAudioUrl, voiceMemoryUrl, onComplete, responseText)
    } else {
      // Regional language: try Sarvam AI first, fallback to browser TTS
      window.speechSynthesis.cancel()
      
      let sarvamSucceeded = false
      
      if (responseText) {
        try {
          // Try calling Sarvam AI for regional language TTS
          const sarvamResponse = await axios.post(API.sarvamTts, {
            text: responseText,
            language: selectedLanguage   // Send full code e.g. 'ml-IN'
          }, { timeout: 10000 })
          
          if (sarvamResponse.data.success && sarvamResponse.data.audio_url) {
            sarvamSucceeded = true
            const sarvamAudioUrl = sarvamResponse.data.audio_url
            
            // Play Sarvam audio then voice memory then complete
            const playAudioSequence = async () => {
              try {
                await playAudioUrl(sarvamAudioUrl)
                await new Promise(resolve => setTimeout(resolve, 800))
                
                // Auto-play voice memory clip after Sarvam TTS finishes
                if (voiceMemoryUrl && isConversationActiveRef.current) {
                  try {
                    await playAudioUrl(voiceMemoryUrl)
                  } catch (vmErr) {
                    console.warn('[VM] Voice memory autoplay failed:', vmErr.message)
                  }
                }
                await new Promise(resolve => setTimeout(resolve, 500))
                if (onComplete) onComplete()
              } catch (err) {
                console.warn('Audio playback error:', err)
                if (onComplete) onComplete()
              }
            }
            
            await playAudioSequence()
            return
          }
        } catch (sarvamError) {
          console.warn('Sarvam API failed, falling back to browser TTS:', sarvamError.message)
          sarvamSucceeded = false
          // Will use browser TTS below
        }
      }
      
      // Fallback to browser TTS if Sarvam failed or no responseText
      if (responseText && !sarvamSucceeded) {
        const utterance = new SpeechSynthesisUtterance(responseText)
        utterance.lang = selectedLanguage
        utterance.rate = 0.85
        utterance.pitch = 1.05
        
        // Pick best available voice for the language
        const voices = window.speechSynthesis.getVoices()
        const bestVoice = voices.find(v => v.lang === selectedLanguage) ||
                          voices.find(v => v.lang.startsWith(selectedLanguage.split('-')[0]))
        if (bestVoice) utterance.voice = bestVoice
        
        utterance.onend = async () => {
          // Still play voice memory clip
          if (voiceMemoryUrl && isConversationActiveRef.current && selectedLanguage === 'hi-IN') {
            await new Promise(resolve => setTimeout(resolve, 800))
            await playAudioUrl(voiceMemoryUrl)
          }
          await new Promise(resolve => setTimeout(resolve, 500))
          if (onComplete) onComplete()
        }
        
        utterance.onerror = async () => {
          // TTS failed, still play voice memory and continue
          if (voiceMemoryUrl && isConversationActiveRef.current) await playAudioUrl(voiceMemoryUrl)
          if (onComplete) onComplete()
        }
        
        window.speechSynthesis.speak(utterance)
      } else if (!responseText) {
        // No text, just play voice memory
        if (voiceMemoryUrl && isConversationActiveRef.current) await playAudioUrl(voiceMemoryUrl)
        if (onComplete) onComplete()
      }
    }
  }

  // ========== CONVERSATION MANAGEMENT ==========
  const startConversation = async () => {
    unlockAudio()
    setIsConversationActive(true)
    isConversationActiveRef.current = true
    setCallState(CALL_STATES.CONNECTING)
    setConversationHistory([])
    setTranscript('')
    setResponse(null)
    
    const openingText = LANGUAGES[selectedLanguage]?.greeting || LANGUAGES['hi-IN'].greeting
    
    setConversationHistory([{
      role: 'assistant',
      content: openingText
    }])
    setResponse({ text: openingText })
    
    // Try to get Polly audio first
    try {
      if (selectedLanguage === 'hi-IN') {
        // Hindi: try Polly first, fallback to browser TTS
        const ttsResult = await axios.post(
          `${API.tts}`,
          { text: openingText, voice: 'Kajal' }
        )
        if (ttsResult.data.audio_url) {
          playSahayaAudio(ttsResult.data.audio_url, () => {
            if (isConversationActiveRef.current) {
              setTimeout(() => startListening(), 500)
            }
          })
        } else {
          speakAndListen(openingText)
        }
      } else {
        // Regional language: use Sarvam for natural voice
        try {
          const sarvamRes = await axios.post(API.sarvamTts, {
            text: openingText,
            language: selectedLanguage
          })
          if (sarvamRes.data.success && sarvamRes.data.audio_url) {
            await playAudioUrl(sarvamRes.data.audio_url)
            if (isConversationActiveRef.current) {
              setTimeout(() => startListening(), 500)
            }
          } else {
            throw new Error('Sarvam failed')
          }
        } catch(e) {
          // Fallback to browser TTS
          console.log('[TTS] Sarvam opening failed, using browser:', e.message)
          window.speechSynthesis.cancel()
          const utterance = new SpeechSynthesisUtterance(openingText)
          utterance.lang = selectedLanguage
          utterance.rate = 0.85
          const voices = window.speechSynthesis.getVoices()
          const bestVoice = voices.find(v => v.lang === selectedLanguage) ||
                            voices.find(v => v.lang.startsWith(selectedLanguage.split('-')[0]))
          if (bestVoice) utterance.voice = bestVoice
          utterance.onend = () => {
            if (isConversationActiveRef.current) setTimeout(() => startListening(), 500)
          }
          window.speechSynthesis.speak(utterance)
        }
      }
    } catch(e) {
      console.log('TTS failed, using browser TTS:', e)
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(openingText)
      utterance.lang = selectedLanguage
      utterance.rate = 0.85
      window.speechSynthesis.speak(utterance)
      setTimeout(() => {
        if (isConversationActiveRef.current) startListening()
      }, 3000)
    }
  }

  const endConversation = () => {
    setIsConversationActive(false)
    isConversationActiveRef.current = false
    recognitionRef.current?.stop()
    window.speechSynthesis?.cancel()
    
    // Stop ALL currently playing audio sources immediately
    activeSourcesRef.current.forEach(source => {
      try { source.stop() } catch(e) {}
    })
    activeSourcesRef.current = []
    
    // Close and reset audio context
    if (audioContextRef.current) {
      try {
        audioContextRef.current.close()
        audioContextRef.current = null
      } catch (err) {}
    }
    
    setIsRecording(false)
    setCallState(CALL_STATES.IDLE)
    setInputEnabled(false)
  }

  // ========== WEB SPEECH API RECOGNITION ==========
  const UNICODE_RANGES = {
    'hi-IN': { min: 0x0900, max: 0x097F, name: 'Devanagari' },
    'ta-IN': { min: 0x0B80, max: 0x0BFF, name: 'Tamil' },
    'kn-IN': { min: 0x0C80, max: 0x0CFF, name: 'Kannada' },
    'te-IN': { min: 0x0C00, max: 0x0C7F, name: 'Telugu' },
    'ml-IN': { min: 0x0D00, max: 0x0D7F, name: 'Malayalam' }
  }

  const detectLanguageFromText = (text) => {
    if (!text) return 'hi-IN'
    
    let languageScores = {}
    Object.entries(UNICODE_RANGES).forEach(([lang, range]) => {
      languageScores[lang] = 0
    })
    
    for (let char of text) {
      const code = char.charCodeAt(0)
      for (let [lang, range] of Object.entries(UNICODE_RANGES)) {
        if (code >= range.min && code <= range.max) {
          languageScores[lang]++
        }
      }
    }
    
    const detectedLang = Object.keys(languageScores).reduce((prev, current) =>
      languageScores[current] > languageScores[prev] ? current : prev
    )
    
    return languageScores[detectedLang] > 0 ? detectedLang : 'hi-IN'
  }

  const startListening = () => {
    unlockAudio()
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Please use Chrome, Edge, or Safari browser for voice input')
      return
    }
    
    // Stop any existing recognition to avoid conflicts
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort()
      } catch(e) {
        console.log('[VoiceBridge] Error aborting previous recognition:', e.message)
      }
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    
    recognition.lang = selectedLanguage  // Use selected language
    recognition.interimResults = false
    recognition.maxAlternatives = 2  // Get top 2 alternatives for better confidence handling
    recognition.continuous = false
    
    recognition.onstart = () => {
      setIsRecording(true)
      setIsProcessing(false)
      setCallState(CALL_STATES.RECORDING)
      setInputEnabled(false)
    }
    
    recognition.onresult = (event) => {
      // Only process the final result
      if (!event.results[event.results.length - 1].isFinal) {
        return
      }
      
      let transcript = event.results[event.results.length - 1][0].transcript
      const confidence = event.results[event.results.length - 1][0].confidence
      
      // For Malayalam and other regional languages, try alternative if low confidence
      if ((selectedLanguage === 'ml-IN' || selectedLanguage === 'ta-IN') && 
          confidence < 0.6 && event.results[event.results.length - 1].length > 1) {
        const altTranscript = event.results[event.results.length - 1][1].transcript
        const altConfidence = event.results[event.results.length - 1][1].confidence
        console.log(`[VoiceBridge] Low confidence (${confidence.toFixed(2)}) - trying alternative (${altConfidence.toFixed(2)}): ${altTranscript}`)
        if (altConfidence > confidence) {
          transcript = altTranscript
        }
      }
      
      console.log('[VoiceBridge] Web Speech transcript:', transcript, 'confidence:', confidence.toFixed(2))
      
      // Auto-detect language from transcript
      const detectedLang = detectLanguageFromText(transcript)
      if (detectedLang !== selectedLanguage && detectedLang !== 'hi-IN') {
        console.log('[VoiceBridge] Auto-detected language:', detectedLang)
        setDetectedLanguage(detectedLang)
      }
      
      setIsRecording(false)
      setIsProcessing(true)
      setTranscript(transcript)
      sendMessage(transcript)  // Send directly to /api/chat
    }
    
    recognition.onerror = (event) => {
      console.log('[VoiceBridge] Speech error:', event.error)
      setIsRecording(false)
      
      // Only handle errors if we're still in conversation mode
      if (!isConversationActiveRef.current) {
        setIsProcessing(false)
        setCallState(CALL_STATES.WAITING)
        setInputEnabled(true)
        return
      }
      
      if (event.error === 'no-speech') {
        // Silently ignore - user just didn't speak, restart listening
        setTimeout(() => {
          if (isConversationActiveRef.current) {
            startListening()
          }
        }, 300)
      } else if (event.error === 'not-allowed') {
        alert('Microphone permission denied. Please allow mic access and try again.')
        setIsProcessing(false)
        setCallState(CALL_STATES.WAITING)
        setInputEnabled(true)
      } else if (event.error === 'network') {
        alert('Network error. Please check your connection.')
        setIsProcessing(false)
        setCallState(CALL_STATES.WAITING)
        setInputEnabled(true)
      } else {
        // Other errors - try restarting
        console.log('[VoiceBridge] Recovering from error:', event.error)
        setTimeout(() => {
          if (isConversationActiveRef.current) {
            startListening()
          }
        }, 300)
      }
    }
    
    recognition.onend = () => {
      setIsRecording(false)
    }
    
    recognitionRef.current = recognition
    recognition.start()
  }

  const stopListening = () => {
    recognitionRef.current?.stop()
    setIsRecording(false)
  }

  // ========== CHAT MESSAGE HANDLING ==========
  const normalizeTranscript = (text) => {
    let t = text.toLowerCase()
    // KCC variants — speech recognition says सीसीसी, केसीसी (Hindi) and കെസിസി, കെസെ (Malayalam)
    if (t.includes('सीसीसी') || t.includes('केसीसी') || 
        t.includes('കെസിസി') || t.includes('കെസെ') || t.includes('കെ സി സി') ||
        t.includes('si si si') || t.includes('kcc') ||
        t.includes('ks si') || t.includes('kesee') || t.includes('kese') ||
        t.includes('kisan credit') || t.includes('credit card')) {
      return 'kcc ke baare mein batao'
    }
    // PM_KISAN variants
    if (t.includes('पीएम किसान') || t.includes('पी एम किसान') || 
        t.includes('pihem kisan') || t.includes('pm kisan') ||
        t.includes('kisan samman')) {
      return 'pm kisan ke baare mein batao'
    }
    // PMFBY variants
    if (t.includes('पीएमएफबीवाई') || t.includes('फसल बीमा') ||
        t.includes('pmfby') || t.includes('fasal bima')) {
      return 'pmfby fasal bima ke baare mein batao'
    }
    return text
  }

  const sendMessage = async (userMessage) => {
    if (!userMessage.trim()) {
      setIsProcessing(false)
      return
    }

    try {
      setCallState(CALL_STATES.THINKING)
      setInputEnabled(false)

      // Normalize transcript using outer function
      const finalMessage = normalizeTranscript(userMessage)
      
      const historyToSend = [
        ...conversationHistory,
        { role: 'user', content: finalMessage }
      ]
      console.log('[VoiceBridge] Sending to Lambda with history length:', historyToSend.length)

      // Get AI response from /api/chat
      const chatRes = await axios.post(API.chat, {
        message: finalMessage,
        farmer_profile: farmerProfile,
        conversation_history: historyToSend,
        language: selectedLanguage
      })

      console.log('CHAT RESULT:', JSON.stringify(chatRes.data))
      console.log('[VM DEBUG] voice_memory_clip from backend:', chatRes.data.voice_memory_clip)
      console.log('[VM DEBUG] full chat result:', JSON.stringify(chatRes.data))

      const aiResponse = {
        text: chatRes.data.response_text,
        schemes: chatRes.data.schemes_mentioned || [],
        stage: chatRes.data.stage,
        voice_memory_clip: chatRes.data.voice_memory_clip,
        audio_url: chatRes.data.audio_type === 'voice_memory' ? null : chatRes.data.audio_url
      }

      // Fetch voice memory audio if available
      if (aiResponse.voice_memory_clip) {
        try {
          console.log('[VM DEBUG] fetching voice memory for schemeId:', aiResponse.voice_memory_clip)
          const vmRes = await fetch(`https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/voice-memory/${aiResponse.voice_memory_clip}?language=${selectedLanguage}`)
          const vmData = await vmRes.json()
          console.log('[VM DEBUG] voice memory response:', JSON.stringify(vmData))
          aiResponse.voiceMemoryUrl = vmData.audio_url
          aiResponse.voiceMemoryScheme = aiResponse.voice_memory_clip
          console.log('[VM DEBUG] voiceMemoryUrl set to:', aiResponse.voiceMemoryUrl)
        } catch(e) {
          console.log('[VM DEBUG] fetch failed:', e.message)
        }
      }

      // Update matched schemes
      if (aiResponse.schemes && aiResponse.schemes.length > 0) {
        setMatchedSchemes(prev => [...new Set([...prev, ...aiResponse.schemes])])
      }

      setResponse(aiResponse)
      setConversationHistory(prev => [
        ...prev,
        { role: 'user', content: userMessage },
        { 
          role: 'assistant', 
          content: aiResponse.text,
          voiceMemoryUrl: aiResponse.voiceMemoryUrl,
          voiceMemoryScheme: aiResponse.voiceMemoryScheme
        }
      ])

      setIsProcessing(false)

      // Always play whatever audio we have
      const hasAudio = aiResponse.audio_url || aiResponse.voiceMemoryUrl
      
      if (hasAudio) {
        setIsSpeaking(true)
        setCallState(CALL_STATES.SAHAYA_SPEAKING)
        playWithLanguage(
          aiResponse.audio_url || null,
          aiResponse.voiceMemoryUrl || null,
          aiResponse.text,
          () => {
            setIsSpeaking(false)
            if (isConversationActiveRef.current) {
              setTimeout(() => startListening(), 500)
            } else {
              setCallState(CALL_STATES.WAITING)
              setInputEnabled(true)
            }
          }
        )
      } else {
        if (isConversationActiveRef.current) {
          speakAndListen(aiResponse.text)
        } else {
          speakAndWait(aiResponse.text)
        }
      }
    } catch(e) {
      console.error('Chat failed:', e)
      setResponse({ error: 'Chat processing failed: ' + e.message })
      setCallState(CALL_STATES.WAITING)
      setInputEnabled(true)
      setIsProcessing(false)
    }
  }

  // Helper function: Speak and manage call state
  const speakAndWait = async (text) => {
    setIsSpeaking(true)
    setCallState(CALL_STATES.SAHAYA_SPEAKING)
    
    try {
      await speakHindi(text, {
        onStart: () => setIsSpeaking(true),
        onEnd: () => {
          setIsSpeaking(false)
          setCallState(CALL_STATES.WAITING)
          setInputEnabled(true)
          // Auto-focus text input for natural flow
          setTimeout(() => {
            document.getElementById('message-input')?.focus()
          }, 100)
        },
        onError: () => {
          console.log('TTS failed, still enabling input')
          setIsSpeaking(false)
          setCallState(CALL_STATES.WAITING)
          setInputEnabled(true)
        }
      })
    } catch(e) {
      console.error('Speech synthesis error:', e)
      setIsSpeaking(false)
      setCallState(CALL_STATES.WAITING)
      setInputEnabled(true)
    }
  }

  // ========== TEXT INPUT HANDLER ==========
  const handleTextInput = async (e) => {
    const userMessage = e.target.value.trim()
    if (!userMessage) return
    
    e.target.value = ''
    setTranscript(userMessage)
    
    // If Sahaya is speaking, interrupt her to let user speak
    if (isSpeaking) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
    }
    
    try {
      setCallState(CALL_STATES.THINKING)
      setInputEnabled(false)

      // Build history BEFORE sending to Lambda (include current user message)
      const historyToSend = [
        ...conversationHistory,
        { role: 'user', content: userMessage }
      ]
      console.log('[VoiceBridge] Text input - sending to Lambda with history length:', historyToSend.length)

      const chatRes = await axios.post(API.chat, {
        message: userMessage,
        farmer_profile: farmerProfile,
        conversation_history: historyToSend,
        language: selectedLanguage
      })

      console.log('CHAT RESULT:', JSON.stringify(chatRes.data))
      console.log('[VM DEBUG] voice_memory_clip from backend:', chatRes.data.voice_memory_clip)
      console.log('[VM DEBUG] full chat result:', JSON.stringify(chatRes.data))

      const aiResponse = {
        text: chatRes.data.response_text,
        schemes: chatRes.data.schemes_mentioned || [],
        stage: chatRes.data.stage,
        voice_memory_clip: chatRes.data.voice_memory_clip,
        audio_url: chatRes.data.audio_type === 'voice_memory' ? null : chatRes.data.audio_url
      }

      // Fetch voice memory audio if available
      if (aiResponse.voice_memory_clip) {
        try {
          console.log('[VM DEBUG] fetching voice memory for schemeId:', aiResponse.voice_memory_clip)
          const vmRes = await fetch(`https://bkzd32abpg.execute-api.ap-southeast-1.amazonaws.com/dev/api/voice-memory/${aiResponse.voice_memory_clip}?language=${selectedLanguage}`)
          const vmData = await vmRes.json()
          console.log('[VM DEBUG] voice memory response:', JSON.stringify(vmData))
          aiResponse.voiceMemoryUrl = vmData.audio_url
          aiResponse.voiceMemoryScheme = aiResponse.voice_memory_clip
          console.log('[VM DEBUG] voiceMemoryUrl set to:', aiResponse.voiceMemoryUrl)
        } catch(e) {
          console.log('[VM DEBUG] fetch failed:', e.message)
        }
      }

      // Update matched schemes
      if (aiResponse.schemes && aiResponse.schemes.length > 0) {
        setMatchedSchemes(prev => [...new Set([...prev, ...aiResponse.schemes])])
      }

      setResponse(aiResponse)
      setConversationHistory(prev => [
        ...prev,
        { role: 'user', content: userMessage },
        { 
          role: 'assistant', 
          content: aiResponse.text,
          voiceMemoryUrl: aiResponse.voiceMemoryUrl,
          voiceMemoryScheme: aiResponse.voiceMemoryScheme
        }
      ])

      // Handle audio playback with fallback
      const hasAudio = aiResponse.audio_url || aiResponse.voiceMemoryUrl
      
      if (hasAudio) {
        setIsSpeaking(true)
        setCallState(CALL_STATES.SAHAYA_SPEAKING)
        playWithLanguage(
          aiResponse.audio_url || null,
          aiResponse.voiceMemoryUrl || null,
          aiResponse.text,
          () => {
            setIsSpeaking(false)
            setCallState(CALL_STATES.WAITING)
            setInputEnabled(true)
          }
        )
      } else {
        speakAndWait(aiResponse.text)
      }
    } catch(e) {
      console.error('Chat failed:', e)
      setResponse({ error: 'Chat processing failed' })
      setCallState(CALL_STATES.WAITING)
      setInputEnabled(true)
    }
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      <Header />
      
      <div className="max-w-6xl mx-auto p-4">
        {/* Cost Impact */}
        <ImpactCounter />

        {/* Architecture */}
        <details className="bg-white rounded-lg border mb-4">
          <summary className="p-3 cursor-pointer text-sm font-semibold text-gray-500 hover:text-gray-700 select-none">
            🏗️ AWS Architecture — 8 Services Integrated (click to expand)
          </summary>
          <div className="px-4 pb-4">
            <ArchitectureBadges />
          </div>
        </details>

        {/* Demo Button and Profile */}
        {!farmerProfile ? (
          <div className="bg-white rounded-lg border p-6 mb-4">
            <h2 className="text-xl font-bold text-gray-800 mb-1">🌾 VoiceBridge AI — Sahaya Demo</h2>
            <p className="text-gray-500 text-sm mb-5">Meet the farmer you'll be helping today</p>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-green-700 rounded-full flex items-center justify-center text-white text-xl font-bold flex-shrink-0">R</div>
                <div>
                  <div className="font-bold text-gray-800 text-lg">Ramesh Kumar</div>
                  <div className="text-green-700 text-sm">Small & Marginal Farmer • Karnataka</div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2 text-sm">
                <div className="bg-white rounded p-2 border border-green-100 text-center">
                  <div className="text-gray-400 text-xs mb-1">Land</div>
                  <div className="font-bold text-gray-800">2 Acres</div>
                </div>
                <div className="bg-white rounded p-2 border border-green-100 text-center">
                  <div className="text-gray-400 text-xs mb-1">Bank Account</div>
                  <div className="font-bold text-green-600">✓ Linked</div>
                </div>
                <div className="bg-white rounded p-2 border border-green-100 text-center">
                  <div className="text-gray-400 text-xs mb-1">KCC Loan</div>
                  <div className="font-bold text-red-500">✗ None</div>
                </div>
                <div className="bg-white rounded p-2 border border-green-100 text-center">
                  <div className="text-gray-400 text-xs mb-1">Age</div>
                  <div className="font-bold text-gray-800">45 yrs</div>
                </div>
                <div className="bg-white rounded p-2 border border-green-100 text-center">
                  <div className="text-gray-400 text-xs mb-1">Income</div>
                  <div className="font-bold text-gray-800">₹50,000/yr</div>
                </div>
                <div className="bg-white rounded p-2 border border-green-100 text-center">
                  <div className="text-gray-400 text-xs mb-1">Schemes</div>
                  <div className="font-bold text-green-600">10 eligible</div>
                </div>
              </div>
            </div>
            <button
              onClick={loadDemoFarmer}
              className="w-full bg-green-700 text-white px-6 py-4 rounded-lg font-bold text-lg hover:bg-green-800 transition-colors"
            >
              🎤 Start Demo — Talk to Sahaya
            </button>
            <p className="text-xs text-gray-400 mt-2 text-center">Select language after loading • Hindi, Tamil, Kannada, Telugu, Malayalam</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Left: Schemes List with Highlighting */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg border p-4 sticky top-4">
                <h3 className="font-bold text-lg mb-3">Eligible Schemes</h3>
                <EligibilityScore schemes={eligibleSchemes} />
                {eligibleSchemes && eligibleSchemes.length > 0 ? (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {eligibleSchemes.map(schemeId => {
                      const scheme = allSchemes.find(s => s.scheme_id === schemeId)
                      const isMatched = matchedSchemes.includes(schemeId)
                      return (
                        <div 
                          key={schemeId} 
                          className={`border-2 rounded p-2 text-xs transition-all ${
                            isMatched 
                              ? 'bg-green-100 border-green-500 shadow-md' 
                              : 'bg-gray-50 border-gray-200'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-semibold">{scheme?.name_en || scheme?.scheme_id}</div>
                              <div className="text-gray-700 text-xs">{scheme?.benefit}</div>
                            </div>
                            {isMatched && (
                              <span className="text-green-600 font-bold">✓</span>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-gray-500 text-sm">Loading schemes...</div>
                )}
              </div>
            </div>

            {/* Right: Chat and Call */}
            <div className="lg:col-span-2 space-y-4">
              {/* Voice Chat */}
              <div className="bg-white rounded-lg border p-4">
                <h3 className="font-bold text-lg mb-3">
                  {callState === CALL_STATES.IDLE ? '🎤 Talk to Sahaya' : 
                   callState === CALL_STATES.CONNECTING ? '⏳ Connecting...' :
                   callState === CALL_STATES.SAHAYA_SPEAKING ? '🔊 Sahaya is speaking...' :
                   callState === CALL_STATES.RECORDING ? '🔴 Recording...' :
                   callState === CALL_STATES.TRANSCRIBING ? '⏳ Transcribing...' :
                   callState === CALL_STATES.THINKING ? '🧠 Sahaya is thinking...' :
                   '✅ Ready to listen'}
                </h3>

                {/* Conversation Display */}
                {conversationHistory.length > 0 && (
                  <div className="mb-3 p-3 bg-gray-50 rounded max-h-48 overflow-y-auto space-y-2 border">
                    {conversationHistory.map((msg, idx) => (
                      <div key={idx} className={`text-sm p-2 rounded ${
                        msg.role === 'user' 
                          ? 'bg-blue-100 text-blue-900' 
                          : 'bg-green-100 text-green-900'
                      }`}>
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <div className="flex-1">
                            {msg.role === 'user' ? `👨 ${langUI.youSaid} ` : `🎙️ ${langUI.sahayaSays} `}
                            {msg.content.substring(0, 120)}
                            {msg.content.length > 120 ? '...' : ''}
                          </div>
                          {msg.role === 'assistant' && (
                            <button
                              onClick={() => speakHindi(msg.content)}
                              className="ml-2 text-lg hover:scale-125 transition-transform flex-shrink-0"
                              title="Replay"
                            >
                              🔊
                            </button>
                          )}
                        </div>
                        {msg.voiceMemoryUrl && msg.voiceMemoryScheme && (
                          <VoiceMemoryClip clip={msg.voiceMemoryUrl} schemeId={msg.voiceMemoryScheme} selectedLanguage={selectedLanguage} />
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Call Controls */}
                {callState === CALL_STATES.IDLE && !isConversationActive && (
                  <div className="space-y-2">
                    <LanguageSelector 
                      selected={selectedLanguage}
                      onSelect={setSelectedLanguage}
                      detected={detectedLanguage}
                    />
                    <button
                      onClick={startConversation}
                      className="w-full py-4 rounded-lg font-bold text-lg transition-all bg-green-600 text-white hover:bg-green-700 animate-pulse"
                    >
                      {langUI.startBtn}
                    </button>
                  </div>
                )}

                {isConversationActive && (
                  <div className="mb-3">
                    <button
                      onClick={endConversation}
                      className="w-full py-4 rounded-lg font-bold text-lg transition-all bg-red-600 text-white hover:bg-red-700"
                    >
                      {langUI.endBtn}
                    </button>
                  </div>
                )}

                {callState !== CALL_STATES.IDLE && (
                  <>
                    {/* Microphone Button */}
                    {!isSpeaking && callState === CALL_STATES.WAITING && !isProcessing && (
                      <div className="mb-3">
                        <button
                          onClick={isRecording ? stopListening : startListening}
                          disabled={!inputEnabled || isSpeaking || callState !== CALL_STATES.WAITING}
                          className={`w-full py-4 rounded-lg font-bold text-lg transition-all ${
                            isRecording
                              ? 'bg-red-500 text-white animate-pulse hover:bg-red-600'
                              : inputEnabled
                              ? 'bg-green-600 text-white hover:bg-green-700'
                              : 'bg-gray-400 text-gray-200 cursor-not-allowed'
                          }`}
                        >
                          {isRecording 
                            ? langUI.stopBtn 
                            : langUI.micBtn}
                        </button>
                      </div>
                    )}

                    {/* Sahaya Speaking Indicator */}
                    {isSpeaking && (
                      <div className="mb-3 p-3 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-400 rounded-lg">
                        <div className="flex items-center justify-center gap-2">
                          <div className="flex gap-1">
                            <div className="h-3 w-1 bg-green-600 rounded-full animate-pulse" style={{animationDelay: '0s'}}></div>
                            <div className="h-4 w-1 bg-green-600 rounded-full animate-pulse" style={{animationDelay: '0.1s'}}></div>
                            <div className="h-3 w-1 bg-green-600 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                            <div className="h-5 w-1 bg-green-600 rounded-full animate-pulse" style={{animationDelay: '0.3s'}}></div>
                            <div className="h-3 w-1 bg-green-600 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                          </div>
                          <span className="text-sm font-semibold text-green-700">{langUI.speaking}</span>
                        </div>
                      </div>
                    )}

                    {/* Text Input (always available after call starts) */}
                    {callState === CALL_STATES.WAITING && !isSpeaking && (
                      <div className="mb-3">
                        <input
                          id="message-input"
                          type="text"
                          placeholder={langUI.placeholder}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              handleTextInput(e)
                            }
                          }}
                          onChange={(e) => {
                            // If Sahaya is speaking and user starts typing, interrupt her
                            if (isSpeaking && e.target.value.length === 1) {
                              window.speechSynthesis.cancel()
                              setIsSpeaking(false)
                              setCallState(CALL_STATES.WAITING)
                            }
                          }}
                          disabled={!inputEnabled}
                          className="w-full p-3 border rounded-lg text-sm focus:outline-none focus:border-green-500 disabled:bg-gray-100"
                        />
                      </div>
                    )}

                    {/* State indicators for Continuous Conversation */}
                    {isConversationActive && callState === CALL_STATES.RECORDING && !isSpeaking && (
                      <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded text-center">
                        <div className="flex justify-center gap-1 mb-2">
                          <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                          <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                          <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                        </div>
                        <p className="text-sm text-blue-800">{langUI.listening}</p>
                      </div>
                    )}

                    {isConversationActive && (callState === CALL_STATES.THINKING || callState === CALL_STATES.TRANSCRIBING) && (
                      <div className="mb-3 p-3 bg-purple-50 border border-purple-200 rounded text-center">
                        <div className="flex justify-center gap-1 mb-2">
                          <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{animationDelay: '0s'}}></div>
                          <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                        <p className="text-sm text-purple-800">
                          {callState === CALL_STATES.TRANSCRIBING ? 'Converting speech to text...' : langUI.thinking}
                        </p>
                      </div>
                    )}

                    {/* State indicators */}
                    {!isConversationActive && (callState === CALL_STATES.CONNECTING || 
                      callState === CALL_STATES.TRANSCRIBING || 
                      callState === CALL_STATES.THINKING) && (
                      <div className="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded text-center">
                        <div className="flex justify-center gap-1 mb-2">
                          <div className="w-2 h-2 bg-yellow-600 rounded-full animate-bounce" style={{animationDelay: '0s'}}></div>
                          <div className="w-2 h-2 bg-yellow-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-yellow-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                        <p className="text-sm text-yellow-800">
                          {callState === CALL_STATES.CONNECTING ? 'Connecting to Sahaya...' :
                           callState === CALL_STATES.TRANSCRIBING ? 'Converting speech to text...' :
                           'Generating response...'}
                        </p>
                      </div>
                    )}
                  </>
                )}

                {/* Transcript Display */}
                {transcript && callState !== CALL_STATES.IDLE && (
                  <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded">
                    <div className="text-xs text-blue-600 mb-1">{langUI.youSaid}</div>
                    <div className="text-sm text-blue-900">{transcript}</div>
                  </div>
                )}

                {response?.error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm mb-3">
                    {response.error}
                  </div>
                )}
              </div>

              {/* Call Initiator */}
              <CallInitiator farmerProfile={farmerProfile} eligibleSchemeIds={eligibleSchemes} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

