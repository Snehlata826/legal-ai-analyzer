"""
Risk analysis for legal clauses.
Uses keyword matching (fast, no API cost).
ML model training script provided separately.
"""
import re
from typing import Literal, List, Dict

RiskLevel = Literal["HIGH", "MEDIUM", "LOW"]

# HIGH risk keywords — serious financial/legal impact
HIGH_RISK_KEYWORDS = [
    "indemnif", "liability", "liable",
    "termination", "terminate",
    "penalty", "penalties",
    "breach", "damages", "default",
    "forfeiture", "waive", "waiver",
    "exclude", "exclusion",
    "disclaim", "disclaimer",
    "non-refundable", "irreversible",
    "unlimited liability", "sole responsibility"
]

# MEDIUM risk keywords — procedural impact
MEDIUM_RISK_KEYWORDS = [
    "arbitration", "dispute", "jurisdiction",
    "governing law", "force majeure",
    "confidential", "proprietary",
    "intellectual property",
    "amendment", "modify", "modification",
    "notice", "consent", "assignment",
    "subcontract", "audit", "inspection"
]

# Word-level explanations for explainability feature
KEYWORD_REASONS: Dict[str, str] = {
    "indemnif": "Creates financial compensation obligation",
    "liability": "Assigns legal responsibility for losses",
    "liable": "Assigns legal responsibility",
    "termination": "Allows the contract to be ended",
    "terminate": "Allows the contract to be ended",
    "breach": "Defines violation consequences",
    "damages": "Specifies financial penalties",
    "waive": "Causes loss of legal rights",
    "waiver": "Causes loss of legal rights",
    "disclaim": "Removes party's responsibility",
    "disclaimer": "Removes party's responsibility",
    "penalty": "Imposes financial punishment",
    "forfeiture": "Results in loss of deposit or rights",
    "non-refundable": "Money cannot be recovered",
    "arbitration": "Dispute handled outside court",
    "jurisdiction": "Determines which court applies",
    "confidential": "Restricts information sharing",
    "force majeure": "Excuses performance on external events",
    "amendment": "Contract can be changed",
    "assignment": "Rights can be transferred to others",
    "audit": "Allows inspection of records",
    "intellectual property": "Affects ownership of created work",
}


def analyze_risk(clause: str) -> RiskLevel:
    """
    Analyze risk level using keyword matching.
    Returns HIGH, MEDIUM, or LOW.
    """
    clause_lower = clause.lower()

    for keyword in HIGH_RISK_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword), clause_lower):
            return "HIGH"

    for keyword in MEDIUM_RISK_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword), clause_lower):
            return "MEDIUM"

    return "LOW"


def get_risk_keywords_found(clause: str) -> List[Dict]:
    """
    Returns which risk keywords were found in clause.
    Used for word-level explainability feature.

    Returns list of:
    {word, risk_level, reason, weight}
    """
    clause_lower = clause.lower()
    found = []

    for keyword in HIGH_RISK_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword), clause_lower):
            found.append({
                "word": keyword,
                "risk_level": "HIGH",
                "reason": KEYWORD_REASONS.get(
                    keyword, "High risk legal term"
                ),
                "weight": 0.9
            })

    for keyword in MEDIUM_RISK_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword), clause_lower):
            found.append({
                "word": keyword,
                "risk_level": "MEDIUM",
                "reason": KEYWORD_REASONS.get(
                    keyword, "Medium risk legal term"
                ),
                "weight": 0.5
            })

    # Sort by weight, return top 5
    found.sort(key=lambda x: x["weight"], reverse=True)
    return found[:5]
