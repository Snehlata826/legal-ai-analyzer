export const calculateRiskSummary = (results) => {
  return results.reduce(
    (acc, item) => {
      acc[item.risk] = (acc[item.risk] || 0) + 1;
      return acc;
    },
    { HIGH: 0, MEDIUM: 0, LOW: 0 }
  );
};
