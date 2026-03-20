"""
Main FastAPI application - Legal AI Analyzer
Upgraded with Groq API (free & fast)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .routers import upload, simplify, report, qa

app = FastAPI(
    title="Legal AI Analyzer API",
    description="AI-powered legal document analysis using Groq (free API)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["Upload"])
app.include_router(simplify.router, tags=["Simplify"])
app.include_router(report.router, tags=["Report"])
app.include_router(qa.router, tags=["Q&A"])


@app.get("/")
async def root():
    return {
        "message": "Legal AI Analyzer API v2.0",
        "powered_by": "Groq API (free & fast)",
        "endpoints": {
            "upload": "POST /upload",
            "simplify": "POST /simplify/{request_id}",
            "report": "GET /report/{request_id}",
            "ask": "POST /ask/"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
