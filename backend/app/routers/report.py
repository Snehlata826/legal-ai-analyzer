"""
Report generation endpoint
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from ..state import store
from ..services.pdf_report import generate_pdf_report

router = APIRouter()


@router.get("/report/{request_id}")
async def generate_report(request_id: str):
    """
    Generate and download PDF report for analyzed clauses.
    """
    if not store.request_exists(request_id):
        raise HTTPException(status_code=404, detail="Request not found")

    request_data = store.get_request(request_id)
    results = request_data.get("results", [])

    if not results:
        raise HTTPException(
            status_code=400,
            detail="No analysis results found. Run /simplify first."
        )

    try:
        # generate_pdf_report now RETURNS FILE PATH
        pdf_path = generate_pdf_report(request_id, results)

        if not Path(pdf_path).exists():
            raise HTTPException(status_code=500, detail="PDF file was not created")

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"legal_analysis_{request_id[:8]}.pdf"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )
