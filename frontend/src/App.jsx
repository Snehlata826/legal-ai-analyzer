import { useState } from "react";
import { uploadFile, simplifyDoc } from "./api";

import FileUploader from "./components/FileUploader";
import ClauseCard from "./components/ClauseCard";
import Loader from "./components/Loader";
import RiskSummary from "./components/RiskSummary";

import { calculateRiskSummary } from "./utils/riskSummary";

import "./index.css";

function App() {
  const [results, setResults] = useState([]);
  const [riskSummary, setRiskSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  const handleFileSelect = async (file) => {
    if (!file) return;

    try {
      setLoading(true);
      setStatus("Uploading and processing document...");

      // Upload + extract
      const uploadRes = await uploadFile(file);
      const requestId = uploadRes.data.request_id;

      setStatus("Simplifying and analyzing clauses...");

      // Simplify + risk
      const simplifyRes = await simplifyDoc(requestId);
      const resultsData = simplifyRes.data.results;

      setResults(resultsData);
      setRiskSummary(calculateRiskSummary(resultsData));

      setStatus(`✅ Processed: ${file.name}`);
    } catch (error) {
      console.error(error);
      setStatus("❌ Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="app-title">
        ⚖️ <span>Legal AI Analyzer</span>
      </div>

      <FileUploader onFileSelect={handleFileSelect} />

      {status && <p className="status-text">{status}</p>}
      {loading && <Loader />}

      {/* Risk Summary */}
      {riskSummary && <RiskSummary summary={riskSummary} />}

      {/* Clause Results */}
      {results.map((item) => (
        <ClauseCard key={item.clause_no} item={item} />
      ))}
    </div>
  );
}

export default App;
