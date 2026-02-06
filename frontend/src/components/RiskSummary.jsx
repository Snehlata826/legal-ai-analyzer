import React from 'react';

const RiskSummary = ({ summary }) => {
  const total = summary.HIGH + summary.MEDIUM + summary.LOW;

  const getPercentage = (count) => {
    return total > 0 ? ((count / total) * 100).toFixed(1) : 0;
  };

  return (
    <div className="risk-summary">
      <h3>Risk Summary</h3>
      <div className="risk-stats">
        <div className="risk-stat">
          <span className="risk-badge high">HIGH</span>
          <span className="risk-count">{summary.HIGH}</span>
          <span className="risk-percentage">({getPercentage(summary.HIGH)}%)</span>
        </div>
        <div className="risk-stat">
          <span className="risk-badge medium">MEDIUM</span>
          <span className="risk-count">{summary.MEDIUM}</span>
          <span className="risk-percentage">({getPercentage(summary.MEDIUM)}%)</span>
        </div>
        <div className="risk-stat">
          <span className="risk-badge low">LOW</span>
          <span className="risk-count">{summary.LOW}</span>
          <span className="risk-percentage">({getPercentage(summary.LOW)}%)</span>
        </div>
      </div>
      <div className="risk-bar">
        <div
          className="risk-bar-segment high"
          style={{ width: `${getPercentage(summary.HIGH)}%` }}
        ></div>
        <div
          className="risk-bar-segment medium"
          style={{ width: `${getPercentage(summary.MEDIUM)}%` }}
        ></div>
        <div
          className="risk-bar-segment low"
          style={{ width: `${getPercentage(summary.LOW)}%` }}
        ></div>
      </div>
    </div>
  );
};

export default RiskSummary;
