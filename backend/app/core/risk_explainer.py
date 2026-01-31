RISK_EXPLANATIONS = {
    "indemnify": "You may have to pay for losses caused to the other party.",
    "terminate": "The agreement can be ended suddenly, which may harm you.",
    "breach": "Breaking this clause can lead to legal action.",
    "liability": "You could be legally responsible for damages.",
    "penalty": "Financial punishment may apply.",
    "arbitration": "You may not be able to go to court directly.",
    "jurisdiction": "Legal cases can only be filed in a specific location.",
    "force majeure": "Uncontrollable events can excuse obligations.",
}

def explain_risk(clause: str):
    clause_lower = clause.lower()
    reasons = []

    for keyword, explanation in RISK_EXPLANATIONS.items():
        if keyword in clause_lower:
            reasons.append(explanation)

    return reasons
