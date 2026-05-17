from pathlib import Path

# Try pymupdf4llm (preferred)
try:
    from pymupdf4llm import LLM
    _llm = LLM()
except Exception:
    _llm = None

# Fallback: PyMuPDF
try:
    import fitz  # pymupdf
except Exception:
    fitz = None


def parse_pdf_with_docling(pdf_path):
    """
    Parse PDF using pymupdf4llm first, fallback to PyMuPDF.
    """

    pdf_path = Path(pdf_path)
    text_path = pdf_path.with_suffix(".txt")

    # If cached txt exists
    if text_path.exists():
        return text_path.read_text(encoding="utf-8", errors="ignore")

    # Preferred: pymupdf4llm
    if _llm is not None:
        try:
            text = _llm.read_pdf(str(pdf_path))
            return text
        except Exception as e:
            print("pymupdf4llm failed, fallback to PyMuPDF:", e)

    # Fallback: PyMuPDF
    if fitz is not None:
        doc = fitz.open(str(pdf_path))
        text = []
        for page in doc:
            text.append(page.get_text())
        return "\n".join(text)

    raise ModuleNotFoundError(
        "No PDF parser available. Install pymupdf4llm or pymupdf."
    )
