def analyze_risk(clause: str) -> str:
    """
    Rule-based legal risk analyzer using weighted scoring.
    Simulates model-like behavior without ML training.

    Returns: HIGH | MEDIUM | LOW
    """

    text = clause.lower()

    HIGH_RISK_KEYWORDS = {
        "indemnify": 3,
        "penalty": 3,
        "liquidated damages": 3,
        "breach": 3,
        "terminate": 3,
        "termination": 3,
        "liability": 3,
        "hold harmless": 3,
        "unlimited liability": 4,
        "fine": 3,
        "forfeit": 3,
        "compensation": 2,
        "damages": 3,
        "losses": 2,
        "default": 3,
    }

    MEDIUM_RISK_KEYWORDS = {
        "arbitration": 2,
        "jurisdiction": 2,
        "governing law": 2,
        "force majeure": 2,
        "dispute": 2,
        "indirect damages": 2,
        "consequential damages": 2,
        "confidentiality": 1,
        "non-disclosure": 1,
        "nda": 1,
        "intellectual property": 2,
        "ip rights": 2,
        "assignment": 1,
        "subcontract": 1,
    }

    LOW_RISK_KEYWORDS = {
        "notice": 0.5,
        "severability": 0.5,
        "amendment": 0.5,
        "entire agreement": 0.5,
        "definitions": 0.5,
        "headings": 0.5,
        "counterparts": 0.5,
    }

    score = 0

    for word, weight in HIGH_RISK_KEYWORDS.items():
        if word in text:
            score += weight

    for word, weight in MEDIUM_RISK_KEYWORDS.items():
        if word in text:
            score += weight

    for word, weight in LOW_RISK_KEYWORDS.items():
        if word in text:
            score += weight

    # ---- Decision thresholds (tunable like training) ----
    if score >= 4:
        return "HIGH"
    elif score >= 2:
        return "MEDIUM"
    else:
        return "LOW"
