"""
Legal text simplification using rule-based replacements
"""
import re
from typing import Dict


# Legal jargon to plain English mappings
JARGON_REPLACEMENTS: Dict[str, str] = {
    r'\bhereby\b': 'by this document',
    r'\bherein\b': 'in this document',
    r'\bhereinafter\b': 'from now on',
    r'\bheretofore\b': 'until now',
    r'\bhereto\b': 'to this',
    r'\bwhereas\b': 'since',
    r'\bwherein\b': 'in which',
    r'\bwhereby\b': 'by which',
    r'\bforthwith\b': 'immediately',
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
    r'\barbitration\b': 'dispute resolution',
    r'\bjurisdiction\b': 'legal authority',
    r'\bgoverning law\b': 'controlling law',
    r'\bexecute\b': 'sign',
    r'\bexecution\b': 'signing',
    r'\bparty\b': 'person or company',
    r'\bparties\b': 'people or companies',
    r'\baforementioned\b': 'mentioned above',
    r'\baforesaid\b': 'mentioned before',
    r'\bthereunder\b': 'under that',
    r'\bthereof\b': 'of that',
    r'\btherein\b': 'in that',
    r'\bwaive\b': 'give up',
    r'\bwaiver\b': 'giving up',
    r'\bpropriety\b': 'ownership',
    r'\bconfidential information\b': 'private information',
    r'\bdisclaim\b': 'deny responsibility for',
    r'\bdisclaimer\b': 'denial of responsibility'
}


def simplify_text(text: str) -> str:
    """
    Simplify legal text by replacing jargon with plain English.
    
    Args:
        text: Legal clause text
        
    Returns:
        Simplified version of the text
    """
    simplified = text
    
    # Apply all jargon replacements
    for pattern, replacement in JARGON_REPLACEMENTS.items():
        simplified = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)
    
    # Remove excessive legal formatting
    simplified = re.sub(r'\s+', ' ', simplified)  # Normalize whitespace
    simplified = simplified.strip()
    
    # Shorten if too long (keep first 200 chars for readability)
    if len(simplified) > 250:
        simplified = simplified[:247] + "..."
    
    return simplified
