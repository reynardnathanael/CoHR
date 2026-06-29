from pathlib import Path
import sys

import fitz

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extractor import extract_resume_info
from pdf_parser_safe import normalize_layout_text, parse_pdf_layout_safe
from resume_merger import merge_resume_outputs
from resume_schema import validate_resume_schema


def _make_pdf(path: Path, text: str) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


def test_old_extractor_still_works():
    info = extract_resume_info("Jane Doe\njane@example.com\nSkills\nPython\nSQL")
    assert info["email"] == "jane@example.com"
    assert "Python" in info["skills_section"] or info["extracted_skills"] is not None


def test_safe_layout_parser_returns_stable_payload(tmp_path):
    pdf_path = tmp_path / "resume.pdf"
    _make_pdf(pdf_path, "Jane Doe\njane@example.com\nPython\nSQL")

    layout = parse_pdf_layout_safe(pdf_path)
    assert "raw_text" in layout
    assert "pages" in layout
    assert "success" in layout

    normalized = normalize_layout_text(layout)
    assert isinstance(normalized, str)


def test_merge_and_validate_fill_keys():
    deterministic = {
        "name": "Jane Doe",
        "contact": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone_number": "123-456-7890",
            "location": "Remote",
            "urls": [],
        },
        "email": "jane@example.com",
        "phone_number": "123-456-7890",
        "location": "Remote",
        "skills": ["python", "sql"],
        "tools": ["python", "sql"],
        "education": {
            "bachelor_edu": [{
                "bachelor_university": "Example University",
                "bachelor_degree": "BSc Computer Science",
                "bachelor_major": "Computer Science",
                "start_date": "2018",
                "end_date": "2022",
                "details": [],
                "raw_text": "BSc Computer Science, Example University, 2018 - 2022",
            }],
            "master_edu": [],
            "phd_edu": [],
            "other_edu": [],
        },
        "experience": [{
            "experience_title": "Data Engineer",
            "experience_description": "Built ETL pipelines.",
            "experience_date": "2020 - 2022",
            "company": "Example Co",
            "location": "Taipei",
            "raw_text": "Data Engineer, Example Co, 2020 - 2022",
        }],
        "projects": [],
        "certifications": [],
        "summary": "",
        "confidence_scores": {"skills": 0.7},
    }
    llm = {
        "contact": {"name": "Jane Doe", "urls": []},
        "summary": "Data engineer with SQL experience.",
        "skills": ["python", "pandas"],
        "tools": ["python", "pandas"],
        "education": {
            "bachelor_edu": [{
                "bachelor_university": "Example University",
                "bachelor_degree": "BSc Computer Science",
                "bachelor_major": "Computer Science",
                "start_date": "2018",
                "end_date": "2022",
                "details": [],
                "raw_text": "BSc Computer Science, Example University, 2018 - 2022",
            }],
            "master_edu": [],
            "phd_edu": [],
            "other_edu": [],
        },
        "experience": [{"experience_title": "Data Engineer"}],
        "projects": [{"project_title": "Pipeline"}],
        "certifications": ["AWS"],
        "languages": ["English"],
        "confidence_scores": {"summary": 0.9},
    }

    merged = merge_resume_outputs(deterministic, llm, "Jane Doe")
    validated = validate_resume_schema(merged)

    for key in ["contact", "summary", "skills", "education", "experience", "projects", "certifications", "languages", "confidence", "raw_text"]:
        assert key in validated


def test_invalid_llm_json_falls_back_safely(monkeypatch):
    from agents import parse_resume_agent

    monkeypatch.setattr("agents.ollama_available", lambda: True)
    monkeypatch.setattr("agents.call_ollama", lambda *args, **kwargs: "not json")

    deterministic = extract_resume_info("Jane Doe\njane@example.com\nPython")
    result = parse_resume_agent("Jane Doe\njane@example.com\nPython", deterministic_info=deterministic)
    assert result["email"] == deterministic["email"]
    assert result["phone_number"] == deterministic["phone_number"]


def test_empty_pdf_text_does_not_crash(tmp_path):
    pdf_path = tmp_path / "empty.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()

    layout = parse_pdf_layout_safe(pdf_path)
    assert "success" in layout
    assert "error" in layout
