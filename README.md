# Legal AI Analyzer

A production-ready web application that analyzes legal documents, extracts clauses, simplifies legal jargon into plain English, and assigns risk levels to each clause.

## Features

- 📄 **PDF Upload**: Upload legal documents in PDF format
- 🔍 **Clause Extraction**: Automatically extracts clauses from legal documents
- 💡 **Plain English Translation**: Simplifies legal jargon using rule-based logic
- ⚠️ **Risk Analysis**: Assigns HIGH, MEDIUM, or LOW risk levels to each clause
- 📊 **Visual Risk Summary**: See risk distribution at a glance
- 📥 **PDF Report Generation**: Download a comprehensive analysis report
- 🖥️ **Local & Offline**: Runs completely on your Windows machine

## Tech Stack

### Backend
- **Python 3.11**
- **FastAPI** - Modern web framework
- **pypdf** - PDF text extraction
- **fpdf2** - PDF report generation
- **Uvicorn** - ASGI server

### Frontend
- **React 18** (Vite)
- **Plain CSS** - No external UI libraries
- **Fetch API** - Backend communication

## Project Structure

```
legal-ai-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── state/
│   │   │   └── store.py         # In-memory request storage
│   │   ├── routers/
│   │   │   ├── upload.py        # PDF upload endpoint
│   │   │   ├── simplify.py      # Simplification endpoint
│   │   │   └── report.py        # Report generation endpoint
│   │   ├── services/
│   │   │   ├── simplifier.py    # Text simplification logic
│   │   │   └── pdf_report.py    # PDF generation service
│   │   └── core/
│   │       ├── clause_extractor.py  # Clause extraction
│   │       ├── risk_analyzer.py     # Risk assessment
│   │       └── risk_explainer.py    # Risk explanations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUploader.jsx     # File upload UI
│   │   │   ├── ClauseCard.jsx       # Clause display card
│   │   │   ├── RiskSummary.jsx      # Risk visualization
│   │   │   └── Loader.jsx           # Loading indicator
│   │   ├── api/
│   │   │   └── index.js             # API client
│   │   ├── utils/
│   │   │   └── riskSummary.js       # Risk calculation
│   │   ├── App.jsx                  # Main application
│   │   ├── main.jsx                 # Entry point
│   │   └── index.css                # Styles
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Installation & Setup

### Prerequisites

- **Python 3.11** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))

### Step 1: Clone or Extract the Project

```bash
cd legal-ai-analyzer
```

### Step 2: Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the backend server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   You should see:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   INFO:     Application startup complete.
   ```

   **Keep this terminal open** - the backend is now running.

### Step 3: Frontend Setup

1. **Open a NEW terminal** and navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Run the frontend development server**:
   ```bash
   npm run dev
   ```

   You should see:
   ```
   VITE v5.x.x  ready in xxx ms

   ➜  Local:   http://localhost:5173/
   ➜  Network: use --host to expose
   ```

4. **Open your browser** and go to:
   ```
   http://localhost:5173
   ```

## Usage

1. **Upload a PDF**: Click the upload box and select a legal PDF document
2. **Auto-Processing**: The app automatically:
   - Extracts clauses from the document
   - Simplifies each clause into plain English
   - Analyzes and assigns risk levels
3. **Review Results**: Browse through the analyzed clauses
4. **Download Report**: Click "Download PDF Report" to get a comprehensive analysis
5. **Analyze Another**: Click "Analyze Another Document" to start over

## API Endpoints

### Backend API (http://localhost:8000)

- **POST /upload** - Upload PDF document
  - Request: `multipart/form-data` with PDF file
  - Response: `{request_id, clauses, total_clauses}`

- **POST /simplify/{request_id}** - Simplify and analyze clauses
  - Response: `{request_id, results, total_processed}`

- **GET /report/{request_id}** - Generate PDF report
  - Response: PDF file download

- **GET /health** - Health check
  - Response: `{status: "healthy"}`

## Risk Levels

### HIGH Risk
Keywords: indemnification, liability, termination, penalties, breach, damages, waiver, exclusion, disclaimer

**Example**: "Party A shall indemnify Party B against all losses"
**Why High**: Could result in significant financial liability

### MEDIUM Risk
Keywords: arbitration, dispute resolution, jurisdiction, force majeure, confidentiality, amendments

**Example**: "Disputes shall be resolved through arbitration"
**Why Medium**: Affects how issues are handled but with less immediate financial impact

### LOW Risk
Keywords: general, standard, interpretation, severability, entire agreement

**Example**: "This agreement constitutes the entire understanding"
**Why Low**: Standard administrative clauses with minimal impact

## Troubleshooting

### Backend won't start
- Ensure Python 3.11 is installed: `python --version`
- Make sure virtual environment is activated
- Check if port 8000 is available: `netstat -an | findstr 8000`

### Frontend won't start
- Ensure Node.js is installed: `node --version`
- Delete `node_modules` and run `npm install` again
- Check if port 5173 is available

### Upload fails
- Ensure file is a valid PDF
- Check backend is running at http://localhost:8000
- Check browser console for CORS errors

### PDF report generation fails
- Ensure you've run the `/simplify` endpoint first
- Check backend logs for errors

## Development Notes

### Code Quality
- Clean, modular architecture with clear separation of concerns
- Type hints used throughout Python code
- Comprehensive error handling
- Production-ready code structure

### Performance
- Limits clause extraction to 50 clauses for optimal performance
- In-memory storage for fast access
- Efficient rule-based processing (no ML overhead)

### Security
- CORS configured for local development only
- File type validation on upload
- Input sanitization in text processing

## Future Enhancements

- [ ] Add support for DOCX files
- [ ] Implement persistent storage (SQLite/PostgreSQL)
- [ ] Add user authentication
- [ ] Export to JSON/Excel formats
- [ ] Add custom risk keyword configuration
- [ ] Implement clause comparison between documents
- [ ] Add historical analysis tracking

## License

MIT License - Feel free to use this project for personal or commercial purposes.

## Disclaimer

This tool is for informational purposes only and does not constitute legal advice. Always consult with a qualified attorney for legal matters.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review backend/frontend logs
3. Ensure all dependencies are properly installed

---

**Version**: 1.0.0  
**Author**: Full-Stack Engineering Team  
**Last Updated**: 2025
