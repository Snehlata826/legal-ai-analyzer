"""
Legal text simplification using Groq API (free)
Falls back to rule-based if API unavailable
"""
from ..core.groq_client import call_groq

# Simple in-memory cache to avoid repeated API calls
_cache: dict = {}


def simplify_text(text: str) -> str:
    """
    Simplify legal clause using Groq LLM API.
    Uses cache to avoid duplicate API calls.
    Falls back to rule-based if API fails.
    """
    # Check cache first
    cache_key = text[:200]
    if cache_key in _cache:
        return _cache[cache_key]

    try:
        result = call_groq(
            prompt=f"""Simplify this legal clause into plain English.

Rules:
- Write maximum 2 short sentences
- Use simple everyday words anyone can understand
- Keep the exact legal meaning intact
- Do NOT add advice or opinions
- Do NOT say "This clause means..." — just write the simplified version directly

Legal clause:
{text}

Plain English:""",
            system="You are a legal document simplifier. Your job is to convert complex legal language into simple plain English that anyone can understand.",
            max_tokens=150,
            model="llama3-8b-8192"
        )
        _cache[cache_key] = result
        return result

    except Exception as e:
        print(f"[WARN] Groq simplification failed: {e}. Using fallback.")
        return _rule_based_simplify(text)


def _rule_based_simplify(text: str) -> str:
    """
    Rule-based fallback when API is unavailable.
    Kept from original project as backup.
    """
    import re

    REPLACEMENTS = {
        r'\bhereby\b': 'by this document',
        r'\bherein\b': 'in this document',
        r'\bhereinafter\b': 'from now on',
        r'\bnotwithstanding\b': 'despite',
        r'\bpursuant to\b': 'according to',
        r'\bprior to\b': 'before',
        r'\bsubsequent to\b': 'after',
        r'\bin the event that\b': 'if',
        r'\bprovided that\b': 'if',
        r'\bshall\b': 'will',
        r'\bmay not\b': 'cannot',
        r'\bshall not\b': 'will not',
        r'\bterminates?\b': 'ends',
        r'\btermination\b': 'ending',
        r'\bindemnify\b': 'compensate for losses',
        r'\bindemnification\b': 'compensation for losses',
        r'\bliable\b': 'responsible',
        r'\bliability\b': 'responsibility',
        r'\bbreach\b': 'violation',
        r'\bforce majeure\b': 'unforeseeable circumstances',
        r'\barbitration\b': 'dispute resolution outside court',
        r'\bjurisdiction\b': 'legal authority',
        r'\bwaive\b': 'give up',
        r'\bwaiver\b': 'giving up rights',
        r'\bdisclaim\b': 'deny responsibility for',
        r'\bdisclaimer\b': 'denial of responsibility',
        r'\bparty\b': 'person or company',
        r'\bparties\b': 'people or companies',
        r'\baforementioned\b': 'mentioned above',
        r'\bwhereas\b': 'since',
    }

    simplified = text
    for pattern, replacement in REPLACEMENTS.items():
        simplified = re.sub(
            pattern, replacement,
            simplified, flags=re.IGNORECASE
        )

    simplified = ' '.join(simplified.split()).strip()
    if len(simplified) > 1000:
        simplified = simplified[:997] + "..."
    return simplified