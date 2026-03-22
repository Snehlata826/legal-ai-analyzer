"""
train_classifier.py — Full training pipeline with cross-validation.

Run from backend/ directory:
    python -m app.core.train_classifier
"""
from __future__ import annotations

import sys
import logging
from pathlib import Path
from collections import Counter

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.model_selection import cross_val_score, StratifiedKFold

sys.path.insert(0, str(Path(__file__).parents[3]))

from app.core.legal_dataset import get_dataset, train_val_test_split
from app.core.risk_model import RiskClassifier
from app.core.baseline_nlp import KeywordBaseline, TFIDFBaseline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("train")

SEP = "=" * 62


def train_and_evaluate():
    print(f"\n{SEP}")
    print("  Legal Risk Classifier — Training Pipeline")
    print(SEP)

    # ── 1. Load ───────────────────────────────────────────────────
    texts, labels = get_dataset()
    dist = Counter(labels)
    print(f"\nDataset: {len(texts)} examples")
    for k in ["HIGH", "MEDIUM", "LOW"]:
        print(f"  {k:<8} {dist[k]} examples")

    # ── 2. Cross-validation (5-fold) ─────────────────────────────
    print(f"\n{SEP}")
    print("  5-Fold Cross-Validation (full dataset)")
    print(SEP)

    cv_model = RiskClassifier()
    # Use LR pipeline for CV scoring (fast)
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder(); le.fit(["HIGH", "MEDIUM", "LOW"])
    y_encoded = le.transform(labels)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    lr_scores = cross_val_score(
        cv_model.lr_pipeline, texts, y_encoded,
        cv=cv, scoring="f1_macro", n_jobs=-1
    )
    rf_scores = cross_val_score(
        cv_model.rf_pipeline, texts, y_encoded,
        cv=cv, scoring="f1_macro", n_jobs=-1
    )

    print(f"\n  Logistic Regression  — CV macro-F1: {lr_scores.mean():.4f} ± {lr_scores.std():.4f}")
    print(f"  Random Forest        — CV macro-F1: {rf_scores.mean():.4f} ± {rf_scores.std():.4f}")
    ensemble_cv = (lr_scores + rf_scores) / 2
    print(f"  Ensemble (avg)       — CV macro-F1: {ensemble_cv.mean():.4f} ± {ensemble_cv.std():.4f}")

    # ── 3. Hold-out split ─────────────────────────────────────────
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split(
        texts, labels, val_ratio=0.10, test_ratio=0.15
    )
    print(f"\nHold-out split → train: {len(X_train)}  val: {len(X_val)}  test: {len(X_test)}")

    # ── 4. Train ──────────────────────────────────────────────────
    model = RiskClassifier()
    logger.info("Training on %d examples…", len(X_train))
    model.fit(X_train, y_train)

    # ── 5. Validation ─────────────────────────────────────────────
    val_preds = [r["label"] for r in model.predict_batch(X_val)]
    val_f1  = f1_score(y_val, val_preds, average="macro", zero_division=0)
    val_acc = accuracy_score(y_val, val_preds)
    print(f"Validation — accuracy: {val_acc:.4f}  macro-F1: {val_f1:.4f}")

    # ── 6. Test ───────────────────────────────────────────────────
    test_preds = [r["label"] for r in model.predict_batch(X_test)]
    test_acc = accuracy_score(y_test, test_preds)
    test_f1  = f1_score(y_test, test_preds, average="macro", zero_division=0)

    print(f"\n{SEP}")
    print("  TEST SET EVALUATION — Ensemble (LR + RF)")
    print(SEP)
    print(classification_report(
        y_test, test_preds,
        labels=["HIGH", "MEDIUM", "LOW"],
        target_names=["HIGH", "MEDIUM", "LOW"],
        zero_division=0,
    ))
    print(f"Accuracy:   {test_acc:.4f}")
    print(f"Macro-F1:   {test_f1:.4f}")

    cm = confusion_matrix(y_test, test_preds, labels=["HIGH", "MEDIUM", "LOW"])
    print("\nConfusion matrix (rows=true, cols=pred):")
    print("             HIGH   MED    LOW")
    for i, lbl in enumerate(["HIGH  ", "MEDIUM", "LOW   "]):
        print(f"  {lbl}  {cm[i]}")

    # ── 7. Baselines ──────────────────────────────────────────────
    kw  = KeywordBaseline()
    tfi = TFIDFBaseline()
    kw_preds  = [kw.predict(t)["label"]  for t in X_test]
    tfi_preds = [tfi.predict(t)["label"] for t in X_test]

    kw_f1   = f1_score(y_test, kw_preds,  average="macro", zero_division=0)
    tfi_f1  = f1_score(y_test, tfi_preds, average="macro", zero_division=0)
    kw_acc  = accuracy_score(y_test, kw_preds)
    tfi_acc = accuracy_score(y_test, tfi_preds)

    print(f"\n{SEP}")
    print("  BASELINE COMPARISON (hold-out test set)")
    print(SEP)
    print(f"  {'Method':<30} {'Accuracy':>10} {'Macro-F1':>10}")
    print(f"  {'-'*52}")
    print(f"  {'Keyword baseline':<30} {kw_acc:>10.4f} {kw_f1:>10.4f}")
    print(f"  {'TF-IDF prototype':<30} {tfi_acc:>10.4f} {tfi_f1:>10.4f}")
    print(f"  {'Ensemble (LR + RF)':<30} {test_acc:>10.4f} {test_f1:>10.4f}")

    best_baseline = max(kw_f1, tfi_f1)
    delta = (test_f1 - best_baseline) / max(best_baseline, 1e-9) * 100
    winner = "✓ ML model wins" if delta > 0 else "⚠ Baseline stronger on this split"
    print(f"\n  vs best baseline: {delta:+.1f}%  {winner}")
    print(f"\n  Cross-validation F1: {ensemble_cv.mean():.4f} ± {ensemble_cv.std():.4f}  ← more reliable estimate")

    # ── 8. Save ───────────────────────────────────────────────────
    # Retrain on train+val for final model
    X_full  = X_train + X_val
    y_full  = y_train + y_val
    model.fit(X_full, y_full)
    saved = model.save()
    print(f"\n  Model saved → {saved}")
    print(f"{SEP}\n")

    return model


if __name__ == "__main__":
    train_and_evaluate()
