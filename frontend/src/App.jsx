import { useState } from "react";
import { uploadFile, simplifyDoc } from "./api";
import "./index.css"; // ✅ CSS imported

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  // Map risk → CSS class
  const getRiskClass = (risk) => {
    if (risk === "HIGH") return "risk-high";
    if (risk === "MEDIUM") return "risk-medium";
    return "risk-low";
  };

  const handleFileSelect = async (file) => {
    if (!file) return;

    try {
      setLoading(true);
      setStatus("Uploading and processing document...");

      // Upload + process
      const uploadRes = await uploadFile(file);
      const requestId = uploadRes.data.request_id;

      setStatus("Simplifying clauses...");

      // Simplify
      const simplifyRes = await simplifyDoc(requestId);
      setResults(simplifyRes.data.results);

      setStatus(`✅ Processed: ${file.name}`);
    } catch (err) {
      console.error(err);
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

      {/* File input */}
      <input
        type="file"
        accept=".pdf"
        onChange={(e) => handleFileSelect(e.target.files[0])}
      />

      {/* Status */}
      {status && <p className="status-text">{status}</p>}
      {loading && <p>⏳ Please wait...</p>}

      {/* Results */}
      {results.map((item) => (
        <div key={item.clause_no} className="clause-card">
          <div className="clause-header">
            <div className="clause-title">
              Clause {item.clause_no}
            </div>

            <span className={`risk-badge ${getRiskClass(item.risk)}`}>
              {item.risk} RISK
            </span>
          </div>

          <p className="original">
            <b>Original:</b> {item.original}
          </p>

          <p className="simplified">
            <b>Simplified:</b> {item.simplified}
          </p>
        </div>
      ))}
    </div>
  );
}

export default App;
