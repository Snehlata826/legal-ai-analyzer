"""
Q&A endpoint using keyword search + Groq API (RAG pipeline)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from ..core.groq_client import call_groq
from ..state.store import REQUEST_STORE

router = APIRouter(prefix="/ask", tags=["Q&A"])


class QuestionRequest(BaseModel):
    request_id: str
    question: str


def _find_relevant_clauses(
    question: str,
    clauses: List[str],
    top_k: int = 3
) -> List[Dict]:
    """
    Find relevant clauses using keyword overlap scoring.
    Much more reliable than hash-based embeddings.
    """
    stop_words = {
        'what', 'is', 'the', 'are', 'how', 'does', 'do',
        'a', 'an', 'in', 'of', 'for', 'to', 'and', 'or',
        'this', 'that', 'it', 'be', 'will', 'can', 'has',
        'have', 'was', 'were', 'been', 'with', 'by', 'at'
    }
    q_words = set(question.lower().split()) - stop_words

    scored = []
    for clause in clauses:
        clause_lower = clause.lower()
        clause_words = set(clause_lower.split()) - stop_words

        # Keyword overlap score
        overlap = len(q_words & clause_words)

        # Bonus for exact phrase match
        bonus = 0
        for word in q_words:
            if len(word) > 4 and word in clause_lower:
                bonus += 2

        score = overlap + bonus
        if score > 0:
            scored.append({
                "clause": clause,
                "score": score
            })

    scored.sort(key=lambda x: x["score"], reverse=True)

    # If nothing matched, return first 3 clauses
    if not scored:
        return [{"clause": c, "score": 0} for c in clauses[:3]]

    return scored[:top_k]


@router.post("/")
async def ask_question(body: QuestionRequest):
    """
    Answer questions about uploaded legal document using RAG.
    """
    if body.request_id not in REQUEST_STORE:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Please upload first."
        )

    request_data = REQUEST_STORE[body.request_id]
    clauses = request_data.get("clauses", [])

    if not clauses:
        raise HTTPException(
            status_code=400,
            detail="No clauses found in document."
        )

    # Step 1 — Find relevant clauses
    relevant = _find_relevant_clauses(
        question=body.question,
        clauses=clauses,
        top_k=3
    )

    # Step 2 — Build context string
    context = "\n\n".join([
        f"Clause {i+1}: {item['clause']}"
        for i, item in enumerate(relevant)
    ])

    # Step 3 — Call Groq with improved prompt
    try:
        answer = call_groq(
            prompt=f"""You are a friendly legal document explainer helping a non-lawyer understand their contract.

Answer the question in TWO clearly labelled parts:

SIMPLE ANSWER: Explain in 1-2 plain English sentences anyone can understand. No legal jargon.

LEGAL DETAIL: Quote the exact relevant part of the clause that supports your answer.

Document clauses:
{context}

Question: {body.question}

Answer:""",
            system=(
                "You are a helpful legal assistant who explains legal documents "
                "in simple plain English. Always give a simple explanation first, "
                "then quote the legal detail. Be concise and clear."
            ),
            max_tokens=350,
            model="llama-3.1-8b-instant"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Groq API error: {str(e)}"
        )

    return {
        "answer": answer,
        "sources": [
            {
                "clause": (
                    item["clause"][:200] + "..."
                    if len(item["clause"]) > 200
                    else item["clause"]
                ),
                "relevance_score": round(item["score"] / 10, 3)
            }
            for item in relevant
        ]
    }