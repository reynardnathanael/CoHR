from pathlib import Path


def load_pdf_files(data_dir):
    data_path = Path(data_dir)

    if not data_path.exists():
        raise FileNotFoundError(f"Folder not found: {data_dir}")

    pdf_files = sorted(data_path.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {data_dir}")

    return pdf_files