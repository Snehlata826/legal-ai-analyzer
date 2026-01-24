import re
from typing import Dict

CLAUSE_KEYWORDS = {
    "Confidentiality": ["confidential", "non-disclosure", "privacy", "secret"],
    "Termination": ["terminate", "termination", "end of agreement", "cancel"],
    "Payment": ["payment", "fees", "compensation", "invoice"],
    "Indemnity": ["indemnify", "hold harmless", "liability"],
    "Governing Law": ["governing law", "jurisdiction", "disputes", "law of"],
}

def extract_clauses(text: str) -> Dict[str, str]:
    clauses = {}
    sections = re.split(r"\n+|\r+", text)

    for clause_name, keywords in CLAUSE_KEYWORDS.items():
        for section in sections:
            if any(keyword.lower() in section.lower() for keyword in keywords):
                clauses[clause_name] = section.strip()
                break
    
    return clauses
