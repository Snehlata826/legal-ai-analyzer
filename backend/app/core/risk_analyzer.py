"""
Risk analysis logic for legal clauses
"""
import re
from typing import Literal

RiskLevel = Literal["HIGH", "MEDIUM", "LOW"]


# Risk keyword patterns
HIGH_RISK_KEYWORDS = [
    "indemnif", "liability", "liable", "termination", "terminate",
    "penalty", "penalties", "breach", "damages", "default",
    "forfeiture", "waive", "waiver", "exclude", "exclusion",
    "disclaim", "disclaimer", "non-refundable", "irreversible"
]

MEDIUM_RISK_KEYWORDS = [
    "arbitration", "dispute", "jurisdiction", "governing law",
    "force majeure", "confidential", "proprietary", "intellectual property",
    "amendment", "modify", "modification", "notice", "consent",
    "assignment", "subcontract", "audit", "inspection"
]

LOW_RISK_KEYWORDS = [
    "general", "standard", "usual", "ordinary", "routine",
    "interpretation", "severability", "headings", "entire agreement",
    "counterparts", "whereas", "recital"
]


def analyze_risk(clause: str) -> RiskLevel:
    """
    Analyze risk level of a clause based on keyword matching.
    
    Returns:
        "HIGH", "MEDIUM", or "LOW"
    """
    clause_lower = clause.lower()
    
    # Check for HIGH risk keywords
    for keyword in HIGH_RISK_KEYWORDS:
        if re.search(r'\b' + keyword, clause_lower):
            return "HIGH"
    
    # Check for MEDIUM risk keywords
    for keyword in MEDIUM_RISK_KEYWORDS:
        if re.search(r'\b' + keyword, clause_lower):
            return "MEDIUM"
    
    # Default to LOW risk
    return "LOW"
