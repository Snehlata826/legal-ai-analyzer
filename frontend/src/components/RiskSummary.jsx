import React from 'react';

const RiskSummary = ({ summary, total }) => {
  const pct = (n) => total > 0 ? ((n / total) * 100).toFixed(0) : 0;

  return (
    <div className="risk-summary-card">
      <div className="risk-summary-header">
        <p className="risk-summary-title">Risk Overview</p>
        <p className="risk-summary-total">{total} clauses analysed</p>
      </div>

      <div className="risk-summary-stats">
        <div className="risk-stat-item">
          <div className="risk-stat-dot risk-stat-dot--high" />
          <div className="risk-stat-info">
            <p className="risk-stat-label">High Risk</p>
            <p className="risk-stat-value">{summary.HIGH}</p>
          </div>
          <p className="risk-stat-pct">{pct(summary.HIGH)}%</p>
        </div>

        <div className="risk-divider" />

        <div className="risk-stat-item">
          <div className="risk-stat-dot risk-stat-dot--medium" />
          <div className="risk-stat-info">
            <p className="risk-stat-label">Medium Risk</p>
            <p className="risk-stat-value">{summary.MEDIUM}</p>
          </div>
          <p className="risk-stat-pct">{pct(summary.MEDIUM)}%</p>
        </div>

        <div className="risk-divider" />

        <div className="risk-stat-item">
          <div className="risk-stat-dot risk-stat-dot--low" />
          <div className="risk-stat-info">
            <p className="risk-stat-label">Low Risk</p>
            <p className="risk-stat-value">{summary.LOW}</p>
          </div>
          <p className="risk-stat-pct">{pct(summary.LOW)}%</p>
        </div>
      </div>

      {/* Segmented bar */}
      <div className="risk-bar-track">
        {summary.HIGH > 0 && (
          <div
            className="risk-bar-fill risk-bar-fill--high"
            style={{ width: `${pct(summary.HIGH)}%` }}
            title={`High: ${summary.HIGH}`}
          />
        )}
        {summary.MEDIUM > 0 && (
          <div
            className="risk-bar-fill risk-bar-fill--medium"
            style={{ width: `${pct(summary.MEDIUM)}%` }}
            title={`Medium: ${summary.MEDIUM}`}
          />
        )}
        {summary.LOW > 0 && (
          <div
            className="risk-bar-fill risk-bar-fill--low"
            style={{ width: `${pct(summary.LOW)}%` }}
            title={`Low: ${summary.LOW}`}
          />
        )}
      </div>
    </div>
  );
};

export default RiskSummary;
