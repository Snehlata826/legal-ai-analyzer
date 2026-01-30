import re
from transformers import pipeline

# ---------- AI MODEL (loaded once) ----------
try:
    ai_simplifier = pipeline(
        "text2text-generation",
        model="google/flan-t5-base"
    )
except Exception:
    ai_simplifier = None


# ---------- RULE-BASED FALLBACK ----------
REPLACEMENTS = {
    "indemnify": "pay for losses",
    "hold harmless": "not blame",
    "force majeure": "events beyond control",
    "terminate": "end",
    "shall": "will",
    "liable": "legally responsible",
    "governed and construed in accordance with": "follow",
    "arbitration": "private dispute resolution",
    "jurisdiction": "legal authority",
    "severed": "removed",
    "waiver": "giving up a right",
}

def rule_based_simplify(text: str) -> str:
    t = text.lower()
    for legal, simple in REPLACEMENTS.items():
        t = t.replace(legal, simple)

    t = re.sub(r"\s+", " ", t).strip()
    return f"Simple meaning: {t.capitalize()}"

def clean_clause_text(clause: str) -> str:
    """
    Removes numbering and clause titles from legal clauses.
    """
    text = clause.strip()

    # Remove numbering like "1.", "2)", "3. "
    text = re.sub(r"^\d+[\.\)]\s*", "", text)

    # Remove clause titles like "Indemnification:", "Force Majeure:"
    text = re.sub(r"^[A-Za-z\s]+:\s*", "", text)

    return text.strip()

# ---------- MAIN FUNCTION ----------
def simplify_clause(clause: str) -> str:
    """
    Production-ready legal clause simplifier.
    Uses AI first, falls back to rule-based logic safely.
    """

    clause = clean_clause_text(clause)
    if not clause:
        return "No meaningful legal content found."

    # ----- Try AI simplification -----
    if ai_simplifier:
        try:
            prompt = (
                "Explain the following legal clause in very simple English.\n"
                "Do NOT repeat the clause.\n"
                "Explain the meaning in 1 or 2 short sentences using everyday words.\n\n"
                f"{clause}"
            )

            result = ai_simplifier(
                prompt,
                max_length=120,
                do_sample=False
            )

            simplified = result[0]["generated_text"].strip()

            # ---- Quality checks ----
            if (
                len(simplified) < 25
                or simplified.lower() in clause.lower()
                or clause.lower() in simplified.lower()
            ):
                raise ValueError("Weak AI output")

            return simplified

        except Exception:
            pass  # fallback below

    # ----- Fallback -----
    return rule_based_simplify(clause)
