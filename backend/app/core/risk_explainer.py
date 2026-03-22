"""
Risk explanation generator with word-level attribution.
"""
from typing import Dict, List
from .risk_analyzer import RiskLevel, get_risk_keywords_found

RISK_EXPLANATIONS: Dict[str, str] = {
    "HIGH": (
        "This clause contains high-risk terms that could significantly "
        "impact your legal rights, financial obligations, or ability to "
        "seek compensation. Review carefully or consult a lawyer."
    ),
    "MEDIUM": (
        "This clause involves procedural or administrative matters "
        "that affect how disputes, changes, or obligations are handled. "
        "Understanding these terms is important before signing."
    ),
    "LOW": (
        "This is a standard administrative or interpretive clause "
        "with minimal risk. These are common in most agreements "
        "and rarely cause issues."
    ),
}


def get_risk_explanation(risk_level: RiskLevel) -> str:
    return RISK_EXPLANATIONS.get(risk_level, RISK_EXPLANATIONS["LOW"])


def get_word_attributions(clause: str) -> List[Dict]:
    return get_risk_keywords_found(clause)
