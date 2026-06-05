import os
import sys
import json
import tempfile
import traceback
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session


BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
TEXT_MINING_DIR = REPO_ROOT / "text-mining"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(TEXT_MINING_DIR) not in sys.path:
    sys.path.append(str(TEXT_MINING_DIR))

from database import engine, Base, get_db
import models  # This registers all your mapped models

# Create tables on startup if they don't already exist
Base.metadata.create_all(bind=engine)

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

def get_or_create_skill(db: Session, skill_name: str) -> models.Skill:
    sn = skill_name.strip()
    skill = db.query(models.Skill).filter(models.Skill.skill_name == sn).first()
    if not skill:
        skill = models.Skill(skill_name=sn)
        db.add(skill)
        db.commit()
        db.refresh(skill)
    return skill

def _save_upload_to_temp_file(file: UploadFile, content: bytes) -> str:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(content)
        return tmp_file.name


    # In-memory store for a precomputed analysis payload uploaded via CLI
    _LATEST_ANALYSIS = None


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
    job_title: str = Form("Uploaded Job"),
    job_description: str = Form(""),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    tmp_paths = []
    original_names = {}

    try:
        for file in files:
            t_path = _save_upload_to_temp_file(file, await file.read())
            tmp_paths.append(t_path)
            original_names[Path(t_path).name] = file.filename

        if not tmp_paths:
            raise HTTPException(
                status_code=400,
                detail="Upload at least one PDF resume.",
            )

        output = build_fast_output(job_description, tmp_paths)

        clean_description = "; ".join(
            line.lstrip("• ").strip() 
            for line in job_description.split("\n") if line.strip()
        )

        job_skills_text = ", ".join(output["job_profile"].get("must_have_skills", []))
        new_job = models.Job(
            title=job_title,
            job_description=clean_description,
            job_skills=job_skills_text
        )
        db.add(new_job); db.commit(); db.refresh(new_job)

        for skill_name in output["job_profile"].get("must_have_skills", []):
            skill_obj = get_or_create_skill(db, skill_name)
            db.add(models.JobSkill(job_id=new_job.job_id, skill_id=skill_obj.skill_id))
        db.commit()

        def safe_join(val):
            if isinstance(val, list): return "\n".join([str(v) for v in val])
            return str(val) if val else ""

        for c in output["candidates"]:
            # Map the temp file name back to the original uploaded file name
            t_name = c.get("file_name", "")
            orig_name = original_names.get(t_name, t_name)
            c["file_name"] = orig_name
            
            extracted_name = c.get("name")
            if not extracted_name:
                extracted_name = orig_name.replace(".pdf", "").replace(".PDF", "")
                # Convert underscores/dashes to spaces and capitalize
                extracted_name = extracted_name.replace("_", " ").replace("-", " ").title()

            # Pass the nicely formatted name back to the Vue frontend
            c["name"] = extracted_name

            new_profile = models.Profile(
                name=extracted_name,
                email=c.get("email", ""),
                phone=c.get("phone_number", "")
            )
            db.add(new_profile); db.commit(); db.refresh(new_profile)

            edu = c.get("education", {})
            new_resume = models.Resume(
                profile_id=new_profile.profile_id,
                raw_text=c.get("full_text", ""),
                summary=c.get("summary", ""),
                bachelor_education=safe_join(edu.get("bachelor_edu", [])),
                master_education=safe_join(edu.get("master_edu", [])),
                phd_education=safe_join(edu.get("phd_edu", [])),
                projects=safe_join(c.get("projects", [])),
                experience=safe_join(c.get("experience", []))
            )
            db.add(new_resume); db.commit(); db.refresh(new_resume)

            c["job_id"] = new_job.job_id
            c["resume_id"] = new_resume.resume_id

            for skill_name in c.get("extracted_skills", []):
                skill_obj = get_or_create_skill(db, skill_name)
                db.add(models.ResumeSkill(resume_id=new_resume.resume_id, skill_id=skill_obj.skill_id))
        db.commit()

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
async def run_agent(request: ScreenRequest, db: Session = Depends(get_db)):
    try:
        # This hits the Ollama agent strictly for ONE candidate
        screening_result = screen_candidate(request.job_profile, request.candidate)

        job_id = request.candidate.get("job_id")
        resume_id = request.candidate.get("resume_id")

        if job_id and resume_id:
            new_result = models.ScreeningResult(
                job_id=job_id,
                resume_id=resume_id,
                fit_category=screening_result.get("fit_category", ""),
                fit_score=float(screening_result.get("score", 0.0)),
                strengths=json.dumps(screening_result.get("strengths", [])),
                weakness=json.dumps(screening_result.get("weaknesses", [])),
                missing_requirements=json.dumps(screening_result.get("missing_requirements", [])),
                recommendation=screening_result.get("recommendation", ""),
                confidence=float(screening_result.get("confidence", 0.0))
            )
            db.add(new_result)
            db.commit()

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


@app.post("/api/upload-analysis")
async def upload_analysis(payload: Dict[str, Any]):
    """Accept a full analysis JSON (from web_runner.py) and store it in memory.

    This allows running the CLI `web_runner.py` locally and pushing the result
    to the backend so the frontend can fetch it from `/api/latest-analysis`.
    """
    global _LATEST_ANALYSIS
    _LATEST_ANALYSIS = payload
    return {"status": "ok", "total": len(payload.get("candidates", []))}


@app.get("/api/latest-analysis")
async def latest_analysis():
    if _LATEST_ANALYSIS is None:
        raise HTTPException(status_code=404, detail="No analysis uploaded yet")
    return _LATEST_ANALYSIS
