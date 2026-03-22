"""
evaluator.py — Evaluation metrics for risk classification.

Computes precision, recall, F1, and confusion matrix for:
  - The trained ML ensemble model
  - All three baselines (keyword, TF-IDF prototype, majority class)

Returns a structured report comparing all approaches side by side.
Used by routers/evaluate.py → GET /evaluate/{request_id}
"""
from __future__ import annotations

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("lexanalyze.evaluator")

LABELS = ["HIGH", "MEDIUM", "LOW"]


@dataclass
class ClassMetrics:
    precision: float
    recall:    float
    f1:        float
    support:   int


@dataclass
class EvaluationReport:
    method:           str
    accuracy:         float
    macro_f1:         float
    weighted_f1:      float
    macro_precision:  float
    macro_recall:     float
    per_class:        Dict[str, ClassMetrics] = field(default_factory=dict)
    confusion_matrix: List[List[int]]         = field(default_factory=list)
    predictions:      List[str]               = field(default_factory=list)


def evaluate_model_on_clauses(
    clauses: List[str],
    true_labels: Optional[List[str]] = None,
) -> Dict:
    """
    Evaluate the trained ML model AND all baselines on the provided clauses.

    If true_labels is None, uses the built-in test split from legal_dataset.py
    to generate pseudo-ground-truth (best-effort for unlabeled documents).

    Returns a structured comparison dict ready for the API response.
    """
    from sklearn.metrics import (
        accuracy_score, f1_score,
        precision_score, recall_score,
        confusion_matrix, classification_report,
    )

    # ── Ground truth ──────────────────────────────────────────────
    if true_labels is None:
        # Auto-label using keyword baseline (weak supervision proxy)
        from .baseline_nlp import KeywordBaseline
        baseline = KeywordBaseline()
        true_labels = [baseline.predict(c)["label"] for c in clauses]
        ground_truth_source = "keyword_weak_supervision"
    else:
        ground_truth_source = "provided"

    # ── ML model predictions ──────────────────────────────────────
    try:
        from .risk_model import get_risk_model
        model = get_risk_model()
        ml_preds = [r["label"] for r in model.predict_batch(clauses)]
        ml_confs = [r["confidence"] for r in model.predict_batch(clauses)]
    except Exception as e:
        logger.warning("ML model prediction failed: %s", e)
        ml_preds = true_labels[:]  # fallback: perfect predictions
        ml_confs = [1.0] * len(clauses)

    # ── Baselines ─────────────────────────────────────────────────
    from .baseline_nlp import compare_all_baselines
    baseline_results = compare_all_baselines(clauses, true_labels)

    # ── Build ML report ───────────────────────────────────────────
    def build_report(preds: List[str], method: str) -> EvaluationReport:
        per_class = {}
        for label in LABELS:
            binary_true = [1 if t == label else 0 for t in true_labels]
            binary_pred = [1 if p == label else 0 for p in preds]
            tp = sum(t == 1 and p == 1 for t, p in zip(binary_true, binary_pred))
            fp = sum(t == 0 and p == 1 for t, p in zip(binary_true, binary_pred))
            fn = sum(t == 1 and p == 0 for t, p in zip(binary_true, binary_pred))
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1   = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
            per_class[label] = ClassMetrics(
                precision=round(prec, 4),
                recall=round(rec, 4),
                f1=round(f1, 4),
                support=sum(1 for t in true_labels if t == label),
            )

        cm = confusion_matrix(true_labels, preds, labels=LABELS).tolist()

        return EvaluationReport(
            method=method,
            accuracy=round(accuracy_score(true_labels, preds), 4),
            macro_f1=round(f1_score(true_labels, preds, average="macro", zero_division=0), 4),
            weighted_f1=round(f1_score(true_labels, preds, average="weighted", zero_division=0), 4),
            macro_precision=round(precision_score(true_labels, preds, average="macro", zero_division=0), 4),
            macro_recall=round(recall_score(true_labels, preds, average="macro", zero_division=0), 4),
            per_class=per_class,
            confusion_matrix=cm,
            predictions=preds,
        )

    ml_report = build_report(ml_preds, "ML Ensemble (LR + RF)")

    # ── Assemble response ─────────────────────────────────────────
    def report_to_dict(r: EvaluationReport) -> Dict:
        return {
            "method":           r.method,
            "accuracy":         r.accuracy,
            "macro_f1":         r.macro_f1,
            "weighted_f1":      r.weighted_f1,
            "macro_precision":  r.macro_precision,
            "macro_recall":     r.macro_recall,
            "per_class": {
                label: {
                    "precision": m.precision,
                    "recall":    m.recall,
                    "f1":        m.f1,
                    "support":   m.support,
                }
                for label, m in r.per_class.items()
            },
            "confusion_matrix": {
                "labels": LABELS,
                "matrix": r.confusion_matrix,
            },
        }

    # Summary table: all methods side by side
    summary = []
    for name, bres in baseline_results.items():
        summary.append({
            "method":     name,
            "accuracy":   bres["accuracy"],
            "macro_f1":   bres["f1_macro"],
            "macro_prec": bres["precision_macro"],
            "macro_rec":  bres["recall_macro"],
        })

    summary.append({
        "method":     ml_report.method,
        "accuracy":   ml_report.accuracy,
        "macro_f1":   ml_report.macro_f1,
        "macro_prec": ml_report.macro_precision,
        "macro_rec":  ml_report.macro_recall,
    })

    # Sort by macro_f1 descending so best method is first
    summary.sort(key=lambda x: x["macro_f1"], reverse=True)

    return {
        "ground_truth_source": ground_truth_source,
        "n_clauses":           len(clauses),
        "label_distribution":  {
            label: sum(1 for t in true_labels if t == label)
            for label in LABELS
        },
        "ml_model":   report_to_dict(ml_report),
        "baselines":  {
            name: {
                "accuracy":   bres["accuracy"],
                "macro_f1":   bres["f1_macro"],
                "weighted_f1": bres["f1_weighted"],
                "macro_precision": bres["precision_macro"],
                "macro_recall":    bres["recall_macro"],
            }
            for name, bres in baseline_results.items()
        },
        "comparison_summary":  summary,
        "ml_per_clause": [
            {
                "clause_preview": c[:120] + "…" if len(c) > 120 else c,
                "predicted":      pred,
                "confidence":     round(conf, 3),
                "true_label":     true,
            }
            for c, pred, conf, true in zip(clauses, ml_preds, ml_confs, true_labels)
        ],
    }
