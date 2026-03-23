import React, { useState, useCallback } from 'react';
import FileUploader   from './components/FileUploader';
import ClauseCard     from './components/ClauseCard';
import RiskSummary    from './components/RiskSummary';
import Loader         from './components/Loader';
import QAChat         from './components/QAChat';
import EvaluatePanel  from './components/EvaluatePanel';
import { uploadDocument, simplifyClauses, downloadReport } from './api';
import { calculateRiskSummary } from './utils/riskSummary';
import './index.css';

function App() {
  const [loading,        setLoading]        = useState(false);
  const [loadingMsg,     setLoadingMsg]      = useState('');
  const [loadingStep,    setLoadingStep]     = useState(0);
  const [requestId,      setRequestId]      = useState(null);
  const [results,        setResults]        = useState([]);
  const [error,          setError]          = useState(null);
  const [activeTab,      setActiveTab]      = useState('clauses');
  const [chatMessages,   setChatMessages]   = useState([]);
  const [classifierInfo, setClassifierInfo] = useState(null);

  const handleFileSelect = useCallback(async (file) => {
    setLoading(true);
    setError(null);
    setResults([]);
    setChatMessages([]);
    setClassifierInfo(null);

    try {
      setLoadingStep(1); setLoadingMsg('Extracting clauses…');
      const upload = await uploadDocument(file);
      setRequestId(upload.request_id);

      setLoadingStep(2); setLoadingMsg('Running ML classifier…');
      await new Promise(r => setTimeout(r, 150));

      setLoadingStep(3); setLoadingMsg('Simplifying with Groq AI…');
      const simplified = await simplifyClauses(upload.request_id);

      setLoadingStep(4); setLoadingMsg('Computing SHAP explanations…');
      await new Promise(r => setTimeout(r, 150));

      setLoadingStep(5); setLoadingMsg('Finalising…');
      await new Promise(r => setTimeout(r, 100));

      setResults(simplified.results);
      setClassifierInfo({
        classifier:     simplified.classifier,
        shap_available: simplified.shap_available,
      });
      setActiveTab('clauses');
    } catch (err) {
      setError(err.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDownload = useCallback(async () => {
    if (!requestId) return;
    try {
      setLoading(true);
      setLoadingMsg('Generating PDF report…');
      await downloadReport(requestId);
    } catch (err) {
      setError(err.message || 'Failed to generate report.');
    } finally {
      setLoading(false);
    }
  }, [requestId]);

  const handleReset = useCallback(() => {
    setRequestId(null);
    setResults([]);
    setError(null);
    setActiveTab('clauses');
    setChatMessages([]);
    setClassifierInfo(null);
  }, []);

  const riskSummary = results.length > 0 ? calculateRiskSummary(results) : null;
  const highCount   = riskSummary?.HIGH || 0;
  const chatCount   = chatMessages.filter(m => m.role === 'user').length;
  const isML        = classifierInfo?.classifier === 'ml_ensemble';
  const hasSHAP     = classifierInfo?.shap_available;

  return (
    <div className="app">

      {/* ── Header ── */}
      <header className="app-header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-icon">⚖</div>
            <div>
              <h1 className="brand-name">LexAnalyze</h1>
              <p className="brand-tagline">Legal Document Intelligence</p>
            </div>
          </div>
          <div className="header-pills">
            <span className="pill pill--dark">Groq LLaMA3</span>
            {results.length > 0 && isML && (
            <span className="pill pill--purple">ML Ensemble</span>
            )}
            {results.length > 0 && !isML && (
              <span className="pill pill--green">Keyword</span>
            )}
            {hasSHAP && <span className="pill pill--purple">SHAP</span>}
          </div>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="app-main">

        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠</span>
            <span className="error-text">{error}</span>
            <button className="error-close" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {loading && (
          <Loader message={loadingMsg} step={loadingStep} />
        )}

        {!loading && results.length === 0 && (
          <FileUploader onFileSelect={handleFileSelect} />
        )}

        {!loading && results.length > 0 && (
          <div className="results-wrap">

            {/* Top bar */}
            <div className="results-topbar">
              <div className="results-title-row">
                <h2 className="results-heading">Analysis complete</h2>
                <div className="results-chips">
                  <span className="chip chip--neutral">{results.length} clauses</span>
                  {highCount > 0 && (
                    <span className="chip chip--danger">
                      {highCount} high risk
                    </span>
                  )}
                  {isML && (
                    <span className="chip chip--purple">ML classifier</span>
                  )}
                </div>
              </div>
              <div className="results-actions">
                <button className="btn btn--ghost" onClick={handleReset}>
                  ↩ New document
                </button>
                <button className="btn btn--solid" onClick={handleDownload}>
                  ↓ Download report
                </button>
              </div>
            </div>

            {/* Risk summary */}
            <RiskSummary summary={riskSummary} total={results.length} />

            {/* Tab bar */}
            <div className="tab-bar">
              <button
                className={`tab-item ${activeTab === 'clauses' ? 'tab-item--active' : ''}`}
                onClick={() => setActiveTab('clauses')}
              >
                Clauses
                <span className={`tab-badge ${highCount > 0 ? 'tab-badge--red' : ''}`}>
                  {results.length}
                </span>
              </button>
              <button
                className={`tab-item ${activeTab === 'qa' ? 'tab-item--active' : ''}`}
                onClick={() => setActiveTab('qa')}
              >
                Ask questions
                {chatCount > 0 && (
                  <span className="tab-badge">{chatCount}</span>
                )}
              </button>
              <button
                className={`tab-item ${activeTab === 'evaluate' ? 'tab-item--active' : ''}`}
                onClick={() => setActiveTab('evaluate')}
              >
                Evaluate
                <span className="tab-badge tab-badge--purple">ML</span>
              </button>
            </div>

            {/* Tab panels */}
            {activeTab === 'clauses' && (
              <div className="clauses-panel">
                {results.map((result, i) => (
                  <ClauseCard key={i} clause={result} index={i} />
                ))}
              </div>
            )}

            {activeTab === 'qa' && (
              <QAChat
                requestId={requestId}
                messages={chatMessages}
                setMessages={setChatMessages}
              />
            )}

            {activeTab === 'evaluate' && (
              <EvaluatePanel
                requestId={requestId}
                hasResults={results.length > 0}
                clauseCount={results.length}
              />
            )}

          </div>
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="app-footer">
        LexAnalyze v2.0 · ML Ensemble + SHAP + Groq · For informational purposes only · Not legal advice
      </footer>
    </div>
  );
}

export default App;
