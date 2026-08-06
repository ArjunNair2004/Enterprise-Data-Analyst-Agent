import { useState, useCallback, useEffect } from 'react'
import { 
  Database, UploadCloud, CheckCircle2, X, Mic, Loader2, Search 
} from 'lucide-react'
import { useDropzone } from 'react-dropzone'
// Import Recharts components
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

function App() {
  const [input, setInput] = useState('')
  const [activeDataset, setActiveDataset] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isSending, setIsSending] = useState(false)
  
  // New state for Voice features
  const [isListening, setIsListening] = useState(false)
  const [availableVoices, setAvailableVoices] = useState([])

  const [messages, setMessages] = useState([
    {
      role: 'agent',
      type: 'text',
      content: 'Welcome! Import a CSV dataset to get started, then ask any analytical question.'
    }
  ])

  // Load available browser voices on mount for Text-to-Speech
  useEffect(() => {
    const updateVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      setAvailableVoices(voices);
    };
    
    updateVoices();
    window.speechSynthesis.onvoiceschanged = updateVoices;
  }, []);

  // --- VOICE LOGIC ---

  // 1. SPEECH-TO-TEXT: Listen to user's voice and type it into the search bar
  const handleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Try Google Chrome or Microsoft Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript); // Automatically fill the search bar
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setIsListening(false);
    };

    recognition.start();
  };

  // 2. TEXT-TO-SPEECH: Make the AI speak its response naturally
  const speakResponse = (text) => {
    if (!('speechSynthesis' in window)) return;

    // Stop any ongoing speech
    window.speechSynthesis.cancel();

    // Remove markdown symbols (like **bold**) before speaking so it sounds natural
    const cleanText = text.replace(/\*\*(.*?)\*\*/g, '$1').replace(/#/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    
    // Attempt to pick a natural-sounding English voice
    const naturalVoice = availableVoices.find(voice => 
      (voice.name.includes('Natural') || voice.name.includes('Google') || voice.name.includes('Microsoft')) && 
      voice.lang.includes('en')
    ) || availableVoices.find(voice => voice.lang.includes('en'));

    if (naturalVoice) {
      utterance.voice = naturalVoice;
    }

    utterance.rate = 1.0; 
    utterance.pitch = 1.0; 

    window.speechSynthesis.speak(utterance);
  };

  // --- CORE APP LOGIC ---

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return
    const file = acceptedFiles[0]
    
    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('Upload failed')
      
      const data = await response.json()
      setActiveDataset({ name: file.name, size: file.size, serverPath: data.filename })
      
      const successMessage = `Successfully loaded dataset "${file.name}". You can now query your data.`
      setMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          type: 'text',
          content: successMessage
        }
      ])
      
      // Optionally have the AI announce the successful upload
      speakResponse(successMessage);

    } catch (error) {
      console.error('Upload Error:', error)
      alert('Failed to connect to backend server. Make sure FastAPI is running on port 8000.')
    } finally {
      setIsUploading(false)
    }
  }, [availableVoices])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    multiple: false,
    disabled: isUploading
  })

  const sendMessage = async (e) => {
    if (e) e.preventDefault()
    if (!input.trim() || isSending) return

    const userMessage = input.trim()
    setInput('')
    
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setIsSending(true)

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: userMessage,
          dataset_name: activeDataset?.name || null 
        }),
      })

      if (!response.ok) throw new Error('Server response failed')

      const data = await response.json()
      
      if (Array.isArray(data.responses)) {
        setMessages((prev) => [...prev, ...data.responses])
        
        // Find text response and speak it
        const textResponse = data.responses.find(r => r.type === 'text')?.content;
        if (textResponse) speakResponse(textResponse);

      } else {
        setMessages((prev) => [...prev, data])
        if (data.type === 'text') speakResponse(data.content);
      }
    } catch (error) {
      console.error('Chat Error:', error)
      setMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          type: 'text',
          content: 'Error: Failed to reach backend agent.'
        }
      ])
    } finally {
      setIsSending(false)
    }
  }

  const removeDataset = (e) => {
    e.stopPropagation()
    setActiveDataset(null)
  }

  const renderMessageContent = (msg) => {
    if (msg.role === 'user' || msg.type === 'text') {
      const formattedText = msg.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      return (
        <div 
          className="text-slate-800 leading-relaxed whitespace-pre-wrap"
          dangerouslySetInnerHTML={{ __html: formattedText }}
        />
      )
    }

    if (msg.type === 'chart') {
      return (
        <div className="mt-4 h-72 w-full bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={msg.data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis 
                dataKey={msg.x_key} 
                axisLine={false} 
                tickLine={false} 
                tick={{fill: '#64748b', fontSize: 12}} 
                dy={10}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{fill: '#64748b', fontSize: 12}} 
                tickFormatter={(value) => `$${value.toLocaleString()}`}
              />
              <Tooltip 
                cursor={{fill: '#f8fafc'}}
                contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                formatter={(value) => [`$${value.toLocaleString()}`, 'Revenue']}
              />
              <Bar dataKey={msg.y_key} fill="#2563eb" radius={[4, 4, 0, 0]} barSize={40} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )
    }
  }

  return (
    <div className="flex h-screen bg-slate-100 text-slate-900 font-sans selection:bg-blue-200">
      
      {/* Sidebar */}
      <aside className="w-72 bg-slate-50 border-r border-slate-200 flex flex-col justify-between shadow-sm z-20">
        <div className="p-5 flex flex-col gap-6">
          <div className="flex items-center gap-3 text-blue-700 px-1">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Database size={20} />
            </div>
            <h1 className="text-lg font-bold tracking-tight">AI Analyst</h1>
          </div>
          
          <div 
            {...getRootProps()} 
            className={`relative border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-200 ${
              isDragActive ? 'border-blue-500 bg-blue-50 scale-[1.02]' : 'border-slate-300 hover:border-blue-400 hover:bg-white'
            } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getInputProps()} />
            
            {isUploading ? (
              <div className="flex flex-col items-center">
                <Loader2 size={28} className="animate-spin text-blue-600 mb-2" />
                <p className="text-xs font-semibold text-slate-600">Uploading dataset...</p>
              </div>
            ) : !activeDataset ? (
              <>
                <UploadCloud size={28} className={`mb-3 ${isDragActive ? 'text-blue-500' : 'text-slate-400'}`} />
                <p className="text-sm font-semibold text-slate-700">
                  {isDragActive ? "Drop CSV here" : "Import Dataset"}
                </p>
                <p className="text-xs text-slate-500 mt-1">CSV files up to 50MB</p>
              </>
            ) : (
              <div className="flex flex-col items-center w-full">
                <CheckCircle2 size={28} className="mb-2 text-emerald-500" />
                <p className="text-sm font-semibold text-slate-800 truncate w-full px-2">
                  {activeDataset.name}
                </p>
                <button 
                  onClick={removeDataset}
                  className="absolute top-2 right-2 p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                >
                  <X size={14} />
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col bg-white">
        
        <header className="h-16 border-b border-slate-200 bg-white flex items-center justify-between px-8 z-10">
          <div className="flex items-center gap-2">
            <h2 className="font-semibold text-slate-800">Data Exploration Session</h2>
          </div>
          {/* Top header Voice Command button has been completely removed as requested */}
        </header>

        <main className="flex-1 overflow-y-auto p-8 flex flex-col gap-6 bg-slate-50/50">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`
                ${msg.role === 'user' 
                  ? 'max-w-2xl bg-blue-600 text-white rounded-2xl rounded-br-sm px-5 py-3.5 shadow-sm' 
                  : 'max-w-4xl w-full bg-transparent'
                }
              `}>
                {msg.role === 'agent' && (
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center text-blue-700">
                      <Database size={12} />
                    </div>
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">AI Agent</span>
                  </div>
                )}
                {renderMessageContent(msg)}
              </div>
            </div>
          ))}

          {isSending && (
            <div className="flex items-center gap-3 text-slate-500 py-2">
              <Loader2 size={18} className="animate-spin text-blue-600" />
              <span className="text-sm font-medium">Analyzing dataset...</span>
            </div>
          )}
        </main>

        {/* Updated Footer Layout matches the Flexbox image reference */}
        <footer className="p-6 bg-white border-t border-slate-100 shadow-[0_-10px_40px_rgba(0,0,0,0.03)]">
          <form onSubmit={sendMessage} className="max-w-4xl mx-auto flex items-center gap-3">
            
            {/* Unified Search Bar & Search Button */}
            <div className="flex flex-1 items-center bg-slate-50 border border-slate-200 rounded-full overflow-hidden focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
              <input 
                type="text" 
                value={input} 
                onChange={(e) => setInput(e.target.value)} 
                disabled={!activeDataset || isSending}
                placeholder={activeDataset ? "e.g., Show top revenue by category..." : "Import a dataset first..."} 
                className="flex-1 bg-transparent text-slate-800 placeholder-slate-400 px-6 py-3.5 outline-none disabled:opacity-50"
              />
              <button 
                type="submit" 
                disabled={!activeDataset || !input.trim() || isSending}
                className="text-slate-500 p-3.5 px-6 hover:bg-slate-200 transition-colors border-l border-slate-200 disabled:opacity-50 flex items-center justify-center"
              >
                <Search size={20} />
              </button>
            </div>

            {/* Voice Command Button placed exactly next to the search bar */}
            <button 
              type="button"
              onClick={handleVoiceInput}
              disabled={!activeDataset || isSending}
              title="Click to speak your query"
              className={`flex items-center justify-center p-3.5 rounded-full transition-all border ${
                isListening 
                  ? 'bg-red-500 text-white border-red-500 animate-pulse scale-105' 
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:text-blue-600'
              } disabled:opacity-50`}
            >
              <Mic size={20} />
            </button>

          </form>
        </footer>
      </div>
    </div>
  )
}

export default App