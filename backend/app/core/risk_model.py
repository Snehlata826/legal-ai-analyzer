"""
risk_model.py — Trained ML classifier for legal risk detection.

Two models trained on TF-IDF features:
  1. LogisticRegression  — fast, interpretable
  2. RandomForestClassifier — ensemble, captures non-linear patterns

Soft-vote ensemble averages probabilities from both models.
Auto-trains from built-in dataset on first run; saves to disk.
"""
from __future__ import annotations

import os
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline

logger = logging.getLogger("lexanalyze.risk_model")

LABEL_ORDER = ["HIGH", "MEDIUM", "LOW"]
MODEL_PATH  = Path(os.getenv("MODEL_PATH", "models/risk_classifier.pkl"))
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)


class RiskClassifier:
    def __init__(self):
        tfidf_params = dict(
            ngram_range=(1, 3),
            max_features=8000,
            sublinear_tf=True,
            min_df=1,
            analyzer="word",
            token_pattern=r"(?u)\b\w\w+\b",
        )

        self.lr_pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_params)),
            ("clf",   LogisticRegression(
                C=5.0,
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
                solver="lbfgs",
                
            )),
        ])

        self.rf_pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_params)),
            ("clf",   RandomForestClassifier(
                n_estimators=300,
                max_depth=None,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )),
        ])

        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(LABEL_ORDER)
        self._trained = False

    def fit(self, texts: List[str], labels: List[str]) -> "RiskClassifier":
        logger.info("Training risk classifier on %d examples…", len(texts))
        encoded = self.label_encoder.transform(labels)
        self.lr_pipeline.fit(texts, encoded)
        self.rf_pipeline.fit(texts, encoded)
        self._trained = True
        logger.info("Training complete.")
        return self

    def predict(self, text: str) -> Dict:
        self._check_trained()
        proba   = self._ensemble_proba([text])[0]
        idx     = int(np.argmax(proba))
        label   = self.label_encoder.inverse_transform([idx])[0]
        classes = self.label_encoder.classes_
        return {
            "label":         label,
            "confidence":    round(float(proba[idx]), 4),
            "probabilities": {c: round(float(p), 4) for c, p in zip(classes, proba)},
            "model":         "ensemble",
        }

    def predict_batch(self, texts: List[str]) -> List[Dict]:
        self._check_trained()
        probas  = self._ensemble_proba(texts)
        classes = self.label_encoder.classes_
        results = []
        for proba in probas:
            idx   = int(np.argmax(proba))
            label = self.label_encoder.inverse_transform([idx])[0]
            results.append({
                "label":         label,
                "confidence":    round(float(proba[idx]), 4),
                "probabilities": {c: round(float(p), 4) for c, p in zip(classes, proba)},
                "model":         "ensemble",
            })
        return results

    def get_feature_names(self) -> List[str]:
        self._check_trained()
        return self.lr_pipeline.named_steps["tfidf"].get_feature_names_out().tolist()

    def save(self, path: Optional[Path] = None) -> Path:
        p = path or MODEL_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            pickle.dump(self, f)
        logger.info("Model saved to %s", p)
        return p

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "RiskClassifier":
        p = path or MODEL_PATH
        with open(p, "rb") as f:
            model = pickle.load(f)
        logger.info("Model loaded from %s", p)
        return model

    @classmethod
    def exists(cls, path: Optional[Path] = None) -> bool:
        return (path or MODEL_PATH).exists()

    def _ensemble_proba(self, texts: List[str]) -> np.ndarray:
        p_lr = self.lr_pipeline.predict_proba(texts)
        p_rf = self.rf_pipeline.predict_proba(texts)
        return (p_lr * 0.55 + p_rf * 0.45)          # LR slightly higher weight

    def _check_trained(self):
        if not self._trained:
            raise RuntimeError(
                "Model not trained. Run: python -m app.core.train_classifier"
            )


_model: Optional[RiskClassifier] = None


def get_risk_model() -> RiskClassifier:
    global _model
    if _model is not None:
        return _model

    if RiskClassifier.exists():
        try:
            _model = RiskClassifier.load()
            return _model
        except Exception as e:
            logger.warning("Could not load saved model (%s). Retraining…", e)

    logger.info("No saved model — training from built-in dataset…")
    from .legal_dataset import get_dataset
    texts, labels = get_dataset()
    _model = RiskClassifier()
    _model.fit(texts, labels)
    _model.save()
    return _model
