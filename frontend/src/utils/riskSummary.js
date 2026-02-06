/**
 * Calculate risk summary from results
 */
export const calculateRiskSummary = (results) => {
  const summary = {
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
  };

  results.forEach((result) => {
    if (summary[result.risk] !== undefined) {
      summary[result.risk]++;
    }
  });

  return summary;
};
