import { useState } from "react";
import { uploadFile, simplifyDoc } from "./api";

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

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

      {/* File input (single action) */}
      <input
        type="file"
        accept=".pdf"
        onChange={(e) => handleFileSelect(e.target.files[0])}
      />

      {/* Status */}
      {status && (
        <p style={{ marginTop: "12px", fontWeight: "500" }}>
          {status}
        </p>
      )}

      {loading && <p>⏳ Please wait...</p>}

      {/* Results */}
            {results.map((item) => (
              <div key={item.clause_no} className="clause-card">
                <div className="clause-title">Clause {item.clause_no}</div>
      
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
