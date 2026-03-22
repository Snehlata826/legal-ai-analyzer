"""
In-memory store for document processing requests.
"""
from typing import Dict, List, Any

REQUEST_STORE: Dict[str, Dict[str, Any]] = {}


def create_request(request_id: str, clauses: List[str]) -> None:
    REQUEST_STORE[request_id] = {"clauses": clauses, "results": []}


def get_request(request_id: str) -> Dict[str, Any]:
    return REQUEST_STORE.get(request_id)


def update_results(request_id: str, results: List[Dict[str, Any]]) -> None:
    if request_id in REQUEST_STORE:
        REQUEST_STORE[request_id]["results"] = results


def request_exists(request_id: str) -> bool:
    return request_id in REQUEST_STORE
