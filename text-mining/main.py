import json
from pathlib import Path

from agents import build_job_profile, parse_resume_agent, screen_candidate
from parser import parse_pdf_with_docling
from extractor import extract_resume_info
from similarity import calculate_similarity


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "test"


job_description = """
Looking for a database engineer with experience in SQL, Oracle, MySQL,
MongoDB, database design, data warehousing, performance tuning,
and database administration.
"""


def _join_or_blank(values):
    if isinstance(values, list):
        return ", ".join(str(value) for value in values if str(value).strip())
    if isinstance(values, dict):
        return json.dumps(values, ensure_ascii=True)
    if values is None:
        return ""
    return str(values)


def _detected_sections(parsed_resume):
    section_labels = [
        ("skills", "Skills"),
        ("tools", "Tools"),
        ("education", "Education"),
        ("experience", "Experience"),
        ("projects", "Projects"),
        ("certifications", "Certifications"),
        ("languages", "Languages"),
    ]

    present = []
    for key, label in section_labels:
        value = parsed_resume.get(key, [])
        if isinstance(value, list) and value:
            present.append(label)
        elif isinstance(value, str) and value.strip():
            present.append(label)

    return ", ".join(present) if present else "None"


def main():
    pdf_files = sorted(DATA_DIR.rglob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {DATA_DIR}")

    job_profile = build_job_profile(job_description)

    resumes = []

    for pdf_file in pdf_files:
        try:
            print(f"Parsing: {pdf_file.name}")

            raw_text = parse_pdf_with_docling(pdf_file)
            llm_resume = parse_resume_agent(raw_text)

            print("\n===== RAW TEXT PREVIEW =====")
            print(raw_text[:1000])
            print()

            print("===== LLM PREPROCESSED RESUME =====")
            print("File Name:", pdf_file.name)
            print("Detected Sections:", _detected_sections(llm_resume))
            print("Skills:", _join_or_blank(llm_resume.get("skills", [])))
            print("Tools:", _join_or_blank(llm_resume.get("tools", [])))
            print("Education:", _join_or_blank(llm_resume.get("education", [])))
            print("Experience:", _join_or_blank(llm_resume.get("experience", [])))
            print("Projects:", _join_or_blank(llm_resume.get("projects", [])))
            print("Certifications:", _join_or_blank(llm_resume.get("certifications", [])))
            print("Languages:", _join_or_blank(llm_resume.get("languages", [])))
            print("Missing Sections:", _join_or_blank(llm_resume.get("missing_sections", [])))
            print("Parsing Notes:", _join_or_blank(llm_resume.get("parsing_notes", [])))
            print("Confidence:", _join_or_blank(llm_resume.get("confidence_scores", {})))
            print()

            resume_info = extract_resume_info(raw_text)
            resume_info["file_name"] = pdf_file.name
            resume_info["full_text"] = raw_text
            resume_info["llm_resume"] = llm_resume

            resumes.append(resume_info)
        except Exception as exc:
            print(f"Skipping {pdf_file.name}: {exc}")

    if not resumes:
        raise RuntimeError("No resumes could be processed.")

    ranked_resumes = calculate_similarity(job_description, resumes)

    for resume in ranked_resumes:
        screening = screen_candidate(job_profile, resume)
        print()
        print("File:", resume["file_name"])
        print("Final Score:", resume["similarity_score"], "%")
        print("Embedding Score:", resume["embedding_score"], "%")
        print("Skill Match Score:", resume["skill_score"], "%")
        print("Matched Skills:", _join_or_blank(resume["matched_skills"]))
        print("Fit Category:", screening["fit_category"])
        print("Screening Score:", screening["score"], "%")
        print("Strengths:", _join_or_blank(screening.get("strengths", [])))
        print("Missing Requirements:", screening["missing_requirements"])
        print("Explanation:", screening["explanation"])


if __name__ == "__main__":
    main()
