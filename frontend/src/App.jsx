import React, { useState } from 'react';
import FileUploader from './components/FileUploader';
import ClauseCard from './components/ClauseCard';
import RiskSummary from './components/RiskSummary';
import Loader from './components/Loader';
import { uploadDocument, simplifyClauses, downloadReport } from './api';
import { calculateRiskSummary } from './utils/riskSummary';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [requestId, setRequestId] = useState(null);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const handleFileSelect = async (file) => {
    setIsLoading(true);
    setLoadingMessage('Uploading and extracting clauses...');
    setError(null);
    setResults([]);

    try {
      // Step 1: Upload document
      const uploadResponse = await uploadDocument(file);
      setRequestId(uploadResponse.request_id);

      // Step 2: Simplify clauses
      setLoadingMessage('Analyzing and simplifying clauses...');
      const simplifyResponse = await simplifyClauses(uploadResponse.request_id);
      
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
      setLoadingMessage('Generating PDF report...');
      setIsLoading(true);
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
  };

  const riskSummary = results.length > 0 ? calculateRiskSummary(results) : null;

  return (
    <div className="app">
      <header className="app-header">
        <h1>⚖️ Legal AI Analyzer</h1>
        <p className="subtitle">Simplify legal documents and analyze risk levels</p>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
            <button className="error-dismiss" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {isLoading && <Loader message={loadingMessage} />}

        {!isLoading && results.length === 0 && (
          <FileUploader onFileSelect={handleFileSelect} isLoading={isLoading} />
        )}

        {!isLoading && results.length > 0 && (
          <>
            <div className="results-header">
              <h2>Analysis Complete</h2>
              <div className="action-buttons">
                <button className="btn btn-primary" onClick={handleDownloadReport}>
                  📥 Download PDF Report
                </button>
                <button className="btn btn-secondary" onClick={handleReset}>
                  🔄 Analyze Another Document
                </button>
              </div>
            </div>

            <RiskSummary summary={riskSummary} />

            <div className="clauses-container">
              <h3>Detailed Clause Analysis ({results.length} clauses)</h3>
              {results.map((result, index) => (
                <ClauseCard key={index} clause={result} index={index} />
              ))}
            </div>
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>Legal AI Analyzer v1.0 • For informational purposes only • Not legal advice</p>
      </footer>
    </div>
  );
}

export default App;
