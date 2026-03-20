import React, { useRef, useState } from 'react';

const FileUploader = ({ onFileSelect }) => {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = (file) => {
    if (!file) return;
    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file.');
      return;
    }
    onFileSelect(file);
  };

  const handleChange = (e) => handleFile(e.target.files[0]);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="upload-page">

      {/* Left — info panel */}
      <div className="upload-info">
        <p className="upload-info-eyebrow">AI-Powered</p>
        <h2 className="upload-info-heading">
          Understand your<br />legal documents
        </h2>
        <p className="upload-info-body">
          Upload any legal PDF and get plain-English summaries,
          risk analysis, and instant answers to your questions —
          all powered by Groq's free LLaMA3 API.
        </p>

        <div className="upload-features-list">
          <div className="feature-row">
            <span className="feature-icon">📋</span>
            <div>
              <p className="feature-title">Clause Extraction</p>
              <p className="feature-desc">Automatically identifies every clause</p>
            </div>
          </div>
          <div className="feature-row">
            <span className="feature-icon">⚠</span>
            <div>
              <p className="feature-title">Risk Analysis</p>
              <p className="feature-desc">HIGH / MEDIUM / LOW with explanation</p>
            </div>
          </div>
          <div className="feature-row">
            <span className="feature-icon">💬</span>
            <div>
              <p className="feature-title">Q&A Chat</p>
              <p className="feature-desc">Ask anything, get grounded answers</p>
            </div>
          </div>
          <div className="feature-row">
            <span className="feature-icon">↓</span>
            <div>
              <p className="feature-title">PDF Report</p>
              <p className="feature-desc">Download full analysis as PDF</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right — upload zone */}
      <div className="upload-zone-wrap">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleChange}
          accept=".pdf"
          style={{ display: 'none' }}
        />

        <div
          className={`upload-zone ${isDragging ? 'upload-zone--drag' : ''}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          <div className="upload-zone-icon">
            {isDragging ? '📂' : '📄'}
          </div>
          <p className="upload-zone-heading">
            {isDragging ? 'Drop to upload' : 'Upload your document'}
          </p>
          <p className="upload-zone-sub">
            Click to browse or drag & drop
          </p>
          <p className="upload-zone-hint">PDF files only · Max 10MB</p>

          <button className="upload-btn" tabIndex={-1}>
            Choose PDF File
          </button>
        </div>

        <p className="upload-disclaimer">
          🔒 Your document is processed locally and never stored permanently.
        </p>
      </div>

    </div>
  );
};

export default FileUploader;
