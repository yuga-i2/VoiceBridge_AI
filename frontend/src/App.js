import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import API from './config/api'
import './App.css'

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

    const utterance = new SpeechSynthesisUtterance(text)
    
    // Language and voice selection
    utterance.lang = 'hi-IN'
    utterance.rate = 0.95 // Slightly slower for clarity
    utterance.pitch = 1.0
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
const VoiceMemoryClip = ({ clip, schemeId }) => {
  if (!clip) return null
  
  const clips = {
    'PM_KISAN': { farmer: 'Suresh Kumar', district: 'Tumkur', state: 'Karnataka' },
    'KCC': { farmer: 'Ramaiah', district: 'Mysuru', state: 'Karnataka' },
    'PMFBY': { farmer: 'Laxman Singh', district: 'Dharwad', state: 'Karnataka' }
  }
  
  const info = clips[schemeId] || { farmer: 'Kisan', district: 'Local', state: 'India' }
  
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
      </div>
      <p className="text-sm font-semibold text-amber-900 mb-1">
        {info.farmer}, {info.district} district, {info.state}
      </p>
      <p className="text-xs text-amber-700 mb-3">
        "Real success story from a farmer in your region — how they benefited from this scheme"
      </p>
      <audio controls src={clip} className="w-full h-8 rounded" />
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
    <div className="bg-white rounded-lg border p-4 mb-4">
      <h3 className="font-semibold text-gray-800 mb-3">AWS Services (8/8)</h3>
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
         '📲 Sahaya Ko Call Karne Do (Initiate AI Call)'}
      </button>
      {callStatus && (
        <div className={`mt-3 p-2 rounded text-sm ${
          callStatus.success ? 'bg-green-50 text-green-800' : 
          'bg-red-50 text-red-800'
        }`}>
          {callStatus.success ? 
            `✅ ${callStatus.message}` : 
            `❌ ${callStatus.error}`}
          {callStatus.provider && (
            <span className="ml-2 text-xs opacity-70">
              via {callStatus.provider}
            </span>
          )}
        </div>
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
  const [transcript, setTranscript] = useState('')
  const [response, setResponse] = useState(null)
  const [conversationHistory, setConversationHistory] = useState([])
  
  // NEW: Call state machine
  const [callState, setCallState] = useState(CALL_STATES.IDLE)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [inputEnabled, setInputEnabled] = useState(false)
  
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  // Load all schemes on mount
  useEffect(() => {
    loadSchemes()
  }, [])

  const loadSchemes = async () => {
    try {
      const res = await axios.get(API.schemes)
      setAllSchemes(res.data.schemes || [])
    } catch(e) {
      console.error('Failed to load schemes:', e)
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
      const res = await axios.post(API.eligibilityCheck, {
        farmer_profile: DEMO_FARMER
      })
      setEligibleSchemes(res.data.eligible_schemes || [])
    } catch(e) {
      console.error('Eligibility check failed:', e)
    }
  }

  // ========== SAHAYA OPENING SPEECH ==========
  const startSahayaCall = async () => {
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

  // ========== MICROPHONE RECORDING ==========
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = async () => {
        if (chunksRef.current.length === 0) {
          console.error('No audio chunks recorded')
          setCallState(CALL_STATES.WAITING)
          alert('No audio recorded. Please try again.')
          return
        }
        
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        stream.getTracks().forEach(track => track.stop())
        processAudio(audioBlob)
      }

      mediaRecorder.start(100) // collect chunks every 100ms
      setIsRecording(true)
      setCallState(CALL_STATES.RECORDING)
      setInputEnabled(false)

      // Auto-stop after 5 seconds
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop()
          setIsRecording(false)
          stream.getTracks().forEach(track => track.stop())
        }
      }, 5000)
    } catch(e) {
      console.error('Microphone error:', e)
      alert('Microphone access denied. Please type your message instead.')
      setCallState(CALL_STATES.WAITING)
      setInputEnabled(true)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  // ========== AUDIO PROCESSING & CHAT ==========
  const processAudio = async (audioBlob) => {
    try {
      if (!audioBlob || audioBlob.size === 0) {
        console.error('Empty audio blob')
        setCallState(CALL_STATES.WAITING)
        alert('No audio recorded. Please try again.')
        return
      }

      setCallState(CALL_STATES.TRANSCRIBING)

      // Send audio as FormData (required by backend)
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')

      const sttRes = await axios.post(API.stt, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      const userMessage = sttRes.data.transcription || sttRes.data.text || ''
      if (!userMessage) {
        console.error('No transcription returned')
        setCallState(CALL_STATES.WAITING)
        alert('Could not understand audio. Please try again.')
        return
      }
      
      setTranscript(userMessage)
      setCallState(CALL_STATES.THINKING)

      // Get AI response
      const chatRes = await axios.post(API.chat, {
        message: userMessage,
        farmer_profile: farmerProfile,
        conversation_history: conversationHistory
      })

      const aiResponse = {
        text: chatRes.data.response_text,
        schemes: chatRes.data.schemes_mentioned || [],
        stage: chatRes.data.stage,
        voice_memory_clip: chatRes.data.voice_memory_clip,
        audio_url: chatRes.data.audio_url
      }

      // Update matched schemes
      if (aiResponse.schemes && aiResponse.schemes.length > 0) {
        setMatchedSchemes(prev => [...new Set([...prev, ...aiResponse.schemes])])
      }

      setResponse(aiResponse)
      setConversationHistory(prev => [
        ...prev,
        { role: 'user', content: userMessage },
        { role: 'assistant', content: aiResponse.text }
      ])

      // Handle audio playback with fallback to TTS
      if (aiResponse.audio_url) {
        // Try to play Polly audio first
        const audio = new Audio(aiResponse.audio_url)
        audio.onplay = () => {
          setIsSpeaking(true)
          setCallState(CALL_STATES.SAHAYA_SPEAKING)
        }
        audio.onended = () => {
          setIsSpeaking(false)
          setCallState(CALL_STATES.WAITING)
          setInputEnabled(true)
        }
        audio.onerror = () => {
          console.log('Polly audio failed, falling back to browser TTS')
          speakAndWait(aiResponse.text)
        }
        audio.play().catch(e => {
          console.log('Audio playback failed:', e)
          speakAndWait(aiResponse.text)
        })
      } else {
        // Fallback to browser TTS if no Polly audio
        speakAndWait(aiResponse.text)
      }
    } catch(e) {
      console.error('Chat failed:', e)
      setResponse({ error: 'Chat processing failed: ' + e.message })
      setCallState(CALL_STATES.WAITING)
      setInputEnabled(true)
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
    
    try {
      setCallState(CALL_STATES.THINKING)
      setInputEnabled(false)

      const chatRes = await axios.post(API.chat, {
        message: userMessage,
        farmer_profile: farmerProfile,
        conversation_history: conversationHistory
      })

      const aiResponse = {
        text: chatRes.data.response_text,
        schemes: chatRes.data.schemes_mentioned || [],
        stage: chatRes.data.stage,
        voice_memory_clip: chatRes.data.voice_memory_clip,
        audio_url: chatRes.data.audio_url
      }

      // Update matched schemes
      if (aiResponse.schemes && aiResponse.schemes.length > 0) {
        setMatchedSchemes(prev => [...new Set([...prev, ...aiResponse.schemes])])
      }

      setResponse(aiResponse)
      setConversationHistory(prev => [
        ...prev,
        { role: 'user', content: userMessage },
        { role: 'assistant', content: aiResponse.text }
      ])

      // Handle audio playback with fallback
      if (aiResponse.audio_url) {
        const audio = new Audio(aiResponse.audio_url)
        audio.onplay = () => {
          setIsSpeaking(true)
          setCallState(CALL_STATES.SAHAYA_SPEAKING)
        }
        audio.onended = () => {
          setIsSpeaking(false)
          setCallState(CALL_STATES.WAITING)
          setInputEnabled(true)
        }
        audio.onerror = () => {
          speakAndWait(aiResponse.text)
        }
        audio.play().catch(() => {
          speakAndWait(aiResponse.text)
        })
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
        <ArchitectureBadges />

        {/* Demo Button and Profile */}
        {!farmerProfile ? (
          <div className="bg-white rounded-lg border p-6 mb-4 text-center">
            <h2 className="text-xl font-bold text-gray-800 mb-3">
              Welcome to VoiceBridge AI
            </h2>
            <p className="text-gray-600 mb-4">
              Experience how Sahaya brings welfare schemes to farmers via voice.
            </p>
            <button
              onClick={loadDemoFarmer}
              className="bg-green-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-800"
            >
              🎤 Load Demo Farmer (Ramesh Kumar)
            </button>
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
                              <div className="font-semibold">{scheme?.name}</div>
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
                          ? 'bg-blue-100 text-blue-900 text-right' 
                          : 'bg-green-100 text-green-900'
                      }`}>
                        {msg.role === 'user' ? '👨 You: ' : '🎙️ Sahaya: '}
                        {msg.content.substring(0, 100)}
                        {msg.content.length > 100 ? '...' : ''}
                      </div>
                    ))}
                  </div>
                )}

                {/* Microphone Button or Text Input - depends on state */}
                {callState === CALL_STATES.IDLE && (
                  <div className="mb-3">
                    <button
                      onClick={startSahayaCall}
                      className="w-full py-4 rounded-lg font-bold text-lg transition-all bg-green-600 text-white hover:bg-green-700 animate-pulse"
                    >
                      📞 Start Call with Sahaya
                    </button>
                    <p className="text-xs text-gray-500 mt-2 text-center">
                      Click to simulate receiving a call from Sahaya
                    </p>
                  </div>
                )}

                {callState !== CALL_STATES.IDLE && (
                  <>
                    {/* Microphone Button */}
                    {!isSpeaking && callState === CALL_STATES.WAITING && (
                      <div className="mb-3">
                        <button
                          onClick={isRecording ? stopRecording : startRecording}
                          disabled={!inputEnabled || isSpeaking || callState !== CALL_STATES.WAITING}
                          className={`w-full py-4 rounded-lg font-bold text-lg transition-all ${
                            isRecording
                              ? 'bg-red-500 text-white animate-pulse hover:bg-red-600'
                              : inputEnabled
                              ? 'bg-green-600 text-white hover:bg-green-700'
                              : 'bg-gray-400 text-gray-200 cursor-not-allowed'
                          }`}
                        >
                          {isRecording ? '🔴 Recording... Tap to stop' : '🎤 Speak your message'}
                        </button>
                      </div>
                    )}

                    {/* Text Input (always available after call starts) */}
                    {callState === CALL_STATES.WAITING && !isSpeaking && (
                      <div className="mb-3">
                        <input
                          type="text"
                          placeholder="Or type your message..."
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              handleTextInput(e)
                            }
                          }}
                          disabled={!inputEnabled}
                          className="w-full p-3 border rounded-lg text-sm focus:outline-none focus:border-green-500 disabled:bg-gray-100"
                        />
                      </div>
                    )}

                    {/* State indicators */}
                    {(callState === CALL_STATES.CONNECTING || 
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
                    <div className="text-xs text-blue-600 mb-1">You said:</div>
                    <div className="text-sm text-blue-900">{transcript}</div>
                  </div>
                )}

                {/* Response Display */}
                {response && (
                  <div className="space-y-2">
                    <div className="p-3 bg-green-50 border border-green-200 rounded">
                      <div className="text-xs text-green-600 mb-1">Sahaya says:</div>
                      <div className="text-sm text-green-900">{response.text}</div>
                    </div>

                    {response.audio_url && (
                      <div className="p-2 bg-purple-50 border border-purple-200 rounded">
                        <audio controls src={response.audio_url} className="w-full h-8" />
                        <p className="text-xs text-purple-600 mt-1">Polly audio (from India region)</p>
                      </div>
                    )}

                    {response.voice_memory_clip && (
                      <VoiceMemoryClip clip={response.voice_memory_clip} schemeId={response.schemes?.[0]} />
                    )}

                    {response.schemes && response.schemes.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {response.schemes.map(s => (
                          <span key={s} className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs font-semibold border border-yellow-300">
                            ✓ {s}
                          </span>
                        ))}
                      </div>
                    )}

                    {response.error && (
                      <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
                        {response.error}
                      </div>
                    )}
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

