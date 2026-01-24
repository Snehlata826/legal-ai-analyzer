from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.core.extract_text import extract_text_from_file
from app.core.clause_extractor import extract_clauses
from app.embeddings.embedder import EmbeddingEngine

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["File Upload"])


# Temporary in-memory store (MVP)
request_state = {}


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Received upload request for file: {file.filename}, content_type: {file.content_type}")
    
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/png",
        "image/jpeg"
    ]:
        logger.warning(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="File type not supported")
    
    content = await file.read()
    logger.info(f"File size: {len(content)} bytes")
    
    extracted_text = extract_text_from_file(content, file.content_type)
    logger.info(f"Extracted text length: {len(extracted_text)} characters")
    
    if not extracted_text:
        logger.error("Failed to extract text from file")
        raise HTTPException(status_code=500, detail="Failed to extract text")

    # Extract clauses
    clauses = extract_clauses(extracted_text)
    logger.info(f"Extracted {len(clauses)} clauses")

    # Embed chunks
    embedder = EmbeddingEngine()
    chunks = embedder.chunk(extracted_text)
    vectors = embedder.embed(chunks)

    # Save global state (prototype)
    request_state["chunks"] = chunks
    request_state["vectors"] = vectors

    logger.info("Upload + Embedding successful")

    return JSONResponse({
        "filename": file.filename,
        "content_type": file.content_type,
        "clauses": clauses,
        "chunks_count": len(chunks)
    })
