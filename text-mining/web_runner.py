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


def build_output(job_description, file_paths):
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
        screening = screen_candidate(job_profile, resume)
        candidates.append(
            {
                "file_name": resume.get("file_name", ""),
                "similarity_score": resume.get("similarity_score", 0.0),
                "embedding_score": resume.get("embedding_score", 0.0),
                "skill_score": resume.get("skill_score", 0.0),
                "matched_skills": resume.get("matched_skills", []),
                "extracted_skills": resume.get("extracted_skills", []),
                "screening": screening,
                "education": resume.get("education", ""),
                "experience": resume.get("experience", ""),
                "summary": resume.get("summary", ""),
                "email": resume.get("email", ""),
                "phone_number": resume.get("phone_number", ""),
                "location": resume.get("location", ""),
            }
        )

    return {
        "job_profile": job_profile,
        "candidates": candidates,
        "total": len(candidates),
        "failed_files": failed_files,
    }


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
