from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover - optional dependency
    fitz = None


def _page_to_blocks(page) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []

    try:
        raw_blocks = page.get_text("blocks") or []
        for block in raw_blocks:
            if len(block) < 5:
                continue
            x0, y0, x1, y1, text = block[:5]
            text = str(text).strip()
            if not text:
                continue
            blocks.append(
                {
                    "x0": float(x0),
                    "y0": float(y0),
                    "x1": float(x1),
                    "y1": float(y1),
                    "text": text,
                }
            )
    except Exception:
        return []

    blocks.sort(key=lambda item: (item["y0"], item["x0"]))
    return blocks


def parse_pdf_layout_safe(pdf_path):
    """
    Extract text from PDF using PyMuPDF without Docling.
    This must not affect the old parser.
    Return:
    {
        "raw_text": str,
        "pages": [...],
        "success": bool,
        "error": str | None
    }
    """

    result = {"raw_text": "", "pages": [], "success": False, "error": None}

    if fitz is None:
        result["error"] = "PyMuPDF is not available."
        return result

    try:
        pdf_path = Path(pdf_path)
        doc = fitz.open(str(pdf_path))
        raw_pages: List[str] = []

        for page_index, page in enumerate(doc):
            page_payload = {"page": page_index + 1, "blocks": [], "text": ""}
            blocks = _page_to_blocks(page)

            if blocks:
                page_payload["blocks"] = blocks
                page_text = "\n".join(block["text"] for block in blocks)
            else:
                page_text = page.get_text("text") or ""
                page_payload["text"] = page_text.strip()

            page_text = str(page_text or "").strip()
            page_payload["text"] = page_text
            if page_text:
                raw_pages.append(page_text)
            result["pages"].append(page_payload)

        result["raw_text"] = "\n".join(raw_pages).strip()
        result["success"] = bool(result["raw_text"])
        if not result["success"]:
            result["error"] = "No extractable text found in PDF."
        return result
    except Exception as exc:
        result["error"] = str(exc)
        result["pages"] = []
        result["raw_text"] = ""
        result["success"] = False
        return result


def normalize_layout_text(layout):
    raw_text = ""
    pages = layout.get("pages") or []

    if pages:
        page_chunks = []
        for page in pages:
            blocks = page.get("blocks") or []
            if blocks:
                page_chunks.append("\n".join(block.get("text", "") for block in blocks if block.get("text")))
            else:
                text = page.get("text", "")
                if text:
                    page_chunks.append(text)
        raw_text = "\n".join(chunk for chunk in page_chunks if chunk).strip()

    if not raw_text:
        raw_text = str(layout.get("raw_text") or "").strip()

    return raw_text
