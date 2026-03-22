# ⚙️ Setup Guide — Legal AI Analyzer v2.0

Follow these steps to run the project locally or with Docker.

---

## Option A — Local Development (recommended for first run)

### Prerequisites

| Tool | Minimum version | Check |
|------|----------------|-------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 8+ | `npm --version` |

---

### Step 1 — Get a free Groq API key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up (free, no credit card required)
3. Click **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_...`)

---

### Step 2 — Backend setup

```bash
# 1. Enter the backend directory
cd backend

# 2. Create a Python virtual environment
python -m venv venv

# 3. Activate it
#    Windows:
venv\Scripts\activate
#    Mac / Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create your .env file
cp .env.example .env

# 6. Open .env and paste your key:
#    GROQ_API_KEY=gsk_your_key_here

# 7. Start the server
uvicorn app.main:app --reload --port 8001
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

Test it: open [http://localhost:8001/health](http://localhost:8001/health)

---

### Step 3 — (Optional) Enable NLP entity extraction

spaCy improves clause extraction and identifies parties, dates, and amounts.

```bash
# Inside the backend venv
pip install spacy
python -m spacy download en_core_web_sm
```

Then restart the backend — it will auto-detect spaCy on startup.

---

### Step 4 — Frontend setup

Open a **new terminal** (keep the backend running):

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) 🎉

---

## Option B — Docker Compose

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Steps

```bash
# 1. Set up your .env
cp backend/.env.example backend/.env
# Edit backend/.env and add: GROQ_API_KEY=gsk_your_key_here

# 2. Build and start
docker compose up --build

# 3. Open the app
#    Frontend: http://localhost:5173
#    Backend:  http://localhost:8001
```

To stop:
```bash
docker compose down
```

---

## Configuration reference

All settings live in `backend/.env`. See `.env.example` for full documentation.

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | *(required)* | Your Groq API key |
| `GROQ_DEFAULT_MODEL` | `llama3-8b-8192` | LLM model to use |
| `GROQ_MAX_TOKENS` | `500` | Max tokens per response |
| `GROQ_TEMPERATURE` | `0.3` | Response creativity (0 = deterministic) |
| `PORT` | `8001` | Backend port |
| `ALLOWED_ORIGINS` | `http://localhost:5173,...` | Comma-separated CORS origins |
| `MAX_UPLOAD_SIZE_MB` | `10` | Maximum PDF upload size |
| `MAX_CLAUSES_PER_DOC` | `50` | Maximum clauses extracted per document |
| `DEBUG` | `false` | Enable FastAPI debug mode |

---

## Troubleshooting

**`GROQ_API_KEY is not set` error**
→ Make sure you created `backend/.env` (not just `.env.example`) and added your key.

**`Could not extract text from PDF`**
→ Your PDF is likely scanned/image-based. The tool requires text-based PDFs.
→ Try running the PDF through an OCR tool first (e.g. Adobe Acrobat, Tesseract).

**Frontend shows "Cannot reach the backend server"**
→ Confirm the backend is running on port 8001.
→ Check for firewall rules blocking localhost connections.

**`spaCy model not found` warning**
→ This is non-fatal — the app falls back to regex extraction automatically.
→ Install with: `pip install spacy && python -m spacy download en_core_web_sm`

---

## API quick reference

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | — | Health check |
| `POST` | `/upload` | `multipart/form-data` (`file`) | Upload PDF |
| `POST` | `/simplify/{id}` | — | Simplify + analyse clauses |
| `GET` | `/report/{id}` | — | Download PDF report |
| `POST` | `/ask/` | `{"request_id": "...", "question": "..."}` | Q&A chat |
