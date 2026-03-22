"""
Embedding engine — lightweight, dependency-free fallback.

The original file imported langchain + sentence_transformers + FAISS,
none of which are in requirements.txt.  This replacement keeps the same
public API but uses only packages that ARE installed:
  - numpy (for cosine similarity)
  - a simple TF-IDF-style vector built from clause text

If you later want real semantic embeddings, install the packages listed
at the bottom of this file and swap in the SentenceTransformer block.
"""
from __future__ import annotations

import re
import math
from typing import List, Dict


# ── Text chunking (no external deps) ──────────────────────────────

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks by word count.
    Replaces RecursiveCharacterTextSplitter.
    """
    words = text.split()
    chunks: List[str] = []
    step = max(1, chunk_size - overlap)

    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk:
            chunks.append(chunk)

    return chunks


# ── Minimal TF-IDF vectoriser ──────────────────────────────────────

def _tokenise(text: str) -> List[str]:
    return re.findall(r"[a-z]+", text.lower())


def _tf(tokens: List[str]) -> Dict[str, float]:
    counts: Dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    n = len(tokens) or 1
    return {t: c / n for t, c in counts.items()}


def build_tfidf_vectors(chunks: List[str]):
    """
    Build simple TF-IDF vectors for a list of text chunks.
    Returns (vocab, matrix) where matrix[i] is the vector for chunks[i].
    """
    tokenised = [_tokenise(c) for c in chunks]

    # Document frequency
    df: Dict[str, int] = {}
    for tokens in tokenised:
        for t in set(tokens):
            df[t] = df.get(t, 0) + 1

    N = len(chunks)
    vocab = sorted(df.keys())
    idx = {t: i for i, t in enumerate(vocab)}

    matrix: List[List[float]] = []
    for tokens in tokenised:
        tf = _tf(tokens)
        vec = [0.0] * len(vocab)
        for t, tf_val in tf.items():
            if t in idx:
                idf = math.log((N + 1) / (df[t] + 1)) + 1
                vec[idx[t]] = tf_val * idf
        matrix.append(vec)

    return vocab, matrix


def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── Public EmbeddingEngine class (same API as before) ─────────────

class EmbeddingEngine:
    """
    Lightweight embedding engine backed by TF-IDF vectors.

    Drop-in for the old sentence_transformers / FAISS version.
    Real semantic search is available by uncommenting the block below.
    """

    def __init__(self):
        self._vocab: List[str] = []
        self._matrix: List[List[float]] = []
        self._chunks: List[str] = []
        print("[INFO] EmbeddingEngine initialised (TF-IDF mode)")

    def chunk(self, text: str) -> List[str]:
        return chunk_text(text)

    def build_index(self, chunks: List[str]) -> None:
        """Index a list of text chunks for similarity search."""
        self._chunks = chunks
        self._vocab, self._matrix = build_tfidf_vectors(chunks)

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Return the top_k most similar chunks to the query.
        Each result: {"chunk": str, "score": float, "index": int}
        """
        if not self._chunks:
            return []

        _, query_matrix = build_tfidf_vectors([query] + self._chunks)
        q_vec = query_matrix[0]

        scores = [
            cosine_similarity(q_vec, self._matrix[i])
            for i in range(len(self._chunks))
        ]

        ranked = sorted(
            enumerate(scores), key=lambda x: x[1], reverse=True
        )[:top_k]

        return [
            {"chunk": self._chunks[i], "score": round(s, 4), "index": i}
            for i, s in ranked
        ]

    # Legacy shims so old call-sites don't break ──────────────────
    def embed(self, chunks: List[str]):
        """Legacy: returns matrix rows (use build_index + search instead)."""
        _, matrix = build_tfidf_vectors(chunks)
        return matrix

    def build_vector_db(self, chunks, vectors):
        """Legacy stub — no-op in TF-IDF mode."""
        self.build_index(chunks)
        return self


# ══════════════════════════════════════════════════════════════════
#  OPTIONAL: Real semantic embeddings with sentence-transformers
#  Uncomment and install:
#    pip install sentence-transformers faiss-cpu
# ══════════════════════════════════════════════════════════════════
#
# from sentence_transformers import SentenceTransformer
# import numpy as np
# import faiss
#
# class EmbeddingEngine:
#     def __init__(self):
#         self.model = SentenceTransformer("all-MiniLM-L6-v2")
#         self._index = None
#         self._chunks = []
#
#     def chunk(self, text):
#         return chunk_text(text)
#
#     def build_index(self, chunks):
#         self._chunks = chunks
#         vecs = self.model.encode(chunks, show_progress_bar=False)
#         dim = vecs.shape[1]
#         self._index = faiss.IndexFlatL2(dim)
#         self._index.add(np.array(vecs, dtype="float32"))
#
#     def search(self, query, top_k=3):
#         q = np.array([self.model.encode(query)], dtype="float32")
#         _, indices = self._index.search(q, top_k)
#         return [{"chunk": self._chunks[i], "index": i} for i in indices[0]]
