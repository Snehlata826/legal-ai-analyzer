export const getRiskClass = (risk) => {
  if (risk === "HIGH") return "risk-high";
  if (risk === "MEDIUM") return "risk-medium";
  return "risk-low";
};
