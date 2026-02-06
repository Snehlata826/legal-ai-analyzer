"""
Simplification endpoint for legal clauses
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ..state import store
from ..services.simplifier import simplify_text
from ..core.risk_analyzer import analyze_risk
from ..core.risk_explainer import get_risk_explanation

router = APIRouter()


@router.post("/simplify/{request_id}")
async def simplify_clauses(request_id: str):
    """
    Simplify clauses and analyze risk for a given request.
    
    Args:
        request_id: Request ID from upload endpoint
        
    Returns:
        results: List of analyzed clauses with simplification and risk
    """
    # Check if request exists
    if not store.request_exists(request_id):
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Get request data
    request_data = store.get_request(request_id)
    clauses = request_data["clauses"]
    
    # Process each clause
    results: List[Dict[str, Any]] = []
    
    for clause in clauses:
        # Simplify text
        simplified = simplify_text(clause)
        
        # Analyze risk
        risk_level = analyze_risk(clause)
        
        # Get risk explanation
        explanation = get_risk_explanation(risk_level)
        
        results.append({
            "original": clause,
            "simplified": simplified,
            "risk": risk_level,
            "explanation": explanation
        })
    
    # Store results
    store.update_results(request_id, results)
    
    return {
        "request_id": request_id,
        "results": results,
        "total_processed": len(results)
    }
