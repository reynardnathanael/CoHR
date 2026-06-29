import argparse
import contextlib
import io
import json
import sys
import warnings
from pathlib import Path

from extractor import extract_resume_info
from agents import build_job_profile, parse_resume_agent, screen_candidate
from parser import parse_pdf_with_docling
from similarity import calculate_similarity
from pdf_parser_safe import normalize_layout_text, parse_pdf_layout_safe
from resume_merger import merge_resume_outputs
from resume_schema import validate_resume_schema


USE_HYBRID_RESUME_PARSER = True


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
            if USE_HYBRID_RESUME_PARSER:
                try:
                    layout = parse_pdf_layout_safe(file_path_obj)
                    if layout.get("success") and str(layout.get("raw_text", "")).strip():
                        raw_text = normalize_layout_text(layout)
                    else:
                        raw_text = parse_pdf_with_docling(file_path_obj)
                    deterministic_info = extract_resume_info(raw_text)
                    llm_info = parse_resume_agent(raw_text, deterministic_info=deterministic_info)
                    merged_info = merge_resume_outputs(deterministic_info, llm_info, raw_text)
                    resume_info = validate_resume_schema(merged_info)
                except Exception:
                    raw_text = parse_pdf_with_docling(file_path_obj)
                    resume_info = extract_resume_info(raw_text)
                    llm_info = parse_resume_agent(raw_text, deterministic_info=resume_info)
                    resume_info["llm_resume"] = llm_info
            else:
                raw_text = parse_pdf_with_docling(file_path_obj)
                resume_info = extract_resume_info(raw_text)
                llm_info = parse_resume_agent(raw_text, deterministic_info=resume_info)
                resume_info["llm_resume"] = llm_info

            resume_info["file_name"] = file_name
            resume_info["full_text"] = raw_text
            if "llm_resume" not in resume_info:
                resume_info["llm_resume"] = llm_info
            resume_info["extraction"] = {"source": "hybrid_parser" if USE_HYBRID_RESUME_PARSER else "legacy_parser", "resume": resume_info.get("llm_resume", {})}
            resumes.append(resume_info)
        except Exception as exc:
            failed_files.append({"file_name": file_name, "error": str(exc)})

    if not resumes:
        raise RuntimeError("No resumes could be processed.")

    ranked_resumes = calculate_similarity(job_description, resumes)

    candidates = []
    raw_for_screening = []
    for resume in ranked_resumes:
        llm_resume = resume.get("llm_resume", {}) or {}
        education = llm_resume.get("education") if isinstance(llm_resume, dict) else {}
        if not isinstance(education, dict):
            education = resume.get("education", {})
        if not isinstance(education, dict):
            education = {
                "bachelor_edu": [],
                "master_edu": [],
                "phd_edu": [],
                "other_edu": [str(education).strip()] if str(education).strip() else [],
            }

        sanitized = {
            "skills": llm_resume.get("skills", []) if isinstance(llm_resume, dict) and llm_resume.get("skills") else resume.get("skills", resume.get("extracted_skills", [])),
            "extracted_skills": llm_resume.get("skills", []) if isinstance(llm_resume, dict) and llm_resume.get("skills") else resume.get("skills", resume.get("extracted_skills", [])),
            "matched_skills": resume.get("matched_skills", []),
            "education": education,
            "experience": llm_resume.get("experience", resume.get("experience", "")),
            "projects": llm_resume.get("projects", resume.get("projects", "")),
            "certifications": llm_resume.get("certifications", resume.get("certifications", "")),
            "full_text": resume.get("full_text", ""),
        }
        raw_for_screening.append(sanitized)
        candidates.append(
            {
                "name": resume.get("name", ""),
                "file_name": resume.get("file_name", ""),
                "similarity_score": resume.get("similarity_score", 0.0),
                "embedding_score": resume.get("embedding_score", 0.0),
                "skill_score": resume.get("skill_score", 0.0),
                "matched_skills": [str(item).strip() for item in resume.get("matched_skills", []) if str(item).strip()],
                "skills": [str(item).strip() for item in resume.get("skills", resume.get("extracted_skills", [])) if str(item).strip()],
                "extracted_skills": [str(item).strip() for item in resume.get("skills", resume.get("extracted_skills", [])) if str(item).strip()],
                "screening": None,
                "education": education,
                "experience": llm_resume.get("experience", resume.get("experience", [])) if isinstance(llm_resume, dict) else resume.get("experience", []),
                "projects": llm_resume.get("projects", resume.get("projects", [])) if isinstance(llm_resume, dict) else resume.get("projects", []),
                "certifications": llm_resume.get("certifications", resume.get("certifications", [])) if isinstance(llm_resume, dict) else resume.get("certifications", []),
                "achievements": llm_resume.get("achievements", resume.get("achievements", [])) if isinstance(llm_resume, dict) else resume.get("achievements", []),
                "languages": llm_resume.get("languages", resume.get("languages", [])) if isinstance(llm_resume, dict) else resume.get("languages", []),
                "summary": resume.get("summary", ""),
                "email": llm_resume.get("email", resume.get("email", "")) if isinstance(llm_resume, dict) else resume.get("email", ""),
                "phone_number": llm_resume.get("phone_number", resume.get("phone_number", "")) if isinstance(llm_resume, dict) else resume.get("phone_number", ""),
                "location": llm_resume.get("location", resume.get("location", "")) if isinstance(llm_resume, dict) else resume.get("location", ""),
                "llm_resume": llm_resume,
                "full_text": resume.get("full_text", ""),
            }
        )

    return {
        "job_profile": job_profile,
        "candidates": candidates,
        "total": len(candidates),
        "failed_files": failed_files,
        "_raw_for_screening": raw_for_screening,
    }

def build_output(job_description, file_paths):
    """Legacy synchronous function that does both fast parsing and slow screening."""
    output = build_fast_output(job_description, file_paths)

    # Use the sanitized resume copies for screening to avoid issues with
    # non-serializable fields (e.g. sets) that may be present in the
    # internal ranked resumes returned by calculate_similarity.
    raw_list = output.get("_raw_for_screening") or []

    for i, candidate in enumerate(output["candidates"]):
        resume_for_screen = raw_list[i] if i < len(raw_list) else candidate
        candidate["screening"] = screen_candidate(output["job_profile"], resume_for_screen)

    # Remove internal helper data before returning the final JSON-serializable output
    if "_raw_for_screening" in output:
        del output["_raw_for_screening"]

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
