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

// messages and setMessages come from App — so chat survives tab switching
const QAChat = ({ requestId, messages, setMessages }) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef(null);

  // Show welcome only once
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([WELCOME]);
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

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

  const renderAnswerText = (text) => {
    return text.split('\n').map((line, i) => {
      // Bold **text**
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
    <div className="chat-wrap">

      {/* Chat header with clear button */}
      <div className="chat-header">
        <div className="chat-header-left">
          <span className="chat-header-icon">💬</span>
          <div>
            <p className="chat-header-title">Document Q&A</p>
            <p className="chat-header-sub">RAG Pipeline · Groq LLaMA3</p>
          </div>
        </div>
        <button
          className="chat-clear-btn"
          onClick={handleClearChat}
          title="Clear chat history"
        >
          Clear Chat
        </button>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`msg-row msg-row--${msg.role}`}>

            {msg.role === 'assistant' && (
              <div className={`msg-bubble msg-bubble--ai ${msg.isError ? 'msg-bubble--error' : ''}`}>
                <div className="msg-avatar">AI</div>
                <div className="msg-body">
                  <div className="msg-text">
                    {renderAnswerText(msg.text)}
                  </div>

                  {/* Suggestion chips on welcome */}
                  {msg.suggestions && (
                    <div className="suggestion-chips">
                      {msg.suggestions.map((s, j) => (
                        <button
                          key={j}
                          className="suggestion-chip"
                          onClick={() => sendMessage(s)}
                          disabled={isLoading}
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Sources collapsible */}
                  {msg.sources && msg.sources.length > 0 && (
                    <details className="msg-sources">
                      <summary className="sources-toggle">
                        View source clauses ({msg.sources.length})
                      </summary>
                      <div className="sources-body">
                        {msg.sources.map((src, j) => (
                          <div key={j} className="source-clause">
                            <span className="source-num">§{j + 1}</span>
                            <p className="source-text">"{src.clause}"</p>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              </div>
            )}

            {msg.role === 'user' && (
              <div className="msg-bubble msg-bubble--user">
                <p className="msg-text">{msg.text}</p>
              </div>
            )}

          </div>
        ))}

        {isLoading && (
          <div className="msg-row msg-row--assistant">
            <div className="msg-bubble msg-bubble--ai">
              <div className="msg-avatar">AI</div>
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="chat-input-area">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask anything about your document..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          className="chat-send"
          onClick={() => sendMessage(input)}
          disabled={isLoading || !input.trim()}
        >
          Send
        </button>
      </div>

    </div>
  );
};

export default QAChat;
