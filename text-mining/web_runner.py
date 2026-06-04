import argparse
import contextlib
import io
import json
import sys
import warnings
from pathlib import Path

from extractor import extract_resume_info
from agents import build_job_profile, screen_candidate
from parser import parse_pdf_with_docling
from similarity import calculate_similarity


def _flatten_text(value):
    if isinstance(value, dict):
        flattened = []
        for item in value.values():
            text = _flatten_text(item)
            if text:
                flattened.append(text)
        return " ".join(flattened)

    if isinstance(value, list):
        return " ".join(
            text for item in value if (text := _flatten_text(item))
        )

    return str(value).strip() if value else ""


def build_fast_output(job_description, file_paths):
    job_profile = build_job_profile(job_description)
    resumes = []
    failed_files = []

    for file_path in file_paths:
        file_path_obj = Path(file_path)
        file_name = file_path_obj.name

        try:
            raw_text = parse_pdf_with_docling(file_path_obj)
            resume_info = extract_resume_info(raw_text)
            resume_info["file_name"] = file_name
            resume_info["full_text"] = raw_text
            resumes.append(resume_info)
        except Exception as exc:
            failed_files.append({"file_name": file_name, "error": str(exc)})

    if not resumes:
        raise RuntimeError("No resumes could be processed.")

    ranked_resumes = calculate_similarity(job_description, resumes)

    candidates = []
    for resume in ranked_resumes:
        education = resume.get("education", {})
        if not isinstance(education, dict):
            education = {
                "bachelor_edu": [],
                "master_edu": [],
                "phd_edu": [],
                "other_edu": [str(education).strip()] if str(education).strip() else [],
            }

        candidates.append(
            {
                "file_name": resume.get("file_name", ""),
                "similarity_score": resume.get("similarity_score", 0.0),
                "embedding_score": resume.get("embedding_score", 0.0),
                "skill_score": resume.get("skill_score", 0.0),
                "matched_skills": [str(item).strip() for item in resume.get("matched_skills", []) if str(item).strip()],
                "extracted_skills": [str(item).strip() for item in resume.get("extracted_skills", []) if str(item).strip()],
                "screening": None,  # To be filled later via Progressive Rendering
                "education": education,
                "experience": _flatten_text(resume.get("experience", "")),
                "projects": _flatten_text(resume.get("projects", "")),
                "certifications": _flatten_text(resume.get("certifications", "")),
                "achievements": _flatten_text(resume.get("achievements", "")),
                "languages": _flatten_text(resume.get("languages", "")),
                "summary": _flatten_text(resume.get("summary", "")),
                "email": _flatten_text(resume.get("email", "")),
                "phone_number": _flatten_text(resume.get("phone_number", "")),
                "location": _flatten_text(resume.get("location", "")),
                "full_text": _flatten_text(resume.get("full_text", "")),
            }
        )

    return {
        "job_profile": job_profile,
        "candidates": candidates,
        "total": len(candidates),
        "failed_files": failed_files,
    }

def build_output(job_description, file_paths):
    """Legacy synchronous function that does both fast parsing and slow screening."""
    output = build_fast_output(job_description, file_paths)
    
    for candidate in output["candidates"]:
        candidate["screening"] = screen_candidate(output["job_profile"], candidate)
        
    return output


def main():
    warnings.filterwarnings(
        "ignore",
        message=r"\[W008\] Evaluating Token.similarity based on empty vectors",
    )

    parser = argparse.ArgumentParser(description="Run TalentMatch text mining pipeline")
    parser.add_argument("--job-description", default="", help="Job description text")
    parser.add_argument("--files", nargs="+", required=True, help="List of PDF file paths")
    args = parser.parse_args()

    # Keep stdout reserved for final JSON payload.
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        output = build_output(args.job_description, args.files)

    captured_text = capture.getvalue().strip()
    if captured_text:
        print(captured_text, file=sys.stderr)

    print(json.dumps(output))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(1)
