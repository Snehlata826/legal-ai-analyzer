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
        {[
          { key: 'HIGH',   label: 'High Risk',   cls: 'high' },
          { key: 'MEDIUM', label: 'Medium Risk',  cls: 'medium' },
          { key: 'LOW',    label: 'Low Risk',     cls: 'low' },
        ].map(({ key, label, cls }, i) => (
          <React.Fragment key={key}>
            {i > 0 && <div className="risk-divider" />}
            <div className="risk-stat-item">
              <div className={`risk-stat-dot risk-stat-dot--${cls}`} />
              <div>
                <p className="risk-stat-label">{label}</p>
                <p className="risk-stat-value">{summary[key]}</p>
              </div>
              <p className="risk-stat-pct">{pct(summary[key])}%</p>
            </div>
          </React.Fragment>
        ))}
      </div>
      <div className="risk-bar-track">
        {summary.HIGH   > 0 && <div className="risk-bar-fill risk-bar-fill--high"   style={{ width: `${pct(summary.HIGH)}%` }} />}
        {summary.MEDIUM > 0 && <div className="risk-bar-fill risk-bar-fill--medium" style={{ width: `${pct(summary.MEDIUM)}%` }} />}
        {summary.LOW    > 0 && <div className="risk-bar-fill risk-bar-fill--low"    style={{ width: `${pct(summary.LOW)}%` }} />}
      </div>
    </div>
  );
};

export default RiskSummary;
