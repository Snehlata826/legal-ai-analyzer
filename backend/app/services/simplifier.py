def simplify_clause(clause: str) -> str:
    """
    Simplifies a legal clause into plain Hinglish.
    (LLM placeholder – rule-based for now)
    """
    prompt = f"""
    Explain the following legal clause in very simple Hinglish.
    Avoid legal jargon. Explain like to a common Indian citizen.

    Clause:
    {clause}
    """

    # TEMP: mock response (replace with LLM later)
    return "Simple explanation: " + clause[:150] + "..."
