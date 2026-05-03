import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from docling.document_converter import DocumentConverter

app = FastAPI()

# Configure CORS for your Vue.js + Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change this to your Vite local server URL (e.g., "http://localhost:5173") in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Docling DocumentConverter
converter = DocumentConverter()

@app.post("/api/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save the uploaded file temporarily so Docling can process it from the file path
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(await file.read())
            tmp_path = tmp_file.name

        # Convert the document using Docling
        result = converter.convert(tmp_path)
        markdown_output = result.document.export_to_markdown()

        return {
            "filename": file.filename,
            "content": markdown_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Ensure the temporary file is deleted after processing
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)