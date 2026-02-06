"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import upload, simplify, report

# Initialize FastAPI app
app = FastAPI(
    title="Legal AI Analyzer API",
    description="Backend API for legal document analysis",
    version="1.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:8000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, tags=["Upload"])
app.include_router(simplify.router, tags=["Simplify"])
app.include_router(report.router, tags=["Report"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Legal AI Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /upload",
            "simplify": "POST /simplify/{request_id}",
            "report": "GET /report/{request_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
