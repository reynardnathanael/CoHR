import os
import sys
import tempfile
import traceback
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


REPO_ROOT = Path(__file__).resolve().parents[1]
TEXT_MINING_DIR = REPO_ROOT / "text-mining"

if str(TEXT_MINING_DIR) not in sys.path:
    sys.path.append(str(TEXT_MINING_DIR))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from extractor import extract_resume_info
from parser import parse_pdf_with_docling
from web_runner import build_output, build_fast_output
from agents import screen_candidate, generate_summary_agent


class ScreenRequest(BaseModel):
    job_profile: Dict[str, Any]
    candidate: Dict[str, Any]
    
class SummaryRequest(BaseModel):
    job_description: str
    resume_text: str

def _save_upload_to_temp_file(file: UploadFile, content: bytes) -> str:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(content)
        return tmp_file.name


@app.post("/api/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    tmp_path = None

    try:
        tmp_path = _save_upload_to_temp_file(file, await file.read())
        raw_text = parse_pdf_with_docling(tmp_path)
        extracted = extract_resume_info(raw_text)
        extracted["file_name"] = file.filename
        extracted["full_text"] = raw_text

        return {
            "filename": file.filename,
            "content": raw_text,
            "extracted": extracted,
        }
    except HTTPException:
        raise
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/api/analyze-resumes")
async def analyze_resumes(
    job_description: str = Form(""),
    files: List[UploadFile] = File(...),
):
    tmp_paths = []

    try:
        for file in files:
            tmp_paths.append(_save_upload_to_temp_file(file, await file.read()))

        if not tmp_paths:
            raise HTTPException(
                status_code=400,
                detail="Upload at least one PDF resume.",
            )

        output = build_output(job_description, tmp_paths)
        output["job_description"] = job_description
        return output
    except HTTPException:
        raise
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        for tmp_path in tmp_paths:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


@app.post("/api/analyze-fast")
async def analyze_fast(
    job_description: str = Form(""),
    files: List[UploadFile] = File(...),
):
    tmp_paths = []

    try:
        for file in files:
            tmp_paths.append(_save_upload_to_temp_file(file, await file.read()))

        if not tmp_paths:
            raise HTTPException(
                status_code=400,
                detail="Upload at least one PDF resume.",
            )

        output = build_fast_output(job_description, tmp_paths)
        output["job_description"] = job_description
        return output
    except HTTPException:
        raise
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        for tmp_path in tmp_paths:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


@app.post("/api/screen-candidate")
async def run_agent(request: ScreenRequest):
    try:
        # This hits the Ollama agent strictly for ONE candidate
        screening_result = screen_candidate(request.job_profile, request.candidate)
        return {"screening": screening_result}
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/api/generate-summary")
async def generate_summary(request: SummaryRequest):
    try:
        result = generate_summary_agent(request.resume_text, request.job_description)
        return {"summary": result}
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
