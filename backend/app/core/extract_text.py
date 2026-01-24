from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
from PIL import Image
import pytesseract
import io

def extract_text_from_file(content: bytes, content_type: str) -> str:
    try:
        # Handle PDF files
        if content_type == "application/pdf":
            # Verify PDF signature
            if content.startswith(b'%PDF-'):
                return extract_pdf_text(io.BytesIO(content)).strip()
            else:
                # Fallback if not real PDF - treat as text
                return content.decode('utf-8', errors='ignore').strip()

        # Handle DOCX files
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(io.BytesIO(content))
            return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()

        # Handle image files (OCR)
        elif content_type in ["image/png", "image/jpeg"]:
            image = Image.open(io.BytesIO(content))
            return pytesseract.image_to_string(image).strip()

        # Default / unknown case: treat as text
        return content.decode('utf-8', errors='ignore').strip()

    except Exception as e:
        print(f"[ERROR] Failed extracting text: {e}")
        raise RuntimeError(f"Text extraction failed: {str(e)}")
