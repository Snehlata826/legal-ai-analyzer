import React, { useState } from 'react';
import FileUploader from './components/FileUploader';
import ClauseCard from './components/ClauseCard';
import RiskSummary from './components/RiskSummary';
import Loader from './components/Loader';
import QAChat from './components/QAChat';
import { uploadDocument, simplifyClauses, downloadReport } from './api';
import { calculateRiskSummary } from './utils/riskSummary';
import './index.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [loadingStep, setLoadingStep] = useState(0);
  const [requestId, setRequestId] = useState(null);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);

  const handleFileSelect = async (file) => {
    setIsLoading(true);
    setLoadingStep(1);
    setLoadingMessage('Reading your document...');
    setError(null);
    setResults([]);
    setChatMessages([]);

    try {
      setLoadingStep(1);
      setLoadingMessage('Extracting clauses...');
      const uploadResponse = await uploadDocument(file);
      setRequestId(uploadResponse.request_id);

      setLoadingStep(2);
      setLoadingMessage('Analysing risk levels...');
      await new Promise(r => setTimeout(r, 300));

      setLoadingStep(3);
      setLoadingMessage('Simplifying with Groq AI...');
      const simplifyResponse = await simplifyClauses(uploadResponse.request_id);

      setLoadingStep(4);
      setLoadingMessage('Finalising...');
      await new Promise(r => setTimeout(r, 200));

      setResults(simplifyResponse.results);
      setIsLoading(false);
    } catch (err) {
      setError(err.message || 'An error occurred');
      setIsLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!requestId) return;
    try {
      setIsLoading(true);
      setLoadingMessage('Generating PDF report...');
      await downloadReport(requestId);
      setIsLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to download report');
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setRequestId(null);
    setResults([]);
    setError(null);
    setChatMessages([]);
  };

  const riskSummary = results.length > 0 ? calculateRiskSummary(results) : null;
  const highCount = riskSummary?.HIGH || 0;

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <div className="brand">
            <span className="brand-icon">⚖</span>
            <div className="brand-text">
              <h1 className="brand-name">LexAnalyze</h1>
              <p className="brand-tagline">Legal Document Intelligence</p>
            </div>
          </div>
          <div className="header-pills">
            <span className="pill pill--dark">Groq LLaMA3</span>
            <span className="pill pill--green">Free</span>
          </div>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠</span>
            <span className="error-text">{error}</span>
            <button className="error-close" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {isLoading && (
          <Loader message={loadingMessage} step={loadingStep} />
        )}

        {!isLoading && results.length === 0 && (
          <FileUploader onFileSelect={handleFileSelect} />
        )}

        {!isLoading && results.length > 0 && (
          <div className="results-wrap">

            {/* Top bar */}
            <div className="results-topbar">
              <div className="results-title-row">
                <h2 className="results-heading">Analysis Complete</h2>
                <div className="results-chips">
                  <span className="chip chip--neutral">{results.length} clauses</span>
                  {highCount > 0 && (
                    <span className="chip chip--danger">
                      ⚠ {highCount} high risk
                    </span>
                  )}
                </div>
              </div>
              <div className="results-actions">
                <button className="btn btn--ghost" onClick={handleReset}>
                  ↩ New Document
                </button>
                <button className="btn btn--solid" onClick={handleDownloadReport}>
                  ↓ Download Report
                </button>
              </div>
            </div>

            {/* Risk summary */}
            <RiskSummary summary={riskSummary} total={results.length} />

            {/* Clauses list */}
            <div className="clauses-panel">
              {results.map((result, index) => (
                <ClauseCard key={index} clause={result} index={index} />
              ))}
            </div>

          </div>
        )}
      </main>

      <footer className="app-footer">
        LexAnalyze v2.0 · For informational purposes only · Not legal advice
      </footer>

      {/* Floating chatbot — only when document is loaded */}
      {requestId && (
        <QAChat
          requestId={requestId}
          messages={chatMessages}
          setMessages={setChatMessages}
        />
      )}
    </div>
  );
}

export default App;