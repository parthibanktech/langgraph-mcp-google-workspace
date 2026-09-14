import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  Send, 
  Sparkles, 
  Wrench, 
  User, 
  FileText, 
  Mail, 
  HardDrive, 
  CheckCircle2 
} from 'lucide-react';

export default function AgentChatView() {
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      text: 'Hello! I am your Gmail & Google Drive MCP Agent. How can I assist your workflow today?',
      toolsUsed: []
    }
  ]);

  const [inputPrompt, setInputPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const quickPrompts = [
    "Check my unread emails",
    "Search Google Drive for project documents",
    "List my recent Gmail messages",
    "Find spreadsheets in Drive"
  ];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (customPrompt) => {
    const textToSend = customPrompt || inputPrompt;
    if (!textToSend.trim() || loading) return;

    const userMsg = { sender: 'user', text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInputPrompt('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend })
      });
      if (!res.ok) {
        if (res.status === 502 || res.status === 504 || res.status === 500) {
          throw new Error(`Backend server offline (HTTP ${res.status}). Please ensure 'python backend/api.py' is running on port 8000.`);
        }
        throw new Error(`HTTP ${res.status}: ${res.statusText || 'Server Error'}`);
      }
      const rawText = await res.text();
      let data;
      try {
        data = JSON.parse(rawText);
      } catch {
        throw new Error("Invalid or empty response received from API server.");
      }

      if (data.status === 'success') {
        const agentMsg = {
          sender: 'agent',
          text: data.message || 'Agent processed your request successfully.',
          toolsUsed: data.tools_used || [],
          resultData: data.data
        };
        setMessages((prev) => [...prev, agentMsg]);
      } else {
        setMessages((prev) => [
          ...prev,
          { sender: 'agent', text: 'Error processing message: ' + (data.message || 'Unknown error') }
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: 'agent', text: 'Backend communication error: ' + err.message }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Quick Prompts Bar */}
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '16px' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Sparkles size={14} /> Preset Prompts:
        </span>
        {quickPrompts.map((promptText, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(promptText)}
            className="badge badge-indigo"
            style={{ cursor: 'pointer', border: 'none', padding: '6px 12px' }}
          >
            {promptText}
          </button>
        ))}
      </div>

      {/* Main Chat Area */}
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`chat-bubble ${msg.sender === 'user' ? 'chat-bubble-user' : 'chat-bubble-agent'}`}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', fontSize: '0.75rem', opacity: 0.85 }}>
                {msg.sender === 'user' ? <User size={14} /> : <Bot size={14} />}
                <span>{msg.sender === 'user' ? 'You' : 'MCP AI Agent'}</span>
              </div>

              <div>{msg.text}</div>

              {/* Tools Execution Indicator */}
              {msg.toolsUsed && msg.toolsUsed.length > 0 && (
                <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.1)', fontSize: '0.75rem' }}>
                  <div style={{ fontWeight: 600, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px', color: '#FBBF24' }}>
                    <Wrench size={12} /> Executed MCP Tools:
                  </div>
                  {msg.toolsUsed.map((tool, tIdx) => (
                    <span key={tIdx} className="badge badge-amber" style={{ marginRight: '6px', fontSize: '0.7rem' }}>
                      {tool.name} ({JSON.stringify(tool.query || tool.keyword || 'ok')})
                    </span>
                  ))}
                </div>
              )}

              {/* Data Items Preview */}
              {msg.resultData && Array.isArray(msg.resultData) && msg.resultData.length > 0 && (
                <div style={{ marginTop: '10px', background: 'rgba(0, 0, 0, 0.2)', padding: '8px 12px', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#34D399', marginBottom: '4px' }}>
                    Returned Data ({msg.resultData.length} items):
                  </div>
                  <ul style={{ paddingLeft: '16px', fontSize: '0.8rem' }}>
                    {msg.resultData.map((item, dIdx) => (
                      <li key={dIdx}>
                        {item.subject || item.name || item.id || JSON.stringify(item)}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="chat-bubble chat-bubble-agent" style={{ opacity: 0.7 }}>
              <Bot size={16} className="animate-spin" /> Thinking & executing MCP tool calls...
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <form
          className="chat-input-row"
          onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
        >
          <input
            type="text"
            placeholder="Ask the AI agent to summarize emails, search Drive, or send messages..."
            className="form-input"
            style={{ flex: 1 }}
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={loading || !inputPrompt.trim()}>
            Send <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
