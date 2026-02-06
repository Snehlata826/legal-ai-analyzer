"""
PDF report generation service
"""
from fpdf import FPDF
from typing import List, Dict, Any
from datetime import datetime
import os

OUTPUT_DIR = "temp_reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------------
# Helpers
# -------------------------
def safe_text(text) -> str:
    """Ensure text is always a safe string."""
    if isinstance(text, (bytes, bytearray)):
        return text.decode("utf-8", errors="ignore")
    return str(text)


def sanitize_text(text) -> str:
    """Replace unsupported Unicode characters."""
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

    # Final ASCII safety pass
    return text.encode("ascii", "replace").decode("ascii")


# -------------------------
# PDF Class
# -------------------------
class LegalReportPDF(FPDF):


    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


# -------------------------
# Main Generator
# -------------------------
def generate_pdf_report(
    request_id: str,
    results: List[Dict[str, Any]]
) -> str:
    """
    Generate PDF report and save to disk.

    Returns:
        Path to generated PDF file
    """
    pdf = LegalReportPDF()
    pdf.add_page()

# --- Cover Section ---
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, "LEGAL RISK ANALYSIS REPORT", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Report ID: {request_id}", ln=True, align="C")
    pdf.cell(0, 8, f"Generated on: {datetime.now():%d %B %Y}", ln=True)
    pdf.cell(0, 8, f"Total Clauses Analyzed: {len(results)}", ln=True)
    pdf.ln(5)

    pdf.ln(12)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(15)



    # Risk summary
    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in results:
        risk_counts[r["risk"]] += 1

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Risk Summary", ln=True)
    pdf.set_font("Arial", "", 10)

    for risk, count in risk_counts.items():
        color = {
            "HIGH": (220, 53, 69),
            "MEDIUM": (255, 193, 7),
            "LOW": (40, 167, 69),
        }[risk]

        pdf.set_text_color(*color)
        pdf.cell(0, 8, f"{risk}: {count} clause(s)", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    # Clause details
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Detailed Analysis", ln=True)
    pdf.ln(5)

    for i, r in enumerate(results, 1):
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"Clause {i} - Risk: {r['risk']}", ln=True)

        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Original:", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, sanitize_text(r["original"][:300]))

        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Simplified:", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, sanitize_text(r["simplified"]))

        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Risk Explanation:", ln=True)
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, sanitize_text(r["explanation"]))

        pdf.ln(5)
        if pdf.get_y() > 250:
            pdf.add_page()

    file_path = os.path.join(OUTPUT_DIR, f"{request_id}.pdf")
    pdf.output(file_path)
    return file_path
