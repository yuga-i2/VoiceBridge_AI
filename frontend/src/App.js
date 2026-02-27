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
    <div className="bg-amber-50 border border-amber-300 rounded-lg p-3 mt-2">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-amber-600">🎙️</span>
        <span className="text-sm font-semibold text-amber-800">
          Voice Memory Network
        </span>
      </div>
      <p className="text-xs text-amber-700 mb-2">
        Message from {info.farmer}, farmer from {info.district} district, {info.state}:
      </p>
      <audio controls src={clip} className="w-full h-8" />
      <p className="text-xs text-amber-600 mt-1 italic">
        "Real success story from a farmer in your region"
      </p>
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
  const [farmerProfile, setFarmerProfile] = useState(null)
  const [eligibleSchemes, setEligibleSchemes] = useState([])
  const [allSchemes, setAllSchemes] = useState([])
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [response, setResponse] = useState(null)
  const [conversationHistory, setConversationHistory] = useState([])
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
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        stream.getTracks().forEach(track => track.stop())
        processAudio(audioBlob)
      }

      mediaRecorder.start(100) // collect chunks every 100ms
      setIsRecording(true)

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
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const processAudio = async (audioBlob) => {
    try {
      if (!audioBlob || audioBlob.size === 0) {
        console.error('Empty audio blob')
        alert('No audio recorded. Please try again.')
        return
      }

      // Send audio as FormData (required by backend)
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')

      const sttRes = await axios.post(API.stt, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      const userMessage = sttRes.data.transcription || sttRes.data.text || ''
      if (!userMessage) {
        console.error('No transcription returned')
        alert('Could not understand audio. Please try again.')
        return
      }
      
      setTranscript(userMessage)

      // Get AI response
      const chatRes = await axios.post(API.chat, {
        message: userMessage,
        farmer_profile: farmerProfile,
        conversation_history: conversationHistory
      })

      const aiResponse = {
        text: chatRes.data.response_text,
        schemes: chatRes.data.schemes,
        voice_memory_clip: chatRes.data.voice_memory_clip,
        audio_url: chatRes.data.audio_url
      }

      setResponse(aiResponse)
      setConversationHistory([
        ...conversationHistory,
        { role: 'user', content: userMessage },
        { role: 'assistant', content: aiResponse.text }
      ])

      // Auto-play audio if available
      if (aiResponse.audio_url) {
        const audio = new Audio(aiResponse.audio_url)
        audio.play().catch(e => console.log('Audio playback failed:', e))
      }
    } catch(e) {
      console.error('Chat failed:', e)
      setResponse({ error: 'Chat processing failed' })
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
            {/* Left: Schemes List */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg border p-4">
                <h3 className="font-bold text-lg mb-3">Eligible Schemes</h3>
                <EligibilityScore schemes={eligibleSchemes} />
                {eligibleSchemes && eligibleSchemes.length > 0 ? (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {eligibleSchemes.map(schemeId => {
                      const scheme = allSchemes.find(s => s.scheme_id === schemeId)
                      return (
                        <div key={schemeId} className="bg-green-50 border border-green-200 rounded p-2 text-xs">
                          <div className="font-semibold text-green-900">{scheme?.name}</div>
                          <div className="text-green-700 text-xs">{scheme?.benefit}</div>
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
                <h3 className="font-bold text-lg mb-3">🎤 Talk to Sahaya</h3>
                <div className="mb-3">
                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`w-full py-4 rounded-lg font-bold text-lg transition-all ${
                      isRecording
                        ? 'bg-red-500 text-white animate-pulse hover:bg-red-600'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {isRecording ? '🔴 Recording... Tap to stop' : '🎤 Talk to Sahaya'}
                  </button>
                </div>

                {transcript && (
                  <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded">
                    <div className="text-xs text-blue-600 mb-1">You said:</div>
                    <div className="text-sm text-blue-900">{transcript}</div>
                  </div>
                )}

                {response && (
                  <div className="space-y-2">
                    <div className="p-3 bg-green-50 border border-green-200 rounded">
                      <div className="text-xs text-green-600 mb-1">Sahaya says:</div>
                      <div className="text-sm text-green-900">{response.text}</div>
                    </div>

                    {response.audio_url && (
                      <div className="p-2 bg-purple-50 border border-purple-200 rounded">
                        <audio controls src={response.audio_url} className="w-full h-8" />
                      </div>
                    )}

                    {response.voice_memory_clip && (
                      <VoiceMemoryClip clip={response.voice_memory_clip} schemeId={response.schemes?.[0]} />
                    )}

                    {response.schemes && response.schemes.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {response.schemes.map(s => (
                          <span key={s} className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs">
                            {s}
                          </span>
                        ))}
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

