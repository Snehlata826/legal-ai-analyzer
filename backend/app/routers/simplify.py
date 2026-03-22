"""
Simplification endpoint — ML classifier + SHAP + Groq + NLP entities.

For each clause returns:
  - original: raw clause text
  - simplified: plain English (Groq LLM)
  - risk: HIGH / MEDIUM / LOW  (ML ensemble — not keyword matching)
  - ml_confidence: model probability for the predicted class
  - ml_probabilities: full probability distribution across all classes
  - explanation: why this risk level
  - shap_attributions: SHAP feature attributions (replaces keyword hack)
  - entities: named entities from spaCy
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ..state import store
from ..services.simplifier import simplify_text
from ..core.risk_analyzer import analyze_risk, get_risk_keywords_found
from ..core.risk_explainer import get_risk_explanation
from ..core.clause_extractor import get_clause_entities
from ..core.shap_explainer import explain_clause, SHAP_AVAILABLE

# ML model — imported lazily so startup doesn't block if not yet trained
_risk_model = None

def _get_model():
    global _risk_model
    if _risk_model is None:
        try:
            from ..core.risk_model import get_risk_model
            _risk_model = get_risk_model()
        except Exception as e:
            print(f"[WARN] ML model unavailable ({e}), falling back to keyword classifier.")
    return _risk_model

router = APIRouter()


@router.post("/simplify/{request_id}")
async def simplify_clauses(request_id: str):
    """
    Simplify all clauses using Groq LLM, classify risk with ML ensemble,
    and generate SHAP explanations.
    """
    if not store.request_exists(request_id):
        raise HTTPException(
            status_code=404,
            detail="Request not found. Upload document first.",
        )

    clauses = store.get_request(request_id)["clauses"]
    model   = _get_model()
    results: List[Dict[str, Any]] = []

    for i, clause in enumerate(clauses):
        print(f"[INFO] Processing clause {i+1}/{len(clauses)}")

        # 1. Plain English summary via Groq
        simplified = simplify_text(clause)

        # 2. Risk classification — ML if available, keyword fallback
        if model is not None:
            ml_result    = model.predict(clause)
            risk_level   = ml_result["label"]
            ml_confidence   = ml_result["confidence"]
            ml_probabilities = ml_result["probabilities"]
            classifier_used  = "ml_ensemble"
        else:
            risk_level   = analyze_risk(clause)
            ml_confidence   = 0.75
            ml_probabilities = {risk_level: 0.75}
            classifier_used  = "keyword_fallback"

        # 3. Human-readable risk explanation
        explanation = get_risk_explanation(risk_level)

        # 4. SHAP attributions (or keyword fallback)
        shap_exp    = explain_clause(clause, top_k=8)
        attributions = shap_exp.top_features
        shap_method  = shap_exp.method

        # 5. Named entity recognition
        entities = get_clause_entities(clause)

        results.append({
            "original":          clause,
            "simplified":        simplified,
            "risk":              risk_level,
            "ml_confidence":     ml_confidence,
            "ml_probabilities":  ml_probabilities,
            "classifier":        classifier_used,
            "explanation":       explanation,
            "attributions":      attributions,
            "shap_method":       shap_method,
            "entities":          entities,
        })

    store.update_results(request_id, results)

    return {
        "request_id":      request_id,
        "results":         results,
        "total_processed": len(results),
        "shap_available":  SHAP_AVAILABLE,
        "classifier":      "ml_ensemble" if model else "keyword_fallback",
    }
