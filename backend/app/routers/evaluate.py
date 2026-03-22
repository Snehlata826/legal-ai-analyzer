"""
routers/evaluate.py — GET /evaluate/{request_id}

Returns a full evaluation report comparing the ML model against
all baselines (keyword, TF-IDF, majority class) on the clauses
from the uploaded document.

Also adds SHAP explanations for each clause's risk prediction.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional

from ..core.security import validate_request_id
from ..core.evaluator import evaluate_model_on_clauses
from ..core.shap_explainer import explain_batch
from ..state.store import REQUEST_STORE

router = APIRouter()


@router.get("/evaluate/{request_id}")
async def evaluate_document(
    request_id: str,
    include_shap: bool = True,
    top_k_shap: int = 8,
):
    """
    Evaluate risk classification quality on this document's clauses.

    Returns:
    - ML ensemble metrics (precision / recall / F1 per class)
    - Confusion matrix
    - Side-by-side comparison with 3 baselines
    - SHAP feature attributions for each clause (if include_shap=True)

    Query params:
      include_shap (bool, default True) — include SHAP explanations
      top_k_shap   (int, default 8)    — number of top SHAP features per clause
    """
    validate_request_id(request_id)

    if request_id not in REQUEST_STORE:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Please upload first.",
        )

    data    = REQUEST_STORE[request_id]
    clauses = data.get("clauses", [])
    results = data.get("results", [])

    if not clauses:
        raise HTTPException(
            status_code=400,
            detail="No clauses found. Please upload and process a document first.",
        )

    # ── Use previously computed risk labels if available ───────────
    true_labels: Optional[List[str]] = None
    if results:
        true_labels = [r.get("risk", "LOW") for r in results]

    # ── Run evaluation ────────────────────────────────────────────
    try:
        eval_report = evaluate_model_on_clauses(clauses, true_labels)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}",
        )

    # ── SHAP explanations ─────────────────────────────────────────
    shap_results: List[Dict] = []
    if include_shap:
        try:
            explanations = explain_batch(clauses, top_k=top_k_shap)
            shap_results = [
                {
                    "clause_index":   i,
                    "predicted_label": exp.predicted_label,
                    "confidence":     exp.confidence,
                    "method":         exp.method,
                    "top_features":   exp.top_features,
                }
                for i, exp in enumerate(explanations)
            ]
        except Exception as e:
            shap_results = [{"error": str(e)}]

    return {
        "request_id":       request_id,
        "evaluation":       eval_report,
        "shap_explanations": shap_results,
        "metadata": {
            "shap_available": _shap_available(),
            "model_type":     "ensemble_lr_rf",
            "feature_type":   "tfidf_ngrams_1_3",
        },
    }


def _shap_available() -> bool:
    try:
        import shap  # noqa
        return True
    except ImportError:
        return False
