"""
Upload endpoint for legal documents
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader
import io
import uuid

from ..core.clause_extractor import extract_clauses
from ..state import store

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF legal document and extract clauses.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:
        content = await file.read()

        # Validate it's actually a PDF
        if not content.startswith(b'%PDF-'):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file"
            )

        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)

        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        clauses = extract_clauses(text)

        if len(clauses) == 0:
            raise HTTPException(
                status_code=400,
                detail="No clauses found in document"
            )

        request_id = str(uuid.uuid4())
        store.create_request(request_id, clauses)

        return {
            "request_id": request_id,
            "clauses": clauses,
            "total_clauses": len(clauses)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )
