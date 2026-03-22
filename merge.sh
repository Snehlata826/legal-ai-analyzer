#!/usr/bin/env bash
# =============================================================
#  LexAnalyze — Merge Script
#  Copies all new/updated files from this package into your
#  existing project directory.
#
#  Usage:
#    chmod +x merge.sh
#    ./merge.sh /path/to/your/existing/project
#
#  If no path is given, merges into the current directory.
# =============================================================
set -e

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${1:-$(pwd)}"

echo ""
echo "  LexAnalyze Merge Script"
echo "  Source : $SRC"
echo "  Target : $DEST"
echo ""

if [ ! -d "$DEST" ]; then
  echo "  ERROR: Target directory does not exist: $DEST"
  exit 1
fi

# ── Backend files ─────────────────────────────────────────────────
echo "  Copying backend files…"

mkdir -p "$DEST/backend/app/"{core,routers,services,state,embeddings,api/v1}
mkdir -p "$DEST/backend/models"          # for saved ML model
mkdir -p "$DEST/backend/temp_reports"    # for PDF reports

BACKEND_FILES=(
  "backend/app/__init__.py"
  "backend/app/main.py"
  "backend/app/core/__init__.py"
  "backend/app/core/config.py"
  "backend/app/core/security.py"
  "backend/app/core/groq_client.py"
  "backend/app/core/clause_extractor.py"
  "backend/app/core/clause_classifier.py"
  "backend/app/core/risk_analyzer.py"
  "backend/app/core/risk_explainer.py"
  "backend/app/core/risk_model.py"
  "backend/app/core/shap_explainer.py"
  "backend/app/core/legal_dataset.py"
  "backend/app/core/train_classifier.py"
  "backend/app/core/baseline_nlp.py"
  "backend/app/core/evaluator.py"
  "backend/app/routers/__init__.py"
  "backend/app/routers/upload.py"
  "backend/app/routers/simplify.py"
  "backend/app/routers/qa.py"
  "backend/app/routers/report.py"
  "backend/app/routers/evaluate.py"
  "backend/app/services/__init__.py"
  "backend/app/services/simplifier.py"
  "backend/app/services/pdf_report.py"
  "backend/app/state/__init__.py"
  "backend/app/state/store.py"
  "backend/app/embeddings/__init__.py"
  "backend/app/embeddings/embedder.py"
  "backend/app/api/__init__.py"
  "backend/app/api/v1/__init__.py"
  "backend/requirements.txt"
  "backend/.env.example"
  "backend/Dockerfile"
)

for f in "${BACKEND_FILES[@]}"; do
  if [ -f "$SRC/$f" ]; then
    cp "$SRC/$f" "$DEST/$f"
    echo "    ✓ $f"
  else
    echo "    ✗ MISSING in source: $f"
  fi
done

# ── Frontend files ────────────────────────────────────────────────
echo ""
echo "  Copying frontend files…"

mkdir -p "$DEST/frontend/src/"{components,api,utils}

FRONTEND_FILES=(
  "frontend/index.html"
  "frontend/package.json"
  "frontend/vite.config.js"
  "frontend/Dockerfile"
  "frontend/src/main.jsx"
  "frontend/src/App.jsx"
  "frontend/src/index.css"
  "frontend/src/api/index.js"
  "frontend/src/utils/riskSummary.js"
  "frontend/src/components/Loader.jsx"
  "frontend/src/components/FileUploader.jsx"
  "frontend/src/components/ClauseCard.jsx"
  "frontend/src/components/RiskSummary.jsx"
  "frontend/src/components/QAChat.jsx"
  "frontend/src/components/EvaluatePanel.jsx"
)

for f in "${FRONTEND_FILES[@]}"; do
  if [ -f "$SRC/$f" ]; then
    cp "$SRC/$f" "$DEST/$f"
    echo "    ✓ $f"
  else
    echo "    ✗ MISSING in source: $f"
  fi
done

# ── Root files ────────────────────────────────────────────────────
echo ""
echo "  Copying root files…"

ROOT_FILES=("docker-compose.yml" "SETUP.md" ".gitignore")
for f in "${ROOT_FILES[@]}"; do
  if [ -f "$SRC/$f" ]; then
    cp "$SRC/$f" "$DEST/$f"
    echo "    ✓ $f"
  fi
done

echo ""
echo "  ✅  Merge complete!"
echo ""
echo "  Next steps:"
echo "  ─────────────────────────────────────────────────────"
echo "  1. cd $DEST/backend"
echo "     cp .env.example .env"
echo "     # Add your GROQ_API_KEY to .env"
echo ""
echo "  2. python -m venv venv && source venv/bin/activate"
echo "     pip install -r requirements.txt"
echo ""
echo "  3. python -m app.core.train_classifier"
echo "     # Trains ML model, prints precision/recall/F1"
echo ""
echo "  4. uvicorn app.main:app --reload --port 8001"
echo ""
echo "  5. cd $DEST/frontend"
echo "     npm install && npm run dev"
echo ""
echo "  6. Open http://localhost:5173"
echo "  ─────────────────────────────────────────────────────"
echo ""
