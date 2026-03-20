import React, { useState, useRef, useEffect } from 'react';
import { askQuestion } from '../api';

const QAChat = ({ requestId }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: '👋 Hi! I can answer questions about your legal document. Try asking things like:\n• "What is the payment amount?"\n• "When does this agreement end?"\n• "What happens if someone breaches the contract?"'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const question = input.trim();
    if (!question || isLoading) return;

    setMessages(prev => [...prev, { role: 'user', text: question }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await askQuestion(requestId, question);

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: response.answer,
          sources: response.sources || []
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          text: `❌ Error: ${err.message || 'Could not get answer. Check your Groq API key.'}`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="qa-chat">
      <div className="qa-header">
        <h3>💬 Ask Questions About Your Document</h3>
        <p className="qa-subtitle">Powered by Groq API (LLaMA3) · RAG Pipeline</p>
      </div>

      <div className="qa-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`qa-message ${msg.role}`}>
            <div className="qa-bubble">
              {msg.text.split('\n').map((line, j) => (
                <p key={j} style={{ margin: '2px 0' }}>{line}</p>
              ))}
              {msg.sources && msg.sources.length > 0 && (
                <div className="qa-sources">
                  <p className="sources-label">📄 Based on:</p>
                  {msg.sources.map((src, j) => (
                    <p key={j} className="source-text">
                      "{src.clause}"
                      <span className="source-score">
                        relevance: {src.relevance_score}
                      </span>
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="qa-message assistant">
            <div className="qa-bubble typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="qa-input-row">
        <input
          type="text"
          className="qa-input"
          placeholder="Ask anything about your document..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          className="qa-send-btn"
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default QAChat;
