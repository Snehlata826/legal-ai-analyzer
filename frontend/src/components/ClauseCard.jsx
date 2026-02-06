import React, { useState } from 'react';

const ClauseCard = ({ clause, index }) => {
  const [expanded, setExpanded] = useState(false);

  const toggleExpand = () => {
    setExpanded(!expanded);
  };

  return (
    <div className="clause-card">
      <div className="clause-header">
        <div className="clause-title">
          <span className="clause-number">Clause {index + 1}</span>
          <span className={`risk-badge ${clause.risk.toLowerCase()}`}>
            {clause.risk}
          </span>
        </div>
      </div>

      <div className="clause-content">
        <div className="clause-section">
          <h4>Simplified Explanation</h4>
          <p className="simplified-text">{clause.simplified}</p>
        </div>

        <button className="expand-button" onClick={toggleExpand}>
          {expanded ? '▼ Hide Details' : '▶ Show Original & Risk Explanation'}
        </button>

        {expanded && (
          <>
            <div className="clause-section">
              <h4>Original Clause</h4>
              <p className="original-text">{clause.original}</p>
            </div>

            <div className="clause-section">
              <h4>Risk Explanation</h4>
              <p className="explanation-text">{clause.explanation}</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ClauseCard;
