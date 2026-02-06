"""
Risk explanation generator
"""
from typing import Dict
from .risk_analyzer import RiskLevel


RISK_EXPLANATIONS: Dict[RiskLevel, str] = {
    "HIGH": "This clause contains terms that could significantly impact your rights, obligations, or financial liability. Review carefully or consult legal counsel.",
    "MEDIUM": "This clause involves procedural or administrative matters that may affect how disputes or changes are handled. Understanding these terms is important.",
    "LOW": "This is a standard administrative or interpretive clause with minimal risk impact. These are common in most agreements."
}


def get_risk_explanation(risk_level: RiskLevel) -> str:
    """Get human-readable explanation for risk level"""
    return RISK_EXPLANATIONS.get(risk_level, RISK_EXPLANATIONS["LOW"])
