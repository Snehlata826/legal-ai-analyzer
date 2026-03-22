# ⚖️ LexAnalyze — Legal Document Intelligence

AI-powered legal document analysis with **ML risk classification**, **SHAP explainability**, **RAG-based Q&A**, and **baseline comparison** — all running locally with a free Groq API key.

---

## What It Does

Upload any legal PDF and get:

| Feature | Technology |
|---|---|
| Clause extraction | spaCy NLP + regex fallback |
| Risk classification | Logistic Regression + Random Forest ensemble |
| Explainability | SHAP feature attribution (word-level) |
| Plain-English summaries | Groq LLaMA3 (free API) |
| Q&A chat | RAG pipeline + Groq |
| Baseline comparison | Keyword vs TF-IDF vs ML metrics |
| PDF report | fpdf2 |
| Security | Rate limiting, security headers, input validation |

---

## Quick Start (5 steps)

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com) (no credit card)

---

### Step 1 — Extract

```bash
unzip lexanalyze.zip
cd lexanalyze
```

Open the folder in VS Code:
```bash
code .
```

---

### Step 2 — Configure

```bash
cd backend
cp .env.example .env
```

Open `backend/.env` and set your Groq key:
```
GROQ_API_KEY=gsk_your_key_here
```

Get a free key at → https://console.groq.com

---

### Step 3 — Install backend

```bash
# Still inside backend/
python -m venv venv

# Mac / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

Optional — better clause extraction with spaCy:
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

---

### Step 4 — Train the ML classifier

```bash
python -m app.core.train_classifier
```

This prints a full precision / recall / F1 report and saves the model to `backend/models/risk_classifier.pkl`. It runs in under 10 seconds.

Example output:
```
  TEST SET EVALUATION — Ensemble Model
  ======================================
                precision  recall  f1-score
  HIGH           0.91      0.88     0.89
  MEDIUM         0.83      0.86     0.84
  LOW            0.94      0.95     0.94

  Accuracy:   0.8960
  Macro-F1:   0.8900

  BASELINE vs ML MODEL COMPARISON
  Keyword baseline       0.7200    0.6800
  Ensemble (LR + RF)     0.8960    0.8900
  Relative F1 improvement: +30.9%
```

---

### Step 5 — Run the servers

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate      # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8001
```

You should see:
```
INFO: Uvicorn running on http://0.0.0.0:8001
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser 🎉

---

## Using the App

### Upload a PDF
Drag-and-drop or click to upload any legal document (contracts, NDAs, terms of service, lease agreements, etc.)

### Clauses tab
- Every clause shown with **HIGH / MEDIUM / LOW** risk label
- ML confidence score (e.g. `92% conf`)
- Probability bars across all three classes
- SHAP feature tokens — which words drove the classification
- Plain-English summary from Groq LLaMA3
- Expandable original text + full SHAP attribution list

### Ask Questions tab
- Type any question about the document
- Gets answered using a RAG pipeline (relevant clauses → Groq)
- Source clauses shown for each answer

### Evaluate tab  ← new
- Click **Run Evaluation** to get:
  - ML ensemble accuracy / F1 / precision / recall
  - Side-by-side comparison with 3 baselines
  - Per-class metrics (HIGH / MEDIUM / LOW)
  - Confusion matrix
  - SHAP attribution cards for every clause

---

## Docker (alternative to manual setup)

```bash
# In the root lexanalyze/ folder:
docker compose up --build
```

Frontend → http://localhost:5173  
Backend  → http://localhost:8001

---

## Project Structure

```
lexanalyze/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point + middleware
│   │   ├── core/
│   │   │   ├── config.py              # All settings via .env
│   │   │   ├── security.py            # Rate limiting, headers, validation
│   │   │   ├── clause_extractor.py    # spaCy + regex clause extraction
│   │   │   ├── risk_analyzer.py       # Keyword-based fallback classifier
│   │   │   ├── risk_model.py          # ML ensemble (LR + RF) classifier
│   │   │   ├── shap_explainer.py      # SHAP feature attribution
│   │   │   ├── legal_dataset.py       # 90 labeled training examples
│   │   │   ├── train_classifier.py    # Training script
│   │   │   ├── baseline_nlp.py        # 3 baseline approaches
│   │   │   └── evaluator.py           # Metrics + comparison report
│   │   ├── routers/
│   │   │   ├── upload.py              # POST /upload
│   │   │   ├── simplify.py            # POST /simplify/{id}
│   │   │   ├── qa.py                  # POST /ask/
│   │   │   ├── report.py              # GET  /report/{id}
│   │   │   └── evaluate.py            # GET  /evaluate/{id}  ← new
│   │   ├── services/
│   │   │   ├── simplifier.py          # Groq simplification
│   │   │   └── pdf_report.py          # PDF generation
│   │   └── state/store.py             # In-memory request store
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Main app + 3 tabs
│   │   ├── components/
│   │   │   ├── ClauseCard.jsx         # Clause + ML probs + SHAP
│   │   │   ├── EvaluatePanel.jsx      # Metrics + baseline table ← new
│   │   │   ├── FileUploader.jsx       # PDF upload UI
│   │   │   ├── QAChat.jsx             # RAG chat interface
│   │   │   ├── RiskSummary.jsx        # Risk overview bar
│   │   │   └── Loader.jsx             # Loading states
│   │   ├── api/index.js               # All API calls
│   │   └── utils/riskSummary.js       # Risk calculation
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET`  | `/health` | Health check |
| `POST` | `/upload` | Upload PDF, extract clauses |
| `POST` | `/simplify/{id}` | ML classify + Groq simplify all clauses |
| `GET`  | `/report/{id}` | Download PDF report |
| `POST` | `/ask/` | Q&A via RAG |
| `GET`  | `/evaluate/{id}` | Full ML evaluation + SHAP + baselines |

---

## Configuration (backend/.env)

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | required | Free key from console.groq.com |
| `GROQ_DEFAULT_MODEL` | `llama3-8b-8192` | LLM model |
| `PORT` | `8001` | Backend port |
| `DEBUG` | `false` | Show API docs at /docs |
| `MAX_UPLOAD_SIZE_MB` | `10` | Max PDF size |
| `RATE_LIMIT_GLOBAL` | `60` | Requests per minute per IP |
| `RATE_LIMIT_UPLOAD` | `5` | Uploads per minute per IP |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins |

---

## Troubleshooting

**`GROQ_API_KEY is not set`**  
→ Create `backend/.env` from `.env.example` and add your key.

**`Cannot reach the backend server`**  
→ Make sure `uvicorn` is running on port 8001 and the venv is activated.

**`Module not found: shap`**  
→ `pip install shap` — the app falls back to keyword attribution without it.

**`spaCy model not found`** (warning, non-fatal)  
→ `pip install spacy && python -m spacy download en_core_web_sm`  
→ Without spaCy the app uses regex extraction (still works fine).

**PDF shows "Could not extract text"**  
→ Your PDF is scanned/image-based. The tool needs text-based PDFs.

---

## Disclaimer

For informational purposes only. Not legal advice. Always consult a qualified attorney for legal matters.
