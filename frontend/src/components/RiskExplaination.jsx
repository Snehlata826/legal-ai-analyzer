function RiskExplanation({ reasons }) {
  if (!reasons || reasons.length === 0) return null;

  return (
    <div className="risk-explanation">
      <b>Why this is risky:</b>
      <ul>
        {reasons.map((reason, idx) => (
          <li key={idx}>{reason}</li>
        ))}
      </ul>
    </div>
  );
}

export default RiskExplanation;
