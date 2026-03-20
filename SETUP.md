# 🛠️ SETUP GUIDE — Legal AI Analyzer v2.0

Follow every step carefully. This guide works on Windows, Mac, and Linux.

---

## BEFORE YOU START — Prerequisites

Install these if you don't have them:

| Tool | Download | Check if installed |
|------|----------|--------------------|
| Python 3.11 | https://python.org/downloads | `python --version` |
| Node.js 18+ | https://nodejs.org | `node --version` |
| Git | https://git-scm.com | `git --version` |

---

## STEP 1 — Get Your FREE Groq API Key

Groq is completely free. No credit card needed.

1. Open your browser → go to **https://console.groq.com**
2. Click **Sign Up** (use Google or email)
3. After login → click **API Keys** in left sidebar
4. Click **Create API Key**
5. Give it a name like `legal-ai`
6. **Copy the key** — you only see it once!
7. Save it somewhere safe (Notepad, etc.)

> Your key looks like: `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## STEP 2 — Extract the Project

If you received a ZIP file:

**Windows:**
- Right-click the ZIP → Extract All
- Choose a location like `C:\Projects\`

**Mac/Linux:**
```bash
unzip legal-ai-analyzer.zip
cd legal-ai-analyzer
```

---

## STEP 3 — Backend Setup

Open a terminal (Command Prompt / PowerShell on Windows, Terminal on Mac/Linux).

### 3a. Go to backend folder
```bash
cd legal-ai-analyzer/backend
```

### 3b. Create virtual environment
```bash
python -m venv venv
```

### 3c. Activate virtual environment

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line. ✅

### 3d. Install Python packages
```bash
pip install -r requirements.txt
```

This installs: FastAPI, Uvicorn, Groq, pypdf, fpdf2, numpy, python-dotenv.

> ⏱️ Takes 1-3 minutes depending on internet speed.

### 3e. Create your .env file

**Windows:**
```bash
copy .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

Now open `.env` in any text editor (Notepad, VS Code, etc.) and replace:
```
GROQ_API_KEY=your_groq_api_key_here
```
with your actual key:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Save the file.

### 3f. (Optional) Install spaCy for better NLP

spaCy improves clause extraction but is optional.

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

> Skip this if your internet is slow — the app works without it.

### 3g. Start the backend server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ **Backend is running! Keep this terminal open.**

---

## STEP 4 — Frontend Setup

Open a **NEW terminal window** (keep the backend terminal running).

### 4a. Go to frontend folder
```bash
cd legal-ai-analyzer/frontend
```

### 4b. Install Node packages
```bash
npm install
```

> ⏱️ Takes 1-2 minutes.

### 4c. Start the frontend
```bash
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

✅ **Frontend is running!**

---

## STEP 5 — Open the App

Open your browser and go to:
```
http://localhost:5173
```

You should see the **Legal AI Analyzer** homepage! 🎉

---

## STEP 6 — Test the App

1. Click the upload box
2. Select any PDF legal document (or use the sample in `backend/contract_sample.txt` — copy to PDF)
3. Wait for analysis (10-30 seconds depending on document size)
4. Browse analysed clauses with risk levels
5. Click **Ask Questions** tab
6. Ask: *"What is the payment amount?"*
7. Click **Download PDF Report**

---

## ❌ Troubleshooting

### "GROQ_API_KEY not set" error
- Make sure you created `.env` file (not `.env.example`)
- Check the key is correct with no extra spaces
- Restart the backend server after editing `.env`

### "ModuleNotFoundError" error
- Make sure your virtual environment is activated (you see `(venv)`)
- Run `pip install -r requirements.txt` again

### "CORS error" in browser
- Make sure backend is running on port 8000
- Make sure frontend is running on port 5173
- Don't use different ports

### "Port already in use" error
**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <pid_number> /F
```

**Mac/Linux:**
```bash
lsof -i :8000
kill -9 <pid_number>
```

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
```
The app works without it — it falls back to regex extraction.

### npm install fails
- Make sure Node.js 18+ is installed: `node --version`
- Try: `npm install --legacy-peer-deps`

---

## 🔄 Stopping the App

Press `Ctrl + C` in both terminal windows.

## 🔄 Restarting Later

Every time you want to use the app:

**Terminal 1 (Backend):**
```bash
cd legal-ai-analyzer/backend
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd legal-ai-analyzer/frontend
npm run dev
```

---

## 📊 Verify Everything is Working

Open: http://localhost:8000/docs

You should see the **Swagger UI** with all API endpoints listed. This confirms the backend is healthy.

---

## 🚀 What the App Does

| Step | What Happens |
|------|-------------|
| 1. Upload PDF | Text extracted, clauses identified |
| 2. Analysis | Each clause simplified by Groq LLaMA3 |
| 3. Risk tags | HIGH / MEDIUM / LOW assigned per clause |
| 4. Explainability | Shows WHICH words caused the risk rating |
| 5. Entities | Parties, dates, amounts identified |
| 6. Q&A | Ask any question, RAG pipeline answers from document |
| 7. Report | Download full PDF analysis report |

---

## 💡 Interview Tips

When asked about the tech stack, say:

> "The backend uses FastAPI with Groq API — which provides free access to LLaMA3 for text simplification. The risk classification uses keyword-based analysis with word-level attribution for explainability. The Q&A feature implements a RAG pipeline — we do semantic search over clauses using cosine similarity, then pass the top 3 relevant clauses as context to Groq's LLaMA3 to generate a grounded answer."

---

*Legal AI Analyzer v2.0 — For informational purposes only. Not legal advice.*
