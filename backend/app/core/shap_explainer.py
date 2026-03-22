"""
shap_explainer.py — SHAP-based feature attribution for the risk classifier.

Provides word-level importance scores showing WHY a clause was classified
at a given risk level. This is the production-grade replacement for the
original keyword-attribution hack.

Two explainers are used:
  - LinearExplainer  → for LogisticRegression (exact, fast)
  - TreeExplainer    → for RandomForest (tree-native, fast)

The final attribution is the average SHAP value across both models,
giving a robust ensemble explanation.

Usage:
    from app.core.shap_explainer import explain_clause
    result = explain_clause("Party B shall indemnify Party A...")
    # result.top_features → [{"word": "indemnify", "shap_value": 0.34, ...}, ...]
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import numpy as np

logger = logging.getLogger("lexanalyze.shap")

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning(
        "shap not installed — SHAP explanations unavailable. "
        "Install with: pip install shap"
    )


@dataclass
class ShapExplanation:
    """Structured SHAP result for a single clause."""
    predicted_label: str
    confidence: float
    top_features: List[Dict]        # [{"word": str, "shap_value": float, "direction": str}]
    all_shap_values: Dict[str, float]  # word → mean |SHAP| across classes
    method: str = "shap"            # "shap" | "keyword_fallback"
    error: Optional[str] = None


def explain_clause(
    clause: str,
    top_k: int = 10,
) -> ShapExplanation:
    """
    Produce a SHAP-based explanation for a single clause.

    Args:
        clause:  The legal clause text to explain.
        top_k:   Number of top features to return.

    Returns:
        ShapExplanation with top_features sorted by |shap_value| descending.
    """
    if not SHAP_AVAILABLE:
        return _keyword_fallback(clause, top_k)

    try:
        return _shap_explain(clause, top_k)
    except Exception as e:
        logger.warning("SHAP explanation failed (%s) — falling back to keywords.", e)
        result = _keyword_fallback(clause, top_k)
        result.error = str(e)
        return result


def explain_batch(clauses: List[str], top_k: int = 10) -> List[ShapExplanation]:
    """Explain multiple clauses (more efficient than repeated explain_clause calls)."""
    if not SHAP_AVAILABLE:
        return [_keyword_fallback(c, top_k) for c in clauses]

    try:
        return _shap_explain_batch(clauses, top_k)
    except Exception as e:
        logger.warning("Batch SHAP failed (%s) — falling back.", e)
        return [_keyword_fallback(c, top_k) for c in clauses]


# ── Private: SHAP computation ─────────────────────────────────────

def _shap_explain(clause: str, top_k: int) -> ShapExplanation:
    from .risk_model import get_risk_model
    model = get_risk_model()

    # Get prediction first
    pred = model.predict(clause)
    pred_label = pred["label"]
    confidence = pred["confidence"]

    # ── LinearExplainer on LogisticRegression ─────────────────────
    lr_pipe  = model.lr_pipeline
    tfidf_lr = lr_pipe.named_steps["tfidf"]
    clf_lr   = lr_pipe.named_steps["clf"]

    X_lr = tfidf_lr.transform([clause])
    feature_names = tfidf_lr.get_feature_names_out()

    # Background: sparse zero vector (mean of training = roughly zero in TF-IDF space)
    background_lr = np.zeros((1, X_lr.shape[1]))
    explainer_lr  = shap.LinearExplainer(clf_lr, background_lr, feature_perturbation="interventional")
    shap_values_lr = explainer_lr.shap_values(X_lr)  # list[n_classes] of (n_samples, n_features)

    # ── TreeExplainer on RandomForest ─────────────────────────────
    rf_pipe  = model.rf_pipeline
    tfidf_rf = rf_pipe.named_steps["tfidf"]
    clf_rf   = rf_pipe.named_steps["clf"]

    X_rf = tfidf_rf.transform([clause])

    # TreeExplainer requires dense arrays for small inputs
    explainer_rf  = shap.TreeExplainer(clf_rf)
    shap_values_rf = explainer_rf.shap_values(X_rf.toarray())  # (n_classes, n_samples, n_features)

    # ── Map predicted label → class index ─────────────────────────
    classes = model.label_encoder.classes_.tolist()   # ["HIGH", "LOW", "MEDIUM"] (sorted)
    pred_idx = classes.index(pred_label)

    # Extract SHAP values for predicted class, clause index 0
    sv_lr = np.array(shap_values_lr[pred_idx][0])   # (n_features,) for LR
    sv_rf = np.array(shap_values_rf[pred_idx][0])   # (n_features,) for RF

    # Re-align RF features to LR vocabulary (same params → same vocab)
    sv_combined = (sv_lr + sv_rf) / 2.0

    # ── Build feature importance dict ──────────────────────────────
    clause_lower = clause.lower()
    shap_dict = {}
    for feat, sv in zip(feature_names, sv_combined):
        # Only include features actually present in the clause
        if feat in clause_lower or any(w in clause_lower for w in feat.split()):
            shap_dict[feat] = float(sv)

    # Sort by absolute value
    sorted_feats = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:top_k]

    top_features = [
        {
            "word":       feat,
            "shap_value": round(sv, 5),
            "direction":  "increases_risk" if sv > 0 else "decreases_risk",
            "abs_value":  round(abs(sv), 5),
        }
        for feat, sv in sorted_feats
    ]

    return ShapExplanation(
        predicted_label=pred_label,
        confidence=confidence,
        top_features=top_features,
        all_shap_values={f: round(v, 5) for f, v in sorted_feats},
        method="shap",
    )


def _shap_explain_batch(clauses: List[str], top_k: int) -> List[ShapExplanation]:
    """Batch SHAP — reuse explainer objects across clauses."""
    # For simplicity and correctness, compute individually
    # (batch SHAP doesn't improve correctness for sparse TF-IDF)
    return [_shap_explain(c, top_k) for c in clauses]


# ── Fallback: keyword-based attribution ───────────────────────────

_HIGH_WORDS = {
    "indemnif", "liability", "liable", "terminate", "termination",
    "breach", "damages", "penalty", "waive", "waiver", "disclaim",
    "disclaimer", "forfeiture", "non-refundable", "unlimited",
}
_MEDIUM_WORDS = {
    "arbitration", "jurisdiction", "confidential", "force majeure",
    "amendment", "assignment", "subcontract", "audit", "consent",
    "governing", "mediation",
}

_REASONS = {
    "indemnif":      "Imposes financial compensation obligation",
    "liability":     "Assigns legal responsibility for losses",
    "liable":        "Assigns legal responsibility",
    "terminate":     "Allows contract to be ended",
    "termination":   "Allows contract to be ended",
    "breach":        "Defines violation consequences",
    "damages":       "Specifies financial penalties",
    "waive":         "Removes legal rights",
    "waiver":        "Removes legal rights",
    "disclaim":      "Denies party's responsibility",
    "disclaimer":    "Denies party's responsibility",
    "penalty":       "Imposes financial punishment",
    "forfeiture":    "Results in loss of deposit or rights",
    "non-refundable":"Money cannot be recovered",
    "arbitration":   "Dispute resolved outside court",
    "jurisdiction":  "Determines which court applies",
    "confidential":  "Restricts information sharing",
    "force majeure": "Excuses performance on external events",
    "amendment":     "Contract can be changed unilaterally",
    "assignment":    "Rights can be transferred",
    "audit":         "Allows inspection of records",
}


def _keyword_fallback(clause: str, top_k: int) -> ShapExplanation:
    from .risk_analyzer import analyze_risk
    label = analyze_risk(clause)
    lower = clause.lower()

    found = []
    for word in _HIGH_WORDS:
        if word in lower:
            found.append({
                "word":       word,
                "shap_value": 0.9,
                "direction":  "increases_risk",
                "abs_value":  0.9,
                "reason":     _REASONS.get(word, "High-risk legal term"),
            })
    for word in _MEDIUM_WORDS:
        if word in lower:
            found.append({
                "word":       word,
                "shap_value": 0.5,
                "direction":  "increases_risk",
                "abs_value":  0.5,
                "reason":     _REASONS.get(word, "Medium-risk legal term"),
            })

    found.sort(key=lambda x: x["abs_value"], reverse=True)

    return ShapExplanation(
        predicted_label=label,
        confidence=0.75 if found else 0.5,
        top_features=found[:top_k],
        all_shap_values={f["word"]: f["shap_value"] for f in found[:top_k]},
        method="keyword_fallback",
    )
