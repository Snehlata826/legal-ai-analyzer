"""
Report generation endpoint — with request_id validation.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from ..core.security import validate_request_id
from ..state import store
from ..services.pdf_report import generate_pdf_report

router = APIRouter()


@router.get("/report/{request_id}")
async def generate_report(request_id: str):
    """
    Generate and download a PDF analysis report.

    Security:
      - request_id validated as UUID4 (prevents path traversal)
      - File path constructed from report_output_dir + safe ID only
    """
    validate_request_id(request_id)

    if not store.request_exists(request_id):
        raise HTTPException(status_code=404, detail="Request not found.")

    results = store.get_request(request_id).get("results", [])
    if not results:
        raise HTTPException(
            status_code=400,
            detail="No analysis results found. Run /simplify first.",
        )

    try:
        pdf_path = generate_pdf_report(request_id, results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {e}")

    if not Path(pdf_path).exists():
        raise HTTPException(status_code=500, detail="PDF file was not created.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"legal_analysis_{request_id[:8]}.pdf",
    )
