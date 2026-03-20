import React, { useState } from 'react';

const RISK_CONFIG = {
  HIGH:   { color: '#c0392b', bg: '#fdf2f2', border: '#e8c4c4', label: 'High Risk' },
  MEDIUM: { color: '#b7770d', bg: '#fdf8ee', border: '#e8d8a0', label: 'Medium Risk' },
  LOW:    { color: '#1a7a4a', bg: '#f2faf5', border: '#a8d8bc', label: 'Low Risk' },
};

const ClauseCard = ({ clause, index }) => {
  const [expanded, setExpanded] = useState(false);
  const cfg = RISK_CONFIG[clause.risk] || RISK_CONFIG.LOW;

  return (
    <div className="clause-card" style={{ borderLeftColor: cfg.color }}>

      {/* Card header */}
      <div className="clause-card-header">
        <div className="clause-card-meta">
          <span className="clause-num">#{index + 1}</span>
          <span
            className="risk-tag"
            style={{
              color: cfg.color,
              background: cfg.bg,
              border: `1px solid ${cfg.border}`
            }}
          >
            {cfg.label}
          </span>
        </div>

        {/* Attribution keywords */}
        {clause.attributions && clause.attributions.length > 0 && (
          <div className="clause-keywords">
            {clause.attributions.slice(0, 3).map((attr, i) => (
              <span
                key={i}
                className="keyword-tag"
                style={{
                  color: attr.risk_level === 'HIGH' ? '#c0392b' : '#b7770d',
                  background: attr.risk_level === 'HIGH' ? '#fdf2f2' : '#fdf8ee',
                }}
                title={attr.reason}
              >
                {attr.word}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Simplified text — always visible */}
      <div className="clause-simplified">
        <p className="simplified-label">Plain English</p>
        <p className="simplified-body">{clause.simplified}</p>
      </div>

      {/* Expand toggle */}
      <button
        className="clause-expand-btn"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? '▲ Hide details' : '▼ Show original & explanation'}
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="clause-details">

          <div className="detail-block">
            <p className="detail-label">Original Text</p>
            <p className="detail-body detail-body--original">{clause.original}</p>
          </div>

          <div className="detail-block">
            <p className="detail-label">Why This Risk Level</p>
            <p className="detail-body">{clause.explanation}</p>
          </div>

          {clause.attributions && clause.attributions.length > 0 && (
            <div className="detail-block">
              <p className="detail-label">Risk Keywords Found</p>
              <ul className="attribution-list">
                {clause.attributions.map((attr, i) => (
                  <li key={i} className="attribution-item">
                    <span
                      className="attribution-word"
                      style={{ color: attr.risk_level === 'HIGH' ? '#c0392b' : '#b7770d' }}
                    >
                      "{attr.word}"
                    </span>
                    <span className="attribution-reason"> — {attr.reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {clause.entities && clause.entities.length > 0 && (
            <div className="detail-block">
              <p className="detail-label">Identified Entities</p>
              <div className="entity-row">
                {clause.entities.map((ent, i) => (
                  <span key={i} className="entity-pill" title={ent.description}>
                    {ent.text}
                    <span className="entity-type-label">{ent.type}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  );
};

export default ClauseCard;
