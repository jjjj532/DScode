import { useState, useRef, useEffect } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMsg: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg.content,
          session_id: sessionId,
        }),
      })
      const data = await res.json()
      setSessionId(data.session_id)
      const assistantMsg: Message = { role: 'assistant', content: data.response }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      const errorMsg: Message = { role: 'assistant', content: 'Error: ' + String(err) }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 20, fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ borderBottom: '2px solid #646cff', paddingBottom: 10 }}>
        CScode
        <span style={{ fontSize: 14, color: '#666', marginLeft: 10 }}>
          AI Coding Assistant
        </span>
      </h1>

      <div style={{
        height: '60vh',
        overflowY: 'auto',
        border: '1px solid #ccc',
        borderRadius: 8,
        padding: 16,
        marginBottom: 16,
        background: '#fafafa',
      }}>
        {messages.length === 0 && (
          <p style={{ color: '#999', textAlign: 'center', marginTop: 40 }}>
            Send a message to start chatting with CScode.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{
            marginBottom: 12,
            textAlign: msg.role === 'user' ? 'right' : 'left',
          }}>
            <div style={{
              display: 'inline-block',
              padding: '8px 16px',
              borderRadius: 12,
              background: msg.role === 'user' ? '#646cff' : '#e0e0e0',
              color: msg.role === 'user' ? '#fff' : '#000',
              maxWidth: '80%',
              whiteSpace: 'pre-wrap',
            }}>
              {msg.content}
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
          disabled={loading}
          style={{
            flex: 1,
            padding: '10px 16px',
            borderRadius: 8,
            border: '1px solid #ccc',
            fontSize: 16,
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{
            padding: '10px 24px',
            borderRadius: 8,
            border: 'none',
            background: loading ? '#ccc' : '#646cff',
            color: '#fff',
            fontSize: 16,
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  )
}

export default App
