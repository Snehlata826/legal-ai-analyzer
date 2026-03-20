"""
Compact & Professional PDF report generation service
"""

from fpdf import FPDF
from typing import List, Dict, Any
from datetime import datetime
import os

OUTPUT_DIR = "temp_reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# TEXT SAFETY HELPERS
# =========================

def safe_text(text) -> str:
    if isinstance(text, (bytes, bytearray)):
        return text.decode("utf-8", errors="ignore")
    return str(text)


def sanitize_text(text) -> str:
    text = safe_text(text)

    replacements = {
        '\u2013': '-', '\u2014': '--',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u2026': '...', '\u00a0': ' ',
        '\u2022': '*', '\u00b7': '*',
        '\u2122': '(TM)', '\u00ae': '(R)',
        '\u00a9': '(C)', '\u00ab': '<<',
        '\u00bb': '>>', '\u2192': '->',
        '\u2190': '<-',
    }

    for u, a in replacements.items():
        text = text.replace(u, a)

    return text.encode("ascii", "replace").decode("ascii")


# =========================
# PDF CLASS
# =========================

class LegalReportPDF(FPDF):

    def header(self):
        self.set_font("Arial", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "Legal AI Analyzer", align="R")
        self.ln(8)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)


# =========================
# MAIN PDF GENERATOR
# =========================

def generate_pdf_report(
    request_id: str,
    results: List[Dict[str, Any]]
) -> str:

    pdf = LegalReportPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    # =====================================
    # TITLE
    # =====================================
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "LEGAL RISK ANALYSIS REPORT", ln=True, align="C")

    pdf.ln(4)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # =====================================
    # METADATA SECTION (Compact)
    # =====================================
    pdf.set_font("Arial", "", 10)

    pdf.cell(35, 6, "Report ID:")
    pdf.cell(0, 6, request_id, ln=True)

    pdf.cell(35, 6, "Generated On:")
    pdf.cell(0, 6, f"{datetime.now():%d %B %Y}", ln=True)

    pdf.cell(35, 6, "Total Clauses:")
    pdf.cell(0, 6, str(len(results)), ln=True)

    pdf.ln(5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # =====================================
    # RISK SUMMARY
    # =====================================
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, "RISK SUMMARY", ln=True)
    pdf.ln(3)

    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in results:
        risk_counts[r["risk"]] += 1

    pdf.set_font("Arial", "", 10)

    for risk in ["HIGH", "MEDIUM", "LOW"]:
        count = risk_counts[risk]

        if risk == "HIGH":
            pdf.set_text_color(220, 53, 69)
        elif risk == "MEDIUM":
            pdf.set_text_color(255, 140, 0)
        else:
            pdf.set_text_color(40, 167, 69)

        pdf.cell(30, 6, risk)
        pdf.cell(0, 6, f"{count} clause(s)", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    # =====================================
    # DETAILED ANALYSIS
    # =====================================
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, "DETAILED ANALYSIS", ln=True)
    pdf.ln(4)

    for i, r in enumerate(results, 1):

        # Clause Header
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, f"Clause {i}", ln=True)

        # Risk Level
        pdf.set_font("Arial", "", 9)
        pdf.cell(25, 5, "Risk:")

        if r["risk"] == "HIGH":
            pdf.set_text_color(220, 53, 69)
        elif r["risk"] == "MEDIUM":
            pdf.set_text_color(255, 140, 0)
        else:
            pdf.set_text_color(40, 167, 69)

        pdf.cell(0, 5, r["risk"], ln=True)
        pdf.set_text_color(0, 0, 0)

        pdf.ln(2)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)

        # Original Clause
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 5, "Original Clause", ln=True)

        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, sanitize_text(r["original"]))
        pdf.ln(2)

        # Simplified Clause
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 5, "Simplified Explanation", ln=True)

        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, sanitize_text(r["simplified"]))
        pdf.ln(2)

        # Risk Explanation
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 5, "Risk Explanation", ln=True)

        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, sanitize_text(r["explanation"]))
        pdf.ln(6)

    # =====================================
    # SAVE FILE
    # =====================================
    file_path = os.path.join(OUTPUT_DIR, f"{request_id}.pdf")
    pdf.output(file_path)

    return file_path