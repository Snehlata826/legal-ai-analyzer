from fastapi import APIRouter, HTTPException
from app.services.simplifier import simplify_clause
from app.state.store import REQUEST_STORE

router = APIRouter(prefix="/simplify", tags=["Simplification"])


@router.post("/{request_id}")
def simplify_document(request_id: str):
    if request_id not in REQUEST_STORE:
        raise HTTPException(status_code=404, detail="Invalid request_id")

    clauses = REQUEST_STORE[request_id]["clauses"]

    simplified_output = []

    for idx, clause in enumerate(clauses, start=1):
        simplified_output.append({
            "clause_no": idx,
            "original": clause,
            "simplified": simplify_clause(clause)
        })

    return {
        "request_id": request_id,
        "total_clauses": len(clauses),
        "results": simplified_output
    }
