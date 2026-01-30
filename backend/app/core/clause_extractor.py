import re
from typing import List

def extract_clauses(text: str) -> List[str]:
    """
    Splits legal document text into individual clauses.
    Returns a list of clause strings.
    """
    if not text:
        return []

    clauses = []
    lines = re.split(r"\n+|\r+", text)

    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect start of a new clause
        if re.match(r"^(\d+\.|clause|section)", line.lower()):
            if buffer:
                clauses.append(buffer.strip())
            buffer = line
        else:
            buffer += " " + line

    if buffer:
        clauses.append(buffer.strip())

    return clauses
