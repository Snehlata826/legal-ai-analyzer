import React, { useRef, useEffect, useState } from 'react';
import { askQuestion } from '../api';

const WELCOME = {
  role: 'assistant',
  text: 'Hello! Ask me anything about your legal document.',
  suggestions: [
    'Who are the parties in this agreement?',
    'What is the payment amount?',
    'What happens if someone breaches the contract?',
    'Where will disputes be resolved?',
  ]
};

const QAChat = ({ requestId, messages, setMessages }) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([WELCOME]);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading, isOpen]);

  const sendMessage = async (text) => {
    const question = text.trim();
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
          text: `Sorry, I encountered an error: ${err.message || 'Please try again.'}`,
          isError: true
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const handleClearChat = () => {
    setMessages([WELCOME]);
  };

  const unreadCount = messages.filter(m => m.role === 'user').length;

  const renderAnswerText = (text) => {
    return text.split('\n').map((line, i) => {
      const parts = line.split(/\*\*(.*?)\*\*/g);
      return (
        <p key={i} className="answer-line">
          {parts.map((part, k) =>
            k % 2 === 1 ? <strong key={k}>{part}</strong> : part
          )}
        </p>
      );
    });
  };

  return (
    <>
      {/* Floating Chat Panel */}
      {isOpen && (
        <div className="floating-chat-panel">
          {/* Header */}
          <div className="floating-chat-header">
            <div className="floating-chat-header-left">
              <div className="floating-chat-avatar">⚖</div>
              <div>
                <p className="floating-chat-title">LexAI Assistant</p>
                <p className="floating-chat-sub">RAG · Groq LLaMA3</p>
              </div>
            </div>
            <div className="floating-chat-header-actions">
              <button
                className="floating-chat-clear"
                onClick={handleClearChat}
                title="Clear chat"
              >
                🗑
              </button>
              <button
                className="floating-chat-close"
                onClick={() => setIsOpen(false)}
                title="Close"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="floating-chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`floating-msg-row floating-msg-row--${msg.role}`}>
                {msg.role === 'assistant' && (
                  <div className={`floating-msg-bubble floating-msg-bubble--ai ${msg.isError ? 'floating-msg-bubble--error' : ''}`}>
                    <div className="floating-msg-avatar">AI</div>
                    <div className="floating-msg-body">
                      <div className="floating-msg-text">
                        {renderAnswerText(msg.text)}
                      </div>

                      {msg.suggestions && (
                        <div className="floating-suggestion-chips">
                          {msg.suggestions.map((s, j) => (
                            <button
                              key={j}
                              className="floating-suggestion-chip"
                              onClick={() => sendMessage(s)}
                              disabled={isLoading}
                            >
                              {s}
                            </button>
                          ))}
                        </div>
                      )}

                      {msg.sources && msg.sources.length > 0 && (
                        <details className="floating-msg-sources">
                          <summary className="floating-sources-toggle">
                            View sources ({msg.sources.length})
                          </summary>
                          <div className="floating-sources-body">
                            {msg.sources.map((src, j) => (
                              <div key={j} className="floating-source-clause">
                                <span className="floating-source-num">§{j + 1}</span>
                                <p className="floating-source-text">"{src.clause}"</p>
                              </div>
                            ))}
                          </div>
                        </details>
                      )}
                    </div>
                  </div>
                )}

                {msg.role === 'user' && (
                  <div className="floating-msg-bubble floating-msg-bubble--user">
                    <p className="floating-msg-text">{msg.text}</p>
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="floating-msg-row floating-msg-row--assistant">
                <div className="floating-msg-bubble floating-msg-bubble--ai">
                  <div className="floating-msg-avatar">AI</div>
                  <div className="floating-typing-indicator">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="floating-chat-input-area">
            <input
              type="text"
              className="floating-chat-input"
              placeholder="Ask about your document..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              autoFocus
            />
            <button
              className="floating-chat-send"
              onClick={() => sendMessage(input)}
              disabled={isLoading || !input.trim()}
            >
              ➤
            </button>
          </div>
        </div>
      )}

      {/* FAB Toggle Button */}
      <button
        className={`chat-fab ${isOpen ? 'chat-fab--open' : ''}`}
        onClick={() => setIsOpen(prev => !prev)}
        title={isOpen ? 'Close chat' : 'Ask about your document'}
      >
        {isOpen ? (
          <span className="chat-fab-icon">✕</span>
        ) : (
          <>
            <span className="chat-fab-icon">💬</span>
            {unreadCount > 0 && (
              <span className="chat-fab-badge">{unreadCount}</span>
            )}
          </>
        )}
        <span className="chat-fab-pulse" />
      </button>
    </>
  );
};

export default QAChat;