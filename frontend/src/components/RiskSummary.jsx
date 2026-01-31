function RiskSummary({ summary }) {
  if (!summary) return null;

  return (
    <div className="risk-summary">
      <span className="risk-chip high">🔴 High Risk: {summary.HIGH}</span>
      <span className="risk-chip medium">🟡 Medium Risk: {summary.MEDIUM}</span>
      <span className="risk-chip low">🟢 Low Risk: {summary.LOW}</span>
    </div>
  );
}

export default RiskSummary;
