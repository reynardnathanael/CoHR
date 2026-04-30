try:
    from docling.document_converter import DocumentConverter
except Exception:
    DocumentConverter = None

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None


def parse_pdf_with_docling(pdf_path):
    if DocumentConverter is not None:
        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        return result.document.export_to_markdown()

    if PdfReader is not None:
        reader = PdfReader(str(pdf_path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages).strip()

    raise ModuleNotFoundError(
        "No PDF parser available. Install docling or PyPDF2."
    )