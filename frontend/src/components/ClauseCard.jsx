import { getRiskClass } from "../utils/riskUtils";

function ClauseCard({ item }) {
  return (
    <div className="clause-card">
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
  );
}

export default ClauseCard;
