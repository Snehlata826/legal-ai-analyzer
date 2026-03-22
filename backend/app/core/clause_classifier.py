"""
Clause classifier — maps extracted clauses to legal categories.
"""
from typing import Dict, List

CLAUSE_KEYWORDS = {
    "Confidentiality": ["confidential", "non-disclosure", "privacy", "secret"],
    "Termination":     ["terminate", "termination", "end of agreement", "cancel"],
    "Payment":         ["payment", "fees", "compensation", "invoice"],
    "Indemnity":       ["indemnify", "hold harmless", "liability"],
    "Governing Law":   ["governing law", "jurisdiction", "disputes", "law of"],
}


def classify_clauses(clauses: List[str]) -> Dict[str, str]:
    classified = {}
    for clause in clauses:
        for clause_name, keywords in CLAUSE_KEYWORDS.items():
            if any(kw.lower() in clause.lower() for kw in keywords):
                classified[clause_name] = clause
                break
    return classified
