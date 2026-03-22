"""
Upload endpoint — with security validation.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader
import io
import uuid

from ..core.clause_extractor import extract_clauses
from ..core.config import settings
from ..core.security import validate_upload_file
from ..state import store

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF legal document and extract clauses.

    Security:
      - Extension + MIME type + magic-byte check via validate_upload_file()
      - Max file size enforced (MAX_UPLOAD_SIZE_MB from config)
      - Rate limited to RATE_LIMIT_UPLOAD/min per IP by middleware
    """
    content = await file.read()

    # ── Security validation ───────────────────────────────────────
    validate_upload_file(
        filename=file.filename or "",
        content=content,
        content_type=file.content_type or "",
    )

    # ── Size check ────────────────────────────────────────────────
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File too large. Maximum allowed size is "
                f"{settings.max_upload_size_mb} MB."
            ),
        )

    # ── Text extraction ───────────────────────────────────────────
    try:
        reader = PdfReader(io.BytesIO(content))
        text = "".join(
            (page.extract_text() or "") + "\n"
            for page in reader.pages
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse PDF: {e}")

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not extract text from this PDF. "
                "The file may be scanned/image-based. "
                "Try a text-based PDF instead."
            ),
        )

    # ── Clause extraction ─────────────────────────────────────────
    clauses = extract_clauses(text)
    if not clauses:
        raise HTTPException(
            status_code=400,
            detail="No clauses found in document.",
        )

    request_id = str(uuid.uuid4())
    store.create_request(request_id, clauses)

    return {
        "request_id": request_id,
        "clauses": clauses,
        "total_clauses": len(clauses),
        "filename": file.filename,
    }
