from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers.upload import router as upload_router
from app.routers.qa import router as qa_router
from app.routers.simplify import router as simplify_router
import logging

app = FastAPI(
    title="Legal AI Analyzer",
    description="AI-powered contract analyzer that extracts clauses, embeddings, chunks, & more.",
    version="1.0.0"
)

# CORS (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload_router)
app.include_router(qa_router)
app.include_router(simplify_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Welcome to Legal AI Analyzer API!"}
