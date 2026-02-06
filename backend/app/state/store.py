"""
In-memory store for document processing requests
"""
from typing import Dict, List, Any

REQUEST_STORE: Dict[str, Dict[str, Any]] = {}


def create_request(request_id: str, clauses: List[str]) -> None:
    """Create a new request entry"""
    REQUEST_STORE[request_id] = {
        "clauses": clauses,
        "results": []
    }


def get_request(request_id: str) -> Dict[str, Any]:
    """Get request data by ID"""
    return REQUEST_STORE.get(request_id)


def update_results(request_id: str, results: List[Dict[str, Any]]) -> None:
    """Update results for a request"""
    if request_id in REQUEST_STORE:
        REQUEST_STORE[request_id]["results"] = results


def request_exists(request_id: str) -> bool:
    """Check if request exists"""
    return request_id in REQUEST_STORE
