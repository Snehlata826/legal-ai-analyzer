from fastapi import APIRouter, HTTPException
from app.embeddings.embedder import EmbeddingEngine
from app.routers.upload import request_state

import requests
import os
import logging
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ask", tags=["Chat Q&A"])

# Sanity configuration
SANITY_PROJECT_ID = "your_project_id"  # replace with your project ID
SANITY_DATASET = "your_dataset"        # replace with your dataset name
SANITY_TOKEN = os.getenv("SANITY_TOKEN")  # optional if private dataset

def fetch_sanity_docs(query: str):
    """Fetch documents from Sanity using GROQ"""
    url = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2025-11-28/data/query/{SANITY_DATASET}"
    headers = {"Authorization": f"Bearer {SANITY_TOKEN}"} if SANITY_TOKEN else {}
    params = {"query": query}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json().get("result", [])
    except Exception as e:
        logger.error(f"Error fetching Sanity docs: {e}")
        return []

@router.post("/")
async def ask_question(question: dict):
    query_text = question.get("q")
    if not query_text:
        raise HTTPException(status_code=400, detail="Question 'q' is required.")

    # Load precomputed vector state
    chunks = request_state.get("chunks", [])
    vectors = request_state.get("vectors", [])

    if not chunks or not vectors:
        raise HTTPException(status_code=500, detail="No vector data available. Upload documents first.")

    # Embed query
    embedder = EmbeddingEngine()
    q_vec = embedder.model.encode([query_text])

    # Compute cosine similarity to find top context
    scores = cosine_similarity(q_vec, vectors)
    top_idx = scores[0].argmax()
    context = chunks[top_idx]

    # Use GROQ to fetch related documents from Sanity
    # Example: search articles or FAQs containing top context keywords
    keywords = " ".join(context.split()[:10])  # first 10 words as query
    groq_query = f'*[_type in ["article", "faq"] && count((title match "{keywords}") + (body match "{keywords}")) > 0]{{title, body}}'
    docs = fetch_sanity_docs(groq_query)

    if docs:
        # Combine matching docs as context
        context_text = "\n\n".join([f"{d['title']}: {d['body']}" for d in docs])
    else:
        context_text = context  # fallback to original chunk

    return {
        "answer": context_text,
        "source": context
    }
