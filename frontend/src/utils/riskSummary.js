export const calculateRiskSummary = (results) => {
  const summary = { HIGH: 0, MEDIUM: 0, LOW: 0 };
  results.forEach((r) => {
    if (summary[r.risk] !== undefined) summary[r.risk]++;
  });
  return summary;
};
