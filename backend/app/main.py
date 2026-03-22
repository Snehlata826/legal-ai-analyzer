"""
Main FastAPI application — Legal AI Analyzer v2.0
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .core.config import settings
from .core.security import SecurityHeadersMiddleware, RateLimitMiddleware, RequestLoggingMiddleware
from .routers import upload, simplify, report, qa, evaluate

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lexanalyze")

settings.validate()
logger.info("Starting %s v%s", settings.app_name, settings.app_version)

app = FastAPI(
    title=settings.app_name,
    description="AI-powered legal document analysis using Groq + ML classifier",
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

app.add_middleware(CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(upload.router,   tags=["Upload"])
app.include_router(simplify.router, tags=["Simplify"])
app.include_router(report.router,   tags=["Report"])
app.include_router(qa.router,       tags=["Q&A"])
app.include_router(evaluate.router, tags=["Evaluate"])

@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name} API {settings.app_version}",
        "endpoints": {
            "upload":   "POST /upload",
            "simplify": "POST /simplify/{request_id}",
            "report":   "GET  /report/{request_id}",
            "ask":      "POST /ask/",
            "evaluate": "GET  /evaluate/{request_id}",
        },
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}
