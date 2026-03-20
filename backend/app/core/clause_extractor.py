"""
Clause extraction with spaCy NLP + regex fallback
"""
import re
from typing import List, Dict

# Try loading spaCy — graceful fallback if not installed
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    NLP_AVAILABLE = True
    print("[INFO] spaCy NLP pipeline loaded")
except Exception:
    NLP_AVAILABLE = False
    print("[WARN] spaCy not available — using regex extraction")


def extract_clauses(text: str) -> List[str]:
    """
    Extract clauses from legal document text.
    Uses spaCy if available, else regex fallback.
    """
    if NLP_AVAILABLE:
        return _spacy_extract(text)
    return _regex_extract(text)


def _spacy_extract(text: str) -> List[str]:
    """NLP-based extraction using spaCy sentence segmentation"""
    text = text.strip()

    # First split by numbered sections
    section_pattern = r'\n\s*\d+\.\s+'
    sections = re.split(section_pattern, text)

    clauses = []

    for section in sections:
        section = section.strip()
        if len(section) < 20:
            continue

        # Use spaCy to segment into sentences
        doc = nlp(section[:5000])
        sentences = [
            sent.text.strip()
            for sent in doc.sents
            if len(sent.text.strip()) > 20
        ]

        if len(sentences) <= 2:
            combined = ' '.join(sentences)
            if combined:
                clauses.append(combined)
        else:
            # Group sentences into meaningful chunks
            chunk = []
            for i, sent in enumerate(sentences):
                chunk.append(sent)
                if len(chunk) >= 2 or i == len(sentences) - 1:
                    combined = ' '.join(chunk)
                    if len(combined) > 30:
                        clauses.append(combined)
                    chunk = []

    # Clean and deduplicate
    seen = set()
    unique = []
    for c in clauses:
        clean = ' '.join(c.split())
        if clean not in seen and len(clean) > 30:
            seen.add(clean)
            unique.append(clean)

    return unique[:50]


def _regex_extract(text: str) -> List[str]:
    """Rule-based fallback extraction"""
    text = text.strip()
    patterns = [
        r'\n\s*\d+\.\s+',
        r'\n\s*[A-Z]\.\s+',
        r'\n\s*\([a-z]\)\s+',
        r'\n\n+'
    ]
    combined = '|'.join(patterns)
    raw = re.split(combined, text)
    clauses = []
    for clause in raw:
        clause = ' '.join(clause.split())
        if len(clause) > 20 and len(clause.split()) > 3:
            clauses.append(clause)
    if not clauses:
        sentences = re.split(r'\.\s+', text)
        clauses = [s.strip() + '.' for s in sentences if len(s.strip()) > 20]
    return clauses[:50]


def get_clause_entities(clause: str) -> List[Dict]:
    """
    Extract named entities from a clause using spaCy.
    Identifies parties, dates, amounts, locations.
    Returns empty list if spaCy not available.
    """
    if not NLP_AVAILABLE:
        return []

    ENTITY_LABELS = {
        "ORG": "Organization",
        "PERSON": "Person",
        "DATE": "Date",
        "MONEY": "Monetary amount",
        "LAW": "Legal reference",
        "GPE": "Location / Country",
        "CARDINAL": "Number",
        "PERCENT": "Percentage",
    }

    doc = nlp(clause)
    entities = []
    seen = set()

    for ent in doc.ents:
        if ent.label_ in ENTITY_LABELS and ent.text not in seen:
            seen.add(ent.text)
            entities.append({
                "text": ent.text,
                "type": ent.label_,
                "description": ENTITY_LABELS[ent.label_]
            })

    return entities
