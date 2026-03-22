"""
baseline_nlp.py — Baseline NLP approaches for risk classification.

Provides three baselines to benchmark against the ML classifier:
  1. KeywordBaseline   — original keyword-matching approach (existing logic)
  2. TFIDFBaseline     — TF-IDF cosine similarity to prototype clauses
  3. LengthBaseline    — majority class prediction (dumbest possible baseline)

Used by:
  - train_classifier.py  → comparison table in training report
  - routers/evaluate.py  → /evaluate/{id} endpoint
"""
from __future__ import annotations

import re
import math
import logging
from typing import List, Dict, Literal

logger = logging.getLogger("lexanalyze.baseline")

RiskLabel = Literal["HIGH", "MEDIUM", "LOW"]

# ── Shared keyword lists (same as original risk_analyzer.py) ──────

HIGH_KEYWORDS = [
    "indemnif", "liability", "liable",
    "termination", "terminate",
    "penalty", "penalties",
    "breach", "damages", "default",
    "forfeiture", "waive", "waiver",
    "exclude", "exclusion",
    "disclaim", "disclaimer",
    "non-refundable", "irreversible",
    "unlimited liability", "sole responsibility",
]

MEDIUM_KEYWORDS = [
    "arbitration", "dispute", "jurisdiction",
    "governing law", "force majeure",
    "confidential", "proprietary",
    "intellectual property",
    "amendment", "modify", "modification",
    "notice", "consent", "assignment",
    "subcontract", "audit", "inspection",
]

# ── Prototype clauses for TF-IDF similarity baseline ─────────────

HIGH_PROTOTYPES = [
    "shall indemnify and hold harmless from any and all claims damages losses",
    "waives any right to seek consequential or punitive damages",
    "disclaims all warranties express or implied including merchantability",
    "terminate immediately without notice and retain all deposits paid",
    "jointly and severally liable for all obligations of the borrower",
]

MEDIUM_PROTOTYPES = [
    "disputes shall be resolved through binding arbitration in the jurisdiction",
    "governing law construed in accordance with the laws of the state",
    "confidential information strictly confidential for a period of years",
    "intellectual property created during the term shall be property of company",
    "force majeure affected party shall be excused from performance",
]

LOW_PROTOTYPES = [
    "entire agreement between parties supersedes all prior discussions",
    "if any provision found invalid remaining provisions continue in full force",
    "headings for convenience only shall not affect interpretation",
    "executed in counterparts each deemed an original",
    "independent contractors neither has authority to bind the other",
]


# ══════════════════════════════════════════════════════════════════
#  Baseline 1: Keyword matching (original logic)
# ══════════════════════════════════════════════════════════════════

class KeywordBaseline:
    """
    Reproduces the original keyword-matching risk logic exactly.
    This is the simplest useful baseline.
    """
    name = "Keyword Baseline"

    def predict(self, text: str) -> Dict:
        lower = text.lower()

        for kw in HIGH_KEYWORDS:
            if re.search(r'\b' + re.escape(kw), lower):
                return {"label": "HIGH", "confidence": 0.75, "method": "keyword"}

        for kw in MEDIUM_KEYWORDS:
            if re.search(r'\b' + re.escape(kw), lower):
                return {"label": "MEDIUM", "confidence": 0.65, "method": "keyword"}

        return {"label": "LOW", "confidence": 0.60, "method": "keyword"}

    def predict_batch(self, texts: List[str]) -> List[Dict]:
        return [self.predict(t) for t in texts]


# ══════════════════════════════════════════════════════════════════
#  Baseline 2: TF-IDF cosine similarity to prototype clauses
# ══════════════════════════════════════════════════════════════════

class TFIDFBaseline:
    """
    Computes TF-IDF vectors for input text and prototype clauses,
    then classifies by nearest prototype cluster (cosine similarity).

    No training data needed — just the 15 prototype sentences above.
    """
    name = "TF-IDF Prototype Baseline"

    def __init__(self):
        self._prototypes = {
            "HIGH":   HIGH_PROTOTYPES,
            "MEDIUM": MEDIUM_PROTOTYPES,
            "LOW":    LOW_PROTOTYPES,
        }
        self._vocab: List[str] = []
        self._proto_vecs: Dict[str, List[List[float]]] = {}
        self._build_index()

    def predict(self, text: str) -> Dict:
        q_vec = self._vectorise(text)

        best_label = "LOW"
        best_score = -1.0

        for label, vecs in self._proto_vecs.items():
            avg_sim = sum(self._cosine(q_vec, v) for v in vecs) / len(vecs)
            if avg_sim > best_score:
                best_score = avg_sim
                best_label = label

        return {
            "label":      best_label,
            "confidence": round(best_score, 4),
            "method":     "tfidf_prototype",
        }

    def predict_batch(self, texts: List[str]) -> List[Dict]:
        return [self.predict(t) for t in texts]

    # ── Private ───────────────────────────────────────────────────

    def _build_index(self):
        all_docs = []
        for sents in self._prototypes.values():
            all_docs.extend(sents)

        self._vocab, all_vecs = self._tfidf(all_docs)

        i = 0
        for label, sents in self._prototypes.items():
            self._proto_vecs[label] = all_vecs[i:i + len(sents)]
            i += len(sents)

    def _tfidf(self, docs: List[str]):
        tokenised = [re.findall(r"[a-z]+", d.lower()) for d in docs]
        df: Dict[str, int] = {}
        for tokens in tokenised:
            for t in set(tokens):
                df[t] = df.get(t, 0) + 1

        N = len(docs)
        vocab = sorted(df.keys())
        idx = {t: i for i, t in enumerate(vocab)}

        matrix = []
        for tokens in tokenised:
            counts: Dict[str, int] = {}
            for t in tokens:
                counts[t] = counts.get(t, 0) + 1
            n = len(tokens) or 1
            vec = [0.0] * len(vocab)
            for t, c in counts.items():
                if t in idx:
                    idf = math.log((N + 1) / (df[t] + 1)) + 1
                    vec[idx[t]] = (c / n) * idf
            matrix.append(vec)

        return vocab, matrix

    def _vectorise(self, text: str) -> List[float]:
        tokens = re.findall(r"[a-z]+", text.lower())
        counts: Dict[str, int] = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        n = len(tokens) or 1
        vec = [0.0] * len(self._vocab)
        vocab_idx = {t: i for i, t in enumerate(self._vocab)}
        for t, c in counts.items():
            if t in vocab_idx:
                vec[vocab_idx[t]] = c / n
        return vec

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na  = math.sqrt(sum(x * x for x in a))
        nb  = math.sqrt(sum(x * x for x in b))
        return dot / (na * nb) if na > 0 and nb > 0 else 0.0


# ══════════════════════════════════════════════════════════════════
#  Baseline 3: Majority class (trivial baseline)
# ══════════════════════════════════════════════════════════════════

class MajorityClassBaseline:
    """Always predicts the majority class. Floor for any useful classifier."""
    name = "Majority Class Baseline"

    def predict(self, text: str) -> Dict:
        return {"label": "HIGH", "confidence": 0.34, "method": "majority_class"}

    def predict_batch(self, texts: List[str]) -> List[Dict]:
        return [self.predict(t) for t in texts]


# ── Convenience function ──────────────────────────────────────────

def compare_all_baselines(texts: List[str], true_labels: List[str]) -> Dict:
    """
    Run all three baselines on the given texts and return a comparison dict.

    Used by the /evaluate/{id} endpoint.
    """
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

    baselines = [KeywordBaseline(), TFIDFBaseline(), MajorityClassBaseline()]
    results = {}

    for baseline in baselines:
        preds = [r["label"] for r in baseline.predict_batch(texts)]
        results[baseline.name] = {
            "accuracy":  round(accuracy_score(true_labels, preds), 4),
            "f1_macro":  round(f1_score(true_labels, preds, average="macro", zero_division=0), 4),
            "f1_weighted": round(f1_score(true_labels, preds, average="weighted", zero_division=0), 4),
            "precision_macro": round(precision_score(true_labels, preds, average="macro", zero_division=0), 4),
            "recall_macro":    round(recall_score(true_labels, preds, average="macro", zero_division=0), 4),
            "predictions": preds,
        }

    return results
