from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.extract_text import extract_text_from_file
from app.core.clause_extractor import extract_clauses
from app.state.store import REQUEST_STORE

import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Received upload request for file: {file.filename}")

    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/png",
        "image/jpeg"
    ]:
        raise HTTPException(status_code=400, detail="File type not supported")

    content = await file.read()

    extracted_text = extract_text_from_file(content, file.content_type)
    if not extracted_text:
        raise HTTPException(status_code=500, detail="Failed to extract text")

    clauses = extract_clauses(extracted_text)

    request_id = str(uuid.uuid4())

    REQUEST_STORE[request_id] = {
        "filename": file.filename,
        "content_type": file.content_type,
        "clauses": clauses
    }

    logger.info(f"Upload successful | request_id={request_id}")

    return {
        "status": "success",
        "request_id": request_id,
        "filename": file.filename,
        "total_clauses": len(clauses)
    }
