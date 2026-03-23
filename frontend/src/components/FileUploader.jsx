import React, { useRef, useState, useCallback } from 'react';

const FEATURES = [
  {
    icon: '⚖',
    title: 'ML risk classification',
    desc: 'Logistic Regression + Random Forest ensemble with confidence scores',
  },
  {
    icon: '✦',
    title: 'Plain-English summaries',
    desc: 'Every clause rewritten in simple language by Groq LLaMA3',
  },
  {
    icon: '◎',
    title: 'Q&A chat',
    desc: 'Ask anything about the document — grounded RAG answers',
  },
];

function FileUploader({ onFileSelect }) {
  const inputRef  = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError]       = useState('');

  const handleFile = useCallback((file) => {
    if (!file) return;
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are supported.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File exceeds the 10 MB limit.');
      return;
    }
    setError('');
    onFileSelect(file);
  }, [onFileSelect]);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  }, [handleFile]);

  return (
    <div className="upload-page">

      {/* Left info panel */}
      <div className="upload-info">
        <p className="upload-info-eyebrow">AI-powered · ML classifier · Groq LLaMa3</p>
        <h2 className="upload-info-heading">
          Understand your<br />
          <em>legal documents</em>
        </h2>
        <p className="upload-info-body">
          Upload any legal PDF and get instant risk analysis, plain-English
          summaries, and answers to your questions — powered by a trained
          ML ensemble and Groq LLaMA3.
        </p>

        <div className="upload-features-list">
          {FEATURES.map(({ icon, title, desc }) => (
            <div className="feature-row" key={title}>
              <div className="feature-icon-wrap">{icon}</div>
              <div>
                <p className="feature-title">{title}</p>
                <p className="feature-desc">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right upload zone */}
      <div className="upload-zone-wrap">
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={e => handleFile(e.target.files[0])}
        />

        <div
          className={`upload-zone${dragging ? ' upload-zone--drag' : ''}`}
          onClick={() => inputRef.current?.click()}
          onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          role="button"
          tabIndex={0}
          onKeyDown={e => e.key === 'Enter' && inputRef.current?.click()}
          aria-label="Upload PDF"
        >
          <div className="upload-icon-wrap">
            {dragging ? '📂' : '📄'}
          </div>
          <p className="upload-zone-heading">
            {dragging ? 'Drop to upload' : 'Upload your document'}
          </p>
          <p className="upload-zone-sub">
            Drag & drop or click to browse
          </p>
          <p className="upload-zone-hint">PDF only · Max 10 MB</p>
          {error && (
            <p style={{ color: 'var(--red)', fontSize: '.8rem', marginBottom: 12 }}>
              {error}
            </p>
          )}
          <button className="upload-btn" tabIndex={-1}>
            Choose PDF file
          </button>
        </div>

        <p className="upload-disclaimer">
          <span>🔒</span>
          Processed in your session only · Never stored permanently
        </p>
      </div>
    </div>
  );
}

export default FileUploader;
