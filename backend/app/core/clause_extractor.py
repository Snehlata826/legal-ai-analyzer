"""
Clause extraction logic from legal documents
"""
import re
from typing import List


def extract_clauses(text: str) -> List[str]:
    """
    Extract clauses from legal document text using rule-based approach.
    
    Splits text based on:
    - Numbered sections (1., 2., etc.)
    - Lettered sections (a., b., etc.)
    - Double newlines (paragraph breaks)
    """
    # Clean up the text
    text = text.strip()
    
    # Split by numbered sections or paragraph breaks
    patterns = [
        r'\n\s*\d+\.\s+',  # Numbered sections like "1. "
        r'\n\s*[A-Z]\.\s+',  # Lettered sections like "A. "
        r'\n\s*\([a-z]\)\s+',  # Sections like "(a) "
        r'\n\n+'  # Double newlines
    ]
    
    # Combine patterns
    combined_pattern = '|'.join(patterns)
    
    # Split text
    raw_clauses = re.split(combined_pattern, text)
    
    # Clean and filter clauses
    clauses = []
    for clause in raw_clauses:
        # Remove extra whitespace
        clause = ' '.join(clause.split())
        
        # Only keep clauses with meaningful content (at least 20 chars and some words)
        if len(clause) > 20 and len(clause.split()) > 3:
            clauses.append(clause)
    
    # If no clauses found, split by sentences as fallback
    if len(clauses) == 0:
        sentences = re.split(r'\.\s+', text)
        clauses = [s.strip() + '.' for s in sentences if len(s.strip()) > 20]
    
    return clauses[:50]  # Limit to 50 clauses for performance
