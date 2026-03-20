"""
PDF report generation — upgraded with attributions + entities
"""
from fpdf import FPDF
from typing import List, Dict, Any
from datetime import datetime
import os

OUTPUT_DIR = "temp_reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def safe_text(text) -> str:
    if isinstance(text, (bytes, bytearray)):
        return text.decode("utf-8", errors="ignore")
    return str(text)


def sanitize(text) -> str:
    text = safe_text(text)
    replacements = {
        '\u2013': '-', '\u2014': '--',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u2026': '...', '\u00a0': ' ',
        '\u2022': '*', '\u2122': '(TM)',
        '\u00ae': '(R)', '\u00a9': '(C)',
    }
    for u, a in replacements.items():
        text = text.replace(u, a)
    return text.encode("ascii", "replace").decode("ascii")


class LegalReportPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Legal AI Analyzer v2.0 | Page {self.page_no()} | Powered by Groq API", align="C")
        self.set_text_color(0, 0, 0)


def generate_pdf_report(request_id: str, results: List[Dict[str, Any]]) -> str:
    pdf = LegalReportPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, "LEGAL RISK ANALYSIS REPORT", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "Powered by Groq API (LLaMA3) + NLP Pipeline", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Report ID: {request_id}", ln=True)
    pdf.cell(0, 8, f"Generated: {datetime.now():%d %B %Y at %H:%M}", ln=True)
    pdf.cell(0, 8, f"Total Clauses: {len(results)}", ln=True)
    pdf.ln(5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)

    # Risk Summary
    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in results:
        risk_counts[r["risk"]] += 1

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "Risk Summary", ln=True)
    pdf.set_font("Arial", "", 10)

    colors = {
        "HIGH": (220, 53, 69),
        "MEDIUM": (255, 150, 0),
        "LOW": (40, 167, 69)
    }
    for risk, count in risk_counts.items():
        pdf.set_text_color(*colors[risk])
        pct = (count / len(results) * 100) if results else 0
        pdf.cell(0, 7, f"  {risk}: {count} clause(s) ({pct:.1f}%)", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    # Detailed Analysis
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "Detailed Clause Analysis", ln=True)
    pdf.ln(3)

    for i, r in enumerate(results, 1):
        if pdf.get_y() > 240:
            pdf.add_page()

        # Clause header
        risk = r["risk"]
        pdf.set_fill_color(*[c // 4 + 192 for c in colors[risk]])
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(*colors[risk])
        pdf.cell(0, 9, f"  Clause {i}  |  Risk: {risk}", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        # Original
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Original Text:", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 5, sanitize(r["original"][:350]))
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        # Simplified (Groq powered)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Plain English (AI-Simplified):", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, sanitize(r["simplified"]))
        pdf.ln(2)

        # Risk explanation
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Risk Explanation:", ln=True)
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, sanitize(r["explanation"]))
        pdf.ln(2)

        # Attributions (explainability)
        attributions = r.get("attributions", [])
        if attributions:
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 6, "Risk Keywords Found:", ln=True)
            pdf.set_font("Arial", "", 9)
            for attr in attributions:
                pdf.set_text_color(*colors.get(attr["risk_level"], (0, 0, 0)))
                pdf.cell(0, 5, f"  - '{attr['word']}': {attr['reason']}", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

        # Entities
        entities = r.get("entities", [])
        if entities:
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 6, "Identified Entities:", ln=True)
            pdf.set_font("Arial", "", 9)
            for ent in entities:
                pdf.cell(0, 5, f"  - {ent['text']} [{ent['description']}]", ln=True)
            pdf.ln(2)

        pdf.ln(4)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(6)

    file_path = os.path.join(OUTPUT_DIR, f"{request_id}.pdf")
    pdf.output(file_path)
    return file_path
