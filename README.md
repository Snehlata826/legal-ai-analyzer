# ⚖️ Legal AI Analyzer v2.0

An AI-powered legal document analysis system that extracts clauses, simplifies legal jargon into plain English, assigns risk levels, provides word-level explainability, and answers questions about your document — all using **Groq API** (free, no GPU needed).

---

## 🚀 What's New in v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Text Simplification | Rule-based regex | **Groq LLM (LLaMA3)** |
| Risk Analysis | Keyword matching | Keyword + explainability |
| Explainability | None | **Word-level attribution** |
| Named Entities | None | **spaCy NLP (parties, dates, amounts)** |
| Q&A System | None | **RAG pipeline with Groq** |
| API Cost | Free | **Free (Groq)** |

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11** — FastAPI, Uvicorn
- **Groq API** — Free LLaMA3 inference (no GPU)
- **spaCy** — Named entity recognition (optional)
- **pypdf** — PDF text extraction
- **fpdf2** — PDF report generation

### Frontend
- **React 18** + **Vite**
- Plain CSS — no UI libraries needed

### AI Pipeline
```
PDF Upload
    ↓
Clause Extraction (spaCy / regex)
    ↓
Risk Classification (keyword matching + explainability)
    ↓
Text Simplification (Groq LLaMA3 API)
    ↓
Q&A via RAG (semantic search + Groq)
    ↓
PDF Report Download
```

---

## 📁 Project Structure

```
legal-ai-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py                  ← FastAPI app entry point
│   │   ├── core/
│   │   │   ├── groq_client.py       ← Groq API wrapper (free LLM)
│   │   │   ├── clause_extractor.py  ← spaCy + regex extraction
│   │   │   ├── risk_analyzer.py     ← Risk classification + explainability
│   │   │   └── risk_explainer.py    ← Word-level attribution
│   │   ├── routers/
│   │   │   ├── upload.py            ← POST /upload
│   │   │   ├── simplify.py          ← POST /simplify/{id}
│   │   │   ├── report.py            ← GET  /report/{id}
│   │   │   └── qa.py                ← POST /ask/ (RAG Q&A)
│   │   ├── services/
│   │   │   ├── simplifier.py        ← Groq simplification service
│   │   │   └── pdf_report.py        ← PDF generation
│   │   └── state/
│   │       └── store.py             ← In-memory request store
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx                  ← Main app with tabs
    │   ├── components/
    │   │   ├── ClauseCard.jsx       ← Clause display with attributions
    │   │   ├── RiskSummary.jsx      ← Risk bar chart
    │   │   ├── QAChat.jsx           ← Chat interface (RAG)
    │   │   ├── FileUploader.jsx     ← PDF upload UI
    │   │   └── Loader.jsx           ← Loading spinner
    │   ├── api/index.js             ← API client
    │   └── utils/riskSummary.js     ← Risk calculation
    ├── package.json
    └── vite.config.js
```

---

## ⚙️ Installation & Setup

> Full step-by-step instructions are in **SETUP.md**

### Quick Start (3 steps)

**Step 1 — Get free Groq API key**
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up (free, no credit card)
3. Create an API key

**Step 2 — Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env → paste your GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

**Step 3 — Frontend**
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) 🎉

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload PDF, extract clauses |
| `POST` | `/simplify/{id}` | Simplify + risk analyse all clauses |
| `GET`  | `/report/{id}` | Download PDF report |
| `POST` | `/ask/` | Ask questions about the document |
| `GET`  | `/health` | Health check |

### Example Q&A Request
```json
POST /ask/
{
  "request_id": "your-request-id",
  "question": "What is the monthly payment amount?"
}
```

### Example Q&A Response
```json
{
  "answer": "The monthly fee is INR 50,000 as stated in Clause 3.",
  "sources": [
    {
      "clause": "Party B agrees to pay Party A a monthly fee of INR 50,000...",
      "relevance_score": 0.847
    }
  ]
}
```

---

## 🎯 Risk Levels

| Level | Keywords | Example |
|-------|----------|---------|
| 🔴 HIGH | indemnify, liability, termination, breach, damages, waiver, disclaimer | "Party B shall indemnify Party A against all losses" |
| 🟡 MEDIUM | arbitration, jurisdiction, confidential, force majeure, amendment | "Disputes resolved through binding arbitration" |
| 🟢 LOW | entire agreement, severability, headings, counterparts | "This document constitutes the entire agreement" |

---

## 💡 How the RAG Pipeline Works

```
User Question
     ↓
Semantic Search
(find most relevant clauses using cosine similarity)
     ↓
Context Building
(top 3 relevant clauses sent as context)
     ↓
Groq LLaMA3 API
(generates answer grounded in document)
     ↓
Answer + Source Citations
```

---

## ⚠️ Disclaimer

This tool is for **informational purposes only** and does **not** constitute legal advice. Always consult a qualified attorney for legal matters.

---

## 📄 License

MIT License — free for personal and commercial use.
