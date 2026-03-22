# ── Legal AI Analyzer — Backend Dockerfile ──────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (required for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional: install spaCy model if you want NLP entity extraction
# RUN python -m spacy download en_core_web_sm

# Copy application source
COPY . .

# Create report output directory
RUN mkdir -p temp_reports

EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
