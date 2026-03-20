"""
Simplification endpoint — upgraded with Groq API + explainability
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ..state import store
from ..services.simplifier import simplify_text
from ..core.risk_analyzer import analyze_risk
from ..core.risk_explainer import get_risk_explanation, get_word_attributions
from ..core.clause_extractor import get_clause_entities

router = APIRouter()


@router.post("/simplify/{request_id}")
async def simplify_clauses(request_id: str):
    """
    Simplify clauses using Groq LLM + analyze risk.

    Returns for each clause:
    - original: original legal text
    - simplified: plain English version (Groq powered)
    - risk: HIGH / MEDIUM / LOW
    - explanation: why this risk level
    - attributions: which words caused the risk (explainability)
    - entities: named entities found (parties, dates, amounts)
    """
    if not store.request_exists(request_id):
        raise HTTPException(
            status_code=404,
            detail="Request not found. Upload document first."
        )

    request_data = store.get_request(request_id)
    clauses = request_data["clauses"]

    results: List[Dict[str, Any]] = []

    for i, clause in enumerate(clauses):
        print(f"[INFO] Processing clause {i+1}/{len(clauses)}")

        # 1. Simplify using Groq API
        simplified = simplify_text(clause)

        # 2. Analyze risk using keyword matching
        risk_level = analyze_risk(clause)

        # 3. Get risk explanation
        explanation = get_risk_explanation(risk_level)

        # 4. Get word-level attributions (explainability)
        attributions = get_word_attributions(clause)

        # 5. Extract named entities (NLP feature)
        entities = get_clause_entities(clause)

        results.append({
            "original": clause,
            "simplified": simplified,
            "risk": risk_level,
            "explanation": explanation,
            "attributions": attributions,
            "entities": entities
        })

    store.update_results(request_id, results)

    return {
        "request_id": request_id,
        "results": results,
        "total_processed": len(results)
    }
